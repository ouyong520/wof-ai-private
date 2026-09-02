"""Windows-first Owner runner for current-source R0.2 real proof + R0.4 fork smoke.

This is orchestration/evidence capture only. It never upgrades fixture evidence to
real authority and never contains ROM bytes or savestates in durable output.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import subprocess
import sys
import tempfile
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Sequence

from .determinism import (
    PROOF_SCOPE_REAL as R02_REAL_SCOPE,
    action_sequence_sha256,
    load_action_sequence,
)
from .identity import (
    SOURCE_NAMESPACE,
    farm_source_identity,
    runtime_identity_sha256,
    validate_runtime_identity,
)
from .observation_discovery import _validate_r02_pass_shape
from .savestate_fork_contract import (
    PROOF_SCOPE_REAL as R04_REAL_SCOPE,
    branch_identity_sha256,
    fork_plan_authority_sha256,
    load_fork_plan,
)
from .stable_retro_backend import (
    PINNED_STABLE_RETRO,
    SUPPORTED_PYTHON_MAX,
    SUPPORTED_PYTHON_MIN,
    dependency_probe,
)

RUNNER_SCHEMA = "wof-training-farm-real-proof-owner-runner-summary-v1"
EXPECTED_SOURCE_NAMESPACE = "stable-retro-fbneo"
R02_HORIZON = 8
R02_REPETITIONS = 3
_SHA = re.compile(r"[0-9a-f]{64}\Z")
_RUN = re.compile(r"[0-9a-f]{32}\Z")

_REQUIRED_FILES = (
    "determinism.py",
    "determinism.schema.json",
    "determinism_actions.example.json",
    "savestate_fork.py",
    "savestate_fork_contract.py",
    "savestate_fork_branch.py",
    "savestate_fork_runner.py",
    "savestate_fork_plan.schema.json",
    "savestate_fork_result.schema.json",
    "real_wof_fork_smoke.plan.json",
)

_SOURCE_GUARD_FILES = (
    "__init__.py",
    "adapter.py",
    "fake_backend.py",
    "stable_retro_backend.py",
    "identity.py",
    "determinism.py",
    "determinism.schema.json",
    "observation_discovery.py",
    "savestate_fork.py",
    "savestate_fork_contract.py",
    "savestate_fork_branch.py",
    "savestate_fork_runner.py",
    "savestate_fork_plan.schema.json",
    "savestate_fork_result.schema.json",
    "determinism_actions.example.json",
    "real_wof_fork_smoke.plan.json",
)


class OwnerRunnerError(RuntimeError):
    pass


@dataclass(frozen=True)
class Preflight:
    ok: bool
    reason: str
    repo_root: Path
    evidence_root: Path
    rom_path: Path | None
    rom_sha256: str | None
    source_guard_sha256: str | None
    dependency: dict[str, object]
    required_files: dict[str, str]


CommandRunner = Callable[[Sequence[str], Path, dict[str, str]], subprocess.CompletedProcess[str]]


def _sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        while True:
            chunk = fh.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def _sha_json(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(raw.encode("ascii")).hexdigest()


def _is_within(child: Path, parent: Path) -> bool:
    try:
        child.resolve(strict=False).relative_to(parent.resolve(strict=False))
        return True
    except ValueError:
        return False


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _default_evidence_root() -> Path:
    if platform.system() == "Windows":
        base = os.environ.get("LOCALAPPDATA")
        root = Path(base) if base else Path.home() / "AppData" / "Local"
    else:
        base = os.environ.get("XDG_STATE_HOME")
        root = Path(base) if base else Path.home() / ".local" / "state"
    return root / "WofTrainingFarm" / "real-proof"


def _source_guard(farm_dir: Path) -> tuple[str, dict[str, str]]:
    files: dict[str, str] = {}
    for name in _SOURCE_GUARD_FILES:
        path = farm_dir / name
        if not path.is_file():
            raise OwnerRunnerError(f"required current-source file missing: training/farm/{name}")
        files[name] = _sha_file(path)
    return _sha_json(files), files


def _check_writable_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    fd, probe = tempfile.mkstemp(prefix=".owner-proof-write-", dir=path)
    os.close(fd)
    Path(probe).unlink()


def preflight(evidence_root: Path | None = None) -> Preflight:
    repo = _repo_root()
    farm = repo / "training" / "farm"
    target = (evidence_root or _default_evidence_root()).expanduser().resolve(strict=False)
    required: dict[str, str] = {}
    dependency = dependency_probe().to_dict()

    def fail(reason: str, rom: Path | None = None, rom_sha: str | None = None) -> Preflight:
        return Preflight(False, reason, repo, target, rom, rom_sha, None, dependency, required)

    if SOURCE_NAMESPACE != EXPECTED_SOURCE_NAMESPACE:
        return fail(f"source namespace mismatch: {SOURCE_NAMESPACE!r}")
    if platform.system() not in {"Windows", "Linux"}:
        return fail(f"unsupported platform {platform.system()!r}; expected Windows or Linux")
    py = sys.version_info[:2]
    if not (SUPPORTED_PYTHON_MIN <= py <= SUPPORTED_PYTHON_MAX):
        return fail(
            f"Python {platform.python_version()} unsupported; expected "
            f"{SUPPORTED_PYTHON_MIN[0]}.{SUPPORTED_PYTHON_MIN[1]}.."
            f"{SUPPORTED_PYTHON_MAX[0]}.{SUPPORTED_PYTHON_MAX[1]}"
        )
    if dependency.get("stable_retro_present") is not True:
        return fail("stable-retro is not installed")
    if dependency.get("stable_retro_version") != PINNED_STABLE_RETRO:
        return fail(
            f"stable-retro version must be exactly {PINNED_STABLE_RETRO}; "
            f"observed {dependency.get('stable_retro_version')!r}"
        )
    if dependency.get("fbneo_declared") is not True or dependency.get("fbneo_zip_mapping") is not True:
        return fail("Stable-Retro FBNeo capability probe did not pass")

    raw_rom = os.environ.get("WOF_ROM_PATH")
    if not raw_rom:
        return fail("WOF_ROM_PATH is not set")
    rom = Path(raw_rom).expanduser()
    if not rom.is_absolute():
        return fail("WOF_ROM_PATH must be an absolute external path", rom)
    rom = rom.resolve(strict=False)
    if _is_within(rom, repo):
        return fail("WOF_ROM_PATH must remain outside the repository", rom)
    if not rom.is_file():
        return fail("WOF_ROM_PATH does not resolve to a readable file", rom)
    if rom.suffix.lower() != ".zip":
        return fail("WOF_ROM_PATH must point to an external FBNeo .zip romset", rom)
    try:
        with rom.open("rb") as fh:
            fh.read(1)
        rom_sha = _sha_file(rom)
    except OSError as exc:
        return fail(f"WOF_ROM_PATH is not readable/hashable: {type(exc).__name__}: {exc}", rom)
    if not _SHA.fullmatch(rom_sha):
        return fail("ROM SHA-256 computation returned malformed digest", rom)
    if dependency.get("runtime_ready") is not True:
        return fail(str(dependency.get("detail") or "Stable-Retro/FBNeo runtime is not ready"), rom, rom_sha)

    for name in _REQUIRED_FILES:
        path = farm / name
        if not path.is_file():
            return fail(f"required R0.2/R0.4 file missing: training/farm/{name}", rom, rom_sha)
        required[name] = _sha_file(path)

    if _is_within(target, repo):
        return fail("evidence root must be outside the repository tree", rom, rom_sha)
    try:
        _check_writable_directory(target)
    except OSError as exc:
        return fail(f"evidence root is not writable: {type(exc).__name__}: {exc}", rom, rom_sha)

    try:
        guard, _ = _source_guard(farm)
    except (OSError, OwnerRunnerError) as exc:
        return fail(f"current-source guard failed: {exc}", rom, rom_sha)

    return Preflight(True, "READY", repo, target, rom, rom_sha, guard, dependency, required)


def _load_json(path: Path) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise OwnerRunnerError(f"invalid JSON evidence {path}: {type(exc).__name__}: {exc}") from exc
    if type(value) is not dict:
        raise OwnerRunnerError(f"evidence {path} must contain one JSON object")
    return value


def _schema_top_level_check(result: dict[str, object], schema_path: Path) -> None:
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise OwnerRunnerError(f"failed to load repository schema {schema_path.name}: {exc}") from exc
    if type(schema) is not dict or schema.get("type") != "object":
        raise OwnerRunnerError(f"repository schema {schema_path.name} is malformed")
    required = schema.get("required")
    properties = schema.get("properties")
    if type(required) is not list or type(properties) is not dict:
        raise OwnerRunnerError(f"repository schema {schema_path.name} lacks required/properties")
    missing = [key for key in required if key not in result]
    if missing:
        raise OwnerRunnerError(f"{schema_path.name} required fields missing: {missing}")
    if schema.get("additionalProperties") is False:
        extra = sorted(set(result) - set(properties))
        if extra:
            raise OwnerRunnerError(f"{schema_path.name} rejects extra top-level fields: {extra}")
    for key, rule in properties.items():
        if key not in result or type(rule) is not dict:
            continue
        if "const" in rule and result[key] != rule["const"]:
            raise OwnerRunnerError(f"{schema_path.name} const mismatch for {key}")
        if "enum" in rule and result[key] not in rule["enum"]:
            raise OwnerRunnerError(f"{schema_path.name} enum mismatch for {key}")


def validate_r02_real_pass(
    result: dict[str, object],
    *,
    farm_dir: Path,
    expected_rom_sha256: str,
    expected_action_sha256: str,
) -> dict[str, object]:
    _schema_top_level_check(result, farm_dir / "determinism.schema.json")
    try:
        validated = _validate_r02_pass_shape(result)
    except Exception as exc:
        raise OwnerRunnerError(f"R0.2 semantic authority rejected: {type(exc).__name__}: {exc}") from exc
    if validated["proofScope"] != R02_REAL_SCOPE or validated["realWofProof"] is not True:
        raise OwnerRunnerError("R0.2 result is not REAL_WOF authority")
    if validated["horizonFrames"] != R02_HORIZON:
        raise OwnerRunnerError("R0.2 horizon differs from Owner runner contract")
    if validated["repetitionsRequired"] != R02_REPETITIONS:
        raise OwnerRunnerError("R0.2 repetitions differ from Owner runner contract")
    if validated["actionSequenceSha256"] != expected_action_sha256:
        raise OwnerRunnerError("R0.2 action sequence differs from Owner runner contract")
    runtime = validate_runtime_identity(validated["runtimeIdentity"], require_real_rom=True)
    current_candidate, current_files = farm_source_identity()
    if runtime["farmCandidateSha256"] != current_candidate:
        raise OwnerRunnerError("R0.2 proof Farm candidate is stale/current-source mismatch")
    if runtime["farmSourceFiles"] != current_files:
        raise OwnerRunnerError("R0.2 proof Farm source-file identity is stale/current-source mismatch")
    if runtime["romSha256"] != expected_rom_sha256:
        raise OwnerRunnerError("R0.2 proof ROM identity differs from preflight ROM")
    if validated["runtimeIdentitySha256"] != runtime_identity_sha256(runtime, require_real_rom=True):
        raise OwnerRunnerError("R0.2 runtime identity hash mismatch")
    return validated


def validate_r04_real_pass(
    result: dict[str, object],
    *,
    farm_dir: Path,
    expected_rom_sha256: str,
    r02: dict[str, object],
) -> dict[str, object]:
    _schema_top_level_check(result, farm_dir / "savestate_fork_result.schema.json")
    plan = load_fork_plan(farm_dir / "real_wof_fork_smoke.plan.json")
    expected_keys = {
        "schema","runId","status","reasonCode","message","proofScope","realWofProof",
        "sourceNamespace","forkSetId","forkPlanAuthoritySha256","forkSetAuthoritySha256",
        "rootAuthority","branchSpecifications","repetitionsRequired","branchesRequired",
        "branchesAttempted","branchesCompleted","branches","deterministic","firstDivergence",
        "resume","r0_2ProofGate",
    }
    if set(result) != expected_keys:
        raise OwnerRunnerError("R0.4 result does not exactly match published result envelope")
    if type(result.get("runId")) is not str or not _RUN.fullmatch(result["runId"]):
        raise OwnerRunnerError("R0.4 runId malformed")
    if result.get("status") != "PASS" or result.get("reasonCode") != "FORK_SET_DETERMINISTIC":
        raise OwnerRunnerError("R0.4 result is not PASS / FORK_SET_DETERMINISTIC")
    if result.get("proofScope") != R04_REAL_SCOPE or result.get("realWofProof") is not True:
        raise OwnerRunnerError("R0.4 result is not REAL_WOF_FORK authority")
    if result.get("sourceNamespace") != EXPECTED_SOURCE_NAMESPACE or result.get("deterministic") is not True:
        raise OwnerRunnerError("R0.4 source/deterministic authority mismatch")
    if result.get("forkSetId") != plan.fork_set_id:
        raise OwnerRunnerError("R0.4 forkSetId mismatch")
    if result.get("forkPlanAuthoritySha256") != fork_plan_authority_sha256(plan):
        raise OwnerRunnerError("R0.4 fork plan authority mismatch")
    gate = result.get("r0_2ProofGate")
    if type(gate) is not dict or gate.get("accepted") is not True:
        raise OwnerRunnerError("R0.4 did not accept the R0.2 real proof gate")
    if gate.get("proofRunId") != r02.get("runId"):
        raise OwnerRunnerError("R0.4 R0.2 proofRunId differs from exact current run")
    if gate.get("proofRuntimeIdentitySha256") != r02.get("runtimeIdentitySha256"):
        raise OwnerRunnerError("R0.4 consumed different R0.2 runtime authority")

    root = result.get("rootAuthority")
    if type(root) is not dict:
        raise OwnerRunnerError("R0.4 rootAuthority missing")
    runtime = validate_runtime_identity(root.get("runtimeIdentity"), require_real_rom=True)
    if runtime["romSha256"] != expected_rom_sha256 or root.get("romSha256") != expected_rom_sha256:
        raise OwnerRunnerError("R0.4 ROM authority differs from preflight/R0.2")
    if runtime["farmCandidateSha256"] != r02["runtimeIdentity"]["farmCandidateSha256"]:
        raise OwnerRunnerError("R0.4 Farm candidate differs from R0.2 proof")
    if root.get("runtimeIdentitySha256") != runtime_identity_sha256(runtime, require_real_rom=True):
        raise OwnerRunnerError("R0.4 root runtime identity SHA mismatch")

    specs = result.get("branchSpecifications")
    rows = result.get("branches")
    if type(specs) is not list or len(specs) != len(plan.branches):
        raise OwnerRunnerError("R0.4 branch specification set incomplete")
    if type(rows) is not list or len(rows) != len(plan.branches):
        raise OwnerRunnerError("R0.4 branch result set incomplete")
    if result.get("branchesRequired") != len(plan.branches):
        raise OwnerRunnerError("R0.4 branchesRequired mismatch")
    if result.get("branchesAttempted") != len(plan.branches) or result.get("branchesCompleted") != len(plan.branches):
        raise OwnerRunnerError("R0.4 branch completion counts mismatch")
    by_id = {b.branch_id: b for b in plan.branches}
    seen: set[str] = set()
    for row in rows:
        if type(row) is not dict:
            raise OwnerRunnerError("R0.4 branch row malformed")
        bid = row.get("branchId")
        if type(bid) is not str or bid not in by_id or bid in seen:
            raise OwnerRunnerError("R0.4 branch id unknown/duplicated")
        seen.add(bid)
        branch = by_id[bid]
        if row.get("branchIdentitySha256") != branch_identity_sha256(branch):
            raise OwnerRunnerError(f"R0.4 branch identity mismatch: {bid}")
        if row.get("status") != "PASS" or row.get("reasonCode") != "BRANCH_DETERMINISTIC":
            raise OwnerRunnerError(f"R0.4 branch not deterministic PASS: {bid}")
        if row.get("repetitionsRequired") != plan.repetitions or row.get("repetitionsCompleted") != plan.repetitions:
            raise OwnerRunnerError(f"R0.4 branch repetition count mismatch: {bid}")
        if row.get("deterministic") is not True or row.get("reusedFromResume") is not False:
            raise OwnerRunnerError(f"R0.4 branch proof flags invalid: {bid}")
        outcomes = row.get("outcomes")
        if type(outcomes) is not list or len(outcomes) != plan.repetitions:
            raise OwnerRunnerError(f"R0.4 branch outcomes incomplete: {bid}")
        fingerprints = {o.get("outcomeFingerprintSha256") for o in outcomes if type(o) is dict}
        if len(fingerprints) != 1 or None in fingerprints:
            raise OwnerRunnerError(f"R0.4 branch outcomes are not repeated-identical: {bid}")
    return result


def _default_command_runner(cmd: Sequence[str], cwd: Path, env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(cmd),
        cwd=str(cwd),
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def _new_run_dir(root: Path) -> Path:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = root / f"{stamp}-{uuid.uuid4().hex[:12]}"
    path.mkdir(parents=True, exist_ok=False)
    return path


def _write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_summary(
    run_dir: Path,
    *,
    state: str,
    detail: str,
    pre: Preflight,
    r02_path: Path | None = None,
    r04_path: Path | None = None,
    r02: dict[str, object] | None = None,
    r04: dict[str, object] | None = None,
) -> dict[str, object]:
    summary: dict[str, object] = {
        "schema": RUNNER_SCHEMA,
        "state": state,
        "detail": detail,
        "sourceNamespace": EXPECTED_SOURCE_NAMESPACE,
        "evidenceDirectory": str(run_dir),
        "preflight": {
            "pythonVersion": platform.python_version(),
            "stableRetroVersion": pre.dependency.get("stable_retro_version"),
            "romSha256": pre.rom_sha256,
            "sourceGuardSha256": pre.source_guard_sha256,
            "requiredFileSha256": pre.required_files,
        },
        "r0_2": {
            "path": str(r02_path) if r02_path else None,
            "runId": r02.get("runId") if r02 else None,
            "runtimeIdentitySha256": r02.get("runtimeIdentitySha256") if r02 else None,
        },
        "r0_4": {
            "path": str(r04_path) if r04_path else None,
            "runId": r04.get("runId") if r04 else None,
            "forkSetAuthoritySha256": r04.get("forkSetAuthoritySha256") if r04 else None,
        },
    }
    _write_json(run_dir / "summary.json", summary)
    lines = [
        f"{state} — {detail}",
        f"Evidence: {run_dir}",
        f"R0.2 JSON: {r02_path if r02_path else 'not produced'}",
        f"R0.4 JSON: {r04_path if r04_path else 'not produced'}",
    ]
    (run_dir / "summary.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return summary


def run_owner_flow(
    *,
    evidence_root: Path | None = None,
    command_runner: CommandRunner = _default_command_runner,
    preflight_result: Preflight | None = None,
) -> tuple[int, dict[str, object]]:
    pre = preflight_result or preflight(evidence_root)
    # Never write proof artifacts under the repository, including on failed preflight.
    root = pre.evidence_root
    if _is_within(root, pre.repo_root):
        root = _default_evidence_root().resolve(strict=False)
    try:
        _check_writable_directory(root)
        run_dir = _new_run_dir(root)
    except OSError as exc:
        summary = {
            "schema": RUNNER_SCHEMA,
            "state": "WAITING_PREREQUISITE",
            "detail": f"evidence directory unavailable: {type(exc).__name__}: {exc}",
            "sourceNamespace": EXPECTED_SOURCE_NAMESPACE,
            "evidenceDirectory": None,
        }
        return 2, summary

    if not pre.ok:
        summary = _write_summary(
            run_dir, state="WAITING_PREREQUISITE", detail=pre.reason, pre=pre
        )
        return 2, summary

    repo = pre.repo_root
    farm = repo / "training" / "farm"
    assert pre.rom_sha256 and pre.source_guard_sha256

    steps = load_action_sequence(
        actions_path=str(farm / "determinism_actions.example.json"),
        actions_json=None,
    )
    action_sha = action_sequence_sha256(steps)
    r02_path = run_dir / "r0_2_real_determinism.json"
    r04_path = run_dir / "r0_4_real_fork_smoke.json"

    def guard(stage: str) -> None:
        observed, _ = _source_guard(farm)
        if observed != pre.source_guard_sha256:
            raise OwnerRunnerError(f"current repository source changed during {stage}")

    env = dict(os.environ)
    phase = "R0.2 REAL DETERMINISM"
    try:
        guard("before R0.2")
        r02_cmd = (
            sys.executable, "-m", "training.farm.determinism",
            "--actions", str(farm / "determinism_actions.example.json"),
            "--horizon", str(R02_HORIZON),
            "--repetitions", str(R02_REPETITIONS),
            "--output", str(r02_path),
        )
        cp02 = command_runner(r02_cmd, repo, env)
        if not r02_path.is_file():
            raise OwnerRunnerError(
                f"R0.2 command did not produce JSON (exit {cp02.returncode}): "
                f"{(cp02.stderr or cp02.stdout).strip()[:1000]}"
            )
        raw02 = _load_json(r02_path)
        if raw02.get("status") != "PASS":
            detail = (
                f"{raw02.get('status')} / {raw02.get('reasonCode')}: "
                f"{raw02.get('message')}"
            )
            summary = _write_summary(
                run_dir, state="BLOCKED_R0_2_REAL_DETERMINISM", detail=detail,
                pre=pre, r02_path=r02_path, r02=raw02,
            )
            return 3, summary
        r02 = validate_r02_real_pass(
            raw02, farm_dir=farm, expected_rom_sha256=pre.rom_sha256,
            expected_action_sha256=action_sha,
        )
        guard("after R0.2 validation")
        phase = "R0.4 REAL FORK SMOKE"

        r04_cmd = (
            sys.executable, "-m", "training.farm.savestate_fork",
            "--plan", str(farm / "real_wof_fork_smoke.plan.json"),
            "--r0-2-proof", str(r02_path),
            "--output", str(r04_path),
        )
        cp04 = command_runner(r04_cmd, repo, env)
        if not r04_path.is_file():
            raise OwnerRunnerError(
                f"R0.4 command did not produce JSON (exit {cp04.returncode}): "
                f"{(cp04.stderr or cp04.stdout).strip()[:1000]}"
            )
        raw04 = _load_json(r04_path)
        if raw04.get("status") != "PASS":
            detail = (
                f"{raw04.get('status')} / {raw04.get('reasonCode')}: "
                f"{raw04.get('message')}"
            )
            summary = _write_summary(
                run_dir, state="BLOCKED_R0_4_REAL_FORK_SMOKE", detail=detail,
                pre=pre, r02_path=r02_path, r04_path=r04_path, r02=r02, r04=raw04,
            )
            return 4, summary
        r04 = validate_r04_real_pass(
            raw04, farm_dir=farm, expected_rom_sha256=pre.rom_sha256, r02=r02
        )
        guard("after R0.4 validation")
        summary = _write_summary(
            run_dir,
            state="PASS",
            detail="R0.2 REAL WOF DETERMINISM + R0.4 REAL FORK SMOKE",
            pre=pre, r02_path=r02_path, r04_path=r04_path, r02=r02, r04=r04,
        )
        return 0, summary
    except (OwnerRunnerError, OSError, ValueError, TypeError) as exc:
        state = (
            "BLOCKED_R0_4_REAL_FORK_SMOKE"
            if phase == "R0.4 REAL FORK SMOKE"
            else "BLOCKED_R0_2_REAL_DETERMINISM"
        )
        summary = _write_summary(
            run_dir, state=state, detail=f"{phase}: {type(exc).__name__}: {exc}",
            pre=pre, r02_path=r02_path if r02_path.is_file() else None,
            r04_path=r04_path if r04_path.is_file() else None,
            r02=_load_json(r02_path) if r02_path.is_file() else None,
            r04=_load_json(r04_path) if r04_path.is_file() else None,
        )
        return 5, summary


def _human_verdict(summary: dict[str, object]) -> str:
    state = summary.get("state")
    detail = str(summary.get("detail", ""))
    if state == "PASS":
        return "PASS — R0.2 REAL WOF DETERMINISM + R0.4 REAL FORK SMOKE"
    if state == "WAITING_PREREQUISITE":
        return f"WAITING_PREREQUISITE — {detail}"
    if state == "BLOCKED_R0_2_REAL_DETERMINISM":
        return f"BLOCKED — R0.2 REAL DETERMINISM — {detail}"
    if state == "BLOCKED_R0_4_REAL_FORK_SMOKE":
        return f"BLOCKED — R0.4 REAL FORK SMOKE — {detail}"
    return f"BLOCKED — OWNER RUNNER — {detail}"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="One-command current-source real-WOF R0.2 + R0.4 Owner proof runner"
    )
    ap.add_argument(
        "--evidence-root",
        help="external local evidence root; defaults to LocalAppData/XDG state outside the repository",
    )
    args = ap.parse_args(argv)
    code, summary = run_owner_flow(
        evidence_root=Path(args.evidence_root) if args.evidence_root else None
    )
    print(_human_verdict(summary))
    if summary.get("evidenceDirectory"):
        print(f"Evidence: {summary['evidenceDirectory']}")
    return code


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Publish one Alpha worker terminal RESULT.json/RESULT.md pair from Git authority.

The publisher is local-only and stdlib-only. It never mutates claims, invokes Git,
or pushes to GitHub. Immutable dispatch metadata and claim identity are read from
the repository; the compact finish input may supply only worker-variable result
fields. The final JSON is validated by the existing C1 alpha_worker_result helper
before either terminal artifact is created.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Mapping, Sequence

MANIFEST_SCHEMA = "wof-alpha-dispatch-manifest-v1"
RESULT_SCHEMA = "wof-alpha-worker-result-v1"
SUMMARY_SCHEMA = "wof-alpha-worker-result-publish-v1"
RESULT_ROOT = ("parallel", "PM", "RESULTS")
CLAIM_ROOT = ("parallel", "PM", "DEDUP_CLAIMS")
STAGE_CLAIM_ROOT = ("parallel", "PM", "STAGE_CLAIMS")
DISPATCH_ROOT = ("parallel", "PM", "DISPATCH_MANIFESTS")
TERMINAL_STATES = {"COMPLETE", "SUBCOMPLETE", "BLOCKED"}
CLAIM_STATES = {"ACTIVE", "COMPLETE", "BLOCKED"}
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
STAGE_RE = re.compile(r"^[A-Z0-9][A-Z0-9_]{2,127}$")
DEDUP_RE = re.compile(r"^[a-z0-9][a-z0-9.-]{2,95}$")

INPUT_FIELDS = (
    "state",
    "verdict",
    "implementationCommits",
    "integrationReady",
    "changedFiles",
    "tests",
    "productProof",
    "ownerGate",
    "blocker",
    "nextAction",
    "evidencePaths",
    "safety",
)


class FinishError(RuntimeError):
    def __init__(self, code: str, detail: str):
        super().__init__(detail)
        self.code = code
        self.detail = detail


@dataclass(frozen=True)
class WorkerSpec:
    slot: int
    stage_id: str
    prompt_path: str
    dedup_key: str
    result_protocol: str
    result_json_path: str
    result_md_path: str
    terminal_commit_prefix: str


@dataclass(frozen=True)
class ClaimAuthority:
    claim_token: str
    start_commit: str
    canonical_state: str
    stage_state: str
    canonical_path: str
    stage_path: str


def _mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        raise FinishError("MALFORMED_JSON_SHAPE", f"{label} must be an object")
    return value


def _string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise FinishError("MALFORMED_JSON_SHAPE", f"{label} must be a non-empty string")
    return value


def _repo_relative(value: Any, label: str, prefix: tuple[str, ...], suffix: str) -> str:
    text = _string(value, label)
    if "\\" in text:
        raise FinishError("UNSAFE_REPOSITORY_PATH", f"{label} must use POSIX separators")
    pure = PurePosixPath(text)
    if pure.is_absolute() or ".." in pure.parts or "." in pure.parts:
        raise FinishError("UNSAFE_REPOSITORY_PATH", f"{label} must be canonical and traversal-free")
    if pure.as_posix() != text or pure.parts[: len(prefix)] != prefix or not text.endswith(suffix):
        raise FinishError("UNSAFE_REPOSITORY_PATH", f"{label} is outside its allowed repository path")
    return text


def _load_json(path: Path, label: str) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise FinishError("AUTHORITY_FILE_MISSING", f"{label} not found: {path}") from exc
    except OSError as exc:
        raise FinishError("AUTHORITY_READ_FAILED", f"cannot read {label}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise FinishError("AUTHORITY_JSON_INVALID", f"{label} is invalid JSON: {exc.msg}") from exc


def _resolve_repo_file(repo_root: Path, relative_path: str, label: str) -> Path:
    root = repo_root.resolve()
    pure = PurePosixPath(relative_path)
    candidate = root.joinpath(*pure.parts)
    try:
        resolved_parent = candidate.parent.resolve(strict=True)
    except OSError as exc:
        raise FinishError("AUTHORITY_PATH_INVALID", f"cannot resolve {label} parent: {exc}") from exc
    try:
        resolved_parent.relative_to(root)
    except ValueError as exc:
        raise FinishError("UNSAFE_REPOSITORY_PATH", f"{label} resolves outside repo root") from exc
    return resolved_parent / candidate.name


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise FinishError("VALIDATOR_LOAD_FAILED", f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    except Exception as exc:  # fail closed on validator import/runtime errors
        sys.modules.pop(name, None)
        raise FinishError("VALIDATOR_LOAD_FAILED", f"cannot execute {path}: {exc}") from exc
    return module


def _validate_manifest_with_existing_c2(repo_root: Path, payload: Any):
    tool = repo_root / "parallel" / "PM" / "tools" / "alpha_pm_result_inbox.py"
    if not tool.is_file():
        raise FinishError("C2_VALIDATOR_MISSING", f"existing C2 manifest validator missing: {tool}")
    module = _load_module(tool, "alpha_pm_result_inbox_c6")
    parser = getattr(module, "parse_manifest_payload", None)
    if not callable(parser):
        raise FinishError("C2_VALIDATOR_INVALID", "alpha_pm_result_inbox.parse_manifest_payload is unavailable")
    try:
        manifest = parser(payload)
    except Exception as exc:
        raise FinishError("MANIFEST_INVALID", str(exc)) from exc
    workers = tuple(getattr(manifest, "workers", ()))
    if not 1 <= len(workers) <= 3:
        raise FinishError("MANIFEST_INVALID", "dispatch manifest must contain 1..3 workers")
    if [getattr(w, "slot", None) for w in workers] != list(range(1, len(workers) + 1)):
        raise FinishError("MANIFEST_INVALID", "dispatch manifest slots must be exactly 1..N")
    return manifest


def _load_worker(repo_root: Path, manifest_arg: str, slot: int) -> WorkerSpec:
    manifest_rel = _repo_relative(manifest_arg, "manifest", DISPATCH_ROOT, ".json")
    manifest_path = _resolve_repo_file(repo_root, manifest_rel, "manifest")
    payload = _load_json(manifest_path, "manifest")
    root = _mapping(payload, "manifest")
    if root.get("schema") != MANIFEST_SCHEMA or root.get("immutable") is not True:
        raise FinishError("MANIFEST_INVALID", "manifest must be immutable wof-alpha-dispatch-manifest-v1")
    authority = root.get("authorityCommit")
    if not isinstance(authority, str) or not SHA_RE.fullmatch(authority):
        raise FinishError("MANIFEST_INVALID", "authorityCommit must be a lowercase 40-hex SHA")

    manifest = _validate_manifest_with_existing_c2(repo_root, payload)
    selected = [worker for worker in manifest.workers if worker.slot == slot]
    if len(selected) != 1:
        raise FinishError("SLOT_NOT_FOUND", f"slot {slot} is not declared exactly once")
    worker = selected[0]
    if not STAGE_RE.fullmatch(worker.stage_id) or not DEDUP_RE.fullmatch(worker.dedup_key):
        raise FinishError("MANIFEST_INVALID", "selected worker identity is malformed")
    if worker.result_protocol != RESULT_SCHEMA:
        raise FinishError("MANIFEST_INVALID", f"unsupported resultProtocol: {worker.result_protocol}")
    return WorkerSpec(
        slot=worker.slot,
        stage_id=worker.stage_id,
        prompt_path=worker.prompt_path,
        dedup_key=worker.dedup_key,
        result_protocol=worker.result_protocol,
        result_json_path=worker.result_json_path,
        result_md_path=worker.result_md_path,
        terminal_commit_prefix=worker.terminal_commit_prefix,
    )


def _claim_repo_path(value: Any, label: str) -> str:
    text = _repo_relative(value, label, CLAIM_ROOT, ".json")
    if len(PurePosixPath(text).parts) != len(CLAIM_ROOT) + 1:
        raise FinishError("CLAIM_IDENTITY_MISMATCH", f"{label} must name one canonical claim file")
    return text


def _validate_claim_authority(repo_root: Path, worker: WorkerSpec, terminal_state: str) -> ClaimAuthority:
    stage_rel = "/".join((*STAGE_CLAIM_ROOT, f"{worker.stage_id}.json"))
    stage_path = _resolve_repo_file(repo_root, stage_rel, "stage claim")
    stage = _mapping(_load_json(stage_path, "stage claim"), "stage claim")

    if stage.get("schema") != "wof-pm-stage-claim-v2":
        raise FinishError("CLAIM_IDENTITY_MISMATCH", "stage claim schema is not v2")
    if stage.get("stageId") != worker.stage_id or stage.get("dedupKey") != worker.dedup_key:
        raise FinishError("CLAIM_IDENTITY_MISMATCH", "stage claim identity does not match manifest worker")
    canonical_rel = _claim_repo_path(stage.get("canonicalClaimPath"), "canonicalClaimPath")
    canonical_path = _resolve_repo_file(repo_root, canonical_rel, "canonical claim")
    canonical = _mapping(_load_json(canonical_path, "canonical claim"), "canonical claim")

    if canonical.get("schema") != "wof-pm-dedup-claim-v2" or canonical.get("dedupProtocol") != "v2":
        raise FinishError("CLAIM_IDENTITY_MISMATCH", "canonical claim schema/protocol is not dedup-v2")
    for label, expected in (
        ("dedupKey", worker.dedup_key),
        ("stageId", worker.stage_id),
        ("promptPath", worker.prompt_path),
    ):
        if canonical.get(label) != expected:
            raise FinishError("CLAIM_IDENTITY_MISMATCH", f"canonical {label} does not match manifest worker")

    effective = canonical.get("effectiveDedupKey")
    if not isinstance(effective, str) or not DEDUP_RE.fullmatch(effective.replace("--iv--", ".")):
        # The exact independent-validation effective key can contain repeated separators;
        # filename binding below is the authoritative structural check.
        if not isinstance(effective, str) or not effective.strip():
            raise FinishError("CLAIM_IDENTITY_MISMATCH", "canonical effectiveDedupKey is malformed")
    expected_canonical_rel = "/".join((*CLAIM_ROOT, f"{effective}.json"))
    if canonical_rel != expected_canonical_rel:
        raise FinishError("CLAIM_IDENTITY_MISMATCH", "canonical claim path does not match effectiveDedupKey")
    if stage.get("effectiveDedupKey") != effective:
        raise FinishError("CLAIM_IDENTITY_MISMATCH", "stage/canonical effectiveDedupKey mismatch")

    token = canonical.get("claimToken")
    if not isinstance(token, str) or not (8 <= len(token) <= 256) or stage.get("claimToken") != token:
        raise FinishError("CLAIM_TOKEN_MISMATCH", "stage and canonical claimToken must match exactly")
    start_commit = canonical.get("startCommit")
    if not isinstance(start_commit, str) or not SHA_RE.fullmatch(start_commit):
        raise FinishError("CLAIM_IDENTITY_MISMATCH", "canonical startCommit is invalid")
    if stage.get("startCommit") != start_commit:
        raise FinishError("CLAIM_IDENTITY_MISMATCH", "stage/canonical startCommit mismatch")

    canonical_state = canonical.get("state")
    stage_state = stage.get("state")
    if canonical_state not in CLAIM_STATES or stage_state not in CLAIM_STATES:
        raise FinishError("CLAIM_STATE_INVALID", "claim state must be ACTIVE, COMPLETE, or BLOCKED")

    if terminal_state == "COMPLETE":
        allowed = canonical_state == stage_state == "COMPLETE"
    elif terminal_state == "BLOCKED":
        allowed = canonical_state == stage_state == "BLOCKED"
    else:  # SUBCOMPLETE
        allowed = canonical_state == stage_state and canonical_state in {"ACTIVE", "COMPLETE"}
    if not allowed:
        raise FinishError(
            "CLAIM_STATE_MISMATCH",
            f"terminal {terminal_state} is incompatible with canonical/stage states "
            f"{canonical_state}/{stage_state}",
        )

    return ClaimAuthority(
        claim_token=token,
        start_commit=start_commit,
        canonical_state=canonical_state,
        stage_state=stage_state,
        canonical_path=canonical_rel,
        stage_path=stage_rel,
    )


def _load_finish_input(path: Path) -> dict[str, Any]:
    payload = _mapping(_load_json(path, "finish input"), "finish input")
    missing = set(INPUT_FIELDS) - set(payload)
    extra = set(payload) - set(INPUT_FIELDS)
    if missing:
        raise FinishError("FINISH_INPUT_INVALID", "missing finish fields: " + ", ".join(sorted(missing)))
    if extra:
        raise FinishError("FINISH_INPUT_REDIRECTION", "unsupported finish fields: " + ", ".join(sorted(extra)))
    state = payload.get("state")
    if state not in TERMINAL_STATES:
        raise FinishError("UNSUPPORTED_TERMINAL_STATE", f"state must be one of {sorted(TERMINAL_STATES)}")
    if state == "SUBCOMPLETE":
        next_action = payload.get("nextAction")
        if not isinstance(next_action, str) or not next_action.strip():
            raise FinishError("FINISH_INPUT_INVALID", "SUBCOMPLETE requires a concrete nextAction")
    return dict(payload)


def _build_result(worker: WorkerSpec, authority: ClaimAuthority, finish: Mapping[str, Any]) -> dict[str, Any]:
    result = {
        "schema": RESULT_SCHEMA,
        "stageId": worker.stage_id,
        "dedupKey": worker.dedup_key,
        "claimToken": authority.claim_token,
        "state": finish["state"],
        "verdict": finish["verdict"],
        "startCommit": authority.start_commit,
        "implementationCommits": finish["implementationCommits"],
        "integrationReady": finish["integrationReady"],
        "changedFiles": finish["changedFiles"],
        "tests": finish["tests"],
        "productProof": finish["productProof"],
        "ownerGate": finish["ownerGate"],
        "blocker": finish["blocker"],
        "nextAction": finish["nextAction"],
        "evidencePaths": finish["evidencePaths"],
        "safety": finish["safety"],
    }
    return result


def _validate_with_c1(repo_root: Path, worker: WorkerSpec, result: Mapping[str, Any]) -> None:
    tool = repo_root / "parallel" / "PM" / "tools" / "alpha_worker_result.py"
    if not tool.is_file():
        raise FinishError("C1_VALIDATOR_MISSING", f"existing C1 result validator missing: {tool}")
    module = _load_module(tool, "alpha_worker_result_c6")
    validate = getattr(module, "validate_result", None)
    verify_paths = getattr(module, "verify_result_paths", None)
    if not callable(validate) or not callable(verify_paths):
        raise FinishError("C1_VALIDATOR_INVALID", "C1 validator public functions are unavailable")
    errors = list(validate(dict(result)))
    errors.extend(verify_paths(worker.stage_id, worker.result_json_path, worker.result_md_path))
    if errors:
        raise FinishError("RESULT_VALIDATION_FAILED", "; ".join(errors))


def _markdown(result: Mapping[str, Any], worker: WorkerSpec, authority: ClaimAuthority) -> str:
    lines = [
        f"# {result['stageId']} — {result['state']}",
        "",
        result["verdict"],
        "",
        "## Authority",
        "",
        f"- dedupKey: `{result['dedupKey']}`",
        f"- claimToken: `{result['claimToken']}`",
        f"- startCommit: `{result['startCommit']}`",
        f"- canonicalClaim: `{authority.canonical_path}` ({authority.canonical_state})",
        f"- stageClaim: `{authority.stage_path}` ({authority.stage_state})",
        f"- terminalCommitSubject: `{worker.terminal_commit_prefix} {result['state']}`",
        "",
        "## Implementation",
        "",
    ]
    commits = result["implementationCommits"]
    lines.extend([f"- commit: `{item}`" for item in commits] or ["- implementation commits: none"])
    lines.append(f"- integrationReady: `{str(result['integrationReady']).lower()}`")
    lines.extend([f"- changed: `{item}`" for item in result["changedFiles"]] or ["- changed files: none"])
    lines += ["", "## Tests", ""]
    tests = result["tests"]
    lines.extend(
        f"- **{item['result']}** — {item['name']}: {item['detail']}" for item in tests
    )
    if not tests:
        lines.append("- none")
    proof = result["productProof"]
    lines += [
        "",
        "## Proof / Gate",
        "",
        f"- productProof: `{proof['status']}` / `{proof['classification']}` — {proof['detail']}",
    ]
    gate = result["ownerGate"]
    lines.append(f"- ownerGate.required: `{str(gate['required']).lower()}`")
    if gate.get("question"):
        lines.append(f"- ownerGate.question: {gate['question']}")
    if gate.get("reason"):
        lines.append(f"- ownerGate.reason: {gate['reason']}")
    blocker = result["blocker"]
    if blocker is None:
        lines.append("- blocker: none")
    else:
        lines.append(f"- blocker: `{blocker['code']}` — {blocker['detail']}")
    lines += ["", "## Next", "", f"{result['nextAction']}", "", "## Evidence", ""]
    lines.extend([f"- `{item}`" for item in result["evidencePaths"]] or ["- none"])
    safety = result["safety"]
    lines += [
        "",
        "## Safety",
        "",
        f"- readOnly: `{str(safety['readOnly']).lower()}`",
        f"- ramWrites: `{safety['ramWrites']}`",
        f"- inputInjection: `{str(safety['inputInjection']).lower()}`",
        "",
    ]
    return "\n".join(lines)


def _output_path(repo_root: Path, relative_path: str) -> Path:
    target = _resolve_repo_file(repo_root, relative_path, "result path")
    expected_root = (repo_root.resolve() / "parallel" / "PM" / "RESULTS").resolve()
    try:
        target.parent.resolve(strict=True).relative_to(expected_root)
    except (OSError, ValueError) as exc:
        raise FinishError("UNSAFE_RESULT_PATH", f"result path escapes RESULTS: {relative_path}") from exc
    return target


def _exclusive_write(path: Path, text: str) -> None:
    created = False
    try:
        with path.open("x", encoding="utf-8", newline="\n") as handle:
            created = True
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
    except FileExistsError as exc:
        raise FinishError("RESULT_ALREADY_EXISTS", f"create-only target already exists: {path}") from exc
    except Exception:
        if created:
            try:
                path.unlink()
            except OSError:
                pass
        raise


def _write_pair_create_only(json_path: Path, md_path: Path, result: Mapping[str, Any], markdown: str) -> None:
    if json_path.exists() or md_path.exists():
        existing = [str(p) for p in (json_path, md_path) if p.exists()]
        raise FinishError("RESULT_ALREADY_EXISTS", "create-only target exists: " + ", ".join(existing))
    json_text = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    wrote_json = False
    try:
        _exclusive_write(json_path, json_text)
        wrote_json = True
        _exclusive_write(md_path, markdown)
    except Exception as exc:
        if wrote_json:
            try:
                json_path.unlink()
            except OSError as cleanup_exc:
                raise FinishError(
                    "RESULT_PAIR_ROLLBACK_FAILED",
                    f"pair publish failed ({exc}); could not remove first artifact: {cleanup_exc}",
                ) from exc
        if isinstance(exc, FinishError):
            raise
        raise FinishError("RESULT_WRITE_FAILED", str(exc)) from exc


def publish(args: argparse.Namespace) -> int:
    repo_root = Path(args.repo_root).resolve()
    if not repo_root.is_dir():
        raise FinishError("REPO_ROOT_INVALID", f"repo root is not a directory: {repo_root}")
    worker = _load_worker(repo_root, args.manifest, args.slot)
    finish = _load_finish_input(Path(args.input).resolve())
    authority = _validate_claim_authority(repo_root, worker, finish["state"])
    result = _build_result(worker, authority, finish)
    _validate_with_c1(repo_root, worker, result)
    markdown = _markdown(result, worker, authority)
    json_path = _output_path(repo_root, worker.result_json_path)
    md_path = _output_path(repo_root, worker.result_md_path)
    _write_pair_create_only(json_path, md_path, result, markdown)
    summary = {
        "schema": SUMMARY_SCHEMA,
        "ok": True,
        "stageId": worker.stage_id,
        "state": result["state"],
        "resultJsonPath": worker.result_json_path,
        "resultMdPath": worker.result_md_path,
        "terminalCommitSubject": f"{worker.terminal_commit_prefix} {result['state']}",
    }
    print(json.dumps(summary, ensure_ascii=False, separators=(",", ":"), sort_keys=True))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    pub = sub.add_parser("publish", help="create one manifest-bound terminal RESULT pair")
    pub.add_argument("--manifest", required=True, help="repository-relative immutable dispatch manifest")
    pub.add_argument("--slot", required=True, type=int, help="manifest worker slot")
    pub.add_argument("--input", required=True, help="compact worker finish JSON")
    pub.add_argument("--repo-root", default=".", help="repository checkout root")
    pub.set_defaults(func=publish)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except FinishError as exc:
        print(f"ERROR {exc.code}: {exc.detail}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"ERROR UNEXPECTED_FAILURE: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

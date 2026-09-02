"""Training Farm R0.4 deterministic single-process savestate fork CLI."""
from __future__ import annotations

import argparse
import json
import re
import uuid
from pathlib import Path

from .adapter import TrainingFarmAdapter, TrainingFarmError
from .fake_backend import DeterministicFakeBackend
from .identity import SOURCE_NAMESPACE, build_fixture_runtime_identity, build_real_runtime_identity
from .savestate_fork_contract import (
    RESULT_SCHEMA, PROOF_SCOPE_FIXTURE, PROOF_SCOPE_REAL, MAX_BRANCHES,
    ForkContractError, BranchSpec, ForkPlan, checkpoint_frames,
    fork_plan_authority_sha256, load_fork_plan, parse_fork_plan,
)
from .savestate_fork_runner import run_fork_set
from .stable_retro_backend import StableRetroFbneoBackend, dependency_probe

__all__ = ["ForkContractError", "BranchSpec", "ForkPlan", "PROOF_SCOPE_FIXTURE", "PROOF_SCOPE_REAL",
           "checkpoint_frames", "fork_plan_authority_sha256", "parse_fork_plan", "run_fork_set", "main"]

def _error(code: str, message: str, scope: str | None) -> dict[str, object]:
    return {"schema": RESULT_SCHEMA, "runId": uuid.uuid4().hex, "status": "ERROR", "reasonCode": code,
            "message": message, "proofScope": scope, "realWofProof": False, "sourceNamespace": SOURCE_NAMESPACE,
            "forkSetId": None, "forkPlanAuthoritySha256": None, "forkSetAuthoritySha256": None, "rootAuthority": None,
            "branchSpecifications": [], "repetitionsRequired": 0, "branchesRequired": 0, "branchesAttempted": 0,
            "branchesCompleted": 0, "branches": [], "deterministic": False, "firstDivergence": None,
            "resume": {"requested": False, "acceptedBranchIds": [], "sourceResultSha256": None}, "r0_2ProofGate": None}

def _skip(plan: ForkPlan, detail: str, env: dict[str, object]) -> dict[str, object]:
    return {"schema": RESULT_SCHEMA, "runId": uuid.uuid4().hex, "status": "SKIP",
            "reasonCode": "RUNTIME_PREREQUISITE_UNAVAILABLE", "message": detail, "proofScope": PROOF_SCOPE_REAL,
            "realWofProof": False, "sourceNamespace": SOURCE_NAMESPACE, "forkSetId": plan.fork_set_id,
            "forkPlanAuthoritySha256": fork_plan_authority_sha256(plan), "forkSetAuthoritySha256": None,
            "rootAuthority": None, "branchSpecifications": [], "repetitionsRequired": plan.repetitions,
            "branchesRequired": len(plan.branches), "branchesAttempted": 0, "branchesCompleted": 0, "branches": [],
            "deterministic": False, "firstDivergence": None,
            "resume": {"requested": False, "acceptedBranchIds": [], "sourceResultSha256": None},
            "r0_2ProofGate": {"provided": False, "accepted": False, "environment": env}}

def _load_json(path: str | Path, name: str) -> object:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ForkContractError(f"failed to load {name}: {type(exc).__name__}: {exc}") from exc

def _root_bytes(path: str | Path | None) -> bytes | None:
    if path is None: return None
    try: value = Path(path).read_bytes()
    except OSError as exc: raise ForkContractError(f"failed to read local root savestate: {type(exc).__name__}: {exc}") from exc
    if not value: raise ForkContractError("local root savestate is empty")
    return value

def _cli_int(raw: str) -> int:
    if type(raw) is not str or not re.fullmatch(r"[1-9][0-9]*", raw):
        raise ForkContractError("max-new-branches must be canonical positive decimal digits")
    value = int(raw)
    if not 1 <= value <= MAX_BRANCHES: raise ForkContractError(f"max-new-branches must be 1..{MAX_BRANCHES}")
    return value

def _write(result: dict[str, object], path: str | Path) -> None:
    target = Path(path); tmp = target.with_name(f".{target.name}.tmp-{uuid.uuid4().hex}"); target.parent.mkdir(parents=True, exist_ok=True)
    try: tmp.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"); tmp.replace(target)
    finally:
        if tmp.exists(): tmp.unlink()

def _emit(result: dict[str, object], output: str | None) -> None:
    if output: _write(result, output)
    print(json.dumps(result, indent=2, sort_keys=True))

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Training Farm R0.4 deterministic single-process savestate fork")
    ap.add_argument("--plan", required=True); ap.add_argument("--root-state"); ap.add_argument("--r0-2-proof")
    ap.add_argument("--resume"); ap.add_argument("--max-new-branches"); ap.add_argument("--fake", action="store_true"); ap.add_argument("--output")
    a = ap.parse_args(argv); scope = PROOF_SCOPE_FIXTURE if a.fake else PROOF_SCOPE_REAL
    try:
        plan = load_fork_plan(a.plan); root = _root_bytes(a.root_state)
        resume = _load_json(a.resume, "resume result") if a.resume else None
        proof = _load_json(a.r0_2_proof, "R0.2 proof") if a.r0_2_proof else None
        cap = _cli_int(a.max_new_branches) if a.max_new_branches else None
        if a.fake and proof is not None: raise ForkContractError("--fake cannot consume --r0-2-proof")
    except ForkContractError as exc:
        result = _error("INVALID_CONTRACT", str(exc), scope); _emit(result, a.output); return 1
    progress = (lambda r: _write(r, a.output)) if a.output else None
    if a.fake:
        try:
            with TrainingFarmAdapter(DeterministicFakeBackend()) as adapter:
                result = run_fork_set(adapter, plan, identity_provider=lambda: build_fixture_runtime_identity(adapter),
                                      proof_scope=scope, root_state=root, resume_result=resume,
                                      max_new_branches=cap, progress_callback=progress)
        except (TrainingFarmError, OSError) as exc: result = _error("RUNTIME_OPERATION_FAILED", f"{type(exc).__name__}: {exc}", scope)
    else:
        report = dependency_probe()
        if not report.runtime_ready:
            result = _skip(plan, report.detail, report.to_dict()); _emit(result, a.output); return 2
        try:
            with TrainingFarmAdapter(StableRetroFbneoBackend()) as adapter:
                result = run_fork_set(adapter, plan, identity_provider=lambda: build_real_runtime_identity(adapter),
                                      proof_scope=scope, root_state=root, r0_2_proof=proof, resume_result=resume,
                                      max_new_branches=cap, progress_callback=progress)
        except (TrainingFarmError, OSError) as exc: result = _error("RUNTIME_OPERATION_FAILED", f"{type(exc).__name__}: {exc}", scope)
    _emit(result, a.output)
    return 0 if result.get("status") == "PASS" else 2 if result.get("status") == "SKIP" else 3 if result.get("status") == "PARTIAL" else 1

if __name__ == "__main__": raise SystemExit(main())

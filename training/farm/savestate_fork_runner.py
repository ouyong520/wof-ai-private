"""R0.4 fork-set orchestration, partial result validation, and resume."""
from __future__ import annotations

import copy
import uuid
from typing import Callable
from .adapter import TrainingFarmAdapter, TrainingFarmError
from .determinism import action_sequence_sha256
from .identity import SOURCE_NAMESPACE, validate_runtime_identity
from .observation_discovery import evaluate_r02_proof_gate
from .savestate_fork_branch import capture_root, outcome_fingerprint, run_branch
from .savestate_fork_contract import (
    RESULT_SCHEMA, PROOF_SCOPE_FIXTURE, PROOF_SCOPE_REAL, MAX_BRANCHES,
    ForkContractError, BranchSpec, ForkPlan, _sha_json, _strict_int, _strict_sha,
    branch_identity_sha256, branch_specification_payload, checkpoint_frames,
    fork_plan_authority_sha256, root_hash_payload,
)

def _base(plan: ForkPlan, scope: str) -> dict[str, object]:
    return {"schema": RESULT_SCHEMA, "runId": uuid.uuid4().hex, "status": "ERROR", "reasonCode": "UNINITIALIZED",
            "message": "", "proofScope": scope, "realWofProof": False, "sourceNamespace": SOURCE_NAMESPACE,
            "forkSetId": plan.fork_set_id, "forkPlanAuthoritySha256": fork_plan_authority_sha256(plan),
            "forkSetAuthoritySha256": None, "rootAuthority": None,
            "branchSpecifications": [branch_specification_payload(b) for b in plan.branches],
            "repetitionsRequired": plan.repetitions, "branchesRequired": len(plan.branches), "branchesAttempted": 0,
            "branchesCompleted": 0, "branches": [], "deterministic": False, "firstDivergence": None,
            "resume": {"requested": False, "acceptedBranchIds": [], "sourceResultSha256": None}, "r0_2ProofGate": None}

def _validate_outcome(o: object, b: BranchSpec, root: dict[str, object], index: int) -> dict[str, object]:
    if type(o) is not dict:
        raise ForkContractError("resume outcome must be an object")
    required = ("branchId", "branchIdentitySha256", "actionSequenceSha256", "horizonFrames", "framesExecuted",
                "rootSavestateSha256", "restoredRamSha256", "restoredRamBlocksSha256", "roundtripRootSavestateSha256",
                "finalRamSha256", "finalRamBlocksSha256", "finalSavestateSha256", "memoryLayoutIdentitySha256",
                "checkpoints", "outcomeFingerprintSha256", "repetitionIndex")
    if any(k not in o for k in required):
        raise ForkContractError("resume outcome is missing required authority fields")
    if o["repetitionIndex"] != index or o["branchId"] != b.branch_id or o["horizonFrames"] != b.horizon_frames or o["framesExecuted"] != b.horizon_frames:
        raise ForkContractError("resume outcome branch/repetition/frame binding mismatch")
    if o["branchIdentitySha256"] != branch_identity_sha256(b) or o["actionSequenceSha256"] != action_sequence_sha256(b.steps):
        raise ForkContractError("resume outcome action authority mismatch")
    if (o["rootSavestateSha256"] != root["rootSavestateSha256"] or o["restoredRamSha256"] != root["rootRamSha256"] or
        o["restoredRamBlocksSha256"] != root["rootRamBlocksSha256"] or o["roundtripRootSavestateSha256"] != root["rootSavestateSha256"]):
        raise ForkContractError("resume outcome root binding mismatch")
    for k in ("finalRamSha256", "finalRamBlocksSha256", "finalSavestateSha256", "outcomeFingerprintSha256"):
        _strict_sha(o[k], f"resume.{k}")
    if o["memoryLayoutIdentitySha256"] != root["memoryLayoutIdentity"]["layoutIdentitySha256"]:
        raise ForkContractError("resume outcome layout binding mismatch")
    frames = checkpoint_frames(b); cps = o["checkpoints"]
    if type(cps) is not list or len(cps) != len(frames):
        raise ForkContractError("resume outcome checkpoint count mismatch")
    for pos, cp in zip(frames, cps):
        if type(cp) is not dict or set(cp) != {"frame", "actionStep", "ramSha256"} or cp["frame"] != pos or type(cp["actionStep"]) is not int:
            raise ForkContractError("resume checkpoint is malformed")
        _strict_sha(cp["ramSha256"], "resume checkpoint ramSha256")
    if outcome_fingerprint(o) != o["outcomeFingerprintSha256"]:
        raise ForkContractError("resume outcome fingerprint mismatch")
    return copy.deepcopy(o)

def validate_resume_result(v: object, plan: ForkPlan, root: dict[str, object], *, proof_scope: str) -> dict[str, dict[str, object]]:
    if type(v) is not dict or v.get("schema") != RESULT_SCHEMA or v.get("sourceNamespace") != SOURCE_NAMESPACE:
        raise ForkContractError("resume result schema/source mismatch")
    if v.get("proofScope") != proof_scope or v.get("forkSetId") != plan.fork_set_id or v.get("forkPlanAuthoritySha256") != fork_plan_authority_sha256(plan):
        raise ForkContractError("resume result fork plan/scope mismatch")
    prior_root = v.get("rootAuthority")
    if type(prior_root) is not dict or prior_root.get("rootAuthoritySha256") != _sha_json(root_hash_payload(prior_root)):
        raise ForkContractError("resume root authority is malformed/self-inconsistent")
    if prior_root["rootAuthoritySha256"] != root["rootAuthoritySha256"]:
        raise ForkContractError("resume root/runtime/ROM/source/layout authority mismatch")
    expected_set = _sha_json({"forkPlanAuthoritySha256": fork_plan_authority_sha256(plan), "rootAuthoritySha256": root["rootAuthoritySha256"]})
    if v.get("forkSetAuthoritySha256") != expected_set:
        raise ForkContractError("resume fork-set authority mismatch")
    specs = v.get("branchSpecifications")
    if type(specs) is not list or len(specs) != len(plan.branches):
        raise ForkContractError("resume branch specification set is incomplete")
    spec_by_id = {s.get("branchId"): s for s in specs if type(s) is dict}
    if set(spec_by_id) != {b.branch_id for b in plan.branches}:
        raise ForkContractError("resume branch specification ids mismatch")
    for b in plan.branches:
        s = spec_by_id[b.branch_id]
        if s.get("horizonFrames") != b.horizon_frames or s.get("actionSequenceSha256") != action_sequence_sha256(b.steps) or s.get("branchIdentitySha256") != branch_identity_sha256(b):
            raise ForkContractError("resume branch specification authority mismatch")
    rows = v.get("branches")
    if type(rows) is not list:
        raise ForkContractError("resume branches must be an array")
    reusable: dict[str, dict[str, object]] = {}; branches = {b.branch_id: b for b in plan.branches}
    for row in rows:
        if type(row) is not dict:
            raise ForkContractError("resume branch result must be object")
        bid = row.get("branchId")
        if bid not in branches or bid in reusable:
            raise ForkContractError("resume branch id is unknown or duplicated")
        b = branches[bid]
        if row.get("status") != "PASS" or row.get("reasonCode") != "BRANCH_DETERMINISTIC" or row.get("deterministic") is not True:
            continue
        if row.get("branchIdentitySha256") != branch_identity_sha256(b) or row.get("actionSequenceSha256") != action_sequence_sha256(b.steps) or row.get("horizonFrames") != b.horizon_frames:
            raise ForkContractError("resume completed branch authority mismatch")
        if row.get("repetitionsRequired") != plan.repetitions or row.get("repetitionsCompleted") != plan.repetitions:
            raise ForkContractError("resume completed branch repetitions mismatch")
        raw = row.get("outcomes")
        if type(raw) is not list or len(raw) != plan.repetitions:
            raise ForkContractError("resume completed branch outcomes incomplete")
        outcomes = [_validate_outcome(o, b, root, i) for i, o in enumerate(raw)]
        if len({o["outcomeFingerprintSha256"] for o in outcomes}) != 1:
            raise ForkContractError("resume deterministic branch contains divergent outcomes")
        copied = copy.deepcopy(row); copied["outcomes"] = outcomes; copied["reusedFromResume"] = True; reusable[bid] = copied
    return reusable

def _finalize(base: dict[str, object], rows: list[dict[str, object]], *, real: bool, interrupted: bool, limited: bool) -> dict[str, object]:
    out = copy.deepcopy(base); rows = sorted(rows, key=lambda r: str(r["branchId"])); out["branches"] = rows
    out["branchesAttempted"] = len(rows); out["branchesCompleted"] = sum(r.get("status") == "PASS" for r in rows)
    failed = [r for r in rows if r.get("status") != "PASS"]
    if interrupted or limited or len(rows) < out["branchesRequired"]:
        out.update(status="PARTIAL", reasonCode="INTERRUPTED" if interrupted else "EXECUTION_LIMIT_REACHED" if limited else "MISSING_BRANCH_COMPLETION",
                   message="fork set is incomplete; completed branch metadata remains resumable", deterministic=False, realWofProof=False)
    elif failed:
        out.update(status="FAIL", reasonCode="BRANCH_FAILURE", message="one or more required branches failed", deterministic=False, realWofProof=False)
        out["firstDivergence"] = next((r.get("firstDivergence") for r in failed if r.get("firstDivergence") is not None), None)
    else:
        out.update(status="PASS", reasonCode="FORK_SET_DETERMINISTIC", message="all required branches completed deterministic replay from the exact root",
                   deterministic=True, realWofProof=real)
    return out

def run_fork_set(adapter: TrainingFarmAdapter, plan: ForkPlan, *, identity_provider: Callable[[], dict[str, object]],
                 proof_scope: str, root_state: bytes | None = None, r0_2_proof: object | None = None,
                 resume_result: object | None = None, max_new_branches: int | None = None,
                 progress_callback: Callable[[dict[str, object]], None] | None = None) -> dict[str, object]:
    if not isinstance(plan, ForkPlan): raise ForkContractError("plan must be ForkPlan")
    if proof_scope not in (PROOF_SCOPE_FIXTURE, PROOF_SCOPE_REAL): raise ForkContractError("proof_scope is invalid")
    if max_new_branches is not None: _strict_int(max_new_branches, "max_new_branches", 1, MAX_BRANCHES)
    real = proof_scope == PROOF_SCOPE_REAL; base = _base(plan, proof_scope)
    try:
        current = validate_runtime_identity(identity_provider(), require_real_rom=real)
        if real:
            gate = evaluate_r02_proof_gate(r0_2_proof, current); base["r0_2ProofGate"] = gate
            if r0_2_proof is None:
                base.update(status="SKIP", reasonCode="R0_2_REAL_PROOF_REQUIRED", message="matching current-source real R0.2 deterministic proof is required"); return base
            if gate.get("accepted") is not True:
                base.update(status="ERROR", reasonCode="R0_2_REAL_PROOF_REJECTED", message=str(gate.get("message", "R0.2 proof rejected"))); return base
        elif r0_2_proof is not None: raise ForkContractError("fixture fork cannot consume an R0.2 proof")
        root_bytes, root = capture_root(adapter, plan, root_state, identity_provider, real)
    except (TrainingFarmError, TypeError, ValueError) as exc:
        base.update(status="ERROR", reasonCode="ROOT_AUTHORITY_FAILED", message=f"{type(exc).__name__}: {exc}"); return base
    base["rootAuthority"] = root
    base["forkSetAuthoritySha256"] = _sha_json({"forkPlanAuthoritySha256": base["forkPlanAuthoritySha256"], "rootAuthoritySha256": root["rootAuthoritySha256"]})
    reusable: dict[str, dict[str, object]] = {}
    if resume_result is not None:
        base["resume"]["requested"] = True
        try: reusable = validate_resume_result(resume_result, plan, root, proof_scope=proof_scope)
        except (TrainingFarmError, TypeError, ValueError, KeyError) as exc:
            base.update(status="ERROR", reasonCode="INVALID_RESUME_RESULT", message=f"{type(exc).__name__}: {exc}"); return base
        base["resume"]["acceptedBranchIds"] = sorted(reusable); base["resume"]["sourceResultSha256"] = _sha_json(resume_result)
    rows = [copy.deepcopy(reusable[b.branch_id]) for b in plan.branches if b.branch_id in reusable]
    new_count = 0; interrupted = False; limited = False
    try:
        for b in plan.branches:
            if b.branch_id in reusable: continue
            if max_new_branches is not None and new_count >= max_new_branches: limited = True; break
            rows.append(run_branch(adapter, b, plan.repetitions, root_bytes, root, identity_provider, real)); new_count += 1
            if progress_callback: progress_callback(_finalize(base, rows, real=real, interrupted=False, limited=False))
    except KeyboardInterrupt: interrupted = True
    final = _finalize(base, rows, real=real, interrupted=interrupted, limited=limited)
    if progress_callback: progress_callback(final)
    return final

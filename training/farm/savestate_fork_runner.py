"""R0.4 fork-set orchestration, partial result validation, and resume."""
from __future__ import annotations

import copy
import uuid
from typing import Callable
from .adapter import TrainingFarmAdapter, TrainingFarmError
from .determinism import action_sequence_sha256
from .identity import SOURCE_NAMESPACE, runtime_identity_sha256, validate_runtime_identity
from .observation_discovery import evaluate_r02_proof_gate
from .savestate_fork_branch import capture_root, outcome_fingerprint, run_branch
from .savestate_fork_contract import (
    RESULT_SCHEMA, PROOF_SCOPE_FIXTURE, PROOF_SCOPE_REAL, MAX_BRANCHES,
    ForkContractError, BranchSpec, ForkPlan, _sha_json, _strict_int, _strict_sha,
    branch_identity_sha256, branch_specification_payload, checkpoint_frames,
    fork_plan_authority_sha256, root_hash_payload, stable_runtime_authority,
)

_RESULT_KEYS = {
    "schema", "runId", "status", "reasonCode", "message", "proofScope", "realWofProof",
    "sourceNamespace", "forkSetId", "forkPlanAuthoritySha256", "forkSetAuthoritySha256",
    "rootAuthority", "branchSpecifications", "repetitionsRequired", "branchesRequired",
    "branchesAttempted", "branchesCompleted", "branches", "deterministic", "firstDivergence",
    "resume", "r0_2ProofGate",
}
_ROOT_KEYS = {
    "schema", "sourceNamespace", "forkSetId", "rootId", "rootCaptureMode", "rootLogicalFrame",
    "rootSavestateSha256", "rootRamSha256", "rootRamBlocksSha256", "memoryLayoutIdentity",
    "runtimeIdentity", "runtimeIdentitySha256", "stableRuntimeAuthority", "romSha256",
    "farmCandidateSha256", "forkCandidateSha256", "forkSourceFiles", "inputIsolationMode",
    "rootAuthoritySha256",
}
_BRANCH_KEYS = {
    "branchId", "branchIdentitySha256", "actionSequenceSha256", "horizonFrames", "status",
    "reasonCode", "message", "repetitionsRequired", "repetitionsCompleted", "deterministic",
    "firstDivergence", "reusedFromResume", "outcomes",
}
_OUTCOME_KEYS = {
    "branchId", "branchIdentitySha256", "actionSequenceSha256", "horizonFrames", "framesExecuted",
    "rootSavestateSha256", "restoredRamSha256", "restoredRamBlocksSha256",
    "roundtripRootSavestateSha256", "finalRamSha256", "finalRamBlocksSha256",
    "finalSavestateSha256", "memoryLayoutIdentitySha256", "checkpoints",
    "outcomeFingerprintSha256", "repetitionIndex",
}

def _base(plan: ForkPlan, scope: str) -> dict[str, object]:
    return {"schema": RESULT_SCHEMA, "runId": uuid.uuid4().hex, "status": "ERROR", "reasonCode": "UNINITIALIZED",
            "message": "", "proofScope": scope, "realWofProof": False, "sourceNamespace": SOURCE_NAMESPACE,
            "forkSetId": plan.fork_set_id, "forkPlanAuthoritySha256": fork_plan_authority_sha256(plan),
            "forkSetAuthoritySha256": None, "rootAuthority": None,
            "branchSpecifications": [branch_specification_payload(b) for b in plan.branches],
            "repetitionsRequired": plan.repetitions, "branchesRequired": len(plan.branches), "branchesAttempted": 0,
            "branchesCompleted": 0, "branches": [], "deterministic": False, "firstDivergence": None,
            "resume": {"requested": False, "acceptedBranchIds": [], "sourceResultSha256": None}, "r0_2ProofGate": None}

def _validate_resume_envelope(v: object, plan: ForkPlan, proof_scope: str) -> dict[str, object]:
    if type(v) is not dict or set(v) != _RESULT_KEYS:
        raise ForkContractError("resume result must exactly match the published result envelope")
    if v["schema"] != RESULT_SCHEMA or v["sourceNamespace"] != SOURCE_NAMESPACE:
        raise ForkContractError("resume result schema/source mismatch")
    run_id = v["runId"]
    if type(run_id) is not str or len(run_id) != 32 or any(ch not in "0123456789abcdef" for ch in run_id):
        raise ForkContractError("resume runId must be 32 lowercase hex characters")
    status = v["status"]
    if status not in ("PASS", "PARTIAL", "FAIL", "ERROR", "SKIP"):
        raise ForkContractError("resume result status is invalid")
    if type(v["reasonCode"]) is not str or not v["reasonCode"] or type(v["message"]) is not str:
        raise ForkContractError("resume result reason/message is malformed")
    if v["proofScope"] != proof_scope or v["forkSetId"] != plan.fork_set_id or v["forkPlanAuthoritySha256"] != fork_plan_authority_sha256(plan):
        raise ForkContractError("resume result fork plan/scope mismatch")
    if type(v["realWofProof"]) is not bool or type(v["deterministic"]) is not bool:
        raise ForkContractError("resume result proof/deterministic flags must be strict booleans")
    expected_real = proof_scope == PROOF_SCOPE_REAL and status == "PASS"
    if v["realWofProof"] is not expected_real or v["deterministic"] is not (status == "PASS"):
        raise ForkContractError("resume result status/proof flags are inconsistent")
    if v["firstDivergence"] is not None and type(v["firstDivergence"]) is not dict:
        raise ForkContractError("resume result firstDivergence is malformed")
    if v["repetitionsRequired"] != plan.repetitions or v["branchesRequired"] != len(plan.branches):
        raise ForkContractError("resume result required-count authority mismatch")
    _strict_int(v["branchesAttempted"], "resume.branchesAttempted", 0, MAX_BRANCHES)
    _strict_int(v["branchesCompleted"], "resume.branchesCompleted", 0, MAX_BRANCHES)
    resume = v["resume"]
    if type(resume) is not dict or set(resume) != {"requested", "acceptedBranchIds", "sourceResultSha256"}:
        raise ForkContractError("resume provenance envelope is malformed")
    if type(resume["requested"]) is not bool or type(resume["acceptedBranchIds"]) is not list:
        raise ForkContractError("resume provenance fields are malformed")
    accepted = resume["acceptedBranchIds"]
    if len(accepted) != len(set(accepted)) or any(type(bid) is not str or bid not in {b.branch_id for b in plan.branches} for bid in accepted):
        raise ForkContractError("resume provenance branch ids are malformed")
    if resume["sourceResultSha256"] is not None:
        _strict_sha(resume["sourceResultSha256"], "resume.sourceResultSha256")
    if v["r0_2ProofGate"] is not None and type(v["r0_2ProofGate"]) is not dict:
        raise ForkContractError("resume R0.2 proof gate is malformed")
    return v

def _validate_outcome(o: object, b: BranchSpec, root: dict[str, object], index: int) -> dict[str, object]:
    if type(o) is not dict or set(o) != _OUTCOME_KEYS:
        raise ForkContractError("resume outcome must exactly match the published outcome envelope")
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
    v = _validate_resume_envelope(v, plan, proof_scope)
    prior_root = v["rootAuthority"]
    if type(prior_root) is not dict or set(prior_root) != _ROOT_KEYS:
        raise ForkContractError("resume root authority must exactly match the published root envelope")
    real = proof_scope == PROOF_SCOPE_REAL
    prior_identity = validate_runtime_identity(prior_root["runtimeIdentity"], require_real_rom=real)
    if prior_root["runtimeIdentitySha256"] != runtime_identity_sha256(prior_identity, require_real_rom=real):
        raise ForkContractError("resume root runtime identity SHA-256 mismatch")
    if prior_root["stableRuntimeAuthority"] != stable_runtime_authority(prior_identity):
        raise ForkContractError("resume root stable runtime authority mismatch")
    if prior_root["romSha256"] != prior_identity["romSha256"] or prior_root["farmCandidateSha256"] != prior_identity["farmCandidateSha256"]:
        raise ForkContractError("resume root runtime/ROM/Farm binding mismatch")
    if prior_root.get("rootAuthoritySha256") != _sha_json(root_hash_payload(prior_root)):
        raise ForkContractError("resume root authority is malformed/self-inconsistent")
    if prior_root["rootAuthoritySha256"] != root["rootAuthoritySha256"]:
        raise ForkContractError("resume root/runtime/ROM/source/layout authority mismatch")
    expected_set = _sha_json({"forkPlanAuthoritySha256": fork_plan_authority_sha256(plan), "rootAuthoritySha256": root["rootAuthoritySha256"]})
    if v["forkSetAuthoritySha256"] != expected_set:
        raise ForkContractError("resume fork-set authority mismatch")
    specs = v["branchSpecifications"]
    if type(specs) is not list or len(specs) != len(plan.branches):
        raise ForkContractError("resume branch specification set is incomplete")
    spec_by_id: dict[str, dict[str, object]] = {}
    for spec in specs:
        if type(spec) is not dict or set(spec) != {"branchId", "horizonFrames", "actions", "actionSequenceSha256", "branchIdentitySha256", "metadata"}:
            raise ForkContractError("resume branch specification is malformed")
        bid = spec["branchId"]
        if type(bid) is not str or bid in spec_by_id:
            raise ForkContractError("resume branch specification ids are malformed or duplicated")
        metadata = spec["metadata"]
        if type(metadata) is not dict or set(metadata) != {"label"} or (metadata["label"] is not None and (type(metadata["label"]) is not str or len(metadata["label"]) > 256)):
            raise ForkContractError("resume branch specification metadata is malformed")
        spec_by_id[bid] = spec
    if set(spec_by_id) != {b.branch_id for b in plan.branches}:
        raise ForkContractError("resume branch specification ids mismatch")
    for b in plan.branches:
        s = spec_by_id[b.branch_id]; expected = branch_specification_payload(b)
        for field in ("branchId", "horizonFrames", "actions", "actionSequenceSha256", "branchIdentitySha256"):
            if s[field] != expected[field]:
                raise ForkContractError("resume branch specification authority mismatch")
    rows = v["branches"]
    if type(rows) is not list:
        raise ForkContractError("resume branches must be an array")
    if v["branchesAttempted"] != len(rows):
        raise ForkContractError("resume attempted-branch count mismatch")
    reusable: dict[str, dict[str, object]] = {}; branches = {b.branch_id: b for b in plan.branches}
    pass_count = 0
    for row in rows:
        if type(row) is not dict or set(row) != _BRANCH_KEYS:
            raise ForkContractError("resume branch result must exactly match the published branch envelope")
        bid = row["branchId"]
        if bid not in branches or bid in reusable:
            raise ForkContractError("resume branch id is unknown or duplicated")
        b = branches[bid]
        if row["branchIdentitySha256"] != branch_identity_sha256(b) or row["actionSequenceSha256"] != action_sequence_sha256(b.steps) or row["horizonFrames"] != b.horizon_frames:
            raise ForkContractError("resume branch authority mismatch")
        if row["status"] not in ("PASS", "FAIL", "ERROR") or type(row["reasonCode"]) is not str or not row["reasonCode"] or type(row["message"]) is not str:
            raise ForkContractError("resume branch status/reason/message is malformed")
        if row["repetitionsRequired"] != plan.repetitions:
            raise ForkContractError("resume branch repetitionsRequired mismatch")
        completed = _strict_int(row["repetitionsCompleted"], "resume.repetitionsCompleted", 0, plan.repetitions)
        if type(row["deterministic"]) is not bool or type(row["reusedFromResume"]) is not bool or (row["firstDivergence"] is not None and type(row["firstDivergence"]) is not dict):
            raise ForkContractError("resume branch flags/divergence are malformed")
        raw = row["outcomes"]
        if type(raw) is not list or len(raw) != completed:
            raise ForkContractError("resume branch outcome count mismatch")
        outcomes = [_validate_outcome(o, b, root, i) for i, o in enumerate(raw)]
        if row["status"] == "PASS":
            pass_count += 1
            if row["reasonCode"] != "BRANCH_DETERMINISTIC" or row["deterministic"] is not True or completed != plan.repetitions:
                raise ForkContractError("resume PASS branch completion authority mismatch")
            if len({o["outcomeFingerprintSha256"] for o in outcomes}) != 1:
                raise ForkContractError("resume deterministic branch contains divergent outcomes")
            copied = copy.deepcopy(row); copied["outcomes"] = outcomes; copied["reusedFromResume"] = True; reusable[bid] = copied
        elif row["deterministic"] is not False:
            raise ForkContractError("resume non-PASS branch cannot claim deterministic")
    if v["branchesCompleted"] != pass_count:
        raise ForkContractError("resume completed-branch count mismatch")
    if v["status"] in ("ERROR", "SKIP") and rows:
        raise ForkContractError("resume ERROR/SKIP result cannot contain branch execution evidence")
    if v["status"] == "PASS" and (len(rows) != len(plan.branches) or pass_count != len(plan.branches)):
        raise ForkContractError("resume PASS result is missing required deterministic branches")
    if v["status"] == "FAIL" and (len(rows) != len(plan.branches) or pass_count == len(plan.branches)):
        raise ForkContractError("resume FAIL result has inconsistent branch completion")
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

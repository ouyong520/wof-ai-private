"""R0.4 exact-root branch execution and deterministic replay."""
from __future__ import annotations

from typing import Callable
from .adapter import TrainingFarmAdapter, TrainingFarmError
from .determinism import action_sequence_sha256
from .identity import SOURCE_NAMESPACE, identities_match_exactly, runtime_identity_sha256, validate_runtime_identity
from .savestate_fork_contract import (
    ROOT_SCHEMA, ForkContractError, BranchSpec, ForkPlan, _sha_bytes, _sha_json,
    blocks_snapshot_sha, branch_identity_sha256, checkpoint_frames, fork_source_identity,
    memory_layout_identity, root_hash_payload, stable_runtime_authority,
)

def verify_live(provider: Callable[[], dict[str, object]], baseline: dict[str, object], real: bool, fork_sha: str) -> None:
    current = validate_runtime_identity(provider(), require_real_rom=real)
    if not identities_match_exactly(baseline, current, require_real_rom=real):
        raise ForkContractError("runtime/ROM/backend/Farm identity changed")
    if fork_source_identity()[0] != fork_sha:
        raise ForkContractError("R0.4 fork source identity changed")

def capture_root(adapter: TrainingFarmAdapter, plan: ForkPlan, root_state: bytes | None,
                 provider: Callable[[], dict[str, object]], real: bool) -> tuple[bytes, dict[str, object]]:
    identity = validate_runtime_identity(provider(), require_real_rom=real)
    fork_sha, fork_files = fork_source_identity()
    if root_state is None:
        adapter.reset(); state = adapter.save_state(); mode = "RESET_CAPTURE"
    else:
        if type(root_state) is not bytes or not root_state:
            raise ForkContractError("root_state must be non-empty bytes")
        state = bytes(root_state); mode = "EXTERNAL_LOCAL_STATE"
    state_sha = _sha_bytes(state)
    if plan.expected_root_savestate_sha256 is not None and state_sha != plan.expected_root_savestate_sha256:
        raise ForkContractError("root savestate SHA-256 does not match plan")
    adapter.load_state(state)
    ram = adapter.read_ram(); blocks = adapter.read_ram_blocks(); layout = memory_layout_identity(blocks)
    if _sha_bytes(adapter.save_state()) != state_sha:
        raise ForkContractError("root savestate load/save roundtrip mismatch")
    verify_live(provider, identity, real, fork_sha)
    root: dict[str, object] = {
        "schema": ROOT_SCHEMA, "sourceNamespace": SOURCE_NAMESPACE, "forkSetId": plan.fork_set_id,
        "rootId": plan.root_id, "rootCaptureMode": mode, "rootLogicalFrame": 0,
        "rootSavestateSha256": state_sha, "rootRamSha256": _sha_bytes(ram),
        "rootRamBlocksSha256": blocks_snapshot_sha(blocks), "memoryLayoutIdentity": layout,
        "runtimeIdentity": identity, "runtimeIdentitySha256": runtime_identity_sha256(identity, require_real_rom=real),
        "stableRuntimeAuthority": stable_runtime_authority(identity), "romSha256": identity["romSha256"],
        "farmCandidateSha256": identity["farmCandidateSha256"], "forkCandidateSha256": fork_sha,
        "forkSourceFiles": fork_files, "inputIsolationMode": "explicit-all-player-mask-every-frame",
    }
    root["rootAuthoritySha256"] = _sha_json(root_hash_payload(root))
    return state, root

def restore_root(adapter: TrainingFarmAdapter, state: bytes, root: dict[str, object]) -> tuple[str, str, str]:
    if _sha_bytes(state) != root["rootSavestateSha256"]:
        raise ForkContractError("in-memory root savestate changed")
    adapter.load_state(state); ram_sha = _sha_bytes(adapter.read_ram()); blocks = adapter.read_ram_blocks()
    block_sha = blocks_snapshot_sha(blocks)
    if ram_sha != root["rootRamSha256"] or block_sha != root["rootRamBlocksSha256"]:
        raise ForkContractError("restored root RAM does not match root authority")
    if memory_layout_identity(blocks) != root["memoryLayoutIdentity"]:
        raise ForkContractError("restored root RAM layout changed")
    roundtrip = _sha_bytes(adapter.save_state())
    if roundtrip != root["rootSavestateSha256"]:
        raise ForkContractError("restored root savestate roundtrip mismatch")
    return ram_sha, block_sha, roundtrip

def outcome_fingerprint(o: dict[str, object]) -> str:
    keys = ("branchId", "branchIdentitySha256", "actionSequenceSha256", "horizonFrames", "framesExecuted",
            "finalRamSha256", "finalRamBlocksSha256", "finalSavestateSha256", "checkpoints")
    return _sha_json({k: o[k] for k in keys})

def run_one(adapter: TrainingFarmAdapter, branch: BranchSpec, rep: int, state: bytes, root: dict[str, object],
            provider: Callable[[], dict[str, object]], real: bool) -> dict[str, object]:
    baseline = root["runtimeIdentity"]; assert isinstance(baseline, dict)
    verify_live(provider, baseline, real, str(root["forkCandidateSha256"]))
    rr, rb, rs = restore_root(adapter, state, root)
    wanted = set(checkpoint_frames(branch)); checkpoints: list[dict[str, object]] = []; frame = 0
    for action_step, step in enumerate(branch.steps):
        for _ in range(step.frames):
            frame += 1; ram = adapter.step_frame(step.frame_input)
            if frame in wanted:
                checkpoints.append({"frame": frame, "actionStep": action_step, "ramSha256": _sha_bytes(ram)})
    if frame != branch.horizon_frames or not checkpoints or checkpoints[-1]["frame"] != branch.horizon_frames:
        raise ForkContractError("executed frame/checkpoint count does not match branch horizon")
    final_ram = adapter.read_ram(); final_blocks = adapter.read_ram_blocks(); final_state = adapter.save_state()
    if memory_layout_identity(final_blocks) != root["memoryLayoutIdentity"]:
        raise ForkContractError("RAM layout changed during branch")
    verify_live(provider, baseline, real, str(root["forkCandidateSha256"]))
    out: dict[str, object] = {
        "repetitionIndex": rep, "branchId": branch.branch_id, "branchIdentitySha256": branch_identity_sha256(branch),
        "actionSequenceSha256": action_sequence_sha256(branch.steps), "horizonFrames": branch.horizon_frames,
        "framesExecuted": frame, "rootSavestateSha256": root["rootSavestateSha256"],
        "restoredRamSha256": rr, "restoredRamBlocksSha256": rb, "roundtripRootSavestateSha256": rs,
        "finalRamSha256": _sha_bytes(final_ram), "finalRamBlocksSha256": blocks_snapshot_sha(final_blocks),
        "finalSavestateSha256": _sha_bytes(final_state),
        "memoryLayoutIdentitySha256": root["memoryLayoutIdentity"]["layoutIdentitySha256"], "checkpoints": checkpoints,
    }
    out["outcomeFingerprintSha256"] = outcome_fingerprint(out)
    return out

def first_divergence(a: dict[str, object], b: dict[str, object], rep: int) -> dict[str, object] | None:
    acp, bcp = a["checkpoints"], b["checkpoints"]; assert isinstance(acp, list) and isinstance(bcp, list)
    for x, y in zip(acp, bcp):
        if x != y:
            return {"kind": "RAM_CHECKPOINT", "baselineRepetition": 0, "repetition": rep,
                    "frame": y.get("frame"), "baseline": x, "actual": y}
    for field, kind in (("finalRamSha256", "FINAL_RAM"), ("finalRamBlocksSha256", "FINAL_RAM_BLOCKS"),
                        ("finalSavestateSha256", "FINAL_SAVESTATE")):
        if a[field] != b[field]:
            return {"kind": kind, "baselineRepetition": 0, "repetition": rep,
                    "baselineSha256": a[field], "actualSha256": b[field]}
    return None

def run_branch(adapter: TrainingFarmAdapter, branch: BranchSpec, reps: int, state: bytes, root: dict[str, object],
               provider: Callable[[], dict[str, object]], real: bool) -> dict[str, object]:
    result: dict[str, object] = {
        "branchId": branch.branch_id, "branchIdentitySha256": branch_identity_sha256(branch),
        "actionSequenceSha256": action_sequence_sha256(branch.steps), "horizonFrames": branch.horizon_frames,
        "status": "ERROR", "reasonCode": "UNINITIALIZED", "message": "", "repetitionsRequired": reps,
        "repetitionsCompleted": 0, "deterministic": False, "firstDivergence": None,
        "reusedFromResume": False, "outcomes": [],
    }
    outcomes: list[dict[str, object]] = []
    try:
        for rep in range(reps):
            o = run_one(adapter, branch, rep, state, root, provider, real)
            outcomes.append(o); result["outcomes"] = outcomes; result["repetitionsCompleted"] = len(outcomes)
            if rep:
                d = first_divergence(outcomes[0], o, rep)
                if d is not None or o["outcomeFingerprintSha256"] != outcomes[0]["outcomeFingerprintSha256"]:
                    result.update(status="FAIL", reasonCode="BRANCH_NON_DETERMINISTIC",
                                  message="branch replay diverged from repetition 0",
                                  firstDivergence=d or {"kind": "OUTCOME_FINGERPRINT", "baselineRepetition": 0, "repetition": rep})
                    return result
        result.update(status="PASS", reasonCode="BRANCH_DETERMINISTIC", message="all branch repetitions matched", deterministic=True)
        return result
    except (TrainingFarmError, TypeError, ValueError) as exc:
        result.update(status="ERROR", reasonCode="BRANCH_EXECUTION_FAILED", message=f"{type(exc).__name__}: {exc}")
        return result

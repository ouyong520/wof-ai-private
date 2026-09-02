"""R0.3 address-aware controlled observation-discovery tooling.

This module prepares deterministic candidate discovery only. It never assigns WOF
semantic meaning to an address. Real semantic mapping remains gated by a matching
R0.2 real-WOF determinism PASS.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from .adapter import RamBlockSnapshot, RuntimeCapabilityError, TrainingFarmAdapter, TrainingFarmError
from .determinism import (
    MAX_HORIZON_FRAMES,
    MAX_REPETITIONS,
    PROOF_SCOPE_REAL as R0_2_PROOF_SCOPE_REAL,
    RESULT_SCHEMA as R0_2_RESULT_SCHEMA,
    ReplayStep,
    action_sequence_sha256,
    canonical_action_payload,
    parse_action_sequence,
)
from .fake_backend import DeterministicFakeBackend
from .identity import (
    SOURCE_NAMESPACE,
    build_fixture_runtime_identity,
    build_real_runtime_identity,
    identities_match_exactly,
    runtime_identity_sha256,
    sha256_file,
    validate_runtime_identity,
)
from .stable_retro_backend import StableRetroFbneoBackend, dependency_probe

PLAN_SCHEMA = "wof-training-farm-observation-plan-v1"
RESULT_SCHEMA = "wof-training-farm-observation-discovery-result-v1"
LAYOUT_SCHEMA = "wof-training-farm-memory-layout-v1"
AUTHORITY_FIXTURE = "IMPLEMENTATION_FIXTURE"
AUTHORITY_REAL_UNVERIFIED = "REAL_RUNTIME_OBSERVATION_UNVERIFIED"
AUTHORITY_REAL_ELIGIBLE = "REAL_RUNTIME_OBSERVATION_ELIGIBLE"
MAX_RETURNED_CANDIDATES = 128
MAX_CHANGED_BYTE_LOCATIONS_ANALYZED = 50_000
_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,127}\Z")
_SHA256 = re.compile(r"[0-9a-f]{64}\Z")
_RUN_ID = re.compile(r"[0-9a-f]{32}\Z")
_DISCOVERY_SOURCE_FILES = (
    "adapter.py",
    "fake_backend.py",
    "stable_retro_backend.py",
    "identity.py",
    "determinism.py",
    "determinism.schema.json",
    "observation_discovery.py",
    "observation_plan.schema.json",
    "observation_discovery.schema.json",
)
_R02_CROSS_PROCESS_COMPATIBILITY_FIELDS = (
    "schema",
    "sourceNamespace",
    "runtimeKind",
    "pinnedStableRetroVersion",
    "stableRetroVersion",
    "osSystem",
    "osRelease",
    "machine",
    "pythonImplementation",
    "pythonVersion",
    "pythonExecutable",
    "romIdentityKind",
    "romSha256",
    "farmCandidateSha256",
    "farmSourceFiles",
    "backend",
)


class ObservationContractError(TrainingFarmError):
    """Malformed/non-canonical observation-discovery request."""


@dataclass(frozen=True)
class ObservationBranch:
    branch_id: str
    steps: tuple[ReplayStep, ...]

    def __post_init__(self) -> None:
        _strict_id(self.branch_id, "branch_id")
        if type(self.steps) is not tuple or not self.steps:
            raise ObservationContractError("branch steps must be a non-empty tuple")
        if any(not isinstance(step, ReplayStep) for step in self.steps):
            raise ObservationContractError("branch steps must contain ReplayStep values")


@dataclass(frozen=True)
class ObservationPlan:
    experiment_id: str
    starting_savestate_id: str
    expected_start_state_sha256: str | None
    baseline: ObservationBranch
    interventions: tuple[ObservationBranch, ...]
    horizon_frames: int
    repetitions: int
    capture_frames: tuple[int, ...]
    semantic_label: str | None
    hypothesis: str | None


@dataclass
class _CapturedRepetition:
    index: int
    checkpoint_blocks: dict[int, tuple[RamBlockSnapshot, ...]]
    checkpoint_hashes: dict[int, str]


@dataclass
class _CapturedBranch:
    branch: ObservationBranch
    repetitions: list[_CapturedRepetition]


def _sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha_json(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return _sha_bytes(payload.encode("ascii"))


def _strict_int(value: object, field: str, minimum: int, maximum: int) -> int:
    if type(value) is not int:
        raise ObservationContractError(f"{field} must be a strict integer")
    if not minimum <= value <= maximum:
        raise ObservationContractError(f"{field} must be in range {minimum}..{maximum}")
    return value


def _strict_id(value: object, field: str) -> str:
    if type(value) is not str or not _ID.fullmatch(value):
        raise ObservationContractError(
            f"{field} must be 1..128 canonical identifier characters"
        )
    return value


def _strict_sha(value: object, field: str) -> str:
    if type(value) is not str or not _SHA256.fullmatch(value):
        raise ObservationContractError(f"{field} must be lowercase SHA-256 hex")
    return value


def _strict_optional_text(value: object, field: str) -> str | None:
    if value is None:
        return None
    if type(value) is not str:
        raise ObservationContractError(f"{field} must be string or null")
    if len(value) > 1024:
        raise ObservationContractError(f"{field} exceeds 1024 characters")
    return value


def _validate_branch_horizon(branch: ObservationBranch, horizon: int) -> None:
    actual = sum(step.frames for step in branch.steps)
    if actual != horizon:
        raise ObservationContractError(
            f"branch {branch.branch_id} covers {actual} frames but horizon is {horizon}"
        )


def parse_observation_plan(value: object) -> ObservationPlan:
    required = {
        "schema",
        "experimentId",
        "startingSavestateId",
        "expectedStartStateSha256",
        "baselineActions",
        "interventions",
        "horizonFrames",
        "repetitions",
        "captureFrames",
        "metadata",
    }
    if type(value) is not dict or set(value) != required:
        missing = sorted(required - set(value)) if type(value) is dict else sorted(required)
        extra = sorted(set(value) - required) if type(value) is dict else []
        raise ObservationContractError(
            f"observation plan key mismatch: missing={missing} extra={extra}"
        )
    if value["schema"] != PLAN_SCHEMA:
        raise ObservationContractError("observation plan schema mismatch")
    experiment_id = _strict_id(value["experimentId"], "experimentId")
    start_id = _strict_id(value["startingSavestateId"], "startingSavestateId")
    expected = value["expectedStartStateSha256"]
    if expected is not None:
        expected = _strict_sha(expected, "expectedStartStateSha256")

    horizon = _strict_int(value["horizonFrames"], "horizonFrames", 1, MAX_HORIZON_FRAMES)
    repetitions = _strict_int(value["repetitions"], "repetitions", 2, MAX_REPETITIONS)

    capture_raw = value["captureFrames"]
    if type(capture_raw) is not list or not capture_raw:
        raise ObservationContractError("captureFrames must be a non-empty JSON array")
    capture_frames = tuple(
        _strict_int(frame, f"captureFrames[{index}]", 0, horizon)
        for index, frame in enumerate(capture_raw)
    )
    if tuple(sorted(set(capture_frames))) != capture_frames:
        raise ObservationContractError(
            "captureFrames must be strictly increasing and contain no duplicates"
        )
    if horizon not in capture_frames:
        raise ObservationContractError("captureFrames must include the final horizon frame")

    baseline_steps = parse_action_sequence(value["baselineActions"])
    baseline = ObservationBranch("baseline", baseline_steps)
    _validate_branch_horizon(baseline, horizon)

    interventions_raw = value["interventions"]
    if type(interventions_raw) is not list or not interventions_raw:
        raise ObservationContractError("interventions must be a non-empty JSON array")
    interventions: list[ObservationBranch] = []
    seen_ids: set[str] = set()
    for index, item in enumerate(interventions_raw):
        if type(item) is not dict or set(item) != {"interventionId", "actions"}:
            raise ObservationContractError(
                f"interventions[{index}] must contain exactly interventionId and actions"
            )
        branch_id = _strict_id(
            item["interventionId"], f"interventions[{index}].interventionId"
        )
        if branch_id == "baseline" or branch_id in seen_ids:
            raise ObservationContractError("intervention ids must be unique and not baseline")
        seen_ids.add(branch_id)
        branch = ObservationBranch(branch_id, parse_action_sequence(item["actions"]))
        _validate_branch_horizon(branch, horizon)
        interventions.append(branch)

    metadata = value["metadata"]
    if type(metadata) is not dict or set(metadata) != {"semanticLabel", "hypothesis"}:
        raise ObservationContractError(
            "metadata must contain exactly semanticLabel and hypothesis"
        )
    semantic_label = _strict_optional_text(metadata["semanticLabel"], "metadata.semanticLabel")
    hypothesis = _strict_optional_text(metadata["hypothesis"], "metadata.hypothesis")

    return ObservationPlan(
        experiment_id=experiment_id,
        starting_savestate_id=start_id,
        expected_start_state_sha256=expected,
        baseline=baseline,
        interventions=tuple(interventions),
        horizon_frames=horizon,
        repetitions=repetitions,
        capture_frames=capture_frames,
        semantic_label=semantic_label,
        hypothesis=hypothesis,
    )


def canonical_plan_payload(plan: ObservationPlan) -> dict[str, object]:
    return {
        "schema": PLAN_SCHEMA,
        "experimentId": plan.experiment_id,
        "startingSavestateId": plan.starting_savestate_id,
        "expectedStartStateSha256": plan.expected_start_state_sha256,
        "baselineActions": canonical_action_payload(plan.baseline.steps),
        "interventions": [
            {
                "interventionId": branch.branch_id,
                "actions": canonical_action_payload(branch.steps),
            }
            for branch in plan.interventions
        ],
        "horizonFrames": plan.horizon_frames,
        "repetitions": plan.repetitions,
        "captureFrames": list(plan.capture_frames),
        "metadata": {
            "semanticLabel": plan.semantic_label,
            "hypothesis": plan.hypothesis,
        },
    }


def observation_plan_sha256(plan: ObservationPlan) -> str:
    return _sha_json(canonical_plan_payload(plan))


def discovery_source_identity() -> tuple[str, dict[str, str]]:
    base = Path(__file__).resolve().parent
    files: dict[str, str] = {}
    for name in _DISCOVERY_SOURCE_FILES:
        path = base / name
        if not path.is_file():
            raise RuntimeCapabilityError(f"R0.3 source identity file is missing: {name}")
        files[name] = sha256_file(path)
    return _sha_json(files), files


def _layout_descriptor(
    blocks: tuple[RamBlockSnapshot, ...],
) -> list[dict[str, int]]:
    return [
        {"index": index, "baseAddress": block.base_address, "length": block.length}
        for index, block in enumerate(blocks)
    ]


def _snapshot_sha256(blocks: tuple[RamBlockSnapshot, ...]) -> str:
    digest = hashlib.sha256()
    for block in blocks:
        digest.update(block.base_address.to_bytes(8, "big", signed=False))
        digest.update(block.length.to_bytes(8, "big", signed=False))
        digest.update(block.data)
    return digest.hexdigest()


def build_memory_layout_identity(
    runtime_identity: object,
    blocks: tuple[RamBlockSnapshot, ...],
    *,
    require_real: bool,
) -> dict[str, object]:
    runtime = validate_runtime_identity(runtime_identity, require_real_rom=require_real)
    if type(blocks) is not tuple or not blocks:
        raise RuntimeCapabilityError("memory layout requires address-aware RAM blocks")
    descriptor = _layout_descriptor(blocks)
    layout_shape_sha = _sha_json(
        {
            "sourceNamespace": SOURCE_NAMESPACE,
            "addressKind": "stable-retro-memory-block-key-plus-byte-offset",
            "blocks": descriptor,
        }
    )
    discovery_candidate_sha, discovery_files = discovery_source_identity()
    body: dict[str, object] = {
        "schema": LAYOUT_SCHEMA,
        "sourceNamespace": SOURCE_NAMESPACE,
        "addressKind": "stable-retro-memory-block-key-plus-byte-offset",
        "addressLimitation": (
            "baseAddress preserves the exact Stable-Retro GameData.memory.blocks key; "
            "no host/Browser/WinKawaks address equivalence is implied"
        ),
        "blockCount": len(descriptor),
        "blocks": descriptor,
        "layoutShapeSha256": layout_shape_sha,
        "runtimeIdentitySha256": runtime_identity_sha256(
            runtime, require_real_rom=require_real
        ),
        "romSha256": runtime["romSha256"],
        "farmCandidateSha256": runtime["farmCandidateSha256"],
        "discoveryCandidateSha256": discovery_candidate_sha,
        "discoverySourceFiles": discovery_files,
    }
    body["layoutIdentitySha256"] = _sha_json(body)
    return body


def _assert_same_layout(
    baseline_layout: dict[str, object],
    runtime_identity: dict[str, object],
    blocks: tuple[RamBlockSnapshot, ...],
    *,
    require_real: bool,
) -> None:
    observed = build_memory_layout_identity(
        runtime_identity, blocks, require_real=require_real
    )
    if observed != baseline_layout:
        raise RuntimeCapabilityError("memory layout/source binding changed during experiment")


def _runtime_compatibility_payload(identity: dict[str, object]) -> dict[str, object]:
    return {
        key: copy.deepcopy(identity[key])
        for key in _R02_CROSS_PROCESS_COMPATIBILITY_FIELDS
    }


def _validate_r02_pass_shape(proof: object) -> dict[str, object]:
    if type(proof) is not dict:
        raise ObservationContractError("R0.2 proof must be a JSON object")
    required = {
        "schema",
        "runId",
        "status",
        "reasonCode",
        "message",
        "proofScope",
        "realWofProof",
        "sourceNamespace",
        "repetitionsRequired",
        "repetitionsCompleted",
        "horizonFrames",
        "actionSequence",
        "actionSequenceSha256",
        "runtimeIdentity",
        "runtimeIdentitySha256",
        "startStateSha256",
        "startRamSha256",
        "repetitions",
        "firstDivergence",
    }
    missing = sorted(required - set(proof))
    if missing:
        raise ObservationContractError(f"R0.2 proof missing required fields: {missing}")
    if proof["schema"] != R0_2_RESULT_SCHEMA:
        raise ObservationContractError("R0.2 proof schema mismatch")
    if type(proof["runId"]) is not str or not _RUN_ID.fullmatch(proof["runId"]):
        raise ObservationContractError("R0.2 proof runId is malformed")
    if proof["status"] != "PASS" or proof["reasonCode"] != "DETERMINISM_MATCH":
        raise ObservationContractError("R0.2 proof is not PASS / DETERMINISM_MATCH")
    if proof["proofScope"] != R0_2_PROOF_SCOPE_REAL or proof["realWofProof"] is not True:
        raise ObservationContractError("R0.2 proof is not a real-WOF proof")
    if proof["sourceNamespace"] != SOURCE_NAMESPACE:
        raise ObservationContractError("R0.2 proof source namespace mismatch")
    if type(proof["message"]) is not str:
        raise ObservationContractError("R0.2 proof message must be a string")
    if proof["firstDivergence"] is not None:
        raise ObservationContractError("R0.2 PASS proof cannot contain firstDivergence")

    repetitions_required = _strict_int(
        proof["repetitionsRequired"], "R0.2 repetitionsRequired", 2, MAX_REPETITIONS
    )
    repetitions_completed = _strict_int(
        proof["repetitionsCompleted"], "R0.2 repetitionsCompleted", 0, MAX_REPETITIONS
    )
    if repetitions_completed != repetitions_required:
        raise ObservationContractError("R0.2 proof repetitions are incomplete")
    horizon = _strict_int(
        proof["horizonFrames"], "R0.2 horizonFrames", 1, MAX_HORIZON_FRAMES
    )

    steps = parse_action_sequence(proof["actionSequence"])
    if sum(step.frames for step in steps) != horizon:
        raise ObservationContractError("R0.2 proof action sequence does not cover horizon")
    action_sha = _strict_sha(proof["actionSequenceSha256"], "R0.2 actionSequenceSha256")
    if action_sequence_sha256(steps) != action_sha:
        raise ObservationContractError("R0.2 proof actionSequenceSha256 mismatch")

    runtime = validate_runtime_identity(proof["runtimeIdentity"], require_real_rom=True)
    runtime_sha = _strict_sha(proof["runtimeIdentitySha256"], "R0.2 runtimeIdentitySha256")
    if runtime_identity_sha256(runtime, require_real_rom=True) != runtime_sha:
        raise ObservationContractError("R0.2 runtimeIdentitySha256 mismatch")
    _strict_sha(proof["startStateSha256"], "R0.2 startStateSha256")
    _strict_sha(proof["startRamSha256"], "R0.2 startRamSha256")

    reps = proof["repetitions"]
    if type(reps) is not list or len(reps) != repetitions_required:
        raise ObservationContractError("R0.2 proof repetition array mismatch")
    for index, rep in enumerate(reps):
        if type(rep) is not dict:
            raise ObservationContractError(f"R0.2 repetition[{index}] must be object")
        if type(rep.get("index")) is not int or rep["index"] != index:
            raise ObservationContractError(f"R0.2 repetition[{index}] index mismatch")
        if type(rep.get("framesExecuted")) is not int or rep["framesExecuted"] != horizon:
            raise ObservationContractError(f"R0.2 repetition[{index}] frame count mismatch")
        _strict_sha(rep.get("finalRamSha256"), f"R0.2 repetition[{index}].finalRamSha256")
        checkpoints = rep.get("checkpoints")
        if type(checkpoints) is not list or len(checkpoints) != horizon:
            raise ObservationContractError(
                f"R0.2 repetition[{index}] checkpoint count mismatch"
            )
        for frame_index, checkpoint in enumerate(checkpoints, start=1):
            if type(checkpoint) is not dict:
                raise ObservationContractError("R0.2 checkpoint must be object")
            if type(checkpoint.get("frame")) is not int or checkpoint["frame"] != frame_index:
                raise ObservationContractError("R0.2 checkpoint frame sequence mismatch")
            if type(checkpoint.get("actionStep")) is not int or checkpoint["actionStep"] < 0:
                raise ObservationContractError("R0.2 checkpoint actionStep is malformed")
            _strict_sha(
                checkpoint.get("ramSha256"),
                f"R0.2 repetition[{index}].checkpoint[{frame_index}].ramSha256",
            )
    return dict(proof)


def evaluate_r02_proof_gate(
    proof: object | None,
    current_runtime_identity: object,
) -> dict[str, object]:
    """Validate an R0.2 real proof for a later, separate R0.3 process.

    Cross-process compatibility intentionally excludes only ``processId``. It is a
    required strict run-local identity field, but a prior proof JSON cannot share
    the same process id with a later CLI invocation. Every other R0.2 runtime,
    ROM, source and backend/core identity field must match exactly.
    """
    current = validate_runtime_identity(current_runtime_identity, require_real_rom=True)
    result: dict[str, object] = {
        "provided": proof is not None,
        "accepted": False,
        "reasonCode": "R0_2_PROOF_MISSING",
        "message": "no R0.2 proof supplied",
        "compatibilityRule": (
            "all validated R0.2 runtime/ROM/source/backend fields must match exactly; "
            "only run-local processId may differ across CLI processes"
        ),
        "proofRunId": None,
        "proofRuntimeIdentitySha256": None,
    }
    if proof is None:
        return result
    try:
        validated = _validate_r02_pass_shape(proof)
        proof_runtime = validate_runtime_identity(
            validated["runtimeIdentity"], require_real_rom=True
        )
        if _runtime_compatibility_payload(proof_runtime) != _runtime_compatibility_payload(
            current
        ):
            result.update(
                reasonCode="R0_2_PROOF_IDENTITY_MISMATCH",
                message="R0.2 proof runtime/ROM/source/backend identity does not match",
                proofRunId=validated["runId"],
                proofRuntimeIdentitySha256=validated["runtimeIdentitySha256"],
            )
            return result
        result.update(
            accepted=True,
            reasonCode="R0_2_PROOF_ACCEPTED",
            message="matching real R0.2 determinism proof accepted",
            proofRunId=validated["runId"],
            proofRuntimeIdentitySha256=validated["runtimeIdentitySha256"],
        )
        return result
    except (ObservationContractError, RuntimeCapabilityError, TypeError, ValueError) as exc:
        result.update(
            reasonCode="R0_2_PROOF_INVALID",
            message=f"{type(exc).__name__}: {exc}",
        )
        return result


def _runtime_same(
    provider: Callable[[], dict[str, object]],
    baseline: dict[str, object],
    *,
    require_real: bool,
) -> dict[str, object]:
    observed = validate_runtime_identity(provider(), require_real_rom=require_real)
    if not identities_match_exactly(
        baseline, observed, require_real_rom=require_real
    ):
        raise RuntimeCapabilityError("runtime/ROM/R0.2 Farm source identity changed")
    return observed


def _capture_branch(
    adapter: TrainingFarmAdapter,
    branch: ObservationBranch,
    plan: ObservationPlan,
    *,
    start_state: bytes,
    start_state_sha: str,
    start_snapshot_sha: str,
    baseline_runtime: dict[str, object],
    baseline_layout: dict[str, object],
    baseline_discovery_candidate_sha: str,
    identity_provider: Callable[[], dict[str, object]],
    require_real: bool,
) -> _CapturedBranch:
    captured: list[_CapturedRepetition] = []
    capture_set = set(plan.capture_frames)
    for repetition_index in range(plan.repetitions):
        observed_runtime = _runtime_same(
            identity_provider, baseline_runtime, require_real=require_real
        )
        current_discovery_sha, _ = discovery_source_identity()
        if current_discovery_sha != baseline_discovery_candidate_sha:
            raise RuntimeCapabilityError("R0.3 discovery source identity changed")

        if _sha_bytes(start_state) != start_state_sha:
            raise RuntimeCapabilityError("in-memory starting savestate hash changed")
        adapter.load_state(start_state)
        roundtrip_state = adapter.save_state()
        if _sha_bytes(roundtrip_state) != start_state_sha:
            raise RuntimeCapabilityError("savestate load/save roundtrip hash mismatch")

        restored_blocks = adapter.read_ram_blocks()
        _assert_same_layout(
            baseline_layout,
            observed_runtime,
            restored_blocks,
            require_real=require_real,
        )
        if _snapshot_sha256(restored_blocks) != start_snapshot_sha:
            raise RuntimeCapabilityError("restored address-aware RAM differs from starting state")

        checkpoint_blocks: dict[int, tuple[RamBlockSnapshot, ...]] = {}
        checkpoint_hashes: dict[int, str] = {}
        if 0 in capture_set:
            checkpoint_blocks[0] = restored_blocks
            checkpoint_hashes[0] = _snapshot_sha256(restored_blocks)

        frame = 0
        for step in branch.steps:
            for _ in range(step.frames):
                frame += 1
                adapter.step_frame(step.frame_input)
                if frame in capture_set:
                    blocks = adapter.read_ram_blocks()
                    current_runtime = _runtime_same(
                        identity_provider, baseline_runtime, require_real=require_real
                    )
                    _assert_same_layout(
                        baseline_layout,
                        current_runtime,
                        blocks,
                        require_real=require_real,
                    )
                    checkpoint_blocks[frame] = blocks
                    checkpoint_hashes[frame] = _snapshot_sha256(blocks)

        if frame != plan.horizon_frames:
            raise RuntimeCapabilityError(
                f"branch {branch.branch_id} executed {frame} frames; "
                f"expected {plan.horizon_frames}"
            )
        if tuple(sorted(checkpoint_blocks)) != plan.capture_frames:
            raise RuntimeCapabilityError(
                f"branch {branch.branch_id} missing or extra capture frame"
            )

        final_runtime = _runtime_same(
            identity_provider, baseline_runtime, require_real=require_real
        )
        final_blocks = adapter.read_ram_blocks()
        _assert_same_layout(
            baseline_layout, final_runtime, final_blocks, require_real=require_real
        )
        current_discovery_sha, _ = discovery_source_identity()
        if current_discovery_sha != baseline_discovery_candidate_sha:
            raise RuntimeCapabilityError("R0.3 discovery source identity changed")

        captured.append(
            _CapturedRepetition(
                index=repetition_index,
                checkpoint_blocks=checkpoint_blocks,
                checkpoint_hashes=checkpoint_hashes,
            )
        )
    if len(captured) != plan.repetitions:
        raise RuntimeCapabilityError("required observation repetitions are missing")
    return _CapturedBranch(branch=branch, repetitions=captured)


def _block_for(
    repetition: _CapturedRepetition,
    frame: int,
    block_index: int,
) -> RamBlockSnapshot:
    blocks = repetition.checkpoint_blocks[frame]
    return blocks[block_index]


def _scalar(block: RamBlockSnapshot, offset: int, width: int) -> int:
    data = block.data[offset : offset + width]
    if len(data) != width:
        raise RuntimeCapabilityError("candidate scalar extends beyond RAM block")
    return int.from_bytes(data, "little", signed=False)


def _changed_byte_locations(
    baseline: _CapturedBranch,
    intervention: _CapturedBranch,
    plan: ObservationPlan,
    block_count: int,
) -> tuple[list[tuple[int, int]], bool]:
    changed: set[tuple[int, int]] = set()
    for repetition_index in range(plan.repetitions):
        base_rep = baseline.repetitions[repetition_index]
        int_rep = intervention.repetitions[repetition_index]
        for frame in plan.capture_frames:
            for block_index in range(block_count):
                base_block = _block_for(base_rep, frame, block_index)
                int_block = _block_for(int_rep, frame, block_index)
                if base_block.base_address != int_block.base_address:
                    raise RuntimeCapabilityError("candidate comparison block base mismatch")
                if base_block.length != int_block.length:
                    raise RuntimeCapabilityError("candidate comparison block length mismatch")
                for offset, (base_byte, int_byte) in enumerate(
                    zip(base_block.data, int_block.data)
                ):
                    if base_byte != int_byte:
                        changed.add((block_index, offset))
    ordered = sorted(changed)
    truncated = len(ordered) > MAX_CHANGED_BYTE_LOCATIONS_ANALYZED
    return ordered[:MAX_CHANGED_BYTE_LOCATIONS_ANALYZED], truncated


def _candidate_locations(
    changed_bytes: list[tuple[int, int]],
    layout_blocks: list[dict[str, int]],
) -> list[tuple[int, int, int]]:
    locations: set[tuple[int, int, int]] = set()
    for block_index, offset in changed_bytes:
        length = layout_blocks[block_index]["length"]
        locations.add((block_index, offset, 1))
        if offset + 1 < length:
            locations.add((block_index, offset, 2))
        if offset > 0:
            locations.add((block_index, offset - 1, 2))
    return sorted(locations, key=lambda item: (item[0], item[1], item[2]))


def _candidate_record(
    baseline: _CapturedBranch,
    intervention: _CapturedBranch,
    plan: ObservationPlan,
    layout_blocks: list[dict[str, int]],
    location: tuple[int, int, int],
) -> dict[str, object]:
    block_index, offset, width = location
    block_meta = layout_blocks[block_index]
    observations: list[dict[str, object]] = []
    changed_comparisons = 0
    stable_comparisons = 0
    baseline_stable_frames = 0
    intervention_stable_frames = 0
    jointly_stable_frames = 0

    baseline_all_values: set[int] = set()
    intervention_all_values: set[int] = set()

    for frame in plan.capture_frames:
        baseline_values = [
            _scalar(
                _block_for(rep, frame, block_index),
                offset,
                width,
            )
            for rep in baseline.repetitions
        ]
        intervention_values = [
            _scalar(
                _block_for(rep, frame, block_index),
                offset,
                width,
            )
            for rep in intervention.repetitions
        ]
        baseline_all_values.update(baseline_values)
        intervention_all_values.update(intervention_values)
        pair_changed = sum(
            base_value != intervention_value
            for base_value, intervention_value in zip(
                baseline_values, intervention_values
            )
        )
        changed_comparisons += pair_changed
        stable_comparisons += plan.repetitions - pair_changed
        base_stable = len(set(baseline_values)) == 1
        int_stable = len(set(intervention_values)) == 1
        baseline_stable_frames += int(base_stable)
        intervention_stable_frames += int(int_stable)
        jointly_stable_frames += int(base_stable and int_stable)
        observations.append(
            {
                "frame": frame,
                "baselineValues": sorted(set(baseline_values)),
                "interventionValues": sorted(set(intervention_values)),
                "changedRepetitionCount": pair_changed,
                "stableRepetitionCount": plan.repetitions - pair_changed,
            }
        )

    baseline_temporal_changes = 0
    for rep in baseline.repetitions:
        previous: int | None = None
        for frame in plan.capture_frames:
            value = _scalar(_block_for(rep, frame, block_index), offset, width)
            if previous is not None and value != previous:
                baseline_temporal_changes += 1
            previous = value

    changed_frames = [
        observation["frame"]
        for observation in observations
        if observation["changedRepetitionCount"] > 0
    ]
    total_comparisons = len(plan.capture_frames) * plan.repetitions
    effect_rate = changed_comparisons / total_comparisons
    repetition_stability = jointly_stable_frames / len(plan.capture_frames)
    changed_in_baseline = baseline_temporal_changes > 0
    control_penalty = 0.5 if changed_in_baseline else 1.0
    score = round(effect_rate * repetition_stability * control_penalty, 6)

    base_address = block_meta["baseAddress"]
    return {
        "interventionId": intervention.branch.branch_id,
        "blockIndex": block_index,
        "blockBaseAddress": base_address,
        "blockLength": block_meta["length"],
        "offsetWithinBlock": offset,
        "sourceNativeAddress": base_address + offset,
        "addressProvenance": "Stable-Retro GameData.memory.blocks key + byte offset",
        "widthBytes": width,
        "valueEncoding": (
            "unsigned-byte" if width == 1 else "unsigned-little-endian-analysis-only"
        ),
        "baselineValues": sorted(baseline_all_values),
        "interventionValues": sorted(intervention_all_values),
        "changedComparisonCount": changed_comparisons,
        "stableComparisonCount": stable_comparisons,
        "baselineStableFrameCount": baseline_stable_frames,
        "interventionStableFrameCount": intervention_stable_frames,
        "jointlyStableFrameCount": jointly_stable_frames,
        "baselineControlTemporalChangeCount": baseline_temporal_changes,
        "changedInBaselineControl": changed_in_baseline,
        "downgradedBecauseBaselineChanged": changed_in_baseline,
        "effectRate": round(effect_rate, 6),
        "repetitionStability": round(repetition_stability, 6),
        "consistencyScore": score,
        "firstObservedChangedFrame": min(changed_frames) if changed_frames else None,
        "lastObservedChangedFrame": max(changed_frames) if changed_frames else None,
        "observations": observations,
    }


def analyze_candidates(
    baseline: _CapturedBranch,
    interventions: tuple[_CapturedBranch, ...],
    plan: ObservationPlan,
    layout_identity: dict[str, object],
) -> tuple[list[dict[str, object]], int, bool]:
    layout_blocks = layout_identity["blocks"]
    if type(layout_blocks) is not list:
        raise RuntimeCapabilityError("layout identity blocks are malformed")
    all_candidates: list[dict[str, object]] = []
    analysis_truncated = False

    for intervention in interventions:
        changed_bytes, truncated = _changed_byte_locations(
            baseline, intervention, plan, len(layout_blocks)
        )
        analysis_truncated = analysis_truncated or truncated
        locations = _candidate_locations(changed_bytes, layout_blocks)
        for location in locations:
            record = _candidate_record(
                baseline, intervention, plan, layout_blocks, location
            )
            if record["changedComparisonCount"] > 0:
                all_candidates.append(record)

    all_candidates.sort(
        key=lambda record: (
            -record["consistencyScore"],
            -record["changedComparisonCount"],
            record["downgradedBecauseBaselineChanged"],
            record["interventionId"],
            record["widthBytes"],
            record["blockBaseAddress"],
            record["offsetWithinBlock"],
        )
    )
    total = len(all_candidates)
    return all_candidates[:MAX_RETURNED_CANDIDATES], total, analysis_truncated


def _branch_summary(capture: _CapturedBranch) -> dict[str, object]:
    return {
        "branchId": capture.branch.branch_id,
        "actionSequence": canonical_action_payload(capture.branch.steps),
        "actionSequenceSha256": action_sequence_sha256(capture.branch.steps),
        "repetitions": [
            {
                "index": rep.index,
                "checkpointSnapshotSha256": {
                    str(frame): rep.checkpoint_hashes[frame]
                    for frame in sorted(rep.checkpoint_hashes)
                },
            }
            for rep in capture.repetitions
        ],
    }


def run_observation_discovery(
    adapter: TrainingFarmAdapter,
    plan: ObservationPlan,
    *,
    identity_provider: Callable[[], dict[str, object]],
    real_runtime: bool,
    r02_proof: object | None = None,
) -> dict[str, object]:
    if not isinstance(plan, ObservationPlan):
        raise ObservationContractError("plan must be ObservationPlan")
    require_real = bool(real_runtime)
    run_id = uuid.uuid4().hex
    base: dict[str, object] = {
        "schema": RESULT_SCHEMA,
        "runId": run_id,
        "status": "ERROR",
        "reasonCode": "UNINITIALIZED",
        "message": "",
        "sourceNamespace": SOURCE_NAMESPACE,
        "experimentId": plan.experiment_id,
        "planSha256": observation_plan_sha256(plan),
        "authorityClassification": (
            AUTHORITY_REAL_UNVERIFIED if require_real else AUTHORITY_FIXTURE
        ),
        "semanticMappingUnlocked": False,
        "runtimeIdentity": None,
        "runtimeIdentitySha256": None,
        "memoryLayoutIdentity": None,
        "startingSavestate": {
            "id": plan.starting_savestate_id,
            "sha256": None,
            "expectedSha256": plan.expected_start_state_sha256,
            "expectedMatched": None,
        },
        "horizonFrames": plan.horizon_frames,
        "repetitions": plan.repetitions,
        "captureFrames": list(plan.capture_frames),
        "branches": [],
        "candidateCountTotal": 0,
        "candidateCountReturned": 0,
        "analysisTruncated": False,
        "rankedCandidateChanges": [],
        "proofGate": {
            "provided": r02_proof is not None,
            "accepted": False,
            "reasonCode": (
                "FIXTURE_CANNOT_USE_REAL_PROOF"
                if not require_real
                else "R0_2_PROOF_UNCHECKED"
            ),
            "message": (
                "implementation fixture cannot be upgraded by any proof object"
                if not require_real
                else ""
            ),
            "compatibilityRule": (
                "fixture authority is permanently non-real"
                if not require_real
                else ""
            ),
            "proofRunId": None,
            "proofRuntimeIdentitySha256": None,
        },
        "metadata": {
            "semanticLabel": plan.semantic_label,
            "hypothesis": plan.hypothesis,
            "metadataIsAuthority": False,
        },
        "firstFailure": None,
    }

    try:
        baseline_runtime = validate_runtime_identity(
            identity_provider(), require_real_rom=require_real
        )
        base["runtimeIdentity"] = baseline_runtime
        base["runtimeIdentitySha256"] = runtime_identity_sha256(
            baseline_runtime, require_real_rom=require_real
        )

        if require_real:
            proof_gate = evaluate_r02_proof_gate(r02_proof, baseline_runtime)
            base["proofGate"] = proof_gate
            if proof_gate["accepted"]:
                base["authorityClassification"] = AUTHORITY_REAL_ELIGIBLE
                base["semanticMappingUnlocked"] = True
            else:
                base["authorityClassification"] = AUTHORITY_REAL_UNVERIFIED
                base["semanticMappingUnlocked"] = False

        adapter.reset()
        start_state = adapter.save_state()
        start_state_sha = _sha_bytes(start_state)
        start_info = base["startingSavestate"]
        assert isinstance(start_info, dict)
        start_info["sha256"] = start_state_sha
        if plan.expected_start_state_sha256 is None:
            start_info["expectedMatched"] = None
        else:
            matched = start_state_sha == plan.expected_start_state_sha256
            start_info["expectedMatched"] = matched
            if not matched:
                raise RuntimeCapabilityError(
                    "starting savestate SHA-256 does not match plan expectation"
                )

        start_blocks = adapter.read_ram_blocks()
        start_snapshot_sha = _snapshot_sha256(start_blocks)
        _runtime_same(identity_provider, baseline_runtime, require_real=require_real)
        baseline_layout = build_memory_layout_identity(
            baseline_runtime, start_blocks, require_real=require_real
        )
        base["memoryLayoutIdentity"] = baseline_layout
        baseline_discovery_sha = baseline_layout["discoveryCandidateSha256"]
        assert isinstance(baseline_discovery_sha, str)

        baseline_capture = _capture_branch(
            adapter,
            plan.baseline,
            plan,
            start_state=start_state,
            start_state_sha=start_state_sha,
            start_snapshot_sha=start_snapshot_sha,
            baseline_runtime=baseline_runtime,
            baseline_layout=baseline_layout,
            baseline_discovery_candidate_sha=baseline_discovery_sha,
            identity_provider=identity_provider,
            require_real=require_real,
        )
        intervention_captures = tuple(
            _capture_branch(
                adapter,
                branch,
                plan,
                start_state=start_state,
                start_state_sha=start_state_sha,
                start_snapshot_sha=start_snapshot_sha,
                baseline_runtime=baseline_runtime,
                baseline_layout=baseline_layout,
                baseline_discovery_candidate_sha=baseline_discovery_sha,
                identity_provider=identity_provider,
                require_real=require_real,
            )
            for branch in plan.interventions
        )
        candidates, candidate_total, analysis_truncated = analyze_candidates(
            baseline_capture, intervention_captures, plan, baseline_layout
        )
        base["branches"] = [
            _branch_summary(baseline_capture),
            *[_branch_summary(capture) for capture in intervention_captures],
        ]
        base["candidateCountTotal"] = candidate_total
        base["candidateCountReturned"] = len(candidates)
        base["analysisTruncated"] = analysis_truncated
        base["rankedCandidateChanges"] = candidates

        if require_real and base["authorityClassification"] == AUTHORITY_REAL_ELIGIBLE:
            reason = "OBSERVATION_CAPTURED_R0_2_ELIGIBLE"
            message = (
                "controlled address-aware candidate discovery completed; matching R0.2 "
                "real proof accepted; candidates remain non-semantic until later R0.3 mapping"
            )
        elif require_real:
            reason = "OBSERVATION_CAPTURED_UNVERIFIED"
            message = (
                "controlled address-aware candidate discovery completed without an "
                "accepted matching R0.2 real proof; semantic mapping remains locked"
            )
        else:
            reason = "IMPLEMENTATION_FIXTURE_PASS"
            message = (
                "ROM-free controlled observation-discovery fixture passed; no real WOF "
                "semantic address authority is claimed"
            )
        base.update(status="PASS", reasonCode=reason, message=message, firstFailure=None)
        return base
    except (TrainingFarmError, TypeError, ValueError) as exc:
        base.update(
            status="ERROR",
            reasonCode="OBSERVATION_DISCOVERY_FAILED",
            message=f"{type(exc).__name__}: {exc}",
            semanticMappingUnlocked=False,
            firstFailure={"kind": type(exc).__name__, "detail": str(exc)},
        )
        if not require_real:
            base["authorityClassification"] = AUTHORITY_FIXTURE
        elif base["authorityClassification"] != AUTHORITY_REAL_ELIGIBLE:
            base["authorityClassification"] = AUTHORITY_REAL_UNVERIFIED
        return base


def load_observation_plan(path: str) -> ObservationPlan:
    if type(path) is not str or not path:
        raise ObservationContractError("plan path must be a non-empty string")
    try:
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ObservationContractError(
            f"failed to load observation plan: {type(exc).__name__}: {exc}"
        ) from exc
    return parse_observation_plan(raw)


def load_optional_r02_proof(path: str | None) -> object | None:
    if path is None:
        return None
    if type(path) is not str or not path:
        raise ObservationContractError("R0.2 proof path must be a non-empty string")
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ObservationContractError(
            f"failed to load R0.2 proof JSON: {type(exc).__name__}: {exc}"
        ) from exc


def prerequisite_skip_result(
    plan: ObservationPlan,
    detail: str,
    environment: dict[str, object],
    *,
    r02_proof_provided: bool,
) -> dict[str, object]:
    return {
        "schema": RESULT_SCHEMA,
        "runId": uuid.uuid4().hex,
        "status": "SKIP",
        "reasonCode": "RUNTIME_PREREQUISITE_UNAVAILABLE",
        "message": detail,
        "sourceNamespace": SOURCE_NAMESPACE,
        "experimentId": plan.experiment_id,
        "planSha256": observation_plan_sha256(plan),
        "authorityClassification": AUTHORITY_REAL_UNVERIFIED,
        "semanticMappingUnlocked": False,
        "runtimeIdentity": None,
        "runtimeIdentitySha256": None,
        "memoryLayoutIdentity": None,
        "startingSavestate": {
            "id": plan.starting_savestate_id,
            "sha256": None,
            "expectedSha256": plan.expected_start_state_sha256,
            "expectedMatched": None,
        },
        "horizonFrames": plan.horizon_frames,
        "repetitions": plan.repetitions,
        "captureFrames": list(plan.capture_frames),
        "branches": [],
        "candidateCountTotal": 0,
        "candidateCountReturned": 0,
        "analysisTruncated": False,
        "rankedCandidateChanges": [],
        "proofGate": {
            "provided": r02_proof_provided,
            "accepted": False,
            "reasonCode": "RUNTIME_PREREQUISITE_UNAVAILABLE",
            "message": "real proof compatibility cannot be evaluated without current runtime",
            "compatibilityRule": (
                "all validated R0.2 runtime/ROM/source/backend fields must match exactly; "
                "only run-local processId may differ across CLI processes"
            ),
            "proofRunId": None,
            "proofRuntimeIdentitySha256": None,
        },
        "metadata": {
            "semanticLabel": plan.semantic_label,
            "hypothesis": plan.hypothesis,
            "metadataIsAuthority": False,
        },
        "environment": environment,
        "firstFailure": None,
    }


def error_result(code: str, message: str) -> dict[str, object]:
    return {
        "schema": RESULT_SCHEMA,
        "runId": uuid.uuid4().hex,
        "status": "ERROR",
        "reasonCode": code,
        "message": message,
        "sourceNamespace": SOURCE_NAMESPACE,
        "experimentId": None,
        "authorityClassification": None,
        "semanticMappingUnlocked": False,
        "rankedCandidateChanges": [],
        "proofGate": None,
        "firstFailure": {"kind": code, "detail": message},
    }


def _emit(result: dict[str, object], output: str | None) -> None:
    text = json.dumps(result, indent=2, sort_keys=True)
    if output:
        Path(output).write_text(text + "\n", encoding="utf-8")
    print(text)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Training Farm R0.3 controlled address-aware observation discovery"
    )
    parser.add_argument("--plan", required=True, help="strict R0.3 experiment-plan JSON")
    parser.add_argument(
        "--r0-2-proof",
        help="optional R0.2 determinism result JSON; required for real eligible authority",
    )
    parser.add_argument(
        "--fake",
        action="store_true",
        help="ROM-free implementation fixture; can never unlock semantic mapping",
    )
    parser.add_argument("--output", help="optional compact structured JSON output path")
    args = parser.parse_args(argv)

    try:
        plan = load_observation_plan(args.plan)
        proof = load_optional_r02_proof(args.r0_2_proof)
    except ObservationContractError as exc:
        result = error_result("INVALID_CONTRACT", str(exc))
        _emit(result, args.output)
        return 1

    if args.fake:
        try:
            with TrainingFarmAdapter(DeterministicFakeBackend()) as adapter:
                result = run_observation_discovery(
                    adapter,
                    plan,
                    identity_provider=lambda: build_fixture_runtime_identity(adapter),
                    real_runtime=False,
                    r02_proof=proof,
                )
        except TrainingFarmError as exc:
            result = error_result(
                "OBSERVATION_DISCOVERY_FAILED", f"{type(exc).__name__}: {exc}"
            )
        _emit(result, args.output)
        return 0 if result.get("status") == "PASS" else 1

    report = dependency_probe()
    if not report.runtime_ready:
        result = prerequisite_skip_result(
            plan,
            report.detail,
            report.to_dict(),
            r02_proof_provided=proof is not None,
        )
        _emit(result, args.output)
        return 2

    try:
        with TrainingFarmAdapter(StableRetroFbneoBackend()) as adapter:
            result = run_observation_discovery(
                adapter,
                plan,
                identity_provider=lambda: build_real_runtime_identity(adapter),
                real_runtime=True,
                r02_proof=proof,
            )
    except (TrainingFarmError, OSError) as exc:
        result = error_result(
            "OBSERVATION_DISCOVERY_FAILED", f"{type(exc).__name__}: {exc}"
        )
    _emit(result, args.output)
    return 0 if result.get("status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

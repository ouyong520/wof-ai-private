"""V11 source-owned read-only export contract for running Training Farm workers.

This module publishes evidence that a Training Farm runtime has already produced.
It deliberately has no TrainingFarmAdapter reference and no reset/step/load-state
or worker-orchestration authority.  The Unified Collector consumes the immutable
local artifacts and atomic per-worker ``current.json`` records written here.
"""
from __future__ import annotations

import base64
import copy
import contextlib
import hashlib
import json
import math
import os
import re
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from .identity import SOURCE_NAMESPACE, runtime_identity_sha256, validate_runtime_identity

EXPORTER_VERSION = "wof-training-farm-read-only-exporter-v1"
ARTIFACT_SCHEMA = "wof-training-farm-collector-export-artifact-v1"
RECORD_SCHEMA = "wof-training-farm-collector-export-record-v1"
MEMORY_LAYOUT_SCHEMA = "wof-training-farm-fork-memory-layout-v1"
ADDRESS_KIND = "stable-retro-memory-block-key-plus-byte-offset"
MAX_ACTIVE_WORKERS = 10
MAX_STREAM_SAMPLES = 4096
MAX_RAW_BYTES_PER_ARTIFACT = 16 * 1024 * 1024
MAX_METADATA_BYTES_PER_ARTIFACT = 1024 * 1024
MAX_RECORD_AGE_MS = 24 * 60 * 60 * 1000

_ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,127}\Z")
_PATH_ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,63}\Z")
_SHA_RE = re.compile(r"[0-9a-f]{64}\Z")
_EXPORTER_SOURCE_FILES = (
    "collector_export.py",
    "collector_export_record.schema.json",
    "collector_export_artifact.schema.json",
)

SAFETY = {
    "readOnlyExporter": True,
    "writesGameMemory": False,
    "inputInjection": False,
    "trainingControlAuthority": False,
    "workerLaunchAuthority": False,
    "workerSchedulingAuthority": False,
}


class ExportContractError(ValueError):
    """Malformed or conflicting source-owned export evidence."""


@dataclass(frozen=True)
class ExportRamBlock:
    base_address: int
    data: bytes

    def __post_init__(self) -> None:
        _strict_int(self.base_address, "base_address", 0, 2**63 - 1)
        if type(self.data) is not bytes or not self.data:
            raise ExportContractError("RAM block data must be non-empty bytes")


@dataclass(frozen=True)
class ObservationSample:
    sample_sequence: int
    logical_frame: int | None = None
    step_counter: int | None = None
    ram: bytes | None = None
    ram_blocks: tuple[ExportRamBlock, ...] = ()
    metadata: Mapping[str, Any] | None = None

    def __post_init__(self) -> None:
        _strict_int(self.sample_sequence, "sample_sequence", 1, 2**63 - 1)
        _optional_counter(self.logical_frame, "logical_frame")
        _optional_counter(self.step_counter, "step_counter")
        if self.ram is not None and (type(self.ram) is not bytes or not self.ram):
            raise ExportContractError("sample ram must be non-empty bytes when present")
        if type(self.ram_blocks) is not tuple:
            raise ExportContractError("sample ram_blocks must be a tuple")
        _validate_blocks(self.ram_blocks)
        if self.metadata is not None and type(self.metadata) is not dict:
            raise ExportContractError("sample metadata must be a dict when present")


@dataclass(frozen=True)
class WorkerExportContext:
    worker_id: str
    worker_generation: str
    generation_started_unix_ms: int
    monotonic_sequence: int
    published_at_unix_ms: int
    runtime_identity: Mapping[str, Any]
    logical_frame: int | None = None
    step_counter: int | None = None
    episode_id: str | None = None
    episode_generation: str | None = None
    fork_set_id: str | None = None
    root_id: str | None = None
    branch_id: str | None = None
    active: bool = True
    health: str = "ACTIVE"
    completeness: str = "COMPLETE"

    def __post_init__(self) -> None:
        _path_id(self.worker_id, "worker_id")
        _strict_id(self.worker_generation, "worker_generation")
        _strict_int(self.generation_started_unix_ms, "generation_started_unix_ms", 0, 2**63 - 1)
        _strict_int(self.monotonic_sequence, "monotonic_sequence", 1, 2**63 - 1)
        _strict_int(self.published_at_unix_ms, "published_at_unix_ms", 0, 2**63 - 1)
        if self.published_at_unix_ms < self.generation_started_unix_ms:
            raise ExportContractError("published_at_unix_ms precedes worker generation start")
        if type(self.runtime_identity) is not dict:
            raise ExportContractError("runtime_identity must be a dict")
        _optional_counter(self.logical_frame, "logical_frame")
        _optional_counter(self.step_counter, "step_counter")
        for value, name in (
            (self.episode_id, "episode_id"),
            (self.episode_generation, "episode_generation"),
            (self.fork_set_id, "fork_set_id"),
            (self.root_id, "root_id"),
            (self.branch_id, "branch_id"),
        ):
            if value is not None:
                _strict_id(value, name)
        if type(self.active) is not bool:
            raise ExportContractError("active must be a strict boolean")
        if self.health not in {"ACTIVE", "DEGRADED", "STOPPED"}:
            raise ExportContractError("health must be ACTIVE, DEGRADED, or STOPPED")
        if self.completeness not in {"COMPLETE", "PARTIAL"}:
            raise ExportContractError("completeness must be COMPLETE or PARTIAL")
        if not self.active and self.health != "STOPPED":
            raise ExportContractError("inactive worker record must use health=STOPPED")
        if self.active and self.health == "STOPPED":
            raise ExportContractError("active worker record cannot use health=STOPPED")


def _strict_int(value: object, name: str, low: int, high: int) -> int:
    if type(value) is not int or not low <= value <= high:
        raise ExportContractError(f"{name} must be a strict integer in range {low}..{high}")
    return value


def _optional_counter(value: object, name: str) -> int | None:
    if value is None:
        return None
    return _strict_int(value, name, 0, 2**63 - 1)


def _strict_id(value: object, name: str) -> str:
    if type(value) is not str or not _ID_RE.fullmatch(value):
        raise ExportContractError(f"{name} must be a canonical 1..128 identifier")
    return value


def _path_id(value: object, name: str) -> str:
    if type(value) is not str or not _PATH_ID_RE.fullmatch(value):
        raise ExportContractError(f"{name} must be a filesystem-safe 1..64 identifier")
    return value


def _strict_sha(value: object, name: str) -> str:
    if type(value) is not str or not _SHA_RE.fullmatch(value):
        raise ExportContractError(f"{name} must be lowercase SHA-256 hex")
    return value


def _sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _canonical_bytes(value: object) -> bytes:
    try:
        return json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode("ascii")
    except (TypeError, ValueError) as exc:
        raise ExportContractError(f"value is not canonical JSON: {exc}") from exc


def _sha_json(value: object) -> str:
    return _sha_bytes(_canonical_bytes(value))


def _validate_json_tree(value: object, where: str = "metadata", depth: int = 0) -> None:
    if depth > 16:
        raise ExportContractError(f"{where} exceeds maximum JSON nesting depth")
    if value is None or type(value) in (str, bool, int):
        return
    if type(value) is float:
        if not math.isfinite(value):
            raise ExportContractError(f"{where} contains non-finite float")
        return
    if type(value) is list:
        for index, item in enumerate(value):
            _validate_json_tree(item, f"{where}[{index}]", depth + 1)
        return
    if type(value) is dict:
        for key, item in value.items():
            if type(key) is not str or not key:
                raise ExportContractError(f"{where} contains a non-string/empty object key")
            _validate_json_tree(item, f"{where}.{key}", depth + 1)
        return
    raise ExportContractError(f"{where} contains unsupported JSON value type {type(value).__name__}")


def _bounded_json_copy(value: object, where: str) -> object:
    _validate_json_tree(value, where)
    payload = _canonical_bytes(value)
    if len(payload) > MAX_METADATA_BYTES_PER_ARTIFACT:
        raise ExportContractError(f"{where} exceeds bounded metadata byte limit")
    return json.loads(payload.decode("ascii"))


def _validate_blocks(blocks: Sequence[ExportRamBlock]) -> None:
    previous_base: int | None = None
    previous_end: int | None = None
    for index, block in enumerate(blocks):
        if type(block) is not ExportRamBlock:
            raise ExportContractError(f"RAM block {index} must be ExportRamBlock")
        base = block.base_address
        end = base + len(block.data)
        if end > 2**63:
            raise ExportContractError("RAM block end exceeds supported range")
        if previous_base is not None and base <= previous_base:
            raise ExportContractError("RAM blocks must be strictly ordered by unique base address")
        if previous_end is not None and base < previous_end:
            raise ExportContractError("RAM blocks overlap")
        previous_base = base
        previous_end = end


def _memory_layout(blocks: Sequence[ExportRamBlock]) -> dict[str, object] | None:
    if not blocks:
        return None
    _validate_blocks(blocks)
    body: dict[str, object] = {
        "schema": MEMORY_LAYOUT_SCHEMA,
        "sourceNamespace": SOURCE_NAMESPACE,
        "addressKind": ADDRESS_KIND,
        "blocks": [
            {"index": index, "baseAddress": block.base_address, "length": len(block.data)}
            for index, block in enumerate(blocks)
        ],
    }
    body["layoutIdentitySha256"] = _sha_json(body)
    return body


def validate_memory_layout(value: object) -> dict[str, object]:
    if type(value) is not dict or set(value) != {
        "schema", "sourceNamespace", "addressKind", "blocks", "layoutIdentitySha256"
    }:
        raise ExportContractError("memory layout has a non-canonical structure")
    if value["schema"] != MEMORY_LAYOUT_SCHEMA or value["sourceNamespace"] != SOURCE_NAMESPACE:
        raise ExportContractError("memory layout schema/source mismatch")
    if value["addressKind"] != ADDRESS_KIND:
        raise ExportContractError("memory layout addressKind mismatch")
    blocks = value["blocks"]
    if type(blocks) is not list or not blocks:
        raise ExportContractError("memory layout blocks must be a non-empty array")
    previous_base: int | None = None
    previous_end: int | None = None
    for expected_index, block in enumerate(blocks):
        if type(block) is not dict or set(block) != {"index", "baseAddress", "length"}:
            raise ExportContractError("memory layout block descriptor malformed")
        if block["index"] != expected_index:
            raise ExportContractError("memory layout block indices must be canonical")
        base = _strict_int(block["baseAddress"], "memory layout baseAddress", 0, 2**63 - 1)
        length = _strict_int(block["length"], "memory layout length", 1, 2**63 - 1)
        if previous_base is not None and base <= previous_base:
            raise ExportContractError("memory layout base addresses are not strictly increasing")
        if previous_end is not None and base < previous_end:
            raise ExportContractError("memory layout blocks overlap")
        previous_base = base
        previous_end = base + length
    _strict_sha(value["layoutIdentitySha256"], "memory layout identity")
    authority = {k: copy.deepcopy(value[k]) for k in ("schema", "sourceNamespace", "addressKind", "blocks")}
    if _sha_json(authority) != value["layoutIdentitySha256"]:
        raise ExportContractError("memory layout identity SHA-256 mismatch")
    return copy.deepcopy(value)


def _encode_bytes(value: bytes, where: str) -> dict[str, object]:
    if type(value) is not bytes or not value:
        raise ExportContractError(f"{where} must be non-empty bytes")
    return {
        "encoding": "base64",
        "bytes": len(value),
        "sha256": _sha_bytes(value),
        "data": base64.b64encode(value).decode("ascii"),
    }


def _encode_blocks(blocks: Sequence[ExportRamBlock]) -> dict[str, object] | None:
    if not blocks:
        return None
    layout = _memory_layout(blocks)
    assert layout is not None
    return {
        "memoryLayoutIdentity": layout,
        "blocks": [
            {
                "index": index,
                "baseAddress": block.base_address,
                "length": len(block.data),
                "sha256": _sha_bytes(block.data),
                "encoding": "base64",
                "data": base64.b64encode(block.data).decode("ascii"),
            }
            for index, block in enumerate(blocks)
        ],
    }


def _decode_bytes(value: object, where: str) -> bytes:
    if type(value) is not dict or set(value) != {"encoding", "bytes", "sha256", "data"}:
        raise ExportContractError(f"{where} byte envelope malformed")
    if value["encoding"] != "base64":
        raise ExportContractError(f"{where} encoding must be base64")
    size = _strict_int(value["bytes"], f"{where}.bytes", 1, MAX_RAW_BYTES_PER_ARTIFACT)
    digest = _strict_sha(value["sha256"], f"{where}.sha256")
    data = value["data"]
    if type(data) is not str:
        raise ExportContractError(f"{where}.data must be base64 string")
    try:
        raw = base64.b64decode(data.encode("ascii"), validate=True)
    except Exception as exc:
        raise ExportContractError(f"{where}.data is invalid base64") from exc
    if len(raw) != size or _sha_bytes(raw) != digest:
        raise ExportContractError(f"{where} byte/hash binding mismatch")
    return raw


def _validate_block_snapshot(value: object, where: str) -> dict[str, object] | None:
    if value is None:
        return None
    if type(value) is not dict or set(value) != {"memoryLayoutIdentity", "blocks"}:
        raise ExportContractError(f"{where} block snapshot malformed")
    layout = validate_memory_layout(value["memoryLayoutIdentity"])
    blocks = value["blocks"]
    descriptors = layout["blocks"]
    assert isinstance(descriptors, list)
    if type(blocks) is not list or len(blocks) != len(descriptors):
        raise ExportContractError(f"{where} block count/layout mismatch")
    total = 0
    for index, (block, descriptor) in enumerate(zip(blocks, descriptors)):
        if type(block) is not dict or set(block) != {
            "index", "baseAddress", "length", "sha256", "encoding", "data"
        }:
            raise ExportContractError(f"{where}.blocks[{index}] malformed")
        if block["index"] != index or block["baseAddress"] != descriptor["baseAddress"] or block["length"] != descriptor["length"]:
            raise ExportContractError(f"{where}.blocks[{index}] layout binding mismatch")
        raw = _decode_bytes(
            {
                "encoding": block["encoding"],
                "bytes": block["length"],
                "sha256": block["sha256"],
                "data": block["data"],
            },
            f"{where}.blocks[{index}]",
        )
        total += len(raw)
    if total > MAX_RAW_BYTES_PER_ARTIFACT:
        raise ExportContractError(f"{where} raw byte limit exceeded")
    return copy.deepcopy(value)


def _source_identity() -> tuple[str, dict[str, str]]:
    base = Path(__file__).resolve().parent
    hashes: dict[str, str] = {}
    for name in _EXPORTER_SOURCE_FILES:
        path = base / name
        if not path.is_file():
            raise ExportContractError(f"exporter source identity file missing: {name}")
        hashes[name] = _sha_bytes(path.read_bytes())
    return _sha_json(hashes), hashes


def _runtime_identity(value: Mapping[str, Any]) -> tuple[dict[str, object], str]:
    kind = value.get("runtimeKind") if type(value) is dict else None
    require_real = kind == "real-wof"
    identity = validate_runtime_identity(value, require_real_rom=require_real)
    return identity, runtime_identity_sha256(identity, require_real_rom=require_real)


def _binding_payload(
    *,
    worker_id: str,
    worker_generation: str,
    generation_started_unix_ms: int,
    runtime_identity_sha: str,
    memory_layout_sha: str | None,
    episode_id: str | None,
    episode_generation: str | None,
    fork_set_id: str | None,
    root_id: str | None,
    branch_id: str | None,
) -> dict[str, object]:
    return {
        "sourceNamespace": SOURCE_NAMESPACE,
        "workerId": worker_id,
        "workerGeneration": worker_generation,
        "generationStartedUnixMs": generation_started_unix_ms,
        "runtimeIdentitySha256": runtime_identity_sha,
        "memoryLayoutIdentitySha256": memory_layout_sha,
        "episodeId": episode_id,
        "episodeGeneration": episode_generation,
        "forkSetId": fork_set_id,
        "rootId": root_id,
        "branchId": branch_id,
    }


def capture_binding_sha256(record: Mapping[str, Any]) -> str:
    validated = validate_export_record(record)
    return str(validated["captureBindingSha256"])


def record_is_stale(record: Mapping[str, Any], *, now_unix_ms: int, max_age_ms: int) -> bool:
    validated = validate_export_record(record)
    _strict_int(now_unix_ms, "now_unix_ms", 0, 2**63 - 1)
    _strict_int(max_age_ms, "max_age_ms", 1, MAX_RECORD_AGE_MS)
    published = int(validated["publishedAtUnixMs"])
    age = now_unix_ms - published
    return age < 0 or age > max_age_ms


class TrainingFarmReadOnlyExporter:
    """Local-filesystem publisher for already-produced Training Farm evidence."""

    def __init__(self, export_root: str | os.PathLike[str]):
        raw = os.fspath(export_root)
        if type(raw) is not str or not raw:
            raise ExportContractError("export_root must be a non-empty filesystem path")
        if raw.startswith("\\\\") or raw.startswith("//"):
            raise ExportContractError("export_root must be local-machine storage, not UNC/network path")
        self.root = Path(raw).expanduser().resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def publish(
        self,
        context: WorkerExportContext,
        *,
        ram_snapshot: bytes | None = None,
        ram_blocks_snapshot: Sequence[ExportRamBlock] = (),
        observation_stream: Sequence[ObservationSample] = (),
        memory_layout_identity: Mapping[str, Any] | None = None,
        trajectory_metadata: Mapping[str, Any] | None = None,
        action_result_trajectory: Sequence[Mapping[str, Any]] | None = None,
        root_fork_branch_savestate_metadata: Mapping[str, Any] | None = None,
        runtime_resource_timing_metadata: Mapping[str, Any] | None = None,
        current_action_result_metadata: Mapping[str, Any] | None = None,
    ) -> dict[str, object]:
        if type(context) is not WorkerExportContext:
            raise ExportContractError("context must be WorkerExportContext")
        if ram_snapshot is not None and (type(ram_snapshot) is not bytes or not ram_snapshot):
            raise ExportContractError("ram_snapshot must be non-empty bytes when present")
        if type(ram_blocks_snapshot) not in (tuple, list):
            raise ExportContractError("ram_blocks_snapshot must be a list/tuple")
        _validate_blocks(ram_blocks_snapshot)
        if type(observation_stream) not in (tuple, list):
            raise ExportContractError("observation_stream must be a list/tuple")
        if len(observation_stream) > MAX_STREAM_SAMPLES:
            raise ExportContractError("observation_stream exceeds bounded sample count")
        last_sample_sequence = 0
        for sample in observation_stream:
            if type(sample) is not ObservationSample:
                raise ExportContractError("observation_stream entries must be ObservationSample")
            if sample.sample_sequence <= last_sample_sequence:
                raise ExportContractError("observation_stream sample_sequence must be strictly increasing")
            last_sample_sequence = sample.sample_sequence

        identity, runtime_sha = _runtime_identity(context.runtime_identity)
        process_id = identity["processId"]
        assert type(process_id) is int
        exporter_sha, exporter_files = _source_identity()

        explicit_layout = validate_memory_layout(memory_layout_identity) if memory_layout_identity is not None else None
        derived_layouts: list[dict[str, object]] = []
        snapshot_layout = _memory_layout(ram_blocks_snapshot)
        if snapshot_layout is not None:
            derived_layouts.append(snapshot_layout)
        for sample in observation_stream:
            layout = _memory_layout(sample.ram_blocks)
            if layout is not None:
                derived_layouts.append(layout)
        if explicit_layout is not None:
            derived_layouts.append(explicit_layout)
        layout: dict[str, object] | None = None
        if derived_layouts:
            layout = derived_layouts[0]
            if any(candidate != layout for candidate in derived_layouts[1:]):
                raise ExportContractError("memory layout changed within one exported artifact")
        memory_layout_sha = str(layout["layoutIdentitySha256"]) if layout is not None else None

        raw_total = len(ram_snapshot) if ram_snapshot is not None else 0
        raw_total += sum(len(block.data) for block in ram_blocks_snapshot)
        for sample in observation_stream:
            raw_total += len(sample.ram) if sample.ram is not None else 0
            raw_total += sum(len(block.data) for block in sample.ram_blocks)
        if raw_total > MAX_RAW_BYTES_PER_ARTIFACT:
            raise ExportContractError("artifact exceeds bounded raw byte limit")

        metadata_values = {
            "trajectoryMetadata": trajectory_metadata,
            "actionResultTrajectory": list(action_result_trajectory) if action_result_trajectory is not None else None,
            "rootForkBranchSavestateMetadata": root_fork_branch_savestate_metadata,
            "runtimeResourceTimingMetadata": runtime_resource_timing_metadata,
            "currentActionResultMetadata": current_action_result_metadata,
        }
        normalized_metadata: dict[str, object] = {}
        metadata_total = 0
        for key, value in metadata_values.items():
            if value is None:
                normalized_metadata[key] = None
                continue
            copied = _bounded_json_copy(value, key)
            metadata_total += len(_canonical_bytes(copied))
            normalized_metadata[key] = copied
        sample_rows: list[dict[str, object]] = []
        for sample in observation_stream:
            sample_meta = None if sample.metadata is None else _bounded_json_copy(sample.metadata, "sample.metadata")
            if sample_meta is not None:
                metadata_total += len(_canonical_bytes(sample_meta))
            sample_rows.append({
                "sampleSequence": sample.sample_sequence,
                "logicalFrame": sample.logical_frame,
                "stepCounter": sample.step_counter,
                "ram": None if sample.ram is None else _encode_bytes(sample.ram, "sample.ram"),
                "ramBlocks": _encode_blocks(sample.ram_blocks),
                "metadata": sample_meta,
            })
        if metadata_total > MAX_METADATA_BYTES_PER_ARTIFACT:
            raise ExportContractError("artifact exceeds aggregate metadata byte limit")

        evidence_kinds: list[str] = ["WORKER_RUNTIME_IDENTITY"]
        if ram_snapshot is not None:
            evidence_kinds.append("RAM_SNAPSHOT")
        if ram_blocks_snapshot:
            evidence_kinds.append("RAM_BLOCK_SNAPSHOT")
        if sample_rows:
            evidence_kinds.append("OBSERVATION_STREAM")
        if trajectory_metadata is not None:
            evidence_kinds.append("TRAJECTORY_METADATA")
        if action_result_trajectory is not None:
            evidence_kinds.append("ACTION_RESULT_TRAJECTORY")
        if root_fork_branch_savestate_metadata is not None:
            evidence_kinds.append("ROOT_FORK_BRANCH_SAVESTATE_METADATA")
        if runtime_resource_timing_metadata is not None:
            evidence_kinds.append("RUNTIME_RESOURCE_TIMING_METADATA")
        if current_action_result_metadata is not None:
            evidence_kinds.append("CURRENT_ACTION_RESULT_METADATA")

        binding_payload = _binding_payload(
            worker_id=context.worker_id,
            worker_generation=context.worker_generation,
            generation_started_unix_ms=context.generation_started_unix_ms,
            runtime_identity_sha=runtime_sha,
            memory_layout_sha=memory_layout_sha,
            episode_id=context.episode_id,
            episode_generation=context.episode_generation,
            fork_set_id=context.fork_set_id,
            root_id=context.root_id,
            branch_id=context.branch_id,
        )
        binding_sha = _sha_json(binding_payload)

        artifact: dict[str, object] = {
            "schema": ARTIFACT_SCHEMA,
            "sourceNamespace": SOURCE_NAMESPACE,
            "exporterVersion": EXPORTER_VERSION,
            "exporterSourceIdentitySha256": exporter_sha,
            "exporterSourceFiles": exporter_files,
            "workerId": context.worker_id,
            "workerGeneration": context.worker_generation,
            "generationStartedUnixMs": context.generation_started_unix_ms,
            "processId": process_id,
            "monotonicSequence": context.monotonic_sequence,
            "publishedAtUnixMs": context.published_at_unix_ms,
            "logicalFrame": context.logical_frame,
            "stepCounter": context.step_counter,
            "episodeId": context.episode_id,
            "episodeGeneration": context.episode_generation,
            "forkSetId": context.fork_set_id,
            "rootId": context.root_id,
            "branchId": context.branch_id,
            "runtimeIdentity": identity,
            "runtimeIdentitySha256": runtime_sha,
            "romSha256": identity["romSha256"],
            "farmCandidateSha256": identity["farmCandidateSha256"],
            "memoryLayoutIdentity": layout,
            "captureBindingSha256": binding_sha,
            "active": context.active,
            "health": context.health,
            "completeness": context.completeness,
            "evidenceKinds": evidence_kinds,
            "rawBytes": raw_total,
            "ramSnapshot": None if ram_snapshot is None else _encode_bytes(ram_snapshot, "ram_snapshot"),
            "ramBlocksSnapshot": _encode_blocks(ram_blocks_snapshot),
            "observationStream": sample_rows,
            **normalized_metadata,
            "safety": copy.deepcopy(SAFETY),
        }
        artifact_bytes = _canonical_bytes(artifact)
        artifact_sha = _sha_bytes(artifact_bytes)

        worker_dir = self.root / "workers" / context.worker_id
        artifact_dir = worker_dir / "artifacts" / context.worker_generation
        artifact_rel = Path("workers") / context.worker_id / "artifacts" / context.worker_generation / (
            f"{context.monotonic_sequence:020d}-{artifact_sha}.json"
        )
        artifact_path = self.root / artifact_rel
        current_path = worker_dir / "current.json"

        artifact_dir.mkdir(parents=True, exist_ok=True)

        with _exclusive_worker_lock(worker_dir):
            previous = self._read_current_if_present(current_path)
            previous_identity: str | None = None
            if previous is not None:
                previous_identity = str(previous["recordIdentitySha256"])
                self._validate_progression(previous, context)

            _write_immutable(artifact_path, artifact_bytes)

            record: dict[str, object] = {
            "schema": RECORD_SCHEMA,
            "sourceNamespace": SOURCE_NAMESPACE,
            "exporterVersion": EXPORTER_VERSION,
            "exporterSourceIdentitySha256": exporter_sha,
            "workerId": context.worker_id,
            "workerGeneration": context.worker_generation,
            "generationStartedUnixMs": context.generation_started_unix_ms,
            "processId": process_id,
            "monotonicSequence": context.monotonic_sequence,
            "publishedAtUnixMs": context.published_at_unix_ms,
            "logicalFrame": context.logical_frame,
            "stepCounter": context.step_counter,
            "episodeId": context.episode_id,
            "episodeGeneration": context.episode_generation,
            "forkSetId": context.fork_set_id,
            "rootId": context.root_id,
            "branchId": context.branch_id,
            "runtimeIdentitySha256": runtime_sha,
            "romSha256": identity["romSha256"],
            "farmCandidateSha256": identity["farmCandidateSha256"],
            "memoryLayoutIdentitySha256": memory_layout_sha,
            "captureBindingSha256": binding_sha,
            "active": context.active,
            "health": context.health,
            "completeness": context.completeness,
            "evidenceKinds": evidence_kinds,
            "artifactRelativePath": artifact_rel.as_posix(),
            "artifactSha256": artifact_sha,
            "artifactBytes": len(artifact_bytes),
            "previousRecordIdentitySha256": previous_identity,
                "safety": copy.deepcopy(SAFETY),
            }
            record["recordIdentitySha256"] = _record_identity_sha(record)
            validate_export_record(record)
            _atomic_replace(current_path, _canonical_bytes(record))
            published = validate_export_record(_load_json(current_path))
            if published["recordIdentitySha256"] != record["recordIdentitySha256"]:
                raise ExportContractError("atomic current-record verification lost publication authority")
            return copy.deepcopy(record)

    @staticmethod
    def _validate_progression(previous: Mapping[str, Any], context: WorkerExportContext) -> None:
        prev_generation = str(previous["workerGeneration"])
        prev_started = int(previous["generationStartedUnixMs"])
        prev_sequence = int(previous["monotonicSequence"])
        prev_published = int(previous["publishedAtUnixMs"])
        if context.worker_generation == prev_generation:
            if context.generation_started_unix_ms != prev_started:
                raise ExportContractError("same worker generation changed generation start authority")
            if context.monotonic_sequence <= prev_sequence:
                raise ExportContractError("worker generation sequence must strictly increase")
            if context.published_at_unix_ms < prev_published:
                raise ExportContractError("worker publish timestamp moved backwards")
        else:
            if context.generation_started_unix_ms <= prev_started:
                raise ExportContractError("conflicting/older worker generation cannot replace current record")

    @staticmethod
    def _read_current_if_present(path: Path) -> dict[str, object] | None:
        if not path.exists():
            return None
        return validate_export_record(_load_json(path))


def _record_identity_sha(record: Mapping[str, Any]) -> str:
    payload = {key: copy.deepcopy(value) for key, value in record.items() if key != "recordIdentitySha256"}
    return _sha_json(payload)


def validate_export_record(value: object) -> dict[str, object]:
    keys = {
        "schema", "sourceNamespace", "exporterVersion", "exporterSourceIdentitySha256",
        "workerId", "workerGeneration", "generationStartedUnixMs", "processId",
        "monotonicSequence", "publishedAtUnixMs", "logicalFrame", "stepCounter",
        "episodeId", "episodeGeneration", "forkSetId", "rootId", "branchId",
        "runtimeIdentitySha256", "romSha256", "farmCandidateSha256",
        "memoryLayoutIdentitySha256", "captureBindingSha256", "active", "health",
        "completeness", "evidenceKinds", "artifactRelativePath", "artifactSha256",
        "artifactBytes", "previousRecordIdentitySha256", "safety", "recordIdentitySha256",
    }
    if type(value) is not dict or set(value) != keys:
        raise ExportContractError("export record must exactly match the v1 record envelope")
    if value["schema"] != RECORD_SCHEMA or value["sourceNamespace"] != SOURCE_NAMESPACE:
        raise ExportContractError("export record schema/source mismatch")
    if value["exporterVersion"] != EXPORTER_VERSION:
        raise ExportContractError("export record exporter version mismatch")
    _strict_sha(value["exporterSourceIdentitySha256"], "exporterSourceIdentitySha256")
    worker_id = _path_id(value["workerId"], "workerId")
    generation = _strict_id(value["workerGeneration"], "workerGeneration")
    started = _strict_int(value["generationStartedUnixMs"], "generationStartedUnixMs", 0, 2**63 - 1)
    _strict_int(value["processId"], "processId", 1, 2**63 - 1)
    _strict_int(value["monotonicSequence"], "monotonicSequence", 1, 2**63 - 1)
    published = _strict_int(value["publishedAtUnixMs"], "publishedAtUnixMs", 0, 2**63 - 1)
    if published < started:
        raise ExportContractError("record publish timestamp precedes generation start")
    _optional_counter(value["logicalFrame"], "logicalFrame")
    _optional_counter(value["stepCounter"], "stepCounter")
    for field in ("episodeId", "episodeGeneration", "forkSetId", "rootId", "branchId"):
        if value[field] is not None:
            _strict_id(value[field], field)
    runtime_sha = _strict_sha(value["runtimeIdentitySha256"], "runtimeIdentitySha256")
    _strict_sha(value["romSha256"], "romSha256")
    _strict_sha(value["farmCandidateSha256"], "farmCandidateSha256")
    layout_sha = value["memoryLayoutIdentitySha256"]
    if layout_sha is not None:
        layout_sha = _strict_sha(layout_sha, "memoryLayoutIdentitySha256")
    binding_sha = _strict_sha(value["captureBindingSha256"], "captureBindingSha256")
    expected_binding = _sha_json(_binding_payload(
        worker_id=worker_id,
        worker_generation=generation,
        generation_started_unix_ms=started,
        runtime_identity_sha=runtime_sha,
        memory_layout_sha=layout_sha,
        episode_id=value["episodeId"],
        episode_generation=value["episodeGeneration"],
        fork_set_id=value["forkSetId"],
        root_id=value["rootId"],
        branch_id=value["branchId"],
    ))
    if binding_sha != expected_binding:
        raise ExportContractError("capture binding SHA-256 mismatch")
    if type(value["active"]) is not bool:
        raise ExportContractError("record active must be strict boolean")
    if value["health"] not in {"ACTIVE", "DEGRADED", "STOPPED"}:
        raise ExportContractError("record health invalid")
    if value["completeness"] not in {"COMPLETE", "PARTIAL"}:
        raise ExportContractError("record completeness invalid")
    if (value["active"] is False) != (value["health"] == "STOPPED"):
        raise ExportContractError("record active/health state inconsistent")
    kinds = value["evidenceKinds"]
    if type(kinds) is not list or not kinds or len(kinds) != len(set(kinds)):
        raise ExportContractError("record evidenceKinds malformed")
    if any(type(kind) is not str or not kind for kind in kinds):
        raise ExportContractError("record evidenceKinds must contain non-empty strings")
    rel = value["artifactRelativePath"]
    if type(rel) is not str:
        raise ExportContractError("artifactRelativePath must be a string")
    expected_prefix = f"workers/{worker_id}/artifacts/{generation}/"
    if not rel.startswith(expected_prefix) or Path(rel).is_absolute() or ".." in Path(rel).parts:
        raise ExportContractError("artifactRelativePath escapes worker export namespace")
    _strict_sha(value["artifactSha256"], "artifactSha256")
    _strict_int(value["artifactBytes"], "artifactBytes", 1, MAX_RAW_BYTES_PER_ARTIFACT * 4 + MAX_METADATA_BYTES_PER_ARTIFACT * 2 + 8 * 1024 * 1024)
    previous = value["previousRecordIdentitySha256"]
    if previous is not None:
        _strict_sha(previous, "previousRecordIdentitySha256")
    if value["safety"] != SAFETY:
        raise ExportContractError("record safety invariants mismatch")
    _strict_sha(value["recordIdentitySha256"], "recordIdentitySha256")
    if _record_identity_sha(value) != value["recordIdentitySha256"]:
        raise ExportContractError("record identity SHA-256 mismatch")
    return copy.deepcopy(value)


def validate_export_artifact(value: object) -> dict[str, object]:
    keys = {
        "schema", "sourceNamespace", "exporterVersion", "exporterSourceIdentitySha256",
        "exporterSourceFiles", "workerId", "workerGeneration", "generationStartedUnixMs",
        "processId", "monotonicSequence", "publishedAtUnixMs", "logicalFrame", "stepCounter",
        "episodeId", "episodeGeneration", "forkSetId", "rootId", "branchId",
        "runtimeIdentity", "runtimeIdentitySha256", "romSha256", "farmCandidateSha256",
        "memoryLayoutIdentity", "captureBindingSha256", "active", "health", "completeness",
        "evidenceKinds", "rawBytes", "ramSnapshot", "ramBlocksSnapshot", "observationStream",
        "trajectoryMetadata", "actionResultTrajectory", "rootForkBranchSavestateMetadata",
        "runtimeResourceTimingMetadata", "currentActionResultMetadata", "safety",
    }
    if type(value) is not dict or set(value) != keys:
        raise ExportContractError("export artifact must exactly match the v1 artifact envelope")
    if value["schema"] != ARTIFACT_SCHEMA or value["sourceNamespace"] != SOURCE_NAMESPACE:
        raise ExportContractError("export artifact schema/source mismatch")
    if value["exporterVersion"] != EXPORTER_VERSION:
        raise ExportContractError("export artifact exporter version mismatch")
    source_sha = _strict_sha(value["exporterSourceIdentitySha256"], "exporterSourceIdentitySha256")
    files = value["exporterSourceFiles"]
    if type(files) is not dict or set(files) != set(_EXPORTER_SOURCE_FILES):
        raise ExportContractError("export artifact source file set mismatch")
    for name, digest in files.items():
        if type(name) is not str:
            raise ExportContractError("exporter source file name malformed")
        _strict_sha(digest, f"exporterSourceFiles[{name}]")
    if _sha_json(files) != source_sha:
        raise ExportContractError("exporter source identity SHA-256 mismatch")

    worker_id = _path_id(value["workerId"], "workerId")
    generation = _strict_id(value["workerGeneration"], "workerGeneration")
    started = _strict_int(value["generationStartedUnixMs"], "generationStartedUnixMs", 0, 2**63 - 1)
    process_id = _strict_int(value["processId"], "processId", 1, 2**63 - 1)
    _strict_int(value["monotonicSequence"], "monotonicSequence", 1, 2**63 - 1)
    published = _strict_int(value["publishedAtUnixMs"], "publishedAtUnixMs", 0, 2**63 - 1)
    if published < started:
        raise ExportContractError("artifact publish timestamp precedes generation start")
    _optional_counter(value["logicalFrame"], "logicalFrame")
    _optional_counter(value["stepCounter"], "stepCounter")
    for field in ("episodeId", "episodeGeneration", "forkSetId", "rootId", "branchId"):
        if value[field] is not None:
            _strict_id(value[field], field)

    identity, runtime_sha = _runtime_identity(value["runtimeIdentity"])
    if identity["processId"] != process_id or value["runtimeIdentitySha256"] != runtime_sha:
        raise ExportContractError("artifact runtime/process identity mismatch")
    if value["romSha256"] != identity["romSha256"] or value["farmCandidateSha256"] != identity["farmCandidateSha256"]:
        raise ExportContractError("artifact ROM/Farm identity mismatch")
    layout = None if value["memoryLayoutIdentity"] is None else validate_memory_layout(value["memoryLayoutIdentity"])
    layout_sha = None if layout is None else str(layout["layoutIdentitySha256"])
    expected_binding = _sha_json(_binding_payload(
        worker_id=worker_id,
        worker_generation=generation,
        generation_started_unix_ms=started,
        runtime_identity_sha=runtime_sha,
        memory_layout_sha=layout_sha,
        episode_id=value["episodeId"],
        episode_generation=value["episodeGeneration"],
        fork_set_id=value["forkSetId"],
        root_id=value["rootId"],
        branch_id=value["branchId"],
    ))
    if value["captureBindingSha256"] != expected_binding:
        raise ExportContractError("artifact capture binding mismatch")
    if type(value["active"]) is not bool or value["health"] not in {"ACTIVE", "DEGRADED", "STOPPED"}:
        raise ExportContractError("artifact worker state malformed")
    if (value["active"] is False) != (value["health"] == "STOPPED"):
        raise ExportContractError("artifact active/health state inconsistent")
    if value["completeness"] not in {"COMPLETE", "PARTIAL"}:
        raise ExportContractError("artifact completeness invalid")
    if value["safety"] != SAFETY:
        raise ExportContractError("artifact safety invariants mismatch")

    kinds = value["evidenceKinds"]
    if type(kinds) is not list or not kinds or len(kinds) != len(set(kinds)) or "WORKER_RUNTIME_IDENTITY" not in kinds:
        raise ExportContractError("artifact evidenceKinds malformed")
    raw_bytes = _strict_int(value["rawBytes"], "rawBytes", 0, MAX_RAW_BYTES_PER_ARTIFACT)
    counted = 0
    if value["ramSnapshot"] is not None:
        counted += len(_decode_bytes(value["ramSnapshot"], "ramSnapshot"))
    block_snapshot = _validate_block_snapshot(value["ramBlocksSnapshot"], "ramBlocksSnapshot")
    if block_snapshot is not None:
        for block in block_snapshot["blocks"]:
            counted += int(block["length"])
        block_layout = block_snapshot["memoryLayoutIdentity"]
        if layout is None or block_layout != layout:
            raise ExportContractError("artifact RAM-block snapshot layout mismatch")

    stream = value["observationStream"]
    if type(stream) is not list or len(stream) > MAX_STREAM_SAMPLES:
        raise ExportContractError("artifact observationStream malformed/bounded count exceeded")
    last_seq = 0
    for index, row in enumerate(stream):
        if type(row) is not dict or set(row) != {
            "sampleSequence", "logicalFrame", "stepCounter", "ram", "ramBlocks", "metadata"
        }:
            raise ExportContractError(f"observationStream[{index}] malformed")
        seq = _strict_int(row["sampleSequence"], "sampleSequence", 1, 2**63 - 1)
        if seq <= last_seq:
            raise ExportContractError("observation stream sample sequence is not strictly increasing")
        last_seq = seq
        _optional_counter(row["logicalFrame"], "sample.logicalFrame")
        _optional_counter(row["stepCounter"], "sample.stepCounter")
        if row["ram"] is not None:
            counted += len(_decode_bytes(row["ram"], f"observationStream[{index}].ram"))
        sample_blocks = _validate_block_snapshot(row["ramBlocks"], f"observationStream[{index}].ramBlocks")
        if sample_blocks is not None:
            for block in sample_blocks["blocks"]:
                counted += int(block["length"])
            sample_layout = sample_blocks["memoryLayoutIdentity"]
            if layout is None or sample_layout != layout:
                raise ExportContractError("observation stream memory layout changed")
        if row["metadata"] is not None:
            _bounded_json_copy(row["metadata"], f"observationStream[{index}].metadata")
    if counted != raw_bytes:
        raise ExportContractError("artifact rawBytes does not equal encoded evidence bytes")
    for field in (
        "trajectoryMetadata", "actionResultTrajectory", "rootForkBranchSavestateMetadata",
        "runtimeResourceTimingMetadata", "currentActionResultMetadata",
    ):
        if value[field] is not None:
            _bounded_json_copy(value[field], field)
    return copy.deepcopy(value)


def read_current_record(export_root: str | os.PathLike[str], worker_id: str, *, verify_artifact: bool = True) -> dict[str, object]:
    worker = _path_id(worker_id, "worker_id")
    root = Path(export_root).expanduser().resolve()
    record = validate_export_record(_load_json(root / "workers" / worker / "current.json"))
    if not verify_artifact:
        return record
    artifact_path = (root / str(record["artifactRelativePath"])).resolve()
    try:
        artifact_path.relative_to(root)
    except ValueError as exc:
        raise ExportContractError("artifact path escapes export root") from exc
    raw = artifact_path.read_bytes()
    if len(raw) != record["artifactBytes"] or _sha_bytes(raw) != record["artifactSha256"]:
        raise ExportContractError("artifact bytes/hash do not match current worker record")
    artifact = validate_export_artifact(json.loads(raw.decode("ascii")))
    if (
        artifact["workerId"] != record["workerId"]
        or artifact["workerGeneration"] != record["workerGeneration"]
        or artifact["monotonicSequence"] != record["monotonicSequence"]
        or artifact["captureBindingSha256"] != record["captureBindingSha256"]
        or artifact["runtimeIdentitySha256"] != record["runtimeIdentitySha256"]
        or artifact["evidenceKinds"] != record["evidenceKinds"]
    ):
        raise ExportContractError("current worker record/artifact authority mismatch")
    return record


def discover_current_records(export_root: str | os.PathLike[str], *, verify_artifacts: bool = True) -> list[dict[str, object]]:
    root = Path(export_root).expanduser().resolve()
    workers_dir = root / "workers"
    if not workers_dir.exists():
        return []
    records: list[dict[str, object]] = []
    seen: set[str] = set()
    for child in sorted(workers_dir.iterdir(), key=lambda path: path.name):
        if not child.is_dir() or not (child / "current.json").is_file():
            continue
        worker_id = _path_id(child.name, "worker directory")
        record = read_current_record(root, worker_id, verify_artifact=verify_artifacts)
        if record["workerId"] != worker_id or worker_id in seen:
            raise ExportContractError("duplicate/conflicting worker ID in export registry")
        seen.add(worker_id)
        records.append(record)
    return records


@contextlib.contextmanager
def _exclusive_worker_lock(worker_dir: Path):
    """Serialize publishers for one worker ID with an OS-released local file lock."""
    worker_dir.mkdir(parents=True, exist_ok=True)
    lock_path = worker_dir / ".publish.lock"
    fh = lock_path.open("a+b")
    try:
        if os.name == "nt":
            import msvcrt
            fh.seek(0, os.SEEK_END)
            if fh.tell() == 0:
                fh.write(b"0")
                fh.flush()
            fh.seek(0)
            msvcrt.locking(fh.fileno(), msvcrt.LK_LOCK, 1)
        else:
            import fcntl
            fcntl.flock(fh.fileno(), fcntl.LOCK_EX)
        yield
    finally:
        try:
            if os.name == "nt":
                import msvcrt
                fh.seek(0)
                msvcrt.locking(fh.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
        finally:
            fh.close()


def _load_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="ascii"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ExportContractError(f"failed to read export JSON {path}: {type(exc).__name__}: {exc}") from exc


def _write_immutable(path: Path, payload: bytes) -> None:
    if path.exists():
        current = path.read_bytes()
        if current != payload:
            raise ExportContractError("immutable export artifact path already exists with different bytes")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.tmp-{uuid.uuid4().hex}")
    try:
        with tmp.open("xb") as fh:
            fh.write(payload)
            fh.flush()
            os.fsync(fh.fileno())
        try:
            os.link(tmp, path)
        except FileExistsError:
            current = path.read_bytes()
            if current != payload:
                raise ExportContractError("immutable export artifact raced with conflicting bytes")
        except OSError:
            try:
                with path.open("xb") as out:
                    out.write(payload)
                    out.flush()
                    os.fsync(out.fileno())
            except FileExistsError:
                current = path.read_bytes()
                if current != payload:
                    raise ExportContractError("immutable export artifact raced with conflicting bytes")
    finally:
        try:
            tmp.unlink()
        except FileNotFoundError:
            pass


def _atomic_replace(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.tmp-{uuid.uuid4().hex}")
    try:
        with tmp.open("xb") as fh:
            fh.write(payload)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
    finally:
        try:
            tmp.unlink()
        except FileNotFoundError:
            pass

"""Source-owned Stable-Retro/FBNeo Training Farm fleet runtime.

This module is deliberately a small fleet layer above the existing single
instance :class:`TrainingFarmAdapter`.  It owns process lifecycle, worker
generation identity, in-memory savestate forks, bounded action experiments,
health/resource telemetry, and publication through the existing read-only
exporter.  It does not add a second Collector queue and it never uses host
keyboard/mouse input.

The ``--fake`` mode is an implementation fixture only.  Real WOF authority is
available only when the existing Stable-Retro/FBNeo dependency probe and the
external legal ROM preflight pass.
"""

from __future__ import annotations

import argparse
import ctypes
from ctypes import wintypes
import hashlib
import json
import multiprocessing as mp
import os
import queue
import tempfile
import time
import traceback
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .adapter import CoreFrameInput, RamBlockSnapshot, RuntimeCapabilityError, TrainingFarmAdapter
from .collector_export import (
    ExportRamBlock,
    ObservationSample,
    TrainingFarmReadOnlyExporter,
    WorkerExportContext,
)
from .fake_backend import DeterministicFakeBackend
from .identity import (
    SOURCE_NAMESPACE,
    build_fixture_runtime_identity,
    build_real_runtime_identity,
    runtime_identity_sha256,
)
from .savestate_fork_contract import (
    ForkPlan,
    branch_identity_sha256,
    fork_plan_authority_sha256,
    load_fork_plan,
    memory_layout_identity,
)
from .stable_retro_backend import StableRetroFbneoBackend, dependency_probe


FLEET_SCHEMA = "wof-training-farm-fleet-run-v1"
FLEET_STATUS_SCHEMA = "wof-training-farm-fleet-status-v1"
FLEET_EVENT_SCHEMA = "wof-training-farm-fleet-event-v1"
MAX_WORKERS = 10
SCALE_LADDER = (1, 2, 4, 8, 10)
DEFAULT_PUBLISH_EVERY_FRAMES = 30
DEFAULT_HEARTBEAT_EVERY_FRAMES = 10
DEFAULT_MAX_RESTARTS = 2
DEFAULT_STAGE_SECONDS = 0.0
DEFAULT_RUN_SECONDS = 5.0
MAX_ACTION_RESULTS = 4096


def _now_ms() -> int:
    return time.time_ns() // 1_000_000


def _sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha_json(value: object) -> str:
    return _sha_bytes(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8"))


def _strict_int(value: object, name: str, low: int, high: int) -> int:
    if type(value) is not int or not low <= value <= high:
        raise ValueError(f"{name} must be a strict integer in range {low}..{high}")
    return value


def _atomic_write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def _append_jsonl(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(value, ensure_ascii=False, sort_keys=True) + "\n")
        handle.flush()


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _outside_repo(path: Path) -> bool:
    try:
        path.resolve(strict=False).relative_to(_repo_root().resolve(strict=False))
    except ValueError:
        return True
    return False


def _fleet_source_identity() -> tuple[str, dict[str, str]]:
    base = Path(__file__).resolve().parent
    names = ("fleet.py", "fleet_plan.schema.json")
    files: dict[str, str] = {}
    for name in names:
        path = base / name
        if not path.is_file():
            raise RuntimeCapabilityError(f"fleet source identity file missing: {name}")
        files[name] = _sha_bytes(path.read_bytes())
    return _sha_json(files), files


def _read_plan(path: str | os.PathLike[str] | None) -> ForkPlan:
    chosen = Path(path) if path is not None else Path(__file__).with_name("real_wof_fork_smoke.plan.json")
    return load_fork_plan(chosen)


def _ladder_for_target(target: int, raw: str | None) -> tuple[int, ...]:
    _strict_int(target, "workers", 1, MAX_WORKERS)
    if raw is None:
        values = tuple(value for value in SCALE_LADDER if value <= target)
        if not values or values[-1] != target:
            values = values + (target,)
    else:
        try:
            values = tuple(int(piece.strip()) for piece in raw.split(",") if piece.strip())
        except ValueError as exc:
            raise ValueError("scale ladder must be comma-separated integers") from exc
    if not values or values[-1] != target:
        raise ValueError("scale ladder must end at --workers")
    if any(value < 1 or value > MAX_WORKERS for value in values):
        raise ValueError("scale ladder values must be in range 1..10")
    if any(left >= right for left, right in zip(values, values[1:])):
        raise ValueError("scale ladder must be strictly increasing")
    return values


def _frame_input_neutral() -> CoreFrameInput:
    return CoreFrameInput.neutral()


def _resource_telemetry(pid: int) -> dict[str, object]:
    """Best-effort process telemetry with no third-party dependency."""
    result: dict[str, object] = {
        "pid": pid,
        "available": False,
        "cpuSeconds": None,
        "rssBytes": None,
        "sampledAtUnixMs": _now_ms(),
    }
    if pid <= 0:
        return result
    if os.name == "nt":
        handle = None
        try:
            kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
            psapi = ctypes.WinDLL("psapi", use_last_error=True)
            handle = kernel32.OpenProcess(0x0400 | 0x0010, False, pid)
            if not handle:
                return result

            class FileTime(ctypes.Structure):
                _fields_ = [("low", wintypes.DWORD), ("high", wintypes.DWORD)]

            class MemoryCounters(ctypes.Structure):
                _fields_ = [
                    ("cb", wintypes.DWORD),
                    ("PageFaultCount", wintypes.DWORD),
                    ("PeakWorkingSetSize", ctypes.c_size_t),
                    ("WorkingSetSize", ctypes.c_size_t),
                    ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                    ("PagefileUsage", ctypes.c_size_t),
                    ("PeakPagefileUsage", ctypes.c_size_t),
                ]

            creation, exit_time, kernel, user = FileTime(), FileTime(), FileTime(), FileTime()
            if kernel32.GetProcessTimes(handle, ctypes.byref(creation), ctypes.byref(exit_time), ctypes.byref(kernel), ctypes.byref(user)):
                kernel_ticks = (kernel.high << 32) | kernel.low
                user_ticks = (user.high << 32) | user.low
                result["cpuSeconds"] = (kernel_ticks + user_ticks) / 10_000_000.0
            counters = MemoryCounters()
            counters.cb = ctypes.sizeof(counters)
            if psapi.GetProcessMemoryInfo(handle, ctypes.byref(counters), counters.cb):
                result["rssBytes"] = int(counters.WorkingSetSize)
            result["available"] = result["cpuSeconds"] is not None or result["rssBytes"] is not None
        except Exception:
            return result
        finally:
            if handle:
                try:
                    ctypes.WinDLL("kernel32", use_last_error=True).CloseHandle(handle)
                except Exception:
                    pass
        return result

    proc = Path(f"/proc/{pid}/stat")
    statm = Path(f"/proc/{pid}/statm")
    try:
        fields = proc.read_text(encoding="utf-8").split()
        page_size = os.sysconf("SC_PAGE_SIZE")
        rss_pages = int(statm.read_text(encoding="utf-8").split()[1])
        result["rssBytes"] = rss_pages * page_size
        result["cpuSeconds"] = (int(fields[13]) + int(fields[14])) / float(os.sysconf("SC_CLK_TCK"))
        result["available"] = True
    except (OSError, IndexError, ValueError, TypeError):
        return result
    return result


@dataclass(frozen=True)
class FleetConfig:
    mode: str
    workers: int
    scale_ladder: tuple[int, ...]
    stage_seconds: float
    run_seconds: float
    export_root: Path
    status_root: Path
    plan_path: Path
    rom_path: Path | None
    publish_every_frames: int = DEFAULT_PUBLISH_EVERY_FRAMES
    heartbeat_every_frames: int = DEFAULT_HEARTBEAT_EVERY_FRAMES
    max_restarts: int = DEFAULT_MAX_RESTARTS
    max_frames: int | None = None

    def __post_init__(self) -> None:
        if self.mode not in {"real", "fake"}:
            raise ValueError("mode must be real or fake")
        _strict_int(self.workers, "workers", 1, MAX_WORKERS)
        if not self.scale_ladder or self.scale_ladder[-1] != self.workers:
            raise ValueError("scale ladder must end at workers")
        if self.stage_seconds < 0 or self.run_seconds < 0:
            raise ValueError("stage_seconds and run_seconds must be non-negative")
        _strict_int(self.publish_every_frames, "publish_every_frames", 1, 100_000)
        _strict_int(self.heartbeat_every_frames, "heartbeat_every_frames", 1, 100_000)
        _strict_int(self.max_restarts, "max_restarts", 0, 100)
        if self.max_frames is not None:
            _strict_int(self.max_frames, "max_frames", 1, 10_000_000)
        for path_name, path in (("export_root", self.export_root), ("status_root", self.status_root)):
            if not path.is_absolute():
                raise ValueError(f"{path_name} must be an absolute local path")
            if not _outside_repo(path):
                raise ValueError(f"{path_name} must be outside the repository")


@dataclass
class WorkerSnapshot:
    worker_id: str
    generation: str
    generation_number: int
    process_id: int | None = None
    alive: bool = False
    health: str = "STARTING"
    frame_count: int = 0
    last_heartbeat_unix_ms: int | None = None
    runtime_identity_sha256: str | None = None
    last_error: str | None = None
    restarts: int = 0
    resource: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return {
            "workerId": self.worker_id,
            "workerGeneration": self.generation,
            "generationNumber": self.generation_number,
            "processId": self.process_id,
            "alive": self.alive,
            "health": self.health,
            "frameCount": self.frame_count,
            "lastHeartbeatUnixMs": self.last_heartbeat_unix_ms,
            "runtimeIdentitySha256": self.runtime_identity_sha256,
            "lastError": self.last_error,
            "restarts": self.restarts,
            "resource": dict(self.resource),
        }


@dataclass
class _WorkerHandle:
    snapshot: WorkerSnapshot
    process: mp.Process
    stop_event: Any
    intentionally_stopped: bool = False


def _make_backend(mode: str, rom_path: str | None):
    if mode == "fake":
        return DeterministicFakeBackend()
    return StableRetroFbneoBackend(rom_path)


def _send_event(events: Any, value: dict[str, object]) -> None:
    try:
        events.put_nowait(value)
    except (queue.Full, OSError, ValueError):
        pass


def _blocks_for_export(adapter: TrainingFarmAdapter) -> tuple[ExportRamBlock, ...]:
    return tuple(ExportRamBlock(block.base_address, block.data) for block in adapter.read_ram_blocks())


def _run_action_experiment(
    adapter: TrainingFarmAdapter,
    plan: ForkPlan,
    root_state: bytes,
    root_ram: bytes,
    root_blocks: tuple[ExportRamBlock, ...],
    stop_event: Any,
) -> list[dict[str, object]]:
    results: list[dict[str, object]] = []
    root_sha = _sha_bytes(root_state)
    root_ram_sha = _sha_bytes(root_ram)
    for repetition in range(1, plan.repetitions + 1):
        for branch in plan.branches:
            if stop_event.is_set():
                return results
            adapter.load_state(root_state)
            start_ram = adapter.read_ram()
            frame_count = 0
            for step in branch.steps:
                for _ in range(step.frames):
                    if stop_event.is_set():
                        return results
                    adapter.step_frame(step.frame_input)
                    frame_count += 1
            final_ram = adapter.read_ram()
            final_blocks = _blocks_for_export(adapter)
            results.append({
                "repetition": repetition,
                "branchId": branch.branch_id,
                "branchIdentitySha256": branch_identity_sha256(branch),
                "horizonFrames": branch.horizon_frames,
                "startRamSha256": _sha_bytes(start_ram),
                "finalRamSha256": _sha_bytes(final_ram),
                "finalRamBlocksSha256": _sha_json([
                    {"baseAddress": block.base_address, "dataSha256": _sha_bytes(block.data)}
                    for block in final_blocks
                ]),
                "frameCount": frame_count,
                "rootSavestateSha256": root_sha,
                "rootRamSha256": root_ram_sha,
                "sourceNamespace": SOURCE_NAMESPACE,
                "inputAuthority": "emulator-core-api-only",
            })
    adapter.load_state(root_state)
    if _sha_bytes(adapter.read_ram()) != root_ram_sha:
        raise RuntimeCapabilityError("savestate fork restore did not recover root RAM")
    if tuple((b.base_address, b.data) for b in _blocks_for_export(adapter)) != tuple((b.base_address, b.data) for b in root_blocks):
        raise RuntimeCapabilityError("savestate fork restore did not recover root RAM blocks")
    return results


def _worker_main(
    worker_id: str,
    generation: str,
    generation_number: int,
    generation_started_unix_ms: int,
    config: dict[str, object],
    plan: ForkPlan,
    events: Any,
    stop_event: Any,
) -> None:
    mode = str(config["mode"])
    rom_path = config.get("romPath")
    publish_every = int(config["publishEveryFrames"])
    heartbeat_every = int(config["heartbeatEveryFrames"])
    max_frames = config.get("maxFrames")
    adapter: TrainingFarmAdapter | None = None
    runtime_identity: dict[str, object] | None = None
    last_error: str | None = None
    frame_count = 0
    sequence = 0
    branch_results: list[dict[str, object]] = []
    last_branch: str | None = None
    fleet_identity, fleet_files = _fleet_source_identity()
    root_state = b""
    root_ram = b""
    root_blocks: tuple[ExportRamBlock, ...] = ()
    root_meta: dict[str, object] = {
        "sourceNamespace": SOURCE_NAMESPACE,
        "savestateIdentityKind": "in-memory-process-local",
        "retainedOnDisk": False,
        "forkSetId": plan.fork_set_id,
        "rootId": plan.root_id,
        "forkPlanAuthoritySha256": fork_plan_authority_sha256(plan),
    }

    def publish(*, active: bool, health: str, completeness: str, failure: str | None = None) -> None:
        nonlocal sequence
        if adapter is None or runtime_identity is None:
            return
        sequence += 1
        now = _now_ms()
        ram = adapter.read_ram()
        blocks = _blocks_for_export(adapter)
        layout = memory_layout_identity(tuple(
            RamBlockSnapshot(item.base_address, item.data) for item in blocks
        ))
        episode_id = f"episode-{worker_id}-{generation}"
        current_branch = last_branch or (plan.branches[0].branch_id if plan.branches else None)
        current_result = next(
            (row for row in reversed(branch_results) if row.get("branchId") == current_branch),
            None,
        )
        resource = _resource_telemetry(os.getpid())
        resource.update({
            "frameCount": frame_count,
            "samplePeriodFrames": publish_every,
            "workerGeneration": generation,
            "fleetSourceIdentitySha256": fleet_identity,
        })
        metadata = {
            "fleetSourceIdentitySha256": fleet_identity,
            "fleetSourceFiles": fleet_files,
            "workerId": worker_id,
            "workerGeneration": generation,
            "generationNumber": generation_number,
            "forkPlanAuthoritySha256": fork_plan_authority_sha256(plan),
            "realWorkerLaunched": mode == "real",
            "collectorSelectedAction": False,
            "collectorInjectedInput": False,
        }
        if failure:
            metadata["failure"] = failure
        _send_event(events, {
            "type": "publish",
            "workerId": worker_id,
            "workerGeneration": generation,
            "generationStartedUnixMs": generation_started_unix_ms,
            "monotonicSequence": sequence,
            "publishedAtUnixMs": now,
            "runtimeIdentity": runtime_identity,
            "logicalFrame": frame_count,
            "stepCounter": frame_count,
            "episodeId": episode_id,
            "episodeGeneration": generation,
            "forkSetId": plan.fork_set_id,
            "rootId": plan.root_id,
            "branchId": current_branch,
            "active": active,
            "health": health,
            "completeness": completeness,
            "ramSnapshot": ram,
            "ramBlocksSnapshot": [(block.base_address, block.data) for block in blocks],
            "observationStream": [{
                "sampleSequence": sequence,
                "logicalFrame": frame_count,
                "stepCounter": frame_count,
                "ram": ram,
                "ramBlocks": [(block.base_address, block.data) for block in blocks],
                "metadata": metadata,
            }],
            "memoryLayoutIdentity": layout,
            "trajectoryMetadata": {
                "schema": "wof-training-farm-fleet-trajectory-v1",
                "sourceNamespace": SOURCE_NAMESPACE,
                "trajectoryId": f"trajectory-{worker_id}-{generation}",
                "workerId": worker_id,
                "workerGeneration": generation,
                "fleetSourceIdentitySha256": fleet_identity,
                "forkPlanAuthoritySha256": fork_plan_authority_sha256(plan),
                "actionExperimentResultCount": len(branch_results),
                "failure": failure,
            },
            "actionResultTrajectory": branch_results[-MAX_ACTION_RESULTS:],
            "rootForkBranchSavestateMetadata": {
                **root_meta,
                "rootSavestateSha256": _sha_bytes(root_state) if root_state else None,
                "rootRamSha256": _sha_bytes(root_ram) if root_ram else None,
                "rootMemoryLayoutIdentitySha256": layout.get("layoutIdentitySha256"),
                "currentBranchId": current_branch,
                "currentBranchResult": current_result,
            },
            "runtimeResourceTimingMetadata": resource,
            "currentActionResultMetadata": {
                "sourceNamespace": SOURCE_NAMESPACE,
                "currentBranchId": current_branch,
                "lastActionResult": current_result,
                "collectorSelectedAction": False,
                "collectorInjectedInput": False,
            },
        })

    try:
        adapter = TrainingFarmAdapter(_make_backend(mode, str(rom_path) if rom_path else None))
        adapter.reset()
        runtime_identity = (
            build_real_runtime_identity(adapter, str(rom_path))
            if mode == "real"
            else build_fixture_runtime_identity(adapter)
        )
        runtime_sha = runtime_identity_sha256(runtime_identity, require_real_rom=mode == "real")
        root_state = adapter.save_state()
        root_ram = adapter.read_ram()
        root_blocks = _blocks_for_export(adapter)
        root_meta.update({
            "rootSavestateSha256": _sha_bytes(root_state),
            "rootRamSha256": _sha_bytes(root_ram),
            "rootMemoryLayoutIdentitySha256": memory_layout_identity(tuple(
                RamBlockSnapshot(item.base_address, item.data) for item in root_blocks
            ))["layoutIdentitySha256"],
        })
        branch_results = _run_action_experiment(adapter, plan, root_state, root_ram, root_blocks, stop_event)
        _send_event(events, {
            "type": "started",
            "workerId": worker_id,
            "workerGeneration": generation,
            "processId": os.getpid(),
            "runtimeIdentitySha256": runtime_sha,
            "actionExperimentResults": len(branch_results),
            "sourceNamespace": SOURCE_NAMESPACE,
        })
        frame_index = 0
        default_steps = plan.branches[0].steps if plan.branches else ()
        while not stop_event.is_set():
            for step in default_steps or (type("Step", (), {"frames": 1, "frame_input": _frame_input_neutral()})(),):
                for _ in range(step.frames):
                    if stop_event.is_set():
                        break
                    adapter.step_frame(step.frame_input)
                    frame_count += 1
                    frame_index += 1
                    if frame_count % heartbeat_every == 0:
                        _send_event(events, {
                            "type": "heartbeat",
                            "workerId": worker_id,
                            "workerGeneration": generation,
                            "processId": os.getpid(),
                            "frameCount": frame_count,
                            "runtimeIdentitySha256": runtime_sha,
                            "health": "ACTIVE",
                            "resource": _resource_telemetry(os.getpid()),
                        })
                    if frame_count % publish_every == 0:
                        last_branch = plan.branches[0].branch_id if plan.branches else None
                        publish(active=True, health="ACTIVE", completeness="COMPLETE")
                    if max_frames is not None and frame_count >= int(max_frames):
                        stop_event.set()
                        break
                if stop_event.is_set():
                    break
        publish(active=False, health="STOPPED", completeness="COMPLETE" if frame_count else "PARTIAL")
        _send_event(events, {
            "type": "stopped",
            "workerId": worker_id,
            "workerGeneration": generation,
            "processId": os.getpid(),
            "frameCount": frame_count,
            "health": "STOPPED",
        })
    except Exception as exc:
        last_error = f"{type(exc).__name__}: {exc}"
        _send_event(events, {
            "type": "error",
            "workerId": worker_id,
            "workerGeneration": generation,
            "processId": os.getpid(),
            "frameCount": frame_count,
            "error": last_error,
            "traceback": traceback.format_exc(limit=8),
        })
        if adapter is not None and runtime_identity is not None:
            try:
                publish(active=False, health="STOPPED", completeness="PARTIAL", failure=last_error)
            except Exception:
                pass
    finally:
        if adapter is not None:
            adapter.close()


class TrainingFarmFleet:
    """Supervisor for isolated Stable-Retro/FBNeo worker processes."""

    def __init__(self, config: FleetConfig, plan: ForkPlan):
        self.config = config
        self.plan = plan
        self.fleet_id = f"fleet-{uuid.uuid4().hex}"
        self.ctx = mp.get_context("spawn")
        self.events = self.ctx.Queue(maxsize=4096)
        # Only the supervisor writes the shared source-owned export registry.
        # Worker processes send bounded evidence messages after emulator work.
        self.exporter = TrainingFarmReadOnlyExporter(config.export_root)
        self.handles: dict[str, _WorkerHandle] = {}
        self.generation_numbers: dict[str, int] = {}
        self.restart_counts: dict[str, int] = {}
        self.total_launches = 0
        self.failures: list[dict[str, object]] = []
        self.scale_history: list[dict[str, object]] = []
        self.started_at_unix_ms = _now_ms()
        self.status_path = config.status_root / "fleet_status.json"
        self.events_path = config.status_root / "fleet_events.jsonl"
        self.config.status_root.mkdir(parents=True, exist_ok=True)
        self.config.export_root.mkdir(parents=True, exist_ok=True)
        _atomic_write_json(self.status_path, self.status())

    def _worker_config(self) -> dict[str, object]:
        return {
            "mode": self.config.mode,
            "romPath": str(self.config.rom_path) if self.config.rom_path else None,
            "exportRoot": str(self.config.export_root),
            "publishEveryFrames": self.config.publish_every_frames,
            "heartbeatEveryFrames": self.config.heartbeat_every_frames,
            "maxFrames": self.config.max_frames,
        }

    def _start_worker(self, worker_id: str) -> None:
        old = self.handles.get(worker_id)
        if old is not None and old.process.is_alive():
            return
        number = self.generation_numbers.get(worker_id, 0) + 1
        self.generation_numbers[worker_id] = number
        generation = f"generation-{number:06d}"
        snapshot = WorkerSnapshot(
            worker_id=worker_id,
            generation=generation,
            generation_number=number,
            restarts=self.restart_counts.get(worker_id, 0),
        )
        stop_event = self.ctx.Event()
        process = self.ctx.Process(
            target=_worker_main,
            name=f"WOF-Training-{worker_id}-{generation}",
            args=(
                worker_id,
                generation,
                number,
                _now_ms(),
                self._worker_config(),
                self.plan,
                self.events,
                stop_event,
            ),
        )
        process.daemon = False
        process.start()
        self.total_launches += 1
        snapshot.process_id = process.pid
        snapshot.alive = True
        self.handles[worker_id] = _WorkerHandle(snapshot, process, stop_event)
        self._event("WORKER_STARTED", {"worker": snapshot.to_dict()})

    def _stop_worker(self, worker_id: str, *, intentional: bool = True) -> None:
        handle = self.handles.get(worker_id)
        if handle is None:
            return
        handle.intentionally_stopped = intentional
        handle.stop_event.set()
        handle.process.join(timeout=10.0)
        if handle.process.is_alive():
            handle.process.terminate()
            handle.process.join(timeout=5.0)
        handle.snapshot.alive = False
        handle.snapshot.health = "STOPPED" if intentional else "FAILED"
        if not intentional:
            handle.snapshot.last_error = handle.snapshot.last_error or "worker terminated by supervisor"
        self._event("WORKER_STOPPED", {"worker": handle.snapshot.to_dict(), "intentional": intentional})

    def _publish_from_event(self, value: dict[str, object]) -> None:
        def blocks(raw: object) -> tuple[ExportRamBlock, ...]:
            if not isinstance(raw, (list, tuple)):
                raise ValueError("worker export blocks must be a list")
            return tuple(ExportRamBlock(int(item[0]), bytes(item[1])) for item in raw)

        raw_samples = value.get("observationStream")
        if not isinstance(raw_samples, list):
            raise ValueError("worker export observationStream must be a list")
        samples: list[ObservationSample] = []
        for raw in raw_samples:
            if not isinstance(raw, dict):
                raise ValueError("worker export observation sample must be an object")
            samples.append(ObservationSample(
                sample_sequence=int(raw["sampleSequence"]),
                logical_frame=raw.get("logicalFrame"),
                step_counter=raw.get("stepCounter"),
                ram=None if raw.get("ram") is None else bytes(raw["ram"]),
                ram_blocks=blocks(raw.get("ramBlocks", [])),
                metadata=raw.get("metadata"),
            ))
        context = WorkerExportContext(
            worker_id=str(value["workerId"]),
            worker_generation=str(value["workerGeneration"]),
            generation_started_unix_ms=int(value["generationStartedUnixMs"]),
            monotonic_sequence=int(value["monotonicSequence"]),
            published_at_unix_ms=int(value["publishedAtUnixMs"]),
            runtime_identity=dict(value["runtimeIdentity"]),
            logical_frame=value.get("logicalFrame"),
            step_counter=value.get("stepCounter"),
            episode_id=value.get("episodeId"),
            episode_generation=value.get("episodeGeneration"),
            fork_set_id=value.get("forkSetId"),
            root_id=value.get("rootId"),
            branch_id=value.get("branchId"),
            active=bool(value["active"]),
            health=str(value["health"]),
            completeness=str(value["completeness"]),
        )
        self.exporter.publish(
            context,
            ram_snapshot=None if value.get("ramSnapshot") is None else bytes(value["ramSnapshot"]),
            ram_blocks_snapshot=blocks(value.get("ramBlocksSnapshot", [])),
            observation_stream=tuple(samples),
            memory_layout_identity=value.get("memoryLayoutIdentity"),
            trajectory_metadata=value.get("trajectoryMetadata"),
            action_result_trajectory=value.get("actionResultTrajectory"),
            root_fork_branch_savestate_metadata=value.get("rootForkBranchSavestateMetadata"),
            runtime_resource_timing_metadata=value.get("runtimeResourceTimingMetadata"),
            current_action_result_metadata=value.get("currentActionResultMetadata"),
        )

    def _event(self, kind: str, payload: dict[str, object]) -> None:
        value = {
            "schema": FLEET_EVENT_SCHEMA,
            "sourceNamespace": SOURCE_NAMESPACE,
            "fleetId": self.fleet_id,
            "eventId": uuid.uuid4().hex,
            "atUnixMs": _now_ms(),
            "kind": kind,
            **payload,
        }
        _append_jsonl(self.events_path, value)

    def _drain_events(self) -> None:
        while True:
            try:
                value = self.events.get_nowait()
            except (queue.Empty, OSError, ValueError):
                return
            if not isinstance(value, dict):
                continue
            worker_id = value.get("workerId")
            if not isinstance(worker_id, str) or worker_id not in self.handles:
                continue
            snapshot = self.handles[worker_id].snapshot
            if value.get("type") == "publish":
                try:
                    self._publish_from_event(value)
                except Exception as exc:
                    snapshot.health = "DEGRADED"
                    snapshot.last_error = f"export publication failed: {type(exc).__name__}: {exc}"
                    self.failures.append({
                        "workerId": worker_id,
                        "workerGeneration": snapshot.generation,
                        "atUnixMs": _now_ms(),
                        "error": snapshot.last_error,
                    })
                    self._event("EXPORT_PUBLICATION_ERROR", {"worker": snapshot.to_dict()})
                continue
            snapshot.process_id = value.get("processId") if isinstance(value.get("processId"), int) else snapshot.process_id
            snapshot.last_heartbeat_unix_ms = _now_ms()
            if isinstance(value.get("frameCount"), int):
                snapshot.frame_count = int(value["frameCount"])
            if isinstance(value.get("runtimeIdentitySha256"), str):
                snapshot.runtime_identity_sha256 = value["runtimeIdentitySha256"]
            if isinstance(value.get("health"), str):
                snapshot.health = value["health"]
            if isinstance(value.get("resource"), dict):
                snapshot.resource = dict(value["resource"])
            if value.get("type") == "error":
                snapshot.health = "FAILED"
                snapshot.last_error = str(value.get("error") or "worker error")
                self.failures.append({
                    "workerId": worker_id,
                    "workerGeneration": snapshot.generation,
                    "atUnixMs": _now_ms(),
                    "error": snapshot.last_error,
                })
                self._event("WORKER_ERROR", {"worker": snapshot.to_dict()})
            elif value.get("type") == "started":
                snapshot.health = "ACTIVE"
                self._event("WORKER_READY", {"worker": snapshot.to_dict(), "actionExperimentResults": value.get("actionExperimentResults")})
            elif value.get("type") == "stopped":
                snapshot.health = "STOPPED"

    def _refresh_process_state(self) -> None:
        self._drain_events()
        for worker_id, handle in list(self.handles.items()):
            handle.snapshot.alive = handle.process.is_alive()
            if handle.snapshot.alive and handle.snapshot.process_id:
                telemetry = _resource_telemetry(handle.snapshot.process_id)
                if telemetry.get("available"):
                    handle.snapshot.resource = telemetry
            elif not handle.intentionally_stopped and handle.snapshot.health not in {"STOPPED", "FAILED"}:
                handle.snapshot.health = "FAILED"
                handle.snapshot.last_error = handle.snapshot.last_error or f"worker exited with code {handle.process.exitcode}"
                self.failures.append({
                    "workerId": worker_id,
                    "workerGeneration": handle.snapshot.generation,
                    "atUnixMs": _now_ms(),
                    "error": handle.snapshot.last_error,
                    "exitCode": handle.process.exitcode,
                })
                self._event("WORKER_EXITED", {"worker": handle.snapshot.to_dict()})

    def _write_status(self, *, desired_workers: int, stage: int | None, state: str) -> None:
        self._refresh_process_state()
        value = self.status(desired_workers=desired_workers, stage=stage, state=state)
        _atomic_write_json(self.status_path, value)

    def status(self, *, desired_workers: int = 0, stage: int | None = None, state: str = "CREATED") -> dict[str, object]:
        self._refresh_process_state() if self.handles else None
        workers = [handle.snapshot.to_dict() for _, handle in sorted(self.handles.items())]
        active = sum(1 for row in workers if row["alive"] and row["health"] in {"STARTING", "ACTIVE", "DEGRADED"})
        return {
            "schema": FLEET_STATUS_SCHEMA,
            "sourceNamespace": SOURCE_NAMESPACE,
            "fleetId": self.fleet_id,
            "fleetRunSchema": FLEET_SCHEMA,
            "runtimeMode": self.config.mode,
            "state": state,
            "stageTarget": stage,
            "desiredWorkers": desired_workers,
            "activeWorkers": active,
            "workerCeiling": MAX_WORKERS,
            "scaleLadder": list(self.config.scale_ladder),
            "scaleHistory": list(self.scale_history),
            "workers": workers,
            "failures": list(self.failures),
            "exportRoot": str(self.config.export_root),
            "statusRoot": str(self.config.status_root),
            "forkSetId": self.plan.fork_set_id,
            "forkPlanAuthoritySha256": fork_plan_authority_sha256(self.plan),
            "readOnlyExporter": True,
            "writesGameMemory": False,
            "inputInjection": False,
            "gameplayInputAuthority": "emulator-core-api-only",
            "collectorStartsWorkers": False,
            "collectorSchedulesWorkers": False,
            "realWorkerLaunches": self.total_launches if self.config.mode == "real" else 0,
            "fixtureWorkerLaunches": self.total_launches if self.config.mode == "fake" else 0,
            "updatedAtUnixMs": _now_ms(),
        }

    def scale_to(self, target: int, *, stage: int | None = None) -> None:
        _strict_int(target, "target", 1, MAX_WORKERS)
        current_ids = sorted(self.handles)
        desired_ids = [f"worker-{index:02d}" for index in range(1, target + 1)]
        for worker_id in desired_ids:
            handle = self.handles.get(worker_id)
            if handle is None or not handle.process.is_alive():
                self._start_worker(worker_id)
        for worker_id in sorted(set(current_ids) - set(desired_ids), reverse=True):
            self._stop_worker(worker_id, intentional=True)
        row = {"target": target, "atUnixMs": _now_ms(), "stage": stage, "workerIds": desired_ids}
        self.scale_history.append(row)
        self._event("SCALE_TARGET", row)
        self._write_status(desired_workers=target, stage=stage, state="SCALING")

    def start(self, target: int | None = None) -> None:
        """Start the requested worker count without entering a timed run."""
        count = self.config.workers if target is None else target
        self.scale_to(count, stage=None)

    def stop(self) -> None:
        """Stop every worker cleanly and publish terminal STOPPED records."""
        self.stop_all()

    def restart_worker(self, worker_id: str) -> None:
        """Restart one worker generation while leaving sibling workers running."""
        if worker_id not in self.handles:
            raise ValueError(f"unknown worker id: {worker_id}")
        self._stop_worker(worker_id, intentional=True)
        self.restart_counts[worker_id] = self.restart_counts.get(worker_id, 0) + 1
        self._event("WORKER_MANUAL_RESTART", {"workerId": worker_id, "restart": self.restart_counts[worker_id]})
        self._start_worker(worker_id)
        self._write_status(desired_workers=self.config.workers, stage=None, state="RESTARTING")

    def monitor(self, seconds: float, *, desired_workers: int, stage: int | None = None) -> None:
        deadline = time.monotonic() + max(0.0, seconds)
        while True:
            self._refresh_process_state()
            for worker_id, handle in list(self.handles.items()):
                if handle.intentionally_stopped or handle.process.is_alive() or handle.snapshot.health == "STOPPED":
                    continue
                if self.restart_counts.get(worker_id, 0) < self.config.max_restarts and desired_workers >= int(worker_id.rsplit("-", 1)[1]):
                    self.restart_counts[worker_id] = self.restart_counts.get(worker_id, 0) + 1
                    self._event("WORKER_RESTART_REQUESTED", {"workerId": worker_id, "restart": self.restart_counts[worker_id]})
                    self._start_worker(worker_id)
                else:
                    self._event("WORKER_RESTART_SUPPRESSED", {"workerId": worker_id, "reason": "restart budget exhausted or worker outside target"})
            self._write_status(desired_workers=desired_workers, stage=stage, state="RUNNING")
            if time.monotonic() >= deadline:
                return
            time.sleep(0.1)

    def stop_all(self) -> None:
        for worker_id in sorted(self.handles, reverse=True):
            self._stop_worker(worker_id, intentional=True)
        self._write_status(desired_workers=0, stage=None, state="STOPPED")

    def run(self) -> dict[str, object]:
        state = "RUNNING"
        try:
            for index, target in enumerate(self.config.scale_ladder, start=1):
                self.scale_to(target, stage=index)
                self.monitor(self.config.stage_seconds, desired_workers=target, stage=index)
            self.monitor(self.config.run_seconds, desired_workers=self.config.workers, stage=len(self.config.scale_ladder))
            state = "COMPLETE"
        except Exception as exc:
            state = "FAILED"
            self.failures.append({"atUnixMs": _now_ms(), "error": f"{type(exc).__name__}: {exc}"})
            self._event("FLEET_ERROR", {"error": self.failures[-1]["error"]})
        finally:
            self.stop_all()
        if state == "COMPLETE" and self.failures:
            state = "COMPLETE_WITH_FAILURES"
        result = self.status(desired_workers=0, stage=None, state=state)
        result.update({
            "schema": FLEET_SCHEMA,
            "startedAtUnixMs": self.started_at_unix_ms,
            "completedAtUnixMs": _now_ms(),
            "statusPath": str(self.status_path),
            "eventsPath": str(self.events_path),
            "fixtureOnly": self.config.mode == "fake",
            "realRuntimeProof": self.config.mode == "real" and state == "COMPLETE" and not self.failures,
        })
        _atomic_write_json(self.status_path, result)
        return result


def _default_status_root() -> Path:
    base = os.environ.get("LOCALAPPDATA") if os.name == "nt" else os.environ.get("XDG_STATE_HOME")
    if base:
        return Path(base) / "WofTrainingFarm" / "fleet"
    return Path.home() / ".local" / "state" / "WofTrainingFarm" / "fleet"


def _default_export_root() -> Path:
    base = os.environ.get("LOCALAPPDATA") if os.name == "nt" else os.environ.get("XDG_STATE_HOME")
    if base:
        return Path(base) / "WofTrainingFarm" / "exports"
    return Path.home() / ".local" / "state" / "WofTrainingFarm" / "exports"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="WOF Stable-Retro/FBNeo 1->2->4->8->10 Training Farm fleet")
    parser.add_argument("--workers", type=int, default=10)
    parser.add_argument("--scale-ladder", default=None, help="strict increasing comma-separated ladder ending at --workers")
    parser.add_argument("--stage-seconds", type=float, default=DEFAULT_STAGE_SECONDS)
    parser.add_argument("--run-seconds", type=float, default=DEFAULT_RUN_SECONDS)
    parser.add_argument("--export-root", default=str(_default_export_root()))
    parser.add_argument("--status-root", default=str(_default_status_root()))
    parser.add_argument("--plan", default=str(Path(__file__).with_name("real_wof_fork_smoke.plan.json")))
    parser.add_argument("--rom", default=None, help="external legal FBNeo ROM zip; defaults to WOF_ROM_PATH")
    parser.add_argument("--fake", action="store_true", help="fixture-only mode; never real WOF authority")
    parser.add_argument("--max-restarts", type=int, default=DEFAULT_MAX_RESTARTS)
    parser.add_argument("--publish-every-frames", type=int, default=DEFAULT_PUBLISH_EVERY_FRAMES)
    parser.add_argument("--heartbeat-every-frames", type=int, default=DEFAULT_HEARTBEAT_EVERY_FRAMES)
    parser.add_argument("--max-frames", type=int, default=None)
    return parser


def run_from_args(args: argparse.Namespace) -> tuple[int, dict[str, object]]:
    mode = "fake" if args.fake else "real"
    workers = _strict_int(args.workers, "workers", 1, MAX_WORKERS)
    ladder = _ladder_for_target(workers, args.scale_ladder)
    plan = _read_plan(args.plan)
    export_root = Path(args.export_root).expanduser().resolve()
    status_root = Path(args.status_root).expanduser().resolve()
    rom_path = Path(args.rom).expanduser().resolve() if args.rom else None
    if mode == "real":
        report = dependency_probe(rom_path)
        if not report.runtime_ready:
            result = {
                "schema": FLEET_SCHEMA,
                "sourceNamespace": SOURCE_NAMESPACE,
                "state": "WAITING_PREREQUISITE",
                "runtimeMode": mode,
                "realRuntimeProof": False,
                "fixtureOnly": False,
                "realWorkerLaunches": 0,
                "dependency": report.to_dict(),
                "requiredOwnerInput": "external legal WOF ROM path and pinned Stable-Retro/FBNeo environment" if not report.rom_configured or not report.rom_exists else None,
            }
            print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
            return 2, result
    try:
        config = FleetConfig(
            mode=mode,
            workers=workers,
            scale_ladder=ladder,
            stage_seconds=float(args.stage_seconds),
            run_seconds=float(args.run_seconds),
            export_root=export_root,
            status_root=status_root,
            plan_path=Path(args.plan).expanduser().resolve(),
            rom_path=rom_path,
            publish_every_frames=args.publish_every_frames,
            heartbeat_every_frames=args.heartbeat_every_frames,
            max_restarts=args.max_restarts,
            max_frames=args.max_frames,
        )
        result = TrainingFarmFleet(config, plan).run()
    except Exception as exc:
        result = {
            "schema": FLEET_SCHEMA,
            "sourceNamespace": SOURCE_NAMESPACE,
            "state": "FAILED",
            "runtimeMode": mode,
            "error": f"{type(exc).__name__}: {exc}",
        }
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
        return 1, result
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result.get("state") == "COMPLETE" else 1, result


def main(argv: list[str] | None = None) -> int:
    return run_from_args(build_parser().parse_args(argv))[0]


if __name__ == "__main__":
    raise SystemExit(main())

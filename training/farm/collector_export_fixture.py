"""ROM-free deterministic V11 Training Farm exporter fixture.

Creates source-owned export records for up to ten fake workers.  It never starts
or schedules a real emulator worker and never resets, steps, loads state, or
chooses gameplay input.  The fixture exists only to exercise V11 worker identity
isolation and the stable-retro-fbneo exporter/adapter boundary.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from .adapter import TrainingFarmAdapter
from .collector_export import (
    ExportRamBlock,
    ObservationSample,
    TrainingFarmReadOnlyExporter,
    WorkerExportContext,
)
from .fake_backend import DeterministicFakeBackend
from .identity import build_fixture_runtime_identity

MAX_FIXTURE_WORKERS = 10


def _strict_workers(value: object) -> int:
    if type(value) is not int or not 1 <= value <= MAX_FIXTURE_WORKERS:
        raise ValueError("workers must be a strict integer in range 1..10")
    return value


def _fixture_identity() -> dict[str, object]:
    # Runtime identity construction reads backend identity only.  No reset/step/
    # save/load operation is called by this fixture.
    with TrainingFarmAdapter(DeterministicFakeBackend()) as adapter:
        return build_fixture_runtime_identity(adapter)


def build_fixture(
    export_root: str | Path,
    *,
    workers: int = MAX_FIXTURE_WORKERS,
    now_unix_ms: int | None = None,
) -> dict[str, object]:
    count = _strict_workers(workers)
    if now_unix_ms is None:
        now_unix_ms = time.time_ns() // 1_000_000
    if type(now_unix_ms) is not int or now_unix_ms < 10_000:
        raise ValueError("now_unix_ms must be a strict non-negative current-like integer")

    identity = _fixture_identity()
    exporter = TrainingFarmReadOnlyExporter(export_root)
    records: list[dict[str, object]] = []
    for index in range(count):
        worker_id = f"fixture-worker-{index:02d}"
        generation = f"fixture-generation-{index:02d}"
        started = now_unix_ms - 2_000 + index
        published = now_unix_ms - 1_000 + index
        base = 0x1000 + index * 0x100
        ram = bytes(((index + offset + 1) & 0xFF) for offset in range(32))
        blocks = (
            ExportRamBlock(base, ram[:16]),
            ExportRamBlock(base + 0x40, ram[16:]),
        )
        record = exporter.publish(
            WorkerExportContext(
                worker_id=worker_id,
                worker_generation=generation,
                generation_started_unix_ms=started,
                monotonic_sequence=1,
                published_at_unix_ms=published,
                runtime_identity=identity,
                logical_frame=100 + index,
                step_counter=100 + index,
                episode_id=f"fixture-episode-{index:02d}",
                episode_generation=f"fixture-episode-generation-{index:02d}",
                fork_set_id=f"fixture-fork-{index:02d}",
                root_id=f"fixture-root-{index:02d}",
                branch_id=f"fixture-branch-{index:02d}",
            ),
            ram_snapshot=ram,
            ram_blocks_snapshot=blocks,
            observation_stream=(
                ObservationSample(
                    1,
                    logical_frame=100 + index,
                    step_counter=100 + index,
                    ram=ram,
                    ram_blocks=blocks,
                    metadata={"fixtureWorkerIndex": index, "sourceOwned": True},
                ),
            ),
            trajectory_metadata={
                "trajectoryId": f"fixture-trajectory-{index:02d}",
                "fixtureWorkerIndex": index,
            },
            action_result_trajectory=[
                {
                    "logicalFrame": 100 + index,
                    "existingActionMask": index,
                    "collectorSelectedAction": False,
                    "resultMarker": f"fixture-result-{index:02d}",
                }
            ],
            root_fork_branch_savestate_metadata={
                "forkSetId": f"fixture-fork-{index:02d}",
                "rootId": f"fixture-root-{index:02d}",
                "branchId": f"fixture-branch-{index:02d}",
                "savestateIdentityKind": "fixture-metadata-only",
            },
            runtime_resource_timing_metadata={
                "fixtureWorkerIndex": index,
                "samplePeriodNs": 16_666_667,
                "realWorkerLaunched": False,
            },
            current_action_result_metadata={
                "collectorSelectedAction": False,
                "collectorInjectedInput": False,
                "existingResultOnly": True,
            },
        )
        records.append(record)

    return {
        "schema": "wof-training-farm-collector-export-fixture-summary-v1",
        "sourceNamespace": "stable-retro-fbneo",
        "fixtureOnly": True,
        "realWorkerLaunches": 0,
        "collectorCallsReset": False,
        "collectorCallsStep": False,
        "collectorCallsLoadState": False,
        "workers": count,
        "workerIds": [record["workerId"] for record in records],
        "workerGenerations": [record["workerGeneration"] for record in records],
        "captureBindingSha256": [record["captureBindingSha256"] for record in records],
        "exportRoot": str(Path(export_root).expanduser().resolve()),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build ROM-free V11 Training Farm exporter fixture")
    parser.add_argument("--export-root", required=True)
    parser.add_argument("--workers", type=int, default=MAX_FIXTURE_WORKERS)
    args = parser.parse_args(argv)
    try:
        summary = build_fixture(args.export_root, workers=args.workers)
    except (OSError, ValueError) as exc:
        print(json.dumps({"status": "ERROR", "error": f"{type(exc).__name__}: {exc}"}, sort_keys=True))
        return 1
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

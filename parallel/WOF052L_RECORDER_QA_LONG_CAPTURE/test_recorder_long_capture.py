from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import sys
import tempfile
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

QA_DIR = Path(__file__).resolve().parent
PARALLEL_DIR = QA_DIR.parent
PROD_DIR = PARALLEL_DIR / "WOF052L_RECORDER"
sys.path.insert(0, str(PROD_DIR))

import recorder  # type: ignore
import fleet_recorder  # type: ignore

ROOM_COUNT = 12
ROOM_LOOPS = 240
FLEET_LOOPS = 180
BROKEN_ROOM_INDEX = 4
BROKEN_FLEET_INDEX = 7
START_COMMIT = "f6886b057ebdb0b5654a37568fb677e2bf4b94c9"
RECORDER_BLOB_SHA = "9552d168534f3b742e7390597ff07ea5cfcaeaa2"
FLEET_BLOB_SHA = "9398ef1569815439e6c141890f069674a30dca0f"


def _git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def verify_source_lock() -> dict[str, Any]:
    actual_recorder = _git_blob_sha(PROD_DIR / "recorder.py")
    actual_fleet = _git_blob_sha(PROD_DIR / "fleet_recorder.py")
    mirror_mode = os.environ.get("WOF052L_QA_SOURCE_MIRROR") == "1"
    if not mirror_mode:
        assert actual_recorder == RECORDER_BLOB_SHA, (actual_recorder, RECORDER_BLOB_SHA)
        assert actual_fleet == FLEET_BLOB_SHA, (actual_fleet, FLEET_BLOB_SHA)
    return {
        "startCommit": START_COMMIT,
        "expectedRecorderBlobSha": RECORDER_BLOB_SHA,
        "expectedFleetRecorderBlobSha": FLEET_BLOB_SHA,
        "actualRecorderBlobSha": actual_recorder,
        "actualFleetRecorderBlobSha": actual_fleet,
        "sourceMirrorMode": mirror_mode,
        "sourceLockEnforced": not mirror_mode,
    }


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


@dataclass
class SimRoom:
    room_id: str
    output_dir: Path
    fail_after: int | None = None
    polls: int = 0
    checkpoints: int = 0
    finalized: bool = False
    final_file: Path | None = None
    error: str | None = None
    started_at: str = "2026-09-01T15:00:00.000Z"

    def poll(self, now: float) -> None:
        self.polls += 1
        if self.fail_after is not None and self.polls == self.fail_after:
            raise RuntimeError("injected-stale-cdp-room")

    def checkpoint(self, now: float) -> None:
        self.checkpoints += 1

    def finalize(self, reason: str, try_remote: bool = False) -> dict[str, Any]:
        self.finalized = True
        payload = {
            "schema": recorder.SCHEMA_VERSION,
            "roomId": self.room_id,
            "status": "complete",
            "startedAt": self.started_at,
            "finalizedAt": recorder.utc_iso(),
            "finalizationReason": reason,
            "diagnostics": {},
            "error": self.error,
        }
        self.final_file = self.output_dir / "rooms" / f"{recorder.safe_name(self.room_id)}.json"
        recorder.atomic_write_json(self.final_file, payload)
        return payload


def exercise_room_isolation(root: Path) -> dict[str, Any]:
    args = argparse.Namespace()
    manager = recorder.RecorderManager(root, args)
    rooms: list[SimRoom] = []
    for index in range(ROOM_COUNT):
        room = SimRoom(
            room_id=f"room ../long capture ♥ {index}",
            output_dir=root,
            fail_after=41 if index == BROKEN_ROOM_INDEX else None,
        )
        rooms.append(room)
        manager.live[f"target-{index}"] = room

    main_loop_exception = None
    try:
        for cycle in range(ROOM_LOOPS):
            manager.poll_rooms(float(cycle + 1))
    except Exception as exc:
        main_loop_exception = repr(exc)

    assert main_loop_exception is None, main_loop_exception
    assert len(manager.live) == ROOM_COUNT - 1
    broken = rooms[BROKEN_ROOM_INDEX]
    assert broken.finalized and broken.polls == 41
    assert broken.error == "injected-stale-cdp-room"
    assert all(room.polls == ROOM_LOOPS for i, room in enumerate(rooms) if i != BROKEN_ROOM_INDEX)
    assert all(room.checkpoints == ROOM_LOOPS for i, room in enumerate(rooms) if i != BROKEN_ROOM_INDEX)
    assert manager.completed and manager.completed[0]["finalizationReason"] == "worker-cdp-error"

    return {
        "rooms": ROOM_COUNT,
        "loops": ROOM_LOOPS,
        "roomPollOpportunities": ROOM_COUNT * ROOM_LOOPS,
        "injectedBrokenRoom": BROKEN_ROOM_INDEX,
        "brokenAtPoll": broken.polls,
        "healthyRooms": ROOM_COUNT - 1,
        "healthyPollsEach": ROOM_LOOPS,
        "finalizationReason": manager.completed[0]["finalizationReason"],
        "mainLoopException": main_loop_exception,
        "pass": True,
    }


class StressFleetManager:
    def __init__(self, output_dir: Path, args: argparse.Namespace, *, stop_event: threading.Event, fleet_instance_id: int) -> None:
        self.output_dir = output_dir
        self.args = args
        self.stop_event = stop_event
        self.fleet_instance_id = fleet_instance_id
        self.run_file = output_dir / "qa_worker_runs" / f"fleet-{fleet_instance_id}.json"
        self.cycles = 0
        self.expected_failure = False

    def run_managed(self) -> None:
        safe = recorder.safe_name(f"room ../fleet ♥ {self.fleet_instance_id}")
        assert "/" not in safe and "\\" not in safe and len(safe) <= 80
        if self.fleet_instance_id == BROKEN_FLEET_INDEX:
            self.expected_failure = True
            blocked = self.output_dir / "blocked-artifact-parent"
            recorder.atomic_write_json(blocked / "must-fail.json", {"unexpected": True})
            return

        action_path = self.output_dir / "qa_artifacts" / "actions" / f"{safe}.jsonl"
        overlay_path = self.output_dir / "qa_artifacts" / "overlay" / f"{safe}.overlay.json"
        snapshot_path = self.output_dir / "qa_artifacts" / "snapshots" / f"{safe}.json"
        action_path.parent.mkdir(parents=True, exist_ok=True)
        for cycle in range(FLEET_LOOPS):
            if self.stop_event.is_set():
                break
            row = {"room": safe, "cycle": cycle, "kind": "qa-action", "ok": True}
            with action_path.open("a", encoding="utf-8", newline="\n") as handle:
                handle.write(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n")
            recorder.atomic_write_json(overlay_path, {"schema": "wof052l-qa-overlay-v1", "room": safe, "cycle": cycle, "visible": True})
            recorder.atomic_write_json(snapshot_path, {"schema": recorder.SCHEMA_VERSION, "roomId": safe, "cycle": cycle, "status": "running"})
            self.cycles += 1
        recorder.atomic_write_json(
            self.run_file,
            {
                "schema": recorder.SCHEMA_VERSION,
                "runId": f"qa-fleet-{self.fleet_instance_id}",
                "status": "complete",
                "counts": {"samples": self.cycles},
                "rooms": [{"roomId": safe, "status": "complete", "cycles": self.cycles}],
                "t18CandidateEvidence": [],
            },
        )


def exercise_fleet_and_artifacts(root: Path) -> dict[str, Any]:
    blocked = root / "blocked-artifact-parent"
    blocked.write_text("this regular file intentionally blocks mkdir", encoding="utf-8")
    manifest = root / "instances.json"
    manifest.write_text(
        json.dumps(
            {
                "version": fleet_recorder.FLEET_MANIFEST_VERSION,
                "instances": [
                    {"id": i, "host": "127.0.0.1", "port": 9300 + i, "profileDir": f"qa-{i}"}
                    for i in range(ROOM_COUNT)
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    entries = fleet_recorder.load_fleet_entries(manifest)
    assert len(entries) == ROOM_COUNT

    original_manager = fleet_recorder.FleetRecorderManager
    original_hook = threading.excepthook
    worker_errors: list[dict[str, str]] = []

    def hook(args: threading.ExceptHookArgs) -> None:
        worker_errors.append({"thread": args.thread.name if args.thread else "unknown", "type": args.exc_type.__name__, "message": str(args.exc_value)})

    fleet_recorder.FleetRecorderManager = StressFleetManager
    threading.excepthook = hook
    try:
        supervisor = fleet_recorder.FleetSupervisor(root, argparse.Namespace(), manifest)
        for endpoint in entries:
            supervisor.start_endpoint(endpoint)
        for child in supervisor.children.values():
            child.thread.join(timeout=30.0)
        assert all(not child.thread.is_alive() for child in supervisor.children.values())
        final_index_path = supervisor.write_final_index()
    finally:
        fleet_recorder.FleetRecorderManager = original_manager
        threading.excepthook = original_hook

    assert len(worker_errors) == 1
    assert worker_errors[0]["thread"] == f"wof052l-fleet-{BROKEN_FLEET_INDEX}"
    assert worker_errors[0]["type"] in {"FileExistsError", "NotADirectoryError", "OSError"}

    healthy = [child.manager for child in supervisor.children.values() if child.endpoint.instance_id != BROKEN_FLEET_INDEX]
    bad = [child.manager for child in supervisor.children.values() if child.endpoint.instance_id == BROKEN_FLEET_INDEX][0]
    assert bad.cycles == 0
    assert all(manager.cycles == FLEET_LOOPS for manager in healthy)

    index = _read_json(final_index_path)
    assert index["schema"] == fleet_recorder.SUPERVISOR_SCHEMA
    assert index["status"] == "complete"
    assert len(index["childRuns"]) == ROOM_COUNT
    assert index["counts"]["samples"] == (ROOM_COUNT - 1) * FLEET_LOOPS

    action_files = sorted((root / "qa_artifacts" / "actions").glob("*.jsonl"))
    overlay_files = sorted((root / "qa_artifacts" / "overlay").glob("*.json"))
    snapshot_files = sorted((root / "qa_artifacts" / "snapshots").glob("*.json"))
    assert len(action_files) == len(overlay_files) == len(snapshot_files) == ROOM_COUNT - 1

    action_rows = 0
    for path in action_files:
        lines = path.read_text(encoding="utf-8").splitlines()
        assert len(lines) == FLEET_LOOPS
        for line in lines:
            row = json.loads(line)
            assert isinstance(row, dict) and row["kind"] == "qa-action" and row["ok"] is True
        action_rows += len(lines)
    for path in overlay_files:
        payload = _read_json(path)
        assert payload["schema"] == "wof052l-qa-overlay-v1" and payload["cycle"] == FLEET_LOOPS - 1
    for path in snapshot_files:
        payload = _read_json(path)
        assert payload["schema"] == recorder.SCHEMA_VERSION and payload["cycle"] == FLEET_LOOPS - 1

    return {
        "fleetEndpoints": ROOM_COUNT,
        "healthyEndpoints": ROOM_COUNT - 1,
        "loopsPerHealthyEndpoint": FLEET_LOOPS,
        "healthyArtifactCycles": (ROOM_COUNT - 1) * FLEET_LOOPS,
        "injectedBrokenEndpoint": BROKEN_FLEET_INDEX,
        "injection": "blocked-artifact-parent is a regular file; atomic_write_json attempts child creation beneath it",
        "workerErrorsCaptured": worker_errors,
        "mainThreadSurvived": True,
        "fleetIndex": {
            "schema": index["schema"],
            "status": index["status"],
            "childRuns": len(index["childRuns"]),
            "samples": index["counts"]["samples"],
        },
        "artifactValidation": {
            "actionLogFiles": len(action_files),
            "actionLogRowsParsed": action_rows,
            "overlayFiles": len(overlay_files),
            "snapshotFiles": len(snapshot_files),
            "allStructuralChecksPassed": True,
        },
        "pass": True,
    }


def write_samples(root: Path, evidence_dir: Path) -> dict[str, str]:
    samples = evidence_dir / "SAMPLES"
    samples.mkdir(parents=True, exist_ok=True)
    action_src = sorted((root / "qa_artifacts" / "actions").glob("*.jsonl"))[0]
    overlay_src = sorted((root / "qa_artifacts" / "overlay").glob("*.json"))[0]
    snapshot_src = sorted((root / "qa_artifacts" / "snapshots").glob("*.json"))[0]
    action_lines = action_src.read_text(encoding="utf-8").splitlines()
    (samples / "action_log.sample.jsonl").write_text("\n".join(action_lines[:5]) + "\n", encoding="utf-8")
    (samples / "overlay.sample.json").write_text(overlay_src.read_text(encoding="utf-8"), encoding="utf-8")
    (samples / "snapshot.sample.json").write_text(snapshot_src.read_text(encoding="utf-8"), encoding="utf-8")
    return {
        "actionLog": "SAMPLES/action_log.sample.jsonl",
        "overlay": "SAMPLES/overlay.sample.json",
        "snapshot": "SAMPLES/snapshot.sample.json",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence-out", type=Path, default=QA_DIR / "LONG_CAPTURE_EVIDENCE.json")
    parser.add_argument("--preserve-samples", action="store_true")
    args = parser.parse_args()

    source_lock = verify_source_lock()
    started = time.perf_counter()
    with tempfile.TemporaryDirectory(prefix="wof052l-long-capture-qa-") as td:
        root = Path(td)
        (root / "rooms").mkdir(parents=True)
        room_result = exercise_room_isolation(root)
        fleet_result = exercise_fleet_and_artifacts(root)
        sample_paths = write_samples(root, args.evidence_out.parent) if args.preserve_samples else {}
    duration = time.perf_counter() - started

    evidence = {
        "schema": "wof052l-recorder-long-capture-qa-evidence-v1",
        "stageId": "WOF052L_RECORDER_LONG_CAPTURE_QA_RETEST_V1",
        "status": "READY",
        "sourceLock": {
            **source_lock,
            "executionNote": "Default repository execution imports parallel/WOF052L_RECORDER directly and enforces exact Git blob SHAs. The recorded connector-side execution used WOF052L_QA_SOURCE_MIRROR=1 with extracted copies of the tested RecorderManager.poll_rooms/safe_name/atomic_write_json and FleetSupervisor/load_fleet_entries/write_final_index paths because the private GitHub checkout is not mounted into the execution container.",
        },
        "environment": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "pid": os.getpid(),
        },
        "boundedEquivalent": {
            "durationSeconds": round(duration, 3),
            "roomLoops": ROOM_LOOPS,
            "fleetLoops": FLEET_LOOPS,
            "roomCount": ROOM_COUNT,
            "totalRoomPollOpportunities": ROOM_COUNT * ROOM_LOOPS,
            "totalHealthyFleetArtifactCycles": (ROOM_COUNT - 1) * FLEET_LOOPS,
        },
        "roomIsolation": room_result,
        "fleetFailureAndArtifacts": fleet_result,
        "preservedSamples": sample_paths,
        "productionCodeChanged": False,
        "pass": True,
    }
    args.evidence_out.parent.mkdir(parents=True, exist_ok=True)
    recorder.atomic_write_json(args.evidence_out, evidence)
    print(json.dumps(evidence, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

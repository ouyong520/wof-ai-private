from __future__ import annotations

import ast
import hashlib
import json
import math
import tempfile
import unittest
from pathlib import Path

from training.farm.adapter import TrainingFarmAdapter
from training.farm.collector_export import (
    ExportContractError,
    ExportRamBlock,
    ObservationSample,
    TrainingFarmReadOnlyExporter,
    WorkerExportContext,
    discover_current_records,
    read_current_record,
    record_is_stale,
    validate_export_registry,
)
from training.farm.fake_backend import DeterministicFakeBackend
from training.farm.identity import build_fixture_runtime_identity


class CollectorExportTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.exporter = TrainingFarmReadOnlyExporter(self.root)
        with TrainingFarmAdapter(DeterministicFakeBackend()) as adapter:
            self.identity = build_fixture_runtime_identity(adapter)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def context(
        self,
        worker: str = "worker-01",
        generation: str = "gen-0001",
        started: int = 1_000,
        sequence: int = 1,
        published: int = 1_001,
        **kwargs,
    ) -> WorkerExportContext:
        return WorkerExportContext(
            worker_id=worker,
            worker_generation=generation,
            generation_started_unix_ms=started,
            monotonic_sequence=sequence,
            published_at_unix_ms=published,
            runtime_identity=self.identity,
            **kwargs,
        )

    def registry(self) -> dict[str, object]:
        return validate_export_registry(json.loads((self.root / "registry.json").read_text(encoding="ascii")))

    def test_publish_roundtrip_binds_identity_layout_and_all_supported_evidence(self) -> None:
        blocks = (ExportRamBlock(0x1000, b"\x01\x02"), ExportRamBlock(0x2000, b"\x03\x04\x05"))
        stream = (
            ObservationSample(1, logical_frame=10, step_counter=10, ram=b"abc", ram_blocks=blocks,
                              metadata={"frameType": "existing-observation"}),
            ObservationSample(2, logical_frame=11, step_counter=11, ram=b"def", ram_blocks=blocks),
        )
        record = self.exporter.publish(
            self.context(
                logical_frame=11,
                step_counter=11,
                episode_id="episode-1",
                episode_generation="episode-gen-1",
                fork_set_id="fork-set-1",
                root_id="root-1",
                branch_id="branch-1",
            ),
            ram_snapshot=b"flat-ram",
            ram_blocks_snapshot=blocks,
            observation_stream=stream,
            trajectory_metadata={"trajectoryId": "trajectory-1"},
            action_result_trajectory=[{"frame": 10, "recordedAction": 3, "result": "existing"}],
            root_fork_branch_savestate_metadata={"rootSavestateSha256": "a" * 64},
            runtime_resource_timing_metadata={"cpuPercentTimes100": 1234, "sampleNs": 50},
            current_action_result_metadata={"actionWasChosenByCollector": False},
        )
        current = read_current_record(self.root, "worker-01")
        self.assertEqual(current, record)
        self.assertEqual(current["sourceNamespace"], "stable-retro-fbneo")
        self.assertEqual(current["sequence"], current["monotonicSequence"])
        self.assertTrue(current["complete"])
        self.assertEqual(current["schemaVersion"], current["schema"])
        self.assertEqual(current["runtimeIdentity"], self.identity)
        self.assertEqual(current["episodeIdentity"], {"episodeId": "episode-1"})
        self.assertEqual(current["rootIdentity"]["rootId"], "root-1")
        self.assertEqual(current["branchIdentity"]["branchId"], "branch-1")
        self.assertEqual(current["actionResultMetadata"], {"actionWasChosenByCollector": False})
        self.assertEqual(current["resourceTimingMetadata"]["sampleNs"], 50)
        self.assertEqual(
            current["evidenceKinds"],
            [
                "WORKER_RUNTIME_IDENTITY", "RAM_SNAPSHOT", "RAM_BLOCK_SNAPSHOT",
                "OBSERVATION_STREAM", "TRAJECTORY_METADATA", "ACTION_RESULT_TRAJECTORY",
                "ROOT_FORK_BRANCH_SAVESTATE_METADATA", "RUNTIME_RESOURCE_TIMING_METADATA",
                "CURRENT_ACTION_RESULT_METADATA",
            ],
        )
        self.assertEqual(set(current["evidence"]), set(current["evidenceKinds"]))
        self.assertIsNotNone(current["memoryLayoutIdentitySha256"])
        self.assertEqual(current["safety"]["trainingControlAuthority"], False)

        registry = self.registry()
        self.assertEqual(registry["sourceNamespace"], "stable-retro-fbneo")
        self.assertEqual(registry["exporterVersion"], "wof-training-farm-read-only-exporter-v1")
        self.assertEqual(len(registry["workers"]), 1)
        row = registry["workers"][0]
        self.assertNotEqual(row["recordPath"], "workers/worker-01/current.json")
        self.assertIn("/records/gen-0001/", row["recordPath"])
        record_path = self.root / row["recordPath"]
        raw = record_path.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(), row["recordSha256"])
        self.assertEqual(json.loads(raw.decode("ascii")), record)
        descriptor = current["evidence"]["RAM_SNAPSHOT"]
        self.assertEqual(descriptor["artifactPath"], current["artifactRelativePath"])
        self.assertEqual(descriptor["sha256"], current["artifactSha256"])

    def test_same_generation_sequence_is_strictly_monotonic(self) -> None:
        first = self.exporter.publish(self.context())
        second = self.exporter.publish(self.context(sequence=2, published=1_002))
        self.assertEqual(second["previousRecordIdentitySha256"], first["recordIdentitySha256"])
        registry = self.registry()
        self.assertEqual(registry["workers"][0]["sequence"], 2)
        self.assertEqual(registry["sequence"], 2)
        with self.assertRaisesRegex(ExportContractError, "strictly increase"):
            self.exporter.publish(self.context(sequence=2, published=1_003))
        self.assertEqual(self.registry(), registry)

    def test_new_generation_must_have_newer_generation_start_and_old_writer_cannot_return(self) -> None:
        self.exporter.publish(self.context(generation="gen-old", started=1_000, published=1_001))
        self.exporter.publish(self.context(generation="gen-new", started=2_000, sequence=1, published=2_001))
        before = self.registry()
        with self.assertRaisesRegex(ExportContractError, "conflicting/older"):
            self.exporter.publish(self.context(generation="gen-old", started=1_000, sequence=2, published=3_000))
        self.assertEqual(self.registry(), before)
        self.assertEqual(before["workers"][0]["workerGeneration"], "gen-new")

    def test_memory_layout_change_inside_one_artifact_fails_closed(self) -> None:
        base = (ExportRamBlock(0x1000, b"aa"),)
        changed = (ExportRamBlock(0x1000, b"bbb"),)
        with self.assertRaisesRegex(ExportContractError, "memory layout changed"):
            self.exporter.publish(
                self.context(),
                ram_blocks_snapshot=base,
                observation_stream=(ObservationSample(1, ram_blocks=changed),),
            )

    def test_stale_and_future_records_fail_stale_check(self) -> None:
        record = self.exporter.publish(self.context(published=2_000, started=1_000))
        self.assertFalse(record_is_stale(record, now_unix_ms=2_010, max_age_ms=20))
        self.assertTrue(record_is_stale(record, now_unix_ms=2_021, max_age_ms=20))
        self.assertTrue(record_is_stale(record, now_unix_ms=1_999, max_age_ms=20))
        with self.assertRaises(ExportContractError):
            record_is_stale(record, now_unix_ms=2_010, max_age_ms=True)

    def test_tampered_artifact_is_rejected(self) -> None:
        record = self.exporter.publish(self.context(), ram_snapshot=b"abc")
        path = self.root / record["artifactRelativePath"]
        path.write_bytes(path.read_bytes() + b" ")
        with self.assertRaisesRegex(ExportContractError, "bytes/hash"):
            read_current_record(self.root, "worker-01")

    def test_metadata_rejects_non_finite_and_non_string_object_keys(self) -> None:
        with self.assertRaises(ExportContractError):
            self.exporter.publish(self.context(), trajectory_metadata={"bad": math.nan})
        with self.assertRaises(ExportContractError):
            self.exporter.publish(self.context(), trajectory_metadata={1: "not-canonical"})  # type: ignore[dict-item]

    def test_worker_and_generation_types_are_not_coerced(self) -> None:
        with self.assertRaises(ExportContractError):
            self.context(worker="../escape")
        with self.assertRaises(ExportContractError):
            self.context(sequence=True)
        with self.assertRaises(ExportContractError):
            self.context(generation="bad generation")

    def test_inactive_worker_requires_stopped_health_and_registry_marks_inactive(self) -> None:
        with self.assertRaises(ExportContractError):
            self.context(active=False, health="ACTIVE")
        record = self.exporter.publish(self.context(active=False, health="STOPPED"))
        self.assertFalse(record["active"])
        self.assertFalse(self.registry()["workers"][0]["active"])

    def test_ten_worker_fixture_is_identity_isolated_without_launching_workers(self) -> None:
        for index in range(10):
            worker = f"worker-{index:02d}"
            generation = f"generation-{index:02d}"
            self.exporter.publish(
                self.context(worker=worker, generation=generation, started=1000 + index, published=2000 + index),
                ram_snapshot=bytes([index + 1]),
                trajectory_metadata={"workerIndex": index},
            )
        records = discover_current_records(self.root)
        registry = self.registry()
        self.assertEqual(len(records), 10)
        self.assertEqual(len(registry["workers"]), 10)
        self.assertEqual(len({row["workerId"] for row in records}), 10)
        self.assertEqual(len({row["workerGeneration"] for row in records}), 10)
        self.assertEqual(len({row["artifactSha256"] for row in records}), 10)
        self.assertEqual(len({row["recordSha256"] for row in registry["workers"]}), 10)
        for row in registry["workers"]:
            immutable = self.root / row["recordPath"]
            self.assertTrue(immutable.is_file())
            self.assertEqual(hashlib.sha256(immutable.read_bytes()).hexdigest(), row["recordSha256"])

    def test_empty_registry_is_safe(self) -> None:
        empty = Path(tempfile.mkdtemp())
        self.assertEqual(discover_current_records(empty), [])

    def test_exporter_source_has_no_training_control_or_worker_launch_calls(self) -> None:
        source_path = Path(__file__).resolve().parents[1] / "collector_export.py"
        source = source_path.read_text(encoding="utf-8")
        self.assertNotIn("TrainingFarmAdapter", source)
        tree = ast.parse(source)
        forbidden = {
            "reset", "step", "step_frame", "load_state", "save_state",
            "Popen", "run", "create_subprocess_exec", "create_subprocess_shell",
        }
        calls = {
            node.func.attr
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
        }
        names = {
            node.func.id
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        }
        self.assertTrue(forbidden.isdisjoint(calls | names))

    def test_record_artifact_binding_rejects_record_tamper(self) -> None:
        self.exporter.publish(self.context(), ram_snapshot=b"abc")
        current = self.root / "workers" / "worker-01" / "current.json"
        payload = json.loads(current.read_text(encoding="ascii"))
        payload["artifactSha256"] = "0" * 64
        current.write_text(json.dumps(payload, sort_keys=True, separators=(",", ":")), encoding="ascii")
        with self.assertRaises(ExportContractError):
            read_current_record(self.root, "worker-01")


if __name__ == "__main__":
    unittest.main()

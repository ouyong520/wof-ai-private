from __future__ import annotations

import ast
import json
import tempfile
import time
import unittest
from pathlib import Path

from training.farm.collector_export import discover_current_records, validate_export_registry
from training.farm.collector_export_fixture import build_fixture


class CollectorExportFixtureTests(unittest.TestCase):
    def test_builds_ten_fresh_isolated_workers_without_real_launches(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            now_ms = time.time_ns() // 1_000_000
            summary = build_fixture(root, workers=10, now_unix_ms=now_ms)
            self.assertEqual(summary["workers"], 10)
            self.assertEqual(summary["realWorkerLaunches"], 0)
            self.assertFalse(summary["collectorCallsReset"])
            self.assertFalse(summary["collectorCallsStep"])
            self.assertFalse(summary["collectorCallsLoadState"])
            self.assertEqual(len(set(summary["workerIds"])), 10)
            self.assertEqual(len(set(summary["workerGenerations"])), 10)
            self.assertEqual(len(set(summary["captureBindingSha256"])), 10)

            registry = validate_export_registry(json.loads((root / "registry.json").read_text(encoding="ascii")))
            self.assertEqual(len(registry["workers"]), 10)
            self.assertTrue(all(row["active"] is True for row in registry["workers"]))
            records = discover_current_records(root)
            self.assertEqual(len(records), 10)
            self.assertEqual(len({record["artifactSha256"] for record in records}), 10)
            self.assertTrue(all(record["complete"] is True for record in records))

    def test_worker_count_is_strict_and_bounded(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            now_ms = time.time_ns() // 1_000_000
            for bad in (0, 11, True, 1.0, "10"):
                with self.subTest(bad=bad), self.assertRaises(ValueError):
                    build_fixture(root, workers=bad, now_unix_ms=now_ms)  # type: ignore[arg-type]

    def test_fixture_source_has_no_control_or_process_launch_calls(self) -> None:
        path = Path(__file__).resolve().parents[1] / "collector_export_fixture.py"
        tree = ast.parse(path.read_text(encoding="utf-8"))
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


if __name__ == "__main__":
    unittest.main()

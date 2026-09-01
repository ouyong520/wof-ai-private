from __future__ import annotations

import copy
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parents[1]
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
SPEC = importlib.util.spec_from_file_location("regression_runner_under_test", HERE / "runner.py")
assert SPEC and SPEC.loader
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)


class RegressionRunnerTests(unittest.TestCase):
    def test_generated_dependency_paths_are_ignored(self) -> None:
        self.assertTrue(
            runner.is_generated_or_dependency_path(
                "parallel/WOF052L_RECORDER/.venv/Lib/site-packages/websocket/tests/test_app.py"
            )
        )
        self.assertTrue(
            runner.is_generated_or_dependency_path(
                "parallel/ANY/node_modules/pkg/test_x.js"
            )
        )
        self.assertFalse(
            runner.is_generated_or_dependency_path(
                "parallel/WOF052L_RECORDER/test_discovery_v2_sync.py"
            )
        )

    def test_safe_discovery_preserves_repository_tests(self) -> None:
        original = runner._CORE_DISCOVER_CANDIDATES
        try:
            runner._CORE_DISCOVER_CANDIDATES = lambda root: [
                "parallel/WOF052L_RECORDER/test_discovery_v2_sync.py",
                "parallel/WOF052L_RECORDER/.venv/Lib/site-packages/websocket/tests/test_app.py",
            ]
            self.assertEqual(
                runner.discover_candidates(Path(".")),
                ["parallel/WOF052L_RECORDER/test_discovery_v2_sync.py"],
            )
        finally:
            runner._CORE_DISCOVER_CANDIDATES = original

    def test_current_manifest_satisfies_discovery_v2_contract(self) -> None:
        manifest = runner.core.load_manifest(HERE / "manifest.json")
        self.assertEqual([], runner.validate_discovery_v2_manifest(manifest))

    def test_allowlisted_component_test_cannot_be_silently_unrun(self) -> None:
        manifest = copy.deepcopy(runner.core.load_manifest(HERE / "manifest.json"))
        future_test = "parallel/PROSPECTIVE_VALIDATOR/test_future_discovery.py"
        manifest["allowlistedTestPaths"].append(future_test)
        errors = runner.validate_discovery_v2_manifest(manifest)
        self.assertTrue(
            any(future_test in error and "未设为 required" in error for error in errors),
            errors,
        )

    def test_recorder_v2_entrypoint_is_required_compile_and_selftest_surface(self) -> None:
        manifest = copy.deepcopy(runner.core.load_manifest(HERE / "manifest.json"))
        suite = next(row for row in manifest["suites"] if row["id"] == "wof052l_recorder")
        suite["requiredPaths"] = [
            path for path in suite["requiredPaths"]
            if path != runner.RECORDER_V2_ENTRYPOINT
        ]
        suite["commands"] = [
            command for command in suite["commands"]
            if not any("owner_v2_zh_cn.py" in str(token) for token in command.get("argv", []))
        ]
        errors = runner.validate_discovery_v2_manifest(manifest)
        self.assertTrue(any("不是 required integration path" in error for error in errors), errors)
        self.assertTrue(any("未纳入 py_compile" in error for error in errors), errors)
        self.assertTrue(any("未作为官方 V2 self-test" in error for error in errors), errors)

    def test_final_rescan_blocks_new_guarded_test(self) -> None:
        manifest = runner.core.load_manifest(HERE / "manifest.json")
        original_discover = runner.core.discover_candidates
        try:
            with tempfile.TemporaryDirectory() as td:
                root = Path(td)
                test_path = root / "parallel" / "PROSPECTIVE_VALIDATOR" / "test_new_safety.py"
                test_path.parent.mkdir(parents=True)
                test_path.write_text("raise SystemExit(99)\n", encoding="utf-8")
                runner.core.discover_candidates = runner.discover_candidates
                guard, _outside = runner.build_allowlist_guard(root, manifest)
                self.assertEqual("BLOCKED", guard["status"])
                self.assertIn(
                    "parallel/PROSPECTIVE_VALIDATOR/test_new_safety.py",
                    guard["unallowlisted"],
                )
        finally:
            runner.core.discover_candidates = original_discover

    def test_final_rescan_ignores_generated_dependency_test(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            generated = (
                root
                / "parallel"
                / "WOF052L_RECORDER"
                / ".venv"
                / "Lib"
                / "site-packages"
                / "pkg"
                / "tests"
                / "test_external.py"
            )
            generated.parent.mkdir(parents=True)
            generated.write_text("raise SystemExit(99)\n", encoding="utf-8")
            self.assertEqual([], runner.discover_candidates(root))

    def test_summary_separates_contract_ready_from_component_health(self) -> None:
        def suite(suite_id: str, status: str) -> dict:
            return {
                "id": suite_id,
                "status": status,
                "platformOptional": False,
                "reasonZh": None,
                "failedCommands": [],
            }

        summary = {
            "suites": [
                suite("orchestrator_selftest", "PASS"),
                suite("allowlist_guard", "PASS"),
                suite("pylaunch_offline", "PASS"),
                suite("browser_fleet", "PASS"),
                suite("wof052l_recorder", "FAIL"),
                suite("prospective_validator", "BLOCKED"),
            ]
        }
        runner.augment_summary(summary)
        self.assertEqual("PASS", summary["orchestratorContract"]["status"])
        self.assertTrue(summary["orchestratorContract"]["ready"])
        self.assertEqual("FAIL", summary["discoveryV2ComponentHealth"]["overall"])
        self.assertEqual(
            "FAIL",
            summary["discoveryV2ComponentHealth"]["components"]["WOF-052L Recorder"]["status"],
        )
        self.assertEqual(
            "BLOCKED",
            summary["discoveryV2ComponentHealth"]["components"]["Prospective Validator"]["status"],
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)

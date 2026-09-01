from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parents[1]
MODULE_PATH = HERE / "orchestrator.py"
SPEC = importlib.util.spec_from_file_location("regression_orchestrator_under_test", MODULE_PATH)
assert SPEC and SPEC.loader
orch = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(orch)


class RegressionOrchestratorTests(unittest.TestCase):
    def test_manifest_has_unique_suite_ids_and_allowlist(self) -> None:
        manifest = orch.load_manifest(HERE / "manifest.json")
        ids = [row["id"] for row in manifest["suites"]]
        self.assertEqual(len(ids), len(set(ids)))
        allowlisted = manifest["allowlistedTestPaths"]
        self.assertEqual(len(allowlisted), len(set(allowlisted)))
        self.assertIn("product/alpha/regression.mjs", allowlisted)
        self.assertIn("parallel/ALPHAQA_RC5/independent_bootstrap_retest.mjs", allowlisted)

    def test_offline_fail_has_priority(self) -> None:
        suites = [
            {"status": "PASS", "platformOptional": False},
            {"status": "FAIL", "platformOptional": False},
            {"status": "BLOCKED", "platformOptional": False},
        ]
        self.assertEqual("FAIL", orch.compute_offline_overall(suites))

    def test_blocked_when_required_suite_cannot_run(self) -> None:
        suites = [
            {"status": "PASS", "platformOptional": False},
            {"status": "BLOCKED", "platformOptional": False},
        ]
        self.assertEqual("BLOCKED", orch.compute_offline_overall(suites))

    def test_platform_optional_skip_does_not_block_offline(self) -> None:
        suites = [
            {"status": "PASS", "platformOptional": False},
            {"status": "SKIPPED", "platformOptional": True},
        ]
        self.assertEqual("PASS", orch.compute_offline_overall(suites))

    def test_manual_proof_keeps_global_result_blocked(self) -> None:
        manual = [{"status": "NOT_RUN"}]
        self.assertEqual("BLOCKED", orch.compute_overall("PASS", manual))
        self.assertEqual("FAIL", orch.compute_overall("FAIL", manual))

    def test_safe_repo_path_rejects_escape(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            with self.assertRaises(ValueError):
                orch.safe_repo_path(root, "../outside")

    def test_candidate_filter_is_conservative(self) -> None:
        self.assertTrue(orch.is_test_candidate(Path("test_x.py")))
        self.assertTrue(orch.is_test_candidate(Path("regression.mjs")))
        self.assertTrue(orch.is_test_candidate(Path("independent_retest.mjs")))
        self.assertFalse(orch.is_test_candidate(Path("owner_zh_cn.py")))
        self.assertFalse(orch.is_test_candidate(Path("worker_probe.js")))


if __name__ == "__main__":
    unittest.main(verbosity=2)

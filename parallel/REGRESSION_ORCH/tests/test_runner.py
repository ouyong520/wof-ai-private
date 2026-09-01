from __future__ import annotations

import importlib.util
import sys
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
        runner._CORE_DISCOVER_CANDIDATES = lambda root: [
            "parallel/WOF052L_RECORDER/test_discovery_v2_sync.py",
            "parallel/WOF052L_RECORDER/.venv/Lib/site-packages/websocket/tests/test_app.py",
        ]
        self.assertEqual(
            runner.discover_candidates(Path(".")),
            ["parallel/WOF052L_RECORDER/test_discovery_v2_sync.py"],
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)

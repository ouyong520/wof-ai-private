from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve()
PYLAUNCH = HERE.parents[1]
ROOT = PYLAUNCH.parents[1]
if str(PYLAUNCH) not in sys.path:
    sys.path.insert(0, str(PYLAUNCH))

RUNNER_PATH = ROOT / "parallel" / "RENDER_AUTHORITY_V3" / "measurement_runner.py"
spec = importlib.util.spec_from_file_location("wof_alpha_measurement_runner_click_wait_test", RUNNER_PATH)
assert spec is not None and spec.loader is not None
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class P1OwnerClickWaitTests(unittest.TestCase):
    def test_pending_required_click_holds_visual_grace(self) -> None:
        self.assertTrue(
            runner._owner_click_pending(
                {"state": "ONE_CLICK_REQUIRED", "ownerClickCount": 0, "ownerClickMaximum": 1}
            )
        )

    def test_click_consumed_releases_visual_grace(self) -> None:
        self.assertFalse(
            runner._owner_click_pending(
                {"state": "ONE_CLICK_REQUIRED", "ownerClickCount": 1, "ownerClickMaximum": 1}
            )
        )
        self.assertFalse(runner._owner_click_pending({"state": "HEAD_TRACKING", "ownerClickCount": 1}))

    def test_runner_starts_grace_only_after_click_wait_is_over(self) -> None:
        source = RUNNER_PATH.read_text(encoding="utf-8")
        self.assertIn('if _owner_click_pending(v):', source)
        self.assertIn('terminal_seen_at=None;publish("ONE_CLICK_REQUIRED"', source)
        self.assertIn('if terminal_seen_at is None:', source)
        self.assertIn('event("P1_VISUAL_GRACE_STARTED"', source)


if __name__ == "__main__":
    unittest.main()

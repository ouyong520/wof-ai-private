from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve()
PYLAUNCH = HERE.parents[1]
if str(PYLAUNCH) not in sys.path:
    sys.path.insert(0, str(PYLAUNCH))

from wof_launcher.discovery_v2 import TargetChoice
from wof_launcher.monitor import LauncherMonitor
from wof_launcher.projection_recovery import ProjectionRecovery, ProjectionRecoveryError
from wof_launcher.reentry_discovery import ATTACH_WINDOW_SECONDS, MAX_DEPTH, MAX_SESSIONS
from wof_launcher.state import StatusStore


GOOD_LIGHT = {"moduleOk": True, "heapOk": True, "readOnly": True, "ramWrites": 0, "inputInjection": False}
GOOD_ID = {"ok": True, "sha256": "5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62", "locator": {"heapBase": 0x1000, "swap16": False}}
PAGE = {"targetId": "page", "type": "page", "url": "https://game/wof"}
WORKER = {"targetId": "worker-b", "type": "worker", "url": "blob:new-room"}


def live_result(*, verdict: str = "IMPLEMENTATION_READY") -> dict:
    return {
        "schema": "wof-owner-projection-proof-result-v1",
        "verdict": verdict,
        "projection": {
            "camera": {"address": "0xFF1234", "read": "u16be", "sign": 1, "scale": 1},
            "native": {"width": 384, "height": 224, "xBias": 7.5, "yModel": "Y-Z", "yBias": -18.0},
            "enemyHeadOffsetsByType": {"18": -18.0, "22": -18.0},
        },
        "boundaries": {"readOnly": True, "ramWrites": 0, "inputInjection": False, "guessedConstants": False, "syntheticAuthority": False},
        "evidence": {"checklist": {"enemyTypes": [18, 22]}},
    }


class ProjectionRecoveryTests(unittest.TestCase):
    def test_live_result_derives_player_and_only_observed_enemy_profiles(self):
        recovery = ProjectionRecovery(lambda _path: "")
        profiles, accepted = recovery._profiles_from_result(live_result())
        self.assertEqual("PROVED", profiles["player"]["status"])
        self.assertEqual("world-camera-floor-z-affine-v1", profiles["player"]["projectionKind"])
        self.assertEqual(-1, profiles["player"]["zScale"])
        self.assertEqual(-18.0, profiles["player"]["yBias"])
        self.assertEqual(0, profiles["player"]["headClearanceNative"])
        self.assertEqual("IMPLEMENTATION_READY", profiles["enemy"]["verdict"])
        self.assertEqual({"18": -18.0, "22": -18.0}, profiles["enemy"]["enemyHeadOffsetsByType"])
        self.assertEqual("CURRENT_LAUNCHER_PROCESS_ONLY", accepted["authorityPersistence"])
        self.assertTrue(accepted["proofId"].startswith("live-"))

    def test_unproved_or_unsafe_result_cannot_activate_projection(self):
        recovery = ProjectionRecovery(lambda _path: "")
        with self.assertRaises(ProjectionRecoveryError):
            recovery._profiles_from_result(live_result(verdict="FAILED_COMPONENT:enemy_head_clearance"))
        bad = live_result(); bad["boundaries"]["syntheticAuthority"] = True
        with self.assertRaises(ProjectionRecoveryError):
            recovery._profiles_from_result(bad)
        missing = live_result(); missing["projection"]["enemyHeadOffsetsByType"] = {}
        with self.assertRaises(ProjectionRecoveryError):
            recovery._profiles_from_result(missing)

    def test_serialized_result_is_not_loaded_as_future_process_authority(self):
        recovery = ProjectionRecovery(lambda _path: "")
        self.assertIsNone(recovery.profiles())
        self.assertFalse(recovery.status()["provedInCurrentLauncherProcess"])
        self.assertNotIn("load", recovery.__class__.__dict__)


class ReentryIntegrationTests(unittest.TestCase):
    def test_reentry_traversal_is_bounded_but_deeper_than_old_depth_two(self):
        self.assertGreaterEqual(MAX_DEPTH, 4)
        self.assertLessEqual(MAX_DEPTH, 8)
        self.assertGreaterEqual(MAX_SESSIONS, 32)
        self.assertLessEqual(MAX_SESSIONS, 64)
        self.assertGreaterEqual(ATTACH_WINDOW_SECONDS, 1.0)
        self.assertLessEqual(ATTACH_WINDOW_SECONDS, 2.0)

    def test_monitor_uses_deep_recovery_after_page_only(self):
        base = TargetChoice(PAGE, None, None, None, "WOF page found; related game Worker not yet discovered", {"path": "page-only"})
        recovered = TargetChoice(PAGE, WORKER, GOOD_LIGHT, GOOD_ID, None, {"path": "reentry-deep-autoattach"})
        monitor = LauncherMonitor(StatusStore(), auto_launch_browser=False)
        monitor._client = object()
        with mock.patch("wof_launcher.monitor.discovery_module.discover", return_value=base) as first, mock.patch("wof_launcher.monitor.recover_page_only", return_value=recovered) as second:
            choice = monitor._fresh_discover()
        self.assertIs(choice, recovered)
        first.assert_called_once()
        second.assert_called_once()

    def test_same_process_live_profiles_survive_runtime_revoke_for_room_reentry(self):
        recovery = ProjectionRecovery(lambda _path: "")
        profiles, accepted = recovery._profiles_from_result(live_result())
        recovery._profiles = profiles; recovery._proof_result = accepted; recovery._state = "PROVED_LIVE_PROCESS_AUTHORITY"
        recovery.stop_runtime(None, preserve_state=True)
        self.assertIsNotNone(recovery.profiles())
        self.assertEqual("PROVED_LIVE_PROCESS_AUTHORITY", recovery.status()["state"])


if __name__ == "__main__":
    unittest.main()

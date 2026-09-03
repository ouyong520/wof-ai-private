from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve()
PYLAUNCH = HERE.parents[1]
if str(PYLAUNCH) not in sys.path:
    sys.path.insert(0, str(PYLAUNCH))

from test_owner_calibration_identity_recovery import OwnerCalibrationIdentityRecoveryTests  # noqa: F401
from wof_launcher.discovery_v2 import TargetChoice
from wof_launcher.monitor import LauncherMonitor
from wof_launcher.projection_recovery import ProjectionRecovery, ProjectionRecoveryError
from wof_launcher.reentry_discovery import ATTACH_WINDOW_SECONDS, MAX_DEPTH, MAX_SESSIONS
from wof_launcher.state import StatusStore


GOOD_LIGHT = {"moduleOk": True, "heapOk": True, "readOnly": True, "ramWrites": 0, "inputInjection": False}
GOOD_ID = {"ok": True, "sha256": "5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62", "locator": {"heapBase": 0x1000, "swap16": False}}
PAGE = {"targetId": "page", "type": "page", "url": "https://game/wof"}
WORKER = {"targetId": "worker-b", "type": "worker", "url": "blob:new-room"}
AUTHORITY_A = "accepted-runtime-authority-a"
AUTHORITY_B = "accepted-runtime-authority-b"


def live_result(*, verdict: str = "IMPLEMENTATION_READY") -> dict:
    return {
        "schema": "wof-owner-projection-proof-result-v2",
        "verdict": verdict,
        "authorityBinding": {
            "workerSessionId": "worker-session-a",
            "sequenceStart": 10,
            "sequenceEnd": 80,
            "p1LifecycleGeneration": 1,
            "cameraAuthorityId": "camera-auth-2",
            "cameraAuthorityGeneration": 2,
            "cameraAddress": "0xFF1234",
            "requestSnapshotId": "worker-session-a:9",
        },
        "calibration": {
            "interactionMode": "ONE_CLICK_VISUAL_SEED",
            "clickCount": 1,
            "pairedSampleCount": 40,
            "holdoutSampleCount": 8,
        },
        "projection": {
            "camera": {
                "address": "0xFF1234",
                "read": "u16be",
                "sign": -1,
                "scale": 0.75,
                "authorityId": "camera-auth-2",
                "authorityGeneration": 2,
            },
            "native": {
                "width": 384,
                "height": 224,
                "projectionKind": "world-camera-floor-z-affine-v2",
                "worldXScale": 1.25,
                "xBias": 37.5,
                "floorYScale": -0.85,
                "zScale": -1.40,
                "yBias": 188.0,
            },
            "validationEnvelope": {
                "worldX": [40.0, 92.0],
                "worldY": [18.0, 34.0],
                "worldZ": [0.0, 14.0],
                "cameraRaw": [100.0, 112.0],
            },
            "motionEnvelope": {
                "worldXStep": 3.0,
                "worldYStep": 2.0,
                "worldZStep": 4.0,
                "cameraRawStep": 2.0,
            },
            "residuals": {"trainRms": 1.25, "holdoutRms": 1.60, "holdoutMax": 3.5},
            "enemyHeadOffsetsByType": {"18": -18.0, "22": -20.0},
            "enemyHeadEvidenceByType": {
                "18": {"sampleCount": 12, "mad": 1.1, "slot": 0, "lifecycleGeneration": 1},
                "22": {"sampleCount": 10, "mad": 1.4, "slot": 1, "lifecycleGeneration": 2},
            },
        },
        "boundaries": {
            "readOnly": True,
            "ramWrites": 0,
            "inputInjection": False,
            "guessedConstants": False,
            "syntheticAuthority": False,
            "ownerModelChoice": False,
            "simultaneousCandidateLabels": False,
            "maxCalibrationClicksPerAuthorityGeneration": 1,
        },
        "evidence": {"tracker": {"acceptedCount": 40}, "suppression": []},
    }


class ProjectionRecoveryTests(unittest.TestCase):
    def test_live_v2_result_derives_affine_player_and_observed_enemy_profiles(self):
        recovery = ProjectionRecovery(lambda _path: "")
        profiles, accepted = recovery._profiles_from_result(live_result(), AUTHORITY_A)
        player = profiles["player"]
        enemy = profiles["enemy"]
        self.assertEqual("PROVED", player["status"])
        self.assertEqual("LIVE_PROCESS_BOUND_OWNER_PROOF_V2", player["activation"])
        self.assertEqual("world-camera-floor-z-affine-v1", player["projectionKind"])
        self.assertEqual(-0.85, player["floorYScale"])
        self.assertEqual(-1.40, player["zScale"])
        self.assertEqual(0, player["headClearanceNative"])
        self.assertEqual("IMPLEMENTATION_READY", enemy["verdict"])
        self.assertEqual("world-camera-floor-z-affine-v2", enemy["projectionKind"])
        self.assertEqual({"18": -18.0, "22": -20.0}, enemy["enemyHeadOffsetsByType"])
        self.assertEqual("CURRENT_ACCEPTED_RUNTIME_AUTHORITY_ONLY", accepted["authorityPersistence"])
        self.assertTrue(accepted["proofId"].startswith("live-v2-"))
        self.assertEqual(64, len(player["authorityBinding"]["launcherAuthorityKeySha256"]))

    def test_unproved_unsafe_ambiguous_or_undercovered_result_cannot_activate_projection(self):
        recovery = ProjectionRecovery(lambda _path: "")
        with self.assertRaises(ProjectionRecoveryError):
            recovery._profiles_from_result(live_result(verdict="FAILED_COMPONENT:enemy_head_clearance"), AUTHORITY_A)
        bad = live_result(); bad["boundaries"]["syntheticAuthority"] = True
        with self.assertRaises(ProjectionRecoveryError): recovery._profiles_from_result(bad, AUTHORITY_A)
        bad = live_result(); bad["boundaries"]["ownerModelChoice"] = True
        with self.assertRaises(ProjectionRecoveryError): recovery._profiles_from_result(bad, AUTHORITY_A)
        bad = live_result(); bad["projection"]["residuals"]["holdoutRms"] = 8.0
        with self.assertRaises(ProjectionRecoveryError): recovery._profiles_from_result(bad, AUTHORITY_A)
        bad = live_result(); bad["projection"]["validationEnvelope"]["worldZ"] = [0.0, 2.0]
        with self.assertRaises(ProjectionRecoveryError): recovery._profiles_from_result(bad, AUTHORITY_A)
        bad = live_result(); bad["projection"]["enemyHeadEvidenceByType"]["18"]["sampleCount"] = 2
        with self.assertRaises(ProjectionRecoveryError): recovery._profiles_from_result(bad, AUTHORITY_A)

    def test_serialized_result_is_not_loaded_as_future_process_authority(self):
        recovery = ProjectionRecovery(lambda _path: "")
        self.assertIsNone(recovery.profiles())
        self.assertFalse(recovery.status()["provedInCurrentLauncherProcess"])
        self.assertNotIn("load", recovery.__class__.__dict__)

    def test_live_profile_is_exact_runtime_authority_bound_and_clearable(self):
        recovery = ProjectionRecovery(lambda _path: "")
        profiles, accepted = recovery._profiles_from_result(live_result(), AUTHORITY_A)
        recovery._profiles = profiles
        recovery._proof_result = accepted
        recovery._profile_authority_key = AUTHORITY_A
        recovery._state = "PROVED_LIVE_PROCESS_AUTHORITY"
        self.assertIsNotNone(recovery.profiles(AUTHORITY_A))
        self.assertIsNone(recovery.profiles(AUTHORITY_B))
        recovery.stop_runtime(None, preserve_state=True)
        self.assertIsNotNone(recovery.profiles(AUTHORITY_A), "same accepted authority may survive the deliberate Alpha rebind")
        self.assertIsNone(recovery.profiles(AUTHORITY_B), "replacement authority must never inherit the old transform")
        recovery.clear_profiles("accepted runtime authority revoked")
        self.assertIsNone(recovery.profiles(AUTHORITY_A))
        self.assertEqual("UNPROVED", recovery.status()["state"])


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


if __name__ == "__main__":
    unittest.main()

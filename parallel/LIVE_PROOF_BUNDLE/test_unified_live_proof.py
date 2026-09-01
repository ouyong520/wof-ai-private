from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import unified_live_proof as u

SAFE_MANIFEST = {
    "version": "wof-browser-fleet-v1",
    "readOnly": True,
    "ramWrites": 0,
    "inputInjection": False,
    "windowWorkerReplacement": False,
    "workerStatusAuthority": "cheap-indicator-only",
    "world921031IdentityAuthoritative": False,
    "instances": [{
        "id": 1,
        "host": "127.0.0.1",
        "port": 9423,
        "profileDir": "Proof_01",
        "pid": 123,
        "status": {
            "browser": "OK",
            "page": "OK",
            "worker": "OK",
            "workerDiscovery": "page-autoattach-module",
            "relatedTopologyCount": 1,
        },
    }],
}

PASS_PROOF = {
    "schema": "wof-python-launcher-windows-proof-v1",
    "automatedResult": "PASS",
    "checks": {
        "Browser": "OK",
        "WOF page": "OK",
        "Worker": "OK",
        "WASM / heap": "OK",
        "World 921031": "OK",
        "READ ONLY / RAM writes: 0": "OK",
    },
    "readOnly": True,
    "ramWrites": 0,
    "inputInjection": False,
    "worldSha256": "5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62",
}

class UnifiedProofTests(unittest.TestCase):
    def recorder(self) -> u.RecorderEvidence:
        r = u.RecorderEvidence()
        r.feed("+ 房间 room-1 已连接 — World 921031 已确认 / Discovery V2 / 只读模式")
        return r

    def test_fleet_indicator_is_explicitly_non_authoritative(self):
        f = u.normalize_fleet(SAFE_MANIFEST)
        self.assertTrue(f["workerIndicator"])
        self.assertEqual(f["workerAuthority"], "cheap-indicator-only")
        self.assertFalse(f["world921031Authoritative"])

    def test_automated_ready_requires_all_three_lanes(self):
        self.assertTrue(u.automated_ready(
            u.normalize_fleet(SAFE_MANIFEST),
            u.normalize_pylaunch(PASS_PROOF),
            self.recorder(),
        ))

    def test_missing_recorder_admission_fails_closed(self):
        self.assertFalse(u.automated_ready(
            u.normalize_fleet(SAFE_MANIFEST),
            u.normalize_pylaunch(PASS_PROOF),
            u.RecorderEvidence(),
        ))

    def test_safety_violation_fails_closed(self):
        bad = dict(SAFE_MANIFEST)
        bad["ramWrites"] = 1
        self.assertFalse(u.automated_ready(
            u.normalize_fleet(bad),
            u.normalize_pylaunch(PASS_PROOF),
            self.recorder(),
        ))

    def test_playability_confirmation_required_for_ten_room_ready(self):
        with tempfile.TemporaryDirectory() as td:
            payload = u.build_status(
                run_id="r1",
                run_dir=Path(td),
                fleet_manifest=SAFE_MANIFEST,
                pylaunch_proof=PASS_PROOF,
                recorder=self.recorder(),
                playability="NOT_READY",
                stage="LIVE_WAITING",
                blockers=[],
            )
            self.assertTrue(payload["live"]["automatedChecksReady"])
            self.assertFalse(payload["tenRoomLongCaptureReady"])
            self.assertEqual(payload["overallResult"], "WAITING")

    def test_full_live_pass_sets_ready_without_starting_long_capture(self):
        with tempfile.TemporaryDirectory() as td:
            payload = u.build_status(
                run_id="r2",
                run_dir=Path(td),
                fleet_manifest=SAFE_MANIFEST,
                pylaunch_proof=PASS_PROOF,
                recorder=self.recorder(),
                playability="CONFIRMED",
                stage="COMPLETE",
                blockers=[],
            )
            self.assertEqual(payload["overallResult"], "PASS")
            self.assertTrue(payload["tenRoomLongCaptureReady"])
            self.assertFalse(payload["longCaptureAutoStarted"])

    def test_partial_failure_preserves_positive_evidence(self):
        proof = dict(PASS_PROOF)
        proof["automatedResult"] = "WAITING"
        proof["checks"] = dict(PASS_PROOF["checks"])
        proof["checks"]["World 921031"] = "--"
        with tempfile.TemporaryDirectory() as td:
            payload = u.build_status(
                run_id="r3",
                run_dir=Path(td),
                fleet_manifest=SAFE_MANIFEST,
                pylaunch_proof=proof,
                recorder=self.recorder(),
                playability="NOT_READY",
                stage="BLOCKED",
                blockers=["PYLAUNCH blocked"],
            )
            self.assertEqual(payload["overallResult"], "BLOCKED")
            self.assertTrue(payload["live"]["fleetDiscoveryV2"]["workerIndicator"])
            self.assertTrue(payload["live"]["recorderDiscoveryV2Admission"]["admitted"])
            self.assertFalse(payload["live"]["pylaunchAuthoritativeProof"]["world921031"])

    def test_recorder_marker_detection(self):
        r = u.RecorderEvidence()
        r.feed("noise")
        self.assertFalse(r.admitted)
        r.feed("+ 房间 x 已连接 — World 921031 已确认 / Discovery V2 / 只读模式")
        self.assertTrue(r.admitted)

    def test_repository_and_live_claims_are_distinct(self):
        with tempfile.TemporaryDirectory() as td:
            payload = u.build_status(
                run_id="r4",
                run_dir=Path(td),
                fleet_manifest=None,
                pylaunch_proof=None,
                recorder=u.RecorderEvidence(),
                playability="NOT_READY",
                stage="STARTING",
                blockers=[],
            )
            self.assertEqual(payload["repository"]["result"], "PASS")
            self.assertFalse(payload["repository"]["liveProofClaimed"])
            self.assertEqual(payload["live"]["result"], "WAITING")

if __name__ == "__main__":
    unittest.main(verbosity=2)

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

TARGET_DIR = Path(__file__).resolve().parents[1] / "LIVE_PROOF_BUNDLE"
sys.path.insert(0, str(TARGET_DIR))

import unified_live_proof as u  # noqa: E402

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
    "lastUpdateUtc": "2026-09-01T13:52:00+00:00",
}

LIVE_PROCESSES = {
    "launcherRequired": True,
    "recorderRequired": True,
    "launcherExitCode": None,
    "recorderExitCode": None,
}


class FailClosedIndependentAdversarialQA(unittest.TestCase):
    def recorder(self) -> u.RecorderEvidence:
        rec = u.RecorderEvidence()
        rec.feed("+ 房间 room-qa 已连接 — World 921031 已确认 / Discovery V2 / 只读模式")
        return rec

    def status(self, *, proof=None, recorder=None, playability="CONFIRMED",
               blockers=None, process_state=LIVE_PROCESSES, manifest=SAFE_MANIFEST):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        return u.build_status(
            run_id="independent-failclosed-qa",
            run_dir=Path(td.name),
            fleet_manifest=manifest,
            pylaunch_proof=PASS_PROOF if proof is None else proof,
            recorder=self.recorder() if recorder is None else recorder,
            playability=playability,
            stage="ADVERSARIAL_QA",
            blockers=list(blockers or []),
            process_state=process_state,
        )

    def test_fatal_after_admission_revokes_current_authority(self):
        rec = self.recorder()
        rec.feed("WOF-052L 采集器没有正常完成：已安全拒绝采集")
        out = self.status(recorder=rec)
        self.assertFalse(out["live"]["recorderDiscoveryV2Admission"]["admitted"])
        self.assertEqual(out["live"]["recorderDiscoveryV2Admission"]["currentHealth"], "FATAL")
        self.assertEqual(out["overallResult"], "BLOCKED")
        self.assertFalse(out["tenRoomLongCaptureReady"])

    def test_sticky_blocker_cannot_be_overridden_by_owner_confirmation(self):
        out = self.status(blockers=["qa-sticky-blocker"])
        self.assertEqual(out["overallResult"], "BLOCKED")
        self.assertFalse(out["live"]["ownerPromptEligible"])
        self.assertFalse(out["tenRoomLongCaptureReady"])

    def test_pylaunch_exit_after_pass_is_blocked(self):
        process = dict(LIVE_PROCESSES)
        process["launcherExitCode"] = 17
        out = self.status(process_state=process)
        self.assertEqual(out["overallResult"], "BLOCKED")
        self.assertFalse(out["tenRoomLongCaptureReady"])

    def test_recorder_exit_after_admission_is_blocked(self):
        process = dict(LIVE_PROCESSES)
        process["recorderExitCode"] = 19
        out = self.status(process_state=process)
        self.assertEqual(out["overallResult"], "BLOCKED")
        self.assertFalse(out["tenRoomLongCaptureReady"])

    def test_safety_violation_is_not_ready(self):
        manifest = dict(SAFE_MANIFEST)
        manifest["ramWrites"] = 1
        out = self.status(manifest=manifest)
        self.assertNotEqual(out["overallResult"], "PASS")
        self.assertFalse(out["tenRoomLongCaptureReady"])

    def test_long_capture_never_auto_starts(self):
        out = self.status()
        self.assertFalse(out["longCaptureAutoStarted"])

    def test_unknown_empty_child_health_must_fail_closed(self):
        # QA requirement 5: child health unknown cannot PASS. An empty mapping
        # has no proof that either required child exists or is alive.
        out = self.status(process_state={})
        self.assertFalse(out["live"]["processes"]["healthKnown"])
        self.assertFalse(out["live"]["automatedChecksReady"])
        self.assertNotEqual(out["overallResult"], "PASS")
        self.assertFalse(out["tenRoomLongCaptureReady"])

    def test_partial_child_health_must_fail_closed(self):
        # Knowing only one child is insufficient for a unified proof.
        for process in ({"launcherRequired": True}, {"recorderRequired": True}):
            with self.subTest(process=process):
                out = self.status(process_state=process)
                self.assertFalse(out["live"]["automatedChecksReady"])
                self.assertNotEqual(out["overallResult"], "PASS")
                self.assertFalse(out["tenRoomLongCaptureReady"])

    def test_stale_pylaunch_positive_json_must_not_retain_current_authority(self):
        # PYLAUNCH proof schema carries lastUpdateUtc. A live-but-hung child can
        # leave a prior PASS JSON behind. Unified proof must reject stale success,
        # not merely check process poll()==None.
        stale = dict(PASS_PROOF)
        stale["lastUpdateUtc"] = "2000-01-01T00:00:00+00:00"
        out = self.status(proof=stale, process_state=dict(LIVE_PROCESSES))
        self.assertFalse(out["live"]["automatedChecksReady"])
        self.assertNotEqual(out["overallResult"], "PASS")
        self.assertFalse(out["tenRoomLongCaptureReady"])


if __name__ == "__main__":
    unittest.main(verbosity=2)

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

LIVE_PROCESSES = {
    "launcherRequired": True,
    "recorderRequired": True,
    "launcherExitCode": None,
    "recorderExitCode": None,
}


class UnifiedProofTests(unittest.TestCase):
    def recorder(self) -> u.RecorderEvidence:
        r = u.RecorderEvidence()
        r.feed("+ 房间 room-1 已连接 — World 921031 已确认 / Discovery V2 / 只读模式")
        return r

    def status(self, *, recorder=None, playability="NOT_READY", blockers=None,
               process_state=None, fleet_manifest=SAFE_MANIFEST, pylaunch_proof=PASS_PROOF):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        return u.build_status(
            run_id="test",
            run_dir=Path(td.name),
            fleet_manifest=fleet_manifest,
            pylaunch_proof=pylaunch_proof,
            recorder=recorder or self.recorder(),
            playability=playability,
            stage="TEST",
            blockers=list(blockers or []),
            process_state=process_state,
        )

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
            LIVE_PROCESSES,
        ))

    def test_missing_recorder_admission_fails_closed(self):
        self.assertFalse(u.automated_ready(
            u.normalize_fleet(SAFE_MANIFEST),
            u.normalize_pylaunch(PASS_PROOF),
            u.RecorderEvidence(),
            LIVE_PROCESSES,
        ))

    def test_safety_violation_fails_closed(self):
        bad = dict(SAFE_MANIFEST)
        bad["ramWrites"] = 1
        self.assertFalse(u.automated_ready(
            u.normalize_fleet(bad),
            u.normalize_pylaunch(PASS_PROOF),
            self.recorder(),
            LIVE_PROCESSES,
        ))

    def test_worker_replacement_safety_violation_fails_closed(self):
        bad = dict(SAFE_MANIFEST)
        bad["windowWorkerReplacement"] = True
        payload = self.status(fleet_manifest=bad, process_state=LIVE_PROCESSES)
        self.assertFalse(payload["live"]["automatedChecksReady"])
        self.assertFalse(payload["live"]["safety"]["pass"])
        self.assertFalse(payload["tenRoomLongCaptureReady"])

    def test_playability_confirmation_required_for_ten_room_ready(self):
        payload = self.status(process_state=LIVE_PROCESSES)
        self.assertTrue(payload["live"]["automatedChecksReady"])
        self.assertTrue(payload["live"]["ownerPromptEligible"])
        self.assertFalse(payload["tenRoomLongCaptureReady"])
        self.assertEqual(payload["overallResult"], "WAITING")

    def test_full_live_pass_sets_ready_without_starting_long_capture(self):
        payload = self.status(playability="CONFIRMED", process_state=LIVE_PROCESSES)
        self.assertEqual(payload["overallResult"], "PASS")
        self.assertTrue(payload["tenRoomLongCaptureReady"])
        self.assertFalse(payload["longCaptureAutoStarted"])

    def test_partial_failure_preserves_positive_evidence(self):
        proof = dict(PASS_PROOF)
        proof["automatedResult"] = "WAITING"
        proof["checks"] = dict(PASS_PROOF["checks"])
        proof["checks"]["World 921031"] = "--"
        payload = self.status(
            pylaunch_proof=proof,
            blockers=["PYLAUNCH blocked"],
            process_state=LIVE_PROCESSES,
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
        self.assertEqual(r.current_health, "HEALTHY")
        self.assertEqual(r.admission_generation, 1)

    def test_fatal_after_admission_revokes_current_authority_and_blocks(self):
        r = self.recorder()
        r.feed("WOF-052L 采集器没有正常完成：已安全拒绝采集")
        payload = self.status(
            recorder=r,
            playability="CONFIRMED",
            process_state=LIVE_PROCESSES,
        )
        self.assertFalse(r.admitted)
        self.assertTrue(r.fatal)
        self.assertEqual(r.current_health, "FATAL")
        self.assertFalse(payload["live"]["automatedChecksReady"])
        self.assertEqual(payload["overallResult"], "BLOCKED")
        self.assertFalse(payload["tenRoomLongCaptureReady"])

    def test_safe_rejection_text_is_fatal_marker(self):
        r = self.recorder()
        r.feed("身份不匹配，已安全拒绝采集")
        self.assertTrue(r.fatal)
        self.assertFalse(r.admitted)

    def test_blocker_plus_owner_y_is_still_blocked(self):
        payload = self.status(
            playability="CONFIRMED",
            blockers=["Recorder 准入失败"],
            process_state=LIVE_PROCESSES,
        )
        self.assertEqual(payload["overallResult"], "BLOCKED")
        self.assertFalse(payload["tenRoomLongCaptureReady"])
        self.assertFalse(payload["live"]["automatedChecksReady"])

    def test_blocker_makes_playability_prompt_unreachable(self):
        payload = self.status(
            blockers=["已有 blocker"],
            process_state=LIVE_PROCESSES,
        )
        self.assertFalse(payload["live"]["ownerPromptEligible"])
        self.assertEqual(payload["overallResult"], "BLOCKED")

    def test_pylaunch_exit_after_pass_fails_closed(self):
        process = dict(LIVE_PROCESSES)
        process["launcherExitCode"] = 7
        payload = self.status(playability="CONFIRMED", process_state=process)
        self.assertEqual(payload["overallResult"], "BLOCKED")
        self.assertFalse(payload["live"]["automatedChecksReady"])
        self.assertFalse(payload["tenRoomLongCaptureReady"])
        self.assertIn("PYLAUNCH 子进程已退出（code=7）", payload["live"]["blockers"])

    def test_recorder_exit_after_admission_fails_closed(self):
        process = dict(LIVE_PROCESSES)
        process["recorderExitCode"] = 9
        payload = self.status(playability="CONFIRMED", process_state=process)
        self.assertEqual(payload["overallResult"], "BLOCKED")
        self.assertFalse(payload["live"]["automatedChecksReady"])
        self.assertFalse(payload["tenRoomLongCaptureReady"])
        self.assertIn("Recorder 子进程已退出（code=9）", payload["live"]["blockers"])

    def test_recovery_requires_new_current_positive_state(self):
        r = self.recorder()
        first_generation = r.admission_generation
        r.feed("WOF-052L 采集器没有正常完成")
        self.assertFalse(r.current_healthy)
        self.assertFalse(u.automated_ready(
            u.normalize_fleet(SAFE_MANIFEST), u.normalize_pylaunch(PASS_PROOF), r, LIVE_PROCESSES
        ))
        r.feed("+ 房间 room-1 已连接 — World 921031 已确认 / Discovery V2 / 只读模式")
        self.assertTrue(r.current_healthy)
        self.assertGreater(r.admission_generation, first_generation)
        self.assertTrue(u.automated_ready(
            u.normalize_fleet(SAFE_MANIFEST), u.normalize_pylaunch(PASS_PROOF), r, LIVE_PROCESSES
        ))

    def test_sticky_run_blocker_prevents_recovered_state_from_passing_same_run(self):
        r = self.recorder()
        r.feed("WOF-052L 采集器没有正常完成")
        sticky = ["Recorder 曾发生 fatal"]
        r.feed("+ 房间 room-1 已连接 — World 921031 已确认 / Discovery V2 / 只读模式")
        payload = self.status(
            recorder=r,
            playability="CONFIRMED",
            blockers=sticky,
            process_state=LIVE_PROCESSES,
        )
        self.assertEqual(payload["overallResult"], "BLOCKED")
        self.assertFalse(payload["tenRoomLongCaptureReady"])
        self.assertTrue(payload["live"]["recorderDiscoveryV2Admission"]["admitted"])

    def test_historical_recorder_positive_evidence_retained_after_fatal(self):
        r = self.recorder()
        admission = r.last_admission_line
        r.feed("WOF-052L 采集器没有正常完成")
        payload = self.status(recorder=r, process_state=LIVE_PROCESSES)
        rec = payload["live"]["recorderDiscoveryV2Admission"]
        self.assertFalse(rec["admitted"])
        self.assertTrue(rec["history"]["everAdmitted"])
        self.assertEqual(rec["history"]["lastAdmissionEvidence"], admission)
        self.assertTrue(rec["history"]["everFatal"])
        self.assertTrue(payload["live"]["fleetDiscoveryV2"]["workerIndicator"])
        self.assertTrue(payload["live"]["pylaunchAuthoritativeProof"]["automatedPass"])

    def test_missing_process_health_cannot_satisfy_live_readiness(self):
        payload = self.status(process_state=None)
        self.assertFalse(payload["live"]["automatedChecksReady"])
        self.assertFalse(payload["live"]["processes"]["healthKnown"])
        self.assertFalse(payload["live"]["processes"]["healthy"])
        self.assertFalse(payload["tenRoomLongCaptureReady"])

    def test_repository_pass_never_substitutes_live_pass(self):
        payload = self.status(
            recorder=u.RecorderEvidence(),
            fleet_manifest=None,
            pylaunch_proof=None,
            process_state=None,
        )
        self.assertEqual(payload["repository"]["result"], "PASS")
        self.assertFalse(payload["repository"]["liveProofClaimed"])
        self.assertEqual(payload["live"]["result"], "WAITING")
        self.assertEqual(payload["overallResult"], "WAITING")
        self.assertFalse(payload["tenRoomLongCaptureReady"])

    def test_long_capture_is_never_auto_started_even_on_pass(self):
        payload = self.status(playability="CONFIRMED", process_state=LIVE_PROCESSES)
        self.assertEqual(payload["overallResult"], "PASS")
        self.assertFalse(payload["longCaptureAutoStarted"])


if __name__ == "__main__":
    unittest.main(verbosity=2)

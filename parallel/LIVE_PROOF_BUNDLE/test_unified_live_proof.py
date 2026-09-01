from __future__ import annotations

import io
import queue
import tempfile
import time
import unittest
from datetime import datetime, timedelta, timezone
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

PASS_PROOF_BASE = {
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


def iso_age(seconds: float = 0.0) -> str:
    value = datetime.now(timezone.utc) - timedelta(seconds=seconds)
    return value.isoformat(timespec="seconds")


def fresh_proof() -> dict:
    proof = dict(PASS_PROOF_BASE)
    proof["checks"] = dict(PASS_PROOF_BASE["checks"])
    proof["lastUpdateUtc"] = iso_age(0)
    return proof


def live_processes(*, generation: int = 1, age: float = 0.0) -> dict:
    return {
        "observedAtUtc": iso_age(age),
        "observationGeneration": generation,
        "launcherRequired": True,
        "recorderRequired": True,
        "launcherLive": True,
        "recorderLive": True,
        "launcherExitCode": None,
        "recorderExitCode": None,
    }


class UnifiedProofTests(unittest.TestCase):
    def recorder(self) -> u.RecorderEvidence:
        r = u.RecorderEvidence()
        r.feed("+ 房间 room-1 已连接 — World 921031 已确认 / Discovery V2 / 只读模式")
        return r

    def status(
        self,
        *,
        recorder=None,
        playability="NOT_READY",
        blockers=None,
        process_state=None,
        fleet_manifest=SAFE_MANIFEST,
        pylaunch_proof=None,
    ):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        return u.build_status(
            run_id="test",
            run_dir=Path(td.name),
            fleet_manifest=fleet_manifest,
            pylaunch_proof=fresh_proof() if pylaunch_proof is None else pylaunch_proof,
            recorder=recorder or self.recorder(),
            playability=playability,
            stage="TEST",
            blockers=list(blockers or []),
            process_state=live_processes() if process_state is None else process_state,
        )

    def test_fleet_indicator_is_explicitly_non_authoritative(self):
        f = u.normalize_fleet(SAFE_MANIFEST)
        self.assertTrue(f["workerIndicator"])
        self.assertEqual(f["workerAuthority"], "cheap-indicator-only")
        self.assertFalse(f["world921031Authoritative"])

    def test_automated_ready_requires_all_three_current_lanes(self):
        self.assertTrue(u.automated_ready(
            u.normalize_fleet(SAFE_MANIFEST),
            u.normalize_pylaunch(fresh_proof()),
            self.recorder(),
            live_processes(),
        ))

    def test_missing_recorder_admission_fails_closed(self):
        self.assertFalse(u.automated_ready(
            u.normalize_fleet(SAFE_MANIFEST),
            u.normalize_pylaunch(fresh_proof()),
            u.RecorderEvidence(),
            live_processes(),
        ))

    def test_safety_violation_fails_closed(self):
        bad = dict(SAFE_MANIFEST)
        bad["ramWrites"] = 1
        self.assertFalse(u.automated_ready(
            u.normalize_fleet(bad),
            u.normalize_pylaunch(fresh_proof()),
            self.recorder(),
            live_processes(),
        ))

    def test_worker_replacement_safety_violation_fails_closed(self):
        bad = dict(SAFE_MANIFEST)
        bad["windowWorkerReplacement"] = True
        payload = self.status(fleet_manifest=bad)
        self.assertFalse(payload["live"]["automatedChecksReady"])
        self.assertFalse(payload["live"]["safety"]["pass"])
        self.assertFalse(payload["tenRoomLongCaptureReady"])

    def test_playability_confirmation_required_for_ten_room_ready(self):
        payload = self.status()
        self.assertTrue(payload["live"]["automatedChecksReady"])
        self.assertTrue(payload["live"]["ownerPromptEligible"])
        self.assertFalse(payload["tenRoomLongCaptureReady"])
        self.assertEqual(payload["overallResult"], "WAITING")

    def test_full_live_pass_sets_ready_without_starting_long_capture(self):
        payload = self.status(playability="CONFIRMED")
        self.assertEqual(payload["overallResult"], "PASS")
        self.assertTrue(payload["tenRoomLongCaptureReady"])
        self.assertFalse(payload["longCaptureAutoStarted"])

    def test_partial_failure_preserves_positive_evidence(self):
        proof = fresh_proof()
        proof["automatedResult"] = "WAITING"
        proof["checks"]["World 921031"] = "--"
        payload = self.status(
            pylaunch_proof=proof,
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
        self.assertEqual(r.current_health, "HEALTHY")
        self.assertEqual(r.admission_generation, 1)
        self.assertGreaterEqual(r.output_generation, 2)
        self.assertTrue(r.current_fresh)

    def test_fatal_after_admission_revokes_current_authority_and_blocks(self):
        r = self.recorder()
        r.feed("WOF-052L 采集器没有正常完成：已安全拒绝采集")
        payload = self.status(recorder=r, playability="CONFIRMED")
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
        )
        self.assertEqual(payload["overallResult"], "BLOCKED")
        self.assertFalse(payload["tenRoomLongCaptureReady"])
        self.assertFalse(payload["live"]["automatedChecksReady"])

    def test_blocker_makes_playability_prompt_unreachable(self):
        payload = self.status(blockers=["已有 blocker"])
        self.assertFalse(payload["live"]["ownerPromptEligible"])
        self.assertEqual(payload["overallResult"], "BLOCKED")

    def test_pylaunch_exit_after_pass_fails_closed(self):
        process = live_processes()
        process["launcherLive"] = False
        process["launcherExitCode"] = 7
        payload = self.status(playability="CONFIRMED", process_state=process)
        self.assertEqual(payload["overallResult"], "BLOCKED")
        self.assertFalse(payload["live"]["automatedChecksReady"])
        self.assertFalse(payload["tenRoomLongCaptureReady"])
        self.assertIn("PYLAUNCH 子进程已退出（code=7）", payload["live"]["blockers"])

    def test_recorder_exit_after_admission_fails_closed(self):
        process = live_processes()
        process["recorderLive"] = False
        process["recorderExitCode"] = 9
        payload = self.status(playability="CONFIRMED", process_state=process)
        self.assertEqual(payload["overallResult"], "BLOCKED")
        self.assertFalse(payload["live"]["automatedChecksReady"])
        self.assertFalse(payload["tenRoomLongCaptureReady"])
        self.assertIn("Recorder 子进程已退出（code=9）", payload["live"]["blockers"])

    def test_recovery_requires_new_current_recorder_positive_generation(self):
        r = self.recorder()
        first_generation = r.admission_generation
        r.feed("WOF-052L 采集器没有正常完成")
        self.assertFalse(r.current_healthy)
        self.assertFalse(u.automated_ready(
            u.normalize_fleet(SAFE_MANIFEST), u.normalize_pylaunch(fresh_proof()),
            r, live_processes()
        ))
        r.feed("+ 房间 room-1 已连接 — World 921031 已确认 / Discovery V2 / 只读模式")
        self.assertTrue(r.current_healthy)
        self.assertGreater(r.admission_generation, first_generation)
        self.assertTrue(u.automated_ready(
            u.normalize_fleet(SAFE_MANIFEST), u.normalize_pylaunch(fresh_proof()),
            r, live_processes()
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
        )
        self.assertEqual(payload["overallResult"], "BLOCKED")
        self.assertFalse(payload["tenRoomLongCaptureReady"])
        self.assertTrue(payload["live"]["recorderDiscoveryV2Admission"]["admitted"])

    def test_historical_recorder_positive_evidence_retained_after_fatal(self):
        r = self.recorder()
        admission = r.last_admission_line
        r.feed("WOF-052L 采集器没有正常完成")
        payload = self.status(recorder=r)
        rec = payload["live"]["recorderDiscoveryV2Admission"]
        self.assertFalse(rec["admitted"])
        self.assertTrue(rec["history"]["everAdmitted"])
        self.assertEqual(rec["history"]["lastAdmissionEvidence"], admission)
        self.assertTrue(rec["history"]["everFatal"])
        self.assertTrue(payload["live"]["fleetDiscoveryV2"]["workerIndicator"])
        self.assertTrue(payload["live"]["pylaunchAuthoritativeProof"]["automatedPass"])

    def test_missing_process_health_cannot_satisfy_live_readiness(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        payload = u.build_status(
            run_id="test",
            run_dir=Path(td.name),
            fleet_manifest=SAFE_MANIFEST,
            pylaunch_proof=fresh_proof(),
            recorder=self.recorder(),
            playability="CONFIRMED",
            stage="TEST",
            blockers=[],
            process_state=None,
        )
        self.assertFalse(payload["live"]["automatedChecksReady"])
        self.assertFalse(payload["live"]["processes"]["healthKnown"])
        self.assertFalse(payload["live"]["processes"]["healthy"])
        self.assertFalse(payload["tenRoomLongCaptureReady"])

    def test_repository_pass_never_substitutes_live_pass(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        payload = u.build_status(
            run_id="test",
            run_dir=Path(td.name),
            fleet_manifest=None,
            pylaunch_proof=None,
            recorder=u.RecorderEvidence(),
            playability="NOT_READY",
            stage="TEST",
            blockers=[],
            process_state=None,
        )
        self.assertEqual(payload["repository"]["result"], "PASS")
        self.assertFalse(payload["repository"]["liveProofClaimed"])
        self.assertEqual(payload["live"]["result"], "WAITING")
        self.assertEqual(payload["overallResult"], "WAITING")
        self.assertFalse(payload["tenRoomLongCaptureReady"])

    def test_long_capture_is_never_auto_started_even_on_pass(self):
        payload = self.status(playability="CONFIRMED")
        self.assertEqual(payload["overallResult"], "PASS")
        self.assertFalse(payload["longCaptureAutoStarted"])

    # Freshness / malformed mapping adversarial vectors.

    def test_unknown_empty_child_health_is_blocked(self):
        payload = self.status(playability="CONFIRMED", process_state={})
        self.assertFalse(payload["live"]["processes"]["healthKnown"])
        self.assertEqual(payload["overallResult"], "BLOCKED")
        self.assertFalse(payload["tenRoomLongCaptureReady"])

    def test_partial_child_health_is_blocked(self):
        for process in (
            {"launcherRequired": True},
            {"recorderRequired": True},
            {"launcherRequired": True, "recorderRequired": True},
        ):
            with self.subTest(process=process):
                payload = self.status(playability="CONFIRMED", process_state=process)
                self.assertFalse(payload["live"]["processes"]["healthKnown"])
                self.assertEqual(payload["overallResult"], "BLOCKED")
                self.assertFalse(payload["tenRoomLongCaptureReady"])

    def test_null_or_wrong_type_child_health_is_blocked(self):
        bad = live_processes()
        bad["launcherLive"] = None
        payload = self.status(playability="CONFIRMED", process_state=bad)
        self.assertFalse(payload["live"]["processes"]["healthKnown"])
        self.assertEqual(payload["overallResult"], "BLOCKED")

        bad2 = live_processes()
        bad2["recorderRequired"] = "yes"
        payload2 = self.status(playability="CONFIRMED", process_state=bad2)
        self.assertFalse(payload2["live"]["processes"]["healthKnown"])
        self.assertEqual(payload2["overallResult"], "BLOCKED")

    def test_inconsistent_live_and_exit_code_is_malformed(self):
        bad = live_processes()
        bad["launcherLive"] = True
        bad["launcherExitCode"] = 3
        payload = self.status(playability="CONFIRMED", process_state=bad)
        self.assertFalse(payload["live"]["processes"]["healthKnown"])
        self.assertEqual(payload["overallResult"], "BLOCKED")

    def test_stale_process_observation_is_blocked(self):
        stale = live_processes(age=u.PROCESS_FRESHNESS_SECONDS + 5)
        payload = self.status(playability="CONFIRMED", process_state=stale)
        self.assertTrue(payload["live"]["processes"]["healthKnown"])
        self.assertFalse(payload["live"]["processes"]["current"])
        self.assertEqual(payload["overallResult"], "BLOCKED")

    def test_both_children_must_be_explicitly_required(self):
        process = live_processes()
        process["recorderRequired"] = False
        process["recorderLive"] = False
        process["recorderExitCode"] = 0
        payload = self.status(playability="CONFIRMED", process_state=process)
        self.assertTrue(payload["live"]["processes"]["healthKnown"])
        self.assertEqual(payload["overallResult"], "BLOCKED")

    def test_stale_pylaunch_positive_json_is_diagnostic_not_authority(self):
        stale = fresh_proof()
        stale["lastUpdateUtc"] = iso_age(u.PYLAUNCH_FRESHNESS_SECONDS + 30)
        payload = self.status(playability="CONFIRMED", pylaunch_proof=stale)
        py = payload["live"]["pylaunchAuthoritativeProof"]
        self.assertTrue(py["automatedPass"])
        self.assertFalse(py["fresh"])
        self.assertFalse(py["currentAutomatedPass"])
        self.assertEqual(payload["overallResult"], "BLOCKED")
        self.assertFalse(payload["tenRoomLongCaptureReady"])

    def test_missing_or_malformed_pylaunch_timestamp_cannot_authorize_pass(self):
        for value in (None, "not-a-time", "2026-09-01T10:00:00"):
            proof = fresh_proof()
            if value is None:
                proof.pop("lastUpdateUtc", None)
            else:
                proof["lastUpdateUtc"] = value
            with self.subTest(value=value):
                payload = self.status(playability="CONFIRMED", pylaunch_proof=proof)
                self.assertTrue(payload["live"]["pylaunchAuthoritativeProof"]["automatedPass"])
                self.assertFalse(payload["live"]["pylaunchAuthoritativeProof"]["currentAutomatedPass"])
                self.assertEqual(payload["overallResult"], "BLOCKED")

    def test_current_pylaunch_generation_restores_authority_in_fresh_state(self):
        stale = fresh_proof()
        stale["lastUpdateUtc"] = iso_age(u.PYLAUNCH_FRESHNESS_SECONDS + 30)
        stale_payload = self.status(playability="CONFIRMED", pylaunch_proof=stale)
        self.assertEqual(stale_payload["overallResult"], "BLOCKED")

        current_payload = self.status(playability="CONFIRMED", pylaunch_proof=fresh_proof())
        self.assertEqual(current_payload["overallResult"], "PASS")
        self.assertTrue(current_payload["live"]["pylaunchAuthoritativeProof"]["currentAutomatedPass"])

    def test_stale_recorder_admission_is_diagnostic_not_authority(self):
        rec = self.recorder()
        rec._last_output_monotonic = time.monotonic() - u.RECORDER_FRESHNESS_SECONDS - 1
        payload = self.status(recorder=rec, playability="CONFIRMED")
        self.assertTrue(payload["live"]["recorderDiscoveryV2Admission"]["admitted"])
        self.assertEqual(payload["live"]["recorderDiscoveryV2Admission"]["currentHealth"], "STALE")
        self.assertEqual(payload["overallResult"], "BLOCKED")
        self.assertFalse(payload["tenRoomLongCaptureReady"])

    def test_recorder_new_output_generation_recovers_freshness(self):
        rec = self.recorder()
        old_generation = rec.output_generation
        rec._last_output_monotonic = time.monotonic() - u.RECORDER_FRESHNESS_SECONDS - 1
        self.assertFalse(rec.current_healthy)
        rec.feed("Fleet entries 1 | Recorder workers 1 | READ ONLY / RAM writes 0")
        self.assertGreater(rec.output_generation, old_generation)
        self.assertTrue(rec.current_healthy)
        payload = self.status(recorder=rec, playability="CONFIRMED")
        self.assertEqual(payload["overallResult"], "PASS")

    def test_authority_generation_gate_requires_all_three_to_advance(self):
        before = {"pylaunch": "a", "recorder": 10, "process": 20}
        good = {"pylaunch": "b", "recorder": 11, "process": 21}
        self.assertTrue(u.authority_generations_advanced(before, good))
        self.assertFalse(u.authority_generations_advanced(
            before, {"pylaunch": "a", "recorder": 11, "process": 21}
        ))
        self.assertFalse(u.authority_generations_advanced(
            before, {"pylaunch": "b", "recorder": 10, "process": 21}
        ))
        self.assertFalse(u.authority_generations_advanced(
            before, {"pylaunch": "b", "recorder": 11, "process": 20}
        ))

    def test_reader_treats_carriage_return_as_recorder_heartbeat(self):
        class FakeProc:
            stdout = io.StringIO("first\rsecond\nthird\r")
        rec = u.RecorderEvidence()
        q = queue.Queue()
        u.reader(FakeProc(), "RECORDER", rec, q)
        self.assertEqual(rec.output_generation, 3)
        self.assertEqual(rec.lines[-3:], ["first", "second", "third"])
        self.assertEqual(q.qsize(), 3)


if __name__ == "__main__":
    unittest.main(verbosity=2)

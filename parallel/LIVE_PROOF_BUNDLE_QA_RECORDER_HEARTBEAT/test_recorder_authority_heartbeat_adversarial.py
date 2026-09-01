from __future__ import annotations

import io
import queue
import sys
import tempfile
import time
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BUNDLE = ROOT / "parallel" / "LIVE_PROOF_BUNDLE"
sys.path.insert(0, str(BUNDLE))

import unified_live_proof as u  # noqa: E402
import unified_preflight as preflight  # noqa: E402

ADMISSION_OLD = "+ 房间 qa-old 已连接 — World 921031 已确认 / Discovery V2 / 只读模式"
ADMISSION_NEW = "+ 房间 qa-new 已连接 — World 921031 已确认 / Discovery V2 / 只读模式"
HEARTBEAT = "Fleet entries 1 | Recorder workers 1 | READ ONLY / RAM writes 0"
FATAL = "WOF-052L 采集器没有正常完成：已安全拒绝采集"

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
        "status": {"browser": "OK", "page": "OK", "worker": "OK"},
    }],
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


def fresh_pylaunch() -> dict:
    return {
        "schema": "wof-python-launcher-windows-proof-v1",
        "automatedResult": "PASS",
        "lastUpdateUtc": now_iso(),
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
    }


def live_processes(generation: int = 10) -> dict:
    return {
        "observedAtUtc": now_iso(),
        "observationGeneration": generation,
        "launcherRequired": True,
        "recorderRequired": True,
        "launcherLive": True,
        "recorderLive": True,
        "launcherExitCode": None,
        "recorderExitCode": None,
    }


class RecorderAuthorityHeartbeatFreshQA(unittest.TestCase):
    def admitted(self, line: str = ADMISSION_NEW) -> u.RecorderEvidence:
        rec = u.RecorderEvidence()
        rec.feed(line)
        return rec

    def stale(self, rec: u.RecorderEvidence) -> None:
        rec._last_output_monotonic = time.monotonic() - u.RECORDER_FRESHNESS_SECONDS - 1
        self.assertFalse(rec.current_healthy)

    def test_noise_cr_diagnostics_and_unrelated_json_never_renew_stale_authority(self):
        noises = (
            "arbitrary stdout",
            "diagnostic: workers still polling",
            '{"kind":"diagnostic","ok":true}',
            "Fleet entries nope | Recorder workers 1 | READ ONLY / RAM writes 0",
        )
        for text in noises:
            with self.subTest(text=text):
                rec = self.admitted()
                authority_before = rec.authority_generation
                output_before = rec.output_generation
                self.stale(rec)
                class FakeProc:
                    stdout = io.StringIO(text + "\r")
                q: queue.Queue[tuple[str, str]] = queue.Queue()
                u.reader(FakeProc(), "RECORDER", rec, q)
                self.assertEqual(rec.authority_generation, authority_before)
                self.assertGreater(rec.output_generation, output_before)
                self.assertFalse(rec.current_healthy)

    def test_partial_cr_fragments_cannot_renew_authority(self):
        rec = self.admitted()
        authority_before = rec.authority_generation
        self.stale(rec)
        class FakeProc:
            stdout = io.StringIO(
                "Fleet entries 1 | Recorder workers 1 |\r"
                "READ ONLY / RAM writes 0\r"
            )
        q: queue.Queue[tuple[str, str]] = queue.Queue()
        u.reader(FakeProc(), "RECORDER", rec, q)
        self.assertEqual(rec.authority_generation, authority_before)
        self.assertFalse(rec.current_healthy)

    def test_recognized_current_supervisor_heartbeat_renews_active_admission(self):
        rec = self.admitted()
        authority_before = rec.authority_generation
        self.stale(rec)
        rec.feed(HEARTBEAT)
        self.assertEqual(rec.authority_generation, authority_before + 1)
        self.assertEqual(rec.last_authority_kind, "supervisor-heartbeat")
        self.assertTrue(rec.current_healthy)

    def test_fresh_recognized_admission_renews_authority(self):
        rec = u.RecorderEvidence()
        rec.feed(ADMISSION_NEW)
        self.assertTrue(rec.current_healthy)
        self.assertEqual(rec.last_authority_kind, "admission")
        self.assertEqual(rec.admission_authority_generation, rec.authority_generation)

    def test_replayed_prior_generation_heartbeat_must_not_renew_new_generation(self):
        rec = self.admitted(ADMISSION_OLD)
        prior_generation_heartbeat = HEARTBEAT
        rec.feed(FATAL)
        rec.feed(ADMISSION_NEW)
        current_admission_authority = rec.admission_authority_generation
        self.stale(rec)

        # Adversarial provenance: this exact heartbeat was captured from the prior
        # admission generation and is replayed after a new admission generation.
        rec.feed(prior_generation_heartbeat)

        self.assertEqual(
            rec.authority_generation,
            current_admission_authority,
            "stale prior-generation heartbeat advanced the new authority generation",
        )
        self.assertFalse(
            rec.current_healthy,
            "stale prior-generation heartbeat revived a stale new admission",
        )

    def test_replayed_prior_generation_admission_must_not_clear_revocation(self):
        rec = self.admitted(ADMISSION_OLD)
        prior_generation_admission = ADMISSION_OLD
        rec.feed(FATAL)
        self.assertTrue(rec.fatal)
        self.assertFalse(rec.admitted)

        # This is not a newly produced admission; it is a delayed/replayed line
        # captured from the revoked generation.
        rec.feed(prior_generation_admission)

        self.assertTrue(rec.fatal, "stale prior-generation admission cleared revocation")
        self.assertFalse(rec.admitted, "stale prior-generation admission re-established authority")
        self.assertFalse(rec.current_healthy)

    def test_fatal_revocation_remains_dominant_over_generic_and_heartbeat(self):
        rec = self.admitted()
        rec.feed(FATAL)
        authority_after_fatal = rec.authority_generation
        rec.feed("generic after fatal")
        rec.feed(HEARTBEAT)
        self.assertTrue(rec.fatal)
        self.assertFalse(rec.admitted)
        self.assertFalse(rec.current_healthy)
        self.assertEqual(rec.authority_generation, authority_after_fatal)

    def test_current_healthy_requires_trusted_authority_not_generic_liveness(self):
        rec = self.admitted()
        authority_before = rec.authority_generation
        self.stale(rec)
        for i in range(5):
            rec.feed(f"diagnostic {i}")
        self.assertEqual(rec.authority_generation, authority_before)
        self.assertFalse(rec.current_healthy)
        self.assertGreater(rec.output_generation, authority_before)

    def test_owner_double_generation_gate_requires_all_three_authorities(self):
        before = {"pylaunch": "p1", "recorder": 10, "process": 20}
        first = {"pylaunch": "p2", "recorder": 11, "process": 21}
        self.assertTrue(u.authority_generations_advanced(before, first))
        second_missing_recorder = {"pylaunch": "p3", "recorder": 11, "process": 22}
        self.assertFalse(u.authority_generations_advanced(first, second_missing_recorder))
        second = {"pylaunch": "p3", "recorder": 12, "process": 22}
        self.assertTrue(u.authority_generations_advanced(first, second))

    def test_status_keeps_safety_chinese_ux_and_no_auto_long_capture(self):
        rec = self.admitted()
        with tempfile.TemporaryDirectory() as td:
            out = u.build_status(
                run_id="qa-recorder-authority-heartbeat",
                run_dir=Path(td),
                fleet_manifest=SAFE_MANIFEST,
                pylaunch_proof=fresh_pylaunch(),
                recorder=rec,
                playability="CONFIRMED",
                stage="RECORDER_AUTHORITY_HEARTBEAT_QA",
                blockers=[],
                process_state=live_processes(),
            )
        self.assertFalse(out["longCaptureAutoStarted"])
        self.assertTrue(out["live"]["safety"]["pass"])
        self.assertEqual(out["live"]["safety"]["ramWrites"], 0)
        self.assertFalse(out["live"]["safety"]["inputInjection"])
        self.assertRegex(out["ownerSummaryZh"], r"[\u3400-\u9fff]")

    def test_preflight_blocked_result_detection_remains_fail_closed(self):
        blocked = preflight._current_block(
            "# QA\n\nBLOCKED — synthetic fresh QA blocker\n"
        )
        self.assertIsNotNone(blocked)
        self.assertTrue(any(
            component == "liveProof" and "LIVE_PROOF_BUNDLE_QA_FRESHNESS/RESULT.md" in path
            for component, path, _marker in preflight.STATUS_GATES
        ))


if __name__ == "__main__":
    unittest.main(verbosity=2)

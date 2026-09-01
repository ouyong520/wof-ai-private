from __future__ import annotations

import io
import queue
import time
import unittest
from datetime import datetime, timedelta, timezone

import unified_live_proof as u

ADMISSION = "+ 房间 room-1 已连接 — World 921031 已确认 / Discovery V2 / 只读模式"
HEARTBEAT = "Fleet entries 1 | Recorder workers 1 | READ ONLY / RAM writes 0"


def iso_at(delta_seconds: float) -> str:
    return (datetime.now(timezone.utc) + timedelta(seconds=delta_seconds)).isoformat(timespec="seconds")


class RecorderAuthorityHeartbeatTests(unittest.TestCase):
    def admitted(self) -> u.RecorderEvidence:
        rec = u.RecorderEvidence()
        rec.feed(ADMISSION)
        return rec

    def stale(self, rec: u.RecorderEvidence) -> None:
        rec._last_output_monotonic = time.monotonic() - u.RECORDER_FRESHNESS_SECONDS - 1
        self.assertFalse(rec.current_fresh)

    def test_arbitrary_diagnostic_cannot_revive_stale_admission(self):
        rec = self.admitted()
        authority_before = rec.authority_generation
        output_before = rec.output_generation
        self.stale(rec)
        rec.feed("arbitrary diagnostic text")
        self.assertEqual(rec.authority_generation, authority_before)
        self.assertGreater(rec.output_generation, output_before)
        self.assertFalse(rec.current_healthy)
        self.assertEqual(rec.current_health, "STALE")

    def test_genuine_current_supervisor_heartbeat_refreshes_authority(self):
        rec = self.admitted()
        authority_before = rec.authority_generation
        self.stale(rec)
        rec.feed(HEARTBEAT)
        self.assertEqual(rec.authority_generation, authority_before + 1)
        self.assertEqual(rec.last_authority_kind, "supervisor-heartbeat")
        self.assertEqual(rec.last_heartbeat_line, HEARTBEAT)
        self.assertTrue(rec.current_healthy)

    def test_malformed_or_near_match_heartbeat_fails_closed(self):
        near_matches = (
            "Fleet entries 1 | Recorder workers 1 | READ ONLY / RAM writes 1",
            "Fleet entries 1 | Recorder workers one | READ ONLY / RAM writes 0",
            "Fleet entries 1 | Recorder workers 1 | READ ONLY / RAM writes 0 extra",
            "Fleet entries 0 | Recorder workers 1 | READ ONLY / RAM writes 0",
            "Fleet entries 1 | Recorder workers 0 | READ ONLY / RAM writes 0",
            "fleet entries 1 | Recorder workers 1 | READ ONLY / RAM writes 0",
        )
        for line in near_matches:
            with self.subTest(line=line):
                rec = self.admitted()
                authority_before = rec.authority_generation
                self.stale(rec)
                rec.feed(line)
                self.assertEqual(rec.authority_generation, authority_before)
                self.assertFalse(rec.current_healthy)

    def test_repeated_arbitrary_output_never_advances_authority_generation(self):
        rec = self.admitted()
        authority_before = rec.authority_generation
        self.stale(rec)
        for i in range(20):
            rec.feed(f"diagnostic {i}")
        self.assertEqual(rec.authority_generation, authority_before)
        self.assertFalse(rec.current_healthy)
        self.assertGreaterEqual(rec.output_generation, 21)

    def test_fatal_overrides_authority_and_later_output_cannot_revive(self):
        rec = self.admitted()
        rec.feed(HEARTBEAT)
        rec.feed("WOF-052L 采集器没有正常完成：已安全拒绝采集")
        authority_after_fatal = rec.authority_generation
        self.assertTrue(rec.fatal)
        self.assertFalse(rec.admitted)
        self.assertFalse(rec.current_healthy)
        rec.feed("generic after fatal")
        rec.feed(HEARTBEAT)
        self.assertEqual(rec.authority_generation, authority_after_fatal)
        self.assertTrue(rec.fatal)
        self.assertFalse(rec.current_healthy)

    def test_valid_cr_delimited_heartbeat_parsing_refreshes_only_authority_path(self):
        class FakeProc:
            stdout = io.StringIO(HEARTBEAT + "\r")

        rec = self.admitted()
        authority_before = rec.authority_generation
        output_before = rec.output_generation
        self.stale(rec)
        q: queue.Queue[tuple[str, str]] = queue.Queue()
        u.reader(FakeProc(), "RECORDER", rec, q)
        self.assertEqual(q.qsize(), 1)
        self.assertEqual(rec.authority_generation, authority_before + 1)
        self.assertEqual(rec.output_generation, output_before + 1)
        self.assertTrue(rec.current_healthy)

    def test_stale_future_missing_child_authority_fails_closed(self):
        base = {
            "observationGeneration": 1,
            "launcherRequired": True,
            "recorderRequired": True,
            "launcherLive": True,
            "recorderLive": True,
            "launcherExitCode": None,
            "recorderExitCode": None,
        }
        missing = u.normalize_process_health(dict(base))
        self.assertFalse(missing["healthKnown"])
        self.assertFalse(missing["healthy"])

        stale = u.normalize_process_health({**base, "observedAtUtc": iso_at(-(u.PROCESS_FRESHNESS_SECONDS + 5))})
        self.assertTrue(stale["healthKnown"])
        self.assertFalse(stale["current"])
        self.assertFalse(stale["healthy"])

        future = u.normalize_process_health({**base, "observedAtUtc": iso_at(u.CLOCK_SKEW_TOLERANCE_SECONDS + 5)})
        self.assertTrue(future["healthKnown"])
        self.assertFalse(future["current"])
        self.assertFalse(future["healthy"])

    def test_authority_snapshot_uses_trusted_generation_not_generic_output(self):
        rec = self.admitted()
        status = {
            "live": {
                "pylaunchAuthoritativeProof": {"authorityGeneration": "p1"},
                "recorderDiscoveryV2Admission": {
                    "authorityGeneration": rec.authority_generation,
                    "outputGeneration": rec.output_generation,
                },
                "processes": {"observationGeneration": 3},
            }
        }
        before = u.authority_generation_snapshot(status)
        rec.feed("arbitrary output")
        status["live"]["recorderDiscoveryV2Admission"]["outputGeneration"] = rec.output_generation
        after = u.authority_generation_snapshot(status)
        self.assertEqual(before["recorder"], after["recorder"])


if __name__ == "__main__":
    unittest.main(verbosity=2)

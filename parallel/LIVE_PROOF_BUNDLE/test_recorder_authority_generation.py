from __future__ import annotations

import io
import queue
import time
import unittest
from pathlib import Path

import unified_live_proof as u

ADMISSION_G1 = "+ 房间 generation-1 已连接 — World 921031 已确认 / Discovery V2 / 只读模式"
ADMISSION_G2 = "+ 房间 generation-2 已连接 — World 921031 已确认 / Discovery V2 / 只读模式"
HEARTBEAT = "Fleet entries 1 | Recorder workers 1 | READ ONLY / RAM writes 0"
FATAL = "WOF-052L 采集器没有正常完成：已安全拒绝采集"


class RecorderAuthorityGenerationTests(unittest.TestCase):
    def setUp(self) -> None:
        self._old_base_start = u._BaseStartChild
        self._old_counter = u._child_generation_counter
        self._old_active_ref = u._active_recorder_evidence_ref
        u._child_generation_counter = 0
        u._active_recorder_evidence_ref = None

    def tearDown(self) -> None:
        u._BaseStartChild = self._old_base_start
        u._child_generation_counter = self._old_counter
        u._active_recorder_evidence_ref = self._old_active_ref

    def stale(self, recorder: u.RecorderEvidence) -> None:
        recorder._last_output_monotonic = (
            time.monotonic() - u.RECORDER_FRESHNESS_SECONDS - 1.0
        )
        self.assertFalse(recorder.current_healthy)

    def admitted(self, token: str, line: str) -> u.RecorderEvidence:
        recorder = u.RecorderEvidence()
        recorder.begin_source_generation(token)
        recorder.feed(line, source_generation=token)
        self.assertTrue(recorder.current_healthy)
        self.assertEqual(recorder.admission_source_generation, token)
        return recorder

    def test_generation1_heartbeat_replay_cannot_refresh_generation2(self):
        recorder = self.admitted("generation-1", ADMISSION_G1)
        recorder.feed(HEARTBEAT, source_generation="generation-1")

        recorder.begin_source_generation("generation-2")
        self.assertFalse(recorder.current_healthy, "rollover must revoke generation 1 immediately")
        recorder.feed(ADMISSION_G2, source_generation="generation-2")
        authority_before_replay = recorder.authority_generation
        self.stale(recorder)

        recorder.feed(HEARTBEAT, source_generation="generation-1")
        self.assertEqual(recorder.authority_generation, authority_before_replay)
        self.assertFalse(recorder.current_healthy)
        self.assertEqual(recorder.admission_source_generation, "generation-2")

        recorder.feed(HEARTBEAT, source_generation="generation-2")
        self.assertEqual(recorder.authority_generation, authority_before_replay + 1)
        self.assertTrue(recorder.current_healthy)

    def test_generation1_admission_replay_after_generation2_is_ignored(self):
        recorder = self.admitted("generation-1", ADMISSION_G1)
        recorder.feed(FATAL, source_generation="generation-1")
        recorder.begin_source_generation("generation-2")
        recorder.feed(ADMISSION_G2, source_generation="generation-2")
        authority_before = recorder.authority_generation
        admission_before = recorder.admission_line

        recorder.feed(ADMISSION_G1, source_generation="generation-1")
        self.assertEqual(recorder.authority_generation, authority_before)
        self.assertEqual(recorder.admission_line, admission_before)
        self.assertEqual(recorder.admission_source_generation, "generation-2")
        self.assertTrue(recorder.current_healthy)

    def test_current_generation_admission_and_heartbeat_refresh_normally(self):
        recorder = u.RecorderEvidence()
        recorder.begin_source_generation("current")
        recorder.feed(ADMISSION_G2, source_generation="current")
        self.assertTrue(recorder.current_healthy)
        admission_authority = recorder.authority_generation
        self.stale(recorder)

        recorder.feed(HEARTBEAT, source_generation="current")
        self.assertEqual(recorder.authority_generation, admission_authority + 1)
        self.assertEqual(recorder.last_authority_kind, "supervisor-heartbeat")
        self.assertTrue(recorder.current_healthy)

    def test_missing_and_wrong_generation_fail_closed(self):
        recorder = u.RecorderEvidence()
        recorder.begin_source_generation("current")

        recorder.feed(ADMISSION_G2)
        self.assertFalse(recorder.admitted)
        recorder.feed(ADMISSION_G2, source_generation="wrong")
        self.assertFalse(recorder.admitted)

        recorder.feed(ADMISSION_G2, source_generation="current")
        self.assertTrue(recorder.admitted)
        self.stale(recorder)
        authority_before = recorder.authority_generation

        recorder.feed(HEARTBEAT)
        recorder.feed(HEARTBEAT, source_generation="wrong")
        self.assertEqual(recorder.authority_generation, authority_before)
        self.assertFalse(recorder.current_healthy)
        self.assertGreaterEqual(recorder.rejected_authority_events, 4)

    def test_restart_rollover_revokes_old_generation_immediately(self):
        recorder = self.admitted("generation-1", ADMISSION_G1)
        authority_before = recorder.authority_generation
        recorder.begin_source_generation("generation-2")

        self.assertFalse(recorder.admitted)
        self.assertFalse(recorder.current_fresh)
        self.assertFalse(recorder.current_healthy)
        self.assertEqual(recorder.authority_generation, authority_before)
        self.assertEqual(recorder.source_generation, "generation-2")

        recorder.feed(HEARTBEAT, source_generation="generation-1")
        self.assertFalse(recorder.current_healthy)
        self.assertEqual(recorder.authority_generation, authority_before)

    def test_child_start_rollover_revokes_before_new_reader(self):
        class FakeProc:
            def __init__(self, pid: int) -> None:
                self.pid = pid
                self.stdout = io.StringIO("")

        next_pid = iter((5101, 5102))
        u._BaseStartChild = lambda cmd, cwd: FakeProc(next(next_pid))

        recorder = u.RecorderEvidence()
        proc1 = u.start_child(["fake-recorder-1"], Path("."))
        gen1 = proc1._wof_authority_generation
        order1 = proc1._wof_authority_generation_order
        recorder.begin_source_generation(gen1, order=order1)
        recorder.feed(ADMISSION_G1, source_generation=gen1)
        recorder.feed(HEARTBEAT, source_generation=gen1)
        self.assertTrue(recorder.current_healthy)
        authority_before = recorder.authority_generation

        proc2 = u.start_child(["fake-recorder-2"], Path("."))
        gen2 = proc2._wof_authority_generation
        self.assertGreater(proc2._wof_authority_generation_order, order1)
        self.assertEqual(recorder.source_generation, gen2)
        self.assertFalse(recorder.admitted)
        self.assertFalse(recorder.current_fresh)
        self.assertFalse(recorder.current_healthy)

        recorder.feed(HEARTBEAT, source_generation=gen1)
        self.assertEqual(recorder.authority_generation, authority_before)
        self.assertFalse(recorder.current_healthy)

    def test_failed_recorder_child_start_does_not_restore_old_authority(self):
        class FakeProc:
            pid = 5201
            stdout = io.StringIO("")

        u._BaseStartChild = lambda cmd, cwd: FakeProc()
        recorder = u.RecorderEvidence()
        proc1 = u.start_child(["fake-recorder-1"], Path("."))
        gen1 = proc1._wof_authority_generation
        order1 = proc1._wof_authority_generation_order
        recorder.begin_source_generation(gen1, order=order1)
        recorder.feed(ADMISSION_G1, source_generation=gen1)
        recorder.feed(HEARTBEAT, source_generation=gen1)
        authority_before = recorder.authority_generation
        self.assertTrue(recorder.current_healthy)

        def fail_start(cmd, cwd):
            raise OSError("synthetic recorder spawn failure")

        u._BaseStartChild = fail_start
        with self.assertRaises(OSError):
            u.start_child(["fake-recorder-2"], Path("."))

        self.assertNotEqual(recorder.source_generation, gen1)
        self.assertIsNotNone(recorder.source_generation_order)
        self.assertGreater(recorder.source_generation_order, order1)
        self.assertFalse(recorder.admitted)
        self.assertFalse(recorder.current_fresh)
        self.assertFalse(recorder.current_healthy)

        recorder.feed(HEARTBEAT, source_generation=gen1)
        self.assertEqual(recorder.authority_generation, authority_before)
        self.assertFalse(recorder.current_healthy)

    def test_non_recorder_child_start_does_not_roll_recorder_generation(self):
        class FakeProc:
            pid = 5301
            stdout = io.StringIO("")

        u._BaseStartChild = lambda cmd, cwd: FakeProc()
        recorder = u.RecorderEvidence()
        recorder.begin_source_generation("generation-1", order=1)
        recorder.feed(ADMISSION_G1, source_generation="generation-1")
        recorder.feed(HEARTBEAT, source_generation="generation-1")
        authority_before = recorder.authority_generation

        u.start_child(["python", "launcher.py", "--proof-json", "proof.json"], Path("."))

        self.assertEqual(recorder.source_generation, "generation-1")
        self.assertTrue(recorder.current_healthy)
        self.assertEqual(recorder.authority_generation, authority_before)

    def test_delayed_out_of_order_old_events_do_not_mutate_current_slot(self):
        recorder = self.admitted("generation-1", ADMISSION_G1)
        recorder.begin_source_generation("generation-2")
        recorder.feed(ADMISSION_G2, source_generation="generation-2")
        authority_before = recorder.authority_generation
        admission_before = recorder.admission_line

        for line in (HEARTBEAT, FATAL, ADMISSION_G1):
            recorder.feed(line, source_generation="generation-1")

        self.assertEqual(recorder.authority_generation, authority_before)
        self.assertEqual(recorder.admission_line, admission_before)
        self.assertFalse(recorder.fatal)
        self.assertTrue(recorder.current_healthy)

    def test_fatal_revokes_source_and_same_generation_cannot_re_admit(self):
        recorder = self.admitted("generation-1", ADMISSION_G1)
        recorder.feed(FATAL, source_generation="generation-1")
        self.assertTrue(recorder.fatal)
        self.assertTrue(recorder.source_revoked)
        authority_before = recorder.authority_generation

        recorder.feed(ADMISSION_G2, source_generation="generation-1")
        recorder.feed(HEARTBEAT, source_generation="generation-1")
        self.assertEqual(recorder.authority_generation, authority_before)
        self.assertFalse(recorder.admitted)
        self.assertFalse(recorder.current_healthy)

    def test_generic_stdout_never_refreshes_authority(self):
        recorder = self.admitted("current", ADMISSION_G2)
        authority_before = recorder.authority_generation
        self.stale(recorder)

        for line in (
            "generic stdout",
            "diagnostic workers polling",
            '{"kind":"diagnostic","ok":true}',
        ):
            recorder.feed(line, source_generation="current")

        self.assertEqual(recorder.authority_generation, authority_before)
        self.assertFalse(recorder.current_healthy)
        self.assertGreater(recorder.output_generation, authority_before)

    def test_reader_attaches_process_generation_and_old_reader_cannot_roll_back(self):
        class FakeProc:
            def __init__(self, token: str, order: int, text: str) -> None:
                self._wof_authority_generation = token
                self._wof_authority_generation_order = order
                self.stdout = io.StringIO(text)

        recorder = u.RecorderEvidence()
        q: queue.Queue[tuple[str, str]] = queue.Queue()
        u.reader(
            FakeProc("reader-generation-1", 1, ADMISSION_G1 + "\r" + HEARTBEAT + "\r"),
            "RECORDER",
            recorder,
            q,
        )
        self.assertTrue(recorder.current_healthy)
        self.assertEqual(recorder.source_generation, "reader-generation-1")

        u.reader(
            FakeProc("reader-generation-2", 2, ADMISSION_G2 + "\r"),
            "RECORDER",
            recorder,
            q,
        )
        self.assertEqual(recorder.source_generation, "reader-generation-2")
        self.assertTrue(recorder.current_healthy)
        authority_before_old_reader = recorder.authority_generation

        u.reader(
            FakeProc("reader-generation-1", 1, HEARTBEAT + "\r" + FATAL + "\r"),
            "RECORDER",
            recorder,
            q,
        )
        self.assertEqual(recorder.source_generation, "reader-generation-2")
        self.assertEqual(recorder.authority_generation, authority_before_old_reader)
        self.assertTrue(recorder.current_healthy)
        self.assertFalse(recorder.fatal)

    def test_legacy_fresh_qa_replay_vectors_now_fail_closed(self):
        # The old QA fixture has no provenance parameter. Keep only the original
        # single-generation positive path; after rollover, missing provenance is
        # fail-closed so its blocker-directed replay vectors now pass unchanged.
        recorder = u.RecorderEvidence()
        recorder.feed(ADMISSION_G1)
        recorder.feed(FATAL)
        recorder.feed(ADMISSION_G2)
        authority_before = recorder.authority_generation
        self.stale(recorder)
        recorder.feed(HEARTBEAT)
        self.assertEqual(recorder.authority_generation, authority_before)
        self.assertFalse(recorder.current_healthy)

        replay = u.RecorderEvidence()
        replay.feed(ADMISSION_G1)
        replay.feed(FATAL)
        replay.feed(ADMISSION_G1)
        self.assertTrue(replay.fatal)
        self.assertFalse(replay.admitted)


if __name__ == "__main__":
    unittest.main(verbosity=2)

from __future__ import annotations

import io
import sys
import threading
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BUNDLE = ROOT / "parallel" / "LIVE_PROOF_BUNDLE"
sys.path.insert(0, str(BUNDLE))

import unified_live_proof as u  # noqa: E402

ADMISSION_G1 = "+ 房间 qa-atomicity-generation-1 已连接 — World 921031 已确认 / Discovery V2 / 只读模式"
ADMISSION_G2 = "+ 房间 qa-atomicity-generation-2 已连接 — World 921031 已确认 / Discovery V2 / 只读模式"
HEARTBEAT = "Fleet entries 1 | Recorder workers 1 | READ ONLY / RAM writes 0"
FATAL = "WOF-052L 采集器没有正常完成：已安全拒绝采集"


class FakeProc:
    def __init__(self, pid: int) -> None:
        self.pid = pid
        self.stdout = io.StringIO("")


class RecorderInflightAtomicityFreshQA(unittest.TestCase):
    def setUp(self) -> None:
        self._old_base_start = u._BaseStartChild
        self._old_counter = u._child_generation_counter
        self._old_active_ref = u._active_recorder_evidence_ref
        self._next_pid = iter(range(8101, 8160))
        u._child_generation_counter = 0
        u._active_recorder_evidence_ref = None
        u._BaseStartChild = lambda cmd, cwd: FakeProc(next(self._next_pid))

    def tearDown(self) -> None:
        u._BaseStartChild = self._old_base_start
        u._child_generation_counter = self._old_counter
        u._active_recorder_evidence_ref = self._old_active_ref

    def _generation1(self, *, healthy: bool) -> tuple[u.RecorderEvidence, str, int]:
        recorder = u.RecorderEvidence()
        proc = u.start_child(["fake-recorder-generation-1"], Path("."))
        generation = proc._wof_authority_generation
        order = proc._wof_authority_generation_order
        recorder.begin_source_generation(generation, order=order)
        if healthy:
            recorder.feed(ADMISSION_G1, source_generation=generation)
            recorder.feed(HEARTBEAT, source_generation=generation)
            self.assertTrue(recorder.current_healthy)
        return recorder, generation, order

    def _rollover(self, recorder: u.RecorderEvidence, generation1: str, order1: int) -> str:
        proc = u.start_child(["fake-recorder-generation-2"], Path("."))
        generation2 = proc._wof_authority_generation
        self.assertNotEqual(generation2, generation1)
        self.assertGreater(proc._wof_authority_generation_order, order1)
        self.assertEqual(recorder.source_generation, generation2)
        self.assertFalse(recorder.admitted)
        self.assertFalse(recorder.current_fresh)
        self.assertFalse(recorder.current_healthy)
        return generation2

    def _assert_generation2_can_recover(self, recorder: u.RecorderEvidence, generation2: str) -> None:
        recorder.feed(ADMISSION_G2, source_generation=generation2)
        authority_after_admission = recorder.authority_generation
        recorder.feed(HEARTBEAT, source_generation=generation2)
        self.assertEqual(recorder.authority_generation, authority_after_admission + 1)
        self.assertEqual(recorder.admission_source_generation, generation2)
        self.assertTrue(recorder.current_healthy)
        self.assertFalse(recorder.fatal)
        self.assertFalse(recorder.source_revoked)

    def test_old_inflight_heartbeat_cannot_refresh_generation2(self) -> None:
        recorder, generation1, order1 = self._generation1(healthy=True)
        entered = threading.Event()
        release = threading.Event()
        errors: list[BaseException] = []
        original = recorder._advance_authority

        def stalled(kind: str, text: str) -> None:
            if kind == "supervisor-heartbeat":
                entered.set()
                if not release.wait(timeout=5):
                    raise AssertionError("heartbeat synchronization timeout")
            original(kind, text)

        recorder._advance_authority = stalled  # type: ignore[method-assign]

        def old_event() -> None:
            try:
                recorder.feed(HEARTBEAT, source_generation=generation1)
            except BaseException as exc:  # pragma: no cover
                errors.append(exc)

        thread = threading.Thread(target=old_event, name="fresh-qa-old-heartbeat")
        thread.start()
        self.assertTrue(entered.wait(timeout=2))
        authority_before = recorder.authority_generation
        generation2 = self._rollover(recorder, generation1, order1)
        release.set()
        thread.join(timeout=2)
        self.assertFalse(thread.is_alive())
        if errors:
            raise errors[0]

        self.assertEqual(recorder.source_generation, generation2)
        self.assertEqual(recorder.authority_generation, authority_before)
        self.assertFalse(recorder.current_fresh)
        self.assertFalse(recorder.current_healthy)
        self.assertEqual(recorder.last_rejected_authority_reason, "stale-or-wrong-source-generation-at-commit")
        self._assert_generation2_can_recover(recorder, generation2)

    def test_old_inflight_fatal_cannot_revoke_generation2(self) -> None:
        recorder, generation1, order1 = self._generation1(healthy=True)
        entered = threading.Event()
        release = threading.Event()
        errors: list[BaseException] = []
        original = recorder._accept_fatal

        def stalled(text: str) -> None:
            entered.set()
            if not release.wait(timeout=5):
                raise AssertionError("fatal synchronization timeout")
            original(text)

        recorder._accept_fatal = stalled  # type: ignore[method-assign]

        def old_event() -> None:
            try:
                recorder.feed(FATAL, source_generation=generation1)
            except BaseException as exc:  # pragma: no cover
                errors.append(exc)

        thread = threading.Thread(target=old_event, name="fresh-qa-old-fatal")
        thread.start()
        self.assertTrue(entered.wait(timeout=2))
        generation2 = self._rollover(recorder, generation1, order1)
        release.set()
        thread.join(timeout=2)
        self.assertFalse(thread.is_alive())
        if errors:
            raise errors[0]

        self.assertEqual(recorder.source_generation, generation2)
        self.assertFalse(recorder.fatal)
        self.assertFalse(recorder.source_revoked)
        self.assertFalse(recorder.admitted)
        self.assertFalse(recorder.current_fresh)
        self.assertEqual(recorder.last_rejected_authority_reason, "stale-or-wrong-source-generation-at-commit")
        self._assert_generation2_can_recover(recorder, generation2)

    def test_old_inflight_admission_cannot_admit_generation2(self) -> None:
        recorder, generation1, order1 = self._generation1(healthy=False)
        entered = threading.Event()
        release = threading.Event()
        errors: list[BaseException] = []
        original = recorder._accept_admission

        def stalled(text: str, source_generation: str | int | None) -> None:
            entered.set()
            if not release.wait(timeout=5):
                raise AssertionError("admission synchronization timeout")
            original(text, source_generation)

        recorder._accept_admission = stalled  # type: ignore[method-assign]

        def old_event() -> None:
            try:
                recorder.feed(ADMISSION_G1, source_generation=generation1)
            except BaseException as exc:  # pragma: no cover
                errors.append(exc)

        thread = threading.Thread(target=old_event, name="fresh-qa-old-admission")
        thread.start()
        self.assertTrue(entered.wait(timeout=2))
        generation2 = self._rollover(recorder, generation1, order1)
        release.set()
        thread.join(timeout=2)
        self.assertFalse(thread.is_alive())
        if errors:
            raise errors[0]

        self.assertEqual(recorder.source_generation, generation2)
        self.assertFalse(recorder.admitted)
        self.assertIsNone(recorder.admission_source_generation)
        self.assertFalse(recorder.current_fresh)
        self.assertEqual(recorder.last_rejected_authority_reason, "stale-or-wrong-source-generation-at-commit")
        self._assert_generation2_can_recover(recorder, generation2)

    def test_failed_recorder_start_keeps_new_generation_fail_closed(self) -> None:
        recorder, generation1, order1 = self._generation1(healthy=True)
        authority_before = recorder.authority_generation

        def fail_start(cmd, cwd):
            raise OSError("fresh QA synthetic Recorder spawn failure")

        u._BaseStartChild = fail_start
        with self.assertRaises(OSError):
            u.start_child(["fake-recorder-generation-2"], Path("."))

        self.assertNotEqual(recorder.source_generation, generation1)
        self.assertIsNotNone(recorder.source_generation_order)
        self.assertGreater(recorder.source_generation_order, order1)
        self.assertFalse(recorder.admitted)
        self.assertFalse(recorder.current_fresh)
        self.assertFalse(recorder.current_healthy)
        recorder.feed(HEARTBEAT, source_generation=generation1)
        self.assertEqual(recorder.authority_generation, authority_before)
        self.assertFalse(recorder.current_healthy)

    def test_non_recorder_start_does_not_roll_generation(self) -> None:
        recorder, generation1, _ = self._generation1(healthy=True)
        authority_before = recorder.authority_generation
        u.start_child(["python", "launcher.py", "--proof-json", "proof.json"], Path("."))
        self.assertEqual(recorder.source_generation, generation1)
        self.assertEqual(recorder.authority_generation, authority_before)
        self.assertTrue(recorder.current_healthy)


if __name__ == "__main__":
    unittest.main(verbosity=2)

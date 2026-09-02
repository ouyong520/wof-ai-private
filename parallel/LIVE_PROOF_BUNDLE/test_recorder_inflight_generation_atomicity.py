from __future__ import annotations

import io
import threading
import unittest
from pathlib import Path

import unified_live_proof as u

ADMISSION_G1 = "+ 房间 impl-generation-1 已连接 — World 921031 已确认 / Discovery V2 / 只读模式"
ADMISSION_G2 = "+ 房间 impl-generation-2 已连接 — World 921031 已确认 / Discovery V2 / 只读模式"
HEARTBEAT = "Fleet entries 1 | Recorder workers 1 | READ ONLY / RAM writes 0"
FATAL = "WOF-052L 采集器没有正常完成：已安全拒绝采集"


class FakeProc:
    def __init__(self, pid: int) -> None:
        self.pid = pid
        self.stdout = io.StringIO("")


class RecorderInflightGenerationAtomicityTests(unittest.TestCase):
    def setUp(self) -> None:
        self._old_base_start = u._BaseStartChild
        self._old_counter = u._child_generation_counter
        self._old_active_ref = u._active_recorder_evidence_ref
        self._next_pid = iter(range(7101, 7140))
        u._child_generation_counter = 0
        u._active_recorder_evidence_ref = None
        u._BaseStartChild = lambda cmd, cwd: FakeProc(next(self._next_pid))

    def tearDown(self) -> None:
        u._BaseStartChild = self._old_base_start
        u._child_generation_counter = self._old_counter
        u._active_recorder_evidence_ref = self._old_active_ref

    def healthy_generation1(self) -> tuple[u.RecorderEvidence, str, int]:
        recorder = u.RecorderEvidence()
        proc1 = u.start_child(["fake-recorder-generation-1"], Path("."))
        gen1 = proc1._wof_authority_generation
        order1 = proc1._wof_authority_generation_order
        recorder.begin_source_generation(gen1, order=order1)
        recorder.feed(ADMISSION_G1, source_generation=gen1)
        recorder.feed(HEARTBEAT, source_generation=gen1)
        self.assertTrue(recorder.current_healthy)
        return recorder, gen1, order1

    def rollover_generation2(
        self,
        recorder: u.RecorderEvidence,
        gen1: str,
        order1: int,
    ) -> str:
        proc2 = u.start_child(["fake-recorder-generation-2"], Path("."))
        gen2 = proc2._wof_authority_generation
        self.assertNotEqual(gen2, gen1)
        self.assertGreater(proc2._wof_authority_generation_order, order1)
        self.assertEqual(recorder.source_generation, gen2)
        self.assertFalse(recorder.admitted)
        self.assertFalse(recorder.current_fresh)
        self.assertFalse(recorder.current_healthy)
        return gen2

    def test_inflight_old_heartbeat_cannot_refresh_new_generation(self) -> None:
        recorder, gen1, order1 = self.healthy_generation1()
        entered = threading.Event()
        release = threading.Event()
        errors: list[BaseException] = []
        original_advance = recorder._advance_authority

        def stalled_advance(kind: str, text: str) -> None:
            if kind == "supervisor-heartbeat":
                entered.set()
                if not release.wait(timeout=5):
                    raise AssertionError("heartbeat mutation synchronization timeout")
            original_advance(kind, text)

        recorder._advance_authority = stalled_advance  # type: ignore[method-assign]

        def old_event() -> None:
            try:
                recorder.feed(HEARTBEAT, source_generation=gen1)
            except BaseException as exc:  # pragma: no cover - propagated below
                errors.append(exc)

        thread = threading.Thread(target=old_event, name="impl-old-heartbeat")
        thread.start()
        self.assertTrue(entered.wait(timeout=2))
        authority_before = recorder.authority_generation

        gen2 = self.rollover_generation2(recorder, gen1, order1)
        release.set()
        thread.join(timeout=2)
        self.assertFalse(thread.is_alive())
        if errors:
            raise errors[0]

        self.assertEqual(recorder.source_generation, gen2)
        self.assertEqual(recorder.authority_generation, authority_before)
        self.assertFalse(recorder.current_fresh)
        self.assertFalse(recorder.current_healthy)

        recorder.feed(ADMISSION_G2, source_generation=gen2)
        authority_after_admission = recorder.authority_generation
        recorder.feed(HEARTBEAT, source_generation=gen2)
        self.assertEqual(recorder.authority_generation, authority_after_admission + 1)
        self.assertTrue(recorder.current_healthy)

    def test_inflight_old_fatal_cannot_revoke_new_generation(self) -> None:
        recorder, gen1, order1 = self.healthy_generation1()
        entered = threading.Event()
        release = threading.Event()
        errors: list[BaseException] = []
        original_accept_fatal = recorder._accept_fatal

        def stalled_accept_fatal(text: str) -> None:
            entered.set()
            if not release.wait(timeout=5):
                raise AssertionError("fatal mutation synchronization timeout")
            original_accept_fatal(text)

        recorder._accept_fatal = stalled_accept_fatal  # type: ignore[method-assign]

        def old_event() -> None:
            try:
                recorder.feed(FATAL, source_generation=gen1)
            except BaseException as exc:  # pragma: no cover - propagated below
                errors.append(exc)

        thread = threading.Thread(target=old_event, name="impl-old-fatal")
        thread.start()
        self.assertTrue(entered.wait(timeout=2))

        gen2 = self.rollover_generation2(recorder, gen1, order1)
        release.set()
        thread.join(timeout=2)
        self.assertFalse(thread.is_alive())
        if errors:
            raise errors[0]

        self.assertEqual(recorder.source_generation, gen2)
        self.assertFalse(recorder.fatal)
        self.assertFalse(recorder.source_revoked)
        self.assertFalse(recorder.admitted)
        self.assertFalse(recorder.current_fresh)

        recorder.feed(ADMISSION_G2, source_generation=gen2)
        recorder.feed(HEARTBEAT, source_generation=gen2)
        self.assertTrue(recorder.current_healthy)
        self.assertFalse(recorder.fatal)

    def test_inflight_old_admission_cannot_mark_new_generation_admitted(self) -> None:
        recorder, gen1, order1 = self.healthy_generation1()
        entered = threading.Event()
        release = threading.Event()
        errors: list[BaseException] = []
        original_accept_admission = recorder._accept_admission

        def stalled_accept_admission(text: str, source_generation: str | int | None) -> None:
            entered.set()
            if not release.wait(timeout=5):
                raise AssertionError("admission mutation synchronization timeout")
            original_accept_admission(text, source_generation)

        recorder._accept_admission = stalled_accept_admission  # type: ignore[method-assign]

        def old_event() -> None:
            try:
                recorder.feed(ADMISSION_G1, source_generation=gen1)
            except BaseException as exc:  # pragma: no cover - propagated below
                errors.append(exc)

        # Use a fresh same-generation evidence object so the old admission gets
        # through the initial duplicate-admission gate before it is stalled.
        recorder.begin_source_generation("generation-1-rebind", order=order1 + 1)
        gen1_rebind = recorder.source_generation
        self.assertIsInstance(gen1_rebind, str)

        thread = threading.Thread(
            target=lambda: recorder.feed(ADMISSION_G1, source_generation=gen1_rebind),
            name="impl-old-admission",
        )
        thread.start()
        self.assertTrue(entered.wait(timeout=2))

        proc2 = u.start_child(["fake-recorder-generation-2"], Path("."))
        gen2 = proc2._wof_authority_generation
        self.assertEqual(recorder.source_generation, gen2)
        self.assertFalse(recorder.admitted)
        release.set()
        thread.join(timeout=2)
        self.assertFalse(thread.is_alive())
        if errors:
            raise errors[0]

        self.assertFalse(recorder.admitted)
        self.assertIsNone(recorder.admission_source_generation)
        recorder.feed(ADMISSION_G2, source_generation=gen2)
        self.assertTrue(recorder.admitted)
        self.assertEqual(recorder.admission_source_generation, gen2)


if __name__ == "__main__":
    unittest.main(verbosity=2)

from __future__ import annotations

import io
import queue
import sys
import threading
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BUNDLE = ROOT / "parallel" / "LIVE_PROOF_BUNDLE"
sys.path.insert(0, str(BUNDLE))

import unified_live_proof as u  # noqa: E402

ADMISSION_G1 = "+ 房间 qa-generation-1 已连接 — World 921031 已确认 / Discovery V2 / 只读模式"
HEARTBEAT = "Fleet entries 1 | Recorder workers 1 | READ ONLY / RAM writes 0"
FATAL = "WOF-052L 采集器没有正常完成：已安全拒绝采集"


class FakeProc:
    def __init__(self, pid: int, text: str = "") -> None:
        self.pid = pid
        self.stdout = io.StringIO(text)


class RecorderGenerationInflightRaceQA(unittest.TestCase):
    def setUp(self) -> None:
        self._old_base_start = u._BaseStartChild
        self._old_counter = u._child_generation_counter
        self._old_active_ref = u._active_recorder_evidence_ref
        self._next_pid = iter(range(6101, 6120))
        u._child_generation_counter = 0
        u._active_recorder_evidence_ref = None
        u._BaseStartChild = lambda cmd, cwd: FakeProc(next(self._next_pid))

    def tearDown(self) -> None:
        u._BaseStartChild = self._old_base_start
        u._child_generation_counter = self._old_counter
        u._active_recorder_evidence_ref = self._old_active_ref

    def healthy_generation1(self) -> tuple[u.RecorderEvidence, str, int]:
        rec = u.RecorderEvidence()
        proc1 = u.start_child(["fake-recorder-generation-1"], Path("."))
        gen1 = proc1._wof_authority_generation
        order1 = proc1._wof_authority_generation_order
        rec.begin_source_generation(gen1, order=order1)
        rec.feed(ADMISSION_G1, source_generation=gen1)
        rec.feed(HEARTBEAT, source_generation=gen1)
        self.assertTrue(rec.current_healthy)
        return rec, gen1, order1

    def start_generation2(self, rec: u.RecorderEvidence, gen1: str, order1: int) -> tuple[str, int]:
        proc2 = u.start_child(["fake-recorder-generation-2"], Path("."))
        gen2 = proc2._wof_authority_generation
        order2 = proc2._wof_authority_generation_order
        self.assertNotEqual(gen2, gen1)
        self.assertGreater(order2, order1)
        self.assertEqual(rec.source_generation, gen2)
        self.assertFalse(rec.admitted)
        self.assertFalse(rec.current_fresh)
        self.assertFalse(rec.current_healthy)
        return gen2, order2

    def test_inflight_generation1_fatal_cannot_revoke_generation2_after_child_start(self) -> None:
        rec, gen1, order1 = self.healthy_generation1()
        entered_mutation = threading.Event()
        release_mutation = threading.Event()
        original_accept_fatal = rec._accept_fatal
        thread_errors: list[BaseException] = []

        def stalled_accept_fatal(text: str) -> None:
            entered_mutation.set()
            if not release_mutation.wait(timeout=5):
                raise AssertionError("QA synchronization timeout before fatal mutation")
            original_accept_fatal(text)

        rec._accept_fatal = stalled_accept_fatal  # type: ignore[method-assign]

        def old_reader_event() -> None:
            try:
                rec.feed(FATAL, source_generation=gen1)
            except BaseException as exc:  # pragma: no cover - propagated below
                thread_errors.append(exc)

        t = threading.Thread(target=old_reader_event, name="qa-old-generation-fatal")
        t.start()
        self.assertTrue(
            entered_mutation.wait(timeout=2),
            "old generation fatal never reached the post-generation-check mutation boundary",
        )

        gen2, _ = self.start_generation2(rec, gen1, order1)
        release_mutation.set()
        t.join(timeout=2)
        self.assertFalse(t.is_alive(), "old generation fatal thread did not finish")
        if thread_errors:
            raise thread_errors[0]

        self.assertEqual(rec.source_generation, gen2)
        self.assertFalse(
            rec.fatal,
            "generation-1 fatal that was already in-flight before rollover mutated generation-2 state",
        )
        self.assertFalse(
            rec.source_revoked,
            "generation-1 fatal that resumed after child-start revoked generation-2 authority",
        )
        self.assertFalse(rec.admitted)
        self.assertFalse(rec.current_fresh)
        self.assertFalse(rec.current_healthy)

    def test_inflight_generation1_heartbeat_cannot_renew_generation2_after_child_start(self) -> None:
        rec, gen1, order1 = self.healthy_generation1()
        entered_mutation = threading.Event()
        release_mutation = threading.Event()
        original_advance = rec._advance_authority
        thread_errors: list[BaseException] = []

        def stalled_advance(kind: str, text: str) -> None:
            if kind == "supervisor-heartbeat":
                entered_mutation.set()
                if not release_mutation.wait(timeout=5):
                    raise AssertionError("QA synchronization timeout before heartbeat mutation")
            original_advance(kind, text)

        rec._advance_authority = stalled_advance  # type: ignore[method-assign]

        def old_reader_event() -> None:
            try:
                rec.feed(HEARTBEAT, source_generation=gen1)
            except BaseException as exc:  # pragma: no cover - propagated below
                thread_errors.append(exc)

        t = threading.Thread(target=old_reader_event, name="qa-old-generation-heartbeat")
        t.start()
        self.assertTrue(
            entered_mutation.wait(timeout=2),
            "old generation heartbeat never reached the post-generation-check mutation boundary",
        )
        authority_before_rollover = rec.authority_generation

        gen2, _ = self.start_generation2(rec, gen1, order1)
        release_mutation.set()
        t.join(timeout=2)
        self.assertFalse(t.is_alive(), "old generation heartbeat thread did not finish")
        if thread_errors:
            raise thread_errors[0]

        self.assertEqual(rec.source_generation, gen2)
        self.assertEqual(
            rec.authority_generation,
            authority_before_rollover,
            "generation-1 heartbeat that was already in-flight advanced generation-2 authorityGeneration",
        )
        self.assertFalse(
            rec.current_fresh,
            "generation-1 heartbeat that resumed after child-start renewed generation-2 freshness",
        )
        self.assertFalse(rec.admitted)
        self.assertFalse(rec.current_healthy)


if __name__ == "__main__":
    unittest.main(verbosity=2)

from __future__ import annotations

import io
import queue
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BUNDLE = ROOT / "parallel" / "LIVE_PROOF_BUNDLE"
sys.path.insert(0, str(BUNDLE))

import unified_live_proof as u  # noqa: E402

ADMISSION = "+ 房间 qa-generation-1 已连接 — World 921031 已确认 / Discovery V2 / 只读模式"
HEARTBEAT = "Fleet entries 1 | Recorder workers 1 | READ ONLY / RAM writes 0"


class FakeProc:
    def __init__(self, pid: int, text: str = "") -> None:
        self.pid = pid
        self.stdout = io.StringIO(text)


class RecorderAuthorityGenerationFreshQA(unittest.TestCase):
    def setUp(self) -> None:
        self._old_base_start = u._BaseStartChild
        self._old_counter = u._child_generation_counter
        self._next_pid = iter((4101, 4102, 4103))
        u._child_generation_counter = 0
        u._BaseStartChild = lambda cmd, cwd: FakeProc(next(self._next_pid))

    def tearDown(self) -> None:
        u._BaseStartChild = self._old_base_start
        u._child_generation_counter = self._old_counter

    def test_new_child_start_immediately_revokes_prior_generation_before_new_reader(self) -> None:
        """Required safety boundary: child generation rollover, not first new stdout/read."""
        rec = u.RecorderEvidence()

        proc1 = u.start_child(["fake-recorder-1"], Path("."))
        gen1 = proc1._wof_authority_generation
        order1 = proc1._wof_authority_generation_order
        rec.begin_source_generation(gen1, order=order1)
        rec.feed(ADMISSION, source_generation=gen1)
        rec.feed(HEARTBEAT, source_generation=gen1)
        self.assertTrue(rec.current_healthy)

        authority_before_rollover = rec.authority_generation

        # Exact adversarial boundary from the real orchestration shape:
        # start_child() has returned a newer Recorder child, but its new reader
        # thread has not entered reader()/begin_source_generation() yet.
        proc2 = u.start_child(["fake-recorder-2"], Path("."))
        gen2 = proc2._wof_authority_generation
        self.assertNotEqual(gen2, gen1)
        self.assertGreater(proc2._wof_authority_generation_order, order1)

        # PASS requirement: generation-1 authority/freshness must already be
        # invalid at this point. Current implementation leaves generation 1
        # current until the generation-2 reader starts.
        self.assertFalse(
            rec.current_healthy,
            "generation-2 child start did not immediately revoke generation-1 authority",
        )
        self.assertEqual(
            rec.source_generation,
            gen2,
            "Recorder source generation did not advance at child-start boundary",
        )

        # A delayed old-reader heartbeat in this window must be diagnostic only.
        rec.feed(HEARTBEAT, source_generation=gen1)
        self.assertEqual(
            rec.authority_generation,
            authority_before_rollover,
            "generation-1 heartbeat renewed authority after generation-2 child start",
        )
        self.assertFalse(rec.current_healthy)

    def test_reader_binding_eventually_revokes_but_is_too_late_for_start_boundary(self) -> None:
        """Control: proves revocation is deferred to reader entry rather than child start."""
        rec = u.RecorderEvidence()
        q: queue.Queue[tuple[str, str]] = queue.Queue()

        proc1 = u.start_child(["fake-recorder-1"], Path("."))
        gen1 = proc1._wof_authority_generation
        rec.begin_source_generation(gen1, order=proc1._wof_authority_generation_order)
        rec.feed(ADMISSION, source_generation=gen1)
        self.assertTrue(rec.current_healthy)

        proc2 = u.start_child(["fake-recorder-2"], Path("."))
        gen2 = proc2._wof_authority_generation
        self.assertEqual(rec.source_generation, gen1)
        self.assertTrue(rec.current_healthy)

        u.reader(proc2, "RECORDER", rec, q)
        self.assertEqual(rec.source_generation, gen2)
        self.assertFalse(rec.admitted)
        self.assertFalse(rec.current_fresh)
        self.assertFalse(rec.current_healthy)


if __name__ == "__main__":
    unittest.main(verbosity=2)

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from executor import (
    AckTimeout,
    AdapterRejected,
    CancelToken,
    CommandPlan,
    CommandStep,
    DeadlineExceeded,
    DeterministicExecutor,
    PreconditionsFailed,
    ScriptedSyntheticAdapter,
    StepTimeout,
    TriggerContext,
    TriggerRejected,
)


class ExecutorTests(unittest.TestCase):
    def trigger(self):
        return TriggerContext(True, "test", "req-001")

    def test_deterministic_press_hold_release_and_ack(self):
        adapter = ScriptedSyntheticAdapter(
            preconditions={"window-focused": True},
            acks={"step-visible": True},
            ack_latency_ms={"step-visible": 7},
        )
        plan = CommandPlan(
            "fixture-plan",
            (
                CommandStep("press", "SYM_A", preconditions=("window-focused",)),
                CommandStep("hold", "SYM_B", hold_ms=25, ack="step-visible", timeout_ms=50),
                CommandStep("release", "SYM_A"),
            ),
            deadline_ms=200,
        )
        result = DeterministicExecutor(adapter, dry_run=False).execute(plan, self.trigger())
        self.assertEqual("COMPLETED", result.status)
        self.assertEqual(
            [(0, "press", "SYM_A"), (0, "press", "SYM_B"), (25, "release", "SYM_B"), (32, "release", "SYM_A")],
            adapter.emitted,
        )
        adapter2 = ScriptedSyntheticAdapter(
            preconditions={"window-focused": True},
            acks={"step-visible": True},
            ack_latency_ms={"step-visible": 7},
        )
        self.assertEqual(
            result.trace_dicts(),
            DeterministicExecutor(adapter2, dry_run=False).execute(plan, self.trigger()).trace_dicts(),
        )

    def test_dry_run_has_trace_but_no_adapter_emission(self):
        adapter = ScriptedSyntheticAdapter()
        plan = CommandPlan("p", (CommandStep("press", "SYM"), CommandStep("release", "SYM")), 100)
        result = DeterministicExecutor(adapter, dry_run=True).execute(plan, self.trigger())
        self.assertEqual([], adapter.emitted)
        events = [event["event"] for event in result.trace_dicts()]
        self.assertIn("dry_run_emit", events)

    def test_non_user_trigger_rejected(self):
        executor = DeterministicExecutor(ScriptedSyntheticAdapter())
        plan = CommandPlan("p", (CommandStep("press", "SYM"),), 100)
        with self.assertRaises(TriggerRejected):
            executor.execute(plan, TriggerContext(False, "test", "req"))

    def test_unknown_trigger_source_rejected(self):
        executor = DeterministicExecutor(ScriptedSyntheticAdapter())
        plan = CommandPlan("p", (CommandStep("press", "SYM"),), 100)
        with self.assertRaises(TriggerRejected):
            executor.execute(plan, TriggerContext(True, "timer", "req"))

    def test_live_adapter_rejected(self):
        class LiveLookingAdapter(ScriptedSyntheticAdapter):
            synthetic_only = False

        with self.assertRaises(AdapterRejected):
            DeterministicExecutor(LiveLookingAdapter())

    def test_precondition_failure_is_fail_closed(self):
        adapter = ScriptedSyntheticAdapter(preconditions={"ready": False})
        plan = CommandPlan("p", (CommandStep("press", "SYM", preconditions=("ready",)),), 100)
        with self.assertRaises(PreconditionsFailed):
            DeterministicExecutor(adapter, dry_run=False).execute(plan, self.trigger())
        self.assertEqual([], adapter.emitted)

    def test_ack_timeout_safety_releases_pressed_symbol(self):
        adapter = ScriptedSyntheticAdapter(acks={"seen": False}, ack_latency_ms={"seen": 10})
        plan = CommandPlan("p", (CommandStep("press", "SYM", ack="seen", timeout_ms=10),), 100)
        with self.assertRaises(AckTimeout):
            DeterministicExecutor(adapter, dry_run=False).execute(plan, self.trigger())
        self.assertEqual([(0, "press", "SYM"), (10, "release", "SYM")], adapter.emitted)

    def test_deadline_exceeded_after_hold_safety_releases(self):
        adapter = ScriptedSyntheticAdapter()
        plan = CommandPlan("p", (CommandStep("hold", "SYM", hold_ms=101, timeout_ms=200),), 100)
        with self.assertRaises(DeadlineExceeded):
            DeterministicExecutor(adapter, dry_run=False).execute(plan, self.trigger())
        self.assertEqual([(0, "press", "SYM"), (101, "release", "SYM")], adapter.emitted)

    def test_step_timeout(self):
        adapter = ScriptedSyntheticAdapter()
        plan = CommandPlan("p", (CommandStep("hold", "SYM", hold_ms=11, timeout_ms=10),), 100)
        with self.assertRaises(StepTimeout):
            DeterministicExecutor(adapter, dry_run=False).execute(plan, self.trigger())
        self.assertEqual([(0, "press", "SYM"), (11, "release", "SYM")], adapter.emitted)

    def test_cancelled_before_first_step(self):
        adapter = ScriptedSyntheticAdapter()
        plan = CommandPlan("p", (CommandStep("press", "SYM"),), 100)
        token = CancelToken(cancelled=True, reason="user released hotkey")
        with self.assertRaises(Exception) as ctx:
            DeterministicExecutor(adapter, dry_run=False).execute(plan, self.trigger(), token)
        self.assertIn("user released hotkey", str(ctx.exception))
        self.assertEqual([], adapter.emitted)


if __name__ == "__main__":
    unittest.main()

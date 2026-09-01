"""Deterministic, synthetic-only input execution contract for WOF Assist.

This prototype intentionally cannot inject real game input. It operates only on
SyntheticAdapter implementations and requires an explicit user trigger boundary.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Optional, Protocol, Tuple


class ExecutionError(RuntimeError):
    """Base class for fail-closed execution failures."""


class TriggerRejected(ExecutionError):
    pass


class AdapterRejected(ExecutionError):
    pass


class PreconditionsFailed(ExecutionError):
    pass


class DeadlineExceeded(ExecutionError):
    pass


class AckTimeout(ExecutionError):
    pass


class StepTimeout(ExecutionError):
    pass


class Cancelled(ExecutionError):
    pass


@dataclass(frozen=True)
class TriggerContext:
    user_triggered: bool
    source: str
    request_id: str


@dataclass(frozen=True)
class CommandStep:
    op: str
    symbol: str
    hold_ms: int = 0
    timeout_ms: int = 1000
    preconditions: Tuple[str, ...] = ()
    ack: Optional[str] = None

    @staticmethod
    def from_mapping(raw: Mapping[str, Any]) -> "CommandStep":
        return CommandStep(
            op=str(raw["op"]),
            symbol=str(raw["symbol"]),
            hold_ms=int(raw.get("holdMs", 0)),
            timeout_ms=int(raw.get("timeoutMs", 1000)),
            preconditions=tuple(str(x) for x in raw.get("preconditions", ())),
            ack=(None if raw.get("ack") is None else str(raw["ack"])),
        )

    def validate(self) -> None:
        if self.op not in {"press", "release", "hold"}:
            raise ExecutionError(f"unsupported op: {self.op}")
        if not self.symbol or self.symbol.strip() != self.symbol:
            raise ExecutionError("symbol must be a non-empty canonical token")
        if self.hold_ms < 0:
            raise ExecutionError("hold_ms must be >= 0")
        if self.timeout_ms <= 0:
            raise ExecutionError("timeout_ms must be > 0")
        if self.op == "hold" and self.hold_ms <= 0:
            raise ExecutionError("hold requires hold_ms > 0")
        if self.op != "hold" and self.hold_ms != 0:
            raise ExecutionError("hold_ms is only valid for hold")


@dataclass(frozen=True)
class CommandPlan:
    plan_id: str
    steps: Tuple[CommandStep, ...]
    deadline_ms: int

    @staticmethod
    def from_mapping(raw: Mapping[str, Any]) -> "CommandPlan":
        steps = tuple(CommandStep.from_mapping(x) for x in raw["steps"])
        return CommandPlan(
            plan_id=str(raw["planId"]),
            steps=steps,
            deadline_ms=int(raw.get("deadlineMs", 5000)),
        )

    def validate(self) -> None:
        if not self.plan_id:
            raise ExecutionError("plan_id is required")
        if not self.steps:
            raise ExecutionError("at least one step is required")
        if self.deadline_ms <= 0:
            raise ExecutionError("deadline_ms must be > 0")
        for step in self.steps:
            step.validate()


@dataclass
class CancelToken:
    cancelled: bool = False
    reason: str = "cancelled"


@dataclass(frozen=True)
class TraceEvent:
    seq: int
    t_ms: int
    event: str
    data: Mapping[str, Any] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, Any]:
        return {
            "seq": self.seq,
            "tMs": self.t_ms,
            "event": self.event,
            "data": dict(sorted(self.data.items())),
        }


@dataclass(frozen=True)
class ExecutionResult:
    status: str
    plan_id: str
    trace: Tuple[TraceEvent, ...]

    def trace_dicts(self) -> List[Dict[str, Any]]:
        return [event.as_dict() for event in self.trace]


class SyntheticAdapter(Protocol):
    """Adapter boundary. Implementations must be synthetic/offline only."""

    synthetic_only: bool

    def now_ms(self) -> int:
        ...

    def advance_ms(self, delta_ms: int) -> None:
        ...

    def check_precondition(self, name: str) -> bool:
        ...

    def emit(self, op: str, symbol: str) -> None:
        ...

    def ack(self, signal: str, timeout_ms: int) -> bool:
        ...


class DeterministicExecutor:
    ALLOWED_TRIGGER_SOURCES = frozenset({"hotkey", "explicit-ui", "test"})

    def __init__(self, adapter: SyntheticAdapter, *, dry_run: bool = True):
        if not getattr(adapter, "synthetic_only", False):
            raise AdapterRejected("live/non-synthetic adapters are forbidden in this stage")
        self._adapter = adapter
        self._dry_run = bool(dry_run)
        self._trace: List[TraceEvent] = []
        self._seq = 0
        self._start_ms = 0

    def _record(self, event: str, **data: Any) -> None:
        self._seq += 1
        self._trace.append(
            TraceEvent(
                seq=self._seq,
                t_ms=self._adapter.now_ms() - self._start_ms,
                event=event,
                data=data,
            )
        )

    def _check_cancel(self, token: CancelToken) -> None:
        if token.cancelled:
            self._record("cancelled", reason=token.reason)
            raise Cancelled(token.reason)

    def _check_deadline(self, plan: CommandPlan) -> None:
        elapsed = self._adapter.now_ms() - self._start_ms
        if elapsed > plan.deadline_ms:
            self._record("deadline_exceeded", elapsedMs=elapsed, deadlineMs=plan.deadline_ms)
            raise DeadlineExceeded(f"deadline exceeded: {elapsed}>{plan.deadline_ms}")

    def _check_step_timeout(self, step: CommandStep, step_started_ms: int) -> None:
        elapsed = self._adapter.now_ms() - step_started_ms
        if elapsed > step.timeout_ms:
            self._record("step_timeout", elapsedMs=elapsed, timeoutMs=step.timeout_ms)
            raise StepTimeout(f"step timeout: {elapsed}>{step.timeout_ms}")

    def _emit(self, index: int, op: str, symbol: str, pressed: set[str]) -> None:
        if self._dry_run:
            self._record("dry_run_emit", index=index, op=op, symbol=symbol)
        else:
            self._adapter.emit(op, symbol)
            self._record("emit", index=index, op=op, symbol=symbol)
        if op == "press":
            pressed.add(symbol)
        elif op == "release":
            pressed.discard(symbol)

    def _safety_release_all(self, pressed: set[str]) -> None:
        for symbol in sorted(pressed):
            if self._dry_run:
                self._record("dry_run_safety_release", symbol=symbol)
            else:
                self._adapter.emit("release", symbol)
                self._record("safety_release", symbol=symbol)
        pressed.clear()

    def execute(
        self,
        plan: CommandPlan,
        trigger: TriggerContext,
        cancel: Optional[CancelToken] = None,
    ) -> ExecutionResult:
        plan.validate()
        cancel = cancel or CancelToken()

        if not trigger.user_triggered or trigger.source not in self.ALLOWED_TRIGGER_SOURCES:
            raise TriggerRejected("execution requires an explicit user-triggered hotkey/UI boundary")
        if not trigger.request_id:
            raise TriggerRejected("request_id is required for auditability")

        self._trace = []
        self._seq = 0
        self._start_ms = self._adapter.now_ms()
        self._record(
            "execution_started",
            planId=plan.plan_id,
            requestId=trigger.request_id,
            triggerSource=trigger.source,
            dryRun=self._dry_run,
        )

        pressed: set[str] = set()
        try:
            for index, step in enumerate(plan.steps):
                self._check_cancel(cancel)
                self._check_deadline(plan)
                self._record("step_started", index=index, op=step.op, symbol=step.symbol)
                step_started_ms = self._adapter.now_ms()

                for condition in step.preconditions:
                    ok = bool(self._adapter.check_precondition(condition))
                    self._record("precondition", index=index, name=condition, ok=ok)
                    if not ok:
                        raise PreconditionsFailed(f"precondition failed: {condition}")

                if step.op == "hold":
                    self._emit(index, "press", step.symbol, pressed)
                    self._adapter.advance_ms(step.hold_ms)
                    self._check_cancel(cancel)
                    self._check_deadline(plan)
                    self._check_step_timeout(step, step_started_ms)
                    self._emit(index, "release", step.symbol, pressed)
                else:
                    self._emit(index, step.op, step.symbol, pressed)

                if step.ack is not None:
                    ok = bool(self._adapter.ack(step.ack, step.timeout_ms))
                    self._record("ack", index=index, signal=step.ack, ok=ok, timeoutMs=step.timeout_ms)
                    if not ok:
                        raise AckTimeout(f"ack timeout: {step.ack}")
                    self._check_deadline(plan)
                    self._check_step_timeout(step, step_started_ms)

                self._check_step_timeout(step, step_started_ms)
                self._record("step_completed", index=index)

            self._record("execution_completed", planId=plan.plan_id)
            return ExecutionResult("COMPLETED", plan.plan_id, tuple(self._trace))
        except ExecutionError as exc:
            self._safety_release_all(pressed)
            self._record("execution_failed", error=type(exc).__name__, message=str(exc))
            raise


class ScriptedSyntheticAdapter:
    """Deterministic fixture adapter with a virtual clock and scripted ACK results."""

    synthetic_only = True

    def __init__(
        self,
        *,
        preconditions: Optional[Mapping[str, bool]] = None,
        acks: Optional[Mapping[str, bool]] = None,
        ack_latency_ms: Optional[Mapping[str, int]] = None,
    ) -> None:
        self._t_ms = 0
        self.preconditions = dict(preconditions or {})
        self.acks = dict(acks or {})
        self.ack_latency_ms = dict(ack_latency_ms or {})
        self.emitted: List[Tuple[int, str, str]] = []

    def now_ms(self) -> int:
        return self._t_ms

    def advance_ms(self, delta_ms: int) -> None:
        if delta_ms < 0:
            raise ValueError("virtual clock cannot move backwards")
        self._t_ms += delta_ms

    def check_precondition(self, name: str) -> bool:
        return bool(self.preconditions.get(name, False))

    def emit(self, op: str, symbol: str) -> None:
        self.emitted.append((self._t_ms, op, symbol))

    def ack(self, signal: str, timeout_ms: int) -> bool:
        latency = int(self.ack_latency_ms.get(signal, 0))
        self.advance_ms(min(latency, timeout_ms))
        return bool(self.acks.get(signal, False) and latency <= timeout_ms)

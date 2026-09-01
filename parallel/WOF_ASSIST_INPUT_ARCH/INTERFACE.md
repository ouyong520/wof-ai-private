# Input Execution Interface Contract

## 1. Scope

This contract is intentionally narrower than a real input injector. It translates a symbolic command plan into deterministic calls against a **synthetic adapter** only. A later stage may bind the same conceptual interface to Browser/emulator adapters only after live evidence and explicit authorization exist.

No field in this contract should be interpreted as proven game-specific movement timing.

## 2. Consumer contract for reverse-lane command model

A future `parallel/WOF_ASSIST_MOVE_REVERSE/command_model.json` can be consumed only after it is normalized to `command_plan.schema.json`:

- `planId`: stable identifier for one user-invoked move plan.
- `deadlineMs`: total execution budget.
- `steps[]`: ordered symbolic steps.
- `steps[].op`: `press`, `release`, or `hold`.
- `steps[].symbol`: opaque symbolic command token. The executor does not infer keyboard/controller bindings.
- `steps[].holdMs`: required only for `hold`; absent/zero otherwise.
- `steps[].timeoutMs`: per-step budget.
- `steps[].preconditions[]`: adapter-owned boolean checks.
- `steps[].ack`: optional adapter-owned completion/acknowledgement signal.

The reverse lane remains authoritative for command semantics. This lane must not invent missing command timing, aliases, ordering, or game-specific bindings.

## 3. User-trigger boundary

Every execution request must include:

```text
TriggerContext(user_triggered=True, source=<hotkey|explicit-ui|test>, request_id=<non-empty>)
```

Unknown sources (for example `timer`, `agent`, `observer`) are rejected. This is the architecture-level boundary that prevents autonomous triggering.

A future UI may map a hotkey or explicit click to this context, but the input executor itself does not register hotkeys, poll state, schedule actions, or decide when a move should happen.

## 4. Adapter abstraction

The executor depends on the following conceptual interface:

```text
synthetic_only: bool
now_ms() -> int
advance_ms(delta_ms)
check_precondition(name) -> bool
emit(op, symbol)
ack(signal, timeout_ms) -> bool
```

`ScriptedSyntheticAdapter` implements this with a virtual clock and scripted responses.

Future adapter families may include:

- `BrowserAssistAdapter`: maps opaque symbols to an explicitly configured browser automation/input bridge.
- `EmulatorAssistAdapter`: maps opaque symbols to an explicitly configured emulator bridge.

Those adapters are **not implemented here**. A live adapter must not claim `synthetic_only=true`; therefore this prototype rejects it by construction.

## 5. Timing and deadlines

Two independent limits exist:

- `deadlineMs`: whole-plan limit measured against the adapter clock.
- `timeoutMs`: per-step limit; also bounds an optional ACK wait.

The prototype uses a virtual synthetic clock, making traces and tests deterministic. Real wall-clock scheduling, OS event timing, and latency compensation are deliberately out of scope.

Fixture timings are synthetic examples only and are not evidence of correct game movement timing.

## 6. Cancellation

A `CancelToken` may be passed by the user-facing caller. Cancellation is checked before each step and after a synthetic hold wait. On cancellation, execution fails closed.

If the executor has a logically pressed symbol when a failure occurs, it attempts deterministic safety release through the synthetic adapter before returning the error path.

A future live adapter would require separate proof that release/cleanup semantics are safe; this stage does not provide that proof.

## 7. Preconditions

Preconditions are opaque names evaluated by the adapter. Examples in tests such as `window-focused` are generic and non-game-specific.

If any required precondition is false, no step emission occurs for that step and execution stops.

## 8. Completion / ACK hooks

A step can name an optional `ack` signal. The adapter owns the meaning of that signal. The executor only requests the signal within `timeoutMs` and records success/failure.

No visual detector, game-state detector, or live completion signal is implemented in this lane.

## 9. Dry-run mode

`dry_run=True` is the default. In this mode:

- the plan is validated;
- trigger/precondition/timeout/deadline rules still apply;
- `dry_run_emit` trace events are produced;
- adapter `emit()` is never called.

This permits consumer integration testing without any input side effect, even on a synthetic adapter.

## 10. Deterministic trace

Trace records are ordered and contain:

```json
{
  "seq": 1,
  "tMs": 0,
  "event": "execution_started",
  "data": {"...": "sorted keys"}
}
```

The adapter clock is the only time source. With the same plan and scripted adapter responses, trace output is identical.

Representative events include:

- `execution_started`
- `step_started`
- `precondition`
- `emit` / `dry_run_emit`
- `ack`
- `step_completed`
- `safety_release` / `dry_run_safety_release`
- `cancelled`
- `step_timeout`
- `deadline_exceeded`
- `execution_failed`
- `execution_completed`

## 11. Fail-closed rules

The executor rejects or stops on:

- non-user or unknown trigger source;
- missing request ID;
- non-synthetic adapter;
- invalid command op or timing field;
- false precondition;
- cancellation;
- step timeout;
- plan deadline;
- missing/failed ACK.

There is no best-effort continuation after an error.

## 12. Park condition

Further implementation is blocked by design if it requires either:

1. actual game input injection, or
2. live-only evidence for command semantics/timing/ACK behavior.

Those belong to later explicitly authorized lanes.

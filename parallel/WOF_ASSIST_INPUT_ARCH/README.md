# WOF Assist Input Execution Architecture

Stage: `WOF_ASSIST_INPUT_EXECUTION_ARCH_V1`

This lane defines an **adapter-neutral, user-triggered, synthetic-only** execution contract for future WOF Beta/Assist. It does not inject real game input and does not provide autonomous gameplay.

## Safety boundary

- Execution requires `TriggerContext.user_triggered=true` and a source of `hotkey`, `explicit-ui`, or `test`.
- The prototype rejects any adapter whose `synthetic_only` flag is not true.
- `dry_run=True` is the default and produces deterministic trace events without adapter emission.
- Any precondition, timeout, deadline, cancellation, or ACK failure stops execution immediately.
- If a symbolic key is logically pressed when execution fails, the prototype performs a deterministic safety release on the synthetic adapter.
- There is no timer/agent/observer/autonomous trigger entry point.

## Files

- `executor.py` — deterministic executor and scripted synthetic adapter.
- `command_plan.schema.json` — narrow consumer contract for a future reverse-lane command model.
- `INTERFACE.md` — adapter, trigger, cancellation, ACK, timeout, trace, and Browser/emulator integration contracts.
- `fixtures/sample_command_plan.json` — synthetic symbolic plan; timings are fixture-only and are not game evidence.
- `tests/test_executor.py` — deterministic unit tests for success and fail-closed paths.
- `RESULT.md` — stage result and stop condition.

## Local deterministic test

From this directory:

```bash
python -m unittest discover -s tests -v
```

The implementation uses only the Python standard library.

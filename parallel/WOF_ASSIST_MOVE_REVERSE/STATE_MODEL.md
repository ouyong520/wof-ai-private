# WOF Assist One-Click Move — State Model

Stage: `WOF_ASSIST_ONECLICK_MOVE_COMMAND_REVERSE_V1`

Final reverse status: **PARKED — one bounded live-only fact is required before a live executor prototype is safe.**

## 1. Boundary

This state model is for an explicitly user-triggered assist action. It is not an autoplay loop, combat policy, enemy-response system, or hidden scheduler.

The currently proved input executor is synthetic-only. It requires an explicit `TriggerContext(user_triggered=True, source=<hotkey|explicit-ui|test>, request_id=<non-empty>)`; it does not register hotkeys, poll the game, decide when to act, or implement a live game adapter.

## 2. Product / request lifecycle

```text
UNREQUESTED
   |
   | explicit user action
   v
REQUESTED --invalid/duplicate--> REJECTED
   |
   | validate command model + trigger + preconditions
   v
READY
   | \
   |  \ user cancel
   |   -> CANCELLED
   |
   | explicit execution request
   v
EXECUTING
   | \
   |  \ fail/timeout/cancel/ACK failure
   |   -> FAIL_CLOSED -> SAFETY_RELEASE -> FAILED
   |
   | all normalized steps complete
   v
TRANSPORT_COMPLETED
   |
   | game acceptance/completion proof available?
   +-- no --> UNVERIFIED_GAME_OUTCOME
   +-- yes -> GAME_ACCEPTED -> GAME_COMPLETED -> RECOVERED
```

`TRANSPORT_COMPLETED` is deliberately not equivalent to `GAME_COMPLETED`. The synthetic executor can prove only its own deterministic trace, not that the game accepted a move.

## 3. Dedup / idempotency

Use `(request_id, planId)` as the invocation identity. A duplicate invocation must not silently replay. There is no automatic retry after failure because a retry would be a new gameplay action and therefore requires a new explicit user invocation.

## 4. Executor states and observable transport signals

| State | Entry evidence | Exit evidence | Failure behavior |
|---|---|---|---|
| `REQUESTED` | non-empty request ID + user-triggered context | validation succeeds | reject |
| `READY` | plan valid, trigger allowed, current preconditions true | first step starts | reject/cancel |
| `EXECUTING` | `step_started` | next step / plan end | stop immediately on error |
| `TRANSPORT_COMPLETED` | `execution_completed` | caller consumes result | no implicit game-success claim |
| `FAIL_CLOSED` | precondition false, cancel, timeout, deadline, failed/missing ACK, invalid op | cleanup attempted | no best-effort continuation |
| `SAFETY_RELEASE` | a logically pressed symbol remains after failure | release trace emitted/attempted | return failure |

The executor's optional `ack` hook is adapter-owned. No repository evidence currently binds an ACK name to a real WOF game-state event.

## 5. Grounded game observables

### P1 coordinates

Confirmed read-only fields:

- `X = 256 * U8(+0x0B) + U8(+0x04)`
- `Y_floor_depth = U8(+0x08)`

These are useful for locomotion observation and negative controls. They do not prove a direction/button command grammar or a special-move completion signal.

### Candidate action-state fields

ROM reverse evidence establishes this structural chain:

```text
selected-player pointer
    -> compare U8(player + 0x29) == 4
    -> branch into action dispatch
    -> read U8(player + 0x2A)
    -> indexed action dispatch

known action target 0x0112C2
    -> read U8(player + 0x2B)
    -> subdispatch
```

Safe interpretation:

- `+0x29 == 4` is an observed comparator/gate. Its semantic name is **unknown**.
- `+0x2A` is an observed action-dispatch selector/candidate observation field. Individual values are **not mapped to named moves**.
- `+0x2B` is an observed subdispatch selector at one known action target. Individual values are **not mapped to move phases**.

Therefore none of these fields may yet be configured as a game-specific executor precondition, acceptance ACK, completion ACK, or recovery ACK.

## 6. Admissibility model

### Proved architecture-level preconditions

A request is admissible to the current prototype only when all are true:

1. invocation is explicitly user-triggered;
2. source is `hotkey`, `explicit-ui`, or `test`;
3. request ID is non-empty;
4. command plan validates;
5. all adapter-owned preconditions for the next step are true;
6. the current adapter declares `synthetic_only=true`;
7. execution remains inside plan deadline and step timeout budgets.

### Unproved game-level preconditions

The repository does not yet prove which concrete WOF state(s) allow or forbid any direction+button move. In particular, the numeric `+0x29` comparator must not be renamed to “idle”, “grounded”, “recovered”, etc. without live or stronger offline evidence.

## 7. Command-state observation contract

A future live adapter may only promote candidate signals after evidence discriminates successful versus rejected attempts.

Required proof pattern for one representative command:

```text
PRECOMMAND_BASELINE
  -> timestamped input edges
  -> candidate state transition(s)
  -> independently labelled ACCEPTED or REJECTED
  -> if accepted: completion transition
  -> return/recovery transition
```

The same candidate state transition must not be accepted as an ACK merely because it correlates with one successful trial; it must distinguish the intentionally rejected controls in the minimum evidence request.

## 8. Cancellation and rollback

Cancellation is checked before each normalized step and after holds. On cancellation or any other execution failure:

- stop the plan;
- do not execute later steps;
- attempt deterministic release of any logically pressed symbol;
- return failure;
- do not retry automatically.

This cleanup rule is proved only for the synthetic adapter. A future live adapter needs separate proof that its release operation is safe and bounded.

## 9. Park boundary

The model cannot safely transition from `TRANSPORT_COMPLETED` to `GAME_ACCEPTED/GAME_COMPLETED/RECOVERED` because the repository currently lacks all three of the following for a concrete move:

1. a grounded direction+button edge sequence;
2. a bounded game timing/order window;
3. a discriminating game-state acceptance/completion/recovery signal.

The single bounded evidence request in `command_model.json` is sufficient to attempt to close all three facts for one representative move without expanding into a movelist, autoplay, or combat logic.

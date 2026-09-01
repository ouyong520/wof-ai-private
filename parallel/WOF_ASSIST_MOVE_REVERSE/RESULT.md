# WOF Assist — One-Click Move Command Reverse Result

Stage: `WOF_ASSIST_ONECLICK_MOVE_COMMAND_REVERSE_V1`

## Final status

**PARKED — OFFLINE LIMIT REACHED — ONE PRECISE LIVE-EVIDENCE REQUEST REQUIRED**

This is a successful park under the stage prompt's stop condition: further useful facts are live-only. The repository is sufficient to define the future executor contract and its fail-closed boundaries, but it is **not** sufficient to claim a concrete WOF direction+button command, its timing window, or its game-level acceptance/completion/recovery signal.

Do not label this stage `READY FOR EXECUTOR PROTOTYPE` for a live adapter yet.

## Scope preserved

- User-triggered assist only.
- No autoplay.
- No combat AI or automatic enemy response.
- No RAM writes.
- No live game input injection added.
- No production/Alpha/HUD/Owner One-Click paths modified.
- All durable stage outputs are under `parallel/WOF_ASSIST_MOVE_REVERSE/**` plus this stage's own claim.

## Durable outputs

- `parallel/WOF_ASSIST_MOVE_REVERSE/command_model.json`
- `parallel/WOF_ASSIST_MOVE_REVERSE/STATE_MODEL.md`
- `parallel/WOF_ASSIST_MOVE_REVERSE/RESULT.md`

No new parser/replay implementation was added: the existing synthetic input executor already validates/replays the normalized `press/release/hold` plan deterministically, and adding a second parser before concrete game semantics are known would duplicate architecture rather than reduce uncertainty.

## What is grounded offline

### 1. Execution grammar boundary

`parallel/WOF_ASSIST_INPUT_ARCH/INTERFACE.md` proves the downstream normalized contract:

- stable `planId`;
- whole-plan `deadlineMs`;
- ordered `steps[]`;
- step operations `press`, `release`, `hold`;
- opaque `symbol` tokens;
- optional per-step preconditions and ACK;
- per-step `timeoutMs`;
- explicit `TriggerContext(user_triggered=True, source=<hotkey|explicit-ui|test>, request_id=<non-empty>)`;
- deterministic cancellation, fail-closed stop, and safety-release behavior in the synthetic adapter.

Critically, that interface explicitly says fixture timing is not game timing and that the reverse lane must not invent command timing, aliases, ordering, bindings, or ACK semantics.

### 2. Confirmed P1 locomotion observables

`parallel/GEO/P1_XY_FRONTIER.md` confirms read-only P1 coordinates:

```text
X = 256 * U8(+0x0B) + U8(+0x04)
Y_floor_depth = U8(+0x08)
```

The evidence history includes an operator-controlled capture with visible RIGHT/LEFT traversal and UP/DOWN floor-depth traversal. This is enough to retain a partially grounded cardinal-locomotion family in the model, but not enough to claim emulator key bindings or deterministic press/hold/release timing.

### 3. Candidate action-state observation chain

`wof_selector_6a_action_causal_proof.js` and `wof_selector_6a_action_handler_map_v2.js` establish a structural ROM chain:

```text
selected-player pointer
  -> compare U8(player + 0x29) == 4
  -> branch to action dispatch
  -> read U8(player + 0x2A)
  -> indexed dispatch

known action target 0x0112C2
  -> read U8(player + 0x2B)
  -> subdispatch
```

Grounded interpretation is deliberately narrow:

- `+0x29 == 4`: observed comparator/gate; semantic state name unknown.
- `+0x2A`: action-dispatch selector/candidate observation field; values are not mapped to named moves.
- `+0x2B`: subdispatch selector at one known action target; values are not mapped to move phases.

These are useful candidates for a bounded live correlation run. They are not yet legal game-specific preconditions or ACKs.

## Minimum reusable command model

The semantic layer is separated from physical input binding:

```text
semantic command
  = ordered direction/button atoms
  + explicit edge/hold intent
  + evidence-backed timing/order constraints

normalized executor plan
  = ordered press/release/hold steps over opaque symbols
```

Rules:

1. A semantic atom may be compiled only after its binding and timing are grounded.
2. Synthetic fixture milliseconds must never be promoted to WOF timings.
3. `request_id + planId` is the invocation dedup identity.
4. Duplicate invocations do not silently replay.
5. There is no automatic retry after a failure; another gameplay action requires another explicit user invocation.
6. Transport completion does not imply game acceptance or game completion.

## Representative families

### Cardinal locomotion — partially grounded

Observed operator semantics: `RIGHT`, `LEFT`, `UP`, `DOWN`, with confirmed coordinate response.

Still unresolved:

- physical emulator/browser binding;
- exact event edge format;
- safe deterministic press/hold/release duration;
- live adapter cleanup semantics.

Therefore it remains unsafe for a live executor despite useful read-only evidence.

### Direction + button move — live-only blocker

No repository artifact found during this stage grounds all of the following for even one concrete move:

- the exact ordered direction/button edges;
- the timing/order acceptance window;
- a discriminating start/admissibility state;
- a game-level acceptance signal;
- a completion signal;
- a recovery signal.

The ROM action-selector artifacts cannot fill this gap without correlating them to a labelled input trace.

## One precise blocker / minimum live-evidence request

`WOF_ASSIST_MOVE_LIVE_EVIDENCE_001`

Perform **one bounded, operator-driven, passive read-only capture session** for one representative known direction+button move. Do not automate input and do not write game memory.

Required trials in the same repeatable neutral/idle setup:

- 3 successful attempts of the same command;
- 2 intentionally rejected attempts, changing only one timing/order boundary at a time.

Record synchronously at >=60 Hz:

1. monotonic timestamped raw direction/button press and release edges;
2. P1 `U8(+0x29)`, `U8(+0x2A)`, `U8(+0x2B)`;
3. P1 `U8(+0x04)`, `U8(+0x0B)`, `U8(+0x08)`;
4. a video/frame marker sufficient to independently label command attempted, accepted, completed, and recovered.

Exit fact for that single session:

> Derive one concrete command sequence, bounded ordering/timing constraints, one admissible-start predicate, and one discriminating acceptance/completion/recovery observation. If `+0x29/+0x2A/+0x2B` do not discriminate successful from rejected attempts, preserve that negative result and stop; do not widen into a movelist or combat reverse lane.

This is the smallest evidence request that can close the executor-significant uncertainty rather than merely add descriptive moves.

## Why work stops here

The start prompt says to stop/park when evidence becomes live-only or when the next useful fact requires real gameplay evidence. The input architecture independently has the same park boundary for actual game injection or live-only command semantics/timing/ACK behavior.

Continuing offline would now either:

- rename numeric fields without proof;
- copy synthetic timing into game semantics;
- expand a movelist without changing the executor contract; or
- drift toward live automation.

All four would violate the stage constraints.

## Downstream handoff

After `WOF_ASSIST_MOVE_LIVE_EVIDENCE_001` is satisfied, update only the concrete command entry and signal bindings in `command_model.json`, then normalize the proved command to the existing input executor schema. The first live executor must remain explicit-user-triggered and fail-closed, and live safety-release behavior needs its own proof before being relied upon.

## Stop condition

**ONE PRECISE BLOCKER / MINIMUM LIVE-EVIDENCE REQUEST PRODUCED — SAFE TO PARK THIS STAGE.**

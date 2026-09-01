# RC2 regression cases — enemy lifecycle / same-type slot reuse

Updated: 2026-09-01  
Scope: fixtures for the RC2 implementation owner. This lane does not change `product/alpha/**`.

## Test model

The fixtures below assume the RC2 engine exposes enough test-only control to distinguish continuity states conceptually:

```text
PROVEN | BROKEN | UNKNOWN
```

If implementation does not expose that enum publicly, tests may drive equivalent internal behavior. The production default for same-slot/same-type consecutive snapshots must remain `UNKNOWN` until a Browser-proven identity mechanism exists.

## P1 mandatory cases

### LIFE-001 — exact ALPHAQA-002 stale-watch reproduction

1. slot 0, type 20, exact T20 B0 state.
2. next sample exact T20 B255 state; fixture continuity is `PROVEN` only for the purpose of arming an A5136 history watch.
3. before horizon expiry, replace the object with a different type-20 episode in slot 0.
4. replacement is attack 0, neutral/nonmatching, valid target, no sampled `null`, no type change.
5. replacement boundary continuity is `UNKNOWN`.

Expected:

- zero user-facing warnings on the replacement sample;
- old watch cannot survive internally as publishable evidence;
- replacement target/coordinates must never be rendered with A's watch.

This is the direct regression for the QA blocker.

### LIFE-002 — hidden replacement manufactures a false T20 edge

1. episode A in slot 0/type20 is exact B0.
2. between samples A disappears and episode B of the same type occupies slot 0.
3. B's first observed state is exact B255.
4. no `null` or type change is sampled; continuity is `UNKNOWN`.

Expected:

- T20 must **not** arm;
- no A5136 warning is published.

This prevents a narrower stale-watch patch from leaving the cross-episode edge bug intact.

### LIFE-003 — hidden replacement manufactures a T16 entry

1. episode A is same type as the later T16 occupant and is attack 0 but does not match frozen T16 B4 predicate.
2. hidden same-type replacement occurs.
3. episode B's first observed sample matches exact T16 B4 predicate.
4. continuity is `UNKNOWN`.

Expected:

- history/entry rule does not arm under the conservative RC2 policy.

### LIFE-004 — hidden replacement manufactures D867 entry

Same shape as LIFE-003, with current B matching exact `D867BA_3232_TM6_220` base.

Expected: no user-facing D867 history warning when continuity is `UNKNOWN`.

### LIFE-005 — hidden replacement manufactures D881 entry

Same shape as LIFE-003, with current B matching exact `D8811E_3232_TM6_135` base.

Expected: no user-facing D881 history warning when continuity is `UNKNOWN`.

## T18 current-level cases

### LIFE-006 — T18 old level warning cannot follow neutral replacement

1. episode A in slot 0 matches exact `T18_5440_CYCLE_BODY7512_TM4_LEVEL_90` predicate.
2. warning is visible.
3. hidden same-type replacement B appears in slot 0 with attack 0 but neutral/nonmatching state.
4. no sampled `null` or type change.

Expected on B sample:

- T18 warning is gone immediately;
- no 90 ms carry from A.

### LIFE-007 — second T18 level rule cannot follow neutral replacement

Repeat LIFE-006 for `T18_5424_CYCLE_BODY7520_TM4_LEVEL_90`.

Expected: warning disappears on first nonmatching B sample.

### LIFE-008 — matching T18 replacement is fresh evidence

1. episode A matches a frozen T18 level predicate.
2. hidden same-type replacement B occurs.
3. B's first observed sample independently matches the same exact frozen T18 predicate.

Expected:

- warning may be visible because the **current B sample** satisfies the rule;
- output must not inherit A's arm timestamp, age, target provenance, watch ID, retarget history, or once-per-cycle suppression state;
- if diagnostics expose provenance, classify it as fresh current-level evidence.

### LIFE-009 — T18 hold-only exit

1. current sample matches T18 exact predicate.
2. next sample is the same episode and remains attack 0 but leaves the exact predicate.

Expected:

- user-facing T18 warning disappears on sample 2 even though the original 90 ms research horizon has not elapsed.

This intentionally trades persistence for release-safe lifetime semantics until positive episode continuity exists.

## Existing lifetime controls must remain green

### LIFE-010 — slot gone

Arm any test watch, then omit the slot.

Expected: warning and publishable watch state cleared.

### LIFE-011 — type change

Arm any test watch, then reuse slot with a different enemy type.

Expected: warning and publishable watch state cleared.

### LIFE-012 — runtime clear/restart

Arm a test watch, call engine/runtime clear, then provide a same-type matching slot.

Expected: no pre-clear historical warning survives.

## Target / retarget adversarial cases

### LIFE-013 — target change is not lifecycle identity

For a current-level T18 matching sample, change only the valid live target/geometry while the predicate still matches.

Expected:

- warning remains valid as current-level evidence;
- target/side are recomputed from current sample;
- target change alone must not be promoted to an enemy episode ID.

### LIFE-014 — replacement target cannot resurrect history warning

Arm a history watch in test scaffolding, then hidden same-type replacement B appears with a different valid target and neutral state.

Expected: no warning; the presence of a valid new target must not keep the old watch alive.

## Timing / sampling cases

### LIFE-015 — long poll gap invalidates history

Provide two same-slot/same-type samples separated by an intentionally large scheduler gap.

Expected:

- history continuity is not inferred from type equality;
- no edge/history warning is allowed to bridge the gap.

The fixture should not encode an arbitrary production threshold as a proof of identity. It only verifies fail-closed behavior.

### LIFE-016 — adjacent 10 ms samples are still not identity proof

Provide A and hidden same-type replacement B at nominal 10 ms spacing with no null/type change.

Expected: behavior remains fail-closed for history rules. Nominal polling cadence must not upgrade continuity from `UNKNOWN` to `PROVEN`.

## Cross-slot cases

### LIFE-017 — same-type enemy moves to another slot

1. A warning exists for slot 0/type T in test scaffolding.
2. next sample has slot 0 neutral/other occupant and a matching type-T enemy in slot 1.

Expected:

- no warning migrates from slot 0 to slot 1;
- warnings are never reassociated by type, target, or proximity.

### LIFE-018 — simultaneous same-type enemies

Two same-type enemies occupy distinct slots; only one current-level T18 predicate matches.

Expected:

- only the matching slot publishes the T18 warning;
- target/geometry remain per-slot current evidence;
- no shared type-level arming state suppresses or transfers warnings between slots.

## Negative guards: forbidden identity heuristics

### LIFE-019 — same position does not prove continuity

A and B use same slot, same type, same target and same X but are fixture-marked as distinct episodes / continuity `UNKNOWN`.

Expected: history rules remain suppressed.

### LIFE-020 — same descriptor fingerprint does not prove continuity

A and B have identical visible descriptor/state fields but are distinct episodes / continuity `UNKNOWN`.

Expected: no old history watch is published solely because the fingerprints match.

### LIFE-021 — WinKawaks metadata is absent from Browser fixture contract

Static/source-level assertion:

- RC2 Browser snapshots and lifecycle code must not add WinKawaks-local `+0xB4`, `+0xB6`, or any other local offset as release identity without a separate Browser proof artifact.

Expected: assertion passes.

## Optional restoration tests for a future Browser identity token

These are **not RC2 blockers** under the quarantine policy. Use them only if a later Browser-proven episode token is introduced.

### LIFE-F01 — stable token allows true T20 edge

Same episode, stable proven token, exact B0 -> B255.

Expected: T20 can arm normally.

### LIFE-F02 — token change blocks same-type false edge

Same slot/type, token changes between B0 and B255.

Expected: no T20 arm; old history is invalidated before rule evaluation.

### LIFE-F03 — token change clears armed watch

Arm a history warning with token A, then current sample is same slot/type with token B.

Expected: old warning cleared before rendering.

## RC2 lifecycle acceptance gate

The lifecycle blocker is closed when mandatory LIFE-001 through LIFE-021 are green (with fixtures adapted to the final internal API), while the pre-existing Alpha regression suite remains green except for intentionally quarantined history-warning expectations that are explicitly updated as a safety change.

Human Browser testing is not required to establish the safety property of this conservative policy. Human Browser testing is only required if the implementation owner elects to preserve/restore history-dependent warnings using a new Browser continuity mechanism.

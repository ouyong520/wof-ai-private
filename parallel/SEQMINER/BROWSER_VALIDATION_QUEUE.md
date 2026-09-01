# SEQMINER Browser Validation Queue

Purpose: rank **prospective experiments**, not production rules.

No item below may be promoted from WinKawaks/local discovery alone.

## P0 — T18 BODY4728 post-anchor split

Known prospectively ambiguous anchor:

```text
S0/A4/B2|BODY4728|FE8b660|NX8b204|Vffff|TM1|P6C4736
```

Known WOF-051 outcomes:

```text
A4704 @ 19.9 ms
A4712 @ 100.4 ms
```

### Validation target

Arm only after the shared anchor occurs in an attack-zero cycle. Preserve ordered distinct states from at least the immediately preceding tail3 through the first several post-anchor transitions.

Rank discriminators in this order:

1. first post-anchor distinct state;
2. post-anchor pair;
3. post-anchor triple;
4. post-anchor descriptor/next progression;
5. exact timer progression;
6. timer-normalized progression;
7. pre-anchor tail2/tail3 only if post-anchor context is still ambiguous.

### Pass condition

A candidate branch must be prospectively armed before ACTIVE and produce repeated A4704/A4712 separation with stable target/side. One successful hit is discovery, not validation.

## P1 — T23 A5888 ordered BODY4936 tail

Discovery sequence from WOF-047:

```text
S0/A8/B2 BODY4936
-> S0/A2/B0 BODY4936
-> S0/A6/B4 BODY4936
```

Observed eventual attack: `A5888`.

Why high priority: the first state alone also appears in an A4792 cycle, making this a direct example where order adds discriminatory information.

### Pass condition

Prospectively arm on the complete ordered tail, not any constituent state. Require multiple evaluable cycles and report all outcomes, including misses/alternate attacks. Preserve target changes at the ACTIVE edge.

## P2 — T23 branch-set validator

WOF-047 resolved only eight T23 cycles and shows that A4792 itself is multi-branch. Do not force a single universal signature.

Build a small branch set from repeated exact/timer-normalized tail2/tail3 families and validate each branch separately against:

```text
A4792
A4920
A5888
other ACTIVE attacks
```

Priority goes to branches that are repeated, attack-pure in discovery, and target-stable.

## P3 — cross-target sequence invariance

For any P0-P2 candidate that survives initial prospective testing, repeat across at least two physical targets if coverage permits.

Reason: retained WinKawaks evidence separates live target from sticky association/reference state, and Browser WOF-047 also exposed target evolution inside T23 cycles. A branch that only works for one target is still useful, but must be labelled target-conditioned rather than universal.

## P4 — all-game ambiguous-type queue

When retained all-game sweep raw becomes visible to SEQMINER and a true local attack descriptor is available, automatically rank every type where:

```text
same final/single state -> more than one eventual activeAttack
```

For each such type, queue the shortest sequence that resolves the ambiguity in this order:

```text
final
-> tail2
-> tail3
-> transition pair
-> transition triple
-> timer-normalized pair/triple
```

Only candidates that remain stable across captures/scenes/targets should be sent back to Browser.

## Explicit non-candidates

Do **not** queue as attack-specific Browser rules:

- T18 BODY4728/A4/B2/TM1 by itself — already falsified as attack-specific.
- any T23 single state whose membership spans multiple eventual attacks.
- WinKawaks `+0x73 != 0` — structural phase proxy only.
- WinKawaks `+0x24 != 0` — type/type-present lifecycle only.
- a pair/triple observed once in one capture.

## Recapture policy

No new Collector task is requested now.

A tiny targeted recapture becomes justified only if an exact WinKawaks-local attack descriptor is independently identified and the only missing evidence is repeated same-cycle coverage of one already-ranked branch. Until then, reuse retained raw and Browser prospective instrumentation.

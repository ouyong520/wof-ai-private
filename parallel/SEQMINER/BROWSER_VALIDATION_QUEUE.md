# SEQMINER Browser Validation Queue

Updated: 2026-09-01

Purpose: rank **prospective Browser experiments**, not production rules. WinKawaks numeric offsets/cursors are discovery structure only and are never copied numerically into Browser/WASM rules.

## P0 — T18 BODY4728 post-anchor split

Known prospectively ambiguous Browser anchor:

```text
S0/A4/B2|BODY4728|FE8b660|NX8b204|Vffff|TM1|P6C4736
```

Known WOF-051 outcomes:

```text
A4704 @ 19.9 ms
A4712 @ 100.4 ms
```

### Arm condition

Arm only after the shared state appears while the same enemy is in the current zero-attack cycle.

Preserve:

```text
pre-anchor tail3
-> anchor
-> first post-anchor distinct state
-> next 2-3 distinct states
-> ACTIVE
```

Candidate ordering:

1. first post-anchor distinct state;
2. post-anchor pair;
3. post-anchor triple;
4. descriptor/body/frameEnd/next progression;
5. timer progression and time already held at terminal timer value;
6. pre-anchor tail2/tail3 only if post-anchor path remains shared.

Pass condition: repeated prospective separation of A4704 vs A4712, with all alternate outcomes/misses recorded and live target/side checked at ACTIVE. One success is discovery only.

## P1 — T23 A5888 BODY4936 ordered tail

Discovery tail:

```text
S0/A8/B2 BODY4936
-> S0/A2/B0 BODY4936
-> S0/A6/B4 BODY4936
```

Observed eventual attack: `A5888`.

The first state also occurs in an A4792 cycle. Arm on the **complete ordered path**, not any constituent state. Require multiple evaluable cycles and preserve event-edge retarget changes.

## P2 — T23 branch-set validator

WOF-047 has only eight cycles and A4792 itself is multi-branch.

Build separate branches from repeated exact/timer-normalized tail2/tail3 families and validate each against:

```text
A4792
A4920
A5888
other ACTIVE attacks
```

Prefer the shortest branch that stays attack-pure after target conditioning. Do not merge distinct branches merely to make one universal rule.

## P3 — cross-target invariance

Any P0-P2 branch that survives initial testing should be exercised across at least two physical targets when coverage permits.

A target-conditioned branch is allowed, but must be labelled target-conditioned rather than universal.

## P4 — future local-to-Browser handoff

When a true WinKawaks-local exact attack field and labeled sweep series exist, SEQMINER will rank ambiguous local types automatically.

The handoff to Browser is **semantic/structural**, for example:

```text
shared pre-attack state
-> branch A uses descriptor transition X->Y + short terminal hold
-> branch B uses X->Z + long terminal hold
```

The Browser test must rediscover/express equivalent Browser fields independently. Do not paste WinKawaks numeric offsets/cursors into Browser code.

## Explicit non-candidates

Do not queue as attack-specific rules:

- T18 BODY4728/A4/B2/TM1 by itself;
- any T23 state known to span eventual attacks;
- WinKawaks `+0x73 != 0`;
- WinKawaks `+0x24 != 0`;
- any local branch hotspot without an exact local attack label;
- any pair/triple supported by only one cycle.

## Recapture policy

No Collector task is requested.

The missing evidence is not generic raw volume. A tiny local recapture becomes justified only after an exact local attack label exists and one already-ranked sequence discriminator is missing a narrowly defined replication condition.
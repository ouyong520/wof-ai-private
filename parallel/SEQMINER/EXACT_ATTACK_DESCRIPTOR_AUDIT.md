# SEQMINER Exact WinKawaks-local Attack Descriptor Audit

Updated: 2026-09-01  
Evidence namespace: **WinKawaks-local discovery only**  
Verdict: **NOT PROVEN in the current connector-visible retained corpus**

This audit exists to prevent an attack-associated structural field from being silently promoted into an exact move-valued attack label merely because SEQMINER needs one.

## Question

Does the currently retained WinKawaks-local enemy `0xE0` object expose a field already proven to mean an exact move/attack identity, suitable for grouping zero-prefix sequences by later values analogous to Browser `A4704`, `A4712`, `A4792`, `A4920`, `A5888`, etc.?

Current answer: **no proven field is available**.

This is not a proof that no such field exists. It is a proof-status audit: the existing reports do not establish one with the evidence standard required by SEQMINER.

## Browser attack values are labels in a different namespace

Browser-labelled outcomes used to prioritize validation include:

| Browser decimal label | hex |
|---:|---:|
| `A4704` | `0x1260` |
| `A4712` | `0x1268` |
| `A4792` | `0x12B8` |
| `A4920` | `0x1338` |
| `A5888` | `0x1700` |

These values are **not searched as assumed WinKawaks offsets or semantics**. Their only use here is to check whether existing human-readable local reports had already surfaced an obviously corresponding exact value/field. They had not.

The bridge `results/efield/summary.json` contains no named `activeAttack` field. Exact searches in that retained summary for listed value entries `4704`, `4712`, `4792`, `4920`, and `5888` returned no match. Because the summary is a ranked/statistical report rather than an exhaustive dump of every raw U16/U32 value, this is **not** used as absence proof; it only means the existing summary does not already expose an obvious exact Browser-like label.

## Attack-themed bridge reports are structurally anchored

### `results/efield/ATTACK_CYCLE.md`

The report explicitly defines:

```text
episode anchor = contiguous +0x73 != 0 run
```

Its outputs are phase-transition/dwell distributions for `+0x6C/+0x70/+0x72/+0x73/+0x77`. This establishes a structured attack-associated executor phase system. It does not establish a move ID.

### `results/efield/MOVE_ATTACK.md`

The report calls its events `attack-field transition events` and finds:

```text
+0x6C attackSupport = 1.0
+0x73 attackSupport = 1.0
```

But the attack event itself is derived from that attack-associated phase family. Perfect selectivity to the phase-transition anchor is therefore evidence that `+0x6C/+0x73` participate in the executor phase transition; it is not independent proof that either field uniquely names the eventual move.

Other strongly attack-selective bytes (`+0x70/+0x72/+0x77/+0x37`, plus sparse candidates) remain phase/gate/context evidence. No report demonstrates a one-to-one or stable many-to-one mapping from one of these local values to exact Browser-like move outcomes.

### `results/efield/ACTIVE_STATE.md`

This report's `ACTIVE` terminology is based on a provisional type-present/lifecycle anchor (`type u16 @ 0x23 != 0`). It must not be confused with Browser semantic attack ACTIVE.

## EFIELD owner boundary

The authoritative EFIELD frontier/completion already limits the attack-side fields to structural meanings:

```text
+0x6C  fine executor / attack-associated phase
+0x73  coarse executor / attack-family phase
+0x70  second fine executor / attack-associated phase
+0x77  second coarse executor / attack-family phase
+0x72  joint-phase companion candidate
+0x37  attack/executor-family gate candidate
```

The owner explicitly does not promote these to hitbox-active, damage onset, startup, recovery, visual attack frame, or exact move names.

SEQMINER inherits that semantic boundary.

## Candidate bytes not promoted by selectivity alone

`MOVE_ATTACK.md` lists additional attack-selective offsets such as `+0xC9`, `+0x64`, `+0x6A`, `+0xCE`, `+0x69`, `+0x7E`, and `+0x71`.

They are **not** treated as exact attack descriptors because the current reports do not provide all of the following:

1. a clear field width and value interpretation;
2. same-object zero -> exact move-valued event cycles;
3. repeated mapping of field values to independent labeled attacks;
4. cross-capture stability;
5. counterexamples / ambiguity accounting;
6. independence from the phase-transition anchor used to discover them.

High attack-transition selectivity is sufficient for candidate ranking, not semantic promotion.

## What would count as proof

An exact WinKawaks-local attack descriptor may be accepted by SEQMINER only after an independent result establishes at least:

- exact local offset and minimum width/endian;
- zero/nonzero or idle/active lifecycle of the field;
- repeated same-object cycles where a pre-event sequence is followed by a stable exact move value;
- multiple exact values corresponding to distinct local move outcomes;
- no collapse to a generic phase family that spans several moves;
- cross-capture reproduction;
- explicit counterexamples and ambiguity rate;
- no Browser/WASM numeric-offset equivalence assumption.

Once that exists, `seqminer.py` v3 can use:

```text
--attack-offset 0xNN --attack-width N --attack-endian be|le
```

and regenerate attack-labelled final/tail2/tail3/pair/triple/timer/reload tables.

## Current decision

```text
exactLocalAttackDescriptor = UNPROVEN
phase73StructuralProxy = AVAILABLE
attackAssociatedExecutorTopology = STRONG
exactAttackSequenceAtlas = BLOCKED_BY_LABEL_SEMANTICS
newGenericCollectorCapture = NOT_REQUESTED
browserProductionPromotion = FORBIDDEN
```

No existing offset is promoted merely to unblock SEQMINER.

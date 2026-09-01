# WOF COVERAGE MATRIX — normalized refresh

Snapshot: `2026-09-01`  
Canonical enemy type notation: **`T<decimal> (0xHH)`**. Old hex-style labels are deprecated.

## Executive verdict

- `SWEEPATLAS`: **present / ingested**.
- `SEQMINER`: **present / ingested**.
- retained WinKawaks type universe in the audited EFIELD corpus: **T1 (0x01) .. T31 (0x1F), all observed**.
- type-present samples: **60,271** across **7** EFIELD raws / **23,400** frames / **2** sessions.
- same-type lifecycle episodes: **1,604** aggregate.
- confirmed live-target changes: **8**.
- structural attack/executor episodes: **271** aggregate.
- **human recap required: NO**.

The old COVERAGE snapshot was stale in two material ways: it treated SWEEPATLAS/SEQMINER as absent, and it mixed old hex-style `Txx` notation with Browser decimal notation. In particular, old `T17` represented raw `0x17`, which is canonically **T23 (0x17)**; local T23 is therefore not missing and has **2,140** retained samples.

## Gap legend

| Class | Meaning |
|---|---|
| `PHYSICAL` | required bytes/condition are genuinely absent from retained corpus |
| `ANALYSIS` | retained bytes exist but requested cross-tab has not been materialized |
| `LABEL` | semantic/human label is not authoritative in retained evidence |
| `BROWSER` | local evidence exists but production-context prospective validation is still needed |

## Per-type normalized cross-tab

| Type | Samples | Density | Stable-type retarget | Replacement-boundary retarget | Ordered evidence | Lifecycle / target occupancy / structural attack per-type counts |
|---|---:|---|---|---|---|---|
| T1 (0x01) | 173 | LOW | — | — | global executor topology only | `ANALYSIS` — not safely materialized per type |
| T2 (0x02) | 408 | LOW | — | — | global executor topology only | `ANALYSIS` — not safely materialized per type |
| T3 (0x03) | 160 | LOW | — | — | global executor topology only | `ANALYSIS` — not safely materialized per type |
| T4 (0x04) | 300 | LOW | — | — | global executor topology only | `ANALYSIS` — not safely materialized per type |
| T5 (0x05) | 495 | LOW | — | — | global executor topology only | `ANALYSIS` — not safely materialized per type |
| T6 (0x06) | 354 | LOW | — | — | global executor topology only | `ANALYSIS` — not safely materialized per type |
| T7 (0x07) | 2,670 | GOOD | — | T7 → T16, P3→P1 @ EFIELD-004 f2961 s17 | global executor topology only | `ANALYSIS` — not safely materialized per type |
| T8 (0x08) | 7,293 | GOOD | — | — | global executor topology only | `ANALYSIS` — not safely materialized per type |
| T9 (0x09) | 2,894 | GOOD | P3→P1 @ EFIELD-003 f3322 s19 | T27 → T9, P2→P1 @ EFIELD-004 f2961 s18 | global executor topology only | `ANALYSIS` — not safely materialized per type |
| T10 (0x0A) | 645 | GOOD | — | — | global executor topology only | `ANALYSIS` — not safely materialized per type |
| T11 (0x0B) | 1,102 | GOOD | P1→P3 @ EFIELD-003 f492 s17 | — | global executor topology only | `ANALYSIS` — not safely materialized per type |
| T12 (0x0C) | 469 | LOW | — | — | global executor topology only | `ANALYSIS` — not safely materialized per type |
| T13 (0x0D) | 470 | LOW | — | — | global executor topology only | `ANALYSIS` — not safely materialized per type |
| T14 (0x0E) | 411 | LOW | — | — | global executor topology only | `ANALYSIS` — not safely materialized per type |
| T15 (0x0F) | 187 | LOW | — | — | global executor topology only | `ANALYSIS` — not safely materialized per type |
| T16 (0x10) | 9,210 | GOOD | P3→P2 @ EFIELD-003 f1827 s17 | T7 → T16, P3→P1 @ EFIELD-004 f2961 s17 | global executor topology only | `ANALYSIS` — not safely materialized per type |
| T17 (0x11) | 2,002 | GOOD | — | — | global executor topology only | `ANALYSIS` — not safely materialized per type |
| T18 (0x12) | 528 | GOOD | — | — | type-specific local + Browser ordered evidence | `ANALYSIS` — not safely materialized per type |
| T19 (0x13) | 1,013 | GOOD | — | — | global executor topology only | `ANALYSIS` — not safely materialized per type |
| T20 (0x14) | 686 | GOOD | — | — | global executor topology only | `ANALYSIS` — not safely materialized per type |
| T21 (0x15) | 2,285 | GOOD | — | — | global executor topology only | `ANALYSIS` — not safely materialized per type |
| T22 (0x16) | 2,309 | GOOD | P3→P1 @ EFIELD-002 f2167 s19 | — | global executor topology only | `ANALYSIS` — not safely materialized per type |
| T23 (0x17) | 2,140 | GOOD | — | — | type-specific local + Browser ordered evidence | `ANALYSIS` — not safely materialized per type |
| T24 (0x18) | 12,866 | GOOD | P1→P3 @ EFIELD-002 f3155 s17 | — | global executor topology only | `ANALYSIS` — not safely materialized per type |
| T25 (0x19) | 6,807 | GOOD | P1→P3 @ EFIELD-002 f3416 s18 | — | global executor topology only | `ANALYSIS` — not safely materialized per type |
| T26 (0x1A) | 1,060 | GOOD | — | — | global executor topology only | `ANALYSIS` — not safely materialized per type |
| T27 (0x1B) | 591 | GOOD | — | T27 → T9, P2→P1 @ EFIELD-004 f2961 s18 | global executor topology only | `ANALYSIS` — not safely materialized per type |
| T28 (0x1C) | 188 | LOW | — | — | global executor topology only | `ANALYSIS` — not safely materialized per type |
| T29 (0x1D) | 272 | LOW | — | — | global executor topology only | `ANALYSIS` — not safely materialized per type |
| T30 (0x1E) | 133 | LOW | — | — | global executor topology only | `ANALYSIS` — not safely materialized per type |
| T31 (0x1F) | 150 | LOW | — | — | global executor topology only | `ANALYSIS` — not safely materialized per type |

### What the table does and does not prove

Sample density is directly materialized by SWEEPATLAS. Retarget rows are exact retained target-change anchors. Ordered evidence is type-specific only where SEQMINER publishes a type-linked example (T18/T23); other types inherit only the global executor-topology corpus, not a claimed type-specific sequence. Per-type lifecycle episode totals, P1/P2/P3 dwell counts, and structural attack/executor episode totals are **analysis/materialization gaps**: aggregate totals exist, but the current retained human-readable outputs do not safely expose those contingency tables.

## Priority type correction

| Type | Local retained evidence | Browser evidence / boundary | Coverage judgment |
|---|---|---|---|
| T16 (0x10) | 9,210 samples; same-type P3→P2 retarget; replacement-boundary arrival T7→T16 at P3→P1 | WOF-051 98/98 strict danger, target/side 98/98 | local GOOD + Browser strong |
| T18 (0x12) | 528 samples; SEQMINER delayed-reload ordered example | A5440 4/4, A5424 4/4; BODY4728 anchor split A4704/A4712 | local GOOD; ordered Browser discriminator still open |
| T20 (0x14) | 686 samples | WOF-051 5/5 strict A5136/target/side | local GOOD + Browser strong |
| T23 (0x17) | 2,140 samples; SEQMINER delayed-reload ordered example | WOF-047: A4792=3 / A4920=3 / A5888=2; later rooms sometimes had zero T23 | local GOOD; Browser scene availability variable, not local missing data |
| T24 (0x18) | 12,866 samples | two production-shadow candidates exist; WOF-051 had zero room coverage | local GOOD; latest Browser zero coverage is scene absence, not rule failure |

## Aggregate target coverage

WinKawaks EFIELD confirms three distinct player-reference layers and 8 exact live-target changes. Existing retained accounting also has global live-target dwell counts P1 **46,865**, P2 **2,967**, P3 **10,439**. These global totals remain useful, but per-type P1/P2/P3 dwell is not yet materialized and must not be guessed from the 8 transition events.

Exact stable-type target-change anchors:

- T22 (0x16): P3→P1
- T24 (0x18): P1→P3
- T25 (0x19): P1→P3
- T11 (0x0B): P1→P3
- T16 (0x10): P3→P2
- T9 (0x09): P3→P1

Replacement-boundary anchors:

- T7 (0x07) → T16 (0x10), P3→P1
- T27 (0x1B) → T9 (0x09), P2→P1

## Aggregate structural attack / executor coverage

Current local corpus contains **271** contiguous `+0x24 != 0 && +0x73 != 0` structural executor episodes. This is not semantic Browser ACTIVE and not exact move identity. Per-type episode counts remain an `ANALYSIS` gap; exact type×attack/move remains additionally blocked by the missing proven WinKawaks-local exact move label.

## Ordered-sequence coverage

SEQMINER is now present and has exhausted the current retained structural corpus. Global record-aware order, timer/hold, branch, mode and delayed-reload topology are materialized. T18 (0x12) and T23 (0x17) each have explicit local type-linked ordered examples. Browser-labelled ordered evidence exists for both priority types, but it is kept separate from WinKawaks-local semantics.

## Provenance / data quality

- bridge head remains `e3676d79a38ac23e572af69d23d560c01bd6777d`, the same bridge snapshot audited by the old COVERAGE matrix; no new gameplay capture landed after that ledger point.
- 30 retained raw artifacts total; 28 mechanically successful gameplay raws, 2 collector/platform test raws excluded.
- all 28 successful gameplay raws have complete task/status/result/raw identity chains.
- failed acquisition attempts are provenance rows only and never samples.
- BASECAP v1 is complete; GEO core is closed; EFIELD bounded mapping is complete; RAWMINE current assignment is complete.

## Remaining gaps by class

| Gap | Class | Recapture now? | Reason |
|---|---|---|---|
| lifecycle episode count per type | ANALYSIS | NO | aggregate 1,604 exists; contingency not materialized |
| P1/P2/P3 dwell per type | ANALYSIS | NO | global dwell + transition events exist; contingency not materialized |
| structural executor episode count per type | ANALYSIS | NO | aggregate 271 exists; contingency not materialized |
| exact type×local-move matrix | ANALYSIS + LABEL | NO | exact local move/attack semantic label is not proven |
| stage / scene / wave | LABEL / missing labeled corpus | NO | no authoritative labels; broad replay is not a bounded minimal recap |
| boss / ordinary / visible enemy name | LABEL | NO | no authoritative join source |
| semantic ACTIVE/hitbox/damage cycle | LABEL | NO | structural executor state must not be renamed |
| T18 post-anchor attack split | BROWSER | not a WinKawaks recap | WOF-052 Browser data gate |
| broader T23 prospective validation | BROWSER | only if cost-effective scene appears | do not force rare scene coverage |

## Recap verdict

**human recap required: NO**

No Collector task is created. A labeled full-game `BASECAP-SWEEP-*` series is genuinely absent, but the current evidence does not identify one specific Product/Beta/v1-critical scene that is both unrecoverable from retained raw and cheap enough to justify human replay. Broad recollection would violate the stop policy. The correct next step is to consume/materialize existing data and allow MAINLINE/Product Browser gates to proceed independently.

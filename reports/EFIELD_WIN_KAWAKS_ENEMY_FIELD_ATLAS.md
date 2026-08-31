# WinKawaks Enemy Field Atlas (EFIELD)

Research line: `EFIELD-` only. This document is a WinKawaks-local discovery atlas, not a Browser/WASM offset contract and not a Future Danger rule specification.

## Scope / invariants

- enemy pool: `0xFFC0BC`
- stride: `0xE0`
- slots: `20`
- read-only; no game-memory writes
- do not modify/advance WOF-045
- do not modify T16/T18/T20/T23/T24/D867/D881 production-shadow rules
- WinKawaks offsets remain namespace-local unless separately re-proven elsewhere
- Collector raw frames are normalized CPS byte-lane captures; semantic field labels below remain WinKawaks hypotheses

## Current field atlas

| Offset | Width | Current evidence | Atlas interpretation |
|---|---:|---|---|
| `0x00` | U8 | 9000 frames: slots 17/18/19 always `1`; slots 0..16 always `0`; zero transitions | **slot-allocation / occupied-object-header candidate**; static in current scene, not current enemy-presence ACTIVE |
| `0x07..0x0A` | s32 candidate | coordinate-X anchor; actual dynamic payload concentrated in lower bytes `0x08/0x09` for current numeric range | high-value geometry / X candidate |
| `0x0B..0x0E` | s32 candidate | coordinate-Y anchor; actual dynamic payload concentrated in `0x0C/0x0D` | high-value geometry / Y candidate |
| `0x15` | u32 candidate | historically static in bounded run | constant/stage-specific candidate |
| `0x24` | **U8** | `0x23` byte is 0 in all 180000 samples; `0x24` has 31 values and all 42 type-present enter/exit edges | **type / current-type-present candidate**; replaces legacy `u16@0x23` wrapper |
| `0x28` | U8 | runs 2+3: exact on 6/6 retargets; 53 total changes; every retarget `00->02` | sparse retarget-associated trigger/state pulse; not target identity |
| `0x2D` | U8 | 361 changes over runs 2+3; exact on 6/6 retargets; usually resets to zero | broad action/state-reset companion |
| `0x2E` | U8 | 710 changes over runs 2+3; exact on 6/6 retargets; strong provisional type-present classifier | broad action/state candidate |
| `0x2F` | u32 candidate | very high transition activity | animation/state progression candidate |
| `0x33` | u32 candidate | strong repeated dynamic cluster; can change independently | timer/progress/phase candidate |
| `0x37` | u16 candidate | sparse transitions | sparse transition/timer candidate |
| `0x65` | U8 | exact on 6/6 retargets but 247 total changes; `00->01/02` | sparse retarget-associated trigger/substate; not target identity |
| `0x6C` | U8 | changes on 772/772 attack-anchor transitions; 810 total active changes; values subdivide coarse `0x73` states | **fine attack substate/phase candidate** |
| `0x6D..0x6E` | U16 BE | six total changes over runs 2+3; all six are known P1/P2/P3 retargets | **strong dynamically supported WinKawaks-local player-target pointer candidate** |
| `0x70` | U8 | attack support 0.9236, movement support 0.0149 | attack/body-neighborhood state candidate |
| `0x71..0x72` | u16 candidate | body anchor; `0x72` changes on every `0x73` attack transition but also within coarse attack states | body/animation-state candidate; attack-coupled low byte |
| `0x73..0x74` | u16 candidate | attack anchor; in current numeric domain only `0x73` changes, `0x74` static | **coarse attack-state/family candidate** |
| `0x77` | U8 | attack support 0.8990, movement support 0.0149 | attack-neighborhood state candidate |
| `0x81` | u16 prior reference | historical integration explicitly treated as non-semantic | unknown/reference only; do not promote |
| `0x9C` | U8 | persistent high-frequency dynamic, strong `0x04` pair; movement-biased | high-frequency state/counter candidate |
| `0xA2` | U8 | ~14.5% movement support, ~0.65% attack support; mostly descending values | movement-associated counter/state candidate |
| `0xB9` | U8 | ~44.3% movement support, ~0.78% attack support; 9-value domain; transitions mostly descending/cyclic | **strong movement-associated phase/counter candidate** |
| `0xBB` | U8 | ~7.33% movement support, ~0.13% attack support; most transitions are countdown-like | sparse movement-associated timer/counter candidate |
| `0xB4` | U8 | type-exit exact 8/21, only 10 total changes | sparse lifecycle-exit flag candidate; insufficient coverage |
| `0xB6` | U8 | type-exit exact 11/21, only 19 total changes; provisional type-present balanced accuracy 0.967 | sparse lifecycle/deallocation-substate candidate; insufficient coverage |

## Corrected type width

A dedicated three-run width verification over `180000` enemy-object samples established:

- byte `0x23`: exactly one value, `0x00`, count `180000`
- byte `0x24`: `31` distinct values
- legacy `u16@0x23..0x24` values are always `0x00XX`

Therefore the atlas now treats **`0x24` U8** as the type candidate. The previous `u16@0x23` representation remains historical only. The bridge analyzer has also been migrated to anchor `type_candidate=(0x24,1)`.

## Allocation vs current type-present state

The previous generic ACTIVE heuristic produced `0/0` enter/exit events. Three-run classification explains why.

Across 9000 captured frames:

- total enemy-object samples: `180000`
- slots `0..16`: `0x00 == 0` for all `153000 = 17 × 9000` samples
- slots `17..19`: `0x00 == 1` for all `27000 = 3 × 9000` samples
- among those three allocated slots, `0x24 != 0` for `21847` samples and `0x24 == 0` for `5153` samples
- `0x00` changed zero times
- `0x24` type-present zero->nonzero edges: `21`
- `0x24` type-present nonzero->zero edges: `21`
- whole-object all-zero->nonzero / nonzero->all-zero edges: `0 / 0`

Current structural interpretation:

1. `0x00` is a strong candidate for a stable **slot-allocation/object-header** layer in these captures.
2. `0x24` is a separate **current type/type-present** layer inside already allocated slots.
3. An inactive/type-zero object can retain nonzero/stale fields; therefore “inactive object == all zero bytes” is false.
4. Current data does not yet contain allocation transitions because the same three slots remained allocated throughout all three captures.

No semantic production `ACTIVE` rule is promoted from this; EFIELD-004 specifically seeks natural allocation/slot-reuse changes.

## Target-pointer evidence

Across EFIELD-002 + EFIELD-003 (7200 frames):

- known P1/P2/P3 retarget events: `6`
- `0x6D` total transitions: `6`
- known-player retargets / all `0x6D` transitions: `6 / 6`
- all known retargets accompanied by `0x6D` transition: `6 / 6`
- observed P1: `0xBE1C`
- observed P2: `0xBEFC`
- observed P3: `0xBFDC`
- directions include P1->P3, P3->P1 and P3->P2

EFIELD-003 supplied the first natural P2 observation. `0x6E` is the low byte of the same U16 field, not an independent semantic field.

### Retarget companion specificity

| Offset | Total changes | Exact on retarget | Retarget support | Event precision | Interpretation |
|---|---:|---:|---:|---:|---|
| `0x28` | 53 | 6 | 1.000 | 0.113208 | sparse retarget pulse/state |
| `0x2D` | 361 | 6 | 1.000 | 0.016620 | broad action reset |
| `0x2E` | 710 | 6 | 1.000 | 0.008451 | broad action/state |
| `0x65` | 247 | 6 | 1.000 | 0.024291 | sparse retarget trigger/substate |
| `0x6D` | 6 | 6 | 1.000 | **1.000000** | target pointer |
| `0x6E` | 6 | 6 | 1.000 | **1.000000** | low byte of target pointer |
| `0x42` | 14546 | 5 | 0.833 | 0.000344 | generic high-frequency dynamics |
| `0x14` | 2054 | 3 | 0.500 | 0.001461 | generic state/animation dynamics |

`0x28` is `00->02` on every observed retarget regardless of target destination, and `0x65` is `00->01/02`; neither maps uniquely to P1/P2/P3. They are retained as trigger/substate candidates, not target identity.

## Movement vs attack separation

Three-run event split:

- clean movement events (coordinate change without same-transition `0x73` attack change): `6231`
- attack-anchor transitions: `772`

Strong movement-associated candidates beyond the coordinate payload itself:

- `0xB9`: movement support `0.442947`, attack support `0.007772`; 2775 total active changes. Values `0..8` show repeated descending/cyclic phase behavior.
- `0xBB`: movement support `0.073343`, attack support `0.001295`; 460 active changes. Dominant chains look like countdowns (`0A->09->...->00`, `0F->0E->...`).
- `0xA2`: movement support `0.144921`, attack support `0.006477`; transitions are frequently decrement-by-one chains.
- coordinate payload bytes `0x09` and `0x0D` are, as expected, strongly movement-selective and should not be mistaken for independent movement flags.

Attack neighborhood:

- `0x73`: 772/772 attack anchor changes by definition; coarse values are mainly `00`, `0A`, `1B`, `0B`, `1E`.
- `0x6C`: support `1.0` against all 772 attack transitions and only 810 active changes overall (~95.3% transition precision relative to the coarse attack anchor).
- observed stable sample mapping strongly suggests `0x6C` refines `0x73`:
  - `6C=E0` -> `73=0A` (`11882` samples)
  - `6C=00` -> `73=00` (`5876`)
  - `6C=40/48/50/58` -> `73=1B`
  - `6C=90` -> `73=0B`
  - `6C=70/78` -> `73=1E`
- `0x72`: attack support `1.0`, but multiple values occur under the same coarse `0x73`, consistent with body/animation-state detail.
- `0x70` and `0x77`: strongly attack-biased (`~0.924` and `~0.899` support respectively) with very low clean-movement support.

Current local hypothesis: `0x73` is a coarse attack-state/family field while `0x6C`, `0x70`, `0x72`, `0x77` encode finer attack/body/animation phases around it. Further event-cycle analysis is required before assigning exact names.

## Important co-change clusters

Stable cross-run pairs/clusters include:

- `0x34 + 0x42`
- `0x04 + 0x9C`
- `0x70 + 0x77`
- `0x6C + 0x73`
- `0x14 + 0x32`
- `0x6D + 0x6E` on all observed retarget transitions
- historical animation cluster `0x2F + 0x71 + 0x73 + 0x33 + 0x6F`

These are correlation observations only.

## EFIELD run ledger

### EFIELD-001-baseline-30s60 — PASS
- `1800` frames, `59.984 Hz`, distinct `1448/1800 = 80.44%`
- read/frame errors `0/0`
- raw: `captures/EFIELD-001-baseline-30s60.jsonl.gz`

### EFIELD-002-natural-diversity-60s60 — PASS
- `3600` frames, `59.993 Hz`, distinct `2848/3600 = 79.11%`
- read/frame errors `0/0`
- `0x6D` retargets `3/3`
- raw: `captures/EFIELD-002-natural-diversity-60s60.jsonl.gz`

### EFIELD-003-passive-retarget-60s60 — PASS
- `3600` frames, `60.001 Hz`, distinct `2817/3600 = 78.25%`
- read/frame errors `0/0`
- `0x6D` retargets `3/3`
- frame 492 slot17 P1->P3
- frame 1827 slot17 P3->P2
- frame 3322 slot19 P3->P1
- raw: `captures/EFIELD-003-passive-retarget-60s60.jsonl.gz`

### EFIELD-004-passive-lifecycle-retarget-60s60 — QUEUED
- `60 s @ 60 Hz`, natural gameplay, raw upload yes, operator gate no
- primary: seek slot-allocation/reuse/lifecycle transitions
- secondary: continue P1/P2/P3 retarget replication and attack/movement atlas
- currently queued behind a separate GEO operator-gated Collector task; EFIELD does not modify that independent line

## Offline analysis outputs

- `results/efield/latest.json` — full atlas analysis
- `results/efield/summary.json` — connector-friendly summary, 3-run
- `results/efield/DECISION.md` — compact decision report, now 3-run
- `results/efield/RUN3_RETARGET.md`
- `results/efield/RETARGET_PRECISION.md`
- `results/efield/LIFECYCLE.md`
- `results/efield/ACTIVE_CLASSIFIER.md`
- `results/efield/TYPE_WIDTH.md`
- `results/efield/MOVE_ATTACK.md`
- `results/efield/STATE_VALUES.md`

Analysis workflow hardening:

- full analyzer race fix: commit `0b62e051d3c0f4b07b8044ae642b3063f82ff013`
- compact decision concurrency also changed to retain runs rather than cancel them
- full analyzer type anchor migrated from legacy `(0x23,2)` to verified `(0x24,1)`

## Current priorities

1. Capture an actual `0x00` allocation transition / slot reuse to test the allocation-header hypothesis.
2. Replicate the `0x24` type-present lifecycle across additional allocated slots and enemy populations.
3. Expand retarget sample beyond six while retaining the clean `0x6D` precision check.
4. Characterize `0xB9/0xBB/A2` against movement start/stop/direction/animation phase.
5. Segment `0x6C/0x70/0x72/0x73/0x77` across attack onset, active, recovery and idle return.
6. Continue type-conditioned field-domain analysis with corrected `0x24` type width.

No Browser/WASM rule and no production-shadow behavior is changed by this atlas.

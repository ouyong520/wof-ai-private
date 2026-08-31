# WinKawaks Enemy Field Atlas (EFIELD)

Research line: `EFIELD-` only. This is a WinKawaks-local discovery atlas, not a Browser/WASM offset contract and not a production-rule specification.

## Scope / invariants

- enemy pool: `0xFFC0BC`
- stride: `0xE0`
- enemy slots: `20`
- read-only; no game-memory writes
- do not modify/advance `WOF-045`
- do not modify T16/T18/T20/T23/T24/D867/D881 production-shadow rules
- WinKawaks offsets remain namespace-local unless separately re-proven elsewhere
- raw Collector frames are normalized CPS byte-lane captures

## Current field atlas

| Offset | Width | Evidence | Current interpretation |
|---|---:|---|---|
| `0x00` | U8 | 9000 frames: slots17/18/19 always `1`, slots0..16 always `0`, zero transitions | **slot-allocation / occupied-object-header candidate**; not current enemy-presence ACTIVE |
| `0x07..0x0A` | s32 candidate | X geometry anchor; dynamic payload mainly `0x08/0x09` in current range | X coordinate / geometry candidate |
| `0x0B..0x0E` | s32 candidate | Y geometry anchor; dynamic payload mainly `0x0C/0x0D` | Y coordinate / geometry candidate |
| `0x19` | U8 | binary `00/FF`; 246/266 same-type episodes constant; 21 within-episode changes | slowly-changing instance/type/variant flag candidate |
| `0x23` | U8 | `0x00` in all 180000 samples | verified padding/high byte for legacy type wrapper |
| `0x24` | **U8** | 31 values; 21 enter + 21 exit edges; actual nonzero type values | **type / current-type-present candidate** |
| `0x28` | U8 | runs2+3 exact on 6/6 retargets but 53 total changes; all retargets `00->02` | sparse retarget-associated pulse/state, not identity |
| `0x2D` | U8 | broad action/reset dynamics; exact on 6/6 retargets | action/reset-state candidate |
| `0x2E` | U8 | broad state dynamics; strong provisional type-present classifier | broad action/state candidate |
| `0x2F` | u32 candidate | very high transition activity | animation/state progression candidate |
| `0x33` | u32 candidate | repeated independent and clustered changes | timer/progress/phase candidate |
| `0x37` | u16 candidate | sparse transitions | sparse timer/state candidate |
| `0x65` | U8 | exact on 6/6 retargets but 247 total changes | retarget-associated trigger/substate; not target identity |
| `0x6C` | **U8** | 810 active changes; every 0x73 attack transition accompanied; `0x6C -> 0x73` deterministic in current sample | **fine attack substate/phase candidate** |
| `0x6D..0x6E` | **U16 BE** | six total changes across runs2+3; all six are known P1/P2/P3 retargets | **strong WinKawaks-local player-target pointer candidate** |
| `0x70` | U8 | strongly attack-biased; `0x70 -> 0x77` deterministic | fine attack/body state candidate |
| `0x71..0x72` | u16 candidate | both bytes dynamic; `0x72` highly attack-coupled | body/animation-state structure; width not yet semantically settled |
| `0x73` | **U8** | five values, 772 changes; following byte `0x74` is zero in all 21847 type-present samples | **coarse attack state/family candidate**; replaces legacy U16 wrapper |
| `0x74` | U8 | constant zero in current type-present corpus | padding/zero neighbor to `0x73` |
| `0x77` | U8 | strongly attack-biased; coarse deterministic projection of `0x70` | attack-neighborhood coarse state candidate |
| `0x81` | historical u16 reference | prior integration treated as non-semantic | unknown/reference only; do not promote |
| `0x9C` | U8 | high-frequency state/counter; strong +1-frame relation with `0x04` | pipelined/high-frequency state candidate |
| `0xA2` | U8 | same-frame equality with X byte `0x08` 95.57%; `0x08[t] == 0xA2[t+1]` 97.80% | **one-frame-delayed X-coordinate mirror/history candidate**, not an independent movement timer |
| `0xB0` | U8 | 249/266 same-type episodes constant; 21 within-episode changes | slowly-changing instance/type/variant property candidate |
| `0xB4` | **U8** | 266/266 same-type episodes constant, zero within-episode changes; next byte `0xB5` always zero | **instance-initialized binary property/variant metadata candidate** |
| `0xB6` | **U8** | 266/266 same-type episodes constant, zero within-episode changes; 18-value domain | **instance-initialized property/variant metadata candidate** |
| `0xB9` | U8 | 2765 changes on movement frames vs only 9 on idle; 9-value cyclic domain | **movement phase/cycle counter candidate** |
| `0xBB` | U8 | 457 changes on movement frames vs only 2 on idle; countdown-like chains | **movement-associated timer/countdown candidate** |

## Verified width corrections

### Type

Across `180000` enemy-object samples:

- `0x23` = `00` for all samples
- `0x24` has `31` distinct byte values
- legacy U16 `0x23..0x24` is always `00XX`

Therefore type is tracked as **`0x24` U8**. The bridge analyzer now uses `type_candidate=(0x24,1)`.

### Attack

Across `21847` type-present samples:

- `0x73` has five values: mainly `0A`, `00`, `1B`, `0B`, `1E`
- `0x73` changes `772` times
- `0x74` is `00` for every sample and changes zero times
- U16@`0x73` therefore adds only a constant low zero byte

The atlas and bridge analyzer now use **`0x73` U8** as the coarse attack anchor.

### Target

`0x6D..0x6E` must remain **U16 BE**. Observed values are exactly:

- P1 `0xBE1C`
- P2 `0xBEFC`
- P3 `0xBFDC`

## Allocation vs type-present lifecycle

Across 9000 frames / 180000 enemy-object samples:

- slots0..16: `0x00 == 0` for all `153000` samples
- slots17..19: `0x00 == 1` for all `27000` samples
- within those allocated slots, `0x24 != 0` for `21847` samples and `0x24 == 0` for `5153`
- `0x00` changed zero times
- `0x24` zero->nonzero edges: `21`
- `0x24` nonzero->zero edges: `21`
- whole-object all-zero transitions: none

Current model has at least two layers:

1. `0x00`: stable allocation/object-header layer in current corpus.
2. `0x24`: current type/type-present layer inside allocated slots.

Inactive/type-zero objects can retain nonzero stale state; “inactive == all zero bytes” is false. No semantic production ACTIVE rule is promoted.

## Target-pointer evidence

Across EFIELD-002 + EFIELD-003 (`7200` frames):

- `0x6D` total transitions: `6`
- known P1/P2/P3 retargets: `6`
- all `0x6D` transitions are known retargets: `6/6`
- all known retargets changed `0x6D`: `6/6`
- local sample event precision: `1.0`
- directions include P1->P3, P3->P1 and P3->P2

EFIELD-003 supplied the first natural P2 observation.

Retarget companion specificity:

| Offset | Total changes | Exact on retarget | Event precision | Interpretation |
|---|---:|---:|---:|---|
| `0x28` | 53 | 6 | 0.113208 | sparse retarget pulse |
| `0x2D` | 361 | 6 | 0.016620 | broad action reset |
| `0x2E` | 710 | 6 | 0.008451 | broad state |
| `0x65` | 247 | 6 | 0.024291 | retarget substate/trigger |
| `0x6D` | 6 | 6 | **1.000000** | target U16 field |
| `0x6E` | 6 | 6 | **1.000000** | low byte of same U16 target |
| `0x42` | 14546 | 5 | 0.000344 | generic high-frequency field |
| `0x14` | 2054 | 3 | 0.001461 | generic state/animation field |

This remains WinKawaks-local discovery only.

## Attack hierarchy and cycle

The attack neighborhood is now structured rather than merely correlated.

Deterministic/current-sample relations:

- H(`0x73 | 0x6C`) = `0`: each `0x6C` fine state maps to exactly one coarse `0x73` family.
- H(`0x77 | 0x70`) = `0`: each `0x70` fine state maps to exactly one `0x77` coarse state.
- `0x72 -> 0x73` is near-deterministic but not perfect.

Representative mappings:

- `6C=E0 -> 73=0A` (`11882` samples)
- `6C=40/48/50/58 -> 73=1B`
- `6C=90 -> 73=0B`
- `6C=70/78 -> 73=1E`
- `70=A0 -> 77=0C` (`10640`)
- `70=80/10/58/28 -> 77=0B`
- `70=D8 -> 77=14`
- `70=F8 -> 77=0A`

Attack-cycle mining found `271` contiguous `0x73 != 0` episodes:

- median duration `31` frames
- mean `58.934`
- maximum `345`

Dominant joint phase states `(6C,70,72,73,77)` include:

- `E0,A0,D8,0A,0C`: `10640` samples
- `40,00,E8,1B,00`: `2660`
- `E0,00,38,0A,00`: `1242`

The most frequent cross-family transition is:

`40,00,E8,1B,00 -> E0,A0,D8,0A,0C` (`123`)

with the reverse transition observed `113` times. This supports a repeatable multi-field attack phase graph rather than incidental cochange.

## Movement subsystem

Clean movement vs attack separation originally showed:

- movement events: `6231`
- attack-anchor transitions: `772`

The movement-cycle pass then found `2163` contiguous movement bouts:

- median duration `2` frames
- mean `2.897`
- max `18`

Key field-change class counts:

- `0xB9`: moving `2765`, idle `9`
- `0xBB`: moving `457`, idle `2`
- `0xA2`: moving `898`, idle `26`
- `0x28`: moving `10`, idle `58`
- `0x2D`: moving `94`, idle `305`
- `0x2E`: moving `222`, idle `526`
- `0x9C`: moving `5327`, idle `348`

`0xB9` and `0xBB` generally do **not** toggle exactly at movement start/stop; they continue/advance during movement. This argues for phase/timer semantics rather than boolean movement flags.

### Lagged coordinate mirror

For `0x08` (X payload byte) vs `0xA2`:

- A2[t-3]: equality `0.887378`
- A2[t-2]: `0.901193`
- A2[t-1]: `0.922816`
- A2[t]: `0.955692`
- **A2[t+1]: `0.977954`**
- A2[t+2]: `0.955530`
- A2[t+3]: `0.923218`

Thus `0xA2` is best treated as a one-frame-delayed/latched X-coordinate mirror or history byte, not an independent movement counter.

For `0x04` vs `0x9C`, equality similarly peaks at +1 frame (`0.835136`) rather than same frame (`0.662288`), indicating a likely pipelined state relationship rather than aliasing.

## Instance-initialized metadata candidates

Episodes are defined as a contiguous nonzero constant `0x24` type in one slot. Across `266` such episodes:

| Offset | Constant episodes | Within-episode changes | Interpretation |
|---|---:|---:|---|
| `0xB4` | **266/266** | **0** | strong instance-initialized binary metadata/variant candidate |
| `0xB6` | **266/266** | **0** | strong instance-initialized multi-value metadata/variant candidate |
| `0xB0` | 249/266 | 21 | slowly-changing instance/type property candidate |
| `0x19` | 246/266 | 21 | slowly-changing binary type/variant property candidate |
| `0x28` | 236/266 | 67 | runtime state/pulse, not static metadata |
| `0x65` | 232/266 | 243 | runtime state/substate |
| `0xB9` | 59/266 | 2601 | runtime movement phase |
| `0xBB` | 194/266 | 332 | runtime movement timer |

The earlier apparent `B4/B6` lifecycle-exit correlation is now interpreted as an episode-boundary effect: these fields are constant inside a type episode but can be reinitialized when a new enemy instance/type episode begins.

## EFIELD run ledger

### EFIELD-001-baseline-30s60 — PASS
- 1800 frames @ ~59.984Hz
- distinct 1448/1800 = 80.44%
- read/frame errors 0/0
- raw `captures/EFIELD-001-baseline-30s60.jsonl.gz`

### EFIELD-002-natural-diversity-60s60 — PASS
- 3600 frames @ ~59.993Hz
- distinct 2848/3600 = 79.11%
- retargets 3/3
- raw `captures/EFIELD-002-natural-diversity-60s60.jsonl.gz`

### EFIELD-003-passive-retarget-60s60 — PASS
- 3600 frames @ 60.001Hz
- distinct 2817/3600 = 78.25%
- frame492 slot17 P1->P3
- frame1827 slot17 P3->P2
- frame3322 slot19 P3->P1
- raw `captures/EFIELD-003-passive-retarget-60s60.jsonl.gz`

### EFIELD-004-passive-lifecycle-retarget-60s60 — QUEUED
- 60s @ 60Hz natural gameplay
- raw upload yes
- operator gate no
- primary: seek real slot-allocation/reuse edges
- secondary: additional retarget and attack/movement replication
- currently serialized behind independent GEO-0005, which remains `WAITING_FOR_OPERATOR`; EFIELD does not modify the GEO task

## Offline analysis outputs

- `results/efield/latest.json`
- `results/efield/summary.json`
- `results/efield/DECISION.md`
- `results/efield/RUN3_RETARGET.md`
- `results/efield/RETARGET_PRECISION.md`
- `results/efield/LIFECYCLE.md`
- `results/efield/ACTIVE_CLASSIFIER.md`
- `results/efield/TYPE_WIDTH.md`
- `results/efield/MOVE_ATTACK.md`
- `results/efield/STATE_VALUES.md`
- `results/efield/TYPE_FINGERPRINT.md`
- `results/efield/MIRROR_STATIC.md`
- `results/efield/LAG_MIRRORS.md`
- `results/efield/ATTACK_CYCLE.md`
- `results/efield/INSTANCE_PROPERTIES.md`
- `results/efield/WIDTH_REFINEMENT.md`
- `results/efield/MOVEMENT_CYCLE.md`

Analysis workflow hardening/corrections:

- analyzer concurrent-push race fixed; result pushes rebase before push and no longer cancel newer queued analyses
- compact decision workflow also retains concurrent runs
- analyzer type anchor corrected to `(0x24,1)`
- analyzer attack anchor corrected to `(0x73,1)`

## Current priorities

1. Capture an actual `0x00` allocation transition / slot reuse; current three-run corpus never changed allocation.
2. Expand `0x6D` retarget sample beyond six while preserving exact event precision.
3. Determine whether `0xB4/B6` encode instance identity, variant/class metadata, facing/spawn attributes, or another initialization-time property.
4. Convert the `0x6C/70/72/73/77` attack graph into onset/active/recovery/idle-return phase semantics.
5. Characterize `0xB9/BB` against velocity sign, step cadence and movement animation cycles.
6. Continue type-conditioned analysis while controlling for position, instance and stage/time confounding.

No Browser/WASM rule and no production-shadow behavior is changed by this atlas.

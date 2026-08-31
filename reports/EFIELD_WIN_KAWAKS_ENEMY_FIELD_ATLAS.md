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

## Current evidence baseline

| WinKawaks normalized offset | Prior label | Width candidate | Dynamic evidence | Current atlas status |
|---|---|---:|---|---|
| `0x07` | enemyX | s32 | high-cardinality movement-coupled dynamics | high-value dynamic / geometry candidate |
| `0x0B` | enemyY | s32 | high-cardinality movement-coupled dynamics | high-value dynamic / geometry candidate |
| `0x15` | frameEnd | u32 | historically static in bounded run | constant/stage-specific candidate |
| `0x23` | type | u16 | repeated type changes across active slots | high-value identity/type candidate |
| `0x28` | unknown | u8 | EFIELD-002+003: exact change on 6/6 known retargets, but 53 total changes; every retarget observed `0x00 -> 0x02` | sparse retarget-associated trigger/state-pulse candidate; not target identity |
| `0x2D` | action2A | u8 | 361 changes over runs 2+3; exact on 6/6 retargets, usually resets to zero | broad action/state reset companion |
| `0x2E` | b2B | u8 | 710 changes over runs 2+3; exact on 6/6 retargets | broad state/action companion |
| `0x2F` | next | u32 | very high transition activity | very high-value animation/state progression candidate |
| `0x33` | value30 | u32 | strong repeated dynamic cluster; often independently changes | very high-value timer/progress/phase candidate |
| `0x37` | timer34 | u16 | sparse transitions | medium/high-value sparse transition candidate |
| `0x65` | unknown | u8 | EFIELD-002+003: exact on 6/6 retargets but 247 total changes; retarget values `0x00 -> 0x01/0x02` | sparse retarget-associated trigger/substate candidate; not target identity |
| `0x6D` | selectedPlayerLow16 | u16 | EFIELD-002+003: 6 total changes, all 6 known P1/P2/P3 retargets; all known retargets changed it | **strong dynamically supported WinKawaks-local 16-bit player-target pointer candidate** |
| `0x6F` | payload6C | u16 | repeated state/body cluster dynamics | high-value state payload candidate |
| `0x71` | body | u16 | repeated low-cardinality body/animation dynamics | high-value animation/body-state candidate |
| `0x73` | attack | u16 | strong repeated attack-neighborhood cochange | high-value attack-cycle candidate |
| `0x81` | raw target selector reference | u16 | historical integration explicitly treated as non-semantic | unknown/reference only; do not promote |
| `0x9C` | state99 | u8 | persistent top dynamic; strong pair with `0x04` | very high-frequency state/counter candidate; semantics unknown |

`0x6D..0x6E` is a two-byte big-endian field. The byte-level `0x6E` changes on exactly the same six retarget transitions because it is the low byte of that local U16 value; it is not a separate semantic field.

## Target-pointer evidence

Across EFIELD-002 + EFIELD-003 (7200 frames total):

- known P1/P2/P3 retarget events: `6`
- `0x6D` total transitions: `6`
- `0x6D` transitions that are known-player retargets: `6 / 6`
- known-player retargets accompanied by `0x6D` transition: `6 / 6`
- `0x6D` event precision in this sample: `1.0`
- `0x6E` byte-level event precision in this sample: `1.0`
- observed target values:
  - P1: `0xBE1C`
  - P2: `0xBEFC`
  - P3: `0xBFDC`

Observed retarget directions across runs 2+3 include P1->P3, P3->P1 and P3->P2. EFIELD-003 supplied the first natural P2 target observation (`0xBEFC`).

This is strong WinKawaks-local discovery evidence only. It is not Browser/WASM proof and is not production promotion.

### Retarget companion specificity

Combined EFIELD-002 + EFIELD-003 exact same-transition statistics:

| Offset | Total changes | Exact on retarget | Retarget support | Event precision | Interpretation |
|---|---:|---:|---:|---:|---|
| `0x28` | 53 | 6 | 1.000 | 0.113208 | sparse retarget-associated pulse/state |
| `0x2D` | 361 | 6 | 1.000 | 0.016620 | broad action reset/state companion |
| `0x2E` | 710 | 6 | 1.000 | 0.008451 | broad action/state companion |
| `0x65` | 247 | 6 | 1.000 | 0.024291 | sparse retarget-associated trigger/substate |
| `0x6D` | 6 | 6 | 1.000 | **1.000000** | target-pointer field candidate |
| `0x6E` | 6 | 6 | 1.000 | **1.000000** | low byte of target-pointer field |
| `0x42` | 14546 | 5 | 0.833 | 0.000344 | generic high-frequency dynamic field; demoted as retarget-specific candidate |
| `0x14` | 2054 | 3 | 0.500 | 0.001461 | generic state/animation companion; demoted as retarget-specific candidate |

Important value-pattern evidence:

- `0x28` was `0x00 -> 0x02` on all six observed retargets despite different target destinations. This argues for a pulse/state transition rather than target identity.
- `0x65` was `0x00 -> 0x01` or `0x02`; the value does not map uniquely to P1/P2/P3.
- `0x2D` usually resets to zero at retarget.
- `0x42` and `0x14` have large background change counts and therefore are not useful target-specific fields despite occasional same-frame coincidence.

## Important co-change clusters

Historical observations:

1. `0x2F + 0x71 + 0x73 + 0x33 + 0x6F` changed together in slot 17.
2. `0x2F + 0x71 + 0x33 + 0x37 + 0x6F` changed together in slot 18.
3. `0x2F + 0x2D + 0x2E + 0x71 + 0x73 + 0x33 + 0x6F` changed together in slot 19.
4. `0x23 + 0x2F + 0x9C + 0x2E + 0x33 + 0x07 + 0x0B` changed together during a lifecycle/type-like transition.
5. `0x33` repeatedly changed alone, supporting a timer/progress interpretation rather than a simple alias of the larger state cluster.

Stable cross-run pairs include:

- `0x34 + 0x42`
- `0x04 + 0x9C`
- `0x70 + 0x77`
- `0x6C + 0x73`
- `0x14 + 0x32`
- `0x6D + 0x6E` on all six observed retarget transitions

These remain correlation observations only.

## EFIELD run ledger

### EFIELD-001-baseline-30s60 — PASS

- requested: `30 s @ 60 Hz`
- collected: `1800` frames
- achieved rate: `59.984 Hz`
- distinct raw frames: `1448 / 1800` = `80.44%`
- read errors / frame-size errors: `0 / 0`
- changing offsets: `80 / 224`
- global constants: `106`
- temporal-stable cross-slot offsets: `38`
- activity heuristic enter/exit: `0 / 0`
- target candidate `0x6D` transitions: `0`
- raw: `captures/EFIELD-001-baseline-30s60.jsonl.gz`

### EFIELD-002-natural-diversity-60s60 — PASS

- requested: `60 s @ 60 Hz`
- collected: `3600` frames
- achieved rate: `59.993 Hz`
- distinct raw frames: `2848 / 3600` = `79.11%`
- read errors / frame-size errors: `0 / 0`
- changing offsets: `80 / 224`
- global constants: `107`
- temporal-stable cross-slot offsets: `37`
- activity heuristic enter/exit: `0 / 0`
- `0x6D` transitions: `3`; known P1/P2/P3 retargets: `3`
- transitions: P3->P1 `1`, P1->P3 `2`
- raw: `captures/EFIELD-002-natural-diversity-60s60.jsonl.gz`

### EFIELD-003-passive-retarget-60s60 — PASS

- requested: `60 s @ 60 Hz`
- collected: `3600` frames
- achieved rate: `60.001 Hz`
- distinct raw frames: `2817 / 3600` = `78.25%`
- state change observed: yes
- read errors / frame-size errors: `0 / 0`
- `0x6D` transitions: `3`; known P1/P2/P3 retargets: `3`
- transitions:
  - frame 492 slot 17: P1 -> P3
  - frame 1827 slot 17: P3 -> P2
  - frame 3322 slot 19: P3 -> P1
- first natural P2 value observed: `0xBEFC`
- raw: `captures/EFIELD-003-passive-retarget-60s60.jsonl.gz`
- compressed bytes: `485302`
- compressed SHA256: `d3e8fae327c7dc9752e2e8f5e8824512cea4a53970d49bc2b7338fa8de4bc8df`
- original JSONL SHA256: `765b754b21c043ab231cfbcd9d1adbb2f6f6c7661340978151531dcf67828fc3`

### EFIELD-004-passive-lifecycle-retarget-60s60 — QUEUED

- action: `capture_raw_burst`
- requested: `60 s @ 60 Hz`
- operator gate: no
- raw upload: yes
- scene: natural gameplay
- purpose:
  - continue the full `0x00..0xDF` atlas
  - expand natural P1/P2/P3 retarget sample
  - validate `0x6D..0x6E` against further target switches
  - prioritize lifecycle/slot-reuse/ACTIVE edges
  - discriminate sparse `0x28/0x65` retarget companions from general action/state behavior

## Analysis infrastructure

The bridge contains offline, read-only EFIELD analyzers. They consume `captures/EFIELD-*.jsonl.gz` and never attach to WinKawaks for writes.

Current outputs include:

- `results/efield/latest.json` — full atlas analysis
- `results/efield/summary.json` — connector-oriented summary; currently covers 3 EFIELD runs
- `results/efield/DECISION.md` — compact decision report
- `results/efield/RUN3_RETARGET.md` — EFIELD-003 exact/lag retarget discriminator
- `results/efield/RETARGET_PRECISION.md` — cross-run retarget specificity/value-transition analysis
- `results/efield/LIFECYCLE.md` — passive lifecycle edge discriminator when generated

The EFIELD analysis workflow was hardened after EFIELD-003 exposed a concurrent-push race: `cancel-in-progress` was disabled and the result push now rebases before pushing. Fix commit: `0b62e051d3c0f4b07b8044ae642b3063f82ff013`.

## Coverage gaps / current priorities

1. **Lifecycle / ACTIVE**: the old occupancy heuristic reported 0/0 enter/exit despite real type/state churn; a better field-level lifecycle discriminator is now being mined from type zero↔nonzero, slot reuse, zero edges and background precision.
2. **Retarget replication**: `0x6D..0x6E` is already very strong locally, but additional natural switches remain useful for broader enemy types and slots.
3. **Sparse retarget companions**: determine what `0x28` and `0x65` actually mean; current evidence favors trigger/substate rather than target identity.
4. **Movement vs attack**: separate generic high-frequency clusters (`0x34/0x42`, `0x04/0x9C`) from discrete animation/attack lifecycle fields.
5. **Type-conditioned behavior**: expand per-type constants and dynamic domains across more enemy populations/stages.

## Current automatic decision

The target identity field is no longer the bottleneck of this local research line. EFIELD-004 therefore keeps passive retarget replication but shifts primary discovery weight toward lifecycle/ACTIVE and slot reuse. No Browser/WASM rule or production-shadow behavior changes as a consequence of this atlas.

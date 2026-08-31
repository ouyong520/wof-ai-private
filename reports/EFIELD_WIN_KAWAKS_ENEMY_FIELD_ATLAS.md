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
- Collector raw frames are normalized CPS byte-lane captures; semantic field labels below remain WinKawaks hypotheses, even where historical Browser references helped seed discovery

## Current evidence baseline

Historical Collector evidence establishes a set of WinKawaks-local candidate fields. The EFIELD line treats their names as prior semantic hypotheses and uses new raw bursts to independently characterize dynamics.

| WinKawaks normalized offset | Prior label | Width candidate | Dynamic evidence | Current atlas status |
|---|---|---:|---|---|
| `0x07` | enemyX | s32 | 103 distinct values in historical dynamic run; EFIELD anchors show heavy movement coupling | high-value dynamic / geometry candidate |
| `0x0B` | enemyY | s32 | 199 distinct values historically; EFIELD anchors show heavy movement coupling | high-value dynamic / geometry candidate |
| `0x15` | frameEnd | u32 | 1 distinct value in prior run | constant/stage-specific candidate; needs broader type/stage coverage |
| `0x23` | type | u16 | 69 changes in EFIELD-001 and 90 in EFIELD-002, across 3 changing slots | high-value identity/type candidate |
| `0x2D` | action2A | u8 | 104 changes in EFIELD-001; 189 in EFIELD-002; strongly paired with `0x2E` around state changes | high-value state/action candidate |
| `0x2E` | b2B | u8 | 196 changes in EFIELD-001; 358 in EFIELD-002; low-cardinality state/flag behavior | high-value state/action candidate |
| `0x2F` | next | u32 | 579 anchor changes in EFIELD-001; 1054 in EFIELD-002 | very high-value animation/state progression candidate |
| `0x33` | value30 | u32 | EFIELD U32 candidate remains strong; `0x34` is one of the two strongest U8 dynamics in both runs | very high-value timer/progress/phase cluster candidate |
| `0x37` | timer34 | u16 | sparse historical transitions | medium/high-value sparse transition candidate |
| `0x6D` | selectedPlayerLow16 | u16 | EFIELD-002 observed 3 natural transitions; all 3 were known P1/P3 retargets; `0x6D+0x6E` cochanged on all 3 | dynamically supported target-pointer candidate; sample still small |
| `0x6F` | payload6C | u16 | 231 anchor changes in EFIELD-001; 542 in EFIELD-002 | high-value state payload candidate |
| `0x71` | body | u16 | U16 `0x71` remains a top low-cardinality dynamic candidate; body anchor 232/574 events | high-value animation/body-state candidate |
| `0x73` | attack | u16 | attack anchor 172/436 events; `0x6C+0x73` strong cochange in both runs | high-value attack-cycle candidate |
| `0x81` | raw target selector reference | u16 | prior integration explicitly treated as non-semantic | unknown/reference only; do not promote |
| `0x9C` | state99 | u8 | top-5 U8 dynamic in both EFIELD runs; strongly cochanges with `0x04` | very high-frequency state/counter candidate; exact semantics unknown |

## Important co-change clusters

Historical observations:

1. `0x2F(next) + 0x71(body) + 0x73(attack) + 0x33(value30) + 0x6F(payload6C)` changed together in slot 17.
2. `0x2F + 0x71 + 0x33 + 0x37(timer34) + 0x6F` changed together in slot 18.
3. `0x2F + 0x2D(action2A) + 0x2E(b2B) + 0x71 + 0x73 + 0x33 + 0x6F` changed together in slot 19.
4. `0x23(type) + 0x2F + 0x9C(state99) + 0x2E + 0x33 + 0x07 + 0x0B` changed together during a slot/type/lifecycle-like transition.
5. `0x33(value30)` repeatedly changed alone across slots 17/18/19, making it a prime independent timer/progress candidate rather than merely an alias of the larger state cluster.

EFIELD-001/002 systematic scan adds these stable same-frame pairs/clusters:

- `0x34 + 0x42`: Jaccard `0.986635` / `0.977685` in runs 1/2; dominant dynamic pair.
- `0x04 + 0x9C`: Jaccard `0.959596` / `0.958707`; very strong high-frequency pair.
- `0x70 + 0x77`: Jaccard `0.985222` / `0.985597`; strong low-cardinality state/body neighborhood pair.
- `0x6C + 0x73`: Jaccard `0.952381` / `0.953995`; strong attack-neighborhood pair.
- `0x14 + 0x32`: Jaccard `0.964211` / `0.951357`; strong repeated pair of currently unknown semantics.
- EFIELD-002 only: `0x6D + 0x6E` Jaccard `1.0`, shared frames `3`, matching the three observed target-pointer transitions and supporting the 16-bit width hypothesis.

These are correlation observations only; no production rule is implied.

## EFIELD run ledger

### EFIELD-001-baseline-30s60 — PASS

- action: `capture_raw_burst`
- requested: `30 s @ 60 Hz`
- collected: `1800` frames
- achieved rate: `59.984 Hz`
- bytes/frame: `5152` = 3 player objects + 20 enemy objects
- distinct raw frames: `1448 / 1800` = `80.44%`
- state change observed: yes
- read errors: `0`
- frame-size errors: `0`
- mapping discovered fresh for this session: `xor3`
- raw artifact: `wof-winkawaks-bridge/captures/EFIELD-001-baseline-30s60.jsonl.gz`
- compressed bytes: `251330`
- compressed SHA256: `66f8d219a26402d41736b42152759076d0222f9e851c1b33beaaf87d2f17e524`
- original JSONL SHA256: `43bf549d2cbb047d9d34febf6b6d8b48d2826bf27278331fd14858122a87f3a4`

Systematic enemy scan:

- changing offsets: `80 / 224`
- global constants: `106`
- temporal-stable but cross-slot-diverse offsets: `38`
- activity heuristic enter/exit: `0 / 0`
- target candidate `0x6D` transitions: `0`
- top U8 dynamics: `0x42`, `0x34`, `0xD3`, `0x9C`, `0x04`
- type-anchor changes: `69`
- attack-anchor changes: `172`
- body-anchor changes: `232`

Interpretation: natural gameplay gives high frame diversity, but this particular interval contained no observable target transition and no activity-heuristic enter/exit transition.

### EFIELD-002-natural-diversity-60s60 — PASS

- action: `capture_raw_burst`
- requested: `60 s @ 60 Hz`
- collected: `3600` frames
- achieved rate: `59.993 Hz`
- distinct raw frames: `2848 / 3600` = `79.11%`
- state change observed: yes
- read errors: `0`
- frame-size errors: `0`
- same fresh WinKawaks session: PID `7128`, RAM base `0xB0CFDFC`, mapping `xor3`
- raw artifact: `wof-winkawaks-bridge/captures/EFIELD-002-natural-diversity-60s60.jsonl.gz`
- compressed bytes: `484189`
- compressed SHA256: `7616be353b9bc535717c5dff38d2d8c97c698246ac5bc9008df24ea921b6c58b`
- original JSONL SHA256: `282e1b0d8363dcb3aa8044fd35f22dccfb2ba5bde442eac7d5984f9f625c38e5`

Systematic enemy scan:

- changing offsets: `80 / 224`
- global constants: `107`
- temporal-stable but cross-slot-diverse offsets: `37`
- activity heuristic enter/exit: `0 / 0`
- top U8 dynamics: `0x34`, `0x42`, `0xD3`, `0x04`, `0x9C`
- type-anchor changes: `90`
- action `0x2D` anchor changes: `189`
- state `0x2E` anchor changes: `358`
- next `0x2F` anchor changes: `1054`
- value `0x33` anchor changes: `5604`
- payload `0x6F` anchor changes: `542`
- body `0x71` anchor changes: `574`
- attack `0x73` anchor changes: `436`
- state `0x9C` anchor changes: `2395`

### EFIELD-002 retarget breakthrough

`0x6D` changed three times in EFIELD-002, across three changing enemy slots, and every observed transition was between a known player-pointer low16 value:

- `P1 0xBE1C -> P3 0xBFDC`: `2` transitions
- `P3 0xBFDC -> P1 0xBE1C`: `1` transition
- known-player retargets / all `0x6D` transitions: `3 / 3`
- no P2 target value was observed in this run
- `0x6D + 0x6E` same-frame cochange: Jaccard `1.0`, shared frames `3`

Within the same slot and a `±2` transition-frame window, all three retarget events were accompanied by changes at each of these offsets:

- `0x28`
- `0x2D`
- `0x2E`
- `0x65`
- `0x6D`
- `0x6E`
- `0x42`
- `0x14`

Current interpretation:

- `0x6D..0x6E` is now dynamically supported as a WinKawaks-local 16-bit target-pointer candidate rather than merely a static prior hypothesis.
- The other six offsets are **retarget-associated candidates only**. With `n=3`, their association can easily be caused by ordinary AI/state transitions around a target change.
- Do not infer that the other six are target fields; EFIELD-003 must increase the retarget sample and separate exact same-transition changes from lagged `±1/±2` changes.

### EFIELD-003-passive-retarget-60s60 — QUEUED

- action: `capture_raw_burst`
- requested: `60 s @ 60 Hz`
- raw upload: yes
- operator gate: no
- scene: natural gameplay only
- purpose: expand natural retarget sample while continuing the full enemy `0x00..0xDF` atlas
- priority candidates around retarget: `0x28`, `0x2D`, `0x2E`, `0x65`, `0x6D..0x6E`, `0x42`, `0x14`
- key analysis requirement: distinguish exact same-transition correlation from lagged `±1/±2` correlation

## Automatic raw analysis route

The bridge contains dedicated discovery-only EFIELD analyzers and compact reporting paths. They consume `captures/EFIELD-*.jsonl.gz` offline and do not attach to WinKawaks or write game RAM.

For enemy objects the current route computes, among other things:

- U8 change-rate/value-domain/entropy ranking over `0x00..0xDF`
- selected U16/U32 big-endian width candidates
- zero↔nonzero edge counts
- changed-slot coverage
- same-frame co-change clusters/pairs
- anchor event windows with `±2`-frame lag
- target-pointer transition values and known P1/P2/P3 retarget counts
- type-conditioned distributions
- multi-run consensus ranking
- compact connector-friendly decision report at `results/efield/DECISION.md`

This is a consumer-side discovery aid only; it does not promote EFIELD candidates to Browser/WASM or production rules.

## Coverage gaps the EFIELD line must resolve

- determine whether the currently changing 3/20 slots reflect scene occupancy versus a structural ACTIVE mask
- ACTIVE enter/exit boundaries and slot reuse signatures; current heuristic observed `0/0` in both runs
- movement-only transitions versus idle
- attack-cycle onset/active/recovery correlations
- increase retarget sample beyond the current `n=3`
- seek natural P2 target observations in addition to P1/P3
- determine whether `0x28`, `0x2D`, `0x2E`, `0x65`, `0x42`, `0x14` are causal/semantic retarget companions or merely nearby AI-state activity
- type-conditioned constants and stage-local constants
- high-value unknown offsets such as the stable dynamic pairs `0x34+0x42`, `0x14+0x32`, `0x04+0x9C`

## Current automatic decision point

The first decisive target-transition evidence now exists, so EFIELD-003 is a passive retarget expansion rather than a generic baseline.

After EFIELD-003:

- compare `0x6D..0x6E` transitions against exact same-frame and lagged changes of the six associated candidates;
- if additional known-player retargets occur, rank candidates by retarget-specific precision/support rather than global dynamic rate;
- if P2 appears naturally, verify that the candidate value becomes `0xBEFC` without introducing a new mapping hypothesis;
- if retarget sample remains sparse but natural diversity remains high, continue another passive 60-second burst before asking for staged play;
- keep lifecycle/ACTIVE as a separate unresolved subproblem because the current activity heuristic produced no enter/exit events despite strong type/state dynamics.

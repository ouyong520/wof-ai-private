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
| `0x07` | enemyX | s32 | 103 distinct values in 510-sample dynamic run | high-value dynamic / geometry candidate |
| `0x0B` | enemyY | s32 | 199 distinct values | high-value dynamic / geometry candidate |
| `0x15` | frameEnd | u32 | 1 distinct value in prior run | constant/stage-specific candidate; needs broader type/stage coverage |
| `0x23` | type | u16 | 6 distinct values; changed with slot lifecycle/type transition | high-value identity/type candidate |
| `0x2D` | action2A | u8 | 6 distinct values; co-changed with state cluster | high-value state/action candidate |
| `0x2E` | b2B | u8 | 7 distinct values; co-changed with action/state cluster | high-value state/action candidate |
| `0x2F` | next | u32 | 131 distinct values; frequent co-change with body/attack/value30/payload6C | very high-value animation/state progression candidate |
| `0x33` | value30 | u32 | 44 distinct values; changes very frequently, often alone | very high-value timer/progress/phase candidate |
| `0x37` | timer34 | u16 | 2 distinct values in prior dynamic run | medium/high-value sparse transition candidate |
| `0x6D` | selectedPlayerLow16 | u16 | constant in prior run | target-pointer hypothesis; retarget coverage missing |
| `0x6F` | payload6C | u16 | 10 distinct values; co-changes with body/attack/next | high-value state payload candidate |
| `0x71` | body | u16 | 15 distinct values; co-changes with next/attack/payload | high-value animation/body-state candidate |
| `0x73` | attack | u16 | 4 distinct values; co-changes with body/next/payload | high-value attack-cycle candidate |
| `0x81` | raw target selector reference | u16 | constant in prior run; prior integration explicitly treated as non-semantic | unknown/reference only; do not promote |
| `0x9C` | state99 | u8 | 177 distinct values | very high-frequency state/counter candidate; exact semantics unknown |

## Important co-change clusters already observed

1. `0x2F(next) + 0x71(body) + 0x73(attack) + 0x33(value30) + 0x6F(payload6C)` changed together in slot 17.
2. `0x2F + 0x71 + 0x33 + 0x37(timer34) + 0x6F` changed together in slot 18.
3. `0x2F + 0x2D(action2A) + 0x2E(b2B) + 0x71 + 0x73 + 0x33 + 0x6F` changed together in slot 19.
4. `0x23(type) + 0x2F + 0x9C(state99) + 0x2E + 0x33 + 0x07 + 0x0B` changed together during a slot/type/lifecycle transition.
5. `0x33(value30)` repeatedly changed alone across slots 17/18/19, making it a prime independent timer/progress candidate rather than merely an alias of the larger state cluster.

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

Interpretation: natural gameplay already gives high frame diversity, so the EFIELD line should keep using passive collection rather than operator-staged scenes. EFIELD-001 proves the acquisition route is suitable for a systematic atlas, but its compact Collector result is not itself a per-offset field analysis; per-offset claims remain limited to evidence actually analyzed.

### EFIELD-002-natural-diversity-60s60 — QUEUED

- action: `capture_raw_burst`
- requested: `60 s @ 60 Hz`
- raw upload: yes
- operator gate: no
- purpose: broaden passive slot lifecycle, movement, attack-cycle, type-diversity and spontaneous retarget coverage

Reason for escalation: EFIELD-001 had `80.44%` distinct raw frames, so occupancy/state diversity is good enough to spend the next full 60-second budget on broader natural coverage rather than repeating the same 30-second baseline.

## Coverage gaps the EFIELD line must resolve

- full `0x00..0xDF` per-byte/per-word/per-dword change-rate atlas across all 20 slots
- constants vs stage-local constants vs type-local constants
- ACTIVE enter/exit boundaries and slot reuse signatures
- movement-only transitions versus idle
- attack-cycle onset/active/recovery correlations
- actual target/retarget transitions (prior target fields remained constant)
- type-conditioned distributions and U8/U16/U32 width/value-range candidates
- co-change graph / lagged correlations (same-frame and +/- few frames)
- high-value unknown offsets not present in the prior named field set

## Automatic next decision

After EFIELD-002 completes:

- if natural retarget occurs: prioritize offsets that change with `0x6D` target-pointer transitions and separate same-frame versus lagged changes;
- if lifecycle/type diversity increases: rank ACTIVE enter/exit and type-local constant candidates;
- if attack transitions are abundant: split attack onset / active / recovery candidate clusters from ordinary movement changes;
- if target remains constant but overall diversity stays high: continue passive collection rather than asking the operator to force retarget;
- only request a staged scene after repeated passive runs fail to cover a specific high-value transition.

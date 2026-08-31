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

Interpretation: natural gameplay gives high frame diversity, so the EFIELD line should keep using passive collection rather than operator-staged scenes.

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

Interpretation: doubling the passive window preserved essentially the same high raw-frame diversity (`79.11%` versus `80.44%`), so natural gameplay is providing sustained dynamic coverage rather than a short transient burst.

## Automatic raw analysis route

The bridge now contains a separate discovery-only `RAWMINE` consumer analyzer. Its workflow watches `captures/EFIELD-*.jsonl.gz` and generates a compact text/JSON report without attaching to WinKawaks or writing game RAM.

For enemy objects it computes, among other things:

- U8 change-rate/value-domain/entropy ranking
- U16/U32 big-endian width candidates
- zero↔nonzero edge counts
- changed-slot coverage
- same-frame co-change clusters/pairs
- event windows with ±2-frame lag
- multi-run consensus ranking

This is a consumer-side discovery aid only; it does not promote EFIELD candidates to Browser/WASM or production rules.

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

## Current automatic decision point

`EFIELD-001` and `EFIELD-002` are both complete. Do not blindly enqueue a third generic burst before consuming the automatic RAWMINE report for these captures. The next EFIELD task should be selected from actual field/transition coverage:

- if natural retarget occurred: prioritize offsets that change with the target-pointer candidate and separate same-frame versus lagged changes;
- if lifecycle/type diversity is strong: prioritize ACTIVE enter/exit and type-local constant candidates;
- if attack transitions dominate: split attack onset / active / recovery candidate clusters from ordinary movement changes;
- if target remains constant but overall diversity stays high: continue passive collection rather than asking the operator to force retarget;
- only request a staged scene after repeated passive runs fail to cover a specific high-value transition.

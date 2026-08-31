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

## Current evidence baseline

Historical Collector evidence establishes a strong WinKawaks-local `+3` mapping for a set of previously studied fields, but this atlas treats those names as prior semantic hypotheses and uses new EFIELD raw bursts to independently characterize dynamics.

| WinKawaks offset | Prior label | Width candidate | Dynamic evidence | Current atlas status |
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

## Coverage gaps the EFIELD line must resolve

- full `0x00..0xDF` per-byte/per-word/per-dword change-rate atlas across all 20 slots
- constants vs stage-local constants vs type-local constants
- ACTIVE enter/exit boundaries and slot reuse signatures
- movement-only transitions versus idle
- attack-cycle onset/active/recovery correlations
- actual target/retarget transitions (prior target fields remained constant)
- type-conditioned distributions and width/endian candidates
- co-change graph / lagged correlations (same-frame and +/- few frames)
- high-value unknown offsets not present in the prior named field set

## Queue state

`EFIELD-001-baseline-30s60` has been submitted to `wof-winkawaks-bridge/tasks/queue/` as a 30 s, 60 Hz, raw-stream, read-only natural-gameplay burst.

As of this update it remains queued and has no `status/by_task/EFIELD-001...` or `results/by_task/EFIELD-001...` entry yet. Do not enqueue redundant baseline bursts until this one is consumed; next capture should be chosen from its actual coverage.

## Next automatic decision after EFIELD-001 completes

- If active-slot occupancy and state diversity are good: run a 60 s follow-up focused on raw full-object statistics and transition/co-change clustering.
- If occupancy is low: repeat natural gameplay for 60 s rather than requiring staged operator input.
- If retarget is observed: prioritize a retarget-window burst and rank offsets by mutual information against target identity changes.
- If retarget is not observed: continue passive natural-gameplay collection; do not ask the operator to force a scene unless passive coverage repeatedly fails.

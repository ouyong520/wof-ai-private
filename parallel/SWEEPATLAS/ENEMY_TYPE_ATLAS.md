# SWEEPATLAS Enemy Type Atlas

Updated: 2026-09-01

Namespace: **WinKawaks-local discovery only**. `Txx` below is the decimal value of enemy U8 `+0x24`; it is not a Browser/WASM offset mapping.

## Current retained coverage

The seven retained EFIELD natural-gameplay captures contain:

- 23,400 frames;
- 468,000 physical enemy-slot samples;
- 60,271 samples with nonzero type;
- 31 distinct nonzero type values;
- 1,604 contiguous same-type episodes.

Every nonzero value `0x01..0x1F` occurs at least once in the retained EFIELD aggregate.

## Priority questions

### T23

- local value: `0x17`
- observed: **YES**
- aggregate type-present samples: **2,140**
- exact stage/scene/wave: **UNKNOWN**

This answers the existence question: T23 is definitely present in retained WinKawaks EFIELD data. It does **not** answer the human location question, because none of the seven EFIELD tasks carries a stage/scene/wave label and no `BASECAP-SWEEP-*` labeled series exists in GitHub.

### T18

- local value: `0x12`
- observed: **YES**
- aggregate type-present samples: **528**
- exact stage/scene/wave: **UNKNOWN**

### T16

- local value: `0x10`
- observed: **YES**
- aggregate type-present samples: **9,210**
- exact stage/scene/wave: **UNKNOWN**

Two capture-local events give stronger provenance than aggregate presence alone:

- `EFIELD-003-passive-retarget-60s60`, frame 1827, slot 17: target P3 -> P2 while type remains T16.
- `EFIELD-004-passive-lifecycle-retarget-60s60`, frame 2961, slot 17: type T7 -> T16 at the same observed replacement/retarget boundary P3 -> P1.

These are capture locations, not game stage labels.

### T20

- local value: `0x14`
- observed: **YES**
- aggregate type-present samples: **686**
- exact stage/scene/wave: **UNKNOWN**

## Full aggregate population

| Type | Hex | Type-present samples |
|---|---:|---:|
| T1 | 0x01 | 173 |
| T2 | 0x02 | 408 |
| T3 | 0x03 | 160 |
| T4 | 0x04 | 300 |
| T5 | 0x05 | 495 |
| T6 | 0x06 | 354 |
| T7 | 0x07 | 2,670 |
| T8 | 0x08 | 7,293 |
| T9 | 0x09 | 2,894 |
| T10 | 0x0A | 645 |
| T11 | 0x0B | 1,102 |
| T12 | 0x0C | 469 |
| T13 | 0x0D | 470 |
| T14 | 0x0E | 411 |
| T15 | 0x0F | 187 |
| T16 | 0x10 | 9,210 |
| T17 | 0x11 | 2,002 |
| T18 | 0x12 | 528 |
| T19 | 0x13 | 1,013 |
| T20 | 0x14 | 686 |
| T21 | 0x15 | 2,285 |
| T22 | 0x16 | 2,309 |
| T23 | 0x17 | 2,140 |
| T24 | 0x18 | 12,866 |
| T25 | 0x19 | 6,807 |
| T26 | 0x1A | 1,060 |
| T27 | 0x1B | 591 |
| T28 | 0x1C | 188 |
| T29 | 0x1D | 272 |
| T30 | 0x1E | 133 |
| T31 | 0x1F | 150 |

## Lifecycle interpretation used by the atlas

A type episode is defined mechanically as a contiguous run in one physical enemy slot where `+0x24` stays at the same nonzero value.

The retained episode analysis found 1,604 episodes. `+0x24` is constant inside all 1,604 episodes and changes at episode boundaries, making it suitable for atlas identity grouping without assigning any game-character name.

The physical slot-header/allocation observation is unusual but stable in the seven-run corpus: slots 0..16 hold header value `0x00`, while slots 17..19 hold `0x01` throughout all 23,400 frames. Therefore slot-header transitions are not a useful spawn counter in this corpus; type enter/exit and same-type episodes are the more informative lifecycle index.

## Target-linked type observations

Known-player target transitions provide these type-local anchor events:

| Capture | Frame | Slot | Target | Type |
|---|---:|---:|---|---|
| EFIELD-002 | 2167 | 19 | P3 -> P1 | T22 -> T22 |
| EFIELD-002 | 3155 | 17 | P1 -> P3 | T24 -> T24 |
| EFIELD-002 | 3416 | 18 | P1 -> P3 | T25 -> T25 |
| EFIELD-003 | 492 | 17 | P1 -> P3 | T11 -> T11 |
| EFIELD-003 | 1827 | 17 | P3 -> P2 | T16 -> T16 |
| EFIELD-003 | 3322 | 19 | P3 -> P1 | T9 -> T9 |
| EFIELD-004 | 2961 | 17 | P3 -> P1 | T7 -> T16 |
| EFIELD-004 | 2961 | 18 | P2 -> P1 | T27 -> T9 |

## Boss mapping

**UNRESOLVED.**

No retained task/result supplies a human label such as a boss name paired with a frame/type. High type frequency, rarity, episode duration, or metadata patterns are insufficient to call an internal type a boss. SWEEPATLAS deliberately leaves boss mappings empty rather than guessing.

## Location reverse index

The requested `Txx -> stage/scene/wave` reverse index cannot yet be truthfully populated. Current safe reverse index is:

```text
T1..T31 -> retained EFIELD natural-gameplay corpus -> stage/scene/wave UNKNOWN
```

For T16, capture-local anchors additionally identify EFIELD-003 and EFIELD-004 as above. For T23/T18/T20, the aggregate analysis proves presence but the currently retained human-readable reports do not safely assign a particular stage/scene/wave.

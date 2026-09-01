# SEQMINER Sequence Atlas

Updated: 2026-09-01  
Evidence namespace: **WinKawaks-local discovery unless explicitly marked Browser evidence**.  
No entry here is a Browser production rule.

## Corpus and coverage

`parallel/SWEEPATLAS/**` is now present. Its capture index confirms that the retained repository corpus is broad but is **not** the intended labeled full-game sweep:

```text
stageSceneWaveLabelsAvailable = false
fullSweepSeriesPresent = false
```

Current natural EFIELD coverage:

- 7 captures / 2 WinKawaks sessions;
- 23,400 frames;
- 468,000 enemy-slot samples;
- 60,271 type-present samples;
- all 31 local nonzero types T1..T31;
- 1,604 same-type episodes;
- T18: 528 samples;
- T23: 2,140 samples.

Local T18/T23 existence is proven. Stage/scene/wave and exact local move labels are not.

## Ordered executor topology

The dominant local ordered backbone is:

```text
logical cursor + embedded flag
-> +0x34 countdown/residence
-> +0x35 control mode / +0x37 gate
-> (6C,70,72,73,77) joint phase
-> branch / +0x0A successor / loop reset
```

Across logical `+0x0A` destination events, leave-one-run-out phase prediction has coverage `4819/4820` and accuracy `4818/4819` on covered events. Pair/triple mining should therefore be record-aware rather than byte-state-only.

## Canonical cursor chains

High-volume executor loop:

```text
02008BD6
-> 02008BE0
-> 02008BEA
-> 02008BF4
-> 02008BFE
-> 02008C08
-> 02008C12
-> 02008BE0
```

Representative counts:

- `08BD6 -> 08BE0`: 148
- `08BE0 -> 08BEA`: 170
- `08BEA -> 08BF4`: 174
- `08BF4 -> 08BFE`: 156
- `08BFE -> 08C08`: 151
- `08C08 -> 08C12`: 132
- `08C12 -> 08BE0`: 135 (`-0x32` loop reset)

Second recurrent family:

```text
02005E9A
-> 02005EA4
-> 02005EAE
-> 02005EB8
-> 02005EC2
-> 02005ECC
-> 02005ED6
-> 02005EA4
```

The final edge is again a loop reset rather than a sequential advance.

## High-value branch nodes

Retained record-exit analysis separates 128 timed-sequential, 32 branch/mixed and 14 wait/conditional record classes.

| logical record | segments | sequential +10 | branch/other | use |
|---|---:|---:|---:|---|
| `02008BE0` | 355 | 199 | 141 | major conditional branch/wait hotspot |
| `02005EA4` | 232 | 114 | 108 | nearly balanced sequential/branch node |
| `02008BEA` | 209 | 171 | 35 | mostly sequential with real alternate exits |
| `02008BD6` | 208 | 173 | 35 | sequential plus flag/context split |
| `02008C12` | 144 | 0 | 142 | branch/reset node |
| `02008C52` | 113 | 0 | 107 | branch/reset node |
| `02005ED6` | 75 | 0 | 75 | branch/reset node |

`02008BE0` also has the visible alternate jump `02008BE0 -> 02009006` 30 times alongside common `02008BE0 -> 02008BEA`.

## Embedded cursor flag is mandatory state context

Logical cursor alone is incomplete at several records.

For `02008BD6`:

- aggregate phase spans `40,00,E8,1B,00`, `E0,00,38,0A,00`, and rare `1E` states;
- flag `0x100000`: 354/354 -> `E0,00,38,0A,00`;
- flag `0x140000`: rare `1E` termination family.

For `02005E9A`:

- flag `0x100000`: 210/210 -> `E0,00,38,0A,00`;
- flag `0x140000`: rare `70/78 ... 1E` family.

SEQMINER v2 therefore includes cursor flags in the core signature.

## Phase-path atlas

Common compressed `(6C,70,72,73,77)` paths:

| path | count |
|---|---:|
| `E0,A0,D8,0A,0C` | 216 |
| `40,00,E8,1B,00 -> E0,A0,D8,0A,0C -> 40,00,E8,1B,00` | 41 |
| `E0,00,38,0A,00 -> E0,A0,D8,0A,0C` | 38 |
| `50,00,18,1B,00` | 28 |
| `40... -> E0... -> 40... -> 48,00,00,1B,00` | 24 |
| `58,00,30,1B,00` | 20 |
| `40... -> E0... -> E0,00,38,0A,00` | 17 |
| `40... -> E0... -> 50,00,18,1B,00` | 14 |

Rare `78,78,78,1E,0B` and `70,70,70,1E,0B` had zero interior samples in boundary analysis and remain termination-context candidates. `90,00,88,0B,00` is the opposite: `257/271 = 94.83%` interior.

## Timer progression and conditional holds

Record-relative arrival normalization:

- ceiling: `3192/4323 = 73.84%`;
- within one: `4000/4323 = 92.53%`;
- within two: `4090/4323 = 94.61%`.

Literal `TM1` is not enough because some records wait at 1:

| record | segments | median terminal TM1 hold | max |
|---|---:|---:|---:|
| `02008D08` | 22 | 32 | 40 |
| `02005FF8` | 13 | 32 | 42 |
| `02008D12` | 22 | 23 | 24 |
| `02006002` | 13 | 23 | 24 |
| `02008BE0` | 355 | 2 | 276 |
| `0200906E` | 46 | 2 | 1518 |

SEQMINER v2 therefore records exact timer start/end/min/max plus `terminalTimer1Frames` and a normalized hold bucket.

## `+0x35` independent branch progression

Transition counts:

- `00->FF`: 353
- `FF->00`: 237
- `02->00`: 128
- `FF->02`: 74
- `00->01`: 67
- `00->02`: 52
- `01->FF`: 39
- `04->00`: 25

Structural alignment:

- `00->FF` with logical cursor `+0x0A`: 251;
- `02->00` with cursor unchanged: 128;
- `FF->02` frequently accompanies `0A -> 1B`;
- `01->FF` frequently accompanies `1B -> 0A`.

Mode history stays in pair/triple signatures and is not collapsed into timer34.

## Local T18 / T23 retained examples

SWEEPATLAS proves local T18 (`0x12`) and T23 (`0x17`) are present.

Raw-derived residence examples show both use the executor machinery:

- T18 example: EFIELD-005 slot19, logical `02008E68`, 15-frame `1B` residence ending timer `1,1`.
- T23 example: EFIELD-005R slot17, logical `02006158`, 10-frame `1B` residence ending timer `1,1`.

These do **not** map local values to Browser A4704/A4712/A4792/A4920/A5888. They only establish retained local coverage.

## Browser-labelled ordered evidence

### T18

Shared exact Browser state:

```text
S0/A4/B2|BODY4728|FE8b660|NX8b204|Vffff|TM1|P6C4736
```

Prospective outcomes:

```text
A4704 @ 19.9 ms
A4712 @ 100.4 ms
```

Target and side were stable 2/2. The next discriminator must be post-anchor order/context.

### T23

WOF-047 resolved `A4792=3`, `A4920=3`, `A5888=2`.

A5888 ordered tail example:

```text
S0/A8/B2 BODY4936
-> S0/A2/B0 BODY4936
-> S0/A6/B4 BODY4936
-> A5888
```

The first state also occurs in A4792, directly proving that order adds information. A4792 itself has multiple immediate tails, so a branch set is more defensible than one universal fingerprint.

## Ranking policy

Rank upward with same-cycle support, outcome purity, independent captures, authoritative scene labels when they truly exist, multiple targets, timer-normalized stability, and ability to split a known ambiguous anchor.

Rank downward for one-cycle purity, one-capture-only support, exact-timer brittleness, target/profile confounding, capture filename masquerading as a scene, or structural `+0x73` proxy being treated as an exact attack.

## Current boundary

The current corpus is sufficient to exhaust structural order, timer, mode and branch topology, but not to emit a trustworthy all-game `Txx -> exact move-valued activeAttack -> attack-specific pair/triple` matrix because both a labeled full-sweep series and a proven exact local move/attack field are absent.

No recapture is requested. `seqminer.py` v2 is ready to regenerate exact tables automatically when either missing condition is resolved.
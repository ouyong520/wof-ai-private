# SEQMINER Sequence Atlas

Updated: 2026-09-01  
Evidence namespace: **WinKawaks-local discovery unless explicitly marked Browser evidence**.  
No entry here is a Browser production rule.

## Corpus and coverage

`parallel/SWEEPATLAS/**` is present. Its capture index confirms that the retained repository corpus is broad but is **not** the intended labeled full-game sweep:

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

SEQMINER v3 therefore includes cursor flags in the core signature.

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

SEQMINER v3 records exact timer start/end/min/max plus `terminalTimer1Frames` and a normalized hold bucket.

### Reload-context holdout guardrail

High in-sample purity from adding `type/B6` to destination record is mostly sparse conditioning, not a robust general law. Leave-one-run-out aggregate results show destination record alone covers `4321/4323` with 0.7464 fallback accuracy, while `dst+type+B6` directly covers only `448/4323` and reaches 0.7331 with fallback. Therefore SEQMINER keeps type/profile as context but does not treat profile-conditioned reload values as a stable attack discriminator.

## Delayed `1B` dwell initialization / positive timer reload

A deeper retained-raw pass finds a separate ordered timer phenomenon inside coarse `0x73=1B` residences:

- 52 multi-frame `1B` residences enter with `+0x34=8` and then load upward later;
- 1,311 other multi-frame `1B` residences do not show this pattern;
- first positive reload occurs at residence frame offset 1 in 37/52, offset 2 in 13/52, offset 3 in 2/52;
- loaded values span 9..17;
- all 52 enter with joint `(6C,70,72,77) = 40,00,E8,00`.

Destination records:

| record | delayed reload events |
|---|---:|
| `02008E68` | 10 |
| `02008DE2` | 10 |
| `02008D98` | 9 |
| `020060D2` | 8 |
| `02006088` | 8 |
| `02006158` | 7 |

Leading predecessor -> destination pairs include:

```text
02005EA4 -> 020060D2   6
02008BE0 -> 02008DE2   6
02008BE0 -> 02008E68   5
02005EA4 -> 02006088   5
02008BE0 -> 02008D98   4
02005EA4 -> 02006158   3
02008BD6 -> 02008E68   3
```

The reload is coordinated with other executor fields:

- `+0x35` changes on 52/52 delayed reload transitions;
- `+0x42` changes on 52/52;
- `+0x7E` changes on 41/52;
- `+0x42` is independently a high-frequency countdown/progress companion whose common deltas track `+0x34` (`-1/-1`, `-2/-2`).

This is stronger evidence for a **multi-field delayed dwell initialization step** than for an arbitrary timer glitch.

Type-conditioned examples include one local T18 and one local T23 event:

```text
T18 / 0x12: EFIELD-005 f3524 s19, rec 02008E68, B6=29, C6=1, 34 8->11
T23 / 0x17: EFIELD-005R f1263 s17, rec 02006158, B6=2C, C6=1, 34 8->9
```

These examples prove the mechanism is reachable by both priority types; they do **not** connect it to Browser A4704/A4712/A4792/A4920/A5888.

The apparent loaded-value purity of `record+type+B6` is not promoted: 48 such groups contain 44 singletons, so the 0.942 in-sample concentration is dominated by sparse memorization.

### v3 representation correction and event-boundary guard

The 52/52 `+0x35` coincidence exposes an important compression boundary: because `+0x35` belongs to the core state, the positive `+0x34` load may occur exactly when the old core state ends and a new one begins. A reload list attached only to one compressed state can therefore miss the canonical delayed-load edge.

v3 records every **positive timer reload that lies inside the selected zero-prefix** independently of compressed-state boundaries and emits four feature families:

```text
timer34_reload_exact
timer34_reload_norm
cross_core_reload_exact
cross_core_reload_norm
```

Each edge preserves pre/post core, cursor, mode35, phase, timer42, exact timer values, record-normalized timer buckets, reload magnitude family and any timer1 hold immediately before the reload. The future nonzero event frame and all post-event frames are excluded from predictor features.

This distinction matters for the 52 delayed-`1B` examples: default structural proxy mode ends the prefix when `+0x73` first becomes nonzero, so those reloads occur **after** the proxy event and are not used as default-mode predictors. They become eligible sequence features only under a future independently proven exact-attack event definition that remains zero until after the reload. The retained 52-event set therefore validates the need for a cross-state representation, not a default-proxy prediction claim.

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

Mode history stays in pair/triple/reload signatures and is not collapsed into timer34.

## Support and loop semantics

Confidence is cycle-based:

```text
one signature in one resolved cycle = at most one support unit
one ambiguous anchor in one resolved cycle = at most one attack-support unit
```

Repeated loop visits remain available separately as raw occurrence diagnostics. They never create independent evidence merely because a script loop revisits the same state several times before one future event.

Capture filename fallback is provenance, not explicit scene evidence. Future explicit `stage/scene/sceneId/room/wave` dimensions are preserved together.

## Local T18 / T23 retained examples

SWEEPATLAS proves local T18 (`0x12`) and T23 (`0x17`) are present.

Raw-derived residence examples show both use the executor machinery:

- T18 example: EFIELD-005 slot19, logical `02008E68`, 15-frame `1B` residence ending timer `1,1`; this same residence family contains a delayed `8->11` initialization event.
- T23 example: EFIELD-005R slot17, logical `02006158`, 10-frame `1B` residence ending timer `1,1`; this family contains a delayed `8->9` initialization event.

These do **not** map local values to Browser A4704/A4712/A4792/A4920/A5888. They only establish retained local coverage and ordered timer diversity.

## Exact local attack-descriptor audit

The bridge's current attack-themed reports remain structurally anchored rather than move-valued:

- `ATTACK_CYCLE.md` defines an attack episode as a contiguous `+0x73 != 0` run.
- `MOVE_ATTACK.md` reports 2,391 "attack-field transition events" and shows `+0x6C/+0x73` as perfectly attack-selective under that phase-transition anchor.
- the retained EFIELD summary contains no `activeAttack` field and no literal `0x1260` value corresponding to Browser A4704.
- the passive `ACTIVE_STATE.md` uses type-present lifecycle activity, not Browser semantic attack ACTIVE.

Therefore no current local field is relabeled as an exact move/attack descriptor merely because it is attack-associated.

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

Rank upward with same-cycle support, outcome purity, independent captures, authoritative scene labels when they truly exist, multiple targets, timer-normalized stability, prefix-valid delayed-reload/terminal-hold stability, and ability to split a known ambiguous anchor.

Rank downward for one-cycle purity, one-capture-only support, exact-timer brittleness, sparse record/type/profile memorization, target/profile confounding, capture filename masquerading as a scene, repeated loop visits masquerading as independent support, post-event leakage, or structural `+0x73` proxy being treated as an exact attack.

## Current boundary

The current corpus is sufficient to exhaust structural order, timer/reload, mode and branch topology, but not to emit a trustworthy all-game `Txx -> exact move-valued activeAttack -> attack-specific pair/triple` matrix because both a labeled full-sweep series and a proven exact local move/attack field are absent.

No recapture is requested. `seqminer.py` v3 and `FEATURE_CONTRACT.json` are ready to regenerate exact tables automatically when either missing condition is resolved.

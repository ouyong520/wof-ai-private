# EFIELD Field Frontier

Updated: 2026-09-01
Lane: `EFIELD-*` only
Namespace: WinKawaks normalized enemy object, stride `0xE0`

This file is the authoritative EFIELD-lane frontier. EFIELD is a WinKawaks-local, read-only discovery lane. Nothing here establishes Browser/WASM numeric offset equivalence or changes any Browser production rule.

## Operating rule

The lane no longer attempts to name the whole `0xE0` object. Each research round resolves only 1–3 high-value fields with exactly one formal status:

- `CONFIRMED`
- `STRONG_CANDIDATE`
- `WEAK_CANDIDATE`
- `REJECTED`
- `UNKNOWN`

`CONFIRMED` requires offset, minimum reasonable width, observed domain, repeated change behavior, cross-event/slot/run evidence, and explicit counterexamples/limits. Correlation alone is not sufficient.

## Corpus boundary

Current valid retained EFIELD raw corpus:

- `EFIELD-001-baseline-30s60`
- `EFIELD-002-natural-diversity-60s60`
- `EFIELD-003-passive-retarget-60s60`
- `EFIELD-004-passive-lifecycle-retarget-60s60`
- `EFIELD-005-cross-session-target-60s60`
- `EFIELD-005R-cross-session-target-60s60`
- `EFIELD-006-cross-session-lifecycle-target-60s60`

Coverage:

- 23,400 frames
- 468,000 enemy-object samples
- 60,271 type-present samples
- 407,729 type-absent samples
- 1,604 same-nonzero-type episodes
- 74 type-enter + 74 type-exit boundaries
- 8 confirmed live-target changes
- two WinKawaks process sessions
- game-memory writes: 0

`EFIELD-007/008/009` failed before sampling because fresh immutable CPS RAM discovery was not uniquely qualified. Those are acquisition-environment failures, not negative field evidence. Do not requeue equivalent generic captures or weaken discovery uniqueness.

## Formal field map

### CONFIRMED

| Offset(s) | Width | Operational interpretation | Key evidence / limits |
|---|---:|---|---|
| `+0x24` | U8 | current type-present / lifecycle discriminator and type code | 74/74 enter + 74/74 exit; perfect active-vs-absent byte separation in current corpus; not Browser ACTIVE/hitbox; nonzero->nonzero replacement exists |
| `+0x6D..+0x6E` | U16 BE | materialized live player-target pointer | exact domain BE1C/BEFC/BFDC; 8 changes = 8 known retargets; can remain latched through `+0x24==0`; not upstream selector |
| `+0x34` | U8 | executor record dwell/countdown | 6,737 multi-frame record residences; 99.21% no positive step; terminal values concentrated at 1/2/3; conditional waits/delayed init are documented |
| `+0xC6` | U8 | stored player-association index | exact 00/01/02 -> P1/P2/P3 association; nearest-X agreement 87.02%; sample-and-hold; separate P1 reset path exists |
| `+0x3D..+0x3E` | U16 BE | stored player-association pointer | exact BE1C/BEFC/BFDC mapping to C6 across 60,271 samples; distinct from live target globally |
| `+0xB9` | U8 | horizontal-locomotion cyclic phase counter | ~45% changes on pure horizontal movement, almost none stationary/pure orthogonal-axis; repeated cyclic chains; not direction bit |
| `+0xBB` | U8 | horizontal-locomotion decrementing step/countdown state | zero changes stationary/pure orthogonal-axis in control pass; moving changes overwhelmingly -1; not universal movement timer |
| `+0x2F..+0x32` | U32 BE | flagged logical executor record cursor | mask 0x001C0000; 4,323/5,539 logical changes are +0x0A; destination phase holdout 4,818/4,819 accurate on covered; loops/branches normal |
| `+0x35` | U8 | executor dwell/control-mode byte | domain 00/FF/01/02/04; 1,024 changes; independent of +34 numeric countdown; exact code meanings unresolved |
| `+0x6C` | U8 | fine executor / attack-associated phase code | 9-value domain; deterministic many-to-one projection to +73; record-driven; no visual hit/startup/recovery naming |
| `+0x73` | U8 | coarse executor / attack-family phase code | exact 00/0A/0B/1B/1E; deterministic coarse projection of +6C; +74 is zero padding; nonzero is not universal attack-active |
| `+0x70` | U8 | second fine executor / attack-associated phase code | 10-value domain; deterministic many-to-one projection to +77; strongly attack-side vs movement controls |
| `+0x77` | U8 | second coarse executor / attack-family phase code | exact 00/0A/0B/0C/14; deterministic projection of +70; +76 is zero neighbor; not attack-active boolean |
| `+0xB4` | U8 | episode-stable coarse profile/variant metadata bit | 1,604/1,604 episodes constant, zero within changes; binary; 3/11 same-type replacements change it; not unique ID |
| `+0xB6` | U8 | episode-stable instance/profile initialization code | 1,604/1,604 episodes constant, zero within changes; 34-value domain; 9/11 same-type replacements change it; not unique ID/type code |
| `+0xCC` | U8 | stored-association nearest-X synchronization checkpoint state | 65 same-type 00->FF entries; 57 already-correct remain, 8 stale C6 values corrected exact frame; post C6 nearest-X 65/65; FF is a latch, not pulse |
| `+0x6F` + `+0x68` | U8 + U8 split encoding | distinct third player-reference layer | `(6F<<8)|68` is BE1C/BEFC/BFDC on 60,271/60,271 samples; equals association 38.32%, live target 74.62%; role beyond player-reference identity unresolved |

### STRONG_CANDIDATE

| Offset(s) | Width | Current interpretation | Why not CONFIRMED |
|---|---:|---|---|
| `+0x07..+0x0A` | S32 BE candidate | first coordinate-bearing fixed-point block | coherent orthogonal movement axis, but final game-space axis label / minimum packed width / scale lacks independent ground truth |
| `+0x0B..+0x0E` | S32 BE candidate | second coordinate-bearing fixed-point block | same as above; two-axis independence is strong but X vs floor-depth/Y label not independently locked |
| `+0x72` | U8 | executor joint-phase payload / companion state | 16-value structured state, attack support 1.0, record-driven; no isolated independent semantic dimension |
| `+0x2D` | U8 | compact executor/control state | seven-value domain; frame-exact at confirmed C6 sync corrections but low selectivity for any one event |
| `+0x2E` | U8 | compact executor/control companion state | seven-value domain; changes on confirmed sync corrections but also broad within-episode execution transitions |
| `+0x37` | U8 | attack/executor-family gate or substate | domain 00/80/02; ~55.6x attack-side selectivity; 80 not a simple attack-on bit; exact mode meaning unresolved |
| `+0xB0` | U8 | slowly-changing profile/runtime-state byte | 98.50% episodes constant but 29 genuine within-episode changes; immutable initialization hypothesis rejected |

### REJECTED hypotheses

| Offset / hypothesis | Verdict reason |
|---|---|
| `+0x00` = current enemy active/presence | zero transitions while +24 has 148 zero/nonzero lifecycle edges |
| separate byte-level active/inactive gate better than +24 | no candidate beats +24; +42 is high-frequency counter-like and +2E misses many lifecycle boundaries |
| `+0x42` = direct lifecycle gate | changes on every lifecycle edge but also 37,162/58,667 same-type transitions; all 256 values |
| `+0x2E` = direct lifecycle gate | only 37/74 enters and 32/74 exits change it; broad within-episode state |
| `+0x6D..+0x6E` = upstream selector | stored association can precede live commit by 57..715 frames |
| `+0x99` = universal/pre-commit retarget signal | only 5/8 target commits; all observed hits lag 0; unrelated sparse transitions exist |
| `+0x34` = simple universal frame timer | conditional terminal waits and delayed initialization contradict it |
| U16 `+0x34..+0x35` = countdown | +34 decrements while +35 is normally unchanged and independently switches modes; no carry/borrow behavior |
| U16 `+0x37..+0x38` = timer | +38 constant 0x84; +37 is a three-state gate-like byte dominated by 00<->80 |
| `+0xB0` = immutable instance-init field | 29 within-episode changes across full corpus |
| C6 / association = live target or universal retarget precursor | equals live only 31.11%; six live commits occur tens/hundreds frames after association is already stable |
| split `+0x6F/+0x68` = live-target alias | only 74.62% global equality; 20 same-type split-ref changes vs 6 same-type live changes |

## Proven structural subsystem summary

### Lifecycle

`+0x24` is the best current typed-enemy episode discriminator. No separate byte-level execution-active gate is supported more strongly by the existing corpus.

### Player references / target

```text
nearest-X synchronization event
        |
        v
+0xCC 00->FF
        |
        v
+0xC6 / +0x3D..+0x3E   stored association

+0x6F + +0x68            separate split player-reference layer

+0x6D..+0x6E             materialized live target
```

The three player-reference layers are structurally distinct. Current raw does not reveal a selective universal pre-commit retarget pulse.

### Executor

```text
+0x2F..+0x32  flagged 10-byte logical record cursor
       |
       +--> +0x34 dwell/countdown
       +--> +0x35 dwell/control mode
       +--> joint phase tuple
             +0x6C -> +0x73
             +0x70 -> +0x77
             +0x72 companion payload
```

The hierarchy is structural only; no value is promoted to hitbox-active, damage onset, startup, recovery, or visual attack frame.

### Movement

`+0xB9` and `+0xBB` are formally separated from attack/executor phase fields and are specific to the first coordinate-motion axis in existing controls. The two coordinate-bearing fixed-point blocks remain strong candidates until an independent axis-label/scale discriminator exists.

### Instance/profile metadata

`+0xB4` and `+0xB6` are episode-invariant profile dimensions. `+0xB0` is slower profile/runtime state but not immutable.

## Round reports

- `ROUND_002_LIFECYCLE_ACTIVE.md`
- `ROUND_003_TARGET_ASSOCIATION_AND_RETARGET.md`
- `ROUND_004_MOVEMENT_COORDINATES.md`
- `ROUND_005_EXECUTOR_CURSOR_AND_MODE.md`
- `ROUND_006_COARSE_FINE_ATTACK_PHASE.md`
- `ROUND_007_SECOND_PHASE_PROJECTION.md`
- `ROUND_008_INSTANCE_METADATA.md`
- `ROUND_009_ASSOCIATION_SYNC_AND_THIRD_REFERENCE.md`
- `ROUND_010_ACTION_CONTROL_RESIDUALS.md`

Round 001 details are the original `+0x24`, `+0x6D..+0x6E`, `+0x34` lock that established this frontier.

## Current bounded-phase stop condition

The existing raw corpus has now been mined through all requested high-value priorities: lifecycle, target/retarget, movement/coordinates, timer/countdown/executor, attack/action/state, and instance/profile metadata.

Do **not** continue generic capture merely to grow the candidate table. Further EFIELD acquisition is justified only when a new concrete question supplies a discriminative scene that can resolve one of the remaining candidate-level ambiguities, principally:

1. independent game-space labeling and minimum packed width/scale for the two coordinate blocks;
2. exact semantic dimension of `+0x72`;
3. value-level meanings for `+0x2D`, `+0x2E`, `+0x37`, `+0x35`;
4. behavioral role of the split third player-reference layer beyond its confirmed P1/P2/P3 identity;
5. a genuinely selective pre-commit retarget trigger, if one exists.

These are explicit unknowns, not justification for undirected 60-second capture loops.

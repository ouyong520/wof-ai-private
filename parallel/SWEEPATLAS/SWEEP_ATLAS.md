# SWEEPATLAS — Capture / Scene / Enemy Atlas

Updated: 2026-09-01

## Corpus verdict

The current GitHub corpus contains healthy retained BASECAP, EFIELD, GEO and RAWMINE raw artifacts, but **no `BASECAP-SWEEP-*` full-game sweep series**. The sweep guide defines the desired stage/scene/wave labeling protocol; the actual labeled sweep task/result/raw files are not present in either repository.

For that reason this table preserves every recoverable human acquisition label but never manufactures game-stage labels from raw values.

## Recoverable controlled-capture labels

| Capture | Human-supported acquisition context | Player configuration | Stage | Scene | Wave | Atlas use |
|---|---|---|---|---|---|---|
| BASECAP-B00 | stationary idle baseline, safe/no combat/no camera scroll | P1 idle; P2/P3 untouched | ? | ? | ? | neutral control |
| BASECAP-B12R | minimal-displacement left/right facing changes | P1 controlled; P2/P3 untouched | ? | ? | ? | facing/orientation control |
| BASECAP-B13R | standing ordinary-attack pulses | P1 ordinary attack; P2/P3 untouched | ? | ? | ? | action control |
| BASECAP-B13 | four ordinary-attack taps | P1 ordinary attack; P2/P3 untouched | ? | ? | ? | canonical short action control |
| BASECAP-B20 | rightward advance intended to cause visible camera scroll | P1 right movement; P2/P3 untouched | ? | ? | ? | camera/geometry acquisition control |
| BASECAP-B40-P2 | right/left/up/down sequence | P2 controlled; P1 static; P3 untouched | ? | ? | ? | P2 geometry control |
| BASECAP-B40-P3 | right/left/up/down sequence | P3 controlled; P1/P2 static | ? | ? | ? | P3 geometry control |
| RAWMINE-005 | long horizontal then depth traversal | controlled P1 object; other players controls | ? | ? | ? | geometry discriminator |

Question marks are intentional: none of these tasks records a game stage/scene/wave identifier.

## Natural gameplay EFIELD corpus

| Capture | Frames | Type enter/exit | Known-player target transitions | Stage/scene/wave label |
|---|---:|---:|---:|---|
| EFIELD-001-baseline-30s60 | 1,800 | 7 / 6 | 0 | absent |
| EFIELD-002-natural-diversity-60s60 | 3,600 | 3 / 4 | 3 | absent |
| EFIELD-003-passive-retarget-60s60 | 3,600 | 11 / 11 | 3 | absent |
| EFIELD-004-passive-lifecycle-retarget-60s60 | 3,600 | 5 / 5 | 2 | absent |
| EFIELD-005-cross-session-target-60s60 | 3,600 | 17 / 16 | 0 | absent |
| EFIELD-005R-cross-session-target-60s60 | 3,600 | 16 / 17 | 0 | absent |
| EFIELD-006-cross-session-lifecycle-target-60s60 | 3,600 | 15 / 15 | 0 | absent |

Aggregate: 23,400 frames, 468,000 enemy-slot samples, 74 type enters, 74 type exits and 8 exact known-player target changes.

## Enemy composition currently recoverable

The retained EFIELD aggregate proves all local nonzero internal type values T1..T31 occur. It does **not** provide human visible-enemy names or a stage label.

Priority types:

- T23 / `0x17`: observed, 2,140 type-present samples.
- T18 / `0x12`: observed, 528 samples.
- T16 / `0x10`: observed, 9,210 samples.
- T20 / `0x14`: observed, 686 samples.

T16 additionally has capture-local anchor events in EFIELD-003 and EFIELD-004. See `ENEMY_TYPE_ATLAS.md`.

## Target distribution observations

Eight exact known-player target transitions are retained. Destination counts among those events are:

- to P1: 4
- to P2: 1
- to P3: 3

Source counts:

- from P1: 3
- from P2: 1
- from P3: 4

This is a transition-event distribution, not a dwell-time target occupancy distribution.

## Lifecycle / slot observations

The seven-run EFIELD analysis finds:

- 1,604 contiguous same-nonzero-type episodes;
- physical slots 0..16 retain slot-header value `0x00` throughout all 23,400 frames;
- physical slots 17..19 retain slot-header value `0x01` throughout all 23,400 frames;
- no slot-header allocation transition occurs in the seven-run aggregate;
- type enter/exit and same-type episode boundaries therefore provide the useful lifecycle indexing in this corpus.

## Attack-associated structural coverage

Retained EFIELD analysis identifies 271 contiguous attack-associated executor episodes under the mechanical `+0x24 != 0` and `+0x73 != 0` definition. The atlas preserves coarse/fine phase values in `ATTACK_ATLAS.md` but does not translate them into exact named attacks or Browser ACTIVE.

## Stage / scene / wave matrix

The truthful current matrix is empty:

| Stage | Scene | Wave | Txx composition | Attack-associated values | Evidence |
|---|---|---|---|---|---|
| UNKNOWN | UNKNOWN | UNKNOWN | T1..T31 observed across EFIELD aggregate | multiple executor phase families observed | natural EFIELD corpus lacks human location labels |

A more specific row would be a fabricated location label, so none is added.

## Duplicate / retry / anomaly handling

- B12 has an earlier short attempt and later timing-robust B12R. B12R is canonical for facing reuse.
- B13 has timing-racy/ungated history; B13R and the later short B13 raw are retained controls. The older delayed timing-racy status is not promoted as canonical atlas evidence.
- EFIELD-005R and EFIELD-005 are adjacent cross-session replication runs; both are retained because they are distinct raw artifacts, not byte-identical duplicates.
- `collector-live-smoke-*` and `collector-p4-delivery-001` are excluded from gameplay atlas statistics.
- No trusted primary entry audited so far points to a missing raw artifact.

## What cannot be recovered from current GitHub data

- actual stage number/name for EFIELD captures;
- scene and wave labels;
- human visible enemy names/composition;
- boss name -> internal Txx mapping;
- exact scene-specific attack values;
- full type×attack×scene contingency table.

These are left unresolved rather than guessed.

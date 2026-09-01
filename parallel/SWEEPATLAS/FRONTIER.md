# SWEEPATLAS Frontier

Updated: 2026-09-01

Status: **CURRENT GITHUB DATA EXHAUSTED TO THE SAFE LABELING BOUNDARY**

Namespace: `WinKawaks-local-discovery-only`

## Closed from retained evidence

1. Retained-capture inventory audited across BASECAP / EFIELD / GEO / RAWMINE families and bridge `captures/` manifest.
2. Trusted corpus admission requires task/result/raw identity, PASS, read-only/no-write contract, and retained raw path/content SHA.
3. Seven-run EFIELD aggregate indexed:
   - 23,400 frames;
   - 468,000 enemy-slot samples;
   - 60,271 type-present samples;
   - all T1..T31 observed;
   - 1,604 same-type lifecycle episodes;
   - 74 type enters / 74 exits;
   - 8 exact known-player target transitions.
4. Priority internal-type existence questions answered:
   - T23 `0x17`: observed, 2,140 samples;
   - T18 `0x12`: observed, 528 samples;
   - T16 `0x10`: observed, 9,210 samples;
   - T20 `0x14`: observed, 686 samples.
5. Attack-associated executor structure indexed without promoting exact move semantics:
   - 271 `+0x73 != 0` episodes under type-present filter;
   - coarse `+0x73`, fine `+0x6C`, secondary `+0x77/+0x70` families retained.
6. Retry/noncanonical and smoke artifacts separated from primary atlas evidence.

## Not closed — provenance/label gap, not a field-analysis gap

The repositories currently contain **no `BASECAP-SWEEP-*` task/result/raw series** despite the full-game sweep guide defining that protocol.

The natural EFIELD tasks carry no stage/scene/wave labels. Because SWEEPATLAS is forbidden to infer a stage from raw numeric patterns alone, the following remain unresolved:

- T23 exact stage/scene/wave;
- T18/T16/T20 exact stage/scene/wave;
- stage/scene/wave -> Txx -> attack matrix;
- Txx -> stage/scene/wave reverse map;
- boss human name -> internal type;
- scene-specific attack values;
- human visible enemy composition.

## Important negative rule

Absence of a stage label is **not** evidence of absence from a stage. Likewise, rarity/frequency/episode duration is not sufficient to call a type a boss.

## Operator gate

`operatorGate: NOT_REQUESTED`

Reason: the immediate gap is not proven to require a human to replay a specific scene. The missing input is the absent full-sweep task/result/raw + human label corpus in GitHub. Requesting the operator to repeat large-scale collection now would violate the reuse-first requirement.

If a previously completed labeled sweep is later pushed into GitHub, SWEEPATLAS can ingest it without new gameplay collection and populate the location matrices.

Only if it is established that no labeled sweep exists anywhere, and a particular unresolved location question cannot be answered from retained data, would a narrowly scoped operatorGate become justified.

## Current safe stop condition

No new Collector tasks are justified by SWEEPATLAS at this point.

The lane should resume automatically when any of the following appears in GitHub:

- `BASECAP-SWEEP-*` task/result/raw;
- another capture with explicit stage/scene/wave metadata;
- an authoritative human label manifest that maps existing retained capture IDs to stage/scene/wave;
- a new retained analysis product providing auditable type×attack or capture-local type population statistics.

Until then, machine-readable truth is in `ATLAS.json` and `CAPTURE_INDEX.json`; human summaries are in `SWEEP_ATLAS.md`, `ENEMY_TYPE_ATLAS.md`, and `ATTACK_ATLAS.md`.

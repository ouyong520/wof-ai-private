# COVERAGE FRONTIER

Snapshot: `2026-09-01`

## Closed enough for current coverage accounting

### Provenance / raw retention — GOOD

- 30 raw artifacts total in `captures/`.
- 28 are deduplicated mechanically successful gameplay raws.
- 2 are collector/platform test raws and are excluded from gameplay coverage.
- all 28 successful gameplay captures have matching `tasks/queue`, `status/by_task`, `results/by_task`, and `captures` artifacts.
- reuse by another lane is not double-counted.

### Current EFIELD Txx sample census — GOOD / LOW

- 31 observed Txx codes.
- 60,271 total type-present samples.
- 17 Txx at COVERAGE `GOOD` density (`>=500` samples).
- 14 Txx at COVERAGE `LOW` density (`1..499` samples).
- T23: 0 samples in the current EFIELD corpus, tracked as `MISSING` exemplar only; expected full-game membership is unknown.

### Aggregate lifecycle evidence — GOOD

- 1,604 same-nonzero-type lifecycle episodes globally.
- Per-Txx episode counts remain `LABEL_UNKNOWN` because the current read-only outputs do not materialize that cross-tab.

### Aggregate structural attack/executor evidence — GOOD / LOW

Coarse `enemy+0x73`:
- `0x0A`: 27,486 frames — GOOD
- `0x1B`: 16,651 — GOOD
- `0x0B`: 726 — GOOD, relatively sparse
- `0x1E`: 42 — LOW
- `0x00`: 15,366 background/zero-family frames

There are 271 nonzero structural executor/attack-family episodes globally. Semantic attack names and semantic ACTIVE cycles are not inferred.

### Aggregate target coverage — GOOD

Live-target counts:
- P1: 46,865
- P2: 2,967
- P3: 10,439

Association counts:
- P1: 18,091
- P2: 17,494
- P3: 24,686

Eight confirmed live-target changes exist. Per-Txx target coverage remains `LABEL_UNKNOWN`.

### Geometry owner closure — GOOD

Read-only GEO owner outputs close:
- P1 X
- P1 Y / floor-depth
- P2/P3 same-offset structure
- facing
- top/bottom

Historical flat/confounded captures remain in the audit, but zero/flat evidence is not treated as field absence.

## Open frontier

### 1. Stage / scene / wave atlas — LABEL_UNKNOWN

This is the highest-priority coverage join. Current task condition names are not game-scene labels.

### 2. Boss / ordinary enemy labels — LABEL_UNKNOWN

No authoritative mapping is present.

### 3. Per-Txx lifecycle / attack / target / scene cross-tabs — LABEL_UNKNOWN

These are primarily analysis/materialization gaps over existing raw. Do not collect first.

### 4. Semantic ACTIVE cycles — LABEL_UNKNOWN

Structural attack/executor episodes must not be renamed as semantic ACTIVE.

### 5. Ordered sequence families — LABEL_UNKNOWN

`parallel/SEQMINER/**` is absent at this snapshot.

### 6. Rare / low-density evidence — LOW

The 14 low-density Txx and coarse `0x1E` family are the main quantitative sparse-evidence frontier, but their optimal recap scenes cannot be chosen until authoritative scene incidence is available.

## Input lanes to consume read-only

COVERAGE should continuously re-audit when these change:

- `parallel/BASECAP/**`
- `parallel/GEO/**`
- `parallel/EFIELD/**`
- `parallel/RAWMINE/**`
- `parallel/SWEEPATLAS/**` when present
- `parallel/SEQMINER/**` when present
- bridge `tasks/queue/**`
- bridge `status/by_task/**`
- bridge `results/by_task/**`
- bridge `captures/**`

COVERAGE does not change field semantics, attack rules, Browser logic, MAINLINE production-shadow state, or other lane files.

## Current next action

**No human capture and no Collector batch.**

The next useful COVERAGE action is to ingest authoritative scene/sequence labels or materialized per-Txx cross-tabs, recompute the matrix, and only then solve the minimal scene set-cover problem. A new physical recap should be requested only if that recomputation leaves genuine residual coverage gaps that existing raw cannot satisfy.

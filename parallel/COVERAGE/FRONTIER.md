# COVERAGE FRONTIER — normalized refresh

Snapshot: `2026-09-01`

## Current closure

### Type identity / sample census — REFRESHED

Canonical notation is `T<decimal> (0xHH)`. The old hex-style `Txx` display is retired.

The seven retained EFIELD captures contain all nonzero raw type bytes `0x01..0x1F`, therefore all normalized types `T1 (0x01)` through `T31 (0x1F)` are observed.

Priority corrections:

- T16 (0x10): 9,210 samples.
- T18 (0x12): 528 samples.
- T20 (0x14): 686 samples.
- T23 (0x17): 2,140 samples.
- T24 (0x18): 12,866 samples.

The previous COVERAGE `T23=0` conclusion was a notation artifact. Old `T17` meant raw `0x17`, which is canonical T23 (0x17).

### SWEEPATLAS — INGESTED

SWEEPATLAS is present. It proves:

- 23,400 EFIELD frames;
- 468,000 enemy-slot samples;
- 60,271 type-present samples;
- 31 distinct nonzero types;
- 1,604 same-type episodes;
- 74 enter + 74 exit boundaries;
- 8 confirmed live-target changes;
- 271 structural attack/executor episodes.

It also proves the current retained corpus does **not** contain an authoritative stage/scene/wave-labeled full-game sweep series.

### SEQMINER — INGESTED

SEQMINER is present and has exhausted the current retained structural corpus to its safe boundary.

Materialized now:

- global record-aware ordered executor topology;
- timer progression and terminal-hold context;
- branch/reset nodes and mode history;
- delayed positive timer-reload sequences;
- explicit local T18 (0x12) and T23 (0x17) ordered examples;
- explicitly separated Browser-labelled T18/T23 ordered evidence.

Not materialized/proven:

- all-game type -> exact local move -> ordered signature matrix;
- authoritative stage/scene/wave conditioning;
- a proven WinKawaks-local exact move/attack semantic field.

SEQMINER itself requests no recapture.

### Concurrent SEQMINER v3 audit — INCLUDED

COVERAGE audited the concurrent SEQMINER v3 work through `fd9cc448b56af353ea4cc3b5f4f4d0e8b45196f1`.

v3 adds/clarifies:

- machine-readable `FEATURE_CONTRACT.json`;
- support counted at most once per unique resolved cycle per signature;
- cycle-level positive `+0x34` reload edges so reloads crossing a `+0x35`/core-state boundary are not lost;
- explicit cross-core delayed-reload feature/branch families;
- explicit separation of raw loop occurrence counts from independent confidence;
- capture filename fallback is not authoritative scene evidence;
- exact local attack semantics remain gated on an independently proven WinKawaks-local attack field.

Coverage impact: **evidence-contract quality strengthened; sample corpus and gap classes unchanged**. These commits modify SEQMINER analysis representation/documentation rather than the retained gameplay corpus, and SEQMINER v3 still requests no generic Collector recapture.

### Deep retained-data audit — SAFE BOUNDARY CONFIRMED

COVERAGE also checked the current bridge EFIELD analysis outputs instead of treating missing cross-tabs as missing data.

Existing retained reports already materialize useful aggregate evidence, including:

- 1,604 contiguous same-type episodes in the seven-run corpus;
- global live-target dwell population P1/P2/P3;
- exact live-target transition anchors;
- 271 structural `+0x73 != 0` attack/executor episodes;
- target/association materialization evidence and attack-selective executor fields.

What they do **not** currently expose as a safe ready-made table is the full per-normalized-type lifecycle-count, P1/P2/P3 dwell, and structural-executor episode contingency. Those remain `ANALYSIS / MATERIALIZATION` gaps over retained raw, not physical acquisition gaps.

The retained gzip bodies are present in GitHub and provenance-complete, but the current GitHub text connector does not decode binary gzip bodies. That tooling boundary is not evidence for recollection and must never be converted into a human capture request.

### Provenance / raw retention — STABLE

The bridge head remains `e3676d79a38ac23e572af69d23d560c01bd6777d`, the same ledger point used by the old COVERAGE snapshot.

- 30 raw artifacts total;
- 28 mechanically successful gameplay raws;
- 2 collector/platform test raws excluded;
- complete task/status/result/raw identity for all 28 successful gameplay raws;
- failed acquisitions are never counted as samples;
- game-memory writes: 0.

### BASECAP / GEO / EFIELD / RAWMINE — CLOSED FOR GENERIC COLLECTION

- BASECAP v1: complete.
- GEO: P1 X/Y, P2/P3 structure, facing, and retained player-object top/bottom search closed; explicit advice is not to repeat the canonical scenes.
- EFIELD: bounded high-value mapping complete; no outstanding generic capture requirement.
- RAWMINE: current candidate-screen assignment complete; no active operator-gated task.

## Open frontier by gap class

### ANALYSIS / MATERIALIZATION

Existing retained bytes support more accounting, but current human-readable outputs do not safely expose these per-type tables:

1. lifecycle episode count per normalized type;
2. target dwell/occupancy P1/P2/P3 per normalized type;
3. structural attack/executor episode count per normalized type;
4. full normalized type × structural executor contingency table.

These are not capture requests.

### LABEL / SEMANTIC

Still UNKNOWN unless an authoritative source appears:

- stage;
- scene;
- wave;
- boss / ordinary;
- human enemy names;
- semantic ACTIVE/hitbox/damage cycle;
- exact WinKawaks-local move/attack identity.

Do not infer any of these from task names, rarity, or raw patterns.

### BROWSER VALIDATION

- T18 (0x12): WOF-052 remains the ordered post-anchor Browser discrimination gate, but current PM priorities no longer make it an Alpha blocker.
- T23 (0x17): Browser ordered evidence exists; do not spend repeated rooms merely to force scene appearance.
- Product release regression / identity guard / live retarget remain Product/MAINLINE gates, not COVERAGE capture work.

### PHYSICAL

A labeled full-game `BASECAP-SWEEP-*` corpus is physically absent. This matters to a future authoritative breadth denominator, but it is **not** currently a justified human recap because no single bounded Product/Beta/v1-critical scene has been identified that would close the gap at low cost.

## PM closure / stop decision

Current PM priorities explicitly mark **COVERAGE refresh complete / PARK** and set the project fastest path to Alpha QA -> real Browser acceptance -> Alpha release.

**human recap required: NO**

COVERAGE has reached the safe accounting boundary of current GitHub material. Do not ask for broad WinKawaks replay. Reopen only if later Beta/v1 work identifies one concrete residual coverage question that existing retained raw cannot answer.

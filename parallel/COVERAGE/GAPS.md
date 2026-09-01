# COVERAGE GAPS

Snapshot: `2026-09-01`

This document separates **physical-data gaps** from **label/materialization gaps**. A missing label or cross-tab is not automatically a request for new gameplay capture.

## P0 — LABEL_UNKNOWN: authoritative stage / scene / wave

Current gameplay raws are named by acquisition purpose (`baseline`, `retarget`, `geometry`, `attack`, etc.). Those names are not authoritative stage/scene/wave identities.

Status: **LABEL_UNKNOWN**

Impact:
- cannot build a trustworthy stage × scene × wave coverage matrix;
- cannot calculate scene-level set cover;
- cannot claim scene coverage for any Txx;
- unlabeled raw must not be assigned a scene from numeric RAM patterns.

Action: consume SWEEPATLAS or another authoritative labeling source if/when it appears. Do not rescan merely to make up names.

## P0 — LABEL_UNKNOWN: boss / ordinary enemy

No audited input currently provides an authoritative boss-vs-ordinary classification tied to capture/episode identity.

Status: **LABEL_UNKNOWN**

Action: wait for an authoritative atlas/label source, then join it to existing raw before considering recap.

## P0 — LABEL_UNKNOWN: semantic ACTIVE cycles

EFIELD establishes lifecycle and structural executor/attack-family behavior, but it does not establish a semantic hitbox/damage `ACTIVE` state.

Status: **LABEL_UNKNOWN**

Known:
- 1,604 global same-nonzero-type lifecycle episodes;
- 271 nonzero structural executor/attack-family episodes.

Unknown:
- semantic ACTIVE cycle count globally and per Txx.

Action: do not relabel structural `+0x73` episodes as semantic ACTIVE cycles.

## P1 — LABEL_UNKNOWN: per-Txx cross-tabs

The current read-only EFIELD outputs materialize:
- per-Txx sample counts;
- a global lifecycle episode total;
- aggregate attack/executor distributions;
- aggregate target distributions.

They do **not** materialize:
- lifecycle episodes per Txx;
- structural/semantic attack kinds per Txx;
- target P1/P2/P3 per Txx;
- scene coverage per Txx.

Status: **LABEL_UNKNOWN**

This is first an **analysis/materialization gap**, not a capture gap. Existing EFIELD raws should be exhausted before requesting more gameplay.

## P1 — LOW: low-density observed Txx

Coverage-only LOW threshold: fewer than 500 type-present samples.

| Txx | Samples |
|---|---:|
| T05 | 495 |
| T0D | 470 |
| T0C | 469 |
| T0E | 411 |
| T02 | 408 |
| T06 | 354 |
| T04 | 300 |
| T1D | 272 |
| T1C | 188 |
| T0F | 187 |
| T01 | 173 |
| T03 | 160 |
| T1F | 150 |
| T1E | 133 |

Status: **LOW**

These counts alone do not justify a full-game rescan. A targeted recap becomes rational only after stage/scene incidence is known and a small set of scenes can close several gaps at once.

## P1 — LOW: rare structural attack/executor family

`enemy+0x73 = 0x1E` occurs for **42 frames** in the current EFIELD corpus.

Status: **LOW**

Fine values contributing to this coarse family:
- `+0x6C = 0x70`: 14 frames
- `+0x6C = 0x78`: 28 frames

The semantic attack/rare-branch name is still **LABEL_UNKNOWN**. Do not design a gameplay recap around a guessed move name.

## P1 — MISSING: T23 in current EFIELD corpus

Current EFIELD census has **0 T23 samples**.

Status: **MISSING in the current EFIELD corpus only**

Important limits:
- the audited data do not establish the full-game expected Txx universe;
- zero T23 coverage is not a rule failure;
- this does not prove T23 exists in a missing stage;
- `T23` must not be confused with enemy byte offset `+0x23`.

No physical recap is authorized from this fact alone.

## P1 — LABEL_UNKNOWN: sequence family

`parallel/SEQMINER/**` is absent at the audited snapshot.

Status: **LABEL_UNKNOWN**

The current structural phase hierarchy is not a substitute for an ordered-sequence family atlas. Recompute this gap when SEQMINER arrives.

## P2 — CONFOUNDED: retained raws with weak intended manipulation/label isolation

Mechanically healthy raw can still be unusable for the dimension it was intended to isolate.

Current tracked cases include:
- `BASECAP-B12-facing-minimal...` — initial facing label noncanonical;
- `BASECAP-B13R-standing-attack-ungated...` — manual attack label noncanonical;
- `GEO-0008...` — intended P1 depth motion not isolated;
- `RAWMINE-001...` — requested attributable P1 depth signal not isolated;
- `GEO-0009...` — intended depth traverse insufficient;
- `GEO-0010...` / `GEO-0011...` — intended depth attribution calibration insufficient;
- `RAWMINE-004...` — intended attribution positive control absent;
- `GEO-0012...` — no controlled P2 trajectory isolated;
- `BASECAP-B40-P3...` — no usable P3 geometry dynamic in the current RAWMINE player-object interpretation.

Status: **CONFOUNDED for the stated intended dimension**, not globally invalid.

GEO owner-level geometry closure remains accepted; these historical flat/confounded attempts must not be interpreted as contradictions.

## P2 — provenance gaps on failed attempts

Seven failed gameplay acquisitions exist in `status/by_task/**` with no result/raw. Only `EFIELD-007` and `EFIELD-008` retain archived task specs; five failed status rows have no retained current/archive task spec.

Status: **CONFOUNDED provenance on failed attempts**

They are never counted as gameplay samples.

## Physical recap verdict

**No generic physical recap is currently justified.**

The dominant residuals are labels and analysis joins, while BASECAP/GEO/RAWMINE owner lanes already state that no generic re-acquisition is needed. SWEEPATLAS/SEQMINER are absent, so scene-level set-cover optimization cannot yet be computed without inventing labels.

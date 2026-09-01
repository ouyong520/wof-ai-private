# COVERAGE MATRIX

Snapshot: `2026-09-01`  
`wof-ai-private`: `204c3995ac9b1b04683ad3cbcfa8c8f7a51bad75`  
`wof-winkawaks-bridge`: `e3676d79a38ac23e572af69d23d560c01bd6777d`

This lane is an accounting/coverage view only. WinKawaks evidence is **local discovery evidence**, not Browser production proof. Browser production-shadow authority remains with MAINLINE.

## Status vocabulary

| Status | Meaning |
|---|---|
| GOOD | Direct usable coverage exists for the stated dimension. |
| LOW | Direct evidence exists but is sparse. |
| MISSING | No current evidence exists for an explicitly requested/known candidate. |
| CONFOUNDED | Raw/status exists, but the intended manipulation/attribution does not isolate the requested dimension. |
| LABEL_UNKNOWN | Evidence may exist, but the semantic label or requested cross-tab is not materialized. |

`GOOD`/`LOW` are coverage labels, not correctness or rule-proof labels. Zero coverage never means a rule failed.

## Audit totals

- Raw artifacts in `captures/`: **30**
- Mechanically successful gameplay raws after excluding two collector/platform test raws: **28**
- Successful gameplay capture identities with complete `task + status + result + raw` provenance: **28 / 28**
- Failed gameplay acquisition attempts retained in status: **7**
- Failed attempts with an archived task spec: **2**
- Failed attempts with status only and no retained current/archive task spec: **5**
- Deduplication key: canonical gameplay `taskId` / raw filename identity. Reuse of the same raw by BASECAP/GEO/EFIELD/RAWMINE does **not** create another capture.
- `parallel/SWEEPATLAS/**`: absent at this snapshot.
- `parallel/SEQMINER/**`: absent at this snapshot.

## Global dimension matrix

| Dimension | Status | Current evidence / limitation |
|---|---|---|
| stage | LABEL_UNKNOWN | No authoritative stage labels are present in the audited corpus. |
| scene | LABEL_UNKNOWN | Task names describe acquisition conditions, not authoritative game scenes. |
| wave | LABEL_UNKNOWN | No authoritative wave labels are present. |
| capture | GOOD | 28 deduplicated mechanically successful gameplay captures retained. |
| player count/config | LABEL_UNKNOWN | Not consistently materialized as an authoritative per-capture label. |
| enemy Txx | GOOD / LOW | 31 observed Txx codes have a sample census; 14 are LOW by the coverage-only threshold below. |
| attack | GOOD + LABEL_UNKNOWN | Structural executor/attack-family values are well represented, but semantic attack names are not established here. |
| semantic ACTIVE cycle count | LABEL_UNKNOWN | Current EFIELD outputs do not establish a semantic hitbox/damage ACTIVE state. |
| target P1/P2/P3 | GOOD | Aggregate live-target and association evidence covers P1/P2/P3 across all 60,271 type-present samples. |
| left/right/geometry diversity | GOOD | GEO owner lane has closed P1 X/Y, P2/P3 same-offset structure, facing, and top/bottom; some historical intended manipulations remain CONFOUNDED. |
| sequence family | LABEL_UNKNOWN | No SEQMINER output exists at this snapshot. |
| rare branch | LOW | Structural coarse family `enemy+0x73 = 0x1E` has only 42 frames. Semantic branch naming remains unknown. |
| boss/ordinary enemy | LABEL_UNKNOWN | No authoritative boss/ordinary atlas exists in current inputs. |
| raw artifact availability | GOOD | All 28 successful gameplay captures have retained raw artifacts. |
| label quality | LABEL_UNKNOWN | Several acquisition-condition labels are good, but stage/scene/wave/boss and multiple semantic axes are absent. |
| capture validity | GOOD | Mechanical/provenance validity is complete for successful captures; condition-level confounds are tracked separately. |

## EFIELD aggregate evidence

The current seven valid EFIELD captures contain:

- **23,400 frames**
- **468,000 enemy-object samples** (`20 enemy slots/frame`)
- **60,271 type-present samples**
- **407,729 type-absent samples**
- **1,604 contiguous same-nonzero-type lifecycle episodes**
- **74 type-enter + 74 type-exit boundaries** in the narrower lifecycle edge analysis
- **271 nonzero structural executor/attack-family episodes**
- **44,905 nonzero structural executor/attack-family frames**
- **8 confirmed live-target changes**
- **2 WinKawaks process sessions**
- **0 game-memory writes**

The global lifecycle episode total is materialized, but the audited read-only outputs do **not** materialize a per-Txx lifecycle-episode table. The same is true for per-Txx attack, target, and scene cross-tabs. Those cells are therefore `LABEL_UNKNOWN`, never zero.

## Enemy Txx coverage

Coverage-only sample heuristic used by COVERAGE:

- `GOOD`: `>= 500` type-present samples
- `LOW`: `1..499` samples
- `MISSING`: `0` samples for an explicitly requested/known candidate

This threshold is only for prioritizing evidence density.

| Txx | Samples | Sample status | Lifecycle episodes | Episode status | Semantic ACTIVE cycles | ACTIVE status | Attack kinds | Attack status | Target P1/P2/P3 | Target status | Scene coverage | Scene status |
|---|---:|---|---:|---|---:|---|---|---|---|---|---|---|
| T18 | 12,866 | GOOD | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN |
| T10 | 9,210 | GOOD | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN |
| T08 | 7,293 | GOOD | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN |
| T19 | 6,807 | GOOD | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN |
| T09 | 2,894 | GOOD | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN |
| T07 | 2,670 | GOOD | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN |
| T16 | 2,309 | GOOD | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN |
| T15 | 2,285 | GOOD | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN |
| T17 | 2,140 | GOOD | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN |
| T11 | 2,002 | GOOD | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN |
| T0B | 1,102 | GOOD | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN |
| T1A | 1,060 | GOOD | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN |
| T13 | 1,013 | GOOD | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN |
| T14 | 686 | GOOD | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN |
| T0A | 645 | GOOD | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN |
| T1B | 591 | GOOD | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN |
| T12 | 528 | GOOD | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN |
| T05 | 495 | LOW | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN |
| T0D | 470 | LOW | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN |
| T0C | 469 | LOW | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN |
| T0E | 411 | LOW | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN |
| T02 | 408 | LOW | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN |
| T06 | 354 | LOW | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN |
| T04 | 300 | LOW | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN |
| T1D | 272 | LOW | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN |
| T1C | 188 | LOW | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN |
| T0F | 187 | LOW | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN |
| T01 | 173 | LOW | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN |
| T03 | 160 | LOW | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN |
| T1F | 150 | LOW | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN |
| T1E | 133 | LOW | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN |
| T23 | 0 | MISSING | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN | — | LABEL_UNKNOWN |

`T23` is included only because it is an explicit coverage exemplar in the COVERAGE brief. It has zero samples in the current EFIELD corpus, but the audited data do not establish that `T23` belongs to the expected full-game type universe. Therefore `T23 = MISSING in current corpus` is **not** rule failure and is **not** by itself a rescan trigger. `T23` must also not be confused with byte offset `+0x23`; EFIELD's type field is the U8 value at enemy `+0x24`.

## Structural attack/executor evidence

These are raw structural families, not semantic move names and not semantic ACTIVE states.

| Field | Value | Frames | Coverage | Semantic label |
|---|---:|---:|---|---|
| enemy+0x73 | 0x00 | 15,366 | GOOD | LABEL_UNKNOWN |
| enemy+0x73 | 0x0A | 27,486 | GOOD | LABEL_UNKNOWN |
| enemy+0x73 | 0x1B | 16,651 | GOOD | LABEL_UNKNOWN |
| enemy+0x73 | 0x0B | 726 | GOOD | LABEL_UNKNOWN |
| enemy+0x73 | 0x1E | 42 | LOW | LABEL_UNKNOWN |

Fine structural values at enemy `+0x6C`:

`00=15,366`, `E0=27,486`, `40=11,432`, `50=2,358`, `48=1,517`, `58=1,344`, `90=726`, `78=28`, `70=14`.

Observed structural mapping:
`00→00`, `E0→0A`, `40/48/50/58→1B`, `90→0B`, `70/78→1E`.

## Target coverage

Across all **60,271 type-present samples**:

| Layer | P1 | P2 | P3 | Status |
|---|---:|---:|---:|---|
| live target | 46,865 | 2,967 | 10,439 | GOOD |
| association pointer | 18,091 | 17,494 | 24,686 | GOOD |

There are **8 confirmed live-target changes**. This establishes aggregate P1/P2/P3 coverage. It does **not** establish the per-Txx target cross-tab, so per-type target cells remain `LABEL_UNKNOWN`.

## Successful gameplay capture inventory

Every row below has a current matching task, status, result, and raw artifact. `Mechanical = GOOD` means the Collector result/raw was retained and valid mechanically. `Intended dimension` is separate so a healthy raw can still be `CONFOUNDED` for the manipulation it was meant to isolate.

| Capture/taskId | Lane | Mechanical | Intended dimension | stage | scene/wave | player config | Raw | Coverage note |
|---|---|---|---|---|---|---|---|---|
| `BASECAP-B00-idle-8s60-20260901-0510Z` | BASECAP | GOOD | GOOD | LABEL_UNKNOWN | LABEL_UNKNOWN | LABEL_UNKNOWN | `captures/BASECAP-B00-idle-8s60-20260901-0510Z.jsonl.gz` | mechanically successful retained gameplay raw |
| `BASECAP-B12-facing-minimal-8s60-20260901-0518Z` | BASECAP | GOOD | CONFOUNDED | LABEL_UNKNOWN | LABEL_UNKNOWN | LABEL_UNKNOWN | `captures/BASECAP-B12-facing-minimal-8s60-20260901-0518Z.jsonl.gz` | initial facing label is noncanonical because READY→capture timing was unsafe |
| `BASECAP-B12R-facing-delayed-30s60-20260901-0527Z` | BASECAP | GOOD | GOOD | LABEL_UNKNOWN | LABEL_UNKNOWN | LABEL_UNKNOWN | `captures/BASECAP-B12R-facing-delayed-30s60-20260901-0527Z.jsonl.gz` | canonical facing acquisition |
| `BASECAP-B13-attack-12s60-20260901-0558Z` | BASECAP | GOOD | GOOD | LABEL_UNKNOWN | LABEL_UNKNOWN | LABEL_UNKNOWN | `captures/BASECAP-B13-attack-12s60-20260901-0558Z.jsonl.gz` | canonical attack acquisition |
| `BASECAP-B13R-standing-attack-ungated-60s60-20260901-0543Z` | BASECAP | GOOD | CONFOUNDED | LABEL_UNKNOWN | LABEL_UNKNOWN | LABEL_UNKNOWN | `captures/BASECAP-B13R-standing-attack-ungated-60s60-20260901-0543Z.jsonl.gz` | manual attack label is noncanonical because operator gate was disabled |
| `BASECAP-B20-camera-scroll-16s60-20260901-0559Z` | BASECAP | GOOD | GOOD | LABEL_UNKNOWN | LABEL_UNKNOWN | LABEL_UNKNOWN | `captures/BASECAP-B20-camera-scroll-16s60-20260901-0559Z.jsonl.gz` | mechanically successful retained gameplay raw |
| `BASECAP-B40-P2-xy-16s60-20260901-0600Z` | BASECAP | GOOD | GOOD | LABEL_UNKNOWN | LABEL_UNKNOWN | LABEL_UNKNOWN | `captures/BASECAP-B40-P2-xy-16s60-20260901-0600Z.jsonl.gz` | mechanically successful retained gameplay raw |
| `BASECAP-B40-P3-xy-16s60-20260901-0601Z` | BASECAP | GOOD | CONFOUNDED | LABEL_UNKNOWN | LABEL_UNKNOWN | LABEL_UNKNOWN | `captures/BASECAP-B40-P3-xy-16s60-20260901-0601Z.jsonl.gz` | canonical acquisition, but no usable P3 geometry dynamic in current RAWMINE interpretation |
| `EFIELD-001-baseline-30s60` | EFIELD | GOOD | GOOD | LABEL_UNKNOWN | LABEL_UNKNOWN | LABEL_UNKNOWN | `captures/EFIELD-001-baseline-30s60.jsonl.gz` | mechanically successful retained gameplay raw |
| `EFIELD-002-natural-diversity-60s60` | EFIELD | GOOD | GOOD | LABEL_UNKNOWN | LABEL_UNKNOWN | LABEL_UNKNOWN | `captures/EFIELD-002-natural-diversity-60s60.jsonl.gz` | mechanically successful retained gameplay raw |
| `EFIELD-003-passive-retarget-60s60` | EFIELD | GOOD | GOOD | LABEL_UNKNOWN | LABEL_UNKNOWN | LABEL_UNKNOWN | `captures/EFIELD-003-passive-retarget-60s60.jsonl.gz` | mechanically successful retained gameplay raw |
| `EFIELD-004-passive-lifecycle-retarget-60s60` | EFIELD | GOOD | GOOD | LABEL_UNKNOWN | LABEL_UNKNOWN | LABEL_UNKNOWN | `captures/EFIELD-004-passive-lifecycle-retarget-60s60.jsonl.gz` | mechanically successful retained gameplay raw |
| `EFIELD-005-cross-session-target-60s60` | EFIELD | GOOD | GOOD | LABEL_UNKNOWN | LABEL_UNKNOWN | LABEL_UNKNOWN | `captures/EFIELD-005-cross-session-target-60s60.jsonl.gz` | mechanically successful retained gameplay raw |
| `EFIELD-005R-cross-session-target-60s60` | EFIELD | GOOD | GOOD | LABEL_UNKNOWN | LABEL_UNKNOWN | LABEL_UNKNOWN | `captures/EFIELD-005R-cross-session-target-60s60.jsonl.gz` | mechanically successful retained gameplay raw |
| `EFIELD-006-cross-session-lifecycle-target-60s60` | EFIELD | GOOD | GOOD | LABEL_UNKNOWN | LABEL_UNKNOWN | LABEL_UNKNOWN | `captures/EFIELD-006-cross-session-lifecycle-target-60s60.jsonl.gz` | mechanically successful retained gameplay raw |
| `GEO-0001-dynamic-baseline-20260831-1517Z` | GEO | GOOD | GOOD | LABEL_UNKNOWN | LABEL_UNKNOWN | LABEL_UNKNOWN | `captures/GEO-0001-dynamic-baseline-20260831-1517Z.jsonl.gz` | mechanically successful retained gameplay raw |
| `GEO-0003-natural-geometry-10s60-20260831-1549Z` | GEO | GOOD | GOOD | LABEL_UNKNOWN | LABEL_UNKNOWN | LABEL_UNKNOWN | `captures/GEO-0003-natural-geometry-10s60-20260831-1549Z.jsonl.gz` | mechanically successful retained gameplay raw |
| `GEO-0004-action-diversity-10s60-20260831-1604Z` | GEO | GOOD | GOOD | LABEL_UNKNOWN | LABEL_UNKNOWN | LABEL_UNKNOWN | `captures/GEO-0004-action-diversity-10s60-20260831-1604Z.jsonl.gz` | mechanically successful retained gameplay raw |
| `GEO-0006-passive-geometry-camera-20s60-20260831-1657Z` | GEO | GOOD | GOOD | LABEL_UNKNOWN | LABEL_UNKNOWN | LABEL_UNKNOWN | `captures/GEO-0006-passive-geometry-camera-20s60-20260831-1657Z.jsonl.gz` | mechanically successful retained gameplay raw |
| `GEO-0008-p1-depth-only-5s60-20260831-2115Z` | GEO | GOOD | CONFOUNDED | LABEL_UNKNOWN | LABEL_UNKNOWN | LABEL_UNKNOWN | `captures/GEO-0008-p1-depth-only-5s60-20260831-2115Z.jsonl.gz` | intended P1 depth manipulation not visible |
| `GEO-0009-p1-depth-visible-traverse-8s60-20260901-0024Z` | GEO | GOOD | CONFOUNDED | LABEL_UNKNOWN | LABEL_UNKNOWN | LABEL_UNKNOWN | `captures/GEO-0009-p1-depth-visible-traverse-8s60-20260901-0024Z.jsonl.gz` | intended depth manipulation remained insufficient |
| `GEO-0010-p1-attribution-depth-calibration-10s60-20260901-0033Z` | GEO | GOOD | CONFOUNDED | LABEL_UNKNOWN | LABEL_UNKNOWN | LABEL_UNKNOWN | `captures/GEO-0010-p1-attribution-depth-calibration-10s60-20260901-0033Z.jsonl.gz` | intended depth attribution calibration remained insufficient |
| `GEO-0011-p1-attribution-depth-calibration-10s60-20260901-0038Z` | GEO | GOOD | CONFOUNDED | LABEL_UNKNOWN | LABEL_UNKNOWN | LABEL_UNKNOWN | `captures/GEO-0011-p1-attribution-depth-calibration-10s60-20260901-0038Z.jsonl.gz` | intended depth attribution calibration remained insufficient |
| `GEO-0012-p2-same-xy-offsets-12s60-20260901-0054Z` | GEO | GOOD | CONFOUNDED | LABEL_UNKNOWN | LABEL_UNKNOWN | LABEL_UNKNOWN | `captures/GEO-0012-p2-same-xy-offsets-12s60-20260901-0054Z.jsonl.gz` | mechanically healthy, but no controlled P2 trajectory was isolated |
| `GEO-0013-p2-attribution-depth-long-35s60-20260901-0104Z` | GEO | GOOD | GOOD | LABEL_UNKNOWN | LABEL_UNKNOWN | LABEL_UNKNOWN | `captures/GEO-0013-p2-attribution-depth-long-35s60-20260901-0104Z.jsonl.gz` | mechanically successful retained gameplay raw |
| `RAWMINE-001-p1-depth-retry-8s60-20260831-2126Z` | RAWMINE | GOOD | CONFOUNDED | LABEL_UNKNOWN | LABEL_UNKNOWN | LABEL_UNKNOWN | `captures/RAWMINE-001-p1-depth-retry-8s60-20260831-2126Z.jsonl.gz` | requested attributable P1 depth signal was not isolated |
| `RAWMINE-004-p1-attribution-depth-redo-10s60-20260901-0037Z` | RAWMINE | GOOD | CONFOUNDED | LABEL_UNKNOWN | LABEL_UNKNOWN | LABEL_UNKNOWN | `captures/RAWMINE-004-p1-attribution-depth-redo-10s60-20260901-0037Z.jsonl.gz` | intended attribution positive control was absent |
| `RAWMINE-005-p1-depth-wide-window-40s60-20260901-0048Z` | RAWMINE | GOOD | GOOD | LABEL_UNKNOWN | LABEL_UNKNOWN | LABEL_UNKNOWN | `captures/RAWMINE-005-p1-depth-wide-window-40s60-20260901-0048Z.jsonl.gz` | accepted P1 depth confirmation |

Important canonical/noncanonical distinctions:

- Initial `BASECAP-B12-facing-minimal...` raw is retained but noncanonical for facing because the old READY→capture timing was unsafe. `BASECAP-B12R-facing-delayed...` is the canonical facing acquisition.
- `BASECAP-B13R-standing-attack-ungated...` is retained but noncanonical for the manual attack condition because the operator gate was disabled. `BASECAP-B13-attack-12s60...` is the canonical confirmed attack acquisition.
- GEO/RAWMINE negative or flat intended manipulations are not field-absence proofs. GEO's owner lane nevertheless closes P1 X/Y and P2/P3 same-offset structure from pooled accepted evidence.
- `RAWMINE-005...` is accepted by GEO as useful P1 depth confirmation.
- `BASECAP-B40-P3...` is a mechanically valid/canonical acquisition condition; only its current player-object geometry dynamic is CONFOUNDED in RAWMINE's interpretation.

## Failed gameplay acquisition attempts

Failed acquisitions are preserved as provenance, but never counted as gameplay samples or negative semantic evidence.

| taskId | Lane | Retained task spec | Result | Raw | Status | Note |
|---|---|---|---|---|---|---|
| `BASECAP-B13-standing-attack-delayed-30s60-20260901-0536Z` | BASECAP | no | no | no | CONFOUNDED | acquisition failed; status retained, no result/raw |
| `EFIELD-007-passive-proximity-association-60s60` | EFIELD | yes | no | no | CONFOUNDED | acquisition failed; archived task spec + status retained |
| `EFIELD-008-discovery-probe-snapshot` | EFIELD | yes | no | no | CONFOUNDED | discovery acquisition failed; archived task spec + status retained |
| `EFIELD-009-discovery-candidate-diagnostic-snapshot` | EFIELD | no | no | no | CONFOUNDED | discovery acquisition failed; status retained only |
| `GEO-0002-p1-facing-right-static-20260831-1534Z` | GEO | no | no | no | CONFOUNDED | acquisition failed; status retained only |
| `GEO-0005-camera-scroll-right-8s60-20260831-1619Z` | GEO | no | no | no | CONFOUNDED | acquisition failed; status retained only |
| `GEO-0007-p1-horizontal-only-5s60-20260831-2038Z` | GEO | no | no | no | CONFOUNDED | acquisition failed; status retained only |

The two archived task specs are `EFIELD-007` and `EFIELD-008`; the remaining five failed status rows do not have a retained current/archive task spec in the audited tree.

## Current coverage verdict

The project already has substantial raw, geometry, lifecycle, structural attack/executor, and aggregate target evidence. The largest unresolved coverage dimensions are **authoritative labels and cross-tabs**, especially stage/scene/wave, boss/ordinary, semantic ACTIVE, sequence-family labels, and per-Txx lifecycle/attack/target/scene breakdowns.

Accordingly, the current minimum physical recap set is **empty**. No broad WinKawaks resweep and no new Collector batch is justified by this audit alone.

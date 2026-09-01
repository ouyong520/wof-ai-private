# BASECAP Reusable Capture Catalog

Updated: 2026-09-01

This file is the authoritative index of reusable labeled WinKawaks raw captures for local discovery work.

## Reuse rule

Before GEO, EFIELD, RAWMINE, BASECAP, or another local research lane submits a basic Collector task, inspect this catalog first. Reuse a `VALID` entry when its material acquisition conditions match the current question.

Do not reuse an entry whose scene label is uncertain or whose relevant confounder invalidates the requested comparison.

A healthy retained raw is not automatically a canonical labeled baseline. BASECAP promotes a capture only when the acquisition condition can be recovered from authoritative task/result/artifact metadata. Never infer operator actions from raw values.

## Dataset identity

A capture is identified by its unique Collector `taskId`.

Preferred retained raw path:

```text
captures/<taskId>.jsonl.gz
```

Task IDs are immutable and must never be reused. A repeated capture receives a new task ID. Historical raw artifacts are never overwritten.

## Entry template

Copy this section for each reusable capture:

```text
### <captureId/taskId>
status: VALID | SUPERSEDED | INVALID
rawPath: captures/<taskId>.jsonl.gz
capturedAtUtc:
taskBlobSha:
ROM/game/session:
playerOccupancy:
preCaptureScene:
operatorGate:
operatorActionDuringCapture:
durationSeconds:
hz:
layout: P1 + P2 + P3 + 20 enemies; stride 0xE0; 5152 bytes/frame
intentionalChangedVariables:
intentionalHeldStableVariables:
intendedReuseQuestions:
knownConfounders:
labelSourceEvidence:
supersedes:
supersededBy:
notes:
```

## Phase-1 coverage snapshot

| Scene | Coverage | Current evidence / action |
| --- | --- | --- |
| B00 stationary idle | MISSING canonical controlled capture | No retained raw has an authoritative idle-only operator label. This is the first new BASECAP gap to fill. |
| B10 P1 horizontal-only | MISSING canonical controlled capture | Historical `GEO-0007-p1-horizontal-only-5s60-20260831-2038Z` never produced a retained raw. `RAWMINE-005` mixes horizontal and depth phases and therefore is not a pure B10 baseline. |
| B11 P1 floor/depth-only | COVERED | `GEO-0008-p1-depth-only-5s60-20260831-2115Z` is registered below as `VALID`; do not recapture B11 merely for reuse. |
| B12 P1 facing / minimal displacement | MISSING canonical controlled capture | Historical facing attempt `GEO-0002-p1-facing-right-static-20260831-1534Z` did not produce a retained raw. |
| B13 P1 action/animation diversity with position held stable | MISSING canonical controlled capture | `GEO-0004-action-diversity-10s60-20260831-1604Z` is retained but was ungated; exact operator actions and position-stability conditions are not recoverable strongly enough for a canonical B13 label. |
| B20 camera scroll discriminator | MISSING canonical controlled capture | Historical `GEO-0005-camera-scroll-right-8s60-20260831-1619Z` did not produce a retained raw. `GEO-0006` is passive/opportunistic and does not prove that a camera-scroll episode occurred. |
| B30 ordinary combat diversity | SUPPORTING CORPUS PRESENT | Retained EFIELD natural-gameplay runs provide broad combat/diversity data. They are useful supporting data but are not promoted as a controlled combat baseline without stronger scene labels. |
| B31 enemy spawn / active / death lifecycle | COVERED AT RETAINED-CORPUS LEVEL | The seven retained EFIELD runs contain 74 type-enter and 74 type-exit lifecycle boundaries across 23,400 frames. No generic lifecycle recapture is justified. Per-capture event localization may be added later if a consumer needs one specific raw. |
| B32 enemy target / retarget diversity | COVERED AT RETAINED-CORPUS LEVEL | Existing EFIELD work reports confirmed live-target changes in the retained corpus. Do not submit another generic retarget capture merely for diversity; localize exact events to retained raws first if a consumer needs a single canonical event set. |
| B40 P2/P3 structure replication | DEFERRED | Retained GEO P2 captures exist, but BASECAP defers B40 until P1 foundational geometry scenes are sufficient. |

## Existing-capture audit

### Retained EFIELD corpus

Retained raws currently include:

- `captures/EFIELD-001-baseline-30s60.jsonl.gz`
- `captures/EFIELD-002-natural-diversity-60s60.jsonl.gz`
- `captures/EFIELD-003-passive-retarget-60s60.jsonl.gz`
- `captures/EFIELD-004-passive-lifecycle-retarget-60s60.jsonl.gz`
- `captures/EFIELD-005-cross-session-target-60s60.jsonl.gz`
- `captures/EFIELD-005R-cross-session-target-60s60.jsonl.gz`
- `captures/EFIELD-006-cross-session-lifecycle-target-60s60.jsonl.gz`

Audit disposition: retained and reusable as natural-gameplay/diversity corpus. These runs are not silently relabeled as operator-controlled B00/B10/B11/B12/B13/B20 scenes. Aggregate EFIELD analysis establishes useful B31/B32 event coverage; individual per-run event localization remains separate from scene labeling.

### Retained GEO corpus

Retained raws include `GEO-0001`, `GEO-0003`, `GEO-0004`, `GEO-0006`, `GEO-0008`, `GEO-0009`, `GEO-0010`, `GEO-0011`, `GEO-0012`, and `GEO-0013` captures.

Audit disposition:

- `GEO-0008` has a sufficiently explicit operator gate and a healthy retained result; it is promoted below as canonical B11.
- `GEO-0009`, `GEO-0010`, and `GEO-0011` are retained depth/calibration-family evidence. Because B11 is already covered, BASECAP does not create redundant canonical entries merely to increase count.
- `GEO-0001`, `GEO-0003`, `GEO-0004`, and `GEO-0006` remain useful exploratory/passive evidence, but their labels are not strong enough to substitute for missing controlled B00/B10/B12/B13/B20 captures.
- `GEO-0012` and `GEO-0013` are retained P2-oriented evidence and are deferred with B40.

Historical tasks `GEO-0002-p1-facing-right-static-20260831-1534Z`, `GEO-0005-camera-scroll-right-8s60-20260831-1619Z`, and `GEO-0007-p1-horizontal-only-5s60-20260831-2038Z` have no retained raw/result suitable for BASECAP. They must never be reused as task IDs and cannot be canonical baselines.

### Retained RAWMINE corpus

Retained raws include:

- `captures/RAWMINE-001-p1-depth-retry-8s60-20260831-2126Z.jsonl.gz`
- `captures/RAWMINE-004-p1-attribution-depth-redo-10s60-20260901-0037Z.jsonl.gz`
- `captures/RAWMINE-005-p1-depth-wide-window-40s60-20260901-0048Z.jsonl.gz`

Audit disposition: preserve and reuse as depth/attribution evidence. In particular, `RAWMINE-005` deliberately contains a horizontal calibration phase followed by a depth phase, so it must not be relabeled as a pure B10 or pure B11 capture.

## Canonical reusable captures

### GEO-0008-p1-depth-only-5s60-20260831-2115Z
status: VALID  
rawPath: `captures/GEO-0008-p1-depth-only-5s60-20260831-2115Z.jsonl.gz`  
capturedAtUtc: `2026-08-31T21:19:12.604662+00:00` (authoritative Collector completion timestamp; a separate capture-start timestamp is not retained in the run result)  
taskBlobSha: `177ca63865714623037e8ff1a097a7698e3bf75e`  
ROM/game/session: WOF WinKawaks local-discovery capture; exact ROM filename/build identifier is not separately retained in the task/result. Collector session: `WinKawaks.exe`, pid `30144`, RAM base `0x8E1FDFC`, mapping `xor3`, fresh discovery method `immutable-player-structure-v2`, unique candidate, cached RAM base not used as discovery input.  
playerOccupancy: P1 is the only intentionally controlled player. P2/P3 were explicitly required to remain untouched; their joined/occupied state is not separately recorded by authoritative metadata.  
preCaptureScene: No authoritative stage/room/coordinate label was recorded. Immediately before the controlled action, the operator was required to run `READY_WOF_TASK.bat`; the task is labeled specifically as the P1 depth-only Y discriminator.  
operatorGate: `required=true`; label `GEO P1 depth-only Y discriminator`. Instructions: `P1 only: repeatedly move UP then DOWN for about 5 seconds. Do not press LEFT/RIGHT, jump, attack, or any other action. Leave P2/P3 untouched.` Then: `Run READY_WOF_TASK.bat immediately before starting that one action.`  
operatorActionDuringCapture: Repeated P1 UP/DOWN movement for about 5 seconds only; no LEFT/RIGHT, jump, attack, or other action; P2/P3 untouched.  
durationSeconds: `5.0` requested; `300` captured frames  
hz: `60.0` target; `60.005` achieved  
layout: P1 + P2 + P3 + 20 enemies; stride `0xE0`; `5152` bytes/frame  
intentionalChangedVariables: P1 floor/depth position under repeated UP/DOWN-only traversal.  
intentionalHeldStableVariables: Horizontal input intentionally absent; jump/attack/other actions absent; P2/P3 untouched. Task purpose explicitly requested reconstructed X and Z to remain stable apart from incidental state noise.  
intendedReuseQuestions: B11 P1 floor/depth-only baseline; P1 depth-versus-horizontal discrimination; candidate screening conditioned on no LEFT/RIGHT input; geometry-field comparisons needing a controlled depth-motion reference.  
knownConfounders: Exact stage/room, exact ROM identifier, and P2/P3 occupancy are not separately retained. Operator compliance is supported by the authoritative gated task definition rather than independent video telemetry. Incidental animation/state noise was explicitly anticipated by the original task.  
labelSourceEvidence: authoritative queue task `tasks/queue/GEO-0008-p1-depth-only-5s60-20260831-2115Z.json` bound to task blob SHA `177ca63865714623037e8ff1a097a7698e3bf75e`; authoritative PASS result `results/by_task/GEO-0008-p1-depth-only-5s60-20260831-2115Z.json`; retained raw artifact path above. No action label is inferred from raw numeric values.  
supersedes: none  
supersededBy: none  
notes: Result status `PASS`; `readOnly=true`; `writesGameMemory=false`; raw stream uploaded; `readErrors=0`; `frameSizeErrors=0`; `273` distinct raw frames; state change observed. This capture is sufficient for B11 reuse and should be preferred over requesting another generic P1 depth-only capture.

## Pending collection policy

BASECAP fills one true gap at a time. A queued task is not a `VALID` catalog entry until its authoritative result is `PASS`, the task blob SHA matches, the retained gzip raw exists at `captures/<taskId>.jsonl.gz`, frame integrity is healthy, and the acquisition label is supported by task/operator metadata.

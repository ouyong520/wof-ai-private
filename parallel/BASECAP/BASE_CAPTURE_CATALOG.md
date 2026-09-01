# BASECAP Reusable Capture Catalog

Updated: 2026-09-01

Authoritative index for reusable labeled WinKawaks raw captures. Reuse before recapture. Never infer operator actions from raw numbers alone. Collector PASS proves mechanical capture health, not that a requested human manipulation succeeded.

Raw identity is immutable:

```text
captures/<taskId>.jsonl.gz
```

Never reuse a task ID or overwrite historical raw.

## Phase-1 coverage

| Scene | State | Canonical/reuse source |
| --- | --- | --- |
| B00 stationary idle | **COVERED / VALID** | `BASECAP-B00-idle-8s60-20260901-0510Z`; gated stationary no-input baseline, 480 frames, retained raw. |
| B10 P1 horizontal-only | **COVERED AS LABELED PHASE** | `RAWMINE-005-p1-depth-wide-window-40s60-20260901-0048Z`, operator-confirmed first phase: visible repeated RIGHT/LEFT for roughly 15 s; no attack/jump/extra action; P2/P3 untouched. |
| B11 P1 floor/depth-only | **COVERED** | Same `RAWMINE-005`, operator-confirmed second phase: visible repeated UP/DOWN for roughly 20 s; P2/P3 untouched. GEO treats this as the closing P1 Y/depth run. |
| B12 facing/minimal displacement | **MISSING** | Old facing task has no retained canonical raw. Do not substitute large horizontal traversal. |
| B13 action/animation diversity with position stable | **MISSING** | `GEO-0004` is ungated; exact actions/position stability cannot be recovered reliably enough. |
| B20 camera-scroll discriminator | **MISSING** | Old gated camera task has no retained canonical raw; passive `GEO-0006` does not prove a scroll episode occurred. |
| B30 ordinary gameplay/combat diversity | **COVERED for natural-gameplay diversity** | `EFIELD-003-passive-retarget-60s60`. Do not reinterpret it as a tightly controlled attack sequence. |
| B31 enemy lifecycle diversity | **COVERED for typed-enemy episode enter/exit diversity** | `EFIELD-003`: 11 type-enter + 11 type-exit edges. Do not rename these exact edges as semantic spawn/death without EFIELD evidence. |
| B32 target/retarget diversity | **COVERED** | `EFIELD-003`: known-player retargets localized at frames 492, 1827, 3322. |
| B40 P2/P3 structure replication | **DEFERRED** | Retained P2 GEO raws exist; defer until foundational P1 scene suite is sufficient. |

## VALID reusable captures

### BASECAP-B00-idle-8s60-20260901-0510Z
status: VALID  
rawPath: `captures/BASECAP-B00-idle-8s60-20260901-0510Z.jsonl.gz`  
capturedAtUtc: `2026-09-01T05:17:05.567887+00:00` (Collector completion timestamp)  
taskBlobSha: `9743cf0a1762b1d0f595cb2639e1ffe1f8b50bb8`  
ROM/game/session: WOF WinKawaks local-discovery capture; exact ROM filename/build not separately retained. Collector session: `WinKawaks.exe`, pid `6968`, RAM base `0xB1AFDFC`, mapping `xor3`, fresh discovery `immutable-player-structure-v2`, unique candidate, cached RAM base not used as discovery input.  
playerOccupancy: P1 intentionally prepared as the controlled/observed player. P2/P3 were explicitly required to remain untouched; exact joined/occupied state is not separately recorded.  
preCaptureScene: P1 placed in a safe place with no combat and no intentional camera scrolling; P2/P3 untouched.  
operatorGate: `required=true`; label `BASECAP B00 stationary idle`. Operator had to prepare the scene, run `READY_WOF_TASK.bat`, then provide no gameplay input for about 8 seconds.  
operatorActionDuringCapture: no movement, attack, jump, or other gameplay controls for about 8 seconds; P2/P3 untouched.  
durationSeconds: `8.0`; `480` frames  
hz: target `60.0`; achieved `59.951`  
layout: P1 + P2 + P3 + 20 enemies; stride `0xE0`; 5152 bytes/frame  
intentionalChangedVariables: none at operator-input level; this is a stationary/no-input baseline.  
intentionalHeldStableVariables: all intentional P1 gameplay controls absent; no intentional combat or camera scroll; P2/P3 untouched.  
intendedReuseQuestions: B00 idle/no-input baseline; background animation/timer/noise screening; comparison against controlled movement/action captures; GEO/RAWMINE/EFIELD change-frequency baselining.  
knownConfounders: `distinctRawFrameCount=453` and `stateChangeObserved=true`, so internal animation/timers/enemy/background state still changed despite no operator input; this is expected and must not be mislabeled as a bytewise static frame. Exact stage/room, ROM build, and P2/P3 occupancy are not separately retained. Operator compliance is supported by the gated acquisition instructions, not independent video telemetry.  
labelSourceEvidence: authoritative queue task `tasks/queue/BASECAP-B00-idle-8s60-20260901-0510Z.json` with matching task blob SHA; authoritative PASS result `results/by_task/BASECAP-B00-idle-8s60-20260901-0510Z.json`; retained raw artifact at the path above. No scene label is inferred from raw numeric values.  
supersedes: none  
supersededBy: none  
notes: result `PASS`; `readOnly=true`; `writesGameMemory=false`; raw uploaded; `readErrors=0`; `frameSizeErrors=0`; original stream bytes `5071909`; original SHA256 `c034bd3444ca6d771dbaeee1fb342117823bae210edfe7903c5d3875f980151a`; compressed bytes `56792`; compressed SHA256 `60c41b513e74af0994cefe4d7e780b6bf28e62e291166db5f228dd8c8dd7a537`; retained content SHA `50973af7f1eae740bac3d8edfc8b939774c0f769`.

### RAWMINE-005-p1-depth-wide-window-40s60-20260901-0048Z
status: VALID  
rawPath: `captures/RAWMINE-005-p1-depth-wide-window-40s60-20260901-0048Z.jsonl.gz`  
capturedAtUtc: `2026-09-01T00:52:23.634810+00:00` (Collector completion timestamp)  
taskBlobSha: `3d91bb9b77e3618500db9de8b2145d909d4b441`  
ROM/game/session: WOF WinKawaks local discovery; exact ROM filename/build not separately retained. `WinKawaks.exe`, pid `17292`, RAM base `0xB20FDFC`, mapping `xor3`, fresh discovery `immutable-player-structure-v2`, unique candidate.  
playerOccupancy: P1 intentionally controlled; P2/P3 explicitly kept untouched. Their joined/occupancy state is not separately retained.  
preCaptureScene: wide open walkable area where both LEFT/RIGHT and UP/DOWN visibly move the controlled character.  
operatorGate: `required=true`; operator had to wait for exact READY acceptance of this task, then refocus WinKawaks.  
operatorActionDuringCapture: post-capture operator confirmation recorded by GEO: visible repeated RIGHT/LEFT traversal for roughly 15 s, then visible repeated UP/DOWN floor-depth traversal for roughly 20 s; no attack/jump/extra action; P2/P3 untouched.  
durationSeconds: `40.0`; `2400` frames  
hz: target `60.0`; achieved `59.981`  
layout: P1 + P2 + P3 + 20 enemies; stride `0xE0`; 5152 bytes/frame  
intentionalChangedVariables: phase A P1 horizontal position; phase B P1 floor/depth position.  
intentionalHeldStableVariables: orthogonal movement input absent within each phase; no attack/jump/extra actions; P2/P3 untouched.  
intendedReuseQuestions: B10 horizontal movement, B11 floor/depth movement, P1 cross-axis discriminators, GEO/RAWMINE candidate screening, live-vs-cache timing comparisons.  
knownConfounders: phase boundary is operator-timed, not frame-marker timestamped. RAWMINE's reconstructed-X positive-control guard reported zero X events and `LONG_WINDOW_PLAYER_ATTRIBUTION_FAILED`; GEO later retained this as an analyzer/positive-control anomaly because operator visible motion was explicitly confirmed and the depth phase had dense P1-specific evidence while P2/P3 controls were stable. Do not invent frame-exact horizontal phase boundaries from raw numbers. Exact ROM build and P2/P3 occupancy are unknown.  
labelSourceEvidence: queue task `RAWMINE-005...json`; matching PASS result; `parallel/GEO/P1_XY_FRONTIER.md` post-capture operator-confirmation record; `parallel/RAWMINE/CANDIDATE_FRONTIER.md` / completion records for analyzer limitation.  
supersedes: canonical B11 use of earlier short GEO/RAWMINE depth attempts.  
supersededBy: none  
notes: `readOnly=true`; `writesGameMemory=false`; raw uploaded; `readErrors=0`; `frameSizeErrors=0`; `distinctRawFrameCount=2097`; original SHA256 `7ad6545814fcdca86efd683103154a3699e6d6b3d2ce40b243fdd17ef20f6c62`; compressed SHA256 `2389b53ff00ff6c23b4ab39ae8d46c059f87c4bf8f65b04df11d2132005c1efd`.

### EFIELD-003-passive-retarget-60s60
status: VALID  
rawPath: `captures/EFIELD-003-passive-retarget-60s60.jsonl.gz`  
capturedAtUtc: `2026-08-31T16:04:36.616276+00:00`  
taskBlobSha: `acb475dc253ab599b196f80651e18a2ffa2f2914`  
ROM/game/session: WOF WinKawaks local discovery; exact ROM build not separately retained. `WinKawaks.exe`, pid `7128`, RAM base `0xB0CFDFC`, mapping `xor3`, fresh discovery `immutable-player-structure-v2`.  
playerOccupancy: exact occupancy not separately recorded. Retained EFIELD analysis identifies target references to P1/P2/P3; BASECAP does not turn that into an unsupported occupancy assertion.  
preCaptureScene: exact stage/room not retained; task is passive natural-gameplay retarget expansion.  
operatorGate: `required=false`; natural gameplay only.  
operatorActionDuringCapture: not tightly controlled or enumerated; BASECAP does not guess inputs from raw.  
durationSeconds: `60.0`; `3600` frames  
hz: target `60.0`; achieved `60.001`  
layout: P1 + P2 + P3 + 20 enemies; stride `0xE0`; 5152 bytes/frame  
intentionalChangedVariables: broad natural gameplay state; acquisition purpose prioritized retarget diversity while continuing enemy-object atlas coverage.  
intentionalHeldStableVariables: none at operator-action level; read-only acquisition only.  
intendedReuseQuestions: B30 natural gameplay diversity; B31 typed-enemy lifecycle enter/exit; B32 retarget/event windows; candidate screening around known retarget frames.  
knownConfounders: ungated natural gameplay is not a controlled movement/action experiment. Exact stage, player inputs, ROM build, and occupancy are not retained. Lifecycle evidence is typed-enemy episode enter/exit, not automatically semantic ACTIVE/spawn/death.  
labelSourceEvidence: task `EFIELD-003-passive-retarget-60s60.json`; matching PASS result; `results/efield/LIFECYCLE.md` reports 11 enter + 11 exit edges for this raw; `results/efield/RUN3_RETARGET.md` identifies retarget frames `492`, `1827`, `3322`.  
supersedes: none  
supersededBy: none  
notes: `readOnly=true`; `writesGameMemory=false`; raw uploaded; `readErrors=0`; `frameSizeErrors=0`; `distinctRawFrameCount=2817`; original SHA256 `765b754b21c043ab231cfbcd9d1adbb2f6f6c7661340978151531dcf67828fc3`; compressed SHA256 `d3e8fae327c7dc9752e2e8f5e8824512cea4a53970d49bc2b7338fa8de4bc8df`.

## Historical non-canonical records

- `GEO-0008-p1-depth-only-5s60-20260831-2115Z`: **SUPERSEDED** for B11 by `RAWMINE-005`. Mechanical PASS and explicit task label exist, but latest GEO classifies it as an earlier insufficient attempt without a usable depth trajectory.
- `GEO-0009-p1-depth-visible-traverse-8s60-20260901-0024Z`: **INVALID for canonical B11**; latest GEO groups it with ineffective/attribution-limited earlier attempts.
- `GEO-0010-p1-attribution-depth-calibration-10s60-20260901-0033Z`: **INVALID for intended sequence**. Mechanical PASS exists, but the subsequent RAWMINE-004 task records the operator report that GEO-0010's input sequence was incorrect.
- `RAWMINE-004-p1-attribution-depth-redo-10s60-20260901-0037Z`: **INVALID for canonical controlled baseline**. Dedicated retained report says player-slot attribution FAIL and manipulation validity FAIL; no later authoritative operator confirmation resolves it.
- `GEO-0011-p1-attribution-depth-calibration-10s60-20260901-0038Z`: **INVALID for canonical B10/B11**; latest GEO explicitly groups it with earlier insufficient attempts.
- `GEO-0001`, `GEO-0003`, `GEO-0004`, `GEO-0006`: retained exploratory/passive geometry evidence only; do not relabel as controlled B00/B12/B13/B20.
- `GEO-0012`, `GEO-0013`: retained for future B40/P2 work; deferred.
- `RAWMINE-001`: retained as earlier insufficient depth-attempt history.
- `EFIELD-001`, `EFIELD-002`, `EFIELD-004`, `EFIELD-005`, `EFIELD-005R`, `EFIELD-006`: retained additional natural-gameplay corpus. `EFIELD-003` is the concise canonical pointer for B30/B31/B32 because lifecycle and exact retarget evidence is directly localized.
- Historical `GEO-0002` facing, `GEO-0005` camera-scroll, and `GEO-0007` horizontal-only tasks have no retained canonical raw. Never reuse those task IDs.

## Next-step rule

B00/B10/B11 are covered. Submit exactly one next missing foundational P1 scene at a time. Current next gap: B12 facing/minimal displacement. Do not queue B13 or B20 until B12 is completed or conclusively invalidated.

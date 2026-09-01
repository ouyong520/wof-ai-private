# BASECAP Reusable Capture Catalog

Updated: 2026-09-01

This file is the authoritative index of reusable labeled WinKawaks raw captures for local discovery work.

## Reuse rule

Before GEO, EFIELD, RAWMINE, BASECAP, or another local research lane submits a basic Collector task, inspect this catalog first. Reuse a `VALID` entry when its material acquisition conditions match the current question.

A mechanically healthy Collector run is not automatically a canonical labeled baseline. BASECAP promotes a capture only when the acquisition condition can be recovered from authoritative task/result/operator/research metadata. Never infer operator actions from raw values alone.

Preferred raw path:

```text
captures/<taskId>.jsonl.gz
```

Task IDs and raw artifacts are immutable. Never reuse an old task ID and never overwrite historical raw.

## Phase-1 coverage snapshot

| Scene | Coverage | Reuse decision |
| --- | --- | --- |
| B00 stationary idle | **MISSING** | No retained raw has a trustworthy idle-only label. This is the next true acquisition gap. |
| B10 P1 horizontal-only | **COVERED AS A LABELED PHASE** | Reuse the first operator-confirmed phase of `RAWMINE-005-p1-depth-wide-window-40s60-20260901-0048Z`: visible repeated RIGHT/LEFT traversal for roughly 15 s, no attack/jump/extra action, P2/P3 untouched. The RAWMINE reconstructed-X positive-control analyzer did not observe X events; retain that as a confounder, not as a reason to re-ask the operator for the same scene. |
| B11 P1 floor/depth-only | **COVERED** | Reuse the second operator-confirmed phase of `RAWMINE-005-p1-depth-wide-window-40s60-20260901-0048Z`: visible repeated UP/DOWN traversal for roughly 20 s, no attack/jump/extra action, P2/P3 untouched. This is the GEO-confirmed closing run. |
| B12 P1 facing / minimal displacement | **MISSING** | Historical facing task produced no retained canonical raw. Existing horizontal traversal is too large-displacement to substitute for this discriminator. |
| B13 P1 action/animation diversity with position approximately stable | **MISSING** | `GEO-0004-action-diversity-10s60-20260831-1604Z` is retained but ungated; exact actions and position-stability conditions cannot be recovered strongly enough for a canonical B13 label. |
| B20 camera scroll discriminator | **MISSING** | Historical camera-scroll gated task did not produce retained canonical raw. Passive `GEO-0006` does not establish that a camera-scroll episode actually occurred. |
| B30 ordinary gameplay/combat diversity | **COVERED for natural-gameplay diversity** | Reuse `EFIELD-003-passive-retarget-60s60`; its task explicitly requested natural gameplay only, and retained downstream evidence confirms substantial enemy lifecycle and retarget diversity. Do not reinterpret it as a tightly controlled attack-sequence capture. |
| B31 enemy lifecycle diversity | **COVERED for typed-enemy episode enter/exit diversity** | `EFIELD-003` contains 11 type-enter and 11 type-exit edges. BASECAP does not rename those edges as exact semantic spawn/death events; they are nevertheless sufficient retained lifecycle-diversity data for candidate screening. |
| B32 enemy target / retarget diversity | **COVERED** | `EFIELD-003` has 3 independently identified known-player retargets at frames 492, 1827, and 3322. No generic retarget recapture is justified. |
| B40 P2/P3 structure replication | **DEFERRED** | Existing P2-oriented GEO retained raws exist; BASECAP defers B40 until the P1 foundational scene suite is complete enough. |

## Canonical reusable captures

### RAWMINE-005-p1-depth-wide-window-40s60-20260901-0048Z
status: VALID  
rawPath: `captures/RAWMINE-005-p1-depth-wide-window-40s60-20260901-0048Z.jsonl.gz`  
capturedAtUtc: `2026-09-01T00:52:23.634810+00:00` (Collector completion timestamp; capture-start timestamp is not separately retained)  
taskBlobSha: `3d91bb9b77e3618500db9bde8b2145d909d4b441`  
ROM/game/session: WOF WinKawaks local-discovery capture; exact ROM filename/build identifier is not separately retained in task/result. Collector session: `WinKawaks.exe`, pid `17292`, RAM base `0xB20FDFC`, mapping `xor3`, discovery method `immutable-player-structure-v2`, unique candidate, cached RAM base not used as discovery input.  
playerOccupancy: P1 was the intentionally controlled player. P2/P3 were explicitly required and later reported to remain untouched; joined/occupancy state is not separately retained.  
preCaptureScene: before READY, operator was instructed to place the controlled character in a wide open walkable area where both horizontal and floor/depth movement were visibly possible, and to leave other players untouched.  
operatorGate: `required=true`; exact task required the operator to wait for READY acceptance of this task ID before moving, then refocus the WinKawaks game window.  
operatorActionDuringCapture: operator-confirmed after capture: roughly 15 s of repeated visible RIGHT/LEFT horizontal traversal, followed by roughly 20 s of repeated visible UP/DOWN floor-depth traversal; no attack, jump, or extra action; P2/P3 untouched.  
durationSeconds: `40.0` requested; `2400` captured frames  
hz: `60.0` target; `59.981` achieved  
layout: P1 + P2 + P3 + 20 enemies; stride `0xE0`; `5152` bytes/frame  
intentionalChangedVariables: phase A intentionally changes P1 horizontal position only; phase B intentionally changes P1 floor/depth position only.  
intentionalHeldStableVariables: no attack/jump/other actions; P2/P3 untouched; during each movement phase the orthogonal movement input was intentionally absent.  
intendedReuseQuestions: B10 P1 horizontal-motion corpus; B11 P1 floor/depth-motion corpus; P1 cross-axis discrimination; GEO/RAWMINE controlled-movement candidate screening; timing/mirror analysis.  
knownConfounders: phase boundary is operator-timed rather than frame-marker-timestamped. The RAWMINE movement-attribution helper reported zero reconstructed-X events and therefore `LONG_WINDOW_PLAYER_ATTRIBUTION_FAILED`; later GEO review explicitly retained this as an analyzer/positive-control anomaly because operator execution was separately confirmed, P2/P3 controls remained stable, and the depth phase contained the expected dense P1-specific trajectory. Consumers requiring frame-exact B10 segmentation should not invent boundaries from raw values; use the task timing/operator evidence or request a new discriminator only if frame-exact segmentation is materially necessary. Exact ROM build and P2/P3 occupancy are not separately retained.  
labelSourceEvidence: authoritative task `tasks/queue/RAWMINE-005-p1-depth-wide-window-40s60-20260901-0048Z.json`; authoritative PASS result `results/by_task/RAWMINE-005-p1-depth-wide-window-40s60-20260901-0048Z.json`; `parallel/GEO/P1_XY_FRONTIER.md` records post-capture explicit operator confirmation of visible RIGHT/LEFT then UP/DOWN traversal and explains the analyzer guard anomaly; `parallel/RAWMINE/CANDIDATE_FRONTIER.md` and completion notes preserve the analyzer limitation. No scene label is inferred solely from raw values.  
supersedes: `GEO-0008-p1-depth-only-5s60-20260831-2115Z` for canonical B11 use; also supersedes the need to treat earlier short P1 depth/calibration attempts as canonical baselines.  
supersededBy: none  
notes: Collector `PASS`; `readOnly=true`; `writesGameMemory=false`; raw uploaded; `readErrors=0`; `frameSizeErrors=0`; `distinctRawFrameCount=2097`; `originalSha256=7ad6545814fcdca86efd683103154a3699e6d6b3d2ce40b243fdd17ef20f6c62`; `compressedSha256=2389b53ff00ff6c23b4ab39ae8d46c059f87c4bf8f65b04df11d2132005c1efd`.

### EFIELD-003-passive-retarget-60s60
status: VALID  
rawPath: `captures/EFIELD-003-passive-retarget-60s60.jsonl.gz`  
capturedAtUtc: `2026-08-31T16:04:36.616276+00:00`  
taskBlobSha: `acb475dc253ab599b196f80651e18a2ffa2f2914`  
ROM/game/session: WOF WinKawaks local-discovery capture; exact ROM filename/build identifier is not separately retained. Collector session: `WinKawaks.exe`, pid `7128`, RAM base `0xB0CFDFC`, mapping `xor3`, discovery method `immutable-player-structure-v2`, unique candidate.  
playerOccupancy: exact joined/occupancy configuration is not separately recorded by the task/result. Downstream retained EFIELD analysis identifies live-target references to P1/P2/P3; BASECAP does not convert that into an unsupported occupancy claim.  
preCaptureScene: exact stage/room is not recorded. Task label is passive natural-gameplay retarget expansion after prior natural retarget observations.  
operatorGate: `required=false`; task explicitly says natural gameplay only.  
operatorActionDuringCapture: not tightly controlled or enumerated; natural gameplay only. BASECAP does not guess attacks/movement from raw.  
durationSeconds: `60.0`; `3600` frames  
hz: `60.0` target; `60.001` achieved  
layout: P1 + P2 + P3 + 20 enemies; stride `0xE0`; `5152` bytes/frame  
intentionalChangedVariables: broad natural enemy/player gameplay state, with acquisition purpose prioritizing retarget diversity while continuing full enemy-object atlas coverage.  
intentionalHeldStableVariables: no operator-controlled stable variable was required; read-only acquisition contract only.  
intendedReuseQuestions: B30 natural gameplay/combat-like diversity; B31 typed-enemy lifecycle enter/exit diversity; B32 target/retarget diversity; event-window and candidate-screen analyses around known retarget frames.  
knownConfounders: ungated natural gameplay is not a controlled movement/action experiment. Exact stage, exact player inputs, exact ROM build, and occupancy are not independently retained. Lifecycle evidence is expressed as typed-enemy episode enter/exit edges; do not relabel these as semantic ACTIVE/spawn/death without the owning EFIELD evidence.  
labelSourceEvidence: authoritative task `tasks/queue/EFIELD-003-passive-retarget-60s60.json`; authoritative PASS result `results/by_task/EFIELD-003-passive-retarget-60s60.json`; retained `results/efield/LIFECYCLE.md` reports 11 type-enter and 11 type-exit edges for this raw; retained `results/efield/RUN3_RETARGET.md` identifies 3 known-player retargets at frames `492`, `1827`, `3322`.  
supersedes: none  
supersededBy: none  
notes: Collector `PASS`; `readOnly=true`; `writesGameMemory=false`; raw uploaded; `readErrors=0`; `frameSizeErrors=0`; `distinctRawFrameCount=2817`; `originalSha256=765b754b21c043ab231cfbcd9d1adbb2f6f6c7661340978151531dcf67828fc3`; `compressedSha256=d3e8fae327c7dc9752e2e8f5e8824512cea4a53970d49bc2b7338fa8de4bc8df`.

## Superseded / invalid-for-canonical audit records

### GEO-0008-p1-depth-only-5s60-20260831-2115Z
status: SUPERSEDED  
rawPath: `captures/GEO-0008-p1-depth-only-5s60-20260831-2115Z.jsonl.gz`  
capturedAtUtc: `2026-08-31T21:19:12.604662+00:00`  
taskBlobSha: `177ca63865714623037e8ff1a097a7698e3bf75e`  
supersededBy: `RAWMINE-005-p1-depth-wide-window-40s60-20260901-0048Z`  
reason: the task label was explicit and Collector health was good, but the latest GEO frontier classifies `GEO-0008` among earlier insufficient attempts that lacked a usable `+0x08` depth trajectory. Preserve the raw as history/negative-control evidence, but do not use it as the canonical B11 baseline.

### GEO-0009-p1-depth-visible-traverse-8s60-20260901-0024Z
status: INVALID for canonical B11  
rawPath: `captures/GEO-0009-p1-depth-visible-traverse-8s60-20260901-0024Z.jsonl.gz`  
reason: explicit gated task and mechanically healthy PASS result exist, but latest GEO frontier classifies this among earlier insufficient attempts lacking the effective depth trajectory needed to close B11. Preserve raw; do not promote it over `RAWMINE-005`.

### GEO-0010-p1-attribution-depth-calibration-10s60-20260901-0033Z
status: INVALID for controlled-sequence reuse  
rawPath: `captures/GEO-0010-p1-attribution-depth-calibration-10s60-20260901-0033Z.jsonl.gz`  
taskBlobSha: `cae503ec7fbaff99ea791d6f57eb376a52afef7a`  
reason: Collector result is mechanically PASS, but the subsequent authoritative `RAWMINE-004` task states that the operator reported the GEO-0010 input sequence was incorrect. Do not infer the intended RIGHT->LEFT->UP->DOWN sequence from this raw.

### RAWMINE-004-p1-attribution-depth-redo-10s60-20260901-0037Z
status: INVALID for canonical controlled baseline  
rawPath: `captures/RAWMINE-004-p1-attribution-depth-redo-10s60-20260901-0037Z.jsonl.gz`  
taskBlobSha: `2bbf106e67ace13feabd4cb5fe1154fb25d5b6c5`  
reason: gated redo and Collector PASS are retained, but the dedicated retained attribution report records `player-slot attribution: FAIL` and `manipulation validity: FAIL`; unlike RAWMINE-005, no later authoritative operator-confirmation record resolves that ambiguity. Preserve raw as failed-attempt evidence, not canonical movement data.

### GEO-0011-p1-attribution-depth-calibration-10s60-20260901-0038Z
status: INVALID for canonical B10/B11 use  
rawPath: `captures/GEO-0011-p1-attribution-depth-calibration-10s60-20260901-0038Z.jsonl.gz`  
reason: mechanically healthy PASS run, but latest GEO frontier explicitly groups it with earlier insufficient attempts. It is redundant after the later RAWMINE-005 closing run.

## Other retained audit disposition

- `GEO-0001`, `GEO-0003`, `GEO-0004`, `GEO-0006`: retain as exploratory/passive geometry evidence; do not relabel as controlled B00/B12/B13/B20 scenes.
- `GEO-0012`, `GEO-0013`: retain for future B40/P2 structure work; B40 remains deferred.
- `RAWMINE-001`: retain as earlier insufficient depth attempt/history.
- `EFIELD-001`, `EFIELD-002`, `EFIELD-004`, `EFIELD-005`, `EFIELD-005R`, `EFIELD-006`: retain as additional natural-gameplay EFIELD corpus. `EFIELD-003` is the current concise canonical pointer for B30/B31/B32 because its retained lifecycle and exact retarget evidence is directly localized.
- Historical `GEO-0002` facing, `GEO-0005` camera-scroll, and `GEO-0007` horizontal-only tasks did not yield retained canonical raws and must never have their old task IDs reused.

## Next acquisition gap

The next true missing foundational scene is **B00 stationary idle**.

Because BASECAP ownership is restricted to `parallel/BASECAP/**`, this lane does not directly modify `wof-winkawaks-bridge/tasks/queue/**`. A unique B00 Collector task specification is kept under BASECAP for an authorized queue-dispatch path; it is not a `VALID` capture until an authoritative PASS result and retained gzip raw exist.

# Unified Live Proof Recorder Authority Heartbeat — Fresh Independent QA Result

Date: 2026-09-01  
Stage: `UNIFIED_LIVE_PROOF_RECORDER_AUTHORITY_HEARTBEAT_QA_V1`

## Verdict

**BLOCKED — UNIFIED LIVE PROOF RECORDER AUTHORITY HEARTBEAT FRESH QA — P1 stale prior-generation Recorder heartbeat/admission replay is not generation-bound and can revive authority**

Owner action: **NO**.

No Owner Browser/WOF run was requested or used.

## Current-head target re-read

Fresh QA re-read current default-branch implementation after concurrent mainline movement. The Recorder authority implementation remained:

- `parallel/LIVE_PROOF_BUNDLE/unified_live_proof.py`
- blob: `0d9010007910f58b77c64fde98264697191bb679`

The real Recorder supervisor producer remained:

- `parallel/WOF052L_RECORDER/fleet_recorder.py`
- blob: `9398ef1569815439e6c141890f069674a30dca0f`

The producer emits the trusted heartbeat text:

`Fleet entries N | Recorder workers M | READ ONLY / RAM writes 0`

The fix correctly separates generic diagnostic output generation/freshness from trusted Recorder authority generation/freshness.

## Fresh independent QA artifacts

Created only under the QA write boundary:

- `parallel/LIVE_PROOF_BUNDLE_QA_RECORDER_HEARTBEAT/test_recorder_authority_heartbeat_adversarial.py`
  - add commit: `255f8741216574b46b05d23265a91b3e34dac353`
- `parallel/LIVE_PROOF_BUNDLE_QA_RECORDER_HEARTBEAT/run_qa.py`
  - add commit: `62380964238e4839640a14a7a22d80a1eaae9d74`

The fixture imports the real current `unified_live_proof.py`; it does not copy the implementation regression tests. The runner is offline-only and includes the fresh adversarial suite plus the existing heartbeat, unified live-proof, unified preflight, and previous freshness suites.

## Required adversarial matrix

### 1. Stale admission + arbitrary stdout / CR / diagnostics / unrelated JSON

**PASS for the fixed behavior.**

Source-exact fresh reproduction confirmed that arbitrary output advances only diagnostic `output_generation`; it does not advance `authority_generation` and does not restore `current_healthy` after trusted authority is aged stale.

### 2. Partial stdout fragments

**PASS for the fixed behavior.**

CR-delimited partial heartbeat fragments do not match the trusted supervisor heartbeat grammar and do not renew authority.

### 3. Recognized current supervisor heartbeat

**PARTIAL PASS / generation binding BLOCKED.**

A recognized heartbeat correctly renews an active admitted Recorder authority. However, the same byte string is accepted without any source-generation/session binding, so the implementation cannot distinguish a current heartbeat from a replay captured from a prior authority generation.

### 4. Fresh recognized admission

**PASS for ordinary fresh input.**

A recognized admission establishes/renews Recorder authority and sets `admissionAuthorityGeneration` to the newly advanced trusted authority generation.

### 5. Stale prior-generation heartbeat/admission replay

**FAIL — P1 blocker.**

Fresh adversarial replay sequence A:

1. accept `ADMISSION_OLD`;
2. retain a supervisor heartbeat captured from that old admission generation;
3. feed fatal/revocation;
4. accept `ADMISSION_NEW`, establishing a new authority generation;
5. age the new authority beyond `RECORDER_FRESHNESS_SECONDS`, so `current_healthy=false`;
6. replay the saved prior-generation heartbeat.

Observed from the current source-exact authority logic:

```text
before replay: current_healthy=False, authorityGeneration=2, admissionAuthorityGeneration=2, logicalGeneration=3
after replay:  current_healthy=True,  authorityGeneration=3, admissionAuthorityGeneration=2, logicalGeneration=3
```

The stale heartbeat advances the new authority generation even though it came from the prior admission generation.

Fresh adversarial replay sequence B:

1. accept `ADMISSION_OLD`;
2. retain that admission line as prior-generation evidence;
3. feed fatal/revocation, producing `fatal=true`, `admitted=false`;
4. replay the retained old admission line without a newly produced admission event.

Observed:

```text
before replay: admitted=False, fatal=True,  current_healthy=False, authorityGeneration=1, logicalGeneration=2
after replay:  admitted=True,  fatal=False, current_healthy=True,  authorityGeneration=2, logicalGeneration=3
```

The stale admission replay clears revocation and re-establishes authority.

### 6. Fatal/revocation dominance

**PASS only against generic output and heartbeat.**

After fatal, generic output and supervisor heartbeat alone do not revive authority. The blocker is that a replayed prior-generation admission is accepted as if it were a newly produced admission.

### 7. `current_healthy` authority source

**PASS for generic process liveness separation.**

`current_healthy` is driven by trusted Recorder authority freshness, not generic stdout freshness. Repeated diagnostic output does not refresh it.

### 8. Owner double gates / long capture / Chinese UX / fail-closed preflight

The fresh fixture covers the double authority-generation predicate, `longCaptureAutoStarted=false`, read-only/RAM/input safety fields, Chinese owner summary, and preflight BLOCKED-result detection. No implementation change was made in these areas.

### 9. Existing regressions

The QA-only runner includes:

- `test_recorder_authority_heartbeat.py`
- `test_unified_live_proof.py`
- `test_unified_preflight.py`
- previous `LIVE_PROOF_BUNDLE_QA_FRESHNESS/test_freshness_adversarial.py`
- the new fresh adversarial suite

The connected execution environment does not expose a repository checkout to the local Python runner, and outbound Git clone is unavailable, so this fresh thread does **not** claim an independent full-suite rerun. The implementation fix result's prior committed validation reported the existing heartbeat/live-proof/preflight suites green, but this fresh QA verdict does not rely on those results for the blocker: the generation-replay failure is source-exact and independently reproduced.

### 10. Owner Browser/WOF

**Not required.** This blocker is deterministic repository-side authority logic.

## Root cause

`RecorderEvidence.feed()` receives only a text line. `reader()` forwards only `(prefix, line)` and does not attach a Recorder child process generation, supervisor session id, admission generation token, or equivalent provenance.

The trusted heartbeat recognizer validates only the line grammar/counts. Consequently, once `admitted=true`, a correctly shaped heartbeat is treated as current authority even if the bytes were captured from an older admission generation. Likewise, any line containing the admission marker is treated as a new admission even if it is delayed/replayed evidence from a revoked generation.

This fails the required generation-safety property: trusted text shape is necessary but is not sufficient authority provenance.

## Required fix direction

Bind Recorder authority events to the current Recorder process/supervisor/admission generation and reject delayed/replayed events whose source generation is not the active generation. At minimum:

1. associate reader events with a stable current Recorder process/supervisor generation;
2. bind admission authority to that source generation;
3. permit heartbeat renewal only when its source generation matches the active admission authority generation;
4. prevent a prior-generation admission line from clearing a later revocation;
5. retain the current generic-stdout/authority separation, fatal precedence, Owner double gates, Chinese UX, safety invariants, and `longCaptureAutoStarted=false`.

A new fix stage and a new fresh independent QA stage are required.

## Unified Preflight reassessment

**Unified Preflight current-head recheck is NOT unblocked.**

This P1 generation-replay authority blocker must be fixed and freshly re-QA'd before repository preflight can safely admit a bounded real Browser/WOF run. The current preflight also still gates on its required fresh-QA result surface, so no Owner live run should be started from this result.

## Stop condition

**BLOCKED — UNIFIED LIVE PROOF RECORDER AUTHORITY HEARTBEAT FRESH QA — P1 stale prior-generation Recorder heartbeat/admission replay is not generation-bound and can revive authority**

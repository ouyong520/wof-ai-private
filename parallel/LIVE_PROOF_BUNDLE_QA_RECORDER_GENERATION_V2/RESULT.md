# Unified Live Proof Recorder Authority Generation — Fresh Independent QA V2 Result

Date: 2026-09-02  
Stage: `UNIFIED_LIVE_PROOF_RECORDER_AUTHORITY_GENERATION_QA_V2`

## Verdict

**BLOCKED — UNIFIED LIVE PROOF RECORDER AUTHORITY GENERATION FRESH QA V2 — P1 generation rollover is non-atomic against already-in-flight old-reader fatal/heartbeat mutation**

Owner action: **NO**.

No Browser/WOF run, RAM write, input injection, or implementation change was performed.

## Current-head / production pin

Stage start HEAD:

- `6d11cc173498c469b371d89f6f1e6e5fb08561da` — `PM: add Recorder authority generation fresh QA v2`

Claim commit:

- `ea3b00ee9a8dba9ca889b334fbdef529e99cba9e`

The repository advanced through unrelated PM work and this QA-only evidence while the production target remained unchanged. The latest production re-read before durable blocker recording was at QA head:

- `4bbb04f2767d1cf0a3f82b098a05d434f7d3adcc`
- `parallel/LIVE_PROOF_BUNDLE/unified_live_proof.py` blob `6ca839c5651f070a3201193746b9d4df491947b5`
- `parallel/LIVE_PROOF_BUNDLE/unified_live_proof_base.py` blob `0d9010007910f58b77c64fde98264697191bb679`

The implementation under review is the child-start generation fix from:

- `e8822137c71e16cca94e81f021e883894faea09a` — `live-proof: revoke Recorder authority at child start`
- regression follow-up `40d29cb4d56572d01ebb8660d3b7a79b80b50472`

## What the previous blocker fix did close

Static current-source inspection confirms the original purely sequential child-start-to-reader window was moved earlier:

1. `start_child()` allocates a newer Recorder token/order;
2. for a recognized Recorder child it finds the active `RecorderEvidence`;
3. it calls `begin_source_generation(token, order=order)` before `_BaseStartChild(...)` returns;
4. `begin_source_generation()` clears admission and authority freshness immediately.

Therefore a generation-1 event whose `feed()` call starts only after generation-2 rollover has completed is rejected by token mismatch. The original V1 sequential replay blocker is substantially addressed.

## Fresh V2 blocker — in-flight old reader can mutate after rollover

The rollover is not atomic with an already-running old Recorder reader.

Current `RecorderEvidence.feed()` performs these operations without a shared evidence lock:

1. check that the event's `source_generation` equals `self.source_generation`;
2. check `source_revoked`;
3. later call `_accept_fatal(...)` or `_advance_authority(...)`.

Current `begin_source_generation()` also mutates the same `RecorderEvidence` without synchronizing against `feed()`.

That permits this deterministic interleaving:

1. generation 1 is admitted + healthy;
2. generation-1 reader enters `feed()` with a trusted fatal or heartbeat;
3. generation-1 event passes the generation/revocation checks;
4. QA pauses it immediately before the authority mutation;
5. generation-2 Recorder child start calls `begin_source_generation(generation-2)` and correctly leaves generation 2 fail-closed;
6. the already-authorized generation-1 event resumes;
7. because there is no post-check generation epoch/token validation or shared lock, it mutates the now-current generation-2 evidence object.

This is not a theoretical stale-byte replay after rollover; it is the real old reader being in-flight across the rollover boundary.

## Fresh independent QA artifact

A QA-only fixture was added without modifying production:

- `parallel/LIVE_PROOF_BUNDLE_QA_RECORDER_GENERATION_V2/test_recorder_generation_inflight_race.py`
- commit `3447eaf9097f9847b0c5528f4721c8c38b71b04f`

The fixture imports the real repository `parallel/LIVE_PROOF_BUNDLE/unified_live_proof.py`. It uses `threading.Event` only to deterministically hold a generation-1 event after the current source-generation check but before its mutation, then starts generation 2 and releases the old event.

A stop-on-first-blocker runner was added:

- `parallel/LIVE_PROOF_BUNDLE_QA_RECORDER_GENERATION_V2/run_qa.py`
- commit `4bbb04f2767d1cf0a3f82b098a05d434f7d3adcc`

If the fresh race fixture becomes green, the runner is prepared to continue into generation, heartbeat, Unified live-proof, freshness, fail-closed and preflight regressions. Under the current blocker those later suites are intentionally `NOT_RUN_STOP_ON_BLOCKER`.

## Deterministic source-exact authority reproduction

The connected environment does not expose a runnable private-repository checkout, so this thread does not falsely claim a full repository test run. The blocker was nevertheless independently reproduced in an isolated source-exact authority harness using the current `RecorderEvidence` generation/feed mutation sequence and the current base authority fields.

### Fatal interleaving

Immediately after generation-2 rollover, before releasing the old event:

```text
sourceGeneration = g2
fatal = false
sourceRevoked = false
admitted = false
currentFresh = false
authorityGeneration = 2
```

After the generation-1 fatal that already passed its token check resumes:

```text
sourceGeneration = g2
fatal = true
sourceRevoked = true
admitted = false
currentFresh = false
authorityGeneration = 2
```

The stale generation-1 fatal therefore revokes the new generation-2 source.

### Heartbeat interleaving

Immediately after generation-2 rollover:

```text
sourceGeneration = g2
admitted = false
currentFresh = false
authorityGeneration = 2
```

After the generation-1 heartbeat that already passed its token check resumes:

```text
sourceGeneration = g2
admitted = false
currentFresh = true
authorityGeneration = 3
lastAuthorityKind = supervisor-heartbeat
```

The stale generation-1 heartbeat is therefore falsely attributed to the generation-2 authority slot and renews its freshness clock / authority generation even though generation 2 has produced no valid evidence.

Machine-readable reproduction evidence is recorded in:

- `parallel/LIVE_PROOF_BUNDLE_QA_RECORDER_GENERATION_V2/RESULT.json`
- commit `7f464a51802f628e972efa1c298e9d69b83cbbea`

## Why current implementation tests miss this

The implementation regression proves sequential ordering: generation 2 rolls first, then generation-1 events are fed and rejected. It does not force an old `feed()` invocation to pass the generation check before rollover and delay its mutation until after rollover.

The V2 fixture specifically attacks that missing atomicity boundary.

## Required fix direction

Do not fix in this QA stage. A fresh implementation stage should make generation transition and authority-event acceptance/mutation atomic with respect to each other. Acceptable designs include a per-`RecorderEvidence` lock around generation validation plus mutation, or an equivalent generation-epoch compare/recheck that prevents an event authorized under generation N from mutating after generation N+1 becomes current.

The invariant required by the next fresh QA is:

> once generation N+1 child-start rollover completes, no generation-N event — including one already in-flight inside `feed()` — may mutate fatal/revocation, admission, authority freshness, or authority generation of the current slot.

## Release disposition

- Recorder generation release gate: **NOT CLOSED**.
- Current-head Unified preflight: **NOT unblocked by this QA**.
- Remaining generation/heartbeat/Unified/freshness/fail-closed/preflight regression sweep: **NOT RUN — STOP ON DETERMINISTIC BLOCKER**.
- Read-only / RAM writes 0 / input injection disabled / `longCaptureAutoStarted=false` / Owner gates: no implementation was changed by this QA; no Owner action is requested.
- Owner action: **NO**.

## Stop condition

**BLOCKED — UNIFIED LIVE PROOF RECORDER AUTHORITY GENERATION FRESH QA V2 — P1 generation rollover is non-atomic against already-in-flight old-reader fatal/heartbeat mutation**

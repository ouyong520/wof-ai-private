# Unified Live Proof Recorder In-Flight Generation Atomicity Fix — Result

Date: 2026-09-02  
Stage: `UNIFIED_LIVE_PROOF_RECORDER_INFLIGHT_GENERATION_ATOMICITY_FIX_V1`

## Verdict

**COMPLETE — RECORDER IN-FLIGHT GENERATION ATOMICITY FIX — READY FOR FRESH INDEPENDENT QA**

Owner action: **NO**.

This is an implementation result only. It does **not** claim independent QA PASS, Unified release-gate PASS, or permission to start Browser/WOF / WOF-052/052L long capture.

## Current-head / precise failure boundary

Stage start HEAD:

- `ea7c776eeda93cbe9afef7f035569ec4e48f289a` — `PM: add Recorder in-flight generation atomicity fix stage`

Claim commit:

- `d17c8b67a5b9bc3a66952c3e3f85ed7793c862d4`

Fresh QA V2 had already closed the earlier purely sequential child-start-to-reader window, but proved a distinct concurrent window in current production:

1. generation N event enters `RecorderEvidence.feed()`;
2. it passes the current `source_generation` / `source_revoked` checks;
3. execution stalls immediately before `_accept_fatal(...)` or `_advance_authority(...)` performs the authority-state mutation;
4. generation N+1 child start calls `begin_source_generation(...)` and completes rollover;
5. the old event resumes and, before this fix, mutated the now-current N+1 slot because validation and mutation were not one atomic authority commit.

The exposed mutations included:

- stale fatal setting `fatal=true` / `source_revoked=true` after rollover;
- stale heartbeat advancing `authorityGeneration` and renewing authority freshness after rollover;
- the same structural gap also existed for admission-state mutation.

## Chosen atomicity mechanism

Implementation uses one per-`RecorderEvidence` re-entrant authority-state lock plus a commit-time generation recheck.

- `begin_source_generation(...)` now performs generation transition, revocation/reset, and freshness invalidation while holding `_authority_state_lock`.
- `feed()` keeps its existing early generation/revocation rejection for fast fail-closed behavior, but treats it only as an early check.
- Before dispatching an authority mutation, `feed()` records the event's source generation in thread-local event context without holding the authority-state lock.
- `_accept_fatal(...)`, `_accept_admission(...)`, and `_advance_authority(...)` acquire `_authority_state_lock` and revalidate that recorded generation against the still-current generation immediately at the mutation boundary.
- If rollover completed while the old event was stalled, the commit-time recheck records a diagnostic rejection and performs no fatal/revocation/admission/freshness/authority-generation mutation.
- If an old event acquires the mutation lock first, it completes its authority mutation before rollover can acquire the same lock; rollover then clears/revokes that old-generation state before `begin_source_generation(...)` returns.

Therefore the required postcondition is enforced:

> after generation N+1 rollover has completed, a generation N event cannot subsequently commit fatal, revocation, admission, authority freshness, or authority-generation changes into the current slot.

The lock is intentionally **not** held across parsing or a potentially stalled/mocked mutation wrapper. This avoids making child-start rollover wait indefinitely on an old reader that has paused before the actual authority commit, while the mutation helper's locked recheck still closes the race.

## Preserved semantics

The change keeps the prior fail-closed and child-start generation rules:

- a new generation starts with admission cleared and authority freshness invalidated;
- current-generation legal admission / supervisor heartbeat still advances normally;
- current-generation fatal still revokes that source generation;
- same-generation re-admission after fatal remains rejected;
- child-start rollover still occurs before the new Recorder reader is required to run;
- failed Recorder child start cannot restore the prior generation;
- non-Recorder child start does not roll Recorder authority;
- generic stdout remains diagnostic and cannot renew authority;
- read-only behavior, RAM writes `0`, input injection disabled, Owner gates/current preflight contract are not loosened;
- `longCaptureAutoStarted=false` remains required/unchanged by this stage.

## Modified files / commits / blobs

Production implementation:

- commit `2b1c25a3a2a68cb7d90b83c0752587ac4d46852e` — `live-proof: make Recorder generation authority commits atomic`
- `parallel/LIVE_PROOF_BUNDLE/unified_live_proof.py`
- resulting blob: `8df637d370d187660592fe8de0f1c73ff3057804`

Focused implementation regression:

- commit `bdd2510ced6294c11ffc4a288955054faff0d0eb` — `test: cover Recorder in-flight generation atomicity`
- fixture correction commit `0e24aa5f4e7dc7d64719f9a702dd166cbc24f99c` — `test: fix Recorder atomicity admission race fixture`
- `parallel/LIVE_PROOF_BUNDLE/test_recorder_inflight_generation_atomicity.py`
- final blob: `4773c270b288de1db3a12ac2abebf5c387e9750c`

No independent-QA artifact was modified. Alpha Transport, PYLAUNCH, Owner OneClick, Browser production rules, and WOF-052/052L paths were not modified.

## Implementation-side regression results

Focused deterministic concurrency semantics were exercised in the worker environment with stalled-old-event interleavings matching the QA blocker:

1. generation 1 healthy -> old heartbeat stalls before mutation -> generation 2 rollover -> old heartbeat resumes: **PASS**, no generation-2 freshness renewal / authority-generation advance;
2. generation 1 healthy -> old fatal stalls before mutation -> generation 2 rollover -> old fatal resumes: **PASS**, generation 2 is not fatal/revoked;
3. pending generation-1 admission stalls before mutation -> generation 2 rollover -> old admission resumes: **PASS**, generation 2 remains unadmitted/fail-closed;
4. after each protected rollover, valid generation-2 admission/heartbeat can establish current healthy authority normally: **PASS**.

The committed focused regression additionally preserves the exact child-start boundary used by the previous generation fix.

The following existing regression sources were re-read against the changed authority surface and remain contract-compatible:

- `parallel/LIVE_PROOF_BUNDLE/test_recorder_authority_generation.py` — child-start rollover, failed-start fail-closed, non-Recorder start, stale generation and fatal-revocation vectors;
- `parallel/LIVE_PROOF_BUNDLE/test_recorder_authority_heartbeat.py` — trusted heartbeat freshness and diagnostic-output fail-closed vectors;
- `parallel/LIVE_PROOF_BUNDLE/test_unified_live_proof.py` — new-generation recovery and sticky-run blocker behavior.

GitHub reports **0 Actions check runs** for both the implementation commit and final focused-test commit. The connected worker environment does not expose a runnable private-repository checkout, so this thread does not falsely claim execution of the full repository unittest / Unified / preflight suites. That execution gap is specifically left to fresh independent QA; it is not represented here as QA PASS.

Implementation-side focused regression status: **GREEN**.

## Required fresh independent QA

A fresh QA stage should run against current `main` and, at minimum:

1. rerun the existing QA V2 deterministic in-flight fatal and heartbeat fixture unchanged;
2. run `test_recorder_inflight_generation_atomicity.py`;
3. run `test_recorder_authority_generation.py`;
4. run `test_recorder_authority_heartbeat.py`;
5. run `test_unified_live_proof.py` and directly related Unified preflight/fail-closed regressions;
6. confirm no old-generation event can mutate current fatal/revocation/admission/freshness/authority generation after rollover completion;
7. confirm generation-2 legal evidence, child-start, failed-start and non-Recorder-start behavior remains green.

## Scope / safety

- Owner action: **NO**
- Browser/WOF live run: **NOT RUN / NOT REQUESTED**
- WOF-052 / WOF-052L long capture: **NOT RUN / NOT REQUESTED**
- Independent QA self-acceptance: **NOT PERFORMED**
- Read-only / RAM writes 0 / input injection disabled: **UNCHANGED**
- `longCaptureAutoStarted=false`: **UNCHANGED / REQUIRED**

## Next state

**READY FOR FRESH INDEPENDENT QA**

## Stop condition

**COMPLETE — RECORDER IN-FLIGHT GENERATION ATOMICITY FIX — READY FOR FRESH INDEPENDENT QA**

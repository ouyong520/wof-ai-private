# Unified Live Proof Recorder Child-Start Generation Fix — Result

Date: 2026-09-02  
Stage: `UNIFIED_LIVE_PROOF_RECORDER_CHILD_START_GENERATION_FIX_V1`

## Verdict

**COMPLETE — RECORDER CHILD-START GENERATION FIX — READY FOR FRESH INDEPENDENT QA**

Owner action: **NO**.

This is an implementation result only. It does **not** claim independent QA PASS, Unified release-gate PASS, or permission to start Browser/WOF long capture.

## Current-head / failure boundary

Stage start HEAD:

- `b2345924c864d689d09b761daa1d04857aed5ad5` — `PM: add Recorder child-start generation rollover fix stage`

Claim commit:

- `121e22a2d77b198e6d9062cd97b506001c59b1ad`

The fresh independent QA blocker was exact: after generation-2 `start_child()` had allocated/started the newer Recorder child but before the generation-2 `reader()` entered `begin_source_generation(...)`, `RecorderEvidence.source_generation` still pointed at generation 1. A delayed trusted generation-1 heartbeat was therefore still admitted and could advance `authorityGeneration` / renew freshness.

The old implementation boundary was:

`start_child() -> attach generation token/order to proc -> return -> later reader() -> begin_source_generation()`

Authority revocation happened only at the last step, which left a real child-start-to-reader window.

## Implementation

Implementation commit:

- `e8822137c71e16cca94e81f021e883894faea09a` — `live-proof: revoke Recorder authority at child start`
- `parallel/LIVE_PROOF_BUNDLE/unified_live_proof.py`
  - resulting blob: `6ca839c5651f070a3201193746b9d4df491947b5`

Regression commit:

- `40d29cb4d56572d01ebb8660d3b7a79b80b50472` — `test: cover Recorder child-start generation rollover`
- `parallel/LIVE_PROOF_BUNDLE/test_recorder_authority_generation.py`
  - resulting blob: `e56f6e4b94b399d32045beb3dd49ee71cb53f9d2`

No production or QA evidence outside the allowed write boundary was modified. In particular, `parallel/LIVE_PROOF_BUNDLE_QA_RECORDER_GENERATION/**` was left untouched.

## Generation-start authority semantics after the fix

The Recorder authority transition is now deliberately moved earlier than reader entry.

1. Child generation order/token is allocated monotonically at the child launch-attempt boundary.
2. Once a Recorder evidence object has an active bound generation, a recognized newer Recorder child launch advances that same `RecorderEvidence` to the newer generation **before** the subprocess spawn returns.
3. `begin_source_generation(...)` immediately clears admission and the authority freshness clock, so the new generation starts fail-closed: `admitted=false`, `currentFresh=false`, `currentHealthy=false` until valid new-generation admission/evidence arrives.
4. Delayed heartbeat/admission/fatal/stdout from generation N carries generation N's old token and is rejected once generation N+1 has been allocated.
5. The new reader later enters with the already-current token/order; that bind is idempotent and cannot create a second authority transition.
6. Recorder child spawn failure does **not** restore generation N. The newly allocated generation remains current but has no valid evidence, so health stays fail-closed.
7. Known non-Recorder child starts (including the current PYLAUNCH `launcher.py` path) do not roll Recorder authority.
8. Existing read-only, RAM-writes-0, input-injection-disabled, freshness, fatal-revocation, and stale-generation rejection semantics were not relaxed.

The generation token was made PID-independent (`recorder-child:<order>`) so a generation can be allocated/revoked before process creation. This is intentional: fail-closed behavior on a failed restart is stronger than waiting for a PID and risking restoration of old authority.

## Implementation-side validation

A focused worker-side semantic harness covering the changed generation/child-start logic passed **6/6** vectors:

- stale generation-1 heartbeat remains rejected after a direct rollover;
- current-generation admission/heartbeat still renews normally;
- wrong-generation admission fails closed;
- generation-2 child start revokes generation 1 before the new reader starts;
- synthetic generation-2 spawn failure leaves the newer generation fail-closed and cannot restore generation-1 heartbeat authority;
- a PYLAUNCH/non-Recorder child start does not roll Recorder generation.

The committed generation regression file now contains three new orchestration-directed tests in addition to the existing generation matrix:

- `test_child_start_rollover_revokes_before_new_reader`
- `test_failed_recorder_child_start_does_not_restore_old_authority`
- `test_non_recorder_child_start_does_not_roll_recorder_generation`

The existing Recorder heartbeat regression and Unified regression sources were re-read against the change. Their authority paths are not loosened: legacy heartbeat tests remain on the unbound compatibility path, while Unified recovery tests continue to require explicit newer source generation.

GitHub reports **0 Actions check runs** for the regression commit. The connected execution environment does not expose a runnable private-repository checkout, so this implementation thread cannot honestly claim that the full repository Recorder heartbeat / Unified / preflight suite was executed here. That limitation is why this result is only `READY FOR FRESH INDEPENDENT QA`, not QA PASS.

## Required fresh QA

A new independent QA/retest stage must run against current `main` and attack the real orchestration window:

1. generation 1 admitted + healthy;
2. generation 2 Recorder child launch/start boundary;
3. generation-2 reader has not started yet;
4. delayed generation-1 trusted heartbeat arrives;
5. generation-1 heartbeat must be rejected, `authorityGeneration` must not advance, and current health must remain false until valid generation-2 evidence arrives.

It should also rerun the existing Recorder generation, Recorder heartbeat, Unified live-proof, Unified preflight, freshness and fail-closed regressions. This implementation thread does not perform or pre-judge that independent QA.

## Scope / safety

- Owner action: **NO**
- Browser/WOF live run: **NOT RUN / NOT REQUESTED**
- WOF-052/052L long capture: **NOT RUN / NOT REQUESTED**
- PYLAUNCH implementation: **UNCHANGED**
- Alpha Transport / Owner OneClick / HUD: **UNCHANGED**
- Independent QA evidence: **UNCHANGED**

## Stop condition

**COMPLETE — RECORDER CHILD-START GENERATION FIX — READY FOR FRESH INDEPENDENT QA**

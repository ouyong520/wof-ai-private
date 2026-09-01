# Unified Live Proof Recorder Authority Heartbeat — Fix Result

Date: 2026-09-01
Stage: `UNIFIED_LIVE_PROOF_RECORDER_AUTHORITY_HEARTBEAT_FIX_V1`
Priority: P1 mainline release gate

## Verdict

**UNIFIED LIVE PROOF RECORDER AUTHORITY HEARTBEAT FIX READY — READY FOR FRESH QA**

Owner action: `NO`

This is implementation READY only. It is **not** final Unified Live Proof freshness PASS. A fresh independent Unified Live Proof freshness QA must re-read the new default-branch implementation and close the previous pre-fix blocker before repository preflight can honestly permit a bounded real Browser/WOF run.

## Precise blocker closed

The pre-fix `RecorderEvidence.feed()` refreshed Recorder success freshness for every non-empty stdout fragment. A historical admission could therefore age stale and then become `current_healthy=true` again after arbitrary diagnostic / carriage-return output.

The implementation now separates:

- generic Recorder stdout diagnostics (`outputGeneration` / diagnostic timestamps), from
- trusted Recorder authority (`authorityGeneration` / authority freshness).

Generic stdout remains observable but cannot renew success authority.

## Trusted heartbeat semantics

Heartbeat recognition is derived narrowly from the real Recorder `FleetSupervisor.run()` producer contract:

`Fleet entries N | Recorder workers M | READ ONLY / RAM writes 0`

Authority renewal requires:

- exact prefix/middle/suffix structure after normal stdout whitespace trimming;
- numeric Fleet entry and Recorder worker counts;
- `entries >= 1`;
- `workers >= 1`;
- an already-current non-revoked Recorder admission.

Malformed / near-match text, arbitrary periodic status text, `RAM writes != 0`, zero workers, zero entries, wrong casing, nonnumeric counts, or extra suffix text do not renew authority.

A fresh recognized admission itself establishes a new authority generation. Fatal/revocation is evaluated first, revokes admission authority, and later generic output or supervisor heartbeat cannot revive it without a new valid admission.

## Generation-gate behavior

`authority_generation_snapshot()` now uses Recorder `authorityGeneration`, not generic `outputGeneration`.

Therefore both Owner freshness gates require a genuinely newer trusted Recorder authority generation together with the existing newer PYLAUNCH and process generations. Arbitrary Recorder diagnostics cannot satisfy either gate.

CR-aware reader behavior is unchanged: `\r` and `\n` still delimit Recorder output fragments, but semantic classification now decides whether a fragment is diagnostic-only or trusted authority.

## Status / safety output

Recorder status now exposes both diagnostic and authority evidence, including:

- `lastAuthorityUtc`
- `authorityAgeSeconds`
- `authorityGeneration`
- `admissionAuthorityGeneration`
- `lastAuthorityKind`
- `lastHeartbeatEvidence`
- existing diagnostic `lastOutputUtc` / `outputAgeSeconds` / `outputGeneration`

Safety behavior remains unchanged:

- `readOnly=true`
- `ramWrites=0`
- `inputInjection=false`
- no Worker replacement/wrap
- no gameplay input capability added
- `longCaptureAutoStarted=false`

## Repository changes

Implementation:

- `parallel/LIVE_PROOF_BUNDLE/unified_live_proof.py`
  - implementation commit: `dbf3bd67df1e5946e14d780ea81b26ccf3c23669`
  - current blob after fix: `0d9010007910f58b77c64fde98264697191bb679`

Targeted deterministic regression:

- `parallel/LIVE_PROOF_BUNDLE/test_recorder_authority_heartbeat.py`
  - add commit: `ec5dd803f60e8f5d972df9d1539b37834d296897`

Existing Unified Live Proof regression now imports the targeted authority suite, so the fixed preflight regression command also executes the new vectors:

- `parallel/LIVE_PROOF_BUNDLE/test_unified_live_proof.py`
  - integration commit: `0f9f3f8cd8a63fcd7a5380feccb9ff7dc23a69d2`
  - current blob: `181376494324cab51d8048f914b2f6d30438e2c0`

## Validation

Affected implementation semantics were exercised with the current committed test definitions in an isolated local verification harness.

1. Targeted Recorder authority adversarial suite

   `python -m unittest -v test_recorder_authority_heartbeat.py`

   Result: **PASS — Ran 8 tests, OK**

   Covers:
   - stale admission + arbitrary diagnostic cannot revive;
   - genuine current supervisor heartbeat refreshes only trusted authority;
   - malformed / near-match heartbeat fails closed;
   - repeated arbitrary output cannot advance authority generation;
   - fatal authority cannot be revived by later output;
   - valid CR-delimited heartbeat parsing;
   - stale/future/missing child process authority fails closed;
   - authority snapshot ignores generic output generation.

2. Existing + targeted Unified Live Proof regression command

   `python -m unittest -v test_unified_live_proof.py`

   Result: **PASS — Ran 42 tests, OK**

   This is the existing 34-test suite plus the 8 imported authority-heartbeat vectors. Existing process-health, PYLAUNCH freshness, safety, Owner gating, and `longCaptureAutoStarted=false` behavior remain green.

3. Preflight hardening tests

   `python -m unittest -v test_unified_preflight.py`

   Result: **PASS — Ran 13 tests, OK**

   The hardening logic remains fail-closed for blocked fresh-QA/result inputs and does not start the live stage when repository-side P0/P1 status gates are blocked.

## Default-branch concurrency check

After the integration commit, default branch advanced by one unrelated commit `947c3c5433a1fe5bf88845c6d1f529e40b82510f` that added only:

- `parallel/ALPHA_TRANSPORT_QA_STALE_GENERATION/targeted_stale_generation_qa.mjs`

No `parallel/LIVE_PROOF_BUNDLE/**` file from this stage was overwritten.

## Fresh QA handoff

The current `parallel/LIVE_PROOF_BUNDLE_QA_FRESHNESS/RESULT.md` is intentionally still the **pre-fix** BLOCKED report and identifies the old implementation blob `ce2e9f970f1a9e70493eb0d06b04431ea4870aa1`.

Do not treat that old result as a verdict on this implementation. The required next stage is a **fresh independent Unified Live Proof freshness QA** against current default-branch HEAD / blob `0d9010007910f58b77c64fde98264697191bb679`.

Until that fresh QA closes, implementation READY must not be promoted to final PASS and repository preflight must continue to respect the existing fresh-QA status gate.

## Stop condition

`UNIFIED LIVE PROOF RECORDER AUTHORITY HEARTBEAT FIX READY — READY FOR FRESH QA`

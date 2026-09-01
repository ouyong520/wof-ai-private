# Unified Live Proof Recorder Authority Heartbeat — Fresh QA Start Prompt

stageId: `UNIFIED_LIVE_PROOF_RECORDER_AUTHORITY_HEARTBEAT_QA_V1`

Priority: **P1 — Alpha live-proof admission authority**

## Dedup / claim

Follow `parallel/PM/STAGE_DEDUP_GUARD.md`.
If equivalent durable result exists, return exactly:
`ALREADY COMPLETE — SAFE TO CLOSE — 当前线程空闲`
If claimed/executing, return exactly:
`ALREADY CLAIMED — SAFE TO CLOSE — 当前线程空闲`
Otherwise claim under `parallel/PM/STAGE_CLAIMS/UNIFIED_LIVE_PROOF_RECORDER_AUTHORITY_HEARTBEAT_QA_V1.json`.

## Role

You are fresh independent QA. Do not implement the fix.

## Read first

Re-read current HEAD, especially:
- `parallel/LIVE_PROOF_BUNDLE/**`
- `parallel/LIVE_PROOF_BUNDLE/RECORDER_AUTHORITY_HEARTBEAT_FIX_RESULT.md`
- previous `parallel/LIVE_PROOF_BUNDLE_QA_FRESHNESS/**`
- current preflight hardening result/tests

## Former blocker

Arbitrary non-empty Recorder stdout could refresh stale admission authority because generic output freshness and trusted heartbeat/admission freshness were conflated.

The fix claims to separate trusted Recorder/Fleet authority heartbeat from generic stdout. Independently prove that claim.

## Required adversarial QA

Construct fresh independent cases covering at minimum:
1. admitted=true becomes stale; arbitrary stdout / CR / diagnostics / unrelated JSON cannot revive admission;
2. partial stdout fragments cannot renew authority;
3. recognized current supervisor heartbeat renews only the matching current authority generation;
4. fresh recognized admission renews authority correctly;
5. stale prior-generation heartbeat/admission cannot revive a new generation;
6. fatal/revocation remains dominant;
7. current healthy requires trusted authority freshness, not generic process liveness;
8. owner double gates, `longCaptureAutoStarted=false`, Chinese UX and fail-closed preflight remain intact;
9. existing live-proof + preflight + new heartbeat regressions remain green;
10. no owner Browser/WOF required.

Do not rely only on implementation tests; create independent adversarial fixtures/runners under a QA-only directory.

## Write boundary

Write only:
- `parallel/LIVE_PROOF_BUNDLE_QA_RECORDER_HEARTBEAT/**`
- mandatory claim file

Do not modify `parallel/LIVE_PROOF_BUNDLE/**` implementation, PYLAUNCH, Recorder, Transport, HUD, or Alpha.

## Delivery reassessment

PASS only if arbitrary stdout cannot renew admission authority and trusted heartbeat semantics are generation-safe.
If PASS, explicitly state whether Unified Preflight current-head recheck is unblocked.

## Stop

Success:
`PASS — UNIFIED LIVE PROOF RECORDER AUTHORITY HEARTBEAT FRESH QA — READY FOR CURRENT-HEAD PREFLIGHT RECHECK`

Failure:
`BLOCKED — UNIFIED LIVE PROOF RECORDER AUTHORITY HEARTBEAT FRESH QA — <precise blocker>`

Owner action: **NO**.

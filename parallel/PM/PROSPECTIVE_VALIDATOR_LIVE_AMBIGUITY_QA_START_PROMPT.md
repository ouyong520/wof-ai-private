# Prospective Validator Live Ambiguity P0 Fix — Fresh Independent QA Start Prompt

stageId: `PROSPECTIVE_VALIDATOR_LIVE_AMBIGUITY_QA_V1`
priority: `P0`

## Dedup / claim
Follow `parallel/PM/STAGE_DEDUP_GUARD.md`. If equivalent complete/claimed work exists, use the standard exact dedup stop message. Otherwise claim under `parallel/PM/STAGE_CLAIMS/PROSPECTIVE_VALIDATOR_LIVE_AMBIGUITY_QA_V1.json`.

## Role
Fresh independent QA. Do not accept the fix thread's READY verdict as proof.

## Read first
- `parallel/PROSPECTIVE_VALIDATOR/RESULT.md`
- current `parallel/PROSPECTIVE_VALIDATOR/**`
- prior blocker result and adversarial fixture under `parallel/PROSPECTIVE_VALIDATOR_QA_DISCOVERY_V2_HARDENING/**`

## Must prove
1. unique live room -> topology becomes shared/cross-page ambiguous -> affected room is censored/finalized before any later prospective `drain()/ingest()`.
2. there is no positive-duration audit gap that can admit post-ambiguity evidence.
3. current exact `(pageTargetId, workerTargetId)` pair is freshly re-proven before each prospective evidence admission cycle.
4. topology scan failure/unverified pair fails closed and cannot defer buffered evidence for later ingest.
5. remote cleanup/stop payload cannot bypass fresh topology authority and enter prospective counters.
6. two pages / two distinct Workers remain independently admissible.
7. shared Worker ambiguity admits none; unrelated rooms remain isolated.
8. discovery-only evidence never enters prospective counters.
9. all conservative manifest gates remain actually enforced: minProspectiveSignals, minProspectiveRooms, requireZeroHardMiss, minDistinctTargets, minObservedTypes, requireLifecycleReset; unknown gate fails closed.
10. PASS remains research-only and `productionPromotionAllowed=false`.
11. exact World 921031 / endpoint confinement / association safety remain intact.
12. `readOnly=true / ramWrites=0 / inputInjection=false`, no Worker replacement/rewrite.

Create at least one independent timing/adversarial fixture around topology transition and one around cleanup/finalization.

## Write scope
Write only under:
- `parallel/PROSPECTIVE_VALIDATOR_QA_LIVE_AMBIGUITY/**`
- mandatory claim file
Do not modify `parallel/PROSPECTIVE_VALIDATOR/**`.

## Stop condition
Success:
`PASS — PROSPECTIVE VALIDATOR LIVE AMBIGUITY P0 FRESH QA`
Or stop on one precise P0/P1 blocker with fresh-fix ownership.

No Owner Browser run.
Owner action: `NO`.

# Unified Windows Live Proof Freshness Fix — Fresh Independent QA Start Prompt

stageId: `UNIFIED_LIVE_PROOF_FRESHNESS_QA_V1`
priority: `P1`

## Dedup / claim
Follow `parallel/PM/STAGE_DEDUP_GUARD.md`. If already complete/claimed, use the standard exact dedup stop message. Otherwise claim under `parallel/PM/STAGE_CLAIMS/UNIFIED_LIVE_PROOF_FRESHNESS_QA_V1.json`.

## Role
Fresh independent QA of the current `parallel/LIVE_PROOF_BUNDLE/**`. Do not trust fix-thread self-tests as independent proof.

## Read first
- `parallel/LIVE_PROOF_BUNDLE/FRESHNESS_FIX_RESULT.md`
- current `parallel/LIVE_PROOF_BUNDLE/**`
- prior independent blocker under `parallel/LIVE_PROOF_BUNDLE_QA_FAILCLOSED/**`
- current PYLAUNCH proof schema and Recorder status semantics as read-only dependencies

## Must prove adversarially
1. empty/partial/malformed child process health cannot authorize PASS.
2. both required child facts must be explicit/current/live.
3. stale/missing/malformed/future PYLAUNCH `lastUpdateUtc` cannot authorize current PASS.
4. live-but-hung PYLAUNCH with a recent old PASS cannot survive the generation-advance gates.
5. Recorder old admission without fresh output/heartbeat cannot authorize readiness.
6. carriage-return heartbeat handling works without accepting arbitrary stale text as new authority.
7. Owner prompt is ineligible unless all current authority generations have advanced.
8. after simulated Owner `Y`, all required authority generations must advance again before final PASS.
9. fatal/exit/blocker during Owner answering revokes authority.
10. historical positive evidence remains diagnostics only and cannot restore readiness.
11. recovery requires genuinely new current evidence/generation.
12. `longCaptureAutoStarted=false` always.
13. Simplified Chinese owner path remains intact.
14. safety stays `readOnly=true / ramWrites=0 / inputInjection=false / no Worker replacement`.

Build fresh adversarial fixtures for malformed health + live-but-hung recent PASS, not just copies of implementation tests.

## Write scope
Write only under:
- `parallel/LIVE_PROOF_BUNDLE_QA_FRESHNESS/**`
- mandatory claim file
Do not modify `parallel/LIVE_PROOF_BUNDLE/**`, PYLAUNCH, Recorder, Fleet, Alpha, or Prospective.

## Stop condition
Success:
`PASS — UNIFIED LIVE PROOF FRESHNESS FRESH INDEPENDENT QA`
Or one precise P0/P1 blocker.

No Owner Windows/WOF run.
Owner action: `NO`.

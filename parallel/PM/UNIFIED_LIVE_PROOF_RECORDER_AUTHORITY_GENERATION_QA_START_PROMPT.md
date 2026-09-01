# Unified Live Proof Recorder Authority Generation — Fresh QA Start Prompt

stageId: `UNIFIED_LIVE_PROOF_RECORDER_AUTHORITY_GENERATION_QA_V1`

Priority: **P1 — Alpha live-proof Recorder authority generation safety**

## Dedup / claim

Follow `parallel/PM/STAGE_DEDUP_GUARD.md`.

If equivalent durable result already exists, return exactly:
`ALREADY COMPLETE — SAFE TO CLOSE — 当前线程空闲`

If this stage is already claimed/executing, return exactly:
`ALREADY CLAIMED — SAFE TO CLOSE — 当前线程空闲`

Otherwise create the atomic claim:
`parallel/PM/STAGE_CLAIMS/UNIFIED_LIVE_PROOF_RECORDER_AUTHORITY_GENERATION_QA_V1.json`.

## Role

You are **fresh independent QA**. Do not implement or repair the fix in this stage.

The implementation stage `UNIFIED_LIVE_PROOF_RECORDER_AUTHORITY_GENERATION_FIX_V1` is complete and claims that Recorder authority is now bound to the exact runtime child generation. Independently prove or disprove that claim against current main.

## Read first

Re-read current HEAD, especially:

- `parallel/LIVE_PROOF_BUNDLE/RECORDER_AUTHORITY_GENERATION_FIX_RESULT.md`;
- `parallel/LIVE_PROOF_BUNDLE/**` current implementation/tests;
- `parallel/LIVE_PROOF_BUNDLE_QA_RECORDER_HEARTBEAT/**` existing independent QA corpus;
- previous Unified freshness/fail-closed QA results;
- current Unified preflight result/tests;
- the completed fix stage claim.

## Former blocker

A stale prior-generation Recorder reader could replay heartbeat/admission text after a restart/reconnect and potentially refresh or revive the authority slot belonging to a newer runtime generation.

The fix claims that the active Recorder child generation is now a first-class provenance boundary and that older readers are diagnostic only.

## Required independent adversarial QA

Create a fresh QA-only runner/fixtures and cover at minimum:

1. generation 1 obtains valid admission + trusted heartbeat;
2. starting generation 2 immediately revokes generation-1 current authority/freshness before generation-2 admission;
3. delayed generation-1 heartbeat after rollover cannot renew generation 2, cannot move the authority freshness clock, and cannot restore `current_healthy`;
4. delayed/replayed generation-1 admission cannot replace, revive, or roll back the current generation-2 authority slot;
5. delayed generation-1 fatal/revocation after generation 2 is active cannot corrupt the newer authority slot and is handled according to the documented generation semantics;
6. missing or wrong generation on the strict real-runtime path fails closed;
7. valid generation-2 admission + trusted heartbeat renews normally;
8. arbitrary stdout, CR-only output, diagnostics, unrelated JSON, and partial stdout fragments cannot renew admission authority;
9. current-generation fatal/revocation remains dominant and cannot coexist with an authoritative healthy PASS;
10. repeated restart/reconnect rollovers remain monotonic across at least three generations;
11. existing Recorder heartbeat QA remains green;
12. existing Unified live-proof, freshness/fail-closed, and current preflight regressions remain green or any failure is precisely attributed;
13. Owner double gates, Chinese owner UX, `longCaptureAutoStarted=false`, read-only mode, zero game-memory writes, and no input injection remain intact;
14. no Owner Browser/WOF run is required for this QA.

Do not rely only on implementation-authored tests. The decisive evidence must come from independent QA fixtures/runners.

## Write boundary

Write only:

- `parallel/LIVE_PROOF_BUNDLE_QA_RECORDER_GENERATION/**`;
- mandatory stage claim file.

Do not modify:

- `parallel/LIVE_PROOF_BUNDLE/**` implementation;
- PYLAUNCH;
- WOF052L Recorder;
- Alpha Transport;
- HUD;
- Browser production rules;
- Owner one-click implementation.

If a blocker is found, record it precisely and stop; do not fix it in this QA thread.

## Delivery reassessment

PASS only if stale/wrong prior-generation authority evidence is proven unable to mutate or revive the current generation while valid current-generation admission/heartbeat still works normally.

On PASS, explicitly state whether current-head Unified preflight / Alpha formal integration QA is unblocked.

## Stop

Success:
`PASS — UNIFIED LIVE PROOF RECORDER AUTHORITY GENERATION FRESH QA — READY FOR CURRENT-HEAD PREFLIGHT / INTEGRATION QA`

Failure:
`BLOCKED — UNIFIED LIVE PROOF RECORDER AUTHORITY GENERATION FRESH QA — <precise blocker>`

Owner action: **NO**.

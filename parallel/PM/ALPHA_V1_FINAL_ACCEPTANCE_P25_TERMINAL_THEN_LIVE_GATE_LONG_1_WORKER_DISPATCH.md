# Alpha V1 — P25 Terminal Then Live Gate — Long 1 Worker Dispatch

This dispatch supersedes the prior P25+P28 two-worker dispatch because P28 is now terminal COMPLETE / integrationReady=true and its PROGRESS is TERMINAL/100.

Only one genuine independent worker task remains before the real-WOF Owner gate: the existing ACTIVE P25 Final Acceptance Composite Capture Integration claim.

Do not create a replacement P25 claim, recovery claim, filler P29, or duplicate worker.

## Worker 1 — P25 exact-token continuation

Stage: `ALPHA_V1_PRODUCT_TAKEOVER_P25_FINAL_ACCEPTANCE_COMPOSITE_CAPTURE_INTEGRATION`

Dedup key: `alpha.v1.product-takeover.final-acceptance-composite-capture-integration-v1`

Existing claimToken: `1a8e410f279e1450057986f7e8212959`

Continuation authority: `parallel/PM/ALPHA_V1_P25_AFTER_P27_BLOCKER_RESOLVED_CONTINUATION.md`

Required work is intentionally narrow:
1. Re-read current canonical/stage claims and confirm the exact existing token remains ACTIVE.
2. Update P25 PROGRESS at continuation start.
3. Re-read terminal P27 RESULT and the committed staged canonical-feed seam.
4. Perform the minimum deterministic post-P27 revalidation that the existing P25 composite path consumes same-session maintained P10 canonical coordinator status and no longer fails solely with `NOT_EXPOSED_BY_STAGED_RUNTIME_STATUS`.
5. Do not redesign P25, widen ownership, run real WOF, or manufacture P22/P24/W3/Owner-visible evidence.
6. If repository-level revalidation passes, publish truthful RESULT `COMPLETE` / `integrationReady=true`; otherwise publish a precise new `BLOCKED` result.
7. Close the exact-token canonical/stage claims, then PROGRESS `TERMINAL/100`, then final `WORKER_RESULT` commit.

P28 is already terminal and must not be reopened. P26 remains historical terminal BLOCKED and must not be recovered.

After P25 terminalizes, PM must fresh-read `parallel/PM/ALPHA_V1_FINAL_LIVE_ACCEPTANCE_OWNER_GATE.md`. The real live sequence remains Owner-gated and begins with exact staging plus bounded W3 normal-play qualification; no additional repo-side W3 reverse engineering should be dispatched merely to avoid the live qualification.

Progress checkpointing must follow `parallel/PM/ALPHA_WORKER_PROGRESS_CHECKPOINT_PROTOCOL_V1.md`; keep `parallel/PM/PROGRESS/ALPHA_V1_PRODUCT_TAKEOVER_P25_FINAL_ACCEPTANCE_COMPOSITE_CAPTURE_INTEGRATION_PROGRESS.json` current at mandatory milestones and before any non-terminal stop.

Terminal reporting must follow `parallel/PM/ALPHA_WORKER_RESULT_FAST_FEEDBACK_PROTOCOL_V1.md`.

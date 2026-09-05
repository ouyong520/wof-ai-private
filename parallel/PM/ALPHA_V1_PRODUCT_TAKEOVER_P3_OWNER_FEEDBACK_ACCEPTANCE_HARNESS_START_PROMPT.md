# Alpha V1 Product Takeover P3 — Owner Feedback + Acceptance Harness

stageId: `ALPHA_V1_PRODUCT_TAKEOVER_P3_OWNER_FEEDBACK_ACCEPTANCE_HARNESS`
dedupProtocol: `v2`
dedupKey: `alpha.v1.product-takeover.first-owner-gate.owner-feedback-acceptance-harness-v1`
dedupMode: `exclusive`

Repository: `ouyong520/wof-ai-private`

Parent authority:
`parallel/PM/ALPHA_V1_PRODUCT_TAKEOVER_FIRST_OWNER_GATE_PARALLEL_3_WORKER_V2_DISPATCH.md`

## Dedup preflight

Before any implementation/test work:

1. Read latest `main`, this prompt, parent dispatch, and `parallel/PM/STAGE_DEDUP_GUARD.md`.
2. Confirm no canonical exists at:
   `parallel/PM/DEDUP_CLAIMS/alpha.v1.product-takeover.first-owner-gate.owner-feedback-acceptance-harness-v1.json`.
3. Create-only canonical with fresh unpredictable `claimToken`, latest-main `startCommit`, `state=ACTIVE`, and exact metadata from this prompt.
4. Re-read and verify exact token + all fields.
5. Then create-only:
   `parallel/PM/STAGE_CLAIMS/ALPHA_V1_PRODUCT_TAKEOVER_P3_OWNER_FEEDBACK_ACCEPTANCE_HARNESS.json`
   using the same token.
6. Re-read and verify stage claim before implementation.
7. Any create/verification failure is fail-closed. Do not invent recovery metadata.

## Scope

Alpha Owner-visible product only. Do not read/run/modify/test Collector, Unified Collector, Training Farm / 10训.

## Your only objective

Build the first Owner-gate **feedback and acceptance layer** so PM can diagnose the result from one obvious artifact without asking Owner to open DevTools, inspect JSON, choose files, or explain internal states.

This worker does not implement HUD/runtime/updater behavior. It only provides deterministic feedback aggregation, fixtures, tests, and acceptance/readiness tooling.

The harness must consume the stable outputs expected from W1/W2/P1/P2 and classify the first-gate result into one precise layer, such as:

- `BOOTSTRAP_NOT_READY`
- `UPDATE_CHANNEL_NOT_READY`
- `LIVE_MODE_NOT_FIXED_DRAW`
- `RUNTIME_NOT_STARTED`
- `HUD_INJECTION_MISSING`
- `GAME_CANVAS_CONTEXT_MISSING`
- `DRAW_HOOK_NOT_FIRING`
- `DRAWING_BUFFER_INVALID`
- `DRAW_FAILED`
- `MACHINE_DRAW_PROOF_PRESENT_AWAITING_OWNER_VISUAL`
- `READY_FOR_OWNER_FIXED_TEST`

The harness must never convert synthetic/fixture state into a real Owner visual PASS.

## Feedback contract

Create or improve one obvious Owner-facing artifact contract under `Documents\WOF_RESULTS`, centered on the existing `LATEST_ALPHA_FEEDBACK.txt` concept. The aggregation logic/schema should make these fields immediately visible when available:

- current release SHA
- alpha-live/live-mode name
- updater/managed-repo readiness
- runtime process readiness
- fixed-smoke raw status file/path
- fixed-smoke state
- drawHooked
- callbackCount
- drawCount
- drawing buffer
- native `384x224`, center `(192,112)`, label `TEST`
- latest error/reason
- one final PM routing classification

If implementation uses a helper, keep it narrow and read-only over existing result files/state. Do not make it responsible for Git fetch, process launch, HUD injection, or branch promotion.

## File boundary

Allowed:
- P3-specific tests/fixtures
- one narrow feedback aggregation/helper/schema module if useful
- docs/P3 SUBRESULT

Do not edit:
- `product/alpha/wof_alpha_hud.js`
- `render_authority_measurement_entry.py` or P1 runtime gate production files
- `owner_live_retest_loop.ps1` / installer / P2 live-mode production files
- W3 renderer/object authority
- `alpha-live` ref

## Acceptance

Focused fixtures/tests must prove:

A. each upstream failure maps to one precise routing state;
B. machine `FIXED_TEST_ACTUALLY_DRAWN` is not treated as human-visible PASS;
C. stale/missing status does not false-green;
D. malformed feedback input fails closed;
E. one artifact contains enough data for PM to route a defect without Owner DevTools;
F. harness can later validate the coherent P1+P2 candidate without modifying production.

## Exit

Deliver integration-ready tests/feedback tooling + durable P3 SUBRESULT, then close canonical/stage with exact token as COMPLETE, or return one precise external BLOCKED.

Do not ask Owner to test. Do not move `alpha-live`. Do not stop at analysis or one patch.

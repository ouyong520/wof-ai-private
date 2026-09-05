stageId: `ALPHA_V1_PRODUCT_TAKEOVER_P8_CANONICAL_OVERLAY_PRODUCT_PLAN`
dedupProtocol: `v2`
dedupKey: `alpha.v1.product-takeover.canonical-overlay-product-plan-v1`
dedupMode: `exclusive`
resultProtocol: `wof-alpha-worker-result-v1`
resultJsonPath: `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P8_CANONICAL_OVERLAY_PRODUCT_PLAN_RESULT.json`
resultMdPath: `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P8_CANONICAL_OVERLAY_PRODUCT_PLAN_RESULT.md`
terminalCommitPrefix: `WORKER_RESULT ALPHA_V1_PRODUCT_TAKEOVER_P8_CANONICAL_OVERLAY_PRODUCT_PLAN`
dispatchManifestPath: `parallel/PM/DISPATCH_MANIFESTS/ALPHA_V1_CANONICAL_RENDER_ANCHOR_P5_P8_P9_CONTINUATION_3_WORKER_V1.json`

# Alpha V1 Product Takeover P8 — Canonical Overlay Product Plan

Repository: `ouyong520/wof-ai-private`

Read latest main first, then:
- `parallel/PM/ALPHA_V1_CANONICAL_RENDER_ANCHOR_P5_P8_P9_CONTINUATION_3_WORKER_DISPATCH.md`
- `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P6_ENEMY_CANONICAL_RENDER_ANCHOR_LABELS_RESULT.json`
- `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P7_PLAYER_DANGER_CANONICAL_ANCHOR_RESULT.json`
- `product/alpha/wof_alpha_enemy_target_labels.js`
- `product/alpha/wof_alpha_player_head_warning.js`
- `parallel/PM/ALPHA_WORKER_RESULT_FAST_FEEDBACK_PROTOCOL_V1.md`

Perform dedup-v2 exactly: latest-main preflight -> create-only canonical claim -> re-read exact claimToken/fields/state ACTIVE -> create-only stage claim -> re-read exact same token/fields/state ACTIVE. Any failure is fail-closed. Do not invent recovery.

## Goal

Create one narrow pure product composition layer that invokes/reuses the already-complete P6 and P7 canonical planning APIs and returns one fail-closed canonical overlay plan. This is implementation/integration preparation, not QA and not W3 renderer-source proof.

Preferred new files only:
- `product/alpha/wof_alpha_canonical_overlay_plan.js`
- optional `product/alpha/canonical_overlay_plan_selfcheck.mjs`

Do not modify P5-owned launcher/HUD/runtime bridge files while P5 is ACTIVE. Do not modify W3 capture/producer/claim files. Do not move `alpha-live`.

## Required behavior

The composition API must accept the product inputs required by the existing P6/P7 canonical planners, including canonical enemy/player anchors, current actor generations, authority binding, drawing-buffer state, timestamps, enemy target markers, and danger warnings.

It must call the existing P6/P7 canonical planning APIs rather than reimplementing their geometry, target semantics, or danger grouping.

Return one explicit product plan with at least:
- schema/version/canonical mode;
- enemy target-label draw intents from P6;
- player danger draw intents from P7;
- suppression/diagnostic summaries adequate for runtime status;
- `fallback: "NONE"`;
- `readOnly=true`, `ramWrites=0`, `inputInjection=false`.

Fail closed:
1. no valid canonical authority binding -> no canonical draw intents;
2. mixed authority/runtime/renderer epochs across supplied anchor sets -> suppress affected output;
3. `SUPPRESSED`, stale, missing, unsafe, ambiguous, unproven or generation-mismatched anchor -> suppress affected output;
4. invalid/stale drawing-buffer mapping -> suppress affected output;
5. never fall back to world/camera projection, Y/Y-Z/Y+Z, screenshot/template tracking, click/calibration, nearest-sprite, relative geometry, or guessed constants;
6. preserve P6 target mapping exactly: `0 -> 1P`, `4 -> 2P`, `8 -> 3P`;
7. preserve P7 warning grouping/content semantics and do not expand danger policy.

Do not add a second HUD, DOM overlay, draw hook or production renderer. The output is a pure draw-intent/product-plan contract for later maintained-HUD consumption.

## Coordination boundary

P5 is ACTIVE and owns P1 maintained production HUD wiring. P8 must not modify `product/alpha/wof_alpha_hud.js` or P5 launcher bridge files unless PM issues a later integration authority after P5 closes.

W3 source qualification is still unproven. P8 must truthfully report implementation proof only and preserve zero draw intents for unproven/SUPPRESSED anchors.

## Minimum self-check only

Implementation first. Run only:
- JS parse/load;
- one narrow fixture where valid P6 label + P7 warning are composed into one plan;
- one narrow fixture where unproven/mixed-epoch canonical input produces zero affected draw intents and `fallback: NONE`.

No broad regression, Fresh QA, Owner acceptance, real-WOF run, or source qualification.

## Terminal

Write exact RESULT.json + RESULT.md declared above. Include implementation commits, changed files, minimal self-checks, integrationReady, productProof boundary, blocker and nextAction. Do not claim real-WOF or Owner visual PASS. Final commit begins:

`WORKER_RESULT ALPHA_V1_PRODUCT_TAKEOVER_P8_CANONICAL_OVERLAY_PRODUCT_PLAN <STATE>`

Chat only COMPLETE / SUBCOMPLETE / precise BLOCKED.

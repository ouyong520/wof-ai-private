stageId: `ALPHA_V1_PRODUCT_TAKEOVER_P6_ENEMY_CANONICAL_RENDER_ANCHOR_LABELS`
dedupProtocol: `v2`
dedupKey: `alpha.v1.product-takeover.enemy-canonical-render-anchor-labels-v1`
dedupMode: `exclusive`
resultProtocol: `wof-alpha-worker-result-v1`
resultJsonPath: `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P6_ENEMY_CANONICAL_RENDER_ANCHOR_LABELS_RESULT.json`
resultMdPath: `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P6_ENEMY_CANONICAL_RENDER_ANCHOR_LABELS_RESULT.md`
terminalCommitPrefix: `WORKER_RESULT ALPHA_V1_PRODUCT_TAKEOVER_P6_ENEMY_CANONICAL_RENDER_ANCHOR_LABELS`
dispatchManifestPath: `parallel/PM/DISPATCH_MANIFESTS/ALPHA_V1_CANONICAL_RENDER_ANCHOR_PARALLEL_3_WORKER_V1.json`

# Alpha V1 Product Takeover P6 — Enemy Canonical Render-Anchor Target Labels

Repository: `ouyong520/wof-ai-private`

Read latest main first, then:
- `parallel/PM/ALPHA_V1_CANONICAL_RENDER_ANCHOR_PARALLEL_3_WORKER_V1_DISPATCH.md`
- `parallel/PM/ALPHA_V1_PRODUCT_TAKEOVER_W3_RENDER_OBJECT_AUTHORITY_CONTINUATION_SUBRESULT.md`
- `parallel/PYLAUNCH/wof_launcher/render_object_anchor.py`
- `product/alpha/wof_alpha_enemy_target_labels.js`

Perform dedup-v2 create-only canonical + exact-token re-read + create-only stage + exact-token re-read before implementation. Any ownership failure is fail-closed. Do not invent recovery.

## Goal

Add a canonical render-anchor planning path for enemy target labels so enemy head `1P/2P/3P` placement no longer depends on the legacy world/camera/Y-model projection once a proven renderer/object source exists.

## Required implementation

1. Preserve target semantics exactly:
   - `target7E == 0` -> target `P1` -> label `1P`
   - `target7E == 4` -> target `P2` -> label `2P`
   - `target7E == 8` -> target `P3` -> label `3P`.
2. Add an explicit canonical-anchor path that consumes enemy anchors already resolved from the proven `wof-render-object-anchor-v1` contract or equivalent normalized READY objects carrying actor/generation/native 384x224/authority epochs/safety.
3. Label anchor position must come directly from the canonical enemy head anchor, then map native coordinates into the maintained drawing-buffer content rect.
4. Missing, SUPPRESSED, stale, unsafe, ambiguous, unproven, actor/generation mismatched, epoch mismatched, invalid native-size, or invalid drawing-buffer input must suppress that enemy label.
5. Enemy labels must not wait for P1 screenshot/head tracker and must not derive enemy position relative to P1.
6. Do not silently fall back from canonical mode into old world/camera projection. Existing legacy functions may remain for compatibility, but canonical mode must be explicit and fail-closed.
7. Do not change P1 HUD/runtime files owned by P5 or player danger files owned by P7. If common-HUD editing would be required, stop at an integration-ready planner/API and report that exact later dependency rather than racing another worker.
8. Do not edit W3 producer/capture files or claims. Do not move `alpha-live`. Do not ask Owner to test.

Preferred scope: `product/alpha/wof_alpha_enemy_target_labels.js` plus at most one narrow owned fixture/self-check file.

## Minimum self-check only

Implementation first. Run only:
- JS parse/load;
- one READY enemy canonical-anchor fixture producing the correct target label and drawing-buffer location;
- one stale/SUPPRESSED/generation-mismatch fixture producing no label;
- one check proving canonical mode does not invoke legacy projection fallback.

No broad regression/Fresh QA/Owner acceptance.

## Terminal

Write exact RESULT.json + RESULT.md declared above with implementation commits, changed files, minimal self-checks, integrationReady, blocker, productProof boundary, and nextAction. Do not claim real-WOF PASS. Final commit begins:

`WORKER_RESULT ALPHA_V1_PRODUCT_TAKEOVER_P6_ENEMY_CANONICAL_RENDER_ANCHOR_LABELS <STATE>`

Chat only COMPLETE / SUBCOMPLETE / precise BLOCKED.
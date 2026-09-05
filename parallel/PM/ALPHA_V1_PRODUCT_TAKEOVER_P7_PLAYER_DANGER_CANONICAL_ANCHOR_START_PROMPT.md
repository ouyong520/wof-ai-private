stageId: `ALPHA_V1_PRODUCT_TAKEOVER_P7_PLAYER_DANGER_CANONICAL_ANCHOR`
dedupProtocol: `v2`
dedupKey: `alpha.v1.product-takeover.player-danger-canonical-anchor-v1`
dedupMode: `exclusive`
resultProtocol: `wof-alpha-worker-result-v1`
resultJsonPath: `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P7_PLAYER_DANGER_CANONICAL_ANCHOR_RESULT.json`
resultMdPath: `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P7_PLAYER_DANGER_CANONICAL_ANCHOR_RESULT.md`
terminalCommitPrefix: `WORKER_RESULT ALPHA_V1_PRODUCT_TAKEOVER_P7_PLAYER_DANGER_CANONICAL_ANCHOR`
dispatchManifestPath: `parallel/PM/DISPATCH_MANIFESTS/ALPHA_V1_CANONICAL_RENDER_ANCHOR_PARALLEL_3_WORKER_V1.json`

# Alpha V1 Product Takeover P7 — Player Danger Canonical Anchor

Repository: `ouyong520/wof-ai-private`

Read latest main first, then:
- `parallel/PM/ALPHA_V1_CANONICAL_RENDER_ANCHOR_PARALLEL_3_WORKER_V1_DISPATCH.md`
- `parallel/PM/ALPHA_V1_PRODUCT_TAKEOVER_W3_RENDER_OBJECT_AUTHORITY_CONTINUATION_SUBRESULT.md`
- `parallel/PYLAUNCH/wof_launcher/render_object_anchor.py`
- `product/alpha/wof_alpha_player_head_warning.js`

Perform dedup-v2 create-only canonical + exact-token re-read + create-only stage + exact-token re-read before implementation. Any ownership failure is fail-closed. Do not invent recovery.

## Goal

Add a canonical actor-anchor planning path for player-head danger/warning placement. This stage changes spatial authority only; it does not expand threat-model policy.

## Required implementation

1. Preserve warning grouping by affected player `P1/P2/P3` and preserve existing warning content/semantics.
2. Add an explicit canonical-anchor path that consumes a READY player anchor from the proven `wof-render-object-anchor-v1` contract or equivalent normalized READY object carrying actor/generation/native 384x224/authority epochs/safety.
3. Derive warning draw rectangle from that canonical head anchor and maintained drawing-buffer content rect.
4. Missing, SUPPRESSED, stale, unsafe, ambiguous, unproven, actor/generation mismatched, epoch mismatched, invalid native-size, or invalid drawing-buffer input must suppress anchored warning placement rather than guess.
5. Canonical mode must not use legacy projection profile, camera sign/address, Y/Y-Z/Y+Z, head-clearance calibration, screenshot-template tracking, click calibration, or relative geometry as fallback.
6. Existing legacy projection functions may remain for compatibility, but canonical mode must be explicit and fail-closed.
7. Do not modify threat-generation policy or enemy target semantics. Do not modify P1 HUD/runtime files owned by P5 or enemy target-label files owned by P6. If common-HUD editing would be required, stop at an integration-ready planner/API and report the later integration dependency.
8. Do not edit W3 producer/capture files or claims. Do not move `alpha-live`. Do not ask Owner to test.

Preferred scope: `product/alpha/wof_alpha_player_head_warning.js` plus at most one narrow owned fixture/self-check file.

## Minimum self-check only

Implementation first. Run only:
- JS parse/load;
- one READY canonical player-anchor fixture producing a warning rect near that player head;
- one stale/SUPPRESSED/generation-mismatch fixture producing no anchored warning;
- one check proving canonical mode does not invoke legacy projection fallback.

No broad regression/Fresh QA/Owner acceptance.

## Terminal

Write exact RESULT.json + RESULT.md declared above with implementation commits, changed files, minimal self-checks, integrationReady, blocker, productProof boundary, and nextAction. Do not claim real-WOF PASS. Final commit begins:

`WORKER_RESULT ALPHA_V1_PRODUCT_TAKEOVER_P7_PLAYER_DANGER_CANONICAL_ANCHOR <STATE>`

Chat only COMPLETE / SUBCOMPLETE / precise BLOCKED.
# Alpha V1 Product Takeover P7 — Player Danger Canonical Anchor — RESULT

Status: **COMPLETE**

- stageId: `ALPHA_V1_PRODUCT_TAKEOVER_P7_PLAYER_DANGER_CANONICAL_ANCHOR`
- dedupKey: `alpha.v1.product-takeover.player-danger-canonical-anchor-v1`
- claimToken: `615ac7ba7b347e5e60d1faa6d8887a745f9ff62cdbef7bde`
- startCommit: `000beefe0210535ce5dcc5ca4e0a5792990ab8b2`
- implementation commit: `2aa158577a11d8a75fb01f9c1fdf33e84576ce28`
- integrationReady: **true**

## Implementation

Changed only `product/alpha/wof_alpha_player_head_warning.js`.

P7 adds a separate explicit canonical player-danger planning path while preserving the existing legacy projection API for compatibility:

- `resolveCanonicalAnchor(...)` consumes exact `wof-render-object-anchor-v1` READY player anchors for P1/P2/P3;
- exact native coordinate contract is `384x224`;
- affected-player grouping and warning content/semantics are unchanged;
- player actor and generation must match the current expected player generation;
- authority key, runtime epoch and renderer epoch must match the supplied canonical authority binding;
- exact safety contract is required: `readOnly=true`, `ramWrites=0`, `inputInjection=false`;
- invalid/missing/suppressed/stale/unsafe/ambiguous/unproven/generation-mismatched/authority-epoch-mismatched inputs suppress the anchored warning;
- native anchor is mapped only through the maintained drawing-buffer content rect;
- invalid/stale drawing-buffer input suppresses placement;
- `buildCanonicalPlan(...)` returns `fixed: []` and `fallback: 'NONE'`, so canonical mode cannot silently drop into world/camera projection, Y/Y-Z/Y+Z fitting, screenshot/template tracking, calibration, click or guessed relative geometry.

Threat-generation policy and enemy target semantics were not modified. P5/P6/W3 production ownership files and `alpha-live` were not modified.

## Minimum self-check

Only implementation-owned focused checks were performed.

1. **JS parse/load — PASS**
   - `node --check` was run against the exact local module copy whose git blob SHA was `e9eaa398a6aaa62e4c0cbf5f73a39c7cb0ac2295`.
   - That SHA matches the committed GitHub blob for `product/alpha/wof_alpha_player_head_warning.js`.

2. **READY canonical player anchor — PASS**
   - synthetic P2 generation 7 anchor at native `(192,80)` on a `768x448` content rect mapped to drawing-buffer `(384,160)`;
   - one warning remained grouped under P2 and produced one canonical anchored draw rectangle.

3. **Fail-closed suppression — PASS**
   - canonical `SUPPRESSED` with `RENDERER_SOURCE_UNPROVEN` produced no anchored warning and no fixed fallback;
   - stale canonical sample produced `STALE_CANONICAL_ANCHOR` and no anchored warning;
   - generation mismatch produced `CANONICAL_GENERATION_MISMATCH` and no anchored warning.

4. **No legacy projection fallback — PASS**
   - poison `projection` and `players` proxy inputs that throw on access were supplied alongside the canonical plan fixture;
   - canonical planning completed without touching them and reported `fallback: 'NONE'`.

No broad regression, Fresh QA, Owner acceptance or real-WOF run was performed.

## Product proof boundary

Classification: **IMPLEMENTATION_PROOF** only.

W3's authoritative continuation subresult explicitly states that the exact displayed-frame renderer/object source is **NOT YET PROVEN**. The W3 canonical consumer therefore remains fail-closed until bounded live qualification proves the source. P7 preserves that boundary: unproven/SUPPRESSED canonical input never becomes a guessed player-danger position.

This RESULT does **not** claim machine-draw proof, real-WOF product PASS, or Owner visual PASS.

## Blocker / next action

- blocker: **none for P7 implementation**
- integrationReady: **true**
- nextAction: PM may wire `buildCanonicalPlan(...)` into the canonical runtime/HUD integration after W3 supplies proven READY P1/P2/P3 anchors, current player generations and the matching authority/runtime/renderer binding. No further player-danger geometry redesign should be needed.

## Safety

- readOnly: `true`
- ramWrites: `0`
- inputInjection: `false`

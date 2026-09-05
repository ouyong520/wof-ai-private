# Alpha V1 Product Takeover P11 — Maintained HUD Canonical Overlay Wiring RESULT

Status: **COMPLETE / integration-ready**

- stage: `ALPHA_V1_PRODUCT_TAKEOVER_P11_MAINTAINED_HUD_CANONICAL_OVERLAY_WIRING`
- dedup key: `alpha.v1.product-takeover.maintained-hud-canonical-overlay-wiring-v1`
- claim token: `67b75598cf68a979fd6c10a547b44170838323ccbbe257dd`
- RESULT JSON: `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P11_MAINTAINED_HUD_CANONICAL_OVERLAY_WIRING_RESULT.json`

The dedup-v2 canonical claim and stage claim were created create-only, re-read with the exact same claim token before implementation, and are now both closed `COMPLETE`.

## Implementation

Implementation commits:

- `421d589da1b6bca1ee379b69a63b0d3028fa94ad` — wire P9/P8 canonical overlay into the maintained production WebGL HUD.
- `ee15c657a1577be57a6303789e6cc09b303a3875` — add the focused maintained-HUD canonical overlay seam self-check.

Changed implementation/test files:

- `product/alpha/wof_alpha_hud.js`
- `product/alpha/maintained_hud_canonical_overlay_selfcheck.mjs`

The maintained HUD now exposes the shared P10/P11 browser interface:

- `bindCanonicalOverlayAuthority(binding)`
- `ingestCanonicalAnchorEnvelope(payload)`
- `clearCanonicalOverlayAuthority(reason)`

The canonical browser chain is:

`P10 transport wrapper -> P9 normalizeEnvelope(...) -> P9 P6/P7 adapters + existing marker/warning semantics -> P8 buildCanonicalPlan(...) -> existing maintained HUD label/warning WebGL primitives`

No second renderer, DOM overlay, window, or canvas was added.

Enemy target-label intent payloads reuse the existing label atlas / `labelTex` / batched `drawLabelPlan(...)` path. Player danger-warning intent payloads reuse the existing warning badge texture / `warningTex` / `drawTexture(...)` path.

The fixed TEST smoke path remains independent. The existing P5/P1 direct top-marker tracker remains independent.

## Canonical takeover / fail-closed behavior

Once canonical overlay authority is bound, enemy-target and player-danger spatial placement is a hard canonical takeover:

- legacy enemy world/camera projection is not called as fallback;
- legacy player projection / player-head-spatial placement is not called as fallback;
- P1 tracker danger placement is not called as fallback;
- fixed warning placement is not used as a canonical spatial fallback;
- screenshot/template tracking, click calibration, Y / Y-Z / Y+Z models, nearest-sprite matching, guessed constants, and stale prior canonical coordinates are not introduced.

The HUD validates the transport schema and exact bound authority identity, calls P9 `normalizeEnvelope(...)`, and clears current canonical plans immediately when transport/P9 validation fails. It re-normalizes the retained payload on draw cadence so stale P9 records become suppressed rather than leaving a previous canonical draw plan visible.

The HUD calls P8 `buildCanonicalPlan(...)` with the current maintained WebGL drawing-buffer/content rectangle. It accepts only `mode=canonical-render-anchor`, `coordinateSpace=webgl-drawing-buffer`, and `fallback=NONE`.

P8 draw intents handled by the HUD are only:

- `enemy-target-label`
- `player-danger-warning`

Existing target semantics remain owned by P6/current marker semantics (`0 -> 1P`, `4 -> 2P`, `8 -> 3P`). Existing danger/threat content remains owned by the current warning message/P7 policy. The canonical envelope supplies canonical anchor identity/position, not replacement gameplay semantics.

`status()` now reports canonical overlay bound/state/reason, exact authority identity, envelope age/last receive time, emitted enemy-label count, emitted player-danger count, and `fallback=NONE`.

## Minimum self-check

- `node --check` on the exact committed HUD candidate — **PASS**. Local git blob `ae17a82c94a0b3ee3fe0a5ff195cc0c393b24959` matches the committed GitHub HUD blob.
- `node --check product/alpha/maintained_hud_canonical_overlay_selfcheck.mjs` — **PASS**. Committed self-check blob is `ff17373ca4211075fb4b64df6306cc820cdbb312`.
- Focused synthetic maintained-HUD seam — **PASS**:
  - bound + READY canonical transport invoked P9 normalization and P8 planning;
  - one enemy label and one player danger intent reached the existing WebGL label/warning draw paths;
  - mixed renderer-epoch transport immediately suppressed both canonical channels;
  - after suppression, another draw-hook callback did not produce legacy enemy/player spatial draws;
  - canonical status remained `fallback=NONE`;
  - fixed TEST remained callable and produced its maintained WebGL draw.

No broad regression, Fresh QA, real-WOF run, Owner acceptance, package churn, W3 qualification, or `alpha-live` movement was performed.

## Product-proof boundary

P11 implementation proof is complete and integration-ready for the browser/HUD side.

This RESULT does **not** claim W3 has qualified the exact displayed-frame renderer/object source, does not claim a real-WOF canonical enemy/player machine draw from W3, and does not claim Owner-visible PASS. While W3 input is unproven, the correct product behavior remains hidden/SUPPRESSED with no legacy spatial fallback.

## Blocker / next action

P11 implementation blocker: **none**.

Next action: P10 may use the exact HUD API after its source injection/load-order bridge installs P9/P8 before `wof_alpha_hud.js`. PM can then integrate P10 + P11; W3-qualified READY records remain the external prerequisite for a truthful real-WOF canonical overlay proof.

Safety: `readOnly=true`, `ramWrites=0`, `inputInjection=false`.

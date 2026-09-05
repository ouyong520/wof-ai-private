stageId: `ALPHA_V1_PRODUCT_TAKEOVER_P11_MAINTAINED_HUD_CANONICAL_OVERLAY_WIRING`
dedupProtocol: `v2`
dedupKey: `alpha.v1.product-takeover.maintained-hud-canonical-overlay-wiring-v1`
dedupMode: `exclusive`
resultProtocol: `wof-alpha-worker-result-v1`
resultJsonPath: `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P11_MAINTAINED_HUD_CANONICAL_OVERLAY_WIRING_RESULT.json`
resultMdPath: `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P11_MAINTAINED_HUD_CANONICAL_OVERLAY_WIRING_RESULT.md`
terminalCommitPrefix: `WORKER_RESULT ALPHA_V1_PRODUCT_TAKEOVER_P11_MAINTAINED_HUD_CANONICAL_OVERLAY_WIRING`
dispatchManifestPath: `parallel/PM/DISPATCH_MANIFESTS/ALPHA_V1_CANONICAL_OVERLAY_RUNTIME_HUD_PARALLEL_2_WORKER_V1.json`

# Alpha V1 Product Takeover P11 — Maintained HUD Canonical Overlay Wiring

Repository: `ouyong520/wof-ai-private`

Read latest `main` first, then:
- `parallel/PM/ALPHA_V1_CANONICAL_OVERLAY_RUNTIME_HUD_PARALLEL_2_WORKER_DISPATCH.md`
- `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P6_ENEMY_CANONICAL_RENDER_ANCHOR_LABELS_RESULT.json`
- `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P7_PLAYER_DANGER_CANONICAL_ANCHOR_RESULT.json`
- `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P8_CANONICAL_OVERLAY_PRODUCT_PLAN_RESULT.json`
- `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P9_CANONICAL_ANCHOR_RUNTIME_ENVELOPE_RESULT.json`
- `product/alpha/wof_alpha_canonical_anchor_envelope.js`
- `product/alpha/wof_alpha_canonical_overlay_plan.js`
- `product/alpha/wof_alpha_hud.js`

Perform dedup-v2 create-only canonical claim + exact-token re-read + create-only stage claim + exact-token re-read before implementation. Fail closed on any ownership error. Do not invent recovery.

## Goal

Wire the already-complete P9 envelope and P8 unified product plan into the **maintained production WebGL HUD** so the HUD has one canonical path for enemy target labels and player danger warnings.

Target chain inside the browser:

`P10 transport payload`
`→ P9 normalizeEnvelope(...)`
`→ P9 adapters to P6/P7 canonical inputs`
`→ P8 buildCanonicalPlan(...)`
`→ existing maintained HUD label/warning draw primitives`

No second overlay and no new canvas/window is allowed.

## Required HUD API

Implement the shared interface from the dispatch:
- `bindCanonicalOverlayAuthority(binding)`
- `ingestCanonicalAnchorEnvelope(payload)`
- `clearCanonicalOverlayAuthority(reason)`

Expose canonical-overlay state in `status()` sufficiently for runtime diagnostics: bound/unbound, READY/SUPPRESSED reason, authority identity, envelope age/last receive time, emitted enemy label count, emitted player danger count, and fallback=`NONE`.

## Required implementation behavior

1. Require `window.WOFAlphaCanonicalAnchorEnvelope` P9 and `window.WOFAlphaCanonicalOverlayPlan` P8. Do not recreate their validation/planning logic inside HUD.
2. On canonical authority bind, store exact authorityKey/runtimeEpoch/rendererEpoch (and World identity if present) and enter canonical overlay mode for enemy-target/player-danger spatial placement.
3. On payload ingest, require the transport schema from the shared dispatch and exact binding equality to the currently bound authority.
4. Normalize with P9 `normalizeEnvelope(...)`. Invalid envelope = canonical overlay channels SUPPRESSED and prior canonical draw plan cleared immediately.
5. Convert P9 envelope into inputs for P6/P7 using P9 helpers and existing current semantic messages already held by HUD:
   - enemy markers / `target7E` semantics remain sourced from the existing marker message;
   - player warnings / danger semantics remain sourced from the existing warning message;
   - canonical envelope supplies **position only**.
6. Feed those inputs through P8 `buildCanonicalPlan(...)` using the maintained current WebGL drawing-buffer/content-rect state.
7. Draw P8 `enemy-target-label` and `player-danger-warning` intents using the existing label/warning textures and WebGL draw path. Do not create a second renderer or DOM overlay.
8. Preserve target semantics exactly: `0→1P`, `4→2P`, `8→3P`.
9. Preserve existing warning content/threat policy. This task changes product position wiring only.
10. When canonical authority is bound, enemy/player spatial placement **must not** fall back to legacy P6/P7 world/camera projection, relative Y models, screenshot/template tracking, click calibration, or stale old coordinates.
11. Missing/invalid/stale/SUPPRESSED/mixed-epoch/generation-mismatched canonical data produces no corresponding intent; clear old intent immediately.
12. `clearCanonicalOverlayAuthority(reason)` clears all canonical enemy/player overlay state and cannot leave stale visible labels/warnings.
13. Fixed TEST smoke remains independent and unchanged.
14. P5 canonical P1 top marker remains independent and unchanged.
15. Do not edit Python launcher/CDP files; P10 owns them.
16. Do not edit W3 capture/producer files or W3 claims. Do not move `alpha-live`.

## Compatibility / takeover rule

The maintained HUD may retain legacy functions for historical compatibility, but once canonical overlay authority is bound those legacy spatial placement paths are **not eligible fallback** for enemy-target labels or player-danger warnings. Canonical bound + no valid canonical position = hidden.

## Minimum self-check only

Implementation first. Run only enough to catch obvious breakage:
- JS parse/load;
- one synthetic bound + READY P9 envelope + existing semantic marker/warning fixture produces a P8 plan and reaches existing draw-intent handling;
- one invalid/SUPPRESSED/mixed renderer-epoch envelope clears both canonical channels and reports fallback NONE;
- fixed TEST path remains callable/unmodified.

No broad regression, Fresh QA, real-WOF run, Owner test, package churn, or W3 qualification.

## Terminal

Write exact RESULT.json + RESULT.md declared above. Record implementation commits, changed files, minimum self-checks, integrationReady, blocker, productProof boundary, safety, and nextAction. Do not claim real-WOF PASS.

Final commit begins:
`WORKER_RESULT ALPHA_V1_PRODUCT_TAKEOVER_P11_MAINTAINED_HUD_CANONICAL_OVERLAY_WIRING <STATE>`

Chat only COMPLETE / SUBCOMPLETE / precise BLOCKED.

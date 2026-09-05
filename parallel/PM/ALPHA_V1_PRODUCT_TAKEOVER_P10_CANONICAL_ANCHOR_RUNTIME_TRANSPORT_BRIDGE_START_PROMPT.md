stageId: `ALPHA_V1_PRODUCT_TAKEOVER_P10_CANONICAL_ANCHOR_RUNTIME_TRANSPORT_BRIDGE`
dedupProtocol: `v2`
dedupKey: `alpha.v1.product-takeover.canonical-anchor-runtime-transport-bridge-v1`
dedupMode: `exclusive`
resultProtocol: `wof-alpha-worker-result-v1`
resultJsonPath: `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P10_CANONICAL_ANCHOR_RUNTIME_TRANSPORT_BRIDGE_RESULT.json`
resultMdPath: `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P10_CANONICAL_ANCHOR_RUNTIME_TRANSPORT_BRIDGE_RESULT.md`
terminalCommitPrefix: `WORKER_RESULT ALPHA_V1_PRODUCT_TAKEOVER_P10_CANONICAL_ANCHOR_RUNTIME_TRANSPORT_BRIDGE`
dispatchManifestPath: `parallel/PM/DISPATCH_MANIFESTS/ALPHA_V1_CANONICAL_OVERLAY_RUNTIME_HUD_PARALLEL_2_WORKER_V1.json`

# Alpha V1 Product Takeover P10 — Canonical Anchor Runtime Transport Bridge

Repository: `ouyong520/wof-ai-private`

Read latest `main` first, then:
- `parallel/PM/ALPHA_V1_CANONICAL_OVERLAY_RUNTIME_HUD_PARALLEL_2_WORKER_DISPATCH.md`
- `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P5_P1_CANONICAL_RENDER_ANCHOR_WIRING_RESULT.json`
- `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P9_CANONICAL_ANCHOR_RUNTIME_ENVELOPE_RESULT.json`
- `parallel/PYLAUNCH/wof_launcher/render_object_anchor.py`
- `parallel/PYLAUNCH/wof_launcher/production_p1_overlay.py`
- `parallel/PYLAUNCH/wof_launcher/canonical_p1_production_bridge.py`

Perform dedup-v2 create-only canonical claim + exact-token re-read + create-only stage claim + exact-token re-read before implementation. Fail closed on any ownership error. Do not invent recovery.

## Goal

Implement the runtime/CDP side of the canonical multi-actor overlay chain so a caller with one W3-format render-object frame, exact current authority binding, and explicit current actor generations can deliver canonical READY/SUPPRESSED records to the maintained HUD without any legacy position fallback.

Target chain:

`wof-render-object-frame-v1`
`→ DeterministicRenderObjectAnchor.resolve(actor,generation)`
`→ transport records`
`→ window.WOFALPHAHUD.ingestCanonicalAnchorEnvelope(payload)`

This task does **not** qualify the W3 renderer source. Current unproven W3 frames must naturally resolve SUPPRESSED and therefore remain hidden.

## Required implementation

1. Reuse `AuthorityBinding` and `DeterministicRenderObjectAnchor`; do not duplicate renderer-source proof rules.
2. Add a narrow runtime bridge, preferably `parallel/PYLAUNCH/wof_launcher/canonical_overlay_runtime_bridge.py`.
3. The bridge must bind only an explicit valid current authority binding and page target. No guessing of generations or actors.
4. Accept an explicit actor descriptor list/map from the caller, e.g. P1/P2/P3 and `enemy-slot-N`, each with `kind`, `actor`, `generation`. Do not infer identity by nearest object, coordinates, order, or screenshot.
5. For every requested actor/generation call the canonical resolver. Wrap READY or SUPPRESSED output as a P9-compatible record with explicit `sampleAt` and binding identity. A SUPPRESSED result must never acquire coordinates from any other source.
6. Send only the transport wrapper defined by the shared dispatch to the maintained HUD API. Browser/P9 remains the normalization authority for the envelope contract.
7. Expose explicit revoke/clear behavior that calls `clearCanonicalOverlayAuthority(reason)` and revokes local resolver binding.
8. Authority/runtime/renderer changes must clear previous overlay state before rebinding.
9. Update the maintained HUD source-injection order only as narrowly needed so these modules are loaded before `wof_alpha_hud.js`:
   - P6 enemy planner
   - P7 player planner
   - P9 `wof_alpha_canonical_anchor_envelope.js`
   - P8 `wof_alpha_canonical_overlay_plan.js`
   - maintained HUD
10. Preserve the existing fixed TEST path and P5 canonical P1 bridge. Do not change their semantics.
11. Do not edit `product/alpha/wof_alpha_hud.js`; P11 owns it.
12. Do not edit W3 capture/producer code or W3 claims. Do not move `alpha-live`.

## Fail-closed rules

No screenshot/template, world/camera/Y-model, click/calibration, nearest-sprite, guessed constant, stale previous point, or implicit actor generation may become position authority.

If the canonical resolver returns SUPPRESSED, transport exactly that suppression. If CDP/HUD API is missing or binding is stale, clear and report suppressed/error state; do not silently keep an old visible frame.

## Minimum self-check only

Implementation first. Run only enough to catch obvious breakage:
- Python parse/compile;
- one fake-CDP READY fixture showing exact actor/generation canonical coordinates are sent in the declared payload;
- one unproven/SUPPRESSED or renderer-epoch mismatch fixture showing no coordinates survive and clear/revoke is invoked;
- source injection order contains P9/P8 before maintained HUD.

No broad regression, Fresh QA, real-WOF run, Owner test, package work, or W3 qualification.

## Terminal

Write exact RESULT.json + RESULT.md declared above. Record implementation commits, changed files, minimum self-checks, integrationReady, blocker, productProof boundary, safety, and nextAction. Do not claim real-WOF PASS.

Final commit begins:
`WORKER_RESULT ALPHA_V1_PRODUCT_TAKEOVER_P10_CANONICAL_ANCHOR_RUNTIME_TRANSPORT_BRIDGE <STATE>`

Chat only COMPLETE / SUBCOMPLETE / precise BLOCKED.

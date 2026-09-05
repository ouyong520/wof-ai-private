stageId: `ALPHA_V1_PRODUCT_TAKEOVER_P5_P1_CANONICAL_RENDER_ANCHOR_WIRING`
dedupProtocol: `v2`
dedupKey: `alpha.v1.product-takeover.p1-canonical-render-anchor-wiring-v1`
dedupMode: `exclusive`
resultProtocol: `wof-alpha-worker-result-v1`
resultJsonPath: `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P5_P1_CANONICAL_RENDER_ANCHOR_WIRING_RESULT.json`
resultMdPath: `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P5_P1_CANONICAL_RENDER_ANCHOR_WIRING_RESULT.md`
terminalCommitPrefix: `WORKER_RESULT ALPHA_V1_PRODUCT_TAKEOVER_P5_P1_CANONICAL_RENDER_ANCHOR_WIRING`
dispatchManifestPath: `parallel/PM/DISPATCH_MANIFESTS/ALPHA_V1_CANONICAL_RENDER_ANCHOR_PARALLEL_3_WORKER_V1.json`

# Alpha V1 Product Takeover P5 — P1 Canonical Render-Anchor Wiring

Repository: `ouyong520/wof-ai-private`

Read latest main first, then:
- `parallel/PM/ALPHA_V1_CANONICAL_RENDER_ANCHOR_PARALLEL_3_WORKER_V1_DISPATCH.md`
- `parallel/PM/ALPHA_V1_PRODUCT_TAKEOVER_W3_RENDER_OBJECT_AUTHORITY_CONTINUATION_SUBRESULT.md`
- `parallel/PYLAUNCH/wof_launcher/render_object_anchor.py`
- maintained production HUD/runtime path needed for the smallest integration.

Perform dedup-v2 create-only canonical + exact-token re-read + create-only stage + exact-token re-read before implementation. Any ownership failure is fail-closed. Do not invent recovery.

## Goal

Wire the already-defined fail-closed canonical render-object anchor contract into the maintained production P1 top-of-head product path, without changing or pretending to prove W3 renderer source authority.

The product should be structurally ready for:

`proven wof-render-object-frame-v1 -> DeterministicRenderObjectAnchor READY P1 -> maintained WebGL HUD P1 marker`

while current unproven source continues to produce no product marker.

## Required implementation

1. Reuse `DeterministicRenderObjectAnchor` / `AuthorityBinding`; do not duplicate the proof rules.
2. Add the narrowest runtime/production bridge needed to consume a canonical P1 anchor and pass exact native 384x224 coordinates to the maintained WebGL HUD.
3. If the canonical consumer returns `SUPPRESSED`, authority is revoked, epoch changes, generation changes, or input becomes stale/invalid, hide/revoke the P1 marker immediately.
4. No fallback to screenshot-template tracking, white acquisition marker, world/camera projection, Y/Y-Z/Y+Z model, nearest-sprite, click calibration, or guessed constants.
5. Preserve fixed-draw first-gate behavior from P1/P4 and normal-mode behavior when canonical anchor input is unavailable.
6. Do not alter enemy target labels or player danger modules owned by P6/P7.
7. Do not edit W3 capture/producer files or W3 claims.
8. Do not move `alpha-live` and do not ask Owner to test.

Preferred implementation shape: one new narrow production bridge/adapter under `parallel/PYLAUNCH/wof_launcher/` and the smallest maintained HUD API change required to set/clear a canonical P1 native anchor. Reuse existing production draw hook rather than adding a second overlay.

## Minimum self-check only

Implementation first. Run only enough to catch obvious breakage:
- Python/JS parse/compile as applicable;
- one READY canonical P1 fixture reaches the maintained HUD adapter with exact coordinates;
- one SUPPRESSED/stale fixture clears/hides it;
- fixed-draw branch remains unaffected.

No broad regression, Fresh QA, second opinion, Owner test, or W3 source qualification in this stage.

## Terminal

Write exact RESULT.json + RESULT.md declared above. State implementation commits, changed files, minimal self-checks, integrationReady, blocker, productProof boundary, and nextAction. Do not claim real-WOF PASS. Final commit begins:

`WORKER_RESULT ALPHA_V1_PRODUCT_TAKEOVER_P5_P1_CANONICAL_RENDER_ANCHOR_WIRING <STATE>`

Chat only COMPLETE / SUBCOMPLETE / precise BLOCKED.
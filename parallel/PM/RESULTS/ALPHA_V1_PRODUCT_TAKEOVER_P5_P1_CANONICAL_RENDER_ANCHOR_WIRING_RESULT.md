# Alpha V1 Product Takeover P5 — P1 Canonical Render-Anchor Wiring RESULT

Status: **COMPLETE / integration-ready**

Existing ACTIVE ownership was continued exactly; no new claim and no recovery were created.

- stage: `ALPHA_V1_PRODUCT_TAKEOVER_P5_P1_CANONICAL_RENDER_ANCHOR_WIRING`
- dedup key: `alpha.v1.product-takeover.p1-canonical-render-anchor-wiring-v1`
- claim token: `f4a00ab4765152053e7fc0309b9f9240`
- RESULT JSON: `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P5_P1_CANONICAL_RENDER_ANCHOR_WIRING_RESULT.json`

## Implementation

Implementation commits:

- `b4c9daf4ccf7ca1d0662db5dd0bd04e48d6aba31` — add `CanonicalP1ProductionBridge`.
- `6963da58227c8d6c6ebf93f53a263b60f2251225` — add focused bridge self-check.

Changed implementation/test files:

- `parallel/PYLAUNCH/wof_launcher/canonical_p1_production_bridge.py`
- `parallel/RENDER_AUTHORITY_V2/canonical_p1_production_bridge_selftest.py`

The bridge reuses `AuthorityBinding`, `DeterministicRenderObjectAnchor`, and the existing maintained `ProductionP1Overlay` / WebGL HUD draw path. It does not create a second overlay or a new position-authority path.

Canonical READY P1 coordinates remain native `384x224` coordinates through the canonical boundary and are supplied to the existing production overlay adapter with native frame size `(384,224)`; the existing adapter performs only current-canvas display scaling.

Fail-closed behavior:

- canonical `SUPPRESSED` clears the P1 marker;
- `rendererSource.proven != true` clears/hides;
- authority/runtime/renderer epoch mismatch clears/hides;
- actor generation change clears immediately before accepting the new generation;
- invalid drawing-surface layout clears/hides;
- explicit authority revoke clears/hides;
- no screenshot/template tracking fallback;
- no world/camera projection fallback;
- no Y / Y-Z / Y+Z model;
- no click calibration;
- no nearest-sprite fallback;
- no guessed-coordinate constants.

Fixed-draw first-gate code was not modified. Enemy target-label and player-danger modules were not modified. W3 producer/capture/claim files were not modified.

## Minimum self-check

- Python syntax parse of the exact submitted bridge source — **PASS**.
- Focused isolated bridge fixture using the exact submitted bridge source and a fake maintained-HUD backend — **PASS**:
  - canonical READY forwarded exact native center `[108.0, 86.0]` with frame size `384x224`;
  - unproven renderer source suppressed and cleared visibility;
  - stale renderer epoch suppressed and cleared visibility;
  - actor generation change cleared visibility immediately;
  - fixed-draw sentinel state remained unchanged.
- The committed self-check encodes the same READY/SUPPRESSED/stale/generation/fixed-draw cases against the repository `DeterministicRenderObjectAnchor` module.

No broad regression, Fresh QA, Owner test, real-WOF run, W3 source qualification, or `alpha-live` promotion was performed.

## Product-proof boundary

Product-side wiring is complete and integration-ready:

`proven wof-render-object-frame-v1 -> DeterministicRenderObjectAnchor READY P1 -> CanonicalP1ProductionBridge -> maintained ProductionP1Overlay/WebGL HUD`

W3 still has not proven the exact displayed-frame renderer/object source. Therefore current unproven W3 input correctly remains `SUPPRESSED` and produces no P1 product marker. This RESULT does **not** claim real-WOF or Owner-visible PASS.

## Blocker / next action

Blocker for P5 implementation: **none**.

Remaining external proof dependency: W3 must qualify a real `rendererSource.proven=true` frame under exact World/runtime/renderer authority. When that exists, PM can feed it into this bridge. Until then, the correct behavior is hidden; legacy projection/screenshot fallback remains forbidden.

Safety: `readOnly=true`, `ramWrites=0`, `inputInjection=false`.

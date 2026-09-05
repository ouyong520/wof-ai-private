# Alpha V1 Product Takeover P10 — Canonical Anchor Runtime Transport Bridge RESULT

Status: **COMPLETE / integration-ready**

- stage: `ALPHA_V1_PRODUCT_TAKEOVER_P10_CANONICAL_ANCHOR_RUNTIME_TRANSPORT_BRIDGE`
- dedup key: `alpha.v1.product-takeover.canonical-anchor-runtime-transport-bridge-v1`
- claim token: `bcb33a85097d7fdc64c0ef40481d272e6061c95701f1b94a`
- implementation commit: `7e408a2f5efd8fe6c62a7adc12e3827793d16c83`
- RESULT JSON commit: `b11d005798c513d17ed947113a67afef298b1bfa`

The existing P10 canonical and stage claims were continued under the original exact claim token. No new claim or recovery was created.

## Implementation

P10 adds `parallel/PYLAUNCH/wof_launcher/canonical_overlay_runtime_bridge.py`, a narrow runtime/CDP bridge for the canonical multi-actor overlay path.

The implemented chain is:

`wof-render-object-frame-v1`
`-> explicit actor/generation descriptors`
`-> DeterministicRenderObjectAnchor.resolve(actor, generation)`
`-> P9-compatible READY/SUPPRESSED transport records`
`-> window.WOFALPHAHUD.ingestCanonicalAnchorEnvelope(payload)`

The bridge binds only an explicit valid `AuthorityBinding` and explicit page target. It does not infer actor identity or generation from coordinates, row order, nearest objects, previous state, screenshots, projection, or any other spatial heuristic.

Each caller-provided descriptor must contain explicit `kind`, `actor`, and non-negative integer `generation`. Each ingest also requires an explicit finite `sampleAt`; the bridge does not manufacture a fresh sample time that could make stale producer data appear current.

For every descriptor the bridge calls the existing `DeterministicRenderObjectAnchor`. The resulting canonical object is transported unchanged as the record's `canonicalAnchor`, together with explicit sample time and exact World/authority/runtime/renderer identity. A canonical `SUPPRESSED` result is transported without coordinates.

The transport wrapper is exactly `wof-alpha-canonical-anchor-runtime-envelope-input-v1`. P10 does not reproduce P9/P8 browser normalization or planning rules.

## Maintained HUD / CDP lifecycle

The bridge uses the P11 canonical HUD API:

- `bindCanonicalOverlayAuthority(binding)`
- `ingestCanonicalAnchorEnvelope(payload)`
- `clearCanonicalOverlayAuthority(reason)`

Binding validates the exact maintained-HUD canonical status, including matching authority identity, `fallback=NONE`, and the read-only safety boundary. Rebind first clears/revokes prior local and HUD state.

When the canonical browser stack is not already present, the bridge derives the existing maintained HUD source list and inserts the canonical modules in this required order before the HUD:

`P6 enemy planner -> P7 player planner -> P9 canonical envelope -> P8 unified plan -> maintained HUD`

Other existing maintained-HUD source entries are preserved. The fixed TEST path and P5 canonical P1 bridge semantics are not changed.

Explicit revoke calls `clearCanonicalOverlayAuthority(reason)`, revokes the local deterministic resolver binding, closes the CDP session, and discards the retained payload.

## Fail-closed behavior

No screenshot/template, world/camera projection, Y/Y-Z/Y+Z model, click/calibration, nearest-sprite selection, guessed constant, stale previous point, or implicit actor generation can become position authority.

If the deterministic resolver returns `SUPPRESSED`, P10 sends that suppression without an anchor. If a suppressed resolver object were ever to carry coordinates, P10 revokes rather than forwarding it. Invalid descriptor/sample input, missing/malformed HUD canonical API, stale binding, or CDP/HUD ingest failure clears/revokes the canonical bridge instead of retaining an old visible frame.

The only position authority reported by P10 is `wof-render-object-anchor-v1`, and `legacyPositionFallback=false`.

## Minimum self-check

- Python parse/compile of the P10 bridge and focused fixture — **PASS**.
- Fake-CDP READY fixture — **PASS**: P1 generation 7 resolved to native `(108,86)` and `enemy-slot-4` generation 3 to `(192,76)`; the declared wrapper carried those exact canonical coordinates, explicit `sampleAt`, and exact binding identity.
- Renderer-epoch mismatch fixture — **PASS**: the resolver returned `STALE_AUTHORITY_OR_RENDERER_EPOCH`; the sent record was `SUPPRESSED` and contained no anchor coordinates.
- Explicit revoke/clear seam — **PASS**: `clearCanonicalOverlayAuthority` was invoked and the local resolver/session were revoked.
- Canonical source order check — **PASS**: P9 and P8 precede the maintained HUD after P6/P7.
- Real-WOF / Owner visual acceptance / W3 qualification — **NOT RUN**, by task boundary.

No broad regression, Fresh QA, package promotion, real-WOF run, Owner test, W3 qualification, or `alpha-live` movement was performed.

## Product-proof boundary

P10 is implementation-proven and integration-ready for the runtime/CDP transport seam only.

This RESULT does not claim that W3 has qualified an exact displayed-frame renderer/object source, does not claim a real-WOF canonical draw, and does not claim Owner-visible PASS. Until W3 source qualification is separately proven, the correct canonical behavior remains `SUPPRESSED` with no legacy spatial fallback.

P12 remains the separate actor/generation descriptor authority. P11/P13 already provide the canonical maintained-HUD/browser bootstrap seam that P10 calls.

## Blocker / next action

P10 implementation blocker: **none**.

Next action: PM should integrate P10 with P12 descriptor production and the already-complete P11/P13 canonical HUD/bootstrap path, while keeping W3-unproven records suppressed until W3 renderer/object source qualification exists.

Safety: `readOnly=true`, `ramWrites=0`, `inputInjection=false`.

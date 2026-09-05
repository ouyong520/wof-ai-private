# Alpha V1 P9 — Canonical Anchor Runtime Envelope RESULT

State: **COMPLETE**

Stage: `ALPHA_V1_PRODUCT_TAKEOVER_P9_CANONICAL_ANCHOR_RUNTIME_ENVELOPE`

Dedup key: `alpha.v1.product-takeover.canonical-anchor-runtime-envelope-v1`

Claim token: `51d37e82c89f2ceb7325ec4e10a8d9d3402e44c27fe4e514`

Start commit: `d462dbae63946aeca992c2d49d60e90b5f924a17`

## Verdict

P9 now provides one strict product-side canonical anchor envelope for player/enemy records derived only from `wof-render-object-anchor-v1`. A normalized record exposes `renderAnchor` only when the canonical source is `READY`; an explicit `SUPPRESSED` source always normalizes to `renderAnchor: null` and keeps its suppression reason.

## Implementation

Implementation commits:

- `3c3abc59c0afb70cd5fa9a7ed58ec12165ebe5f7` — add `product/alpha/wof_alpha_canonical_anchor_envelope.js`
- `9ab1528bf699cce9fd194b17654ae97ae68f66c2` — add focused self-check `product/alpha/canonical_anchor_envelope_selfcheck.mjs`

Changed files:

- `product/alpha/wof_alpha_canonical_anchor_envelope.js`
- `product/alpha/canonical_anchor_envelope_selfcheck.mjs`

## Runtime envelope contract

The envelope version is `wof-alpha-canonical-anchor-envelope-v1` and accepts only the existing `wof-render-object-anchor-v1` source schema under native `384x224` coordinates.

For each accepted player/enemy record it preserves and validates:

- deterministic actor identity and current generation metadata;
- `READY` or explicit `SUPPRESSED` canonical state;
- `authorityKey`, `runtimeEpoch`, `rendererEpoch`;
- exact World SHA identity when supplied by the binding/source;
- sample freshness metadata;
- safety invariants `readOnly=true`, `ramWrites=0`, `inputInjection=false`.

`READY` requires a finite canonical source point and the source record's own actor/generation/authority/epoch binding. `SUPPRESSED` requires an explicit reason and is forbidden from carrying a usable fallback position.

The helper adapters `toPlayerAnchorSamples()` and `toEnemyAnchorArray()` expose the already-normalized canonical source records in the shapes P7/P6 can consume; they do not calculate, project, fit or guess coordinates.

## Fail-closed behavior

The envelope rejects unsupported source/native schema, invalid identity/generation, stale or future samples, duplicate actor+generation records, mixed authority/epoch bindings, mixed World identity, unsafe source flags, malformed READY/SUPPRESSED states, and SUPPRESSED records that attempt to carry fallback coordinates.

Legacy projection-like data is not used as product truth. The focused valid fixture deliberately includes poison `legacyProjection` coordinates and verifies that the canonical READY point remains unchanged.

## Minimum self-check

PASS — `node --check product/alpha/wof_alpha_canonical_anchor_envelope.js`

PASS — `node product/alpha/canonical_anchor_envelope_selfcheck.mjs`

The local checked module blob `32197b5ed8c2069b23e5e883e396db5a472904e5` and self-check blob `75b9d84049a690da9e2f675cffeac641243b7e87` exactly match the committed `main` blobs. The fixture covers a valid same-epoch READY+SUPPRESSED envelope plus fail-closed mixed renderer epoch, duplicate actor+generation, unsafe source and SUPPRESSED fallback-position cases.

No broad regression, Fresh QA, Owner acceptance, real-WOF run or W3 qualification was performed, per P9 authority.

## Product-proof boundary

This is **implementation proof only**. P9 does not change or qualify W3 `rendererSource.proven`, does not draw anything, and does not claim machine-draw or Owner-visible real-WOF PASS. If W3 remains unproven, upstream canonical anchors remain `SUPPRESSED` and the envelope preserves that suppression instead of promoting or reconstructing a position.

## Integration readiness

`integrationReady: true`

Blocker: none for the P9 implementation boundary.

Next action: product composition may consume this envelope once runtime supplies W3-qualified canonical samples plus the exact current authority binding. Any missing, stale, unsafe, mixed-epoch or SUPPRESSED input must remain hidden; no old projection/screenshot/geometry fallback is permitted.

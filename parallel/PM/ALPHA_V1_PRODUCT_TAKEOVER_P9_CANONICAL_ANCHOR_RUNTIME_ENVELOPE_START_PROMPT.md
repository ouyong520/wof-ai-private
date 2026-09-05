stageId: `ALPHA_V1_PRODUCT_TAKEOVER_P9_CANONICAL_ANCHOR_RUNTIME_ENVELOPE`
dedupProtocol: `v2`
dedupKey: `alpha.v1.product-takeover.canonical-anchor-runtime-envelope-v1`
dedupMode: `exclusive`
resultProtocol: `wof-alpha-worker-result-v1`
resultJsonPath: `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P9_CANONICAL_ANCHOR_RUNTIME_ENVELOPE_RESULT.json`
resultMdPath: `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P9_CANONICAL_ANCHOR_RUNTIME_ENVELOPE_RESULT.md`
terminalCommitPrefix: `WORKER_RESULT ALPHA_V1_PRODUCT_TAKEOVER_P9_CANONICAL_ANCHOR_RUNTIME_ENVELOPE`
dispatchManifestPath: `parallel/PM/DISPATCH_MANIFESTS/ALPHA_V1_CANONICAL_RENDER_ANCHOR_P5_P8_P9_CONTINUATION_3_WORKER_V1.json`

# Alpha V1 Product Takeover P9 — Canonical Anchor Runtime Envelope

Repository: `ouyong520/wof-ai-private`

Read latest main first, then:
- `parallel/PM/ALPHA_V1_CANONICAL_RENDER_ANCHOR_P5_P8_P9_CONTINUATION_3_WORKER_DISPATCH.md`
- `parallel/PYLAUNCH/wof_launcher/render_object_anchor.py`
- `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P6_ENEMY_CANONICAL_RENDER_ANCHOR_LABELS_RESULT.json`
- `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P7_PLAYER_DANGER_CANONICAL_ANCHOR_RESULT.json`
- `parallel/PM/ALPHA_WORKER_RESULT_FAST_FEEDBACK_PROTOCOL_V1.md`

Perform dedup-v2 exactly: latest-main preflight -> create-only canonical claim -> re-read exact claimToken/fields/state ACTIVE -> create-only stage claim -> re-read exact same token/fields/state ACTIVE. Any failure is fail-closed. Do not invent recovery.

## Goal

Implement a strict product-side runtime envelope/validator for already-resolved canonical render-object anchors. The envelope gives browser/product consumers one deterministic contract for player/enemy anchor records, actor generation, exact World identity, authority key, runtime epoch and renderer epoch, without changing W3 source qualification and without drawing anything.

Preferred new files only:
- `product/alpha/wof_alpha_canonical_anchor_envelope.js`
- optional `product/alpha/canonical_anchor_envelope_selfcheck.mjs`

Do not modify P5-owned launcher/HUD/runtime bridge files while P5 is ACTIVE. Do not modify P6/P7 implementation modules. Do not edit W3 capture/producer/claim files. Do not move `alpha-live`.

## Required contract

Define one versioned envelope, e.g. `wof-alpha-canonical-anchor-envelope-v1`, that can carry a bounded set of player and enemy anchor records derived from `wof-render-object-anchor-v1` outputs.

Each accepted record must preserve/validate at least:
- actor identity (`P1`/`P2`/`P3` or deterministic enemy actor/slot identity);
- current generation;
- canonical anchor state `READY` or explicit `SUPPRESSED`;
- canonical native coordinate contract exactly `384x224`;
- `authorityKey`;
- `runtimeEpoch`;
- `rendererEpoch`;
- exact World safety identity when present/required by the upstream contract;
- safety metadata `readOnly=true`, `ramWrites=0`, `inputInjection=false`;
- sample timestamp / freshness metadata sufficient for downstream stale suppression.

The module must expose deterministic validation/normalization APIs suitable for P6/P7/P8 consumption. It must not infer coordinates from world state or screenshots.

Fail closed on:
- unsupported schema/native dimensions;
- missing/invalid actor or generation;
- duplicate actor+generation records where uniqueness is required;
- mixed authorityKey/runtimeEpoch/rendererEpoch inside one envelope unless explicitly represented as separate rejected/suppressed records;
- READY record without finite canonical anchor coordinates;
- SUPPRESSED record that is malformed or tries to carry a usable fallback position;
- unsafe safety flags;
- stale/future-invalid sample timing;
- unrecognized source state.

The normalized result should make it easy for later product composition to select only READY records under one exact authority binding while retaining explicit suppression reasons for diagnostics.

## Forbidden behavior

No draw hook, HUD change, DOM overlay, second renderer, screenshot/template fallback, world/camera projection, Y/Y-Z/Y+Z fitting, click calibration, nearest-sprite selection, relative geometry, or guessed constants.

P9 does not prove W3 source authority and must not change `rendererSource.proven` or reinterpret `SUPPRESSED` as READY.

## Minimum self-check only

Implementation first. Run only:
- JS parse/load;
- one valid same-epoch READY+SUPPRESSED envelope normalization fixture;
- one invalid mixed-epoch/duplicate/unsafe fixture that fails closed.

No broad regression, Fresh QA, Owner acceptance, real-WOF run, or W3 qualification.

## Terminal

Write exact RESULT.json + RESULT.md declared above. Include implementation commits, changed files, minimal self-checks, integrationReady, productProof boundary, blocker and nextAction. Do not claim real-WOF or Owner visual PASS. Final commit begins:

`WORKER_RESULT ALPHA_V1_PRODUCT_TAKEOVER_P9_CANONICAL_ANCHOR_RUNTIME_ENVELOPE <STATE>`

Chat only COMPLETE / SUBCOMPLETE / precise BLOCKED.

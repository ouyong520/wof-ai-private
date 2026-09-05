# Alpha V1 Product Takeover P12 — Canonical Actor Generation Registry RESULT

Status: **COMPLETE / integration-ready**

- stage: `ALPHA_V1_PRODUCT_TAKEOVER_P12_CANONICAL_ACTOR_GENERATION_REGISTRY`
- dedup key: `alpha.v1.product-takeover.canonical-actor-generation-registry-v1`
- claim token: `e31a17b35e9175681f7c7f26ff5af381`
- RESULT JSON: `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P12_CANONICAL_ACTOR_GENERATION_REGISTRY_RESULT.json`

The existing dedup-v2 canonical claim and stage claim were continued under the original exact token. No new claim or recovery was created. Both original claims are now closed `COMPLETE`.

## Implementation

Implementation commit:

- `864fda69a3b777f05119bc7ae1ea4cc3a2a039c8` — canonical actor/generation registry.

Changed implementation file only:

- `parallel/PYLAUNCH/wof_launcher/canonical_actor_generation_registry.py`

The module provides `resolve(frame, binding, requestedActors=None)` plus a narrow `CanonicalActorGenerationRegistry.resolve(...)` facade.

It accepts only `wof-render-object-frame-v1`, requires the exact supplied `AuthorityBinding` identity (`worldSha256`, `authorityKey`, `runtimeEpoch`, `rendererEpoch`) and the native `384x224` contract, and supports only `P1`/`P2`/`P3` plus `enemy-slot-0..19`.

A descriptor is exported only when the current frame row has:

- an explicit supported `actor`;
- an integer non-boolean `generation >= 0`;
- `association.proven == true`;
- `association.ambiguous != true`;
- integer `association.candidateCount == 1`;
- no unsafe row flag.

READY descriptors contain exactly:

`{kind, actor, generation}`

No `parts`, `bodyBounds`, anchor, x/y, projection, screenshot, camera/world coordinate, nearest-object hint, render-order hint, or cached prior identity is exported or consulted.

Descriptor ordering is canonical by actor name set (`P1`, `P2`, `P3`, then enemy slots), not W3 row order. Duplicate rows or conflicting generations fail closed rather than selecting one by order.

`requestedActors` only filters exact supported actor names. It never chooses or rewrites a generation.

The registry is stateless. A failed resolve always returns `descriptors: []`; it has no previous-frame cache to fall back to.

P12 deliberately does not require `rendererSource.proven == true` for identity authority. A safe explicit actor association can remain a READY identity descriptor while P10/`DeterministicRenderObjectAnchor` independently suppresses spatial resolution as `RENDERER_SOURCE_UNPROVEN`.

## Minimum self-check

- Exact committed Python compile — **PASS**. Local Git blob `53110e04bb9048bde326615a21c9ea9af25e54d5` exactly matches the GitHub content SHA for implementation commit `864fda69a3b777f05119bc7ae1ea4cc3a2a039c8`.
- Exact-binding P1 + enemy fixture — **PASS**. P1 generation 7 and enemy-slot-3 generation 12 resolved deterministically to descriptor-only output; reversing W3 row order produced the same descriptor sequence; spatial fields in actor rows were not exported.
- Renderer-source separation fixture — **PASS**. `rendererSource.proven=false` did not upgrade coordinates and did not erase otherwise explicit safe identity authority.
- Fail-closed fixture — **PASS**. Conflicting generations -> `CONFLICTING_ACTOR_GENERATIONS`; ambiguous association -> `ACTOR_ASSOCIATION_UNPROVEN`; stale renderer epoch -> `STALE_AUTHORITY_OR_RENDERER_EPOCH`; boolean generation -> `ACTOR_GENERATION_INVALID`; all returned no usable descriptor set.
- Real-WOF / Owner acceptance / W3 source qualification — **NOT_RUN**, outside P12 authority.

No broad regression, Fresh QA, P10 bridge edit, W3 producer/capture edit, field-adapter/HUD edit, package change, or `alpha-live` movement was performed.

## Integration boundary

P12 is identity/generation authority only.

- P12: current-frame proven `{kind, actor, generation}` descriptors.
- P10 / `DeterministicRenderObjectAnchor`: position authority and canonical anchor transport.
- W3: renderer/object source proof authority.

The latest P10 bridge already accepts explicit actor descriptors. The next runtime integration step is to resolve each current W3 frame through P12 and pass only a READY registry descriptor set into P10 instead of constructing actor generations ad hoc.

P12 does not modify P10 or W3 ownership and does not claim that caller wiring has already been performed by this task.

## Product-proof boundary

P12 provides implementation proof only for exact-binding identity/generation registry behavior and its fail-closed/non-spatial contract.

It does **not** prove W3 renderer-source qualification, P10 spatial READY output, maintained-HUD draw in real WOF, or Owner-visible persistence.

## Blocker / next action

P12 implementation blocker: **none**.

Next action: runtime/P10 caller consumes P12 READY descriptors from the same current W3 frame and stops constructing actor generations ad hoc; P10 remains the only spatial resolver and W3 remains the only renderer-source proof authority.

Safety: `readOnly=true`, `ramWrites=0`, `inputInjection=false`.

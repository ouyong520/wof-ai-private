stageId: `ALPHA_V1_PRODUCT_TAKEOVER_P12_CANONICAL_ACTOR_GENERATION_REGISTRY`
dedupProtocol: `v2`
dedupKey: `alpha.v1.product-takeover.canonical-actor-generation-registry-v1`
dedupMode: `exclusive`
resultProtocol: `wof-alpha-worker-result-v1`
resultJsonPath: `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P12_CANONICAL_ACTOR_GENERATION_REGISTRY_RESULT.json`
resultMdPath: `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P12_CANONICAL_ACTOR_GENERATION_REGISTRY_RESULT.md`
terminalCommitPrefix: `WORKER_RESULT ALPHA_V1_PRODUCT_TAKEOVER_P12_CANONICAL_ACTOR_GENERATION_REGISTRY`
dispatchManifestPath: `parallel/PM/DISPATCH_MANIFESTS/ALPHA_V1_CANONICAL_RUNTIME_P10_P12_P13_CONTINUATION_3_WORKER_V1.json`

# Alpha V1 Product Takeover P12 — Canonical Actor Generation Registry

Repository: `ouyong520/wof-ai-private`

Read latest `main` first, then:
- `parallel/PM/ALPHA_V1_CANONICAL_RUNTIME_P10_P12_P13_CONTINUATION_3_WORKER_DISPATCH.md`
- `parallel/PM/ALPHA_V1_PRODUCT_TAKEOVER_P10_CANONICAL_ANCHOR_RUNTIME_TRANSPORT_BRIDGE_START_PROMPT.md`
- `parallel/PYLAUNCH/wof_launcher/render_object_anchor.py`
- `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P9_CANONICAL_ANCHOR_RUNTIME_ENVELOPE_RESULT.json`
- existing W3 continuation RESULT/contract only as needed to understand `wof-render-object-frame-v1`; do not modify W3 ownership.

Perform dedup-v2 create-only canonical claim + exact-token re-read + create-only stage claim + exact-token re-read before implementation. Fail closed on ownership failure. Do not invent recovery.

## Goal

Provide the missing explicit actor/generation identity registry for the P10 caller.

P10 deliberately refuses to infer actor identity or generation from coordinates, object order, nearest sprite, screenshot, or stale history. P12 must turn one exact W3-format `wof-render-object-frame-v1` identity snapshot into a deterministic descriptor set such as:

`[{kind:'player', actor:'P1', generation:7}, {kind:'enemy', actor:'enemy-slot-3', generation:12}, ...]`

without exporting or inventing any spatial coordinates.

This registry is **identity/generation authority only**. P10/`DeterministicRenderObjectAnchor` remains position authority and W3 remains renderer-source proof authority.

## Preferred implementation

Add one narrow module:

`parallel/PYLAUNCH/wof_launcher/canonical_actor_generation_registry.py`

Preferred public shape may be a class or pure function, but it must expose a deterministic operation equivalent to:

`resolve(frame, binding, requestedActors=None) -> registry status + descriptors`

## Required behavior

1. Accept only `wof-render-object-frame-v1`.
2. Require exact binding identity against the supplied `AuthorityBinding`:
   - `worldSha256`
   - `authorityKey`
   - `runtimeEpoch`
   - `rendererEpoch`
   - native `384x224` contract.
3. Supported actor names only:
   - `P1`, `P2`, `P3`
   - `enemy-slot-0` through `enemy-slot-19`.
4. Generation must be an integer `>= 0`; booleans are invalid.
5. Require each exported actor row to have an explicit proven actor association:
   - `association.proven == true`
   - `association.ambiguous != true`
   - `association.candidateCount == 1`.
6. Reject/omit unsafe rows rather than treating them as identity authority.
7. An actor may have only one current generation in a frame. Duplicate rows, conflicting generations, or multiple current rows for the same actor must fail closed for that actor or the whole registry; never choose by order.
8. `requestedActors` may filter the exact allowed actor names but must not alter generation selection.
9. The descriptor output must contain **no position authority**. Do not copy `parts`, `bodyBounds`, `anchor`, x/y, projection, screenshot, camera/world coordinates, or nearest-object hints into the registry output.
10. Renderer source `proven=false` does not by itself authorize coordinates and must not be upgraded. P12 may still expose a proven actor/generation identity if the actor association itself is explicit and safe; P10 will then correctly resolve the position as `SUPPRESSED/RENDERER_SOURCE_UNPROVEN`.
11. Preserve exact binding metadata in registry status so P10 can reject stale/mixed epochs.
12. Provide explicit `SUPPRESSED`/reason output for invalid frame/binding/association/duplicate conditions; no silent fallback to prior descriptors.
13. Do not keep stale prior generations after a new frame becomes invalid. A failed resolve returns no usable descriptor set for the affected authority generation.

## Forbidden

Do not:
- edit P10 bridge/transport files;
- edit `alpha_runtime.py`;
- edit P11 HUD/product JS;
- edit W3 capture/producer/claims;
- infer player/enemy identity from coordinates, row index, render order, sprite appearance, target semantics, screenshot/template, click, nearest sprite, or old cached state;
- move `alpha-live`.

## Minimum self-check only

Implementation first. Run only enough to catch obvious breakage:
- Python parse/compile;
- one exact-binding fixture with P1 + one enemy proving deterministic `{actor,generation}` descriptors and no coordinates in output;
- one conflicting-generation/ambiguous/stale-epoch fixture proving fail-closed output.

Do not add a broad test suite. No real-WOF run, Owner test, Fresh QA, or W3 source qualification.

## Terminal

Write the exact RESULT.json + RESULT.md declared above. Record implementation commits, changed files, minimum self-checks, integrationReady, blocker, productProof boundary, safety, and nextAction.

Do not claim real-WOF source proof. Expected next action is that the runtime/P10 caller consumes the registry descriptors instead of constructing actor generations ad hoc.

Final commit begins:
`WORKER_RESULT ALPHA_V1_PRODUCT_TAKEOVER_P12_CANONICAL_ACTOR_GENERATION_REGISTRY <STATE>`

Chat only COMPLETE / SUBCOMPLETE / precise BLOCKED.

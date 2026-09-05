# Alpha V1 Canonical Runtime — P10 / P12 / P14 Continuation 3-Worker Dispatch

Repository: `ouyong520/wof-ai-private`

This dispatch continues the canonical render-anchor product path after P11 and P13 reached COMPLETE. It intentionally keeps the existing ACTIVE P10 and P12 ownership intact and adds exactly one independent downstream-enabling implementation stream, P14.

## Current accepted state

- P5 COMPLETE: canonical P1 production HUD wiring exists and fails closed.
- P6 COMPLETE: enemy target-label canonical planner exists.
- P7 COMPLETE: player danger canonical planner exists.
- P8 COMPLETE: unified canonical overlay product plan exists.
- P9 COMPLETE: canonical anchor runtime envelope exists.
- P11 COMPLETE: maintained production WebGL HUD consumes P9 -> P8 and exposes canonical bind/ingest/clear APIs.
- P13 COMPLETE: package-selected `AlphaRuntimeManager` now loads P9/P8 before P11 and fails closed on missing canonical capability.
- P10 remains ACTIVE under its existing claim and owns runtime/CDP canonical anchor transport.
- P12 remains ACTIVE under its existing claim and owns actor/generation descriptor authority.
- W3 renderer/object source qualification remains separate ownership and is not modified by this dispatch.

## Product problem addressed by P14

The current Worker field adapter still couples enemy marker publication to the legacy enemy projection profile. Its `markerSnapshot(...)` returns no marker payload when `projectionProfile` is absent, even though the target gameplay semantics (`slot`, `target7E`, mapped target player) are readable independently from position.

That coupling is now wrong for the canonical product path. P11 deliberately treats existing gameplay semantics as content authority while P9/P10 canonical anchors are the only spatial authority. Therefore canonical enemy labels must not disappear merely because the old world/camera projection profile is unproved.

P14 must separate **target semantics** from **legacy spatial projection** without reintroducing any old coordinate fallback.

## Worker boundaries

### Slot 1 — P10 continuation

Continue the already ACTIVE P10 exactly under its existing claim/token and original authority. Do not open a new claim or recovery.

Ownership:
- canonical runtime/CDP transport bridge;
- exact AuthorityBinding bind/revoke lifecycle;
- W3-format frame -> `DeterministicRenderObjectAnchor` -> P9-compatible transport records;
- HUD canonical bind/ingest/clear invocation.

Do not edit P14's semantic-only publication behavior unless a direct merge conflict must be resolved after both implementations are terminal.

### Slot 2 — P12 continuation

Continue the already ACTIVE P12 exactly under its existing claim/token and original authority. Do not open a new claim or recovery.

Ownership:
- explicit actor/generation identity descriptors only;
- no position authority;
- no P10 bridge edits;
- no field adapter/HUD edits.

### Slot 3 — P14 canonical semantic/spatial decoupling

New exclusive task. P14 owns the semantic-only target publication seam needed by canonical enemy labels.

Primary files may include:
- `product/alpha/wof_alpha_field_adapter.js`
- `product/alpha/wof_alpha_hud.js`
- one narrow focused self-check file if needed.

P14 must not edit:
- P10's new/runtime bridge implementation files;
- `parallel/PYLAUNCH/wof_launcher/render_object_anchor.py`;
- `parallel/PYLAUNCH/wof_launcher/canonical_actor_generation_registry.py` or P12 result ownership;
- W3 capture/producer/claims;
- package manifest/generator/updater;
- `alpha-live`.

## Cross-worker interface

P14 must preserve this product split:

`field adapter gameplay RAM semantics`
`-> semantic-only target state (no spatial authority)`
`+ P10/P9 canonical anchor envelope (only spatial authority)`
`-> P11 maintained HUD`
`-> P8 unified plan`
`-> existing maintained WebGL label/warning primitives`

Canonical-bound enemy target labels must require both:
- valid current target semantics; and
- valid current canonical enemy anchor.

If either side is missing/stale/invalid, hide. Never borrow legacy coordinates.

## Implementation-first cadence

Follow `parallel/PM/TESTING_CADENCE_POLICY.md`.

Priority is implementation and end-to-end wiring. Only minimum syntax/parse and narrow seam self-checks are expected. Do not create Fresh QA, broad regression, second-opinion, packaging, or Owner test work in this dispatch.

## Safety

All Alpha paths remain:
- `readOnly=true`
- `ramWrites=0`
- `inputInjection=false`

No RAM writes, no input injection, no gameplay automation.

## Terminal reporting

Terminal reporting must follow `parallel/PM/ALPHA_WORKER_RESULT_FAST_FEEDBACK_PROTOCOL_V1.md`.

Workers write only their exact declared `RESULT.json` + `RESULT.md` paths and use the declared `WORKER_RESULT <stageId> <STATE>` terminal prefix.

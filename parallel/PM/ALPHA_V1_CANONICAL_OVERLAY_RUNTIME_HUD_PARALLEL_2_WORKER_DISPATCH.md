# Alpha V1 — Canonical Overlay Runtime → Maintained HUD Parallel 2-Worker Dispatch

Repository: `ouyong520/wof-ai-private`

## Current product state

- P5 P1 canonical production bridge: COMPLETE / integration-ready.
- P6 enemy canonical target-label planner: COMPLETE / integration-ready.
- P7 player danger canonical anchor planner: COMPLETE / integration-ready.
- P8 unified canonical overlay product plan: COMPLETE / integration-ready.
- P9 canonical anchor runtime envelope: COMPLETE / integration-ready.
- W3 exact displayed-frame renderer/object source qualification remains under its existing ACTIVE authority and is still not proven by repository-only evidence.

This dispatch does **not** create, recover, replace, or modify W3 ownership. It advances the product plumbing that can be completed safely before final live qualification.

## Product objective

Finish the missing middle of the real product chain:

`wof-render-object-frame-v1`
`→ DeterministicRenderObjectAnchor READY/SUPPRESSED records`
`→ P9 canonical runtime envelope`
`→ P8 unified canonical overlay draw plan`
`→ maintained production WebGL HUD`

When W3 source remains unproven, the exact same chain must stay fail-closed and draw no canonical enemy/danger position. No legacy geometry may silently reappear.

## Parallel ownership

### P10 — Canonical Anchor Runtime Transport Bridge

Owns Python/runtime/CDP side only.

Preferred writable files:
- new `parallel/PYLAUNCH/wof_launcher/canonical_overlay_runtime_bridge.py`;
- minimal load-order/source-list change in `parallel/PYLAUNCH/wof_launcher/production_p1_overlay.py` so P9 + P8 product modules are injected before `wof_alpha_hud.js`;
- one narrow implementation self-check file if needed.

P10 must not modify:
- `product/alpha/wof_alpha_hud.js`;
- P6/P7/P8/P9 product planners except source loading references;
- W3 capture/producer/claim files;
- `alpha-live`.

### P11 — Maintained HUD Canonical Overlay Wiring

Owns browser product/HUD side only.

Preferred writable files:
- `product/alpha/wof_alpha_hud.js`;
- one narrow product self-check fixture if needed.

P11 must not modify:
- Python launcher/CDP files owned by P10;
- W3 capture/producer/claim files;
- P5 bridge implementation;
- `alpha-live`.

## Fixed P10 ↔ P11 interface contract

The maintained HUD must expose these exact semantic operations (names may only vary if both workers can preserve compatibility without touching each other's files; default names are authoritative):

- `bindCanonicalOverlayAuthority(binding)`
- `ingestCanonicalAnchorEnvelope(payload)`
- `clearCanonicalOverlayAuthority(reason)`

`binding` contains only current canonical authority identity:

```json
{
  "authorityKey": "...",
  "runtimeEpoch": "...",
  "rendererEpoch": "...",
  "worldSha256": "... optional exact World identity ..."
}
```

`payload` is a transport wrapper, not a second position authority:

```json
{
  "schema": "wof-alpha-canonical-anchor-runtime-envelope-input-v1",
  "authorityBinding": {"authorityKey":"...","runtimeEpoch":"...","rendererEpoch":"..."},
  "records": [
    {
      "kind": "player|enemy",
      "actor": "P1|P2|P3|enemy-slot-N",
      "generation": 0,
      "sampleAt": 0,
      "canonicalAnchor": {"schema":"wof-render-object-anchor-v1","state":"READY|SUPPRESSED", "...":"..."}
    }
  ]
}
```

The browser side must run P9 `normalizeEnvelope(...)` and then P8 `buildCanonicalPlan(...)`. P10 must not reproduce P9/P8 validation logic in Python beyond transport/binding sanity required to fail closed.

## Required fail-closed behavior

Canonical mode must never use:
- screenshot/template tracking;
- world/camera projection;
- Y / Y-Z / Y+Z models;
- click/calibration;
- nearest-sprite matching;
- guessed constants;
- stale prior canonical position.

Any missing, invalid, stale, SUPPRESSED, unsafe, ambiguous, generation-mismatched, authority-mismatched, runtime-epoch-mismatched, or renderer-epoch-mismatched canonical record produces no corresponding draw intent.

When canonical overlay authority is bound, legacy enemy/player spatial placement paths are not a fallback for those channels. Fixed TEST smoke remains independent and unchanged. P5 canonical P1 top marker remains independent and unchanged.

## Cadence

Implementation first. Only minimum parse/compile plus one READY and one SUPPRESSED/invalid seam fixture per worker. No broad regression, Fresh QA, second-opinion audit, real-WOF run, Owner acceptance, or package churn in this dispatch.

## Safety

Always preserve:
- `readOnly=true`
- `ramWrites=0`
- `inputInjection=false`
- exact World/runtime/renderer binding semantics

## Reporting

Each worker writes the exact RESULT.json + RESULT.md paths from its start prompt / immutable manifest. Terminal reporting follows `parallel/PM/ALPHA_WORKER_RESULT_FAST_FEEDBACK_PROTOCOL_V1.md`.

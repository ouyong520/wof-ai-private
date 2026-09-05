stageId: `ALPHA_V1_PRODUCT_TAKEOVER_P14_CANONICAL_SEMANTIC_SPATIAL_DECOUPLING`
dedupProtocol: `v2`
dedupKey: `alpha.v1.product-takeover.canonical-semantic-spatial-decoupling-v1`
dedupMode: `exclusive`
resultProtocol: `wof-alpha-worker-result-v1`
resultJsonPath: `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P14_CANONICAL_SEMANTIC_SPATIAL_DECOUPLING_RESULT.json`
resultMdPath: `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P14_CANONICAL_SEMANTIC_SPATIAL_DECOUPLING_RESULT.md`
terminalCommitPrefix: `WORKER_RESULT ALPHA_V1_PRODUCT_TAKEOVER_P14_CANONICAL_SEMANTIC_SPATIAL_DECOUPLING`
dispatchManifestPath: `parallel/PM/DISPATCH_MANIFESTS/ALPHA_V1_CANONICAL_RUNTIME_P10_P12_P14_CONTINUATION_3_WORKER_V1.json`

# Alpha V1 Product Takeover P14 — Canonical Semantic / Spatial Decoupling

Repository: `ouyong520/wof-ai-private`

Read latest `main` first, then:
- `parallel/PM/ALPHA_V1_CANONICAL_RUNTIME_P10_P12_P14_CONTINUATION_3_WORKER_DISPATCH.md`
- `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P11_MAINTAINED_HUD_CANONICAL_OVERLAY_WIRING_RESULT.json`
- `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P6_ENEMY_CANONICAL_RENDER_ANCHOR_LABELS_RESULT.json`
- `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P8_CANONICAL_OVERLAY_PRODUCT_PLAN_RESULT.json`
- `product/alpha/wof_alpha_field_adapter.js`
- `product/alpha/wof_alpha_hud.js`
- `product/alpha/wof_alpha_enemy_target_labels.js`

Perform dedup-v2 create-only canonical claim + exact-token re-read + create-only stage claim + exact-token re-read before implementation. Fail closed on any ownership failure. Do not invent recovery.

## Goal

Decouple enemy **gameplay target semantics** from legacy world/camera projection so the canonical P11 path can receive `slot / target7E / target` even when legacy enemy projection is unproved, while canonical P9/P10 anchors remain the **only** spatial authority once canonical overlay authority is bound.

Current defect to fix:

`wof_alpha_field_adapter.js` currently gates enemy marker construction through `projectionProfile`; `markerSnapshot(...)` returns no marker payload when that old projection profile is unavailable. P11, however, needs the current target semantics independently from position because canonical position now comes from the P9/P10 anchor envelope.

The intended product split is:

`RAM gameplay semantics (slot / target7E / target)`
`+ canonical anchor envelope (position only)`
`-> P11 maintained HUD`
`-> P8 unified product draw plan`

No legacy coordinate fallback is allowed.

## Required implementation

1. Inspect the current field-adapter publication and maintained-HUD receive paths before editing. Preserve existing safe transport authority/session/epoch checks.
2. Introduce or expose a semantic-only enemy target publication path that does **not** require a valid legacy `projectionProfile`.
3. Semantic-only target rows may contain only non-spatial gameplay identity/content needed by the canonical product path, such as:
   - enemy slot/source id (`enemy-slot-N`);
   - enemy type if already part of current semantics;
   - `target7E`;
   - mapped target player (`P1/P2/P3`) using the existing canonical mapping;
   - current sample/runtime authority metadata needed for staleness checks;
   - safety metadata.
4. Semantic-only publication must contain **no position authority**:
   - no enemy x/y/z;
   - no world/camera coordinates;
   - no projection snapshot/profile;
   - no screen-space x/y;
   - no screenshot/template/click/nearest-object data.
5. Preserve exact target semantics: `0 -> P1`, `4 -> P2`, `8 -> P3`; unsupported/invalid target values must fail closed for that row.
6. Prefer a distinct semantic-only message kind/channel shape if that is the safest compatibility boundary. Do not silently reinterpret a legacy spatial marker payload in a way that could make old consumers draw guessed coordinates.
7. Update the maintained P11 HUD only as narrowly needed so canonical-bound enemy target planning consumes the semantic-only current target state plus canonical anchor positions.
8. When canonical authority is bound:
   - target **content/identity** comes from semantic-only current target state;
   - target **position** comes only from valid current P9 canonical enemy anchors;
   - missing/stale/malformed semantic state => no enemy target-label intent;
   - missing/stale/SUPPRESSED canonical anchor => no enemy target-label intent;
   - legacy marker/world/camera/projected coordinates are never fallback.
9. When canonical authority is not bound, preserve existing legacy compatibility behavior as-is. P14 is not asked to make old projection the normal path; it is only forbidden from breaking unrelated historical behavior unnecessarily.
10. Clear stale semantic state on authority/runtime/session mismatch, transport reset, or explicit canonical clear as appropriate. Never retain a prior target semantic row across an invalid/new authority generation.
11. Confirm player danger semantics are not accidentally coupled to the same enemy projection gate. Do not broaden P14 into danger-policy changes unless a direct equivalent coupling is proven in current code; if found, record it precisely and make only the minimum equivalent semantic/spatial split.
12. Do not edit P10 transport bridge implementation files, P12 registry implementation files, W3 producer/capture/claims, `alpha_runtime.py`, package manifests/generators, updater, or `alpha-live`.
13. Preserve fixed TEST and P5 direct P1 behavior.
14. Preserve safety: `readOnly=true`, `ramWrites=0`, `inputInjection=false`.

## Fail-closed rules

Canonical-bound path must never obtain position from:
- legacy world/camera projection;
- Y/Z models;
- screenshot/template tracking;
- click calibration;
- nearest sprite/object;
- stale marker payloads;
- guessed constants.

Semantic-only target publication is not spatial proof and must never be presented as such in status/result evidence.

## Minimum self-check only

Implementation first. Run only enough to catch obvious breakage:
- JS parse/load for changed files;
- one synthetic field-adapter/transport fixture proving target semantics are publishable with legacy enemy projection absent and that the semantic payload contains no spatial fields;
- one canonical HUD fixture proving semantic target + READY canonical enemy anchor produces the existing target-label intent;
- one missing/stale semantic or SUPPRESSED canonical anchor fixture proving the label clears/hides with no legacy draw fallback.

No broad regression, Fresh QA, real-WOF run, Owner test, package rebuild, or W3 qualification.

## Terminal

Write exact RESULT.json + RESULT.md declared above. Record implementation commits, changed files, minimum self-checks, integrationReady, blocker, productProof boundary, safety, and nextAction.

Do not claim real-WOF product PASS. Expected next action is PM integration with P10/P12/P13 and then one coherent pinned candidate before final live qualification.

Terminal reporting must follow `parallel/PM/ALPHA_WORKER_RESULT_FAST_FEEDBACK_PROTOCOL_V1.md`.

Final commit begins:
`WORKER_RESULT ALPHA_V1_PRODUCT_TAKEOVER_P14_CANONICAL_SEMANTIC_SPATIAL_DECOUPLING <STATE>`

Chat only COMPLETE / SUBCOMPLETE / precise BLOCKED.

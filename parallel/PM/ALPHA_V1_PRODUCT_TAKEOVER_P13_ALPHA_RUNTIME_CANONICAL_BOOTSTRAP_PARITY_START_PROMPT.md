stageId: `ALPHA_V1_PRODUCT_TAKEOVER_P13_ALPHA_RUNTIME_CANONICAL_BOOTSTRAP_PARITY`
dedupProtocol: `v2`
dedupKey: `alpha.v1.product-takeover.alpha-runtime-canonical-bootstrap-parity-v1`
dedupMode: `exclusive`
resultProtocol: `wof-alpha-worker-result-v1`
resultJsonPath: `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P13_ALPHA_RUNTIME_CANONICAL_BOOTSTRAP_PARITY_RESULT.json`
resultMdPath: `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P13_ALPHA_RUNTIME_CANONICAL_BOOTSTRAP_PARITY_RESULT.md`
terminalCommitPrefix: `WORKER_RESULT ALPHA_V1_PRODUCT_TAKEOVER_P13_ALPHA_RUNTIME_CANONICAL_BOOTSTRAP_PARITY`
dispatchManifestPath: `parallel/PM/DISPATCH_MANIFESTS/ALPHA_V1_CANONICAL_RUNTIME_P10_P12_P13_CONTINUATION_3_WORKER_V1.json`

# Alpha V1 Product Takeover P13 — AlphaRuntime Canonical Bootstrap Parity

Repository: `ouyong520/wof-ai-private`

Read latest `main` first, then:
- `parallel/PM/ALPHA_V1_CANONICAL_RUNTIME_P10_P12_P13_CONTINUATION_3_WORKER_DISPATCH.md`
- `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P11_MAINTAINED_HUD_CANONICAL_OVERLAY_WIRING_RESULT.json`
- `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P8_CANONICAL_OVERLAY_PRODUCT_PLAN_RESULT.json`
- `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P9_CANONICAL_ANCHOR_RUNTIME_ENVELOPE_RESULT.json`
- `parallel/PYLAUNCH/wof_launcher/alpha_runtime.py`
- `product/alpha/wof_alpha_canonical_anchor_envelope.js`
- `product/alpha/wof_alpha_canonical_overlay_plan.js`
- `product/alpha/wof_alpha_hud.js`

Perform dedup-v2 create-only canonical claim + exact-token re-read + create-only stage claim + exact-token re-read before implementation. Fail closed on ownership failure. Do not invent recovery.

## Goal

Bring the package-selected `AlphaRuntimeManager` page bootstrap route into parity with the now-complete P11 maintained HUD dependency chain.

Current `AlphaRuntimeManager.PAGE_SOURCES` loads P6/P7 and then the maintained HUD, but P11's maintained HUD now requires the P9 canonical envelope and P8 unified product plan. P13 must ensure this normal Alpha runtime path can load the same canonical browser stack in the correct order and positively verify the P11 canonical HUD API instead of silently starting an incomplete page runtime.

Target page load order:

`bootstrap`
`-> HUD model`
`-> P6 enemy planner`
`-> P7 player warning planner`
`-> P9 canonical anchor envelope`
`-> P8 canonical overlay product plan`
`-> P11 maintained HUD`

This task is bootstrap/dependency parity only. P10 owns canonical frame transport and authority bind/ingest/revoke. W3 owns renderer-source qualification.

## Required implementation

Prefer changing only:

`parallel/PYLAUNCH/wof_launcher/alpha_runtime.py`

1. Add these browser dependencies to `PAGE_SOURCES` before `wof_alpha_hud.js`:
   - `product/alpha/wof_alpha_canonical_anchor_envelope.js`
   - `product/alpha/wof_alpha_canonical_overlay_plan.js`.
2. Refactor `_page_install(...)` only as needed so source loading remains deterministic and readable; do not duplicate canonical planning/normalization logic.
3. After page injection, verify all required canonical globals exist:
   - `window.WOFAlphaCanonicalAnchorEnvelope`
   - `window.WOFAlphaCanonicalOverlayPlan`
   - `window.WOFALPHAHUD`.
4. Positively verify the completed P11 HUD exposes:
   - `bindCanonicalOverlayAuthority`
   - `ingestCanonicalAnchorEnvelope`
   - `clearCanonicalOverlayAuthority`
   - `status`.
5. If any canonical dependency/API is missing, `_page_install` must fail closed with a precise `AlphaRuntimeError`; do not continue as a seemingly successful legacy page runtime.
6. Return/store page capability evidence in runtime status, e.g. `canonicalOverlayCapable: true` plus the current unbound canonical HUD status. Do not report READY draw proof merely because the API exists.
7. Preserve fixed TEST APIs/behavior; this task must not modify fixed smoke semantics.
8. Preserve the existing P5 direct P1 path. Do not change tracker geometry or P1 bridge semantics.
9. Do not bind canonical overlay authority or ingest anchor envelopes here. P10 owns runtime transport and binding.
10. Do not modify `production_p1_overlay.py`, P10's bridge file, P11 HUD JS, W3 producer/capture code, package manifest/generator, updater, launcher package selection, or `alpha-live`.
11. Do not use legacy projection/screenshot data as a substitute if the canonical browser dependency stack fails to load. Missing P9/P8/P11 capability is a bootstrap failure for the canonical-capable path.
12. Keep safety `readOnly=true`, `ramWrites=0`, `inputInjection=false`.

## Important package boundary

`AlphaRuntimeManager._verified_text(...)` remains package-manifest-gated. P13 must not weaken that integrity check and must not auto-load unpinned files from arbitrary `main`.

If the current package manifest does not yet pin the new P9/P8 files, record that as a **later package-promotion dependency**, not a reason to bypass verification. Do not modify package manifests in this task and do not move `alpha-live`.

## Minimum self-check only

Implementation first. Run only enough to catch obvious breakage:
- Python parse/compile;
- one fake/controlled page-install fixture or narrow source-order inspection proving P9 then P8 are loaded before HUD and P11 API capability is required;
- one missing-P9/P8/HUD-API fixture proving precise fail-closed bootstrap behavior;
- confirm fixed-draw API path is not removed/renamed.

Do not add broad regression. No real-WOF run, Owner test, Fresh QA, package rebuild, or W3 qualification.

## Terminal

Write the exact RESULT.json + RESULT.md declared above. Record implementation commits, changed files, minimum self-checks, integrationReady, blocker, package-boundary note, productProof boundary, safety, and nextAction.

Do not claim real-WOF PASS. Expected next action is to combine the canonical-capable AlphaRuntime page bootstrap with P10 transport and later update the pinned package candidate only after PM integration.

Final commit begins:
`WORKER_RESULT ALPHA_V1_PRODUCT_TAKEOVER_P13_ALPHA_RUNTIME_CANONICAL_BOOTSTRAP_PARITY <STATE>`

Chat only COMPLETE / SUBCOMPLETE / precise BLOCKED.

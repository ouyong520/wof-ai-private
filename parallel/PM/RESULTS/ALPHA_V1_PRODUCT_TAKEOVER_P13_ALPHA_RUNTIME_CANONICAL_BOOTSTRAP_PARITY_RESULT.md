# Alpha V1 Product Takeover P13 — AlphaRuntime Canonical Bootstrap Parity RESULT

Status: **COMPLETE / integration-ready**

- stage: `ALPHA_V1_PRODUCT_TAKEOVER_P13_ALPHA_RUNTIME_CANONICAL_BOOTSTRAP_PARITY`
- dedup key: `alpha.v1.product-takeover.alpha-runtime-canonical-bootstrap-parity-v1`
- claim token: `96b25761873f9dfc3072a21a2b239a1d`
- RESULT JSON: `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P13_ALPHA_RUNTIME_CANONICAL_BOOTSTRAP_PARITY_RESULT.json`

The dedup-v2 canonical claim and stage claim were created create-only, re-read with the exact token before implementation, and are now both closed `COMPLETE`.

## Implementation

Implementation commit:

- `12c8b73bf91fc4af81203b1f9c3772e59b995321` — canonical AlphaRuntime bootstrap parity.

Changed implementation file only:

- `parallel/PYLAUNCH/wof_launcher/alpha_runtime.py`

`PAGE_SOURCES` now loads the package-verified browser stack in this deterministic order:

`bootstrap -> HUD model -> P6 enemy planner -> P7 player warning planner -> P9 canonical anchor envelope -> P8 canonical overlay plan -> P11 maintained HUD`

`_page_install(...)` now positively requires:

- `window.WOFAlphaCanonicalAnchorEnvelope`
- `window.WOFAlphaCanonicalOverlayPlan`
- `window.WOFALPHAHUD`
- `WOFALPHAHUD.bindCanonicalOverlayAuthority`
- `WOFALPHAHUD.ingestCanonicalAnchorEnvelope`
- `WOFALPHAHUD.clearCanonicalOverlayAuthority`
- `WOFALPHAHUD.status`

Missing package-selected P9/P8 text, source-injection failure, missing canonical HUD API, invalid HUD status, or an unexpectedly bound initial canonical status fails closed through `AlphaRuntimeError`; P13 does not silently continue as a legacy-success page runtime.

The page capability evidence records `canonicalOverlayCapable=true` plus the initial canonical HUD status. The controlled fixture proved the expected initial state is unbound / `SUPPRESSED` / `NOT_BOUND`; API presence is not reported as READY draw proof.

P13 does not bind canonical overlay authority and does not ingest envelopes. Those remain P10 responsibilities.

## Minimum self-check

- Exact committed `alpha_runtime.py` Python compile + AST parse — **PASS**. Local git blob `19203d281c7f3b8127946e39ed5f3c7d3d145aee` exactly matches the GitHub committed content SHA.
- Controlled `_page_install` source-order/capability fixture — **PASS**. P9 then P8 were injected before HUD; canonical capability was true and initial canonical status was unbound.
- Missing dependency/API fail-closed fixture — **PASS**. Missing P9, missing P8, and missing `ingestCanonicalAnchorEnvelope` each produced precise `AlphaRuntimeError` failure.
- Fixed TEST preservation inspection — **PASS**. P13 changed no HUD file; `setFixedDrawSmokeEnabled` / `fixedDrawSmokeStatus` remain exported by the maintained HUD. The P5 direct P1 path was not changed.
- Real-WOF / Owner acceptance / package rebuild — **NOT_RUN**, outside P13 authority.

No broad regression, Fresh QA, P10 transport execution, W3 qualification, package generator/manifest change, updater/launcher selection change, or `alpha-live` movement was performed.

## Package boundary

The current pinned package is `2026.09.03.65422137bc1e`. It predates P13/P11 and does not pin the new P9/P8 browser modules; its pinned AlphaRuntime/HUD are also pre-integration versions.

This is intentionally a later package-promotion dependency. `_verified_text(...)` remains package-manifest-gated and was not weakened. Until PM promotes a candidate containing the integrated P13 AlphaRuntime plus P9/P8/P11 HUD files, the canonical-capable package-selected path correctly fails closed instead of loading arbitrary `main` content.

## Product-proof boundary

P13 provides implementation proof only for package-selected AlphaRuntime bootstrap/dependency parity, canonical HUD API gating, fail-closed behavior, and capability-status reporting.

It does **not** prove P10 runtime transport, W3 renderer/object source qualification, real-WOF canonical machine draw, or Owner-visible persistence.

## Blocker / next action

P13 implementation blocker: **none**.

Next action: PM integrates P13 with P10/P11, then promotes a later pinned package candidate containing the integrated `alpha_runtime.py` plus P9/P8/P11 canonical HUD files before any `alpha-live` movement or real-WOF canonical acceptance.

Safety: `readOnly=true`, `ramWrites=0`, `inputInjection=false`.

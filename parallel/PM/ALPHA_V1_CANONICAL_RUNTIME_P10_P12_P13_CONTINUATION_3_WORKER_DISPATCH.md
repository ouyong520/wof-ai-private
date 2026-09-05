# Alpha V1 — Canonical Runtime P10/P12/P13 Continuation Dispatch

Repository: `ouyong520/wof-ai-private`

This continuation preserves the already ACTIVE P10 runtime-transport ownership, accepts P11 as COMPLETE/integration-ready, and adds exactly two new independent implementation workers: P12 actor-generation registry and P13 AlphaRuntime canonical bootstrap parity.

## Current authority state

- P10 `ALPHA_V1_PRODUCT_TAKEOVER_P10_CANONICAL_ANCHOR_RUNTIME_TRANSPORT_BRIDGE` remains ACTIVE under its existing dedup-v2 claim. Do not re-claim, recover, supersede, or steal it.
- P11 `ALPHA_V1_PRODUCT_TAKEOVER_P11_MAINTAINED_HUD_CANONICAL_OVERLAY_WIRING` is COMPLETE / integration-ready.
- P5/P6/P7/P8/P9 are COMPLETE / integration-ready.
- W3 renderer/object source qualification remains under its existing ACTIVE authority. P12/P13 may consume its frame contract but must not modify W3 producer/capture/claim files or pretend source qualification is proven.

## Parallel objective

Advance the remaining runtime integration without creating QA-only work:

1. **P10** continues building the canonical frame -> READY/SUPPRESSED transport bridge into the P11 maintained HUD API.
2. **P12** provides the missing explicit `actor + generation` registry that a P10 caller can use without guessing actor identity, order, or coordinates.
3. **P13** fixes the package-selected `AlphaRuntimeManager` browser bootstrap path so it loads the P9/P8 dependencies required by the completed P11 HUD and verifies canonical HUD capability instead of silently starting an incomplete page runtime.

Target convergence:

`W3-format frame`
`-> explicit actor/generation registry (P12)`
`-> DeterministicRenderObjectAnchor / P10 transport`
`-> P9 envelope`
`-> P8 unified product plan`
`-> P11 maintained WebGL HUD`

with the package-selected Alpha page bootstrap able to load the same canonical modules through P13.

## Ownership boundaries

### P10 owns
- `parallel/PYLAUNCH/wof_launcher/canonical_overlay_runtime_bridge.py` or equivalent runtime/CDP transport bridge it creates;
- narrow `production_p1_overlay.py` source-injection/load-order changes required by its existing prompt;
- its existing RESULT and claims.

### P12 owns
- a new actor/generation registry module, preferably `parallel/PYLAUNCH/wof_launcher/canonical_actor_generation_registry.py`;
- only the minimum implementation evidence needed for that module.

P12 must not edit P10-owned bridge/transport files, `alpha_runtime.py`, HUD files, W3 producer/capture files, or package manifests.

### P13 owns
- `parallel/PYLAUNCH/wof_launcher/alpha_runtime.py` only, unless one tiny adjacent launcher source is strictly necessary and non-overlapping;
- browser PAGE_SOURCES/bootstrap verification for P9/P8/P11 canonical capability.

P13 must not edit P10 bridge/transport files, `production_p1_overlay.py`, P11 HUD code, W3 producer/capture files, package manifests, updater/launcher package selection, or `alpha-live`.

## Product rules

- Implementation and chain completion are the priority. Only minimum parse/compile and narrow fixtures are expected.
- No broad regression, Fresh QA, second-opinion audit, Owner test, real-WOF acceptance, or package churn in this dispatch.
- Canonical spatial authority remains fail-closed. Missing/unproven/SUPPRESSED/stale/mixed-epoch/ambiguous/generation-invalid data must remain hidden.
- No screenshot/template, world/camera projection, Y/Y-Z/Y+Z fitting, click calibration, nearest-sprite, guessed constants, stale previous coordinates, or actor-order inference may become position authority.
- Preserve `readOnly=true`, `ramWrites=0`, `inputInjection=false`.
- Do not move `alpha-live`.

## Reporting

P10 continues using its original result paths and claim token.

P12/P13 must follow:
`parallel/PM/ALPHA_WORKER_RESULT_FAST_FEEDBACK_PROTOCOL_V1.md`

Each new worker writes only the exact RESULT.json + RESULT.md paths declared by its start prompt/manifest. Terminal chat remains only COMPLETE / SUBCOMPLETE / precise BLOCKED.

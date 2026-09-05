# Alpha V1 Product Takeover G1 — Fixed-Draw Owner-Gate Runtime Wiring

stageId: `ALPHA_V1_PRODUCT_TAKEOVER_G1_FIXED_DRAW_OWNER_GATE_RUNTIME_WIRING`
dedupProtocol: `v2`
dedupKey: `alpha.v1.product-takeover.fixed-draw-owner-gate-runtime-wiring`
dedupMode: `exclusive`

Repository: `ouyong520/wof-ai-private`

Parent authority:
`parallel/PM/ALPHA_V1_PRODUCT_TAKEOVER_FIRST_OWNER_GATE_3_WORKER_DISPATCH.md`

Baseline before this dispatch: `f63f53042f555d4f0e0221a0dc165aa51f7c5add`

## Scope isolation

Alpha Owner-visible product only. Do not read, run, modify, test, schedule, or use evidence from Collector, Unified Collector, Training Farm / 10训.

## Dedup-v2 gate

Before task work, re-read latest `main`, parent dispatch, `parallel/PM/STAGE_DEDUP_GUARD.md`, relevant W1/W2/W3 results and claims, and recent equivalent commits.

If the stop condition is already satisfied, return `ALREADY COMPLETE — SAFE TO CLOSE`.

Otherwise create-only acquire:
`parallel/PM/DEDUP_CLAIMS/alpha.v1.product-takeover.fixed-draw-owner-gate-runtime-wiring.json`

with a fresh unpredictable token and latest-main `startCommit`. Re-read current main and verify exact schema/dedupKey/effectiveDedupKey/dedupMode/stageId/promptPath/claimToken/state=ACTIVE. Then create-only acquire and verify:
`parallel/PM/STAGE_CLAIMS/ALPHA_V1_PRODUCT_TAKEOVER_G1_FIXED_DRAW_OWNER_GATE_RUNTIME_WIRING.json`

Do not implement or test before both are verified. Any create/verification failure fails closed; do not invent a recovery key.

## Existing accepted components

W2 already delivered:
- maintained production WebGL fixed `TEST` smoke;
- `ProductionHudFixedDrawSmoke` adapter;
- fixed native contract `384x224`, center `(192,112)`;
- states including `HUD_INJECTION_MISSING`, `GAME_CANVAS_CONTEXT_MISSING`, `DRAW_HOOK_NOT_FIRING`, `DRAWING_BUFFER_INVALID`, `DRAW_FAILED`, `FIXED_TEST_ACTUALLY_DRAWN`, `DISABLED`.

Do not reimplement the HUD smoke itself.

## Objective

Wire the **existing permanent Alpha runtime** so a controlled first-Owner-gate mode can enable and poll the accepted `ProductionHudFixedDrawSmoke` without waiting for P1 semantic/visual acquisition.

Canonical gate environment contract for this workstream:
`WOF_ALPHA_FIXED_DRAW_SMOKE=1`

When absent/not `1`, normal Alpha behavior must remain unchanged.

## Required behavior

1. The runtime entry discovers/attaches to the accepted real WOF page using existing Alpha discovery/reuse behavior.
2. When `WOF_ALPHA_FIXED_DRAW_SMOKE=1`, it enables `ProductionHudFixedDrawSmoke` as soon as the maintained production HUD can be attached/installed; it must not wait for P1, enemy, semantic, screenshot, or world-projection readiness.
3. Poll fixed-smoke state at a bounded cadence and persist one machine-readable status under `Documents\WOF_RESULTS` (a narrowly named JSON/status file is allowed).
4. Status must include at least release/commit/runtime epoch, fixed-smoke state, `drawHooked`, `drawCount`, callback count, drawing-buffer metadata, last error, and safety fields.
5. `FIXED_TEST_ACTUALLY_DRAWN` may be reported only when the W2 adapter's strict predicate is true. No callback-only/DOM/diagnostic false green.
6. If page/HUD/canvas/hook is missing, surface the exact W2 machine state rather than falling into P1 acquisition status.
7. Smoke mode must remain opt-in and reversible. When env is off, do not enable fixed smoke and do not disturb existing production overlay behavior.
8. Maintain `readOnly=true`, `ramWrites=0`, `inputInjection=false`.

## File ownership

G1 owns runtime gate activation/status glue only, principally:
- `parallel/PYLAUNCH/render_authority_measurement_entry.py` and/or the narrow accepted runtime entry it delegates to;
- `parallel/PYLAUNCH/wof_launcher/production_p1_overlay.py` only if a minimal adapter interface correction is unavoidable;
- one narrowly named gate-status helper if required;
- focused tests and G1 SUBRESULT.

Do **not** edit:
- `WOF_ALPHA_SETUP_ONCE.cmd`;
- `WOF_ALPHA_TEST.cmd`;
- `parallel/PYLAUNCH/owner_live_retest_loop.ps1`;
- updater/bootstrap release-mode marker owned by G2;
- `product/alpha/wof_alpha_hud.js` unless a proven W2 regression requires a minimal correction (otherwise stop and report conflict);
- W3 renderer/object authority files;
- enemy/semantic/danger logic.

## Acceptance

Focused tests must prove:
- gate env off => current normal runtime unchanged;
- gate env on => fixed-smoke path starts before any P1 acquisition dependency;
- strict W2 success predicate is preserved;
- all upstream failure states remain distinguishable;
- status artifact is deterministic and contains safety fields;
- no P1/enemy/semantic/screenshot/projection input is required to enter the smoke probe.

Do not run broad historical QA. Do not ask Owner to test from this worker.

## Exit

Deliver one integration-ready commit + durable G1 SUBRESULT and close canonical/stage claims with exact token, or a precise blocker. Stop only at SUBCOMPLETE/COMPLETE/precise BLOCKED.
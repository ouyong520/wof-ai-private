# Alpha V1 Product Takeover P1 — Runtime Fixed TEST Gate — SUBRESULT

result: `SUBCOMPLETE`
executionState: `COMPLETE`
integrationReady: `true`
ownerLiveGate: `PENDING_PM_INTEGRATION_NOT_RUN`

stageId: `ALPHA_V1_PRODUCT_TAKEOVER_P1_RUNTIME_FIXED_TEST_GATE`
dedupProtocol: `v2`
dedupKey: `alpha.v1.product-takeover.first-owner-gate.runtime-fixed-test-gate-v2`
dedupMode: `exclusive`
claimToken: `551e380d6edb76de2182acfd2e94039d11feb8f4329f769d`
startCommit: `fbda59aa0b2ba21ecb4b7f56b3506d71bce72d1e`
integrationReadyCommit: `81c8883c104741612dad1e02cfebf577a844a897`

## Delivered P1 runtime gate

When `WOF_ALPHA_FIXED_DRAW_SMOKE=1` is present, `parallel/PYLAUNCH/render_authority_measurement_entry.py` now diverts into a dedicated fixed-smoke runtime gate **before** loading the existing Render Authority V3/P1 runner.

The gate therefore does not wait for or consume P1 identity, semantic evidence, click fallback, screenshot tracking, enemy data, world/camera projection, or P1 lifecycle readiness. It discovers only a page target with the existing WOF game canvas + WebGL context signature, then enables and continuously polls the already-accepted `ProductionHudFixedDrawSmoke` adapter.

When the environment flag is absent, the existing runtime runner path remains unchanged.

## Stable machine-readable artifact

The controlled gate continuously maintains:

`<output-root>\ALPHA_FIXED_DRAW_STATUS.json`

The permanent Alpha launcher supplies the normal `Documents\WOF_RESULTS` output root, so the product artifact is `Documents\WOF_RESULTS\ALPHA_FIXED_DRAW_STATUS.json`.

The artifact schema is `wof-alpha-runtime-fixed-draw-status-v1` and contains at least:

- release/acceptance SHA plus checkout SHA fallback
- runtime epoch
- page target id / URL / title when available
- fixed-smoke state
- `drawHooked`
- `callbackCount`
- `drawCount`
- drawing-buffer metadata
- native `384x224`
- native center `192,112`
- label `TEST`
- last error
- `readOnly=true`
- `ramWrites=0`
- `inputInjection=false`

Explicit states are preserved without collapsing failures:

- `HUD_INJECTION_MISSING`
- `GAME_CANVAS_CONTEXT_MISSING`
- `DRAW_HOOK_NOT_FIRING`
- `DRAWING_BUFFER_INVALID`
- `DRAW_FAILED`
- `FIXED_TEST_ACTUALLY_DRAWN`
- `DISABLED`

The additional `drawSuccess` field is fail-closed. It can become true only for `FIXED_TEST_ACTUALLY_DRAWN` with maintained HUD injected, real game canvas/context present, draw hook active, `drawCount > 0`, a positive drawing buffer, exact `TEST` / `384x224` / `192,112` metadata, and the read-only safety contract intact.

## Files changed under P1 authority

- `parallel/PYLAUNCH/wof_launcher/fixed_draw_runtime_gate.py`
- `parallel/PYLAUNCH/render_authority_measurement_entry.py`
- `parallel/PYLAUNCH/tests/test_alpha_p1_runtime_fixed_test_gate.py`
- this P1 SUBRESULT and the P1 canonical/stage claim records

P1 did **not** modify `product/alpha/wof_alpha_hud.js`, setup/bootstrap/updater/live-mode marker files, W3 renderer/object authority, enemy/semantic/danger logic, or the `alpha-live` ref. Collector / Unified Collector / Training Farm / 10训 were not read, run, modified, or tested.

## Focused verification

Implementation-owned focused checks completed on the exact P1-authored runtime/test contents:

- Python syntax/compile-equivalent parse for the new runtime helper, modified entry, and focused test: PASS
- `parallel/PYLAUNCH/tests/test_alpha_p1_runtime_fixed_test_gate.py`: `4/4 PASS`
- exact opt-in (`1` only) and OFF-path preservation: PASS
- gate reaches the existing fixed-smoke probe using only page/canvas/context discovery: PASS
- scan expression contains no P1 / semantic / click / screenshot / enemy / projection / camera dependency: PASS
- all seven fixed-smoke states persist exactly: PASS
- false-green checks for zero draw count and invalid drawing buffer: PASS
- exact native metadata and read-only safety fields: PASS

No GitHub Actions workflow run was attached to the integration-ready commit, so no CI result is fabricated here.

## Owner/live checkpoint

This P1 worker did not ask the Owner to test and did not move `alpha-live`. Real-WOF visual acceptance remains owned by the later PM integration gate.

P1 is integration-ready for P2/P3 consumption at `81c8883c104741612dad1e02cfebf577a844a897`.

# Alpha V1 Product Takeover W2 — Maintained Production HUD Fixed-Draw Smoke — Execution Recovery V1 SUBRESULT

result: `SUBCOMPLETE`
executionState: `COMPLETE`
integrationReady: `true`
ownerLiveGate: `PENDING_NOT_RUN`

stageId: `ALPHA_V1_PRODUCT_TAKEOVER_W2_MAINTAINED_PRODUCTION_HUD_FIXED_DRAW_SMOKE_EXECUTION_RECOVERY_V1`
dedupKey: `alpha.v1.product-takeover.maintained-production-hud-fixed-draw-smoke.execution-recovery-v1`
effectiveDedupKey: `alpha.v1.product-takeover.maintained-production-hud-fixed-draw-smoke.execution-recovery-v1`
claimToken: `444405bb-8fb6-4b60-a8ee-6240151dd936`
startCommit: `5093baa02d49b2c11285e0ad08ef5a7032494c09`
integrationReadyCommit: `9b4a99b445c9004f7c2d5dc41a3a7fa8878c9335`

## Delivered W2 implementation

The maintained Alpha production WebGL HUD now has a strictly opt-in fixed-draw smoke path. Smoke is disabled by default and normal production behavior is unchanged until explicitly enabled.

When enabled, the maintained HUD draws literal `TEST` from canonical native `384x224` centered at native `(192,112)`. The canonical native rectangle is mapped explicitly once to the current WebGL drawing buffer. The smoke callback runs before the ordinary product visibility/P1 path and therefore does not require P1 tracking, semantic identity, enemy data, screenshot tracking, or world/camera projection.

The smoke draw uses the maintained production renderer's existing `drawTexture(...)` path and the same persistent `__WOF_GL_HOOK` callback used by final Alpha. A smoke draw is counted as successful only after `bridge.nativeDraw.call(gl, gl.TRIANGLES, 0, 6)` completes and the maintained renderer's draw count advances. DOM overlay, Tk, diagnostic canvas, white acquisition marker, and callback-only/fake draw counts cannot satisfy the success predicate.

## Machine-readable states

The probe exposes explicit state including:

- `HUD_INJECTION_MISSING`
- `GAME_CANVAS_CONTEXT_MISSING`
- `DRAW_HOOK_NOT_FIRING`
- `DRAWING_BUFFER_INVALID`
- `DRAW_FAILED`
- `FIXED_TEST_ACTUALLY_DRAWN`
- `DISABLED`

Successful proof additionally requires the exact fixed label/native metadata (`TEST`, `384`, `224`, `192`, `112`), real game canvas/context, maintained hook active, and smoke `drawCount > 0`.

## Files changed under W2 authority

- `product/alpha/wof_alpha_hud.js`
- `parallel/PYLAUNCH/wof_launcher/production_p1_overlay.py` — narrow fixed-smoke probe adapter only; existing production P1 adapter behavior retained
- `parallel/PYLAUNCH/tests/test_alpha_w2_fixed_draw_smoke.py`
- this W2 SUBRESULT and the recovery claim/stage records

No W1 updater/bootstrap files, W3 renderer/object-authority files, semantic identity, screenshot tracker algorithm, enemy target semantics, danger policy, Collector, Unified Collector, or Training Farm / 10训 files were modified by this W2 execution.

## Focused verification

Implementation-owned focused checks completed before this SUBRESULT:

- `node --check` on the staged `product/alpha/wof_alpha_hud.js`: PASS
- `python -m py_compile` on the staged `production_p1_overlay.py`: PASS
- `python -m py_compile` on the focused W2 test: PASS
- `parallel/PYLAUNCH/tests/test_alpha_w2_fixed_draw_smoke.py`: `5/5` PASS

Focused acceptance covers: no DOM/diagnostic false-green; smoke-disabled behavior; maintained-native-draw proof ordering; explicit native-to-drawing-buffer mapping; fixed-smoke independence from P1/enemy/semantic/screenshot/projection inputs; and precise upstream failure-state reporting.

## Owner/live checkpoint

This worker did **not** request or run the first Owner real-WOF visual gate. The next integration checkpoint remains exactly:

`真实 WOF 游戏画面里，固定 TEST 是否持续可见？`

Therefore this SUBRESULT records an integration-ready W2 implementation, not a fabricated real-WOF visual PASS.

## Dedup / authority closeout

The superseded original W2 canonical/stage remain historical `BLOCKED` for `PM_COORDINATOR_CLAIM_ONLY_NO_IMPLEMENTATION` and were not modified, revived, or reused. Only the execution-recovery canonical/stage carrying exact claimToken `444405bb-8fb6-4b60-a8ee-6240151dd936` are eligible for COMPLETE closeout.

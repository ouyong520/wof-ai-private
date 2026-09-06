# Alpha V1 P40 — Native Marker Renderer Source Runtime Exposure — RESULT

State: **BLOCKED**

P40 completed a fresh fail-closed source trace of the maintained Browser/Alpha Page, Worker/WASM discovery, page WebGL submission bridge, and the existing P36 source observer. No checked-in source-traced per-object gstyphoon CPS1 renderer submit export/hook exists that can truthfully provide exact native 1P/2P/3P + DOWN marker identity, explicit actor generation, native 384x224 x/y, displayed-frame/submission generation, and runtimeEpoch/rendererEpoch/authorityKey.

## Exact blocker

`NATIVE_PLAYER_MARKER_DISPLAYED_SUBMIT_SOURCE_EXPORT_NOT_PRESENT`

The maintained page HUD only wraps generic WebGL `drawArrays`; that hook has no native marker semantic identity or actor-generation association. The maintained Worker discovers an Emscripten-like module via HEAP arrays and reads ROM/CPS RAM/world/projection state; those paths are explicitly forbidden as native marker renderer authority. P36 already exposes the correct fail-closed consumer seam and refuses missing/ambiguous/stale sources.

Therefore P40 did **not** create `__WOF_NATIVE_MARKER_RENDERER_SUBMIT_SOURCE_V1__` or `WOFNativeMarkerRendererSubmitSourceV1`. Doing so from the generic GL hook, HEAP structure, pixels, screenshot/OCR/template, nearest/list order/timing, world projection, or guessed offsets would fabricate authority.

## Durable candidate/readback

- source-trace candidate commit: `5a3b9bce01e794e030974a94f7511a39fa56e818`
- candidate tree: `4ebd86fb0e58f07fe774401ab42a0d3c65241760`
- P40 source-trace artifact blob: `ac820e9aded5678cd105e8d6759ea22d57cab31e`
- fresh runtime blobs used by the trace:
  - `product/alpha/wof_alpha_bootstrap.user.js`: `5aed15ff14aa39d95eade187cefb63dbd00848e6`
  - `product/alpha/wof_alpha_hud.js`: `f6f176294a4fe4a77b21c02abae6ba2d37681b70`
  - `product/alpha/wof_alpha_real_worker.js`: `c3ffa748b334f4124466d553b72ff29f8fb5b3d2`
  - `parallel/RENDER_AUTHORITY_V2/native_marker_renderer_submit_source_trace_worker.js`: `c188d1b34fe45c295a24a1dd012a9b671e604bfb`

## Focused checks

- exact candidate/readback: PASS
- maintained Page/Worker/WASM source eligibility audit: PASS; blocker confirmed
- unique truthful P36 runtime source exposure: FAIL because the source producer/export is absent
- exact P1/P2/P3 actor-generation native submit events: NOT_RUN because the direct source is the missing edge and fixtures cannot prove it exists
- zero-click / zero-manual-seed boundary: PASS
- no HEAP/pixel/screenshot/OCR/template/nearest/order/timing/guessed-offset fallback: PASS
- stale/mixed authority and missing/ambiguous source rejection: preserved unchanged in P36/P32
- real WOF: NOT_RUN by scope
- promotion / alpha-live move: NOT_RUN

P39 visible-baseline ownership and P41 harness ownership were not modified.

## Next action

A successor requires a checked-in or runtime-verifiable source mapping/export for the actual gstyphoon per-object displayed CPS1 submit, with enough direct semantic information to bind exact native marker state and actor generation. Until that exists, P36/P32 must remain fail-closed.

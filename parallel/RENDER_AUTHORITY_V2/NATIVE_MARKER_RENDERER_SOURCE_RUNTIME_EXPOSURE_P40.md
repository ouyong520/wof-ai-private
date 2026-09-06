# P40 Native Marker Renderer Source Runtime Exposure — Source-Trace Result

Status: **BLOCKED — fail-closed; no P36 source surface was fabricated.**

## Mission boundary

P40 may expose `__WOF_NATIVE_MARKER_RENDERER_SUBMIT_SOURCE_V1__` or `WOFNativeMarkerRendererSubmitSourceV1` only when the checked runtime provides a truthful `SOURCE_TRACED_POINTER`, `DIRECT_RENDER_HOOK`, or `EXPORTED_RENDERER_POINTER` for the actual displayed CPS1 native player-marker object submission.

The surface must provide exact 1P / 2P / 3P + DOWN marker identity, native 384x224 coordinates, explicit actor generation, displayedFrameId/submissionId/frameGeneration, runtimeEpoch/rendererEpoch/authorityKey, and a direct displayed-frame causal link. Structural HEAP, screenshot/pixel/OCR/template, nearest/order/timing, world projection, or guessed offsets are not substitutes.

## Fresh checked-in runtime trace

P40 traced the maintained Browser/Alpha runtime from the Page bootstrap through Worker/WASM discovery and the page draw hook.

### Page bootstrap

`product/alpha/wof_alpha_bootstrap.user.js` (fresh blob `5aed15ff14aa39d95eade187cefb63dbd00848e6`) deliberately leaves the game's Worker untouched. Its page-side game-surface readiness check sees only the game canvas/WebGL context (`window.I_GF1TC`, `window.I_fdC8Q`) and a generic `drawArrays` capability. It does not own or expose the game's CPS1 object renderer.

### Maintained HUD draw hook

`product/alpha/wof_alpha_hud.js` (fresh blob `f6f176294a4fe4a77b21c02abae6ba2d37681b70`) wraps the page WebGL context's generic `drawArrays` solely so Alpha can render after game draws. That callback proves only that a WebGL draw happened. It has no exact native marker object identity, no per-marker logical state, no actor generation association, and no source-traced CPS1 object-submit pointer/export. Therefore `window.__WOF_GL_HOOK` is **not** a qualifying P36 source and must not be relabeled as `DIRECT_RENDER_HOOK` for marker authority.

### Worker / WASM discovery

`product/alpha/wof_alpha_real_worker.js` (fresh blob `c3ffa748b334f4124466d553b72ff29f8fb5b3d2`) discovers an Emscripten-like module by `HEAPU8`/`HEAPU32`, validates the exact World 921031 ROM identity, obtains the CPS RAM window, and publishes state / player-spatial / enemy-target-marker data from read-only memory plus projection helpers. It contains no checked-in native renderer-submit export, source-traced renderer pointer, per-object CPS1 marker callback, or explicit mapping from displayed marker submission to P1/P2/P3 actor generation.

Those HEAP/world/projection paths are explicitly non-authoritative for P40's native marker renderer source and cannot be used to synthesize the missing surface.

### P36 observer seam

`parallel/RENDER_AUTHORITY_V2/native_marker_renderer_submit_source_trace_worker.js` (fresh blob `c188d1b34fe45c295a24a1dd012a9b671e604bfb`) already discovers exactly the two authorized surface names under `self`, `Module`, or `Module.asm`; it rejects missing/ambiguous surfaces and stale/mixed binding. P40 found no truthful checked-in producer behind those names.

P36's own source-trace contract also records the same underlying limitation: the repository does not contain the running gstyphoon WASM or a proven exported native renderer pointer and refuses to synthesize one.

## Why no runtime patch is correct

A P40 patch that wraps the generic WebGL `drawArrays`, scans `HEAPU8`, assigns marker identity by pixels/templates/nearest/order/timing, or guesses a WASM offset would manufacture authority that P36/P32 are designed to reject. None of those paths can supply the required exact displayed submit -> marker object/cluster -> actor-generation causal edge.

Accordingly P40 intentionally leaves both authorized source names absent. Absence is the correct fail-closed runtime state.

## Narrow exact blocker

`NATIVE_PLAYER_MARKER_DISPLAYED_SUBMIT_SOURCE_EXPORT_NOT_PRESENT`

Exact missing edge:

```text
actual running gstyphoon CPS1 renderer per-object displayed submit
-> source-traced/exported hook with exact native marker logical identity (1P/2P/3P/DOWN)
-> explicit P1/P2/P3 actor generation association
-> native 384x224 x/y + displayedFrameId/submissionId/frameGeneration
-> runtimeEpoch/rendererEpoch/authorityKey
-> __WOF_NATIVE_MARKER_RENDERER_SUBMIT_SOURCE_V1__ / WOFNativeMarkerRendererSubmitSourceV1
-> existing P36 observer
-> existing P32 qualifier
```

The checked-in maintained runtime reaches only the generic page WebGL draw boundary and read-only Worker HEAP/world-state boundary; neither contains the required semantic renderer submit edge.

## Focused acceptance matrix

- unique exact runtime source exposure + P36 discovery: **BLOCKED** — producer/export absent; P36 absence behavior remains fail-closed.
- P1/P2/P3 actor-generation event emission: **BLOCKED** — no source-traced per-object submit exists to emit truthful events.
- native 384x224 + displayed frame IDs: **BLOCKED** — no direct submit source exists.
- stale/mixed authority rejection: **PRESERVED** by unchanged P36 observer/P32 qualifier.
- ambiguity/missing source fail-closed: **PRESERVED**; no fallback source added.
- zero click / zero manual seed: **PASS BY CONSTRUCTION**; no Owner selection path was added.
- no structural/pixel/screenshot fallback: **PASS BY CONSTRUCTION**; no such adapter was added.
- bounded teardown/unsubscribe/no mutation: **PRESERVED** by unchanged P36 observer; P40 adds no live subscription or mutation.

No real WOF run was performed. No promotion or alpha-live movement was performed. P39 visible-baseline files and P41 harness ownership were not modified.

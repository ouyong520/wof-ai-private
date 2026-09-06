# P44 Historical GStyphoon Renderer Submit Export Archaeology

Status: **HISTORICAL SEARCH COMPLETE — NO QUALIFYING HISTORICAL DIRECT SOURCE FOUND**

Stage: `ALPHA_V1_PRODUCT_TAKEOVER_P44_HISTORICAL_GSTYPHOON_RENDERER_SUBMIT_EXPORT_ARCHAEOLOGY`

Blocker under investigation: `NATIVE_PLAYER_MARKER_DISPLAYED_SUBMIT_SOURCE_EXPORT_NOT_PRESENT`

## Scope and authority rule

This task searched repository history only. It did not run WOF, did not modify P42/P43 assets, did not create `rendererSourceProof`, did not promote anything, and did not move `alpha-live`.

A historical item is a `DIRECT_SOURCE_CANDIDATE` only if it can truthfully expose the actual displayed CPS1/gstyphoon per-object submit (or a source-traced/exported pointer to it), with enough semantics to recover the native `1P` / `2P` / `3P` + downward-marker object/cluster, native 384x224 x/y, displayed frame/submission identity, and explicit P1/P2/P3 actor-generation association. Generic WebGL timing, pixels, structural HEAP patterns, world-state coordinates, order/timing/nearest assumptions, and overlay-owned draws are not renderer authority.

## Search coverage

The reachable Git history was searched by commit-history keyword families covering: `gstyphoon`, `renderer`, `WebGL`, `WASM`, `object`, `sprite`, `pointer`, `export`, `queue`, `frame`, `CPS1`, `drawArrays`, `submit`, `source-traced`, `rendererSourceProof`, and `glue`.

In addition to the repository-wide history sweeps, exact historical blobs and relevant path histories were inspected for:

- `wof_canvas_probe.js` — complete retained path lineage from the original 2D probe through the real WebGL-game-canvas correction.
- `wof_canvas_hud.js` — retained direct-WebGL HUD/draw-hook lineage.
- `wof_hud_overlay.js` at required commit `6eeebf4a00ce7751ce9ba6008982e8136d1c4290`.
- `product/alpha/wof_alpha_hud.js` at required commit `d30a071c668c716cd8d9b5d02932808c76c7a3a7`.
- `wof_resume_dispatch_selector.js` WASM-module discovery lineage.
- `parallel/RENDER_AUTHORITY_V2/wof_render_authority_capture_worker.js` from its `204fda7f...` origin through its later W3 candidate-timeline revisions.
- GEO P1/P2/P3 player-object structural closure.
- P36/P40 terminal authority and source-surface contract, used only as the qualification rule/cross-check.

No historical commit-message hit for `CPS1` or `drawArrays` identified a native submit export; `submit` history before P36/P42 contained no renderer-submit implementation. No historical `rendererSourceProof` commit hit exists. `glue` commit-message search returned no candidate.

## Candidate ledger

### C0 — qualifying historical direct source

Classification: **DIRECT_SOURCE_CANDIDATE: NONE FOUND**

No retained historical blob provides a source-traced/exported gstyphoon/CPS1 per-object displayed-submit producer with native marker identity + actor generation + native 384x224 coordinates + displayed submission identity.

---

### C1 — obsolete 2D game-canvas probe / `I_n3jTY`

Classification: **NOT_ELIGIBLE**

- commit: `a41f59de1b95c09c15931c3f98c073cfe9484107`
- path: `wof_canvas_probe.js`
- blob: `edfc5416795a9b8a996a1dfba49ac9da90576278`
- symbols: `window.I_n3jTY`, `window.I_KkacD`, `window.I_QKG4Q.Pad`, `window.I_Aj3M8`, `window.WOFCANVAS`
- actual semantics: wraps an obfuscated function labeled by the probe as a render function, then draws an Alpha HUD on a 2D canvas using `Pad.X/Pad.Y`. It does not inspect or export the wrapped function arguments as CPS1 objects.
- displayed frame/submission: only a post-call wrapper boundary; no frame/submission id and no native object submission.
- native 384x224 x/y: **no**; uses `Pad.X/Pad.Y` and a source canvas.
- binds `1P/2P/3P + ↓`: **no**.
- binds actor generation: **no**.
- disqualifier: commit `1ab83add837cda7c7bd752d057be8069f678fae0` explicitly replaced this path to target the real WebGL game canvas, so `I_n3jTY` cannot be treated as recovered renderer authority.

### C2 — real game WebGL frame/RAF wrapper

Classification: **CORRELATION_ONLY**

- commit: `1ab83add837cda7c7bd752d057be8069f678fae0`
- path: `wof_canvas_probe.js`
- blob: `565505043c8bfa2e3b58657b46bbe1101abf2b61`
- symbols: `window.I_GF1TC`, `window.I_fdC8Q`, `window.I_b1EdF` (`frameTarget`), `window.I_FHW46` (`rafTarget`), `wrappedFrame`, `wrappedRaf`
- actual semantics: identifies the real WebGL canvas/context and wraps two page-side frame/queued-frame functions. The wrapper draws Alpha-owned geometry after the original call. It snapshots/restores GL state but does not inspect a native CPS1 object submit or expose gstyphoon renderer data.
- displayed frame/submission: **frame-boundary correlation only**; no explicit displayedFrameId/submissionId and no per-object callback.
- native 384x224 x/y: **no**; uses WebGL drawing-buffer dimensions.
- binds `1P/2P/3P + ↓`: **no**.
- binds actor generation: **no**.
- useful handoff value: historical names `I_b1EdF` and `I_FHW46` prove that a page-side frame boundary was once discoverable. They are not a native renderer pointer/export.

### C3 — generic final WebGL `drawArrays` hook

Classification: **CORRELATION_ONLY**

- commit: `60e7bd3581156b878a3246964e2b984e87d4b69c`
- path: `wof_canvas_hud.js`
- blob: `909f89ceb7456dad580b5b44a531736a5f8b821d`
- symbols: `origDraw`, `wrapped(mode,first,count)`, `gl.drawArrays`, `drawHud`
- actual semantics: wraps the game WebGL context's generic `drawArrays`; after the original draw returns, `count===6` can trigger an Alpha HUD draw. The code preserves GL program/buffer/texture/viewport/attrib state for its own overlay.
- displayed frame/submission: **yes only at generic WebGL-call level**; it proves a GL draw happened, not which CPS1 object produced it. It has no submission sequence/id.
- native 384x224 x/y: **no**; overlay uses drawing-buffer coordinates.
- binds `1P/2P/3P + ↓`: **no**.
- binds actor generation: **no**.
- disqualifier: the hook never snapshots the original draw's CPU-side object payload, native object pointer, tile/object queue entry, or marker identity. A six-vertex WebGL draw is not equivalent to a CPS1 per-object submit.

### C4 — HUDANCHOR generic WebGL hook/viewport proof

Classification: **CORRELATION_ONLY**

- commit: `441ca4a207881925ff08c93bb842d56a8754a274`
- path: `parallel/HUDANCHOR_PROOF/wof_hudanchor_gl.js`
- blob: `adcebcdad7baec098a2ead0b2e7331d93cffab03`
- symbol: `createHudAnchorGl({gl,canvas,getPoints})`
- actual semantics: wraps `gl.drawArrays`, records hook count/current viewport, and paints Alpha-owned labels supplied by external `getPoints()`. The `nativeDraw` symbol refers to the browser WebGL prototype method, not a CPS1 native renderer function.
- displayed frame/submission: generic WebGL-call correlation only; no native object or submission identity.
- native 384x224 x/y: **no source**; coordinates come from external `getPoints()` and are mapped to drawing-buffer space.
- binds `1P/2P/3P + ↓`: **no native binding**.
- binds actor generation: **no**.
- disqualifier: it is an overlay proof renderer, not an observer/export of game object submission.

### C5 — required historical native-label pixel tracker

Classification: **CORRELATION_ONLY**

- commit: `6eeebf4a00ce7751ce9ba6008982e8136d1c4290`
- path: `wof_hud_overlay.js`
- blob: `b0346c0fae756edc5757dd416484c3a3041b0f38`
- symbols: `scanCanvas`, `scanCtx.drawImage`, `getImageData`, `playerColor`, `buildMask`, `components`, `textCandidates`, `arrowBelow`, `candidateScore`, `detect`, `acceptHit`, `updateTracking`, `positionAnchor`
- actual semantics: downsamples/copies the rendered game canvas into a fixed `384x224` scan canvas, color-segments pixels, finds connected components, scores the native `1P/2P/3P` text + downward-arrow visual cluster, and temporally tracks it through motion/jumps.
- displayed frame/submission: **displayed pixels only**; no renderer submission identity or source pointer.
- native 384x224 x/y: **yes as image-derived pixel coordinates**, not as native renderer object-submit x/y.
- binds `1P/2P/3P + ↓`: **visually/correlationally yes**, by color/shape geometry.
- binds actor generation: **no**.
- disqualifier: pixel/native-label tracking is explicitly not renderer authority. It is valuable only as a historical correlation oracle.

### C6 — required screen-space P1 warning bridge

Classification: **CORRELATION_ONLY**

- commit: `d30a071c668c716cd8d9b5d02932808c76c7a3a7`
- path: `product/alpha/wof_alpha_hud.js`
- blob: `00d1fabd7c01c8869926d90bb0e149042153fd8a`
- symbols: `bindP1HeadTrackerAuthority`, `setP1HeadTracker`, `p1TrackerStatus`, `drawP1Tracker`, `drawP1HeadWarningFromTracker`
- actual semantics: consumes an already-existing screen-space P1 tracker `(x,y)` under `authorityKey/runtimeEpoch`, maps it through the canvas client rect into drawing-buffer coordinates, and draws the P1 danger HUD near that tracker.
- displayed frame/submission: **no native submit**; only HUD render timing.
- native 384x224 x/y: **no**; consumed coordinates are screen/client-space tracker coordinates and are remapped into drawing-buffer space.
- binds `1P/2P/3P + ↓`: P1 only through external tracker; no native marker object identity.
- binds actor generation: **no**.
- disqualifier: this is a consumer of tracker coordinates, not a renderer-source producer.

### C7 — obfuscated Emscripten/WASM Module resolver

Classification: **STRUCTURAL_ONLY**

- commit: `50081ce24235bcde39609c84eec50c1a648de6ca`
- path: `wof_resume_dispatch_selector.js`
- blob: `39d67f3b0914ef75aa1d3fac55a0d845e684da2c`
- symbols: `ensureWasmModule`, `_0x515056`, `__WOF_MODULE_GLOBAL_KEY`, `HEAPU8`, `HEAPU32`
- actual semantics: scans Worker globals for an Emscripten-like Module whose `HEAPU8`/`HEAPU32` share a buffer, aliases it to `_0x515056`, then continues CPS RAM/ROM reverse engineering. The retained frontier records game object `+4/+8` as 16.16 world X/Y.
- displayed frame/submission: **no**.
- native 384x224 x/y: **no**; `+4/+8` are game object/world coordinates, not proven displayed native marker-submit coordinates.
- binds `1P/2P/3P + ↓`: can reach player/game structures, but not native marker submissions.
- binds actor generation: **no renderer-side generation binding**.
- disqualifier: a HEAP/Module handle is not an exported renderer pointer. No historical `Module`/`Module.asm` renderer-submit export was recovered from this path.

### C8 — W3 structural renderer-object candidate scanner / timeline

Classification: **STRUCTURAL_ONLY**

Origin revision:
- commit: `204fda7f65a85f53a51fac6d1c9a00715ad59bee`
- path: `parallel/RENDER_AUTHORITY_V2/wof_render_authority_capture_worker.js`
- blob: `33cffbf66f77c13cad9d29d2850c261f5a959498`

Strongest historical candidate-timeline revision inspected:
- commit: `5ee09a7230a50c775496c560b91ce200f7d4a7f6`
- same path
- blob: `e77cce4aebba1955d1bd4ee1166f41bae8222703`
- symbols: `moduleOf`, `decodeEntries`, `structuralScore`, `topStructuralRegions`, `snapshotRegion`, `surface`, `makeActors`, `G.WOFRENDERAUTHV2`
- actual semantics: scans arbitrary WASM HEAP regions for repeated 8-byte rows interpreted as `xWord/yWord/tileWord/attrWord`; ranks them by structural plausibility, records raw hex and a bounded timeline, and separately samples known CPS player/enemy records.
- authority label in code: `UNVERIFIED_CANDIDATE_ONLY`.
- displayed frame/submission: **no**; sampling is timer/HEAP based, not called from the real renderer submit.
- native 384x224 x/y: **not proven**. It masks candidate words into `x9/y9`; the same state explicitly sets `canonicalNativeContract:{width:384,height:224,accepted:false,reason:'exact renderer/object source not yet proven'}`.
- binds `1P/2P/3P + ↓`: **no marker binding**. Structural regions are not causally linked to marker objects.
- binds actor generation: **yes only on the separate CPS RAM actor feed** via `makeActors()` lifecycle signatures. There is no causal edge from a structural candidate row to that actor generation.
- disqualifier: this is exactly the structural-HEAP class that P36/P40 forbid from masquerading as renderer authority.

### C9 — CPS player-object identity / world geometry

Classification: **STRUCTURAL_ONLY**

- commit: `25fde12c57a7d0f51797978611607d5624b2a3ac`
- path: `parallel/GEO/P2_P3_STRUCTURE_CLOSURE.md`
- blob: `9213d87710029430231b576320dca41d8a748fe9`
- symbols/data: `PLAYER_P1=0xFFBE1C`, `PLAYER_STRIDE=0xE0`, P1/P2/P3 records, common player table, relative fields `+0x04/+0x0B/+0x08/...`
- actual semantics: establishes P1/P2/P3 as three instances of one CPS player-object structure and confirms game-world/player geometry fields.
- displayed frame/submission: **no**.
- native 384x224 x/y: **no**; this is game-state/world geometry, not the displayed marker renderer-submit coordinate stream.
- binds `1P/2P/3P + ↓`: binds player records, **not** the native label/down-arrow renderer object.
- binds actor generation: structural player identity exists, but no displayed-renderer generation association.
- disqualifier: source is CPS RAM/ROM structure evidence, not renderer submit.

## Requested capability matrix

| Candidate | Class | actual displayed per-object submit | displayed frame/submission id | native 384x224 submit x/y | native 1P/2P/3P + ↓ identity | actor generation on same causal edge |
|---|---|---:|---:|---:|---:|---:|
| C1 `I_n3jTY` 2D probe | NOT_ELIGIBLE | no | no | no | no | no |
| C2 `I_b1EdF/I_FHW46` frame wrapper | CORRELATION_ONLY | no | no | no | no | no |
| C3 generic `gl.drawArrays` hook | CORRELATION_ONLY | no | no | no | no | no |
| C4 HUDANCHOR GL hook | CORRELATION_ONLY | no | no | no | no | no |
| C5 384x224 pixel native-label tracker | CORRELATION_ONLY | no | no | image pixels only | visual only | no |
| C6 screen-space P1 tracker bridge | CORRELATION_ONLY | no | no | no | external P1 only | no |
| C7 Emscripten Module/HEAP resolver | STRUCTURAL_ONLY | no | no | no | no | no |
| C8 W3 HEAP x/y/tile/attr candidate timeline | STRUCTURAL_ONLY | no | no | unverified words only | no | separate actor feed only |
| C9 CPS P1/P2/P3 player-object structure | STRUCTURAL_ONLY | no | no | world geometry only | player identity, not marker | no displayed-edge binding |

## Historical conclusions

1. **No old direct source exists in the inspected retained Git history.** There is no recoverable checked-in gstyphoon/CPS1 per-object renderer-submit bridge, exported renderer pointer, source-traced renderer pointer, native object queue export, or WASM/JS glue export that closes the marker-authority chain.
2. The strongest old **display-boundary** evidence is the generic WebGL/frame-hook family (C2/C3/C4). It can correlate time/viewport/draw occurrence, but it never carries CPS1 object semantics.
3. The strongest old **marker-location** evidence is the 384x224 native-label pixel tracker (C5). It can visually identify `1P/2P/3P + ↓`, but its coordinates are image-derived and therefore non-authoritative for P36/P32.
4. The strongest old **object-shaped** evidence is W3 (C8). It has `x/y/tile/attr`-shaped HEAP rows plus a separate actor-generation feed, but no renderer call-site causal edge connecting them.
5. The strongest old **player identity/geometry** evidence is GEO/CPS RAM (C9), but it describes actors/world state rather than the native marker render object.
6. The historical `I_n3jTY` surface (C1) should not be revived: the subsequent `1ab83add...` change explicitly corrected the probe to the real WebGL game canvas.

## Do-not-repeat ledger

Future workers should not reopen these as if they were unexamined renderer-source candidates unless new independent evidence changes their semantics:

- `I_n3jTY` / 2D canvas probe — wrong/obsolete surface.
- `I_b1EdF` / `I_FHW46` — frame timing only.
- generic `gl.drawArrays` / `window.__WOF_GL_HOOK` family — generic GL draw boundary only.
- HUDANCHOR `createHudAnchorGl` — overlay-owned renderer.
- `6eeebf4...` native-label tracker — pixel correlation only.
- `d30a071...` P1 tracker HUD bridge — coordinate consumer only.
- `_0x515056` / `HEAPU8` / `HEAPU32` discovery — Module/HEAP access only.
- `WOFRENDERAUTHV2` structural candidate scanner — unverified HEAP structure only.
- GEO player-object records — world/player state only.

A future direct-source claim needs **new evidence from the actual running gstyphoon renderer implementation or its real exported/source-traced call site**, not a reclassification of the items above.

## Minimal future handoff

Because no historical direct source was found, there is no old implementation to restore or adapt. The minimum useful handoff is therefore a negative constraint:

```text
Do not recover authority from historical pixels, generic WebGL hooks, W3 HEAP candidates,
or CPS actor coordinates.
Only accept a newly observed actual gstyphoon/CPS1 per-object displayed-submit call site/export
that exposes (or can source-trace without guessing) object identity/payload + native x/y + frame/submission
sequence, and that can be explicitly associated with P1/P2/P3 actor generation.
```

This P44 result does not alter the current blocker. It removes historical-repository archaeology as an unsearched escape hatch for `NATIVE_PLAYER_MARKER_DISPLAYED_SUBMIT_SOURCE_EXPORT_NOT_PRESENT`.

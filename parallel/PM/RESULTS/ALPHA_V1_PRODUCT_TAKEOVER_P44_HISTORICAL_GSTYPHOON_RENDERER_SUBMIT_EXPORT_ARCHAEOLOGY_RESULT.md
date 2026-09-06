# P44 Historical GStyphoon Renderer Submit Export Archaeology — Result

State: **COMPLETE**

P44 completed the historical-source archaeology lane. No qualifying historical direct gstyphoon/CPS1 per-object displayed-submit source/export was found in the inspected reachable Git history.

## Exact result

- tested archaeology commit: `a08c98f144af8f7dc47034165086fca91557a626`
- report: `parallel/RENDER_AUTHORITY_V2/HISTORICAL_GSTYPHOON_RENDERER_SUBMIT_EXPORT_ARCHAEOLOGY_P44.md`
- report blob: `aef3b59efa88a81874ac662d776df911fabbf198`
- classification: `DIRECT_SOURCE_CANDIDATE: NONE FOUND`
- current blocker preserved: `NATIVE_PLAYER_MARKER_DISPLAYED_SUBMIT_SOURCE_EXPORT_NOT_PRESENT`

## Strongest historical non-qualifying candidates

- `1ab83add837cda7c7bd752d057be8069f678fae0` / `wof_canvas_probe.js` / blob `565505043c8bfa2e3b58657b46bbe1101abf2b61`: real game WebGL frame/RAF wrapper (`I_b1EdF`, `I_FHW46`) — `CORRELATION_ONLY`.
- `60e7bd3581156b878a3246964e2b984e87d4b69c` / `wof_canvas_hud.js` / blob `909f89ceb7456dad580b5b44a531736a5f8b821d`: generic `gl.drawArrays` hook — `CORRELATION_ONLY`.
- `6eeebf4a00ce7751ce9ba6008982e8136d1c4290` / `wof_hud_overlay.js` / blob `b0346c0fae756edc5757dd416484c3a3041b0f38`: 384x224 native-label pixel tracker — `CORRELATION_ONLY`.
- `d30a071c668c716cd8d9b5d02932808c76c7a3a7` / `product/alpha/wof_alpha_hud.js` / blob `00d1fabd7c01c8869926d90bb0e149042153fd8a`: screen-space P1 tracker consumer — `CORRELATION_ONLY`.
- `50081ce24235bcde39609c84eec50c1a648de6ca` / `wof_resume_dispatch_selector.js` / blob `39d67f3b0914ef75aa1d3fac55a0d845e684da2c`: Emscripten Module/HEAP resolver — `STRUCTURAL_ONLY`.
- `5ee09a7230a50c775496c560b91ce200f7d4a7f6` / `parallel/RENDER_AUTHORITY_V2/wof_render_authority_capture_worker.js` / blob `e77cce4aebba1955d1bd4ee1166f41bae8222703`: W3 `x/y/tile/attr` HEAP candidate timeline plus separate actor-generation feed — `STRUCTURAL_ONLY`.
- `25fde12c57a7d0f51797978611607d5624b2a3ac` / `parallel/GEO/P2_P3_STRUCTURE_CLOSURE.md` / blob `9213d87710029430231b576320dca41d8a748fe9`: CPS player-object identity/world geometry — `STRUCTURAL_ONLY`.
- `a41f59de1b95c09c15931c3f98c073cfe9484107` / `wof_canvas_probe.js` / blob `edfc5416795a9b8a996a1dfba49ac9da90576278`: obsolete 2D `I_n3jTY` probe — `NOT_ELIGIBLE`.

None closes the required causal chain:

`actual displayed CPS1 per-object submit -> native marker identity/cluster -> native 384x224 x/y -> displayed frame/submission identity -> explicit P1/P2/P3 actor generation`.

## Coverage and checks

Repository history was swept across `gstyphoon`, `renderer`, `WebGL`, `WASM`, `object`, `sprite`, `pointer`, `export`, `queue`, `frame`, `CPS1`, `drawArrays`, `submit`, `source-traced`, `rendererSourceProof`, and `glue`, then exact historical blobs/path lineages were fresh-read for the strongest candidates.

Fresh candidate readback confirmed the report blob and both required historical commits (`6eeebf4...`, `d30a071...`). The tested candidate commit changes only the P44 archaeology report. No real WOF run was performed because P44 is historical-source archaeology only.

## Boundaries preserved

P42/P43 ownership was not modified. No `rendererSourceProof` was created. No promotion or alpha-live movement occurred. No RAM writes or input injection occurred.

## PM handoff

Treat historical-repository direct-source recovery as exhausted unless genuinely new historical evidence appears. A future qualifying source must come from newly observed actual gstyphoon renderer implementation/export/call-site evidence; do not relabel the historical pixel, generic WebGL, W3 structural HEAP, or CPS world-coordinate paths as renderer authority.

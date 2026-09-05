# Alpha V1 P36 — Native Marker Renderer Submit Source Trace — RESULT

State: **COMPLETE**

## Verdict

P36 now has a durable, exact-byte-tested, zero-click, read-only renderer-submit source-trace/proof producer. It accepts only an explicit direct/source-traced renderer authority surface, preserves exact P1/P2/P3 actor generation and native 384x224 coordinates, binds runtimeEpoch / rendererEpoch / authorityKey, and feeds the existing P32 qualifier without weakening P29/P32 semantics.

This result does **not** claim that a real WOF native marker has already passed live authority. The task did not run the real game.

## Durable tested candidate

- tested commit: `162e50b6c65fd1d3901ad694854563b686b2ce22`
- tested tree: `5d059ad40b0bdb806a441e19441d28ee17b71265`
- implementation commit: `162e50b6c65fd1d3901ad694854563b686b2ce22`

Exact candidate blobs:

- `parallel/RENDER_AUTHORITY_V2/native_marker_renderer_submit_source_trace.py` — `98cccbf245cf20e21a91c0a135791bce369acd77`
- `parallel/RENDER_AUTHORITY_V2/native_marker_renderer_submit_source_trace_worker.js` — `c188d1b34fe45c295a24a1dd012a9b671e604bfb`
- `parallel/RENDER_AUTHORITY_V2/test_native_marker_renderer_submit_source_trace.py` — `c06cf688c1fddc4c2c6d056982af9f453865ebf9`
- `parallel/RENDER_AUTHORITY_V2/test_native_marker_renderer_submit_source_trace_worker.mjs` — `2b3eb45873db9335898c140c22be05058d7d57bb`
- `parallel/RENDER_AUTHORITY_V2/NATIVE_MARKER_RENDERER_SUBMIT_SOURCE_TRACE.md` — `7eeb87540a4823f1fb386109904af4f1683ca700`

## What is implemented

The bounded Worker-side observer auto-discovers only an explicit P36 source surface on `self`, `Module`, or `Module.asm`. A valid source must truthfully declare one of `SOURCE_TRACED_POINTER`, `DIRECT_RENDER_HOOK`, or `EXPORTED_RENDERER_POINTER`, a displayed-frame causal link, native renderer 384x224 coordinate authority, an exact source trace/hook identity, zero-click operation, and the read-only safety contract.

The producer adapter accepts exact renderer-submit events only when runtimeEpoch, rendererEpoch and authorityKey match and actor association is explicit, generation-bound and unambiguous. It selects P1/P2/P3 only by exact `(player, generation)` association, then builds the existing `wof-native-player-marker-direct-evidence-v1` contract and invokes the unchanged P32 qualifier.

No structural HEAP scan, screenshot, OCR, template, world projection, nearest-object selection, list-order selection, arrival timing or guessed offset can mint marker authority. Missing or ambiguous direct source remains fail-closed under `NATIVE_PLAYER_MARKER_DIRECT_RENDERER_CAUSAL_EDGE_NOT_CHECKED_IN`; stale/mixed authority is rejected.

## Focused self-check

- Python P36 producer + exact P32 qualifier regression: **PASS — 15/15**.
  - exact P32 qualifier blob: `dd1cf633193312d65bc241b86eb23dace0656508`
  - exact P32 test blob: `1131c5c24b5558d5419b90cec24fa82b34219fef`
- Node bounded source-observer self-test: **PASS**.
- Python `py_compile`: **PASS**.
- Fresh candidate blob readback: **PASS** for all five candidate files.
- Real WOF bounded live renderer-source verification: **NOT RUN**, because P36 explicitly forbids a real game run.

## Product-proof separation

Repo-side implementation proof is complete: the exact durable bytes implement the required zero-click source-trace producer and preserve the existing fail-closed qualifier.

Live native-marker authority remains unproven. One later bounded zero-click real-WOF verification must establish that the runtime exposes one unique actual displayed renderer-submit source and that its direct marker events satisfy the unchanged P32 qualifier. This later run must not require avatar clicks, player selection or a manual seed.

## Scope and safety

- read-only: `true`
- game RAM writes: `0`
- input injection: `false`
- Owner/player manual selection: `false`
- manual seed: `false`
- no real game run
- no alpha-live movement
- no P29 acceptance change
- no P37 ownership change
- no P38 candidate-materialization change

## Next action

PM should integrate tested commit `162e50b6c65fd1d3901ad694854563b686b2ce22` and schedule one bounded zero-click live verification. If the exact renderer source is absent, stale or ambiguous, P36 must remain fail-closed; structural or visual evidence must not be promoted.

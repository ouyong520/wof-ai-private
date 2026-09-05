# Native Player Marker Renderer Anchor Qualification (P32)

## Scope

This seam qualifies a native WOF `1P` / `2P` / `3P` + down-arrow marker only after a direct displayed-frame renderer/object submission has already been captured. It does **not** discover authority from structural HEAP rows, screenshot/OCR/template coordinates, world projection, object proximity, row order, or timing.

The maintained P9 consumer is intentionally unchanged. P32 only prepares an upstream marker authority/anchor proof contract. P30 owns P9/P1/P16 staging and binding readiness; P31 owns Page/Worker/WASM association; P29 analyzer criteria remain unchanged.

## Qualification contract

`native_player_marker_anchor_qualification.py` accepts `wof-native-player-marker-direct-evidence-v1` and requires all of the following before it emits a `wof-renderer-source-proof-v1`-compatible proof candidate:

- exact `runtimeEpoch`, `rendererEpoch`, and `authorityKey` binding at capture and every direct sample;
- native renderer dimensions exactly `384 x 224`;
- source derivation explicitly one of `SOURCE_TRACED_POINTER`, `DIRECT_RENDER_HOOK`, or `EXPORTED_RENDERER_POINTER`, with `guessed=false`;
- explicit displayed-frame causal link and a concrete source trace;
- screenshot/OCR/template/world-projection coordinates explicitly excluded from authority;
- at least three distinct direct displayed-frame submissions with strictly increasing renderer frame generation;
- exactly one marker for the requested `P1` / `P2` / `P3` actor generation in each sample;
- explicit, non-ambiguous, generation-bound actor association;
- explicit stable cluster key and explicit non-guessed cluster join;
- exactly one semantically identified `DOWN_ARROW` member carrying the native renderer anchor point;
- deterministic member identity independent of input row order.

Any missing/duplicate/ambiguous/stale/mixed condition returns `REJECTED` with `rendererSourceProof=null`.

## Multi-object rule

A label+arrow marker may contain multiple renderer objects, but membership must arrive with an explicit stable `clusterKey` and member identity from the direct renderer source. The qualifier canonicalizes members by declared semantic role/member key only after the explicit join has been established. It never uses array order, nearest-distance, screen geometry, or timing to decide membership or player identity.

The down-arrow coordinate is accepted only from the member explicitly identified by the renderer evidence as `DOWN_ARROW`; the qualifier does not infer an arrow tip from a screenshot or body/head geometry.

## Focused regression status

`test_native_player_marker_anchor_qualification.py` is a contract regression only. Its direct-source rows are fixtures that exercise the repo-side validator; they are **not** live WOF evidence and must never be cited as W3 PASS or real marker proof. Regressions cover exact-generation qualification, row-order-independent deterministic clustering, duplicate ambiguity rejection, stale epoch/key/generation rejection, visual/structural-only rejection, and no-proof behavior when displayed-frame causality is absent.

## Remaining authoritative live edge

Current checked-in W3 capture code exposes actor lifecycle plus structural HEAP candidates and labels them `UNVERIFIED_CANDIDATE_ONLY`; no checked-in source-traced renderer submit hook/exported renderer pointer connects the native player marker object/cluster to the displayed CPS1 frame. Therefore this P32 seam cannot prove the real marker offline.

The missing edge is:

`displayed CPS1 renderer/object submission -> exact native player-marker object/cluster identity + explicit P1/P2/P3 generation association`

A later bounded Owner live run must supply that direct source evidence through a legitimate renderer hook/exported pointer/source-traced pointer. Until then, the qualifier remains fail-closed. No structural candidate is promoted, no synthetic live `rendererSourceProof` is created, and no W3 PASS is claimed.

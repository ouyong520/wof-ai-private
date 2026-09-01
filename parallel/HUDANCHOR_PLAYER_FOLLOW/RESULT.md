# HUDANCHOR Player-Follow Bounds Fail-Closed Fix Result

Stage: `HUDANCHOR_PLAYER_FOLLOW_BOUNDS_FIX_V1`

Status: **HUDANCHOR PLAYER-FOLLOW BOUNDS FIX READY — READY FOR FRESH QA**

## Fix delivered

Updated:

- `parallel/HUDANCHOR_PLAYER_FOLLOW/src/player_follow_reference.js`
- `parallel/HUDANCHOR_PLAYER_FOLLOW/test/bounds_regression.js`

`PlayerAnchorResolver.resolve()` now rejects a finite player-head anchor before native -> drawing-buffer mapping when the final resolved anchor is outside the native viewport:

- `anchorXNative < 0`;
- `anchorXNative >= nativeWidth`;
- `anchorYNative < 0`;
- `anchorYNative >= nativeHeight`.

The existing body/player projection validation through `validationBounds` is preserved unchanged.

An invalid anchor therefore returns `PROJECTION_OUT_OF_BOUNDS`, routes immediately to fixed-HUD fallback, clears follow/smoothing state, and never reaches the warning-rectangle edge clamp.

The final warning rectangle is still safely clamped only after a valid anchor has been resolved, preserving legitimate near-edge anchored rendering.

## Regression coverage

Added targeted synthetic regression:

`parallel/HUDANCHOR_PLAYER_FOLLOW/test/bounds_regression.js`

Coverage:

1. `anchorXNative < 0` -> fixed fallback;
2. `anchorXNative >= native width` -> fixed fallback;
3. `anchorYNative < 0` -> fixed fallback;
4. `anchorYNative >= native height` -> fixed fallback;
5. body/player reference remains in bounds while derived head anchor is out of bounds -> fixed fallback;
6. valid anchor near viewport edge remains anchored and only final rectangle clamps;
7. invalid anchor after a valid frame clears smoothing state and never reuses the old coordinate;
8. retarget during an invalid-anchor frame removes the old player cue immediately and falls back for the new target.

Targeted result:

```json
{"status":"PASS","passed":8,"total":8,"fixture":"SYNTHETIC_BOUNDS_ONLY_NOT_BROWSER_PROOF"}
```

Then the existing full player-follow synthetic regression was run unchanged after the targeted suite.

Full regression result:

```json
{"status":"PASS","passed":15,"total":15,"fixture":"SYNTHETIC_ONLY_NOT_BROWSER_PROOF"}
```

Preserved coverage includes movement, camera compensation, depth/jump, P1/P2/P3 routing, immediate retarget invalidation, resize/fullscreen/DPR remap, stale/epoch fail-closed behavior, aggregation, disappearance/no coordinate reuse, lifecycle reset, camera discontinuity reset, and viewport rectangle clamping.

## Commit / blob evidence

Implementation commit:

- `d43b0711db33532e15d90606f18a632597ea95bf`

Regression commit:

- `418fc7c7e5aa64c7e7bb5b8a5e31743472f6ff91`

Executed source/test blobs were verified against committed GitHub blobs:

- fixed source: `4beb7f8d4c9f815e125ed795aca536f02562f5d1`;
- bounds regression: `d5798e3470625d440092aa00a05142157f99799b`;
- unchanged synthetic fixture: `79e42e675d371ec91715116227fecf0ed3c27d97`;
- unchanged full synthetic regression: `b7d56a74ef520bccb47055bc59558da6dfcb6139`.

## Product / safety semantics preserved

Authoritative behavior remains:

`怪物锁定谁 -> 在被锁定角色 P1/P2/P3 头顶显示提示 -> 跟随角色 -> 不漂移 -> 换锁立即切换`

Preserved:

- read-only presentation semantics;
- no RAM writes;
- no input injection;
- no Worker replacement/wrap;
- no new danger semantics;
- no Browser/projection constant guessing;
- no `product/alpha/**`, PYLAUNCH, Recorder, Prospective, Browser Fleet, Transport, or HUDANCHOR proof-lane changes.

No real Browser/WOF run was required or used for this repository-side fail-closed fix.

## Stop condition

**HUDANCHOR PLAYER-FOLLOW BOUNDS FIX READY — READY FOR FRESH QA**

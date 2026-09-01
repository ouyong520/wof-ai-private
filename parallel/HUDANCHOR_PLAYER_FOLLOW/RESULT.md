# HUDANCHOR Player-Follow Reference Implementation Result

Stage: `HUDANCHOR_PLAYER_FOLLOW_REFERENCE_IMPL_V1`

Status: **HUDANCHOR PLAYER-FOLLOW REFERENCE IMPLEMENTATION READY**

## Delivered

Implemented under the only permitted implementation lane:

- `parallel/HUDANCHOR_PLAYER_FOLLOW/src/player_follow_reference.js`
  - `PlayerAnchorResolver`
  - `TargetLockIndicatorRouter`
  - `PlayerFollowStateMachine`
  - `AnchoredWarningRenderer`
  - drawing-buffer -> WebGL clip conversion
- `parallel/HUDANCHOR_PLAYER_FOLLOW/fixtures/synthetic_projection.js`
  - explicitly synthetic, arbitrary projection fixture
  - explicitly not Browser proof
- `parallel/HUDANCHOR_PLAYER_FOLLOW/test/synthetic_regression.js`
- `parallel/HUDANCHOR_PLAYER_FOLLOW/package.json`
- `parallel/HUDANCHOR_PLAYER_FOLLOW/README.md`

## Product semantic implemented

The implementation follows the corrected authoritative target-lock HUD requirement:

`怪物锁定谁 -> 在被锁定角色 P1/P2/P3 头顶显示提示 -> 跟随该角色 -> 不漂移 -> 换锁时立即切到新角色`

It does not attach the marker to the enemy and does not add/modify any attack-prediction rule.

## Core invariants

### Anchor resolver

- consumes current P1/P2/P3 `x/y/z` plus injected camera/projection state and live drawing-buffer/content-rect state;
- returns drawing-buffer anchor coordinates plus validity, freshness, confidence and reason;
- projection implementation is versioned/injected behind `projectNative(...)`;
- stale player/projection/drawing-buffer state fails closed;
- epoch mismatch fails closed;
- invalid viewport/non-finite/out-of-bounds projection fails closed;
- no DOM/page coordinate is used as the production anchor plane.

### Target-lock routing

- target player is part of target-bound display identity;
- a source retarget immediately invalidates the previous player's hold even when a release hold is otherwise enabled;
- P1 -> P2 -> P3 retarget therefore cannot leave a stale old-player indicator;
- multiple warning payloads targeting one player are aggregated without creating new danger semantics.

### Renderer / non-drift state

- direct WebGL/drawing-buffer coordinate contract;
- warning rectangle is clamped to current game-content viewport;
- resize/fullscreen remaps from current drawing-buffer state;
- DPR is not treated as coordinate truth; live drawing-buffer mapping is authoritative;
- smoothing defaults off;
- optional smoothing resets on lifecycle/respawn replacement, projection version change, mapping change, camera discontinuity and invalidation;
- player disappearance or unrouting clears follow state immediately;
- anchor failure routes the warning to fixed-HUD fallback and never reuses a last-known player coordinate.

## Synthetic regression

Executed with Node.js `v22.16.0`:

```text
npm test
```

Result:

```json
{"status":"PASS","passed":15,"total":15,"fixture":"SYNTHETIC_ONLY_NOT_BROWSER_PROOF"}
```

Coverage:

1. horizontal movement;
2. camera scroll compensation;
3. depth/lane movement;
4. jump/Z movement;
5. P1/P2/P3 independent routing;
6. retarget P1 -> P2 -> P3 with immediate old hold invalidation;
7. resize/fullscreen remap;
8. DPR-only non-drift;
9. stale projection -> fixed fallback;
10. epoch mismatch -> fail closed;
11. multi-warning aggregation;
12. player disappearance -> no last-coordinate reuse;
13. respawn/lifecycle replacement -> reset;
14. camera discontinuity -> reset;
15. drawing-buffer viewport clamp.

The executed local files were checked against the committed GitHub blob SHAs:

- source: `47a03e1ce459e153ba2b5db42ba10a4d0d746490`
- fixture: `79e42e675d371ec91715116227fecf0ed3c27d97`
- regression: `b7d56a74ef520bccb47055bc59558da6dfcb6139`
- package: `0d040a37b3a44293a80d3289708d01f0e14e93ef`

## Projection truth boundary

No real WOF Browser projection constant was guessed or hardcoded as proved.

The fixture contains arbitrary values and is explicitly labelled synthetic.

The reference architecture accepts the eventual externally proved Browser transform through `projectionState.projectNative(...)`, with native viewport/version/epoch/camera metadata supplied alongside it.

## Remaining work allowed by this stage

Only integration of externally proved real Browser facts/wiring remains:

1. inject the proved Browser player/camera projection through `projectNative(...)`;
2. inject the proved native/drawing-buffer content mapping;
3. wire the plan into the existing direct-WebGL/fixed-HUD draw adapter.

No architectural redesign, new danger semantics, broad capture or guessed constants are required by this reference lane.

## Safety / write-scope audit

Preserved:

- read-only presentation semantics;
- no RAM writes;
- no gameplay input;
- no Worker replacement;
- no `product/alpha/**` modification;
- no PYLAUNCH modification;
- no Recorder modification;
- no Prospective modification;
- no Browser Fleet modification.

Implementation writes were confined to `parallel/HUDANCHOR_PLAYER_FOLLOW/**`; the only additional write is the mandatory PM stage claim.

## Stop condition

**HUDANCHOR PLAYER-FOLLOW REFERENCE IMPLEMENTATION READY**

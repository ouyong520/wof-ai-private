# HUDANCHOR Player-Follow Reference Implementation

Status: **REFERENCE IMPLEMENTATION READY (synthetic projection fixture only)**

This lane implements the corrected product presentation semantic:

`怪物锁定谁 -> 在被锁定角色 P1/P2/P3 头顶显示提示 -> 跟随该角色 -> 不漂移 -> 换锁时立即切到新角色`

It does **not** change danger/prediction semantics and does not modify `product/alpha/**`.

## Modules

### `PlayerAnchorResolver`

`src/player_follow_reference.js`

Input contract:

- player identity: `P1 | P2 | P3`;
- current player state: `x/y/z`, lifecycle id, sample time, epoch, presence;
- injected projection state: version/source, camera state, native viewport, freshness/epoch and `projectNative(...)`;
- live drawing-buffer state: width/height plus current game-content rectangle.

Output contract:

- drawing-buffer anchor `xDb/yDb`;
- projected body reference `bodyXDb/bodyYDb`;
- `ok`, freshness, confidence, projection version and reason;
- mapping/lifecycle metadata used to reset presentation state safely.

Fail-closed conditions include missing/invalid XYZ, stale player/projection/drawing-buffer state, epoch mismatch, invalid viewport, non-finite projection and projection bounds failure.

**No real Browser projection constants are embedded.** The implementation accepts a projection function/config only after another lane proves it.

### `TargetLockIndicatorRouter`

Routes already-existing warning/target state to the currently targeted player.

Rules:

- target identity is presentation identity;
- source retarget P1 -> P2/P3 immediately invalidates any old target-bound hold;
- release/visibility hold may be supplied by the caller, but it can never keep a marker on the old player after retarget;
- multiple threats for one player are aggregated into one player row, preserving the original warning payloads and selecting by caller-provided/existing priority only;
- no danger rule, probability, timing or attack-family inference is created here.

### `PlayerFollowStateMachine`

Presentation-only non-drift state.

Default smoothing is **off**. Optional smoothing is drawing-buffer-only and resets immediately on:

- player lifecycle replacement/respawn;
- projection version change;
- drawing-buffer/content-rect mapping change;
- camera discontinuity;
- anchor invalidation/disappearance.

Players no longer routed in the current frame are removed from follow state, so no old-player marker can survive a retarget.

### `AnchoredWarningRenderer`

Builds a renderer-neutral direct-WebGL plan in **drawing-buffer coordinates**:

- resolves each currently targeted player;
- clamps the warning rectangle inside the live game-content viewport;
- emits drawing-buffer and clip-space rectangles;
- on any anchor failure, emits the warning through the fixed-HUD fallback list instead of reusing a last-known player coordinate;
- `executePlan(plan, adapter)` lets the existing WebGL state-save/draw/state-restore implementation consume the plan without changing this architecture.

DOM/page coordinates are not accepted as the production anchor coordinate plane.

## Projection injection contract

A proved Browser adapter supplies a `projectionState` with this shape:

```js
{
  source: 'proved-browser-source',
  version: 'versioned-proof-id',
  epoch,
  sampleAtMs,
  nativeWidth,
  nativeHeight,
  camera,
  confidence,
  validationBounds,
  projectNative({ player, x, y, z, lifecycleId, camera, projectionState }) {
    return {
      bodyXNative,
      bodyYNative,
      anchorXNative,
      anchorYNative,
      confidence
    };
  }
}
```

The reference implementation deliberately does not assume whether the eventual model is affine, table-driven, renderer-derived or another proved transform. That decision is entirely behind `projectNative(...)`.

## Resize / fullscreen / DPR

Native projection is separated from native->drawing-buffer mapping.

Every resolve uses current:

- drawing-buffer width/height;
- game-content rectangle;
- projection version/epoch.

A resize/fullscreen mapping change creates a new mapping key and resets smoothing. DPR is not itself used as a coordinate source: if DPR changes the drawing buffer, live dimensions/remapping handle it; if DPR changes without changing the drawing-buffer mapping, the anchor does not drift.

## Synthetic regression

Run from this directory:

```text
npm test
```

No dependencies are required beyond Node.js.

Current coverage:

1. horizontal movement;
2. camera scroll compensation;
3. depth/lane movement;
4. jump/Z movement;
5. P1/P2/P3 independent routing;
6. retarget P1 -> P2 -> P3 with old hold invalidation;
7. resize/fullscreen remap;
8. DPR-only non-drift;
9. stale projection -> fixed fallback;
10. epoch mismatch -> fail closed;
11. multi-warning aggregation;
12. player disappearance -> no last-coordinate reuse;
13. respawn/lifecycle replacement reset;
14. camera discontinuity reset;
15. viewport clamp in drawing-buffer space.

`fixtures/synthetic_projection.js` is explicitly marked **SYNTHETIC ONLY / NOT BROWSER PROOF**. Its numbers are arbitrary test values and must never be promoted as real WOF constants.

## Safety / scope

This lane is presentation-only:

- read-only semantics;
- no RAM writes;
- no gameplay input;
- no Worker replacement;
- no `product/alpha/**` changes;
- no PYLAUNCH / Recorder / Prospective / Browser Fleet changes.

## Remaining real-runtime work

Architecture work is complete. The only allowed remaining integration step is to inject:

1. externally proved Browser player/camera projection state/constants via `projectNative(...)`;
2. the externally proved native/drawing-buffer viewport mapping;
3. the existing direct-WebGL/fixed-HUD draw adapter wiring.

If those real Browser facts are not yet proved, keep using fixed HUD in production and keep this reference implementation on the synthetic fixture. Do not guess constants.

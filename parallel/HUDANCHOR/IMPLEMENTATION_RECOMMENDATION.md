# HUDANCHOR Implementation Recommendation

Classification: **NEEDS ONE MINIMAL BROWSER PROOF**

This document is the handoff contract for a later Beta implementation thread. It is not an instruction to modify Alpha.

## 1. Do not change danger semantics

The implementation thread should treat the current Future Danger runtime as authoritative for:

- player state,
- danger level/action,
- source/family/slot metadata,
- target-aware warning generation,
- stale/unsupported fail-closed behavior.

HUDANCHOR adds a presentation resolver only.

Do not change:

- `product/alpha/**`,
- Alpha warning thresholds,
- danger-map/rule semantics,
- family probabilities,
- prediction timing,
- enemy lifecycle logic.

## 2. Recommended modules

### `PlayerAnchorResolver`

Input:

```text
player name + live x/y/z + projection state + drawing-buffer state
```

Output:

```text
valid drawing-buffer warning anchor + confidence/freshness metadata
```

Responsibilities:

- apply the proved native projection,
- apply live camera state,
- apply live Z,
- apply the proved above-character clearance,
- remap after drawing-buffer/viewport changes,
- fail closed if projection is unavailable.

It must not decide whether the player is in danger.

### `AnchoredWarningRenderer`

Reuse the existing direct-WebGL HUD state-save/draw/state-restore pattern.

Responsibilities:

- consume current per-player warning rows,
- ask `PlayerAnchorResolver` for each active player,
- render one compact warning near that player,
- clamp the warning rectangle to the game-content viewport when the anchor itself is valid but close to an edge,
- fall back to the fixed in-game HUD if the resolver is invalid.

### `AnchorProjectionState`

A small immutable/versioned configuration produced from the Browser proof, e.g.:

```js
{
  version: 'wof-browser-anchor-projection-v1',
  cameraAddress: 0xFFxxxx,
  cameraRead: 'u16|s16|s32_16_16',
  nativeWidth:  ...,
  nativeHeight: ...,
  xModel: ...,
  yModel: ...,
  aboveCharacterClearance: ...,
  validationBounds: ...
}
```

Do not fill these constants from guesswork. Populate them only from the minimal Browser proof result.

## 3. Rendering destination

Prefer direct game WebGL over a DOM overlay.

Reason:

- direct WebGL already has a proven drawing-buffer -> clip-space path,
- it stays in the game rendering surface,
- it avoids confusing page/sidebar/browser coordinates with game coordinates,
- resizing can be handled from live GL dimensions.

The older DOM-fixed HUD remains useful as diagnostics/fallback evidence, not the preferred player-anchor plane.

## 4. Warning routing and live retarget

The renderer should be player-row driven.

Pseudocode:

```js
for (const name of ['P1','P2','P3']) {
  const warning = current.players[name];
  if (!isActionableOrVisible(warning)) continue;

  const anchor = anchorResolver.resolve(name, now);
  if (anchor.ok) {
    drawAnchored(name, warning, anchor);
  } else {
    fixedFallback.add(name, warning, anchor.reason);
  }
}
```

Do not store one global `currentTargetAnchor` that can survive a retarget.

### Hold/retarget invariant

The current fixed HUD lineage intentionally has warning hold/grace behavior. The anchored version must refine that behavior:

```text
hold identity includes target player
```

If the danger source retargets from P1 to P2:

1. invalidate the old P1 target-bound anchored hold immediately;
2. resolve current P2 anchor from current P2 state;
3. render the warning on P2 on the next fresh render/update;
4. if P2 anchor is invalid, use fixed fallback — never leave it on P1.

This is required even if the semantic warning itself retains a short release/urgency hold.

## 5. Multiple simultaneous threats

Recommended Beta policy:

- at most one visual warning box per player anchor;
- aggregate multiple danger sources for the same player using the current highest-priority/actionable result;
- P1/P2/P3 may each have a warning simultaneously;
- if boxes collide visually, use a small deterministic vertical stack around each player's own anchor rather than moving a box to another player's anchor.

## 6. Above-character placement

Initial Beta should use:

```text
projected player reference point - proved native clearance
```

not a claimed exact sprite-top.

The proof must choose a clearance that remains visually above the character across ordinary idle/walk/depth/jump states.

A later sprite/frame-descriptor lane can provide exact bounds behind the same resolver API.

## 7. Jump behavior

Do not infer jump from animation names or pixels.

Use the already available live Z state and the proved screen-Y Z transform.

If the Browser proof finds that the visible vertical displacement differs from a simple `-z` relationship, encode the measured model explicitly in `AnchorProjectionState`.

## 8. Camera behavior

Do not use a last-known page offset or a DOM scrolling heuristic.

Read the proved game camera state from the authoritative Browser/CPS source and use it inside the native projection before drawing-buffer scaling.

The camera value should be sampled at the same cadence/frame as practical for the player position. If player/camera samples are from materially different epochs, return `ok:false` and use the fixed HUD for that frame.

## 9. Resize / fullscreen / DPR

Keep game-state/native projection constants separate from presentation scaling.

On each draw:

```text
native anchor
  -> current game-content rectangle in drawing buffer
  -> drawing-buffer x/y
  -> clip space
```

When the drawing buffer or content rectangle changes:

- rebuild only the native->drawing-buffer scale/offset,
- retain the game projection constants,
- reset anchor smoothing,
- suppress anchored placement until the new mapping is valid.

Do not bake a particular desktop CSS size or DPR into game-space constants.

## 10. Staleness and fail-closed thresholds

Exact milliseconds should follow the implementation's current HUD cadence, but the state machine should include:

- warning state stale,
- player state stale,
- camera/projection state stale,
- canvas/GL unavailable,
- viewport unknown during transition.

All of these select the existing fixed in-game HUD.

Do not hide the warning just because anchoring failed.

## 11. Smoothing policy

Only add smoothing if the proved projection still has visible integer/frame jitter.

Allowed:

- small EMA/lerp in drawing-buffer coordinates while player identity and projection version are unchanged.

Reset immediately on:

- retarget,
- respawn/player object disappearance,
- projection invalid->valid transition,
- camera discontinuity,
- drawing-buffer resize/fullscreen transition.

Never let smoothing create a visible delay that defeats real-time retarget.

## 12. Implementation acceptance tests

After the projection proof is committed, the implementation thread should pass:

1. **P1 horizontal:** warning remains above P1 while moving left/right.
2. **Camera scroll:** warning remains attached while background scrolls.
3. **Depth:** warning follows P1 moving to upper/lower floor lanes.
4. **Jump:** warning moves vertically with P1 rather than remaining on the floor anchor.
5. **P2/P3 structure:** if present, manual diagnostic route-to-P2/P3 uses the same projection model.
6. **Live retarget:** real warning retarget moves destination immediately; no old-player inherited hold.
7. **Resize/fullscreen:** anchored HUD remaps or temporarily falls back fixed; it never drifts into page UI.
8. **Projection failure:** deliberately disable camera/projection state and confirm fixed HUD fallback.
9. **No Alpha regression:** no files under `product/alpha/**` changed.

## 13. Exact next step

Run the single bounded Browser proof described in `MINIMAL_BROWSER_PROBE.md`.

If it proves:

- authoritative camera/native X transform,
- floor/depth + Z screen-Y model,
- one stable above-character clearance,
- current drawing-buffer mapping,

then change this lane classification to **IMPLEMENTATION READY** and hand these documents to a Beta implementation thread.

If it fails, do not start broad capture. Preserve the probe result and narrow only the failed transform component.

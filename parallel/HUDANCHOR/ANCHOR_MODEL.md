# HUDANCHOR Anchor Model

Status: **candidate model; Browser projection proof still required**

## 1. Coordinate domains

Do not mix these domains implicitly.

### A. Actor/game-state domain

Browser runtime already uses the live player objects:

- P1 base `0xFFBE1C`
- P2 base `0xFFBEFC`
- P3 base `0xFFBFDC`
- player stride `0xE0`

The current Browser runtime reads:

```text
x = S32(player + 0x04) / 65536
y = S32(player + 0x08) / 65536
z = S32(player + 0x0C) / 65536
```

These are game-state coordinates. They are **not DOM pixels** and must not be sent directly to CSS/WebGL placement.

The WinKawaks GEO lane independently closed the equivalent structural semantics: horizontal X, floor/depth Y, and vertical/Z displacement are separate state dimensions and the same structure replicates across P1/P2/P3.

### B. Native game-screen domain

This is the missing proof layer.

The resolver needs a proven transform of the form:

```text
nativeX = Fx(worldX, cameraState)
nativeY = Fy(floorY, z, cameraState_if_any)
```

Do not hardcode a guessed formula before the Browser proof.

The strongest current hypotheses, to be tested rather than assumed, are:

```text
nativeX ~= worldX - cameraX + xBias
nativeY ~= floorY - z + yBias
```

The exact sign, camera address, offsets, and any scale must be established by the Browser proof.

### C. WebGL drawing-buffer domain

This domain is already usable.

Existing direct-WebGL HUD code demonstrates that a HUD position in drawing-buffer pixels maps to clip space as:

```text
left   = x / drawingBufferWidth * 2 - 1
right  = (x + width) / drawingBufferWidth * 2 - 1
top    = 1 - y / drawingBufferHeight * 2
bottom = 1 - (y + height) / drawingBufferHeight * 2
```

Therefore the final resolver should return **drawing-buffer pixels**, not CSS pixels.

### D. DOM/CSS domain

DOM coordinates should be treated as an optional diagnostics/calibration domain only.

If a Browser probe records a pointer/click sample against the game canvas, convert CSS coordinates to drawing-buffer coordinates explicitly:

```text
dbX = (clientX - rect.left) * drawingBufferWidth  / rect.width
dbY = (clientY - rect.top)  * drawingBufferHeight / rect.height
```

This conversion is allowed as a calibration/proof step because it is an explicit canvas transform, not a guessed RAM->DOM mapping.

The production Beta renderer should remain direct WebGL whenever possible.

## 2. Anchor definition

Until exact sprite bounds are proven, define:

```text
playerAnchor = projected player center/foot position
warningAnchorY = playerAnchorY - provenAboveCharacterClearance
```

The clearance is a WOF native-game constant proved once by the Browser test and then scaled through the native-screen -> drawing-buffer transform.

Do **not** call this exact sprite-top tracking. GEO explicitly did not find a stable dynamic sprite-height/top/bottom field in the player object.

A later renderer/frame-descriptor implementation may replace:

```text
warningAnchorY = footY - clearance
```

with:

```text
warningAnchorY = exactSpriteTopY - margin
```

without changing the rest of the interface.

## 3. Resolver contract

Recommended presentation-only contract:

```js
resolvePlayerAnchor(playerName, now) -> {
  ok,                 // boolean
  player,             // 'P1' | 'P2' | 'P3'
  xDb, yDb,           // warning anchor in drawing-buffer pixels
  bodyXDb, bodyYDb,   // optional projected player reference point
  source,             // e.g. 'wof-native-projection-v1'
  projectionVersion,
  sampleAt,
  ageMs,
  confidence,
  reason              // null or fail-closed reason
}
```

`ok` must be false if any required transform component is missing or stale.

## 4. Live inputs

For every rendered warning, use current values:

- current threatened player identity,
- that player's latest `x/y/z`,
- current camera/projection state,
- current `drawingBufferWidth/Height`,
- current game viewport/scale state.

Do not snapshot the target at warning birth and reuse it through a later retarget.

The current HUD bridge already transports each player's live `x/y/z`; an implementation can either consume those values or re-read the same live player object in the rendering worker. Duplicating semantic danger logic is unnecessary.

## 5. Movement behavior

### Horizontal movement

Anchor X follows projected player X continuously.

When the camera starts scrolling, camera motion must be part of the transform. The required invariant is:

```text
world player moves + camera follows -> anchor remains attached to visible player
```

### Floor/depth movement

Anchor Y must use the proven floor/depth projection. P1/P2/P3 share the same object structure, so one projection model should apply to all three unless the Browser proof disproves that assumption.

### Jump / Z

Use live Z. The current Browser runtime already reads `z = S32(+0x0C)/65536` for players and actors.

The proof must establish the screen-Y sign/scale of Z; do not assume that positive Z is visually upward until the marker test confirms it.

### Camera scrolling

Camera state is part of the projection, not an after-the-fact DOM offset.

The WinKawaks object-only BASECAP cannot supply a standalone global camera variable, so Browser proof is authoritative for this layer.

## 6. Scaling, DPR, fullscreen, resize, letterboxing

Final drawing should be expressed in drawing-buffer pixels and then converted to clip space using the live GL dimensions.

On every animation frame or before every warning draw:

1. read `gl.drawingBufferWidth/Height`,
2. read/validate the game viewport mapping used by the proven projection,
3. if dimensions/viewport changed, recompute scale/offset,
4. suppress anchored placement until the new mapping is valid,
5. fixed HUD remains available during the transition.

This avoids making `devicePixelRatio` itself a source of truth. DPR matters only insofar as it changes CSS-to-drawing-buffer size or the emulator's GL surface.

If the emulator introduces internal letterboxing, the proof must return the actual game-content rectangle inside the drawing buffer; do not assume the full canvas is the native game viewport.

## 7. Retarget model

Use a target-bound display identity. Recommended key:

```text
warningIdentity = dangerSourceIdentity + targetPlayer
```

A source retarget edge must produce a new identity.

Rules:

- same source, same target: ordinary display hold may continue;
- same source, target changes: old anchored hold is invalidated immediately;
- new target receives the current warning on its current anchor;
- if the new target anchor is invalid: show fixed HUD, not the old player's anchor;
- multiple simultaneously threatened players may each have one anchored warning; aggregate multiple threats per player before rendering if needed.

## 8. Safety/fallback state machine

```text
ANCHOR_VALID
  -> draw player-anchored warning

ANCHOR_INVALID / STALE / RESIZE_TRANSITION / CAMERA_UNKNOWN
  -> draw fixed in-game warning

DANGER_SAFE
  -> normal warning release semantics
```

Never transition from `ANCHOR_INVALID` to “draw at last known player location” for an unbounded period. A short visual smoothing window is acceptable only while the transform remains valid and the player/target identity has not changed.

## 9. Smoothing

If visual jitter exists after projection proof, smooth only in drawing-buffer space and keep the filter lightweight:

```text
smoothed = lerp(previous, current, alpha)
```

Do not smooth across:

- target-player changes,
- player respawn/object replacement,
- camera discontinuity,
- fullscreen/resize mapping change,
- stale-data recovery.

Those events reset the filter immediately.

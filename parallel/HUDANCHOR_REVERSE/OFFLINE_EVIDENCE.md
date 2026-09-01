# HUDANCHOR Player Projection Reverse — Offline Evidence

Stage: `HUDANCHOR_PLAYER_PROJECTION_REVERSE_V1`

## Conclusion

Offline/static/history/replay evidence has been exhausted far enough to close the reusable coordinate structure and runtime viewport mapping, but it does **not** contain a retained authoritative Browser result that identifies the real scrolling camera candidate or the visual above-character calibration constants.

Therefore this stage must not guess those constants. The only remaining work is the already-bounded Browser proof in `parallel/HUDANCHOR_PROOF/**`, restated more narrowly in `MINIMAL_LIVE_PROOF.md`.

## Offline-closed facts

### Player records

Canonical Browser bridge reader already used by the existing HUD anchor probe:

- P1 base: `0xFFBE1C`
- P2 base: `0xFFBEFC`
- P3 base: `0xFFBFDC`
- stride: `0xE0`
- byte access transform: `address ^ 1`
- X: signed big-endian 32-bit 16.16 at `base + 0x04`
- floor/depth Y: signed big-endian 32-bit 16.16 at `base + 0x08`
- Z: signed big-endian 32-bit 16.16 at `base + 0x0C`

`parallel/GEO/P1_XY_FRONTIER.md` independently closes P1 X as horizontal world movement and Y as floor/depth movement. `parallel/GEO/P2_P3_STRUCTURE_CLOSURE.md` closes P2 with the same movement semantics and P3 with the same object layout/stride. There is no evidence for player-specific projection constants, so one projection model is the correct reusable contract for P1/P2/P3, subject to live validation when extra players are observable.

### Native raster and drawing-buffer mapping

The existing Browser proof tooling fixes the native game raster at `384 x 224` and maps it through the *current* WebGL viewport:

```text
viewportTop = drawingBufferHeight - (viewportY + viewportHeight)
xDb = viewportX + nativeX / 384 * viewportWidth
yDb = viewportTop + nativeY / 224 * viewportHeight
```

The inverse mapping for the single calibration click uses the current canvas CSS rect, current drawing-buffer dimensions and current WebGL viewport. Therefore CSS scale, DPR, fullscreen and letterboxing are runtime layout variables, not game-space constants. They must be remeasured rather than baked into projection constants.

The existing objective gate also requires a real layout change followed by stable remapping. This is sufficient offline closure of the *mapping contract*; a single live run still has to prove that the implementation survives one actual layout change.

### Fail-closed freshness / camera identity policy

The current proof pipeline samples Worker state every 100 ms. Top-side evidence is fresh only while the last Worker state is less than 700 ms old. Calibration freezes a selected camera address, and projection points are not emitted unless the locked camera still matches that calibration address.

For the implementation contract, player and camera values must be consumed from the same Worker state message. A stale Worker state or camera-identity mismatch invalidates the anchored cue rather than reusing an old projection.

## Bounded camera candidate family

The existing Worker proof performs an intentionally bounded scan:

```text
0xFF0000 .. 0xFFBDFF
step 2
read u16be
```

The player object block is excluded. Candidate ranking already uses screen-X plausibility, strong occupancy, range, changes, player-follow correlation, smoothness and top-score separation. Calibration is blocked until all quality gates pass.

The repository does **not** retain a successful proof JSON selecting the authoritative camera address. Consequently these remain live-only facts:

- exact camera address;
- confirmation that the selected read form is the real camera signal for this Browser runtime;
- effective sign/scale embodied by the accepted `worldX-camera+xBias` transform;
- X bias after one visual calibration.

No additional broad RAM scan is justified by the available evidence.

## Bounded vertical / clearance candidate family

One click at the desired warning-anchor center produces exactly three hypotheses:

```text
Y-Z + yBiasMinus
Y+Z + yBiasPlus
Y   + yBiasNone
```

A depth excursion separates floor/depth behavior; a jump separates Z behavior. The successful visual classification freezes one model and its bias.

The stored `aboveCharacterOffsetNative` is deliberately a logical offset from the raw player floor/Z reference to the chosen warning-anchor center. It is **not** a sprite-height or sprite-top claim. No retained static evidence can determine this visual target point, so it must come from the single bounded calibration click and subsequent stability check.

## Why offline work stops here

The unresolved values are observational constants tied to the real Browser renderer/session:

1. which bounded camera candidate is the real scrolling camera signal;
2. which of the three Z models remains attached during a real jump;
3. the desired visual anchor/clearance bias from the raw game-space reference;
4. proof that current WebGL viewport remapping survives one actual layout transition.

The repository already contains objective tooling for all four. Inventing any of them offline would weaken the fail-closed contract rather than advance it.

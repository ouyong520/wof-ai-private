# HUDANCHOR Browser / GEO / WebGL Evidence

Status: evidence audit complete; one Browser projection proof remains.

## Evidence table

| Layer | Existing evidence | What it proves | What it does not prove |
|---|---|---|---|
| Player object layout | `parallel/GEO/P1_XY_FRONTIER.md`, `parallel/GEO/P2_P3_STRUCTURE_CLOSURE.md` | P1/P2/P3 share the same object structure; X, floor/depth Y, and Z/vertical state are distinct and structurally replicated | Browser screen projection |
| Player top/bottom | `parallel/GEO/TOP_BOTTOM_CLOSURE.md` | dynamic sprite top/bottom/height was **not** proven in the player object | exact per-animation head/sprite-top position |
| Browser runtime XYZ | `wof_v4_install_once.js` | Browser runtime already reads actor/player `x=S32(+4)/65536`, `y=S32(+8)/65536`, `z=S32(+0x0C)/65536` | mapping of those values to visible canvas pixels |
| Browser HUD bridge | `wof_hud_worker.js` | every HUD state row already carries live `x/y/z` for P1/P2/P3 | anchored placement |
| Live danger/target semantics | current Future Danger runtime / production-shadow lineage | danger is evaluated against current player state; target-related state is not intended to be a permanent frozen snapshot | presentation-layer retarget hold correctness |
| Direct WebGL HUD | `wof_canvas_probe.js`, `wof_canvas_hud.js`, Alpha HUD lineage | reliable in-game drawing in WebGL drawing-buffer coordinates; clip transform and GL state save/restore pattern are already established | player world -> drawing-buffer projection |
| DOM fixed HUD | `wof_hud_overlay.js` | game canvas rectangle can be located and fixed HUD can remain inside that rectangle | RAM/world -> DOM projection; this is not a player anchor proof |
| Browser camera discovery | `wof_camera_probe.js` | a bounded CPS-RAM candidate scan exists for horizontal camera correlation using `screenX = playerX - candidate` plausibility | no retained authoritative camera address/result or final screen transform exists in repo |
| WinKawaks camera-scroll capture | `parallel/BASECAP/BASE_CAPTURE_CATALOG.md`, bridge B20 capture | operator-confirmed visible horizontal scroll has a retained raw capture | BASECAP records only object windows; cannot directly reveal a standalone global camera variable |
| RAWMINE B20 audit | bridge `results/rawmine/basecap_incremental_audit.md` | confirms object-record data did not expose a broad synchronous camera field; explicitly states the visibility limit | global camera state outside object records |
| Geometry atlas | `reports/GEO_WIN_KAWAKS_PLAYER_GEOMETRY_ATLAS.md` | world/floor/Z anchors are usable; natural captures did not close worldX -> screenX | final camera/projection constants |

## 1. Player geometry is sufficiently solved for an anchor input

The anchor lane does not need more player-object mining.

The useful stable state is already known:

```text
P1 0xFFBE1C
P2 0xFFBEFC
P3 0xFFBFDC
stride 0xE0

Browser:
+0x04 -> x (16.16)
+0x08 -> y (16.16)
+0x0C -> z (16.16)
```

The WinKawaks GEO lane independently supports the same conceptual split: horizontal position, floor/depth position, and vertical/Z displacement.

Therefore a new large Collector campaign is not justified.

## 2. Exact sprite-top is not available from current object proof

GEO explicitly rejected old candidate fields for stable top/bottom/height semantics.

This matters because “warning over the head” has two possible meanings:

1. **logical above-character anchor** — projected player position minus one proved clearance;
2. **exact current sprite top** — depends on animation-frame sprite bounds.

Only (1) is ready to pursue with current evidence. (2) should remain a future renderer/frame-descriptor refinement unless the minimal Browser proof unexpectedly exposes an authoritative native sprite bound.

## 3. WebGL already solves the final rendering coordinate plane

The existing game-canvas probe/HUD creates its own small shader/program, saves the game's GL state, draws a HUD quad, then restores state.

It uses the live drawing-buffer dimensions and converts drawing-buffer pixels to clip coordinates directly.

This is exactly the right final presentation plane for a player anchor because it avoids treating page layout, browser zoom, or a side panel as game coordinates.

The player-anchor lane should reuse that renderer pattern rather than revive the older DOM-fixed overlay as the primary Beta path.

## 4. Native WebGL sprite interception is not currently proven as the anchor source

There is no retained repository evidence that P1/P2/P3 are exposed as separately identifiable WebGL sprite draw calls with recoverable per-player bounds.

The existing WebGL work proves the **composited game canvas / overlay plane**, not an authoritative P1/P2/P3 draw-call identity API.

Therefore do not make “intercept the player's WebGL sprite quad” the primary implementation plan unless a future renderer-specific probe proves that representation.

This keeps the lane within the no-pixel-recognition constraint while avoiding an unsupported renderer assumption.

## 5. Camera is the actual unresolved state variable

`wof_camera_probe.js` already contains the right research direction: scan broader CPS RAM, compare candidate values against P1 world X, and rank values for which `playerX - candidate` behaves like a plausible screen X while the operator triggers visible scrolling.

What is missing is a retained successful result. No saved file currently closes:

```text
camera address + signedness/scale + x bias + viewport scaling
```

This is why the lane is not yet implementation-ready.

## 6. Why B20 does not remove the Browser proof

BASECAP B20 is valuable because the operator explicitly confirmed that the whole background visibly scrolled during the capture.

However the BASECAP contract stores P1/P2/P3 plus enemy object records, not arbitrary global CPS RAM. RAWMINE's incremental audit correctly concludes:

> object-record raw cannot directly expose a standalone global camera variable outside the 23 records.

So B20 is negative/limiting evidence, not the missing camera value itself.

## 7. Retarget evidence is already enough for presentation architecture

The existing runtime lineage reads live player states and the current danger stack is target-aware. The HUD bridge publishes one row per player.

For the anchored renderer the safest presentation rule is therefore:

```text
render each active danger row on that row's player anchor
```

rather than carrying an old anchor with the warning object.

The remaining UI-specific requirement is to make display holds target-bound. A retarget edge must invalidate the old target's anchored hold immediately.

That is an implementation rule, not a new game-memory research problem.

## 8. Evidence classification

### Closed

- P1/P2/P3 object structure
- Browser live X/Y/Z reads
- direct WebGL drawing-buffer HUD plane
- fixed HUD fallback path
- live per-player warning transport
- no need for pixel/color recognition

### Intentionally bounded

- exact sprite-top/current animation bounds

Beta v1 may use a proved logical above-character clearance.

### Open and blocking only this Beta feature

- authoritative Browser camera/native projection
- one proved native/drawing-buffer above-character offset
- confirmation that resize/fullscreen remapping does not break the projection

## Final evidence verdict

**NEEDS ONE MINIMAL BROWSER PROOF**

No additional WinKawaks capture or broad field-mining task should be created before that proof.

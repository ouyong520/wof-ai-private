# HUDANCHOR — Player-Anchored Future Danger HUD

Status: **NEEDS ONE MINIMAL BROWSER PROOF**

Date: 2026-09-01

## Scope

This is bounded Beta support research. It does **not** block Alpha and must not modify `product/alpha/**`.

Goal: render a Future Danger warning slightly above the currently threatened P1/P2/P3 actor and keep it attached through:

- horizontal movement,
- floor/depth movement,
- jump / Z displacement,
- camera scrolling,
- browser scaling / DPR / fullscreen changes,
- live enemy retarget from one player to another.

Pixel/color recognition is not an anchor source.

## Current verdict

Most of the chain is already solved:

1. Browser runtime already reads P1/P2/P3 `x/y/z` as signed 16.16 values from the live CPS RAM object records.
2. P1/P2/P3 use the same player-object structure and the same X/Y/Z offsets.
3. Future Danger already evaluates players independently and existing target logic is live, not a permanently frozen target snapshot.
4. The existing WebGL HUD path already proves reliable drawing in **WebGL drawing-buffer coordinates** and survives normal DOM layout differences better than a page overlay.
5. Existing HUD bridge messages already carry live `x/y/z` for P1/P2/P3.

The only material missing proof is the middle projection layer:

`player world/floor/Z + camera/native game projection -> game native screen position -> WebGL drawing-buffer position`

Repository evidence does **not** yet contain a saved, closed Browser proof for that transform.

## Why this is not IMPLEMENTATION READY yet

The existing `wof_camera_probe.js` is a discovery/correlation probe. It can rank candidate camera values in CPS RAM, but the repository does not contain a retained result proving the authoritative camera address and the final projection constants.

The WinKawaks B20 camera-scroll capture cannot close this gap because BASECAP records only the 23 object windows; RAWMINE explicitly notes that a standalone global camera variable outside those object records is invisible to that dataset.

Likewise, GEO proved X/Y/Z object anchors but did **not** prove dynamic sprite top/bottom/height fields in the player object. Therefore an exact per-animation “head pixel” must not be claimed from object RAM alone.

## Recommended product interpretation

For Beta v1, define the anchor as a **stable logical above-character anchor**, not an exact anatomical head tracker:

- X: projected player center/foot X.
- Y: projected floor/depth position adjusted by live Z, then a single proven native-game upward clearance.
- The clearance is calibrated/proved once for WOF native game coordinates, not per browser session.
- If a later renderer/frame-descriptor lane proves exact sprite bounds, `headTop` can replace the fixed clearance without changing the danger/HUD architecture.

## Preferred architecture

```text
Future Danger runtime
  -> per-player danger rows / live target identity
  -> PlayerAnchorResolver(P1|P2|P3)
       -> live x/y/z
       -> proven camera/native projection
       -> drawing-buffer x/y
       -> validity + freshness + confidence
  -> anchored WebGL warning
       -> if anchor valid: draw above threatened player
       -> else: fixed in-game HUD fallback
```

The anchor layer is presentation-only. It must not change danger semantics, rule tables, family scoring, or Alpha behavior.

## Retarget rule

Retarget must be edge-sensitive:

- The render destination is the **current** threatened player identity on every fresh state/update.
- A display hold may continue only while its hazard identity remains bound to the same target player.
- When a hazard retargets P1 -> P2 (or any other pair), invalidate the old target-bound anchor hold immediately and start/render on the new target.
- Never let a warning remain visually attached to the previous player because a UI hold timer outlived the target edge.

## Fail-closed rules

Use the fixed in-game HUD when any of these is true:

- no supported game canvas/WebGL context,
- player object absent,
- target player invalid,
- projection/camera proof not loaded or not trustworthy,
- anchor sample stale,
- computed anchor is non-finite or grossly outside the game viewport,
- resize/fullscreen transition has not yet produced a valid new drawing-buffer mapping.

A bad anchor must degrade to the fixed HUD, never disappear silently and never guess from DOM/world coordinates.

## Remaining work

Exactly one Browser proof is required. It should validate a single projection model while the operator performs one bounded sequence: horizontal movement into visible scroll, depth up/down, one jump, and optional P1/P2/P3 route cycling if extra players are present.

See:

- `ANCHOR_MODEL.md`
- `BROWSER_EVIDENCE.md`
- `IMPLEMENTATION_RECOMMENDATION.md`
- `MINIMAL_BROWSER_PROBE.md`

After that proof passes, this lane can be promoted to **IMPLEMENTATION READY** without any new large capture campaign.

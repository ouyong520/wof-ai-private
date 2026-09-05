# P37 — Zero-Click Native Marker Auto-Acquisition Baseline

Status/classification: **`UNVERIFIED_AUTO_BASELINE`**

This directory is an isolated functional/diagnostic baseline for automatic WOF native player-marker tracking. It is intentionally **not** renderer authority and must never be used to manufacture `rendererSourceProof`, P29 PASS, P32 native-marker qualification, P34 retry readiness, promotion eligibility, or alpha-live movement.

## Historical behavior recovered

P37 reuses the useful mechanics from the historical tracker commit `6eeebf4a00ce7751ce9ba6008982e8136d1c4290` (`HUD v6: robust native player-label tracking through jumps`):

- native `384x224` scan space;
- player-specific palette masks for P1/P2/P3;
- connected components for native label ink;
- deterministic label + downward-arrow geometry;
- bounded velocity prediction for short loss;
- bounded two-observation automatic reacquisition after a long loss or large jump.

The historical manual F6/F7 focus/click fallback is **not** restored. P37 scans P1/P2/P3 on every frame and exposes no click, portrait, player-selection, or manual-seed API.

Commit `d30a071c668c716cd8d9b5d02932808c76c7a3a7` is retained only as evidence that the maintained Alpha HUD could consume a screen-space P1 tracker. It does not prove renderer-source authority and P37 does not modify that HUD path.

## Coordinate convention and Y-axis regression

P37 canonical diagnostic coordinates are:

- width: `384`
- height: `224`
- origin: top-left
- X increases to the right
- Y increases downward

Therefore:

- move left -> native X decreases;
- move right -> native X increases;
- move up/jump upward -> native Y decreases;
- move down/fall -> native Y increases.

`mapNativeToViewport()` preserves this orientation directly. It never applies `224 - y`, a GL bottom-left inversion, or any equivalent Y flip. The unit fixtures explicitly cover left/right/up/down and viewport round-trip mapping.

## Ambiguity behavior

A structurally valid marker candidate requires a player-color label component/group with a plausible same-color component below it matching the historical down-arrow geometry. If more than one distinct native label+arrow cluster exists for the same player in one frame, P37 returns `AMBIGUOUS` for that player and emits no current X/Y.

Tracking history, nearest distance, list order, timing, and prior focus are not used to break a multi-candidate ambiguity. Motion prediction is used only after a frame has exactly one structural candidate, to decide whether that unique candidate can continue the existing track or needs a second automatic reacquisition confirmation.

## Authority boundary

Every envelope includes:

- `classification = UNVERIFIED_AUTO_BASELINE`
- `coordinateAuthority = DIAGNOSTIC_FRAME_PIXEL_NATIVE_384X224_NOT_RENDERER`
- `rendererSourceProof = null`
- all P29/P32/P36/P34/promotion eligibility flags = `false`
- `readOnly = true`, `ramWrites = 0`, `inputInjection = false`

The pixel/structure scan can provide correlation data to P36, but only P36 owns the direct displayed renderer/object submission source trace. P37 must remain non-authoritative even if its visible tracking later looks correct in a real session.

## Focused deterministic self-check

Run:

```bash
node parallel/AUTO_MARKER_BASELINE/test_native_marker_auto_acquisition_baseline.js
```

The suite covers zero-click startup/acquisition, automatic P1/P2/P3 distinction, horizontal and vertical coordinate orientation, jump/short-loss behavior, long-loss automatic reacquisition, ambiguity fail-closed behavior, invalid native-frame rejection, and the permanent proof boundary.

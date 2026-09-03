# Alpha V1 — All Idle Workers Head-Anchor Convergence Dispatch

## Scope lock
This dispatch is Alpha V1 only. Do not touch Collector, Training Farm, 10-train, recorder, unrelated products, or new version/recovery work.

## Product gate
Nothing counts as delivery until both enemy and player head anchors are visibly correct during normal WOF movement. The eventual core product is enemy-head target label (1P/2P/3P) plus player-head danger warning, but business text is not the current blocker: head geometry is.

## Current mainline facts
- Enemy geometry v2 exists and uses explicit `yAxisSign`, `Y|Y-Z|Y+Z`, `yBias`, and positive per-type head clearance.
- Field adapter is now wired to `enemyHeadClearanceByType` (commit 30f067f81a61a66bbc36723e0a090ff54816c5c5).
- Player geometry is now v2 and uses the same simplified candidate family instead of freeform `floorYScale/zScale` (commit 038160e95acc94d7f238c559c24e775e226d4abb; profile commit 377ce03d06c609fe4df11fc5ee91ceca0c657649).
- HUD drawing-buffer mapping already performs WebGL bottom-origin -> top-origin conversion: `y = H - (vpY + vpHeight)`. Do not reopen viewport-Y theory unless new evidence contradicts it.
- Prior bounded evidence showed Y / Y-Z / Y+Z candidates moved with the actors; therefore prioritize direction/sign/model/offset correction over broad RAM discovery.

## Idle-worker queue
Any idle Alpha worker must take exactly one non-overlapping item below. Do not create a new W/recovery/version.

### A. Player Y-model/sign binder
Use existing retained proof code/evidence plus current direct P1 screen tracker as cross-check. Determine the smallest evidence-backed tuple for player projection v2: camera sign/scale, world-X mapping, `yModel`, `yAxisSign`, `yBias`, positive head clearance. No broad RAM sweep and no manual calibration campaign. If current evidence cannot select one tuple, return the exact missing observation only.

### B. Enemy Y-model/sign/clearance binder
Consume enemy geometry v2. Reuse existing enemy world XYZ and prior Y/Y-Z/Y+Z movement evidence. Bind `yModel`, `yAxisSign`, `yBias`, camera mapping, and per-type positive head clearances for observed enemy types. Do not expand target-label business logic. Reject wrong-direction mappings immediately.

### C. Direct P1 tracker -> projection cross-check
Use the maintained P1 screen-space tracker as ground truth while reading the already-existing P1 world X/Y/Z lifecycle. Build a deterministic comparison that scores only `{Y,Y-Z,Y+Z} x {+1,-1}` and exposes residual/drift. This is validation/cross-check, not a new calibration UX. Goal: prove whether the old evidence was a sign/model error and provide exact selected tuple or exact ambiguity.

### D. Dual-anchor focused regression
Build/extend focused tests that exercise both enemy and player geometry through horizontal movement, depth movement, jump/Z, scroll/camera, stale hide/recovery, and drawing-buffer resize/fullscreen mapping. Tests must reject mirrored Y direction and legacy freeform/offset contracts. No production rewrite unless a test exposes a concrete defect.

### E. Mainline integration consumer
Continuously consume exact commits from A-D into the existing Alpha HUD path. No package release until both anchors are integration-ready. Once both are bound, render simple head markers first; only then enable enemy 1P/2P/3P and player danger content on those same anchors.

## Acceptance
Integration-ready requires:
- enemy head anchor stays above actual enemy head through left/right, depth movement and scroll;
- player head anchor stays above actual player head through left/right, depth movement, jump and scroll;
- no inverted vertical response;
- stale/lost authority hides instead of freezing in old position;
- recovery reappears automatically;
- resize/fullscreen does not introduce drift;
- `readOnly=true`, `ramWrites=0`, `inputInjection=false` remain unchanged.

If any item cannot be completed from retained/runtime evidence, return a precise blocker. Do not replace missing evidence with guessed constants.

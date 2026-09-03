# Alpha V1 Head Anchor Mainline — Extra 2 Worker Acceleration

Authority: existing Alpha V1 mainline only. This is not a new recovery/version/workstream family.

## Scope lock

Only Alpha V1 head-anchor convergence. Do not touch Collector, Training Farm, 10-train, unrelated products, package release, or business-prompt expansion.

Current owner-confirmed defect: both enemy and player top-of-head anchors are wrong. Treat this as a coordinate/mapping defect first. Existing Y / Y-Z / Y+Z evidence that visibly followed motion but may have opposite direction/sign is valuable retained evidence and must be reused before reopening any broad discovery.

## Worker A — Sign / direction root-cause fast path

Goal: determine and fix the minimum transform/sign error causing reversed or displaced top-of-head motion across enemy and player paths.

Inspect only the existing mapping chain and retained evidence:
- native/world Y direction;
- Y, Y-Z, Y+Z candidate direction;
- Z sign and jump direction;
- camera sign;
- player floorYScale / zScale / yBias / headClearance;
- enemy yModel / head offset;
- WebGL drawing-buffer Y origin and viewportTop conversion;
- scroll/camera contribution.

Do not start broad RAM scans or manual calibration campaigns. Prefer a minimal sign/origin correction when retained motion evidence proves the chain already tracks movement.

Acceptance: provide an exact minimal implementation commit or exact BLOCKED reason. Horizontal movement, depth movement, jump where applicable, and scrolling must move the anchor in the same visual direction as the real head. No body/feet/opposite-direction anchor accepted.

## Worker B — Dual-anchor integration regression

Goal: make the corrected enemy and player anchors converge on one verified screen-space convention and prevent false-green integration.

Consume latest exact commits from the existing enemy-head, player-head, and shared-screen mapping work. Build/adjust only focused Alpha tests and the minimal integration glue needed to verify:
- enemy head anchor remains above the real enemy through left/right, depth and scroll;
- player head anchor remains above P1/P2/P3 through left/right, depth, jump and scroll;
- viewport/drawing-buffer resize/fullscreen mapping does not invert Y or drift;
- stale/lost authority hides the anchor and recovery reappears;
- no legacy projection/manual calibration is reselected as a shortcut.

Do not implement danger/1P/2P/3P business expansion yet. Once both anchor classes are correct, hand back integration-ready evidence for the existing Alpha HUD.

## Delivery rule

Success is not a test name, status flag, package, or tracker state. Success means the screen-space anchor is geometrically correct for both enemy and player heads under the covered motions. Return integration-ready exact commits or precise BLOCKED evidence only.

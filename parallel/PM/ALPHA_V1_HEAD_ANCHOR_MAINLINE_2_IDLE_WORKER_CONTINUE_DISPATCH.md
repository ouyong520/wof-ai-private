# Alpha V1 Head Anchor Mainline — 2 Idle Worker Continue Dispatch

## PM interpretation

`1 2` means: continue the current Alpha V1 project and immediately use 2 idle workers. Do not reinterpret this as a request to inspect two completed results.

## Product scope lock

Only Alpha V1. Do not touch Collector, Training Farm, 10-training, data collector, or any other product.

Current product priority is still the same: first make enemy and player head anchors correct and stable. Business text comes after the anchors are correct.

Authoritative constraints:
- `parallel/PM/ALPHA_V1_DELIVERABLE_ONLY_HEAD_ANCHOR_LOCK.md`
- `parallel/PM/ALPHA_V1_HEAD_ANCHOR_MAINLINE_3_WORKER_DISPATCH.md`

Current retained facts:
- enemy geometry sign/clearance correction has landed in `e6c4839e09c02522d954874bfdb78e244a31e49a`;
- enemy path now treats Y-axis sign explicitly and uses positive head clearance subtracted from body Y;
- player head anchor remains the main unclosed implementation gap;
- previous Y / Y-Z / Y+Z experiments that visibly tracked movement are evidence that the chain was alive; prefer sign/origin/scale correction over reopening broad collection or calibration.

## Worker 1 — Player head anchor correction

Own only the player head anchor implementation and focused tests.

Goal: make P1/P2/P3 anchors stay on the real top of the head through horizontal movement, depth movement, jump, and camera scroll.

Inspect and minimally correct the current player world/camera/floor/Z -> native -> WebGL mapping. Prioritize:
- floorYScale sign;
- zScale sign;
- yBias;
- headClearanceNative semantics;
- camera sign;
- Y-axis origin / top-vs-bottom convention;
- interaction between Y, Y-Z, Y+Z evidence and the current affine formula.

Do not reopen manual calibration or broad RAM scanning. Do not change enemy target business logic, menu/package, or unrelated Alpha features.

Acceptance:
- horizontal movement: anchor follows head;
- depth movement: anchor moves in the same visual direction as the head;
- jump: anchor rises/falls with the head, never inverted;
- scroll: anchor remains attached while the camera moves;
- loss hides; recovery reappears;
- no body/feet/opposite-direction anchors.

Deliver integration-ready exact commit(s) or precise BLOCKED reason.

## Worker 2 — Cross-anchor shared screen mapping / integration validation

Own the shared mapping and cross-path validation only. Consume the enemy correction from `e6c4839e09c02522d954874bfdb78e244a31e49a` and the player correction from Worker 1 when it lands.

Goal: ensure enemy and player anchors use a coherent screen-space convention and do not diverge because of viewport/DPR/Y-origin differences.

Prioritize:
- native 384x224 -> WebGL drawing buffer mapping;
- viewportTop calculation;
- WebGL bottom-left vs UI top-left Y origin;
- drawingBuffer/CSS/DPR scaling;
- resize/fullscreen remapping;
- camera sign consistency;
- fail-closed stale/lifecycle behavior.

Do not invent a new projection model. Do not reintroduce manual calibration. Do not touch Collector, Training Farm, 10-training, menu/package, or business text.

Acceptance:
- enemy and player head anchors are both correct under the same viewport state;
- neither becomes vertically inverted after resize/fullscreen;
- no duplicated renderer or legacy projection path is selected as primary;
- loss hides; recovery rebinds cleanly;
- focused regression covers both paths together.

Deliver integration-ready exact commit(s) or precise BLOCKED reason.

## Mainline completion condition for this dispatch

This dispatch is not complete because a PM file exists. It is useful only when the two workers produce code/test commits that make both enemy and player head anchors visually correct and ready to reconnect to the existing Alpha HUD.

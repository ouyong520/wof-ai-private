# Alpha V1 Head Anchor Mainline — Extra 2 Worker Acceleration V2

Scope lock: Alpha V1 only. Do not touch Collector, Training Farm, 10训, package/menu business logic, or unrelated products.

Current durable fact: enemy head geometry/sign correction landed at `e6c4839e09c02522d954874bfdb78e244a31e49a` and changed enemy projection to explicit `yAxisSign`, `yBias`, and positive head-clearance semantics. Do not reimplement that patch.

## Worker A — Player head sign/clearance convergence

Goal: make P1/P2/P3 head anchors land above the real visible heads under horizontal movement, depth movement, jump and scrolling.

Focus only on existing player mapping: `world/camera/floorY/Z -> native -> drawingBuffer`.

Priority checks:
- whether the old Y / Y-Z / Y+Z evidence was directionally correct but sign-inverted;
- `floorYScale`, `zScale`, `yBias`, `headClearanceNative` semantics;
- camera sign and native Y sign;
- ensure clearance is a positive distance subtracted from body/floor reference, not an opaque signed offset;
- do not reopen manual calibration or broad RAM scanning.

Deliver implementation-ready code + focused regression, or exact BLOCKED. Do not touch enemy logic.

## Worker B — Cross-anchor integration validator

Goal: consume the landed enemy sign/clearance fix plus the latest player-head result and prove both species use a coherent screen-space convention.

Validate/fix only shared mapping issues:
- native 384x224 -> WebGL drawing buffer;
- viewportTop / WebGL Y-origin;
- CSS/DPR/resize/fullscreen remap;
- scrolling/camera direction;
- hide-on-loss and reappear-on-recovery;
- no body/feet/reverse-direction anchor acceptance.

Do not create a new projection family. Prefer the smallest sign/origin/mapping correction consistent with retained Y / Y-Z / Y+Z evidence.

Terminal output: integration-ready exact commits or precise BLOCKED. No package release until both enemy and player head anchors are visually correct.

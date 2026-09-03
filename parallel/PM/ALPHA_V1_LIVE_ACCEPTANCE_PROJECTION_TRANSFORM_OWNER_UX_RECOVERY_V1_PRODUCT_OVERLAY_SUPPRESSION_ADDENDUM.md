# Projection Recovery V1 — Product Overlay / Suppression UX Addendum

Applies to the currently ACTIVE stage:
`ALPHA_V1_LIVE_ACCEPTANCE_PROJECTION_TRANSFORM_OWNER_UX_RECOVERY_V1`.

This is a PM clarification of Owner-facing product behavior. It does not create a new task or new dedup generation.

## Owner directive

The current live calibration experience still looks like a projection test harness rather than the intended head-top warning/target product. The Owner explicitly rejects exposing candidate math such as `Y`, `Y-Z`, `Y+Z` during normal use, and reports a current state where only one `Y` remained on screen without a clear instruction.

The product target is not to visually demonstrate projection candidates. The target is to deliver reliable production head-top overlays with minimal/no calibration burden.

## Required product behavior

1. **No candidate/debug labels in normal Owner flow.**
   - Do not show `Y`, `Y-Z`, `Y+Z`, candidate IDs, residual labels, or multi-model black boxes to the Owner during normal menu-6 use.
   - Candidate/fitting diagnostics may exist only in collected evidence/logs or an explicitly diagnostic/developer mode that normal Owner flow never enters.

2. **Uncertain motion => temporarily suppress, never draw wrong.**
   - During jump, rapid vertical/depth motion, room scroll, camera transition, resize/fullscreen transition, runtime-generation change, or any state where current projection confidence/authority is insufficient, temporarily hide head-top overlays.
   - When the stable projection authority becomes valid again, overlays may automatically resume.
   - Do not force the implementation to maintain a visually wrong marker through every jump/scroll frame merely to claim continuous drawing.
   - Suppression must be fail-closed and evidence-visible; stale/wrong coordinates must never be shown as production output.

3. **Production output only.**
   - After projection authority is established, the visible product overlay should be only the intended user-facing result, principally enemy `1P/2P/3P` target labels and player `[危险]` when an existing supported danger rule actually fires.
   - Calibration status should be a compact temporary message only when necessary, not a persistent test panel that dominates gameplay.

4. **Normal flow must be simple.**
   Desired success path:
   `menu 6 -> enter game -> play normally -> automatic calibration/authority -> production head overlays`.
   - Prefer zero clicks.
   - If vision-assisted tracking truly requires a seed, allow at most one P1-head click for the current authority generation.
   - Never request second/third repeated clicks unless authority was explicitly revoked and a single new seed is objectively required; such a case must be clearly explained and should be exceptional, not normal flow.
   - Do not require the Owner to manually perform a checklist of horizontal/depth/jump/resize actions if ordinary play can collect sufficient evidence automatically.
   - If a specific missing motion is truly required, request exactly one simple action at a time (e.g. `现在跳一次`) and automatically detect completion.

5. **No silent single-Y state.**
   - A screen containing one residual `Y` marker with no clear next action is an invalid Owner state.
   - Every non-production state must either progress automatically, show one explicit next action, or terminate with one clear fail-closed reason.

6. **Separate implementation proof from product UX.**
   - The implementation may use vision tracking, RAM/world samples, camera samples, fitting/residual analysis, and deterministic test fixtures internally.
   - The Owner should not be made to act as a projection engineer or interpret those internals.
   - Treat calibration/test rendering and production head-top warnings as separate surfaces. Normal Owner validation should primarily validate the actual production presentation, not a debug visualization of candidate equations.

7. **Evidence remains automatic.**
   - Record suppression intervals/reasons, authority acquisition/revocation, visual tracker confidence, fit residuals, and production activation in the menu-6 live-session evidence ZIP.
   - Keep these details out of the gameplay surface unless an actionable Owner instruction is required.

## Acceptance implication

A successor is not Owner-ready merely because an internal projection candidate can be rendered. It is Owner-ready only when:
- normal gameplay no longer exposes candidate/debug markers;
- unstable jump/scroll/transition frames safely suppress rather than misplace overlays;
- production labels resume automatically under valid authority;
- the Owner can validate the actual `1P/2P/3P` / `[危险]` experience with essentially no coordinate-model knowledge.

Preserve all existing strict safety, exact World identity, Camera READY authority, runtime-generation revocation, lifecycle binding, and fail-closed contracts.

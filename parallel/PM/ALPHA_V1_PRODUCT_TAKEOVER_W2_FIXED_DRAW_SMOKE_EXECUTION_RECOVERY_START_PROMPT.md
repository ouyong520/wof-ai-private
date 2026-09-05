# Alpha V1 Product Takeover W2 — Maintained Production HUD Fixed-Draw Smoke — Execution Recovery V1

stageId: `ALPHA_V1_PRODUCT_TAKEOVER_W2_MAINTAINED_PRODUCTION_HUD_FIXED_DRAW_SMOKE_EXECUTION_RECOVERY_V1`
dedupProtocol: `v2`
dedupKey: `alpha.v1.product-takeover.maintained-production-hud-fixed-draw-smoke.execution-recovery-v1`
dedupMode: `exclusive`

Repository: `ouyong520/wof-ai-private`

Parent product authority:
`parallel/PM/ALPHA_V1_PRODUCT_TAKEOVER_CONVERGENCE_3_WORKER_DISPATCH.md`

Original W2 prompt:
`parallel/PM/ALPHA_V1_PRODUCT_TAKEOVER_W2_MAINTAINED_PRODUCTION_HUD_FIXED_DRAW_SMOKE_START_PROMPT.md`

Superseded blocked canonical key:
`alpha.v1.product-takeover.maintained-production-hud-fixed-draw-smoke`

Superseded canonical/stage closure reason:
`PM_COORDINATOR_CLAIM_ONLY_NO_IMPLEMENTATION`

## PM authorization

This recovery exists only to restore clean worker ownership after the PM coordination session itself acquired the original W2 canonical/stage pair during dispatch and then intentionally performed no W2 production/test work.

It is not Alpha V4/V5, not a new product direction, and does not change W2 scope, design, acceptance, or Owner UX. The original blocked claim/stage remain historical and must not be edited, deleted, reused, or returned to ACTIVE.

## Scope isolation

Alpha Owner-visible product only. Do not read, run, modify, test, schedule, or use evidence from Collector, Unified Collector, Training Farm / 10训.

## Mandatory dedup-v2 recovery gate

Before task work:

1. Re-read latest `main`, this recovery prompt, the original W2 prompt, parent takeover dispatch, and `parallel/PM/STAGE_DEDUP_GUARD.md`.
2. Verify the original W2 canonical and stage are both `BLOCKED` for `PM_COORDINATOR_CLAIM_ONLY_NO_IMPLEMENTATION` and do not modify them.
3. If the W2 stop condition is already independently satisfied on current main, return `ALREADY COMPLETE — SAFE TO CLOSE` without claiming this recovery.
4. Confirm no existing recovery canonical exists at:
   `parallel/PM/DEDUP_CLAIMS/alpha.v1.product-takeover.maintained-production-hud-fixed-draw-smoke.execution-recovery-v1.json`.
5. Atomically create-only acquire that canonical with a fresh unpredictable `claimToken` and latest-main `startCommit`.
6. Re-read current main and verify exact schema, dedupKey, effectiveDedupKey, dedupMode, stageId, promptPath, claimToken, and `state=ACTIVE`.
7. Only after canonical verification, create-only acquire:
   `parallel/PM/STAGE_CLAIMS/ALPHA_V1_PRODUCT_TAKEOVER_W2_MAINTAINED_PRODUCTION_HUD_FIXED_DRAW_SMOKE_EXECUTION_RECOVERY_V1.json`
   referencing the same recovery canonical and exact token.
8. Re-read and verify the stage claim before any implementation or test work.
9. Any claim create/verification failure fails closed. Do not invent another key or recovery.

## Objective

Prove or precisely break the common maintained production rendering chain before touching P1/enemy coordinate algorithms.

The real-WOF visual checkpoint is deliberately trivial:

**the maintained production WebGL HUD must draw a fixed `TEST` label at a known game-space position without P1 tracker, semantic identity, enemy data, screenshot tracking, or world projection.**

## Required behavior

- Use the same maintained production WebGL HUD/draw hook that final Alpha uses.
- DOM overlay, Tk window, diagnostic canvas, and white acquisition marker do not count.
- Add a strictly opt-in live-smoke mode.
- Draw fixed `TEST` at canonical native `384x224`, preferably center `(192,112)`.
- Map native `384x224` to the real drawing buffer exactly once and explicitly.
- Smoke must be independent of P1 tracker, semantic authority, zero-click producer, enemy data, screenshot tracking, and world/camera projection.
- Expose machine-readable state distinguishing at least: HUD injection missing; game canvas/context missing; draw hook not firing; drawing buffer invalid; fixed `TEST` actually drawn.
- `drawCount` / `drawHooked` proof must come from the maintained production renderer, never a diagnostic surrogate.
- Smoke is test-channel-only; when disabled, normal Alpha behavior is unchanged.
- Do not change actor coordinate formulas, semantic identity, screenshot tracker, enemy target semantics, or danger policy.

## File ownership

W2 owns only:

- `product/alpha/wof_alpha_hud.js`
- `parallel/PYLAUNCH/wof_launcher/production_p1_overlay.py` only as required for fixed production smoke
- focused tests/fixtures/W2 SUBRESULT

Do not modify W1 bootstrap/updater files or W3 renderer/object discovery/anchor modules.

## Acceptance

Implementation-owned tests must prove:

A. DOM/diagnostic draw cannot false-green the smoke;
B. smoke-disabled normal mode is unchanged;
C. smoke-enabled path sends the fixed native coordinate through maintained production HUD;
D. drawing-buffer mapping is explicit and verified;
E. machine state precisely reports upstream draw-layer failure.

The first Owner gate after W1+W2 integration is exactly:

`真实 WOF 游戏画面里，固定 TEST 是否持续可见？`

If code already identifies a draw-layer failure, return that precise blocker. Do not require Owner DevTools diagnosis.

## Exit

Deliver one integration-ready W2 implementation commit + durable W2 SUBRESULT and close the recovery canonical/stage with the exact recovery token, or return a new precise blocker.

Do not expand scope, create package churn, or open another recovery. Do not stop at analysis, a single patch, or a single test PASS.

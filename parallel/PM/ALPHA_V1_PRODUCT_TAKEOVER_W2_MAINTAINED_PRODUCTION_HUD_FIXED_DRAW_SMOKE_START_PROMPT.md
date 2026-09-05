# Alpha V1 Product Takeover W2 — Maintained Production HUD Fixed-Draw Smoke

stageId: `ALPHA_V1_PRODUCT_TAKEOVER_W2_MAINTAINED_PRODUCTION_HUD_FIXED_DRAW_SMOKE`
dedupProtocol: `v2`
dedupKey: `alpha.v1.product-takeover.maintained-production-hud-fixed-draw-smoke`
dedupMode: `exclusive`

Repository: `ouyong520/wof-ai-private`

Parent PM authority:
`parallel/PM/ALPHA_V1_PRODUCT_TAKEOVER_CONVERGENCE_3_WORKER_DISPATCH.md`

Authority baseline before takeover dispatch: `747c5b09d7a3d510a2df4bb8f9cb480ca8101da4`

## Scope isolation

Alpha only. Do not read, run, modify, test, schedule, or use evidence from Collector, Unified Collector, Training Farm / 10训.

## Dedup-v2 execution gate

Before task work:

1. Re-read latest `main`, parent takeover dispatch, `parallel/PM/STAGE_DEDUP_GUARD.md`, relevant results/claims, and recent equivalent commits.
2. If equivalent stop condition is already satisfied, return `ALREADY COMPLETE — SAFE TO CLOSE`.
3. Otherwise atomically create-only acquire:
   `parallel/PM/DEDUP_CLAIMS/alpha.v1.product-takeover.maintained-production-hud-fixed-draw-smoke.json`
   using a fresh unpredictable `claimToken` and latest-main `startCommit`.
4. Re-read the canonical claim from current `main` and verify exact schema, dedupKey, effectiveDedupKey, dedupMode, stageId, promptPath, claimToken, and `state=ACTIVE`.
5. Only after canonical verification, create-only acquire the matching stage claim:
   `parallel/PM/STAGE_CLAIMS/ALPHA_V1_PRODUCT_TAKEOVER_W2_MAINTAINED_PRODUCTION_HUD_FIXED_DRAW_SMOKE.json`
6. If either acquisition/verification fails, follow dedup v2 and stop; do not invent another key or recovery.

## Objective

Prove or precisely break the common maintained production rendering chain before touching P1/enemy coordinate algorithms.

The real-WOF visual checkpoint is deliberately trivial:

**the maintained production WebGL HUD must draw a fixed `TEST` label at a known game-space position without P1 tracker, semantic identity, enemy data, screenshot tracking, or world projection.**

## Required behavior

- Use the same maintained production WebGL HUD/draw hook that final Alpha uses.
- DOM overlay, Tk window, diagnostic canvas, and white acquisition marker do not count.
- Add a strictly opt-in live-smoke mode.
- Draw fixed `TEST` at canonical native 384x224 coordinates, preferably center `(192,112)`.
- Map native 384x224 to the real drawing buffer exactly once and explicitly.
- Smoke must be independent of P1 tracker, P1 semantic authority, zero-click producer, enemy data, screenshot tracking, world/camera projection.
- Expose machine-readable state distinguishing at least: HUD injection missing; game canvas/context missing; draw hook not firing; drawing buffer invalid; fixed TEST actually drawn.
- `drawCount`/`drawHooked` proof must come from the maintained production renderer, never a diagnostic surrogate.
- Smoke is test-channel-only; when disabled, normal Alpha behavior is unchanged.
- Do not change actor coordinate formulas, semantic identity, screenshot tracker, enemy target semantics, or danger policy.

## File ownership

W2 owns only the maintained HUD smoke/draw proof and narrow adapter integration, principally:

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

The first Owner gate after W1+W2 integration is exactly one question:

`真实 WOF 游戏画面里，固定 TEST 是否持续可见？`

If the code layer already identifies failure, return the precise blocker; do not require Owner DevTools diagnosis.

## Exit

Deliver one integration-ready commit + durable W2 SUBRESULT and close canonical/stage claims with the exact token, or return a precise blocker.

Do not expand scope, create package churn, or open a new recovery.

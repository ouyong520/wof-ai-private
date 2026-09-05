# Alpha V1 Product Takeover G3 — First Owner-Gate Integration / Promotion

stageId: `ALPHA_V1_PRODUCT_TAKEOVER_G3_FIRST_OWNER_GATE_INTEGRATION_PROMOTION`
dedupProtocol: `v2`
dedupKey: `alpha.v1.product-takeover.first-owner-gate-integration-promotion`
dedupMode: `exclusive`

Repository: `ouyong520/wof-ai-private`

Parent authority:
`parallel/PM/ALPHA_V1_PRODUCT_TAKEOVER_FIRST_OWNER_GATE_3_WORKER_DISPATCH.md`

Baseline before this dispatch: `f63f53042f555d4f0e0221a0dc165aa51f7c5add`

## Scope isolation

Alpha Owner-visible product only. Do not read, run, modify, test, schedule, or use evidence from Collector, Unified Collector, Training Farm / 10训.

## Dedup-v2 gate

Before task work, re-read latest `main`, parent dispatch, `parallel/PM/STAGE_DEDUP_GUARD.md`, W1/W2 durable subresults, current `alpha-live`, and G1/G2 prompt/claim/result state.

If the full stop condition is already satisfied, return `ALREADY COMPLETE — SAFE TO CLOSE`.

Otherwise create-only acquire:
`parallel/PM/DEDUP_CLAIMS/alpha.v1.product-takeover.first-owner-gate-integration-promotion.json`

with fresh token/latest-main startCommit; re-read current main and verify exact v2 ownership. Then create-only acquire and verify:
`parallel/PM/STAGE_CLAIMS/ALPHA_V1_PRODUCT_TAKEOVER_G3_FIRST_OWNER_GATE_INTEGRATION_PROMOTION.json`

No promotion/test/result work before both exact-token checks pass. Fail closed on any create/verification failure; do not invent recovery.

## Objective

Produce exactly one coherent first Owner fixed-TEST candidate from accepted W1 + accepted W2 + G1 runtime wiring + G2 bootstrap/handoff, then move controlled `alpha-live` to that exact accepted commit.

G3 is an integration/release coordinator. It does **not** own product feature implementation.

## Dependency behavior

G1 and G2 may still be running when this worker starts.

- Do not duplicate or modify their files.
- Poll/re-read latest main and their canonical/stage/result paths at a reasonable cadence while doing only non-mutating readiness inspection.
- Proceed to integration acceptance only after both provide durable integration-ready SUBRESULT/COMPLETE evidence with exact implementation commits.
- If either becomes precise BLOCKED, stop G3 as dependency BLOCKED; do not patch their layer yourself.

## Required integration checks

Once G1+G2 are ready:

1. Verify their exact implementation commits are present in one current-main lineage and do not conflict with accepted W1/W2 sources.
2. Verify the live-mode marker explicitly requests the fixed TEST gate for this candidate.
3. Verify permanent updater reads controlled `alpha-live`, not arbitrary `main`.
4. Verify gate handoff reaches `WOF_ALPHA_FIXED_DRAW_SMOKE=1` without Owner manual flags.
5. Verify G1 runtime can enable/poll `ProductionHudFixedDrawSmoke` before P1 acquisition and persists precise machine state.
6. Verify W2 strict proof still requires maintained production WebGL draw and exact fixed metadata `TEST`, native `384x224`, center `(192,112)`.
7. Verify normal mode remains possible by changing the controlled marker in a future release; no new launcher download is needed.
8. Verify `LATEST_ALPHA_FEEDBACK.txt` exposes candidate SHA/live mode/status path.
9. Verify read-only safety and no Browser kill/unrelated SSH-key mutation.
10. Run only the focused tests for W1 permanent bootstrap, W2 fixed-draw smoke, G1 runtime wiring, and G2 live-mode handoff plus one narrow integration check. Do not run broad historical Alpha QA.

## Alpha-live promotion

Before promotion, read current `alpha-live` and record its old SHA.

Only if every required integration check passes:

- identify the exact current-main commit containing the accepted W1/W2/G1/G2 candidate;
- move `refs/heads/alpha-live` to that exact commit using non-force fast-forward semantics whenever possible;
- re-read `alpha-live` and verify exact target SHA;
- write durable first-gate candidate RESULT with old/new alpha-live SHA, component commits, focused test results, live-mode marker, Owner instruction, and rollback target.

Do not move `alpha-live` to a PM-doc-only commit that lacks the integrated product files. Do not promote an untested intermediate commit.

If fast-forward cannot be established cleanly, fail closed and report the exact branch lineage issue; do not force unless a separate PM authority explicitly authorizes it.

## File / mutation ownership

G3 may mutate only:
- PM integration RESULT/claim/stage records under its own authority;
- the `alpha-live` branch ref after acceptance.

G3 must not edit production/runtime/updater/HUD/W3 source files.

## Owner handoff

Do **not** run real WOF or fabricate Owner PASS.

Successful terminal state is:
`READY_FOR_OWNER_FIXED_TEST`

The only Owner product question after PM receives this result is:
`固定 TEST 是否持续显示在真实游戏画面？`

The Owner should use the same permanent launcher and should not be asked to choose files, versions, flags, DevTools, or internal JSON.

## Exit

Deliver durable G3 integration RESULT, verified `alpha-live` promotion and close canonical/stage claims with exact token; or precise dependency/integration BLOCKED. Stop only at READY_FOR_OWNER_FIXED_TEST / COMPLETE / precise BLOCKED.
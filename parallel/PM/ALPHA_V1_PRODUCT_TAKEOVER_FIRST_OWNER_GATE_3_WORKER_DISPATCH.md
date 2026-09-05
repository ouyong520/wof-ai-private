# Alpha V1 Product Takeover — First Owner Gate 3-Worker Dispatch

Repository: `ouyong520/wof-ai-private`

Authority baseline: `f63f53042f555d4f0e0221a0dc165aa51f7c5add`

Scope: **Alpha Owner-visible product only**. Collector / Unified Collector / Training Farm / 10训 are out of scope.

## PM audit at dispatch

W1 permanent live-test bootstrap is integration-ready and its recovery claim/stage are COMPLETE. It established zero-state bootstrap, SSH/22 updates, a single permanent `WOF_ALPHA_TEST.cmd`, controlled `alpha-live`, Browser/WOF-preserving Alpha runtime restarts, and `Documents\WOF_RESULTS\LATEST_ALPHA_FEEDBACK.txt`.

W2 maintained production fixed-draw smoke is integration-ready and its execution-recovery claim/stage are COMPLETE. The maintained HUD can, when explicitly enabled, draw fixed `TEST` at native `384x224` center `(192,112)` and expose fail-closed machine states.

W3 deterministic renderer/object authority remains SUBCOMPLETE with its existing logical claim ACTIVE. It is intentionally waiting for the first Owner live gate; do not open another W3 recovery or duplicate research task.

Current `alpha-live` still points to W1 implementation commit `d664618403b1ae83f6880ca4d3833202c299415f`, so it does **not yet represent the final W1+W2 first-gate candidate**.

The only immediate product goal is:

`one permanent Owner bootstrap/launcher -> controlled alpha-live -> fixed production TEST automatically enabled for the first gate -> precise feedback -> one Owner real-WOF observation`

No P1/enemy/semantic/zero-click/danger expansion is authorized in this dispatch.

## G1 — Fixed-draw Owner-gate runtime wiring

Start prompt:
`parallel/PM/ALPHA_V1_PRODUCT_TAKEOVER_G1_FIXED_DRAW_OWNER_GATE_RUNTIME_WIRING_START_PROMPT.md`

Goal: make the existing permanent Alpha runtime consume a controlled first-gate mode and actually enable/poll `ProductionHudFixedDrawSmoke`, independently of P1 acquisition. Emit precise machine-readable status into the Owner result path. Normal mode must remain unchanged when gate mode is off.

## G2 — First-gate bootstrap / handoff mode

Start prompt:
`parallel/PM/ALPHA_V1_PRODUCT_TAKEOVER_G2_FIRST_OWNER_GATE_BOOTSTRAP_HANDOFF_START_PROMPT.md`

Goal: make the permanent updater/launcher read a repo-controlled Alpha live-mode marker and set the fixed-smoke gate environment only for the first Owner candidate. Preserve zero-state bootstrap and SSH/22 behavior. Keep one permanent launcher and one obvious feedback path.

## G3 — Candidate integration + alpha-live promotion

Start prompt:
`parallel/PM/ALPHA_V1_PRODUCT_TAKEOVER_G3_FIRST_OWNER_GATE_INTEGRATION_PROMOTION_START_PROMPT.md`

Goal: wait for exact G1/G2 integration-ready commits, verify one coherent first-gate candidate, run only focused integration checks, then move `alpha-live` to that exact candidate. No production feature implementation is owned by G3.

## File / authority separation

- G1 owns runtime gate activation/probe/status glue; it does not edit updater/bootstrap or branch refs.
- G2 owns updater/bootstrap live-mode handoff and release-mode marker; it does not edit HUD/probe internals or branch refs.
- G3 owns integration evidence and `alpha-live` promotion only after G1/G2 are ready; it does not implement product logic.
- W3 renderer/object authority files and its ACTIVE claim are untouched by all three.

## Owner gate

Do not ask Owner to test until G3 produces `READY_FOR_OWNER_FIXED_TEST` and `alpha-live` points to the exact accepted candidate.

Then Owner action is intentionally minimal:

1. run the one-time setup only if not already installed;
2. use the same permanent `WOF_ALPHA_TEST.cmd`;
3. enter/reuse real WOF;
4. answer only: **固定 TEST 是否持续显示在真实游戏画面？**

If not visible, use the machine-readable fixed-smoke state and latest feedback artifact to route the defect back to the owning layer. Do not ask Owner to use DevTools or choose files/versions.

## Exit

This dispatch exits when G1/G2 are integration-ready, G3 has promoted one coherent first-gate candidate to `alpha-live`, and PM is ready to request the single Owner fixed-TEST observation. It does not declare Alpha complete.
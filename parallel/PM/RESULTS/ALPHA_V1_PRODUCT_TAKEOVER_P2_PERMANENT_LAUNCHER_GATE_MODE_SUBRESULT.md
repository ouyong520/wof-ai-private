# Alpha V1 Product Takeover P2 — Permanent Launcher Gate Mode SUBRESULT

State: **SUBCOMPLETE / INTEGRATION-READY**

Execution authority:
`parallel/PM/ALPHA_V1_PRODUCT_TAKEOVER_P2_PERMANENT_LAUNCHER_GATE_MODE_START_PROMPT.md`

Parent authority:
`parallel/PM/ALPHA_V1_PRODUCT_TAKEOVER_FIRST_OWNER_GATE_PARALLEL_3_WORKER_V2_DISPATCH.md`

Dedup key:
`alpha.v1.product-takeover.first-owner-gate.permanent-launcher-gate-mode-v2`

Claim token:
`9923cadcc689bfde33a0b4f5474a3461981e4b98eee49be9`

Implementation commit:
`a861ba4d0e3c58501e0b54f872a788325e80be90`

## Implemented

- Added repo-controlled marker `parallel/PYLAUNCH/alpha_live_mode.txt` with first-candidate value `fixed-draw-first-gate`.
- `parallel/PYLAUNCH/owner_live_retest_loop.ps1` now resolves the marker on every Alpha runtime start/restart.
- `fixed-draw-first-gate` launches only the Alpha runtime child with `WOF_ALPHA_FIXED_DRAW_SMOKE=1`, then restores/removes the controller process environment immediately after `Start-Process`.
- `normal` explicitly removes the smoke flag for the child launch.
- missing, unreadable, multi-line, surrounding-whitespace, and unknown markers fail closed to effective `normal` with one explicit `liveModeReason`; none can enable smoke.
- future `alpha-live` releases that return the marker to `normal` automatically restart Alpha without the smoke flag because mode is re-resolved on every runtime start.
- existing `Documents\WOF_RESULTS\LATEST_ALPHA_FEEDBACK.txt` now exposes `currentSha`, `liveMode`, and `liveModeReason` while retaining the existing feedback/status surface.
- no second desktop launcher was added; `WOF_ALPHA_TEST.cmd` remains the single permanent entry.
- no Browser/Chrome stop behavior was added; normal updates still stop/restart only the Alpha runtime.
- no installer change was required.

## W1 preservation

The accepted W1 files remained unchanged from implementation commit `d664618403b1ae83f6880ca4d3833202c299415f`:

- `WOF_ALPHA_SETUP_ONCE.cmd` blob `b57db6602e7fdcf3be8bbd2a1ff1f795e380e5a1`
- `WOF_ALPHA_TEST.cmd` blob `a4e8dac92b822d6f14a327083a0d94d5f167725e`
- `parallel/PYLAUNCH/install_live_retest_once.ps1` blob `c5f299544c468e1ce85a73b6dec9d5cc19600c6f`

Therefore the zero-state managed-directory bootstrap, `%USERPROFILE%\.ssh` preservation, GitHub SSH port 22 transport, `alpha-live` pointer, and single permanent launcher behavior are preserved rather than redesigned.

`alpha-live` was deliberately **not moved** by P2 and remained at `d664618403b1ae83f6880ca4d3833202c299415f` at closeout verification.

## Focused acceptance

Focused test added:
`parallel/PYLAUNCH/tests/test_owner_permanent_launcher_gate_mode_p2.py`

Result against the exact P2 implementation blobs:

`9 passed`

Exact P2 blobs verified:

- `owner_live_retest_loop.ps1` -> `0506ecbfa71477bb50053d40a18b1ad74a642267`
- `alpha_live_mode.txt` -> `0f478c0a163ba14cd7c3dc44d6f2391e7c3d135c`
- `test_owner_permanent_launcher_gate_mode_p2.py` -> `943fed003e5eaea29199853b1d6bdb9b3dedd45a`

Acceptance mapping:

- A zero-state/bootstrap contract preserved: PASS via unchanged accepted W1 setup blob plus focused invariant coverage.
- B SSH/22-only update path preserved: PASS.
- C normal mode does not set smoke: PASS.
- D `fixed-draw-first-gate` sets `WOF_ALPHA_FIXED_DRAW_SMOKE=1` automatically for the Alpha child: PASS.
- E malformed/unknown marker cannot enable smoke and reports fail-closed reason: PASS.
- F Browser/WOF is not deliberately killed by P2 handoff: PASS.
- G exactly one permanent launcher path remains: PASS.

No Owner test was requested or performed. P2 is ready for PM integration with P1/P3 before any `alpha-live` promotion.

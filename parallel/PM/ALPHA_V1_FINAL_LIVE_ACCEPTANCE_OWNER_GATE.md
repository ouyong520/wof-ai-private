# Alpha V1 Final Live Acceptance — Owner Gate

Status: BLOCKED — P36/P37/P38 TERMINAL COMPLETE; P39/P40/P41 DISPATCHED; no Owner retry yet

P25, P27, P28, P29, P30, P31, P33, P34, P35, P36, P37 and P38 are terminal COMPLETE at their repository-side authority boundaries. P26 remains historical terminal BLOCKED and must not be reopened. P32 remains historical terminal BLOCKED authority; its direct renderer proof requirement is still enforced by the unchanged qualifier.

## Fresh PM-reviewed state

- P36 terminal COMPLETE, testedCommit `162e50b6c65fd1d3901ad694854563b686b2ce22`, integrationReady=true. A durable zero-click read-only renderer-submit source observer/proof producer exists and passed exact-candidate focused tests. Real WOF live marker authority is still NOT_PROVEN; the runtime must expose one unique actual direct source during the later bounded run.
- P37 terminal COMPLETE, testedCommit `64d5c3d2c1c84fffc7d9f59e701ec37fd1c68530`, classification `UNVERIFIED_AUTO_BASELINE`. Automatic P1/P2/P3 acquisition/reacquisition, native 384x224 tracking and explicit non-inverted Y behavior are exact-byte tested. It remains diagnostic only.
- P38 terminal COMPLETE, testedCommit `3e9ae7e725e3dd32d1172866fef11d3ff89e163f`. It materialized a deterministic accepted-repair candidate from P35 source, but that candidate predates accepted terminal P36/P37 and therefore is not the final live candidate.
- Current main contains the exact P36 and P37 tested commits in ancestry and exact tested blobs.

## Product requirement — zero click

Final Alpha behavior requires zero manual avatar/portrait clicks, zero manual player selection and zero manual seed. Owner starts/plays the game; P1/P2/P3 discovery/reacquisition must be automatic.

## Current three Worker lanes

1. P39 `ALPHA_V1_PRODUCT_TAKEOVER_P39_ZERO_CLICK_VISIBLE_HUD_BASELINE_INTEGRATION`
   - integrate P37 into maintained HUD under an explicit diagnostic/staging gate;
   - restore visible automatic following with correct X/Y orientation;
   - remain clearly `UNVERIFIED_AUTO_BASELINE`, never renderer authority.

2. P40 `ALPHA_V1_PRODUCT_TAKEOVER_P40_NATIVE_MARKER_RENDERER_SOURCE_RUNTIME_EXPOSURE`
   - expose the truthful actual displayed renderer-submit source surface that P36 can discover;
   - exact P1/P2/P3 actor generation + native 384x224 + runtimeEpoch/rendererEpoch/authorityKey;
   - no structural/pixel/screenshot/template/nearest/order/timing fallback.

3. P41 `ALPHA_V1_PRODUCT_TAKEOVER_P41_BOUNDED_ZERO_CLICK_LIVE_VERIFICATION_HARNESS`
   - build the later single-run harness with exact source/candidate precheck;
   - capture P36 raw source evidence, P37/P39 diagnostic correlation, Page/Worker/WASM/runtime identity and complete raw logs/receipt;
   - no real game run under Worker authority.

## Retry rule

No Owner rerun is authorized yet. P39/P40/P41 must terminalize first. PM will then materialize one fresh exact containing candidate that includes the accepted live-bridge work, rerun the P34 readiness gate against that exact candidate, and only if it reports READY will exactly one bounded zero-click Owner live verification be authorized.

The next live verification must preserve complete raw logs/receipts rather than only a summary status so any failure can be attributed to the exact gate/source/identity stage.

Reuse the existing Windows repo, dedicated project venv, browser and Git objects; no unnecessary reinstall/redownload and no global Python/PATH/site-packages changes. Codex performs local deployment/run only; Owner performs actual game interaction and visual judgment.

Only explicit live renderer authority plus exact P16/P17 readiness may advance to the Owner visual question. A truthful INCONCLUSIVE/BLOCKED remains fail-closed.

Safety remains unchanged: `readOnly=true`, `ramWrites=0`, `inputInjection=false`, no guessed addresses, no screenshot/world-projection production coordinates, and no alpha-live movement before a separately guarded promotion action.

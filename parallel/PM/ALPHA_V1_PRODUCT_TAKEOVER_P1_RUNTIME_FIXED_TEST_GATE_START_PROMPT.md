# Alpha V1 Product Takeover P1 — Runtime Fixed TEST Gate

stageId: `ALPHA_V1_PRODUCT_TAKEOVER_P1_RUNTIME_FIXED_TEST_GATE`
dedupProtocol: `v2`
dedupKey: `alpha.v1.product-takeover.first-owner-gate.runtime-fixed-test-gate-v2`
dedupMode: `exclusive`

Repository: `ouyong520/wof-ai-private`

Parent authority:
`parallel/PM/ALPHA_V1_PRODUCT_TAKEOVER_FIRST_OWNER_GATE_PARALLEL_3_WORKER_V2_DISPATCH.md`

## Dedup preflight

Before any implementation/test work:

1. Read latest `main`, this prompt, parent dispatch, and `parallel/PM/STAGE_DEDUP_GUARD.md`.
2. Confirm no canonical exists at:
   `parallel/PM/DEDUP_CLAIMS/alpha.v1.product-takeover.first-owner-gate.runtime-fixed-test-gate-v2.json`.
3. Create-only the canonical with fresh unpredictable `claimToken`, latest-main `startCommit`, `state=ACTIVE`, this exact promptPath/stageId/dedupKey/dedupMode.
4. Re-read and verify exact token + all metadata.
5. Only then create-only:
   `parallel/PM/STAGE_CLAIMS/ALPHA_V1_PRODUCT_TAKEOVER_P1_RUNTIME_FIXED_TEST_GATE.json`
   with the exact same token and canonical path.
6. Re-read and verify the stage claim before implementation.
7. Any create/verification failure is fail-closed. Do not retry with an invented recovery key.

## Scope

Alpha Owner-visible product only. Do not read/run/modify/test Collector, Unified Collector, Training Farm / 10训.

## Accepted inputs

W2 already delivered the maintained production fixed-draw smoke implementation and probe adapter. Do not rewrite it.

Existing class:
`ProductionHudFixedDrawSmoke`

Expected states include:
- `HUD_INJECTION_MISSING`
- `GAME_CANVAS_CONTEXT_MISSING`
- `DRAW_HOOK_NOT_FIRING`
- `DRAWING_BUFFER_INVALID`
- `DRAW_FAILED`
- `FIXED_TEST_ACTUALLY_DRAWN`
- `DISABLED`

Canonical fixed draw remains native `384x224`, center `(192,112)`, label `TEST`.

## Your only objective

Wire the permanent Alpha runtime so that when the controlled environment flag:

`WOF_ALPHA_FIXED_DRAW_SMOKE=1`

is present, it enables and continuously polls the existing maintained production fixed-smoke probe **without waiting for P1, semantic identity, screenshot tracking, enemy data, projection, or click acquisition**.

The runtime must write one raw machine-readable status artifact under `Documents\WOF_RESULTS`, for example a stable file such as `ALPHA_FIXED_DRAW_STATUS.json`, containing at least:

- current release/acceptance SHA
- runtime epoch if available
- page/target identity if available
- fixed-smoke state
- `drawHooked`
- `drawCount`
- `callbackCount`
- drawing buffer metadata
- native 384x224 / 192,112 metadata
- last error
- read-only safety fields

When the env flag is absent, normal Alpha behavior must remain unchanged.

## File boundary

Prefer only:
- `parallel/PYLAUNCH/render_authority_measurement_entry.py`
- narrowly necessary runtime orchestration module(s)
- P1-specific focused tests
- P1 SUBRESULT

Do not edit:
- `product/alpha/wof_alpha_hud.js`
- updater/bootstrap/live-mode marker files owned by P2
- W3 renderer/object authority
- enemy/semantic/danger logic
- `alpha-live` branch ref

## Acceptance

Prove with focused tests that:

A. gate flag OFF leaves existing path unchanged;
B. gate flag ON reaches fixed-smoke probe without P1 prerequisites;
C. raw status artifact reports each fail-closed state without false green;
D. only `FIXED_TEST_ACTUALLY_DRAWN` + real drawCount/hook can count as draw success;
E. read-only safety remains `ramWrites=0`, `inputInjection=false`;
F. no Owner DevTools/manual environment action is introduced.

## Exit

Deliver integration-ready commit + durable P1 SUBRESULT, then close canonical and stage with the exact token as COMPLETE, or return one precise external BLOCKED.

Do not ask Owner to test. Do not move `alpha-live`. Do not stop at analysis or one patch.

# Alpha V1 Product Takeover P2 — Permanent Launcher Gate Mode

stageId: `ALPHA_V1_PRODUCT_TAKEOVER_P2_PERMANENT_LAUNCHER_GATE_MODE`
dedupProtocol: `v2`
dedupKey: `alpha.v1.product-takeover.first-owner-gate.permanent-launcher-gate-mode-v2`
dedupMode: `exclusive`

Repository: `ouyong520/wof-ai-private`

Parent authority:
`parallel/PM/ALPHA_V1_PRODUCT_TAKEOVER_FIRST_OWNER_GATE_PARALLEL_3_WORKER_V2_DISPATCH.md`

## Dedup preflight

Before any implementation/test work:

1. Read latest `main`, this prompt, parent dispatch, and `parallel/PM/STAGE_DEDUP_GUARD.md`.
2. Confirm no canonical exists at:
   `parallel/PM/DEDUP_CLAIMS/alpha.v1.product-takeover.first-owner-gate.permanent-launcher-gate-mode-v2.json`.
3. Create-only canonical with fresh unpredictable `claimToken`, latest-main `startCommit`, `state=ACTIVE`, and exact metadata from this prompt.
4. Re-read and verify exact token + fields.
5. Then create-only:
   `parallel/PM/STAGE_CLAIMS/ALPHA_V1_PRODUCT_TAKEOVER_P2_PERMANENT_LAUNCHER_GATE_MODE.json`
   using the same token.
6. Re-read and verify stage claim before implementation.
7. Any claim create/verification failure is fail-closed. Do not invent recovery metadata.

## Scope

Alpha Owner-visible product only. Do not read/run/modify/test Collector, Unified Collector, Training Farm / 10训.

## Accepted W1 behavior that must remain

- zero-state bootstrap from `%LOCALAPPDATA%\WOF_ALPHA_CURRENT_MAIN` absent/empty;
- GitHub update transport over SSH port 22, not Git HTTPS/443;
- preserve `%USERPROFILE%\.ssh` and unrelated VPS keys;
- one permanent Desktop `WOF_ALPHA_TEST.cmd`;
- controlled `alpha-live` update pointer;
- Alpha-runtime-only restart while preserving Browser/WOF when safe;
- updater self-update safety.

Do not redesign W1.

## Your only objective

Add one repository-controlled live-mode marker/config for the first Owner gate and make the permanent launcher/updater consume it automatically.

For the first candidate the marker must resolve to a fixed-draw gate mode which causes the launched Alpha runtime to receive:

`WOF_ALPHA_FIXED_DRAW_SMOKE=1`

The Owner must **not** set environment variables, edit files, choose versions, or select modes manually.

Requirements:

1. The live-mode marker is fetched as part of controlled `alpha-live` content.
2. Unknown/malformed mode fails closed to normal/safe behavior with one clear status reason.
3. When mode is `fixed-draw-first-gate`, launcher sets the runtime flag only for that Alpha process.
4. When future marker returns to normal, the same permanent launcher stops setting the flag automatically.
5. No new desktop launcher, ZIP, or version-specific CMD is created.
6. The live-mode name and current release SHA are exposed in the existing Owner results/status surface without taking over P3 feedback aggregation ownership.
7. Existing Browser/WOF reuse and SSH/22 update behavior remain intact.

## File boundary

Prefer only:
- `parallel/PYLAUNCH/owner_live_retest_loop.ps1`
- `parallel/PYLAUNCH/install_live_retest_once.ps1` only if strictly necessary
- one narrow repo-controlled Alpha live-mode marker/config file
- P2-specific focused tests
- P2 SUBRESULT

Do not edit:
- `product/alpha/wof_alpha_hud.js`
- P1 runtime probe/orchestration files
- P3 feedback/acceptance harness files
- W3 renderer/object authority
- `alpha-live` ref itself

## Acceptance

Prove with focused tests that:

A. zero-state/bootstrap contract is not regressed;
B. SSH/22-only update path remains;
C. normal mode does not set the smoke flag;
D. fixed-draw-first-gate mode does set it automatically;
E. malformed/unknown marker does not accidentally enable smoke;
F. Browser/WOF is not deliberately killed by this mode handoff;
G. Owner still has exactly one permanent launcher path.

## Exit

Deliver integration-ready commit + durable P2 SUBRESULT, then close canonical/stage with exact token as COMPLETE, or return one precise external BLOCKED.

Do not ask Owner to test. Do not move `alpha-live`. Do not stop at analysis or one patch.

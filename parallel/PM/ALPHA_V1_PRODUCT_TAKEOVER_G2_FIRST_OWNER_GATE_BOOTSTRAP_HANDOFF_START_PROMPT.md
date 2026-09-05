# Alpha V1 Product Takeover G2 — First Owner-Gate Bootstrap / Handoff

stageId: `ALPHA_V1_PRODUCT_TAKEOVER_G2_FIRST_OWNER_GATE_BOOTSTRAP_HANDOFF`
dedupProtocol: `v2`
dedupKey: `alpha.v1.product-takeover.first-owner-gate-bootstrap-handoff`
dedupMode: `exclusive`

Repository: `ouyong520/wof-ai-private`

Parent authority:
`parallel/PM/ALPHA_V1_PRODUCT_TAKEOVER_FIRST_OWNER_GATE_3_WORKER_DISPATCH.md`

Baseline before this dispatch: `f63f53042f555d4f0e0221a0dc165aa51f7c5add`

## Scope isolation

Alpha Owner-visible product only. Do not read, run, modify, test, schedule, or use evidence from Collector, Unified Collector, Training Farm / 10训.

## Dedup-v2 gate

Before task work, re-read latest `main`, parent dispatch, `parallel/PM/STAGE_DEDUP_GUARD.md`, W1/W2 durable subresults, current `alpha-live`, and recent equivalent claims/commits.

If already satisfied, return `ALREADY COMPLETE — SAFE TO CLOSE`.

Otherwise create-only acquire:
`parallel/PM/DEDUP_CLAIMS/alpha.v1.product-takeover.first-owner-gate-bootstrap-handoff.json`

with fresh token/latest-main startCommit; re-read current main and verify exact v2 ownership. Then create-only acquire and verify:
`parallel/PM/STAGE_CLAIMS/ALPHA_V1_PRODUCT_TAKEOVER_G2_FIRST_OWNER_GATE_BOOTSTRAP_HANDOFF.json`

No implementation/tests before both exact-token checks pass. Fail closed on any create/verification failure; do not invent recovery.

## Existing accepted W1 behavior

W1 already established:
- true zero-state bootstrap from `%LOCALAPPDATA%\WOF_ALPHA_CURRENT_MAIN` absent;
- SSH/22 Git transport, no Git HTTPS/443 dependency;
- preservation of `%USERPROFILE%\.ssh` and unrelated VPS keys;
- one permanent Desktop `WOF_ALPHA_TEST.cmd`;
- controlled `alpha-live` polling;
- Alpha-runtime-only restart and Browser/WOF reuse when safe;
- `Documents\WOF_RESULTS\LATEST_ALPHA_FEEDBACK.txt`.

Do not redesign or replace W1.

## Objective

Make the permanent updater/launcher hand off a **repo-controlled first Owner gate mode** to G1 without requiring a new launcher or manual flags from Owner.

Canonical first-gate runtime contract:
`WOF_ALPHA_FIXED_DRAW_SMOKE=1`

G2 owns how the controlled `alpha-live` content declares this mode; G1 owns how runtime consumes it.

## Required behavior

1. Add one simple repo-controlled Alpha live-mode marker/config under the Alpha/PYLAUNCH product path (for example a small JSON file) with explicit schema/version and a boolean/enum for the fixed-draw first gate.
2. `owner_live_retest_loop.ps1` must read the marker from the currently checked-out controlled release and set `WOF_ALPHA_FIXED_DRAW_SMOKE=1` only when that release explicitly requests the first fixed-draw gate.
3. Missing/malformed marker must fail safe to normal mode, not silently force smoke.
4. Owner must not type environment variables or choose modes.
5. Preserve the same permanent Desktop `WOF_ALPHA_TEST.cmd` and zero-state `WOF_ALPHA_SETUP_ONCE.cmd` flow.
6. Preserve GitHub SSH port 22 and the bounded Alpha SSH config block; do not touch unrelated keys.
7. Preserve Alpha-only process restart and Browser/WOF reuse behavior.
8. Update `LATEST_ALPHA_FEEDBACK.txt` (or its generated content) so the active release SHA/live mode and the path to G1's fixed-smoke machine status are obvious. Do not make Owner hunt internal JSON.
9. Mode must be removable by a later controlled release simply by changing the repo marker; no new launcher download.
10. Do not move `alpha-live` in this worker; G3 owns promotion.

## File ownership

G2 owns bootstrap/updater handoff files only, principally:
- `parallel/PYLAUNCH/owner_live_retest_loop.ps1`;
- one small Alpha live-mode marker/config file;
- `WOF_ALPHA_SETUP_ONCE.cmd`, `WOF_ALPHA_TEST.cmd`, or `install_live_retest_once.ps1` only if strictly required to preserve first-install behavior;
- focused tests and G2 SUBRESULT.

Do not edit:
- `product/alpha/wof_alpha_hud.js`;
- `parallel/PYLAUNCH/wof_launcher/production_p1_overlay.py`;
- G1 runtime entry/status logic;
- W3 renderer/object capture/anchor files;
- P1/enemy/semantic/danger logic;
- branch refs.

## Acceptance

Focused tests must prove:
- zero-state bootstrap contract is not regressed;
- SSH/22/no-443 update contract remains intact;
- marker absent/malformed => no smoke env;
- fixed-gate marker => `WOF_ALPHA_FIXED_DRAW_SMOKE=1` reaches Alpha runtime launch;
- later normal marker => smoke env removed without changing permanent launcher;
- latest feedback clearly identifies release/mode/status path;
- no Browser kill or unrelated SSH-key mutation is introduced.

Do not run broad historical QA. Do not ask Owner to test from this worker.

## Exit

Deliver one integration-ready commit + durable G2 SUBRESULT and close canonical/stage claims with exact token, or precise blocker. Stop only at SUBCOMPLETE/COMPLETE/precise BLOCKED.
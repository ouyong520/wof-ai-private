# Alpha V1 Product Takeover W1 — Owner Permanent Live-Test Bootstrap

stageId: `ALPHA_V1_PRODUCT_TAKEOVER_W1_OWNER_PERMANENT_LIVE_TEST_BOOTSTRAP`
dedupProtocol: `v2`
dedupKey: `alpha.v1.product-takeover.owner-permanent-live-test-bootstrap`
dedupMode: `exclusive`

Repository: `ouyong520/wof-ai-private`

Parent PM authority:
`parallel/PM/ALPHA_V1_PRODUCT_TAKEOVER_CONVERGENCE_3_WORKER_DISPATCH.md`

Authority baseline before takeover dispatch: `747c5b09d7a3d510a2df4bb8f9cb480ca8101da4`

## Scope isolation

Alpha Owner-visible product only. Do not read, run, modify, test, schedule, or use evidence from Collector, Unified Collector, Training Farm / 10训.

## Dedup-v2 execution gate

Before task work:

1. Re-read latest `main`, parent takeover dispatch, `parallel/PM/STAGE_DEDUP_GUARD.md`, relevant results/claims, and recent equivalent commits.
2. If equivalent stop condition is already satisfied, return `ALREADY COMPLETE — SAFE TO CLOSE`.
3. Otherwise atomically create-only acquire:
   `parallel/PM/DEDUP_CLAIMS/alpha.v1.product-takeover.owner-permanent-live-test-bootstrap.json`
   using a fresh unpredictable `claimToken` and latest-main `startCommit`.
4. Re-read the canonical claim from current `main` and verify exact schema, dedupKey, effectiveDedupKey, dedupMode, stageId, promptPath, claimToken, and `state=ACTIVE`.
5. Only after canonical verification, create-only acquire the matching stage claim:
   `parallel/PM/STAGE_CLAIMS/ALPHA_V1_PRODUCT_TAKEOVER_W1_OWNER_PERMANENT_LIVE_TEST_BOOTSTRAP.json`
6. If either acquisition/verification fails, follow dedup v2 and stop; do not invent another key or recovery.

## Objective

Make Owner testing a one-time installation followed by one permanent launcher. The Owner must never again download a new Alpha ZIP/CMD for each fix.

The Owner has explicitly deleted:
`%LOCALAPPDATA%\WOF_ALPHA_CURRENT_MAIN`

Therefore bootstrap must genuinely succeed from a missing/empty managed directory; it may not depend on an old `.git`, old clone, or old managed runtime.

## Required behavior

- One bootstrap entry establishes the managed Alpha environment from zero state.
- Do not require an already existing managed `.git` repository.
- Do not depend on Git HTTPS/443.
- Use GitHub SSH port 22 for the Alpha update channel.
- Preserve `%USERPROFILE%\.ssh`.
- Reuse existing `wof_alpha_github_ed25519` when valid.
- Never delete/overwrite unrelated keys, including VPS keys.
- If the Alpha key is absent, generate only the dedicated Alpha key and reduce the one unavoidable GitHub authorization to one clear step.
- Install exactly one permanent Desktop entry: `WOF_ALPHA_TEST.cmd`.
- After install, Owner workflow is: run once -> test -> send screenshot/feedback -> keep the same controller/entry -> receive automatic update/restart.
- Separate Owner live releases from arbitrary development/docs commits. Prefer controlled `alpha-live` or an equivalent explicit release pointer.
- Do not restart Owner runtime for every unrelated `main` commit.
- On live update, stop/restart Alpha controller/runtime only; preserve current browser/WOF page whenever technically safe.
- Updater must self-update safely.
- Keep results under `Documents\WOF_RESULTS` and provide one obvious latest-feedback artifact/path.
- If Git/Python/SSH authorization/browser prerequisite is genuinely missing, emit one precise actionable message.

## File ownership

W1 owns only Owner delivery/update/bootstrap files, principally:

- `WOF_ALPHA_SETUP_ONCE.cmd`
- `WOF_ALPHA_TEST.cmd`
- `parallel/PYLAUNCH/install_live_retest_once.ps1`
- `parallel/PYLAUNCH/owner_live_retest_loop.ps1`
- at most one narrowly named bootstrap/update helper if required
- focused tests/docs/W1 SUBRESULT

Do not modify HUD drawing, head tracker/anchor algorithms, renderer/object authority, enemy target logic, danger logic, Collector, or Training Farm.

## Acceptance

Implementation-owned acceptance must prove:

A. bootstrap succeeds when `%LOCALAPPDATA%\WOF_ALPHA_CURRENT_MAIN` is absent;
B. GitHub update channel does not require HTTPS/443;
C. same `WOF_ALPHA_TEST.cmd` detects a new controlled live release;
D. update is applied and Alpha runtime/controller restarts automatically;
E. updater self-update is safe;
F. Owner does not need a new ZIP/CMD/path for subsequent fixes.

Windows networking/auth that cannot be emulated may remain one narrow Owner gate, but do not send the Owner back into a manual download chain.

## Exit

Deliver one integration-ready commit + durable W1 SUBRESULT and close canonical/stage claims with the exact token, or return a precise external blocker.

Do not stop at analysis, a single patch, or a single test PASS.

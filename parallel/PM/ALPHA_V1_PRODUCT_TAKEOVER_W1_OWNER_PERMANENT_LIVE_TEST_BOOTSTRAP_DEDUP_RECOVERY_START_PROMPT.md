# Alpha V1 Product Takeover W1 — Dedup Claim Recovery After Stage-Create Race

stageId: `ALPHA_V1_PRODUCT_TAKEOVER_W1_OWNER_PERMANENT_LIVE_TEST_BOOTSTRAP_DEDUP_RECOVERY_V1`
dedupProtocol: `v2`
dedupKey: `alpha.v1.product-takeover.owner-permanent-live-test-bootstrap.claim-recovery-v1`
dedupMode: `exclusive`

Repository: `ouyong520/wof-ai-private`

Parent product authority:
`parallel/PM/ALPHA_V1_PRODUCT_TAKEOVER_CONVERGENCE_3_WORKER_DISPATCH.md`

Original W1 prompt:
`parallel/PM/ALPHA_V1_PRODUCT_TAKEOVER_W1_OWNER_PERMANENT_LIVE_TEST_BOOTSTRAP_START_PROMPT.md`

Superseded blocked canonical key:
`alpha.v1.product-takeover.owner-permanent-live-test-bootstrap`

Superseded blocked canonical path:
`parallel/PM/DEDUP_CLAIMS/alpha.v1.product-takeover.owner-permanent-live-test-bootstrap.json`

Blocked evidence commit:
`8137541da7871be368af001b27db28fdb2b03c8b`

Blocker being recovered:
`DEDUP_V2_STAGE_CLAIM_CREATE_RACE`

## PM authorization

This is a **dedup ownership-continuity recovery only**. It is not Alpha V4/V5, not a new product recovery, and does not change W1 product scope, design, acceptance, or Owner UX.

The prior canonical claim was lawfully acquired and then lawfully closed `BLOCKED` because the matching stage-claim create-only operation returned GitHub 409 after unrelated concurrent main advancement. The old canonical remains historical evidence and must not be edited, deleted, reused, or returned to ACTIVE.

PM explicitly authorizes one fresh dedup-v2 generation so W1 can obtain a complete canonical+stage ownership pair and resume the original W1 implementation.

## Scope isolation

Alpha Owner-visible product only. Do not read, run, modify, test, schedule, or use evidence from Collector, Unified Collector, Training Farm / 10训.

## Mandatory recovery preflight

Before task work:

1. Re-read latest `main`, this recovery prompt, the original W1 prompt, `parallel/PM/STAGE_DEDUP_GUARD.md`, and the blocked prior canonical claim.
2. Verify the prior canonical remains `BLOCKED` with blocker `DEDUP_V2_STAGE_CLAIM_CREATE_RACE` and do not modify it.
3. If the original W1 stop condition has already been independently satisfied on current main, return `ALREADY COMPLETE — SAFE TO CLOSE` without claiming recovery.
4. Confirm no existing recovery canonical exists at:
   `parallel/PM/DEDUP_CLAIMS/alpha.v1.product-takeover.owner-permanent-live-test-bootstrap.claim-recovery-v1.json`.
5. Atomically create-only acquire that recovery canonical using a fresh unpredictable `claimToken` and latest-main `startCommit`.
6. Re-read current main and verify exact schema, dedupKey, effectiveDedupKey, dedupMode, stageId, promptPath, claimToken, and `state=ACTIVE`.
7. Only after canonical verification, create-only acquire:
   `parallel/PM/STAGE_CLAIMS/ALPHA_V1_PRODUCT_TAKEOVER_W1_OWNER_PERMANENT_LIVE_TEST_BOOTSTRAP_DEDUP_RECOVERY_V1.json`
   referencing the same recovery canonical and exact token.
8. Re-read and verify the recovery stage claim before any implementation/test work.
9. If either fresh recovery claim acquisition/verification fails, fail closed under `STAGE_DEDUP_GUARD.md`; do not invent another key.

## Work to resume after ownership is valid

After the recovery canonical and stage claim are both verified, continue the **original W1 objective unchanged**:

- bootstrap from `%LOCALAPPDATA%\WOF_ALPHA_CURRENT_MAIN` absent/empty;
- one-time setup, then one permanent `WOF_ALPHA_TEST.cmd`;
- no Git HTTPS/443 dependency;
- use GitHub SSH port 22;
- preserve `%USERPROFILE%\.ssh` and reuse `wof_alpha_github_ed25519` when valid;
- never overwrite unrelated SSH/VPS keys;
- controlled Alpha live update pointer/channel rather than arbitrary main churn;
- automatic update + Alpha runtime/controller restart while preserving Browser/WOF when safe;
- updater self-update safety;
- `Documents\WOF_RESULTS` with one obvious latest-feedback artifact/path;
- no new ZIP/CMD handoff on each fix.

All file ownership and acceptance criteria from the original W1 prompt remain authoritative.

## Exit

Deliver one integration-ready W1 implementation commit + durable W1 SUBRESULT and close **the recovery canonical and recovery stage claim** with the exact recovery token, or return a new precise external blocker.

Do not alter the historical blocked canonical except to read it as superseded evidence. Do not open another product version/recovery. Do not stop at analysis, a single patch, or a single test PASS.

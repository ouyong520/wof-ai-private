# Alpha V1 P23 — Post-Promotion Verification / Project Close Harness

This directory is the P23 verification-only closure harness. It never moves `alpha-live`, never rewrites the permanent W1 updater/launcher, never executes rollback, and never turns repository fixtures into a real acceptance PASS.

## Later Owner/PM command

Run:

```text
parallel\OWNER_RELEASE_POSTVERIFY\WOF_ALPHA_POST_PROMOTION_VERIFY.cmd
```

The command reads the exact P19 final candidate/attestation, P17/P16/P18 evidence, W3 live qualification, P20 real visual receipt + promotion artifacts, P22 dynamic-state evidence, the current `alpha-live` ref, and the permanent W1 managed repo at `%LOCALAPPDATA%\WOF_ALPHA_CURRENT_MAIN\repo`. It writes under `Documents\WOF_RESULTS`:

- `ALPHA_POST_PROMOTION_VERIFICATION.json/.md`
- `ALPHA_V1_FINAL_CLOSE_BUNDLE.json/.md` only when every real close gate is proven.

Incomplete evidence produces exactly one fail-closed next state. `NOT_OBSERVED` / `UNPROVEN_SIGNAL` P22 coverage gaps remain visible and are never silently converted to PASS.

## Real post-promotion confirmation input

Final close additionally requires an actual later real Owner evidence input named `ALPHA_POST_PROMOTION_OWNER_CONFIRMATION.json` (or an explicit `--post-promotion-confirmation` path). P23 does **not** manufacture this file. The verifier accepts it only when it is an object with:

- `schema = wof-alpha-post-promotion-owner-confirmation-v1`, `version = 1`;
- `fixtureMode = false`;
- `realWofPostPromotionAcceptance = PASS` and `ownerConfirmation = PASS`;
- exact `promotedCommit`, `managedRepoHead`, `packageVersion`, `candidateSha256`;
- exact `promotionPlanHash`, `promotionResultSha256`, and runtime/renderer `identity`;
- optional `p22EvidenceSha256`, which must match when present;
- safety: `readOnly=true`, `ramWrites=0`, `inputInjection=false`, `legacySpatialFallback=false`.

A fixture/non-real confirmation is intentionally classified `WAITING_FOR_POST_PROMOTION_ACCEPTANCE`, never `ALPHA_V1_FINAL_COMPLETE`.

## State / safety boundary

The close state machine uses the P23 authority states:

`WAITING_FOR_P19_CANDIDATE`, `WAITING_FOR_W3_LIVE_PASS`, `WAITING_FOR_OWNER_VISUAL_PASS`, `WAITING_FOR_PROMOTION`, `WAITING_FOR_PERMANENT_CHANNEL_CONFIRMATION`, `WAITING_FOR_POST_PROMOTION_ACCEPTANCE`, `REJECTED_EVIDENCE_MISMATCH`, `READY_TO_CLOSE`, and `ALPHA_V1_FINAL_COMPLETE`.

`ALPHA_V1_FINAL_COMPLETE` is emitted only after exact candidate/attestation hashes, P17 READY-before-visual ordering, W3 PASS, P18 draw acknowledgement, real P20 visual PASS, confirmed non-force/fast-forward P20 promotion, current `alpha-live`, rollback ancestry/files, permanent W1 repo/launcher convergence, P22 evidence, and real post-promotion confirmation all agree.

Observation timestamps are outside the deterministic receipt/close hash cores. For fixed evidence inputs the receipt/close hashes remain deterministic.

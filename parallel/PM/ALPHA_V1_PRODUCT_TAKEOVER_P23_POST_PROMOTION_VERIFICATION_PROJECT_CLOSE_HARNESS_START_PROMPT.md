stageId: `ALPHA_V1_PRODUCT_TAKEOVER_P23_POST_PROMOTION_VERIFICATION_PROJECT_CLOSE_HARNESS`
dedupProtocol: `v2`
dedupKey: `alpha.v1.product-takeover.post-promotion-verification-project-close-harness-v1`
dedupMode: `exclusive`
resultProtocol: `wof-alpha-worker-result-v1`
resultJsonPath: `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P23_POST_PROMOTION_VERIFICATION_PROJECT_CLOSE_HARNESS_RESULT.json`
resultMdPath: `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P23_POST_PROMOTION_VERIFICATION_PROJECT_CLOSE_HARNESS_RESULT.md`
terminalCommitPrefix: `WORKER_RESULT ALPHA_V1_PRODUCT_TAKEOVER_P23_POST_PROMOTION_VERIFICATION_PROJECT_CLOSE_HARNESS`

# Alpha V1 Product Takeover P23 — Post-Promotion Verification + Project Close Harness

Repository: `ouyong520/wof-ai-private`

This is a long final-release closure module. Implement the complete post-promotion verifier and project-close evidence harness now, but do **not** move `alpha-live`, do not perform real promotion, and do not claim Alpha V1 COMPLETE before the real gates exist.

Read latest `main`, `AGENTS.md`, PM testing cadence, dedup guard, current dispatch, and at minimum:
- P19 COMPLETE final candidate/result/latest pointer/attestation;
- P20 COMPLETE Owner visual confirmation + promotion gate result and implementation;
- P21 staging prompt/result if available;
- P22 dynamic-state coverage prompt/result if available;
- P17/P16/P18 final automatic acceptance evidence contracts;
- W3 qualification result/runner;
- W1 permanent Owner bootstrap result;
- `WOF_ALPHA_SETUP_ONCE.cmd`;
- `parallel/PYLAUNCH/owner_live_retest_loop.ps1`;
- permanent Owner feedback/status paths;
- current controlled `alpha-live` ref behavior.

## Ownership

Perform normal dedup-v2 create-only canonical claim -> exact-token re-read -> create-only stage claim -> exact-token re-read. Fail closed. Do not invent recovery.

Do not modify P19/P20/P21/P22/W3 claims or RESULT files.

## Goal

Implement the final verifier that will later prove the release actually reached the permanent Owner channel and that the Alpha V1 project is safe to close after a real P20 promotion.

Required future chain:

`P19 exact final candidate`
`+ P17/P18/P22 acceptance evidence`
`+ W3 live PASS`
`+ P20 real Owner visual PASS receipt`
`+ P20 confirmed promotion result`
`-> exact alpha-live ref now points at the intended promoted commit`
`-> permanent W1 managed repo/update channel observes/applies that same commit`
`-> package/runtime identity remains exact and safety unchanged`
`-> final post-promotion evidence bundle`
`-> ALPHA_V1_FINAL_COMPLETE only when every real gate is proven`.

At repository implementation time, actual state will likely remain `WAITING_FOR_PROMOTION` or `WAITING_FOR_REAL_ACCEPTANCE`. That is correct.

## Workstream A — exact post-promotion release verifier

Create a new isolated area, preferably `parallel/OWNER_RELEASE_POSTVERIFY/`.

Implement a verifier that consumes:
- P19 final candidate + attestation + latest pointer;
- P20 promotion plan and confirmed promotion-result artifact when later present;
- P20 real Owner visual receipt;
- current observed remote/local `alpha-live` ref;
- W1 permanent managed-repo HEAD / feedback evidence when later available;
- P17 final acceptance bundle;
- P16/P18 evidence;
- P22 dynamic-state coverage evidence when present.

A post-promotion `RELEASE_MATCHED` state requires all of the following:
1. P20 promotion result proves the exact plan hash was applied successfully.
2. Promotion target commit equals P19 candidate source commit (or exact explicitly attested final release commit if P20 contract defines an attested successor).
3. Current `alpha-live` equals the promoted target commit.
4. Promotion `from` and rollback/previous commit metadata are retained.
5. Current `alpha-live` movement was non-force / fast-forward as proven by P20 artifacts.
6. W1 permanent required release files exist at the promoted commit.
7. Candidate/attestation hashes still match exact P19 evidence.
8. Real Owner visual receipt is PASS, promotionEligible, and bound to the same candidate/acceptance bundle.
9. W3 live qualification is PASS for the same exact authority/runtime/renderer identity represented by the acceptance bundle.
10. P17 automatic acceptance reached `READY_FOR_OWNER_VISUAL_CONFIRMATION` before the real visual PASS.
11. P18 maintained draw evidence was acknowledged for the same identity.
12. Safety remains readOnly=true, ramWrites=0, inputInjection=false, legacySpatialFallback=false.

Any mismatch must fail closed and produce a precise state/reason.

## Workstream B — permanent W1 channel convergence proof

Implement a later-use verification mode that can establish the permanent Owner updater actually converged to the promoted release without requiring a new install path.

Allowed evidence includes:
- permanent managed repo HEAD;
- `Documents\WOF_RESULTS\LATEST_ALPHA_FEEDBACK.txt` fields;
- exact package/runtime status/evidence already emitted by the promoted candidate;
- P16 canonical Owner status/evidence;
- P18 draw evidence;
- P20 promotion result.

Require:
- managed repo HEAD == promoted `alpha-live` commit;
- feedback/status identifies the same commit/package when fields are available;
- no temporary P21 staging checkout is mistaken for the permanent W1 managed repo;
- permanent Desktop launcher path remains the existing `WOF_ALPHA_TEST.cmd` path;
- no new ZIP/versioned launcher/manual branch selection is introduced.

If permanent convergence evidence is unavailable because the Owner has not yet run the permanent launcher after promotion, state `WAITING_FOR_PERMANENT_CHANNEL_CONFIRMATION`; do not infer success from the remote ref alone.

## Workstream C — post-promotion runtime acceptance receipt

Provide a bounded post-promotion receipt builder that records:
- promoted commit;
- package version/candidate/attestation hashes;
- alpha-live before/after/current commit;
- P20 promotion plan/result hashes;
- real Owner visual receipt hash/verdict;
- W3/P17/P16/P18/P22 evidence hashes/states;
- permanent managed repo HEAD if available;
- permanent feedback/status summary;
- rollback commit;
- safety flags;
- timestamp;
- deterministic receipt hash.

Repository fixtures must never mark `realWofPostPromotionAcceptance=PASS` without an actual later real evidence input.

## Workstream D — rollback readiness verification

Do not implement another updater or competing rollback mechanism. Verify the existing release artifacts retain an exact rollback point and that the promoted release remains compatible with W1's existing local last-known-good behavior.

Add deterministic checks that:
- previous alpha-live commit is present and not equal to promoted commit;
- rollback metadata is bound to the same promotion plan/result;
- required W1 files exist at both promoted target and rollback point where repository evidence permits;
- no force-push requirement is introduced;
- rollback verification never auto-executes a real remote ref move in this stage.

If a later rollback is actually required, P23 should output the exact evidence/command boundary but not invent a new release channel.

## Workstream E — final project-close state machine

Implement a deterministic close state machine with explicit states such as:
- `WAITING_FOR_P19_CANDIDATE`
- `WAITING_FOR_W3_LIVE_PASS`
- `WAITING_FOR_OWNER_VISUAL_PASS`
- `WAITING_FOR_PROMOTION`
- `WAITING_FOR_PERMANENT_CHANNEL_CONFIRMATION`
- `WAITING_FOR_POST_PROMOTION_ACCEPTANCE`
- `REJECTED_EVIDENCE_MISMATCH`
- `READY_TO_CLOSE`
- `ALPHA_V1_FINAL_COMPLETE`

`ALPHA_V1_FINAL_COMPLETE` may be emitted only when all real gates are present and consistent, including permanent channel convergence and the real post-promotion Owner confirmation required by PM policy.

Do not allow repository fixtures, fake receipts, draw acknowledgements, package integrity, or remote ref equality alone to reach FINAL COMPLETE.

If P22 coverage evidence exists, include it in the final close bundle. Core dynamic-state coverage gaps should be reported explicitly. Do not silently convert `NOT_OBSERVED` rare states into PASS. PM may define whether a gap is informational or close-blocking, but the evidence must remain truthful.

## Workstream F — final one-command verification UX

Provide a Windows-friendly command such as `WOF_ALPHA_POST_PROMOTION_VERIFY.cmd` that later performs **verification only**:
1. discovers the exact P19/P20 artifacts;
2. reads current alpha-live and permanent managed repo state;
3. reads latest acceptance/visual/dynamic-state evidence;
4. writes the final post-promotion bundle;
5. prints one concise Chinese Owner/PM status;
6. never moves alpha-live and never rewrites the permanent launcher.

If the real gates are incomplete, the command must explain the single next missing gate rather than dumping implementation details.

## Evidence output

Use deterministic JSON + Markdown/text with fixtureable output root. Suggested:
- `ALPHA_POST_PROMOTION_VERIFICATION.json`
- `ALPHA_POST_PROMOTION_VERIFICATION.md`
- `ALPHA_V1_FINAL_CLOSE_BUNDLE.json`
- `ALPHA_V1_FINAL_CLOSE_BUNDLE.md`

For fixed inputs, hashes/output must be deterministic except explicitly separated observation timestamps.

## Write boundaries

Expected new files only under `parallel/OWNER_RELEASE_POSTVERIFY/` plus narrow tests/docs.

Do not modify:
- P20 `parallel/OWNER_RELEASE/`;
- P21 `parallel/OWNER_STAGING/` while ACTIVE;
- P22 files if ACTIVE;
- P19 candidate/attestation builder;
- P17/P18/P15 runtime/HUD;
- W3 producer/qualification;
- W1 permanent updater/setup;
- `alpha-live` ref.

If a genuine upstream evidence-contract defect prevents verification, fail closed and document the exact missing field rather than crossing ownership.

## Focused checks only

Implementation first. Run only narrow checks:
- Python/CMD syntax/compile;
- waiting-state fixtures for absent promotion/visual/W3/permanent convergence;
- exact candidate/promotion/alpha-live match fixture;
- stale/mismatched promotion plan/result rejection;
- permanent managed repo staging-vs-live disambiguation fixture;
- rollback metadata consistency fixture;
- deterministic close-bundle hash fixture;
- explicit fixture-proof that fake/fixture receipts cannot reach FINAL COMPLETE;
- safety invariant fixture.

No broad QA, no real WOF, no real alpha-live mutation.

## Terminal result

Write exactly:
- `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P23_POST_PROMOTION_VERIFICATION_PROJECT_CLOSE_HARNESS_RESULT.json`
- `parallel/PM/RESULTS/ALPHA_V1_PRODUCT_TAKEOVER_P23_POST_PROMOTION_VERIFICATION_PROJECT_CLOSE_HARNESS_RESULT.md`

Record implementation commits, changed files, focused checks, integrationReady, current truthful close state, exact later real gates, safety, and nextAction.

Successful repository implementation should normally be COMPLETE/integration-ready while the **runtime close state remains WAITING**, because no real promotion/Owner final confirmation has happened yet.
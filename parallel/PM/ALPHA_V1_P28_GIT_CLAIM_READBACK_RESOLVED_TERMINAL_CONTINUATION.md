# Alpha V1 P28 — Git Claim Readback Resolved Terminal Continuation

Stage: `ALPHA_V1_PRODUCT_TAKEOVER_P28_FINAL_ACCEPTANCE_SESSION_PROVENANCE_DURABLE_REBUILD`

Existing claimToken: `69884841cf571855163ab7db0ac663dc`

This is a continuation of the same ACTIVE P28 task. Do not create a new claim and do not recover/reopen P26.

## PM fresh readback

Latest-main Git authority was re-read after the P28 fresh-focused PASS checkpoint.

Canonical claim:
`parallel/PM/DEDUP_CLAIMS/alpha.v1.product-takeover.final-acceptance-session-provenance-durable-rebuild-v1.json`

Stage claim:
`parallel/PM/STAGE_CLAIMS/ALPHA_V1_PRODUCT_TAKEOVER_P28_FINAL_ACCEPTANCE_SESSION_PROVENANCE_DURABLE_REBUILD.json`

Both files are present in Git, both carry exact claimToken `69884841cf571855163ab7db0ac663dc`, and both are currently `ACTIVE`.

Therefore the PROGRESS blocker `P28_LIVE_CLAIM_FILES_NOT_MOUNTED_IN_CURRENT_CONNECTED_EXECUTION_ENVIRONMENT` is resolved for Git-governed terminal publication. Do not require a separate Windows-local claim-path mount if the repository governance files above remain the authoritative exact-token claim records under the current dedup-v2 protocol.

## Tested candidate already complete

Do not rerun tests unless implementation bytes changed.

Exact tested candidate:
`5e373a21292f22be46ce8b311af9b1ec606b6874`

Exact tested tree:
`dce2ab917f6bcf9a6536d6a33f735b24074272aa`

Fresh exact-candidate evidence already durably records:
- candidate/tree/blob readback PASS;
- compile/syntax PASS;
- durable-session focused tests 16/16 PASS;
- compatibility provenance focused tests 20/20 PASS;
- safety/static scan PASS;
- P26 historical 13/13 not reused;
- superseded `9a02856...` evidence not reused;
- no implementation bytes changed after testing.

## Terminal-only continuation

1. Re-read latest main plus the exact canonical/stage claim files above and confirm the same token remains ACTIVE.
2. Update P28 PROGRESS to record continuation and resolved blocker; do not modify implementation.
3. Publish truthful RESULT.json and RESULT.md with `testedCommit=5e373a21292f22be46ce8b311af9b1ec606b6874` and `integrationReady=true` if no new terminal blocker appears.
4. Keep `realWofAcceptance=NOT_RUN`, `ownerVisualAcceptance=NOT_RUN`, `visibleProof=NOT_PROVEN`, `alphaLiveMoved=false`.
5. Close the exact-token canonical and stage claims using the same token; no force, no token replacement.
6. Only after RESULT and both claim closes, update PROGRESS to `TERMINAL` / `100`, result publication DONE, claim close DONE.
7. Finish with the required `WORKER_RESULT` terminal commit.

Do not rerun real WOF, do not ask Owner YES/NO, do not promote or move alpha-live, do not modify P28 implementation, and do not widen ownership.

Progress checkpointing must follow `parallel/PM/ALPHA_WORKER_PROGRESS_CHECKPOINT_PROTOCOL_V1.md`; keep `parallel/PM/PROGRESS/ALPHA_V1_PRODUCT_TAKEOVER_P28_FINAL_ACCEPTANCE_SESSION_PROVENANCE_DURABLE_REBUILD_PROGRESS.json` current at mandatory milestones and before any non-terminal stop.

Terminal reporting must follow `parallel/PM/ALPHA_WORKER_RESULT_FAST_FEEDBACK_PROTOCOL_V1.md`.

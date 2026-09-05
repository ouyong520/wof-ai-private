# Alpha V1 P33 — Post-Repair Final Candidate Rebuild Preparation — START PROMPT

StageId:
`ALPHA_V1_PRODUCT_TAKEOVER_P33_POST_REPAIR_FINAL_CANDIDATE_REBUILD_PREP`

DedupKey:
`alpha.v1.product-takeover.post-repair-final-candidate-rebuild-prep-v1`

Mission: harden the final canonical candidate build/rebuild path so the next bounded Owner retry can run a fresh candidate assembled from one exact source commit that contains all PM-accepted repair candidates, without promotion or alpha-live movement.

Fresh PM state for this dispatch:
- P29 terminal COMPLETE / PM accepted, testedCommit `c02f7e108e73665f22eb950573622acb6f452732`.
- P30 terminal COMPLETE / PM accepted, testedCommit `90094a656ab311f18b0a758716dc97c3f8df092d`.
- P31 terminal COMPLETE / PM accepted, testedCommit `423c9c6c4a54ff4abd701e1dcd8c170cc4e9d731`.
- P32 terminal BLOCKED, testedCommit `bd75c3b5f7fd20fe004fae21142a0fa19942e076`, `integrationReady=false`; its blocker is the missing direct displayed-frame native-marker renderer submission causal edge. Do not count P32 as an accepted repair candidate and do not rewrite it to PASS.
- P34 is an independent ACTIVE final-retry readiness gate and is out of P33 ownership.
- P35 is separately dispatched to assemble/verify accepted-repair integration lineage; P33 owns rebuild mechanism only and must not duplicate P35 merge/integration ownership.

Read latest main, root AGENTS.md, full dedup/progress/result protocols, current final live gate, terminal P29/P30/P31/P32 RESULT authority, P19/final canonical candidate authority and `parallel/OWNER_ONECLICK/**` build/manifest code and focused tests.

Dedup-v2: if equivalent ACTIVE/CLAIMED, return `ALREADY ACTIVE / CLAIMED — NO EXECUTION`; if COMPLETE/PASS, return `ALREADY COMPLETE — NO EXECUTION`; otherwise create canonical claim then stage claim with one fresh exact claimToken, read both back, then create PROGRESS.

Ownership is limited to final-candidate build/rebuild contract and focused deterministic tests. Do not modify P31 discovery code, P32/P36 renderer-marker code, P29 analyzer semantics, P30 staging/P16/P9 implementation files, or P35 integration-lineage artifacts.

Required work:
- make the rebuild path accept/select one exact source commit and fail closed if it is not a valid repository commit;
- require deterministic proof that every required PM-accepted tested commit is contained by the selected source commit before a candidate can be marked retry-eligible;
- current required accepted tested commits are P29 `c02f7e108e73665f22eb950573622acb6f452732`, P30 `90094a656ab311f18b0a758716dc97c3f8df092d`, and P31 `423c9c6c4a54ff4abd701e1dcd8c170cc4e9d731`;
- preserve immutable candidate identity: sourceCommit, packageVersion, candidate SHA-256, manifest content and runtime pins must read back exactly;
- stale historical P19 candidate/package bytes must never be silently reused as if they contained later repairs;
- deterministic fixtures may use synthetic/temporary ancestry graphs, but do not fabricate a final integrated source commit if P35 has not produced one;
- no promotion, no alpha-live move, no real game run, no Owner YES/NO;
- do not mutate detached staging checkout or permanent runtime state;
- preserve existing safety and package semantics; minimal repair only, no redesign of OWNER_ONECLICK.

Focused deterministic tests must cover at least:
- exact source commit containing all required tested commits => rebuild contract can proceed;
- missing one required tested commit => fail closed;
- stale pre-repair source commit => fail closed;
- manifest/sourceCommit/packageVersion/SHA mismatch => fail closed;
- deterministic repeated build metadata for identical inputs;
- P32 BLOCKED candidate is not silently treated as required/accepted;
- no alpha-live or promotion side effects.

Terminal COMPLETE means the repo-side rebuild mechanism is durable and ready to assemble the actual integrated candidate once an accepted integration source lineage exists. It does not mean that real WOF passed, Owner visual acceptance passed, P32 blocker is resolved, or alpha-live moved.

Before terminal-significant self-check create a durable tested candidate commit/tree and bind PROGRESS to it. Any implementation-byte change after test requires a new candidate and rerun of affected checks.

Progress checkpointing must follow parallel/PM/ALPHA_WORKER_PROGRESS_CHECKPOINT_PROTOCOL_V1.md; keep parallel/PM/PROGRESS/<stageId>_PROGRESS.json current at mandatory milestones and before any non-terminal stop.
Terminal reporting must follow parallel/PM/ALPHA_WORKER_RESULT_FAST_FEEDBACK_PROTOCOL_V1.md.

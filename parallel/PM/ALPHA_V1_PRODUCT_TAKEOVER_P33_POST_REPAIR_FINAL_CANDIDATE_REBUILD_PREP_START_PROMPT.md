# Alpha V1 P33 — Post-Repair Final Candidate Rebuild Preparation — START PROMPT

StageId:
`ALPHA_V1_PRODUCT_TAKEOVER_P33_POST_REPAIR_FINAL_CANDIDATE_REBUILD_PREP`

DedupKey:
`alpha.v1.product-takeover.post-repair-final-candidate-rebuild-prep-v1`

Mission: harden the final canonical candidate build/rebuild path so the next bounded Owner retry can run a fresh candidate assembled from one exact source commit that contains all PM-accepted repair candidates, without promotion or alpha-live movement.

Fresh PM state when this task is dispatched:
- P29 terminal COMPLETE / PM accepted, testedCommit `c02f7e108e73665f22eb950573622acb6f452732`.
- P30 terminal COMPLETE / PM accepted, testedCommit `90094a656ab311f18b0a758716dc97c3f8df092d`.
- P31 remains ACTIVE and owns Page/Worker/WASM association.
- P32 remains ACTIVE and owns native 1P/2P/3P marker renderer-anchor qualification.

Read latest main, root AGENTS.md, full dedup/progress/result protocols, current final live gate, P19/final canonical candidate authority and `parallel/OWNER_ONECLICK/**` build/manifest code and focused tests.

Dedup-v2: if equivalent ACTIVE/CLAIMED, return `ALREADY ACTIVE / CLAIMED — NO EXECUTION`; if COMPLETE/PASS, return `ALREADY COMPLETE — NO EXECUTION`; otherwise create canonical claim then stage claim with one fresh exact claimToken, read both back, then create PROGRESS.

Ownership is limited to final-candidate build/rebuild contract and focused deterministic tests. Do not modify P31 discovery code, P32 renderer/marker qualification code, P29 analyzer semantics, or P30 staging/P16/P9 implementation files.

Required work:
- make the rebuild path accept/select one exact source commit and fail closed if it is not a valid repository commit;
- require deterministic proof that every required accepted tested commit is contained by the selected source commit before a candidate can be marked retry-eligible;
- preserve immutable candidate identity: sourceCommit, packageVersion, candidate SHA-256, manifest content and runtime pins must read back exactly;
- stale historical P19 candidate/package bytes must never be silently reused as if they contained later repairs;
- candidate build may be prepared/tested now with deterministic fixtures, but the actual post-P31/P32 final candidate must not be falsely declared complete before those terminal dependencies exist;
- no promotion, no alpha-live move, no real game run, no Owner YES/NO;
- do not mutate detached staging checkout or permanent runtime state;
- preserve existing safety and package semantics; minimal repair only, no redesign of OWNER_ONECLICK.

Focused deterministic tests must cover at least:
- exact source commit containing all required tested commits => rebuild contract can proceed;
- missing one required tested commit => fail closed;
- stale pre-repair source commit => fail closed;
- manifest/sourceCommit/packageVersion/SHA mismatch => fail closed;
- deterministic repeated build metadata for identical inputs;
- no alpha-live or promotion side effects.

Terminal COMPLETE means the repo-side rebuild mechanism is durable and ready to assemble the actual integrated candidate after P31/P32 terminalize. It does not mean that integrated candidate already exists, real WOF passed, Owner visual acceptance passed, or alpha-live moved.

Before terminal-significant self-check create a durable tested candidate commit/tree and bind PROGRESS to it. Any implementation-byte change after test requires a new candidate and rerun of affected checks.

Progress checkpointing must follow parallel/PM/ALPHA_WORKER_PROGRESS_CHECKPOINT_PROTOCOL_V1.md; keep parallel/PM/PROGRESS/<stageId>_PROGRESS.json current at mandatory milestones and before any non-terminal stop.
Terminal reporting must follow parallel/PM/ALPHA_WORKER_RESULT_FAST_FEEDBACK_PROTOCOL_V1.md.

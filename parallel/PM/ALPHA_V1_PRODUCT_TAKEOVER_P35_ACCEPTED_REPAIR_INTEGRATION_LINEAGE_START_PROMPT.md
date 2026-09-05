# Alpha V1 P35 — Accepted Repair Integration Lineage — START PROMPT

StageId:
`ALPHA_V1_PRODUCT_TAKEOVER_P35_ACCEPTED_REPAIR_INTEGRATION_LINEAGE`

DedupKey:
`alpha.v1.product-takeover.accepted-repair-integration-lineage-v1`

Mission: assemble and prove one deterministic integration lineage for the PM-accepted repair candidates so a later final-candidate rebuild can select one exact source commit whose ancestry really contains every accepted tested commit. This task is source-lineage integration only; it does not build/promote alpha-live and does not run the real game.

Fresh PM authority:
- P29 terminal COMPLETE / PM accepted, testedCommit `c02f7e108e73665f22eb950573622acb6f452732`.
- P30 terminal COMPLETE / PM accepted, testedCommit `90094a656ab311f18b0a758716dc97c3f8df092d`.
- P31 terminal COMPLETE / PM accepted, testedCommit `423c9c6c4a54ff4abd701e1dcd8c170cc4e9d731`.
- P32 terminal BLOCKED / integrationReady=false, testedCommit `bd75c3b5f7fd20fe004fae21142a0fa19942e076`; do not count it as accepted/retry-ready and do not rewrite it to PASS.
- P33 owns OWNER_ONECLICK rebuild mechanism. P34 owns readiness gate. P36 owns native-marker renderer submit source trace. Do not touch those ownership surfaces.

Read latest main, root AGENTS.md, dedup/progress/result protocols, terminal P29/P30/P31/P32 RESULTs and exact tested commits, current live gate, and the exact changed-file/blob evidence for each accepted repair.

Dedup-v2: if equivalent ACTIVE/CLAIMED, return `ALREADY ACTIVE / CLAIMED — NO EXECUTION`; if COMPLETE/PASS, return `ALREADY COMPLETE — NO EXECUTION`; otherwise create canonical claim then stage claim with one fresh exact claimToken, read both back, then create PROGRESS.

Required work:
- create a dedicated integration candidate branch/commit lineage from latest authoritative main without rewriting history;
- prove with Git ancestry that the final integration source commit contains exact P29/P30/P31 tested commits as ancestors; cherry-pick-only equivalence is insufficient if the original tested commit is not an ancestor;
- preserve each accepted repair's tested implementation bytes. Fresh-read the repair-owned files from the integration source and compare to terminal RESULT blob identities where available; if an accepted later repair intentionally supersedes the same file, prove that precedence from terminal authority rather than guessing;
- if a merge conflict would require semantic hand-editing of accepted implementation bytes, fail closed and report the exact conflict instead of inventing a merge;
- P32 BLOCKED candidate may be read for context but must not be silently merged as a PM-accepted repair dependency;
- produce deterministic integration metadata recording latest-main base, required tested commits, ancestry checks, file/blob readback, source commit/tree and no-promotion state;
- run only focused deterministic integration regression needed to prove the accepted repair seams coexist; no broad QA.

Scope boundaries:
- do not modify OWNER_ONECLICK rebuild code (P33);
- do not modify final retry gate (P34);
- do not modify P31 discovery semantics, P29 analyzer criteria, P30 staging implementation, or P32/P36 renderer proof contracts except through conflict-free ancestry integration of the exact accepted commits;
- no real WOF/browser run, no Owner YES/NO, no promotion, no alpha-live move, no global environment changes.

Terminal COMPLETE means there is a durable integration source commit/tree whose ancestry contains P29/P30/P31 exact tested commits and whose accepted repair bytes read back correctly. It does not mean P32 blocker is resolved or final Owner retry is authorized.

Before terminal-significant self-check create/record the durable integration candidate commit/tree and exact ancestry/blob map. Any semantic byte change afterward requires a new candidate and rerun.

Progress checkpointing must follow parallel/PM/ALPHA_WORKER_PROGRESS_CHECKPOINT_PROTOCOL_V1.md; keep parallel/PM/PROGRESS/<stageId>_PROGRESS.json current at mandatory milestones and before any non-terminal stop.
Terminal reporting must follow parallel/PM/ALPHA_WORKER_RESULT_FAST_FEEDBACK_PROTOCOL_V1.md.

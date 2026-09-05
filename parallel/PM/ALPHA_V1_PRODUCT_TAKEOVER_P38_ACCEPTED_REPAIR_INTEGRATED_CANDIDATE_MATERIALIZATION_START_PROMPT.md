# Alpha V1 P38 — Accepted Repair Integrated Candidate Materialization — START PROMPT

StageId:
`ALPHA_V1_PRODUCT_TAKEOVER_P38_ACCEPTED_REPAIR_INTEGRATED_CANDIDATE_MATERIALIZATION`

DedupKey:
`alpha.v1.product-takeover.accepted-repair-integrated-candidate-materialization-v1`

Mission: consume the terminal P35 accepted-repair integration source through the terminal P33 deterministic rebuild mechanism and materialize one exact fresh integrated candidate/package provenance now, while truthfully keeping it NOT retry-eligible until the separate P36 renderer-source blocker is resolved.

Fresh PM authority:
- P33 terminal COMPLETE: rebuild mechanism testedCommit `c8c61112efbccdef5794ee68cd27767eacb72e96`;
- P35 terminal COMPLETE: exact integration sourceCommit `82b0b09ecd902f502ae5509bcb3ee5a713f43fee`, tree `e5dba33a2cd579826704d3f78ec2587ee2305a5a`;
- P35 proves exact P29/P30/P31 tested commits are true ancestors and 13/13 accepted repair blobs match;
- P32 remains terminal BLOCKED and is not an accepted repair; P36 is the separately authorized successor for the missing native-marker direct renderer causal edge;
- P34 readiness gate remains fail-closed and must not be weakened.

Read latest main, root AGENTS.md, dedup/progress/result protocols, terminal P33/P35 RESULT authority, P33 rebuild code/tests, P35 exact candidate provenance, current final-canonical pointer/manifest/candidate files and P34 readiness contract.

Dedup-v2: if equivalent P38 ACTIVE/CLAIMED, return `ALREADY ACTIVE / CLAIMED — NO EXECUTION`; if COMPLETE/PASS, return `ALREADY COMPLETE — NO EXECUTION`; otherwise create canonical claim then stage claim with one fresh exact claimToken, read both back, then create PROGRESS.

Ownership is limited to exact integrated candidate/package materialization and readback. Do not modify P36 renderer/source-trace code, P37 zero-click baseline, P29/P32 qualification semantics, P34 readiness gate logic, P35 integration lineage, HUD behavior, promotion flows, or alpha-live.

Required work:
- use exact P35 sourceCommit `82b0b09ecd902f502ae5509bcb3ee5a713f43fee` as the only source input to the P33 rebuild mechanism;
- prove again that required accepted tested commits P29 `c02f7e108e73665f22eb950573622acb6f452732`, P30 `90094a656ab311f18b0a758716dc97c3f8df092d`, and P31 `423c9c6c4a54ff4abd701e1dcd8c170cc4e9d731` are exact ancestors of the selected source;
- materialize deterministic candidate metadata/package provenance and fresh-read exact `sourceCommit`, `packageVersion`, candidate SHA-256, attestation/hash, manifest/runtime pins as defined by P33/P19 contracts;
- reject stale historical P19 bytes/pointers as substitutes;
- candidate status must explicitly remain `NOT_RETRY_ELIGIBLE_PENDING_P36` (or equally explicit) because P32 is BLOCKED/P36 unresolved; do not allow this materialization to satisfy P34 READY;
- if current P33 mechanism intentionally separates contract verification from repository candidate publication, follow its terminal semantics exactly and create only the authorized deterministic candidate/provenance artifact, never silently overwrite a canonical pointer without explicit contract authorization;
- no real game run, no Owner YES/NO, no promotion, no alpha-live movement, no global environment changes.

Focused deterministic checks must cover at least:
- exact P35 source identity/tree readback;
- exact P29/P30/P31 ancestry recheck;
- repeated materialization determinism for identical source;
- exact manifest/package/candidate hash readback;
- stale P19 rejection;
- P32 BLOCKED/P36 pending status prevents retry eligibility;
- no promotion / no alpha-live side effects.

Terminal COMPLETE means a fresh exact accepted-repair integrated candidate/provenance has been materialized and verified, but remains explicitly blocked from Owner retry pending P36. It does not mean real WOF PASS or Owner visual acceptance.

Before terminal-significant self-check create/bind a durable tested candidate/provenance commit/tree as required by the implementation path. Any implementation/provenance byte change after test requires rerun.

Progress checkpointing must follow parallel/PM/ALPHA_WORKER_PROGRESS_CHECKPOINT_PROTOCOL_V1.md; keep parallel/PM/PROGRESS/<stageId>_PROGRESS.json current at mandatory milestones and before any non-terminal stop.
Terminal reporting must follow parallel/PM/ALPHA_WORKER_RESULT_FAST_FEEDBACK_PROTOCOL_V1.md.

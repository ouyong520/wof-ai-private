# Alpha V1 P29 — W3 Live Evidence Contract Repair — START PROMPT

StageId:
`ALPHA_V1_PRODUCT_TAKEOVER_P29_W3_LIVE_EVIDENCE_CONTRACT_REPAIR`

DedupKey:
`alpha.v1.product-takeover.w3-live-evidence-contract-repair-v1`

Mission: repair the W3 capture/analyzer contract defect exposed by the first real Owner live run, without weakening the renderer-source truth boundary.

Read latest main, root AGENTS.md, full dedup/progress/result protocols, current final live gate, `parallel/RENDER_AUTHORITY_V2/RENDER_OBJECT_SOURCE_LONG_QUALIFICATION.md`, the real live evidence facts recorded by PM, and relevant W3 source/tests.

Dedup-v2: if equivalent ACTIVE/CLAIMED, return `ALREADY ACTIVE / CLAIMED — NO EXECUTION`; if COMPLETE/PASS, return `ALREADY COMPLETE — NO EXECUTION`; otherwise create canonical claim then stage claim with one fresh exact claimToken, read both back, then create PROGRESS.

Ownership is limited to W3 capture/analyzer/runtime-authority evidence code and focused tests. Do not edit P16 staging or page-association discovery unless strictly required to keep W3 interfaces compiling; coordinate via existing contracts instead.

Required repair:
- every `candidateTimeline` frame used by analyzer carries exact `runtimeEpoch`, `rendererEpoch`, `authorityKey`;
- same heap offset diagnostic exploration in BE16/LE16 must not create false `REJECTED` solely because both byte orders were explored;
- malformed/stale/epoch-mixed evidence still rejects;
- safe structural-only evidence with no legitimate `rendererSourceProof` deterministically returns `INCONCLUSIVE`;
- `PASS` remains strict and requires the existing direct displayed-frame renderer/object proof contract;
- structural/stable candidate never self-qualifies;
- no screenshot/world projection/guessed address production authority.

Focused deterministic tests only. No real game run, no promotion, no alpha-live move, no Owner YES/NO, no global Python/browser/environment changes.

Before terminal-significant self-check create a durable tested candidate commit/tree and bind PROGRESS to it. Any implementation-byte change after test requires a new candidate and rerun of affected checks.

Terminal COMPLETE means repo-side W3 contract repaired and ready for a new Owner run, not that live acceptance passed. Preserve `realWofAcceptance=NOT_RUN`, `ownerVisualAcceptance=NOT_RUN`, `visibleProof=NOT_PROVEN`, `alphaLiveMoved=false`.

Progress checkpointing must follow parallel/PM/ALPHA_WORKER_PROGRESS_CHECKPOINT_PROTOCOL_V1.md; keep parallel/PM/PROGRESS/<stageId>_PROGRESS.json current at mandatory milestones and before any non-terminal stop.
Terminal reporting must follow parallel/PM/ALPHA_WORKER_RESULT_FAST_FEEDBACK_PROTOCOL_V1.md.

# Alpha V1 P30 — P16/P9 Binding & Staging Readiness Repair — START PROMPT

StageId:
`ALPHA_V1_PRODUCT_TAKEOVER_P30_P16_P9_BINDING_AND_STAGING_READINESS_REPAIR`

DedupKey:
`alpha.v1.product-takeover.p16-p9-binding-staging-readiness-repair-v1`

Mission: repair the concrete P16/P9/P1 live staging defects proven by the Owner run, without broad HUD redesign.

Read latest main, root AGENTS.md, full dedup/progress/result protocols, current final live gate, P16/P17/P18/P21/P25/P27/P28 authorities/results, the maintained P9 canonical anchor envelope/HUD code, staging code, and focused tests.

Dedup-v2: if equivalent ACTIVE/CLAIMED, return `ALREADY ACTIVE / CLAIMED — NO EXECUTION`; if COMPLETE/PASS, return `ALREADY COMPLETE — NO EXECUTION`; otherwise create canonical claim then stage claim with one fresh exact claimToken, read both back, then create PROGRESS.

Live evidence already proves:
- `ProductionP1OverlayError: maintained Alpha HUD P1 binding failed`;
- `Error: WOF Alpha canonical anchor envelope P9 missing`;
- `p1LiveGateReady=false`, `templateCount=0`, `trackedFrames=0`, `p1Generation=null`, `productionOverlayVisible=false`;
- P16 was captured while `world.accepted=false`, canonical state `VERIFYING_WORLD`, downstream runtime identity fields incomplete.

Ownership is limited to the maintained P9/P1 HUD binding seam plus P16 staging readiness/waiting logic and focused tests. Do not edit W3 analyzer/capture logic and do not own general page-target discovery.

Required repair:
- diagnose why the maintained P9 canonical anchor envelope is absent in the exact staged runtime and repair that deterministic packaging/bootstrap/binding boundary;
- preserve canonical P9 semantics; do not substitute legacy projection, screenshot coordinates, guessed anchors, or redesign the HUD;
- make P1 binding fail closed with precise diagnostics when P9 is genuinely unavailable;
- prevent staging from accepting a fresh-but-still-`VERIFYING_WORLD` P16 record as final staged P16 evidence;
- usable P16 must require exact World accepted, expected world identity, nonempty runtime epoch, nonempty authorityKey, and required renderer/runtime authority fields used by P18/P17;
- keep P25/P27/P28 terminal truth intact.

Focused deterministic tests only. No real game run, no promotion, no alpha-live move, no Owner YES/NO, no global Python/browser/environment changes.

Before terminal-significant self-check create a durable tested candidate commit/tree and bind PROGRESS to it. Any implementation-byte change after test requires a new candidate and rerun of affected checks.

Terminal COMPLETE means repo-side P9/P16 staging seam repaired and ready for integration/live retry, not that live acceptance passed. Preserve `realWofAcceptance=NOT_RUN`, `ownerVisualAcceptance=NOT_RUN`, `visibleProof=NOT_PROVEN`, `alphaLiveMoved=false`.

Progress checkpointing must follow parallel/PM/ALPHA_WORKER_PROGRESS_CHECKPOINT_PROTOCOL_V1.md; keep parallel/PM/PROGRESS/<stageId>_PROGRESS.json current at mandatory milestones and before any non-terminal stop.
Terminal reporting must follow parallel/PM/ALPHA_WORKER_RESULT_FAST_FEEDBACK_PROTOCOL_V1.md.

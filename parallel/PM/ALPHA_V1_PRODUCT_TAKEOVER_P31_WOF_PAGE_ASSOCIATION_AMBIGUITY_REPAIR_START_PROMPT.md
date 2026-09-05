# Alpha V1 P31 — WOF Page Association Ambiguity Repair — START PROMPT

StageId:
`ALPHA_V1_PRODUCT_TAKEOVER_P31_WOF_PAGE_ASSOCIATION_AMBIGUITY_REPAIR`

DedupKey:
`alpha.v1.product-takeover.wof-page-association-ambiguity-repair-v1`

Mission: repair the concrete live discovery ambiguity `WOF page association ambiguous: 2 page targets` so the runtime selects/associates Page/Worker/WASM deterministically and fail-closed.

Read latest main, root AGENTS.md, full dedup/progress/result protocols, current final live gate, discovery/reentry/runtime-authority code and focused tests, plus the live evidence facts recorded by PM.

Dedup-v2: if equivalent ACTIVE/CLAIMED, return `ALREADY ACTIVE / CLAIMED — NO EXECUTION`; if COMPLETE/PASS, return `ALREADY COMPLETE — NO EXECUTION`; otherwise create canonical claim then stage claim with one fresh exact claimToken, read both back, then create PROGRESS.

Live evidence already proves the browser endpoint, WOF page, Worker, WASM and HEAP are present, but discovery reported `WOF page association ambiguous: 2 page targets` while one accepted page target/worker pair was also observed. The repair must make this association deterministic without guessing.

Ownership is limited to page/worker/WASM discovery, reentry association, runtime-authority selection and focused tests. Do not edit W3 qualification semantics and do not own P9/P16 staging readiness code.

Required repair:
- identify why two page targets are simultaneously considered plausible in the real browser profile;
- deterministically associate the exact game Page with its Worker/WASM using existing semantic/runtime evidence;
- if ambiguity cannot be resolved from authoritative evidence, remain fail-closed with precise diagnostics;
- do not pick first/last/nearest target by ordering, timing accident or guessed URL-only heuristics;
- preserve exact World identity requirements and runtime authority revocation semantics;
- add deterministic fixtures covering two-page ambiguity, one authoritative match, stale/duplicate target rejection, and fail-closed unresolved ambiguity.

Focused deterministic tests only. No real game run, no promotion, no alpha-live move, no Owner YES/NO, no global Python/browser/environment changes.

Before terminal-significant self-check create a durable tested candidate commit/tree and bind PROGRESS to it. Any implementation-byte change after test requires a new candidate and rerun of affected checks.

Terminal COMPLETE means repo-side discovery ambiguity repaired and ready for integrated live retry, not that live acceptance passed. Preserve `realWofAcceptance=NOT_RUN`, `ownerVisualAcceptance=NOT_RUN`, `visibleProof=NOT_PROVEN`, `alphaLiveMoved=false`.

Progress checkpointing must follow parallel/PM/ALPHA_WORKER_PROGRESS_CHECKPOINT_PROTOCOL_V1.md; keep parallel/PM/PROGRESS/<stageId>_PROGRESS.json current at mandatory milestones and before any non-terminal stop.
Terminal reporting must follow parallel/PM/ALPHA_WORKER_RESULT_FAST_FEEDBACK_PROTOCOL_V1.md.

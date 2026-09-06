# Alpha V1 P41 — Bounded Zero-Click Live Verification Harness — START PROMPT

StageId:
`ALPHA_V1_PRODUCT_TAKEOVER_P41_BOUNDED_ZERO_CLICK_LIVE_VERIFICATION_HARNESS`

DedupKey:
`alpha.v1.product-takeover.bounded-zero-click-live-verification-harness-v1`

Mission: build the deterministic repo-side harness for the next single bounded Owner Windows verification so it can start the exact candidate/runtime, collect the actual P36 renderer-source evidence plus P37/P39 diagnostic visibility correlation, and publish a machine-readable receipt/log bundle without any avatar click/manual seed. This task builds the harness only; it does not run the real game.

Fresh PM authority:
- P36 terminal COMPLETE testedCommit `162e50b6c65fd1d3901ad694854563b686b2ce22`; its observer/proof producer is ready for bounded live verification but live authority is NOT_PROVEN.
- P37 terminal COMPLETE testedCommit `64d5c3d2c1c84fffc7d9f59e701ec37fd1c68530`, classification `UNVERIFIED_AUTO_BASELINE`; useful for correlation only, never authority.
- P38 terminal COMPLETE materialized source `82b0b09ecd902f502ae5509bcb3ee5a713f43fee`, but that artifact predates terminal P36 and is not the final live candidate.
- P39 owns visible diagnostic HUD integration. P40 owns actual runtime source exposure. P41 must not implement either of those surfaces.
- P34 readiness semantics remain fail-closed; P41 must not authorize retry/promotion by itself.

Read latest main, root AGENTS.md, dedup/progress/result protocols, P21/P30 staging runner/runtime, P31 deterministic discovery, P33 rebuild contract, P34 readiness gate, P36/P37/P38 terminal RESULTs, current Owner staging CMD/Python runner, current evidence/receipt schemas, and any existing log capture utilities.

Dedup-v2: if equivalent P41 ACTIVE/CLAIMED, return `ALREADY ACTIVE / CLAIMED — NO EXECUTION`; if COMPLETE/PASS, return `ALREADY COMPLETE — NO EXECUTION`; otherwise create canonical claim then stage claim with one fresh exact claimToken, read both back, then create PROGRESS.

Required work:
- create one bounded, deterministic, zero-click verification harness/entrypoint for later Codex/Owner use; no implicit HEAD is allowed: exact sourceCommit/candidate/package identity must be supplied and fresh-read before launch;
- reuse the existing dedicated WOF project venv/browser/runtime; no install logic, no global Python/PATH/site-packages changes, no deleting unrelated environments;
- verify exact candidate/source/manifest/attestation/runtime pins before any launch action; stale historical P19/P38-incomplete candidate must fail closed when it lacks required final inputs;
- resolve Page/Worker/WASM only through accepted P31 deterministic authority; ambiguous association fails closed;
- start/collect the P36 bounded source observer using exact runtimeEpoch/rendererEpoch/authorityKey and capture raw source-discovery status, source metadata, direct renderer-submit events, producer result and unchanged P32 qualification result for P1/P2/P3 generations;
- if P37/P39 diagnostic outputs are present, capture their status/tracks/HUD visibility only as `UNVERIFIED_AUTO_BASELINE` correlation, clearly separated from authority;
- capture the raw runtime/console/staging diagnostics needed to explain a failure, including exact error strings and the causal ordering of P16/P17/P9/HUD/source-observer gates; do not reduce the receipt to a single summary code;
- write a machine-readable receipt and human-readable summary under a bounded run directory, with exact paths to raw logs/evidence files, start/end timestamps, exit state and alphaLiveMoved=false;
- final harness result vocabulary must distinguish at least `READY_FOR_OWNER_RUN`, `FAILED_PRECHECK`, `FAILED_RUNTIME_IDENTITY`, `FAILED_SOURCE_EXPOSURE`, `FAILED_RENDERER_AUTHORITY`, `FAILED_VISIBLE_DIAGNOSTIC`, and `PASS_LIVE_AUTHORITY_PENDING_OWNER_VISUAL`; do not map INCONCLUSIVE/BLOCKED to PASS;
- zero-click contract: no avatar/portrait click, no manual player selection, no manual seed; Owner only starts/plays the game during the later authorized run;
- bounded execution and cleanup must preserve browser/runtime for diagnosis when configured, while never indefinitely blocking.

Focused deterministic tests must cover at least:
- exact source/candidate identity and stale candidate rejection;
- P31 multi-page ambiguity fail-closed;
- P36 source absent/ambiguous/stale/qualified receipt mapping;
- P37/P39 diagnostic evidence separated from authority;
- raw-log/receipt completeness and deterministic paths;
- zero-click contract and no environment mutation;
- alpha-live/promotion remains unchanged.

Scope boundaries:
- may add/modify Owner staging/live-verification orchestration, receipt/log capture and focused tests/docs;
- do not modify P36/P40 renderer source semantics, P37/P39 detection/HUD semantics, P29/P32 qualifier criteria, candidate bytes/materialization ownership, readiness-gate semantics or promotion flows;
- no real WOF run, no Owner YES/NO, no RAM writes, no input injection, no alpha-live move, no global environment changes.

Terminal COMPLETE means the exact-byte-tested harness is ready for a separately authorized bounded real-WOF run after P39/P40 integration and fresh candidate materialization/readiness. COMPLETE does not itself authorize or perform that run.

Before terminal-significant self-check create a durable tested candidate commit/tree and bind PROGRESS to it. Any implementation-byte change after test requires a new candidate and rerun.

Progress checkpointing must follow parallel/PM/ALPHA_WORKER_PROGRESS_CHECKPOINT_PROTOCOL_V1.md; keep parallel/PM/PROGRESS/<stageId>_PROGRESS.json current at mandatory milestones and before any non-terminal stop.
Terminal reporting must follow parallel/PM/ALPHA_WORKER_RESULT_FAST_FEEDBACK_PROTOCOL_V1.md.

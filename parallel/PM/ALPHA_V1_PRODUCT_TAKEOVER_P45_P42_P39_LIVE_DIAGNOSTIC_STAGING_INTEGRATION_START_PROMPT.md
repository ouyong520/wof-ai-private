# Alpha V1 P45 — P42/P39 Live Diagnostic Staging Integration — START PROMPT

StageId:
`ALPHA_V1_PRODUCT_TAKEOVER_P45_P42_P39_LIVE_DIAGNOSTIC_STAGING_INTEGRATION`

DedupKey:
`alpha.v1.product-takeover.p42-p39-live-diagnostic-staging-integration-v1`

Mission: wire the terminal COMPLETE P42 renderer-correlation probe and terminal COMPLETE P39 zero-click visible baseline into the maintained Alpha staging/diagnostic runtime so the later P43 bounded live diagnostic can actually collect both raw mapping evidence and visible P1/P2/P3 tracker state in one run, without changing production authority semantics.

Fresh PM authority:
- P39 terminal COMPLETE testedCommit `ac5387f00d8c2382dcf3ed435ffcfa0acc1a2f05`, classification `UNVERIFIED_AUTO_BASELINE`.
- P40 terminal BLOCKED with `NATIVE_PLAYER_MARKER_DISPLAYED_SUBMIT_SOURCE_EXPORT_NOT_PRESENT`.
- P42 terminal COMPLETE testedCommit `7b523187a955179b04155b758847c82aaf569a0d`, mapping-only, authorityEligible=false.
- P43 is separately ACTIVE and owns the diagnostic harness/receipt/log capture; do not modify its files.
- P44 terminal COMPLETE found no historical direct-source candidate.

Dedup-v2: if equivalent P45 ACTIVE/CLAIMED, return `ALREADY ACTIVE / CLAIMED — NO EXECUTION`; if COMPLETE/PASS, return `ALREADY COMPLETE — NO EXECUTION`; otherwise acquire canonical then stage claim with one fresh exact claimToken and read both back before implementation.

Required work:
- integrate the exact accepted P42 probe source into the maintained staging/diagnostic injection path under one explicit bounded diagnostic gate;
- integrate/reuse the exact accepted P39 staging visible baseline in the same run without copying its tracker heuristics;
- expose deterministic status/readout surfaces that P43 can collect: P42 probe state, raw bundle/seal/teardown reason, P39 tracker/HUD state, runtimeEpoch/rendererEpoch/authorityKey and explicit diagnostic classification;
- injection order must be deterministic and must not replace or bypass maintained Alpha HUD, P16/P17/P9 gates or P36/P32 authority;
- gate-off behavior must restore exact pre-existing runtime behavior and leave production source tuples/authority bytes semantically unchanged;
- stale/mixed runtime identity must reject/fail closed; no implicit HEAD, no guessed binding;
- preserve full P42 raw bundle. Do not pre-rank or discard candidate draw/state records needed by later mapping analysis;
- zero click / zero manual seed / no avatar selection.

Authority boundary:
- P42 data remains `BOUNDED_LIVE_DIAGNOSTIC_MAPPING_ONLY`;
- P39 remains `UNVERIFIED_AUTO_BASELINE`;
- this task must never create `rendererSourceProof`, `P29 PASS`, `P32 QUALIFIED`, retry eligibility, promotion eligibility or the P36 direct-source surface;
- pixel/screenshot/OCR/template/nearest/order/timing/guessed-offset evidence cannot become authority.

Scope:
- may modify narrowly scoped staging/runtime diagnostic injection files and add focused tests/docs for P45;
- do not modify P43-owned harness files, P40/P42/P39 tested source semantics, P29/P32/P36 acceptance logic, production promotion flows or alpha-live;
- no real game run, no Owner YES/NO, no global Python/PATH/site-packages changes.

Before terminal-significant self-check create a durable tested candidate commit/tree and bind PROGRESS to it. Any implementation-byte change after test requires a new candidate and rerun.

Progress checkpointing must follow parallel/PM/ALPHA_WORKER_PROGRESS_CHECKPOINT_PROTOCOL_V1.md; keep parallel/PM/PROGRESS/<stageId>_PROGRESS.json current at mandatory milestones and before any non-terminal stop.
Terminal reporting must follow parallel/PM/ALPHA_WORKER_RESULT_FAST_FEEDBACK_PROTOCOL_V1.md.

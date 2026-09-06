# Alpha V1 P39 — Zero-Click Visible HUD Baseline Integration — START PROMPT

StageId:
`ALPHA_V1_PRODUCT_TAKEOVER_P39_ZERO_CLICK_VISIBLE_HUD_BASELINE_INTEGRATION`

DedupKey:
`alpha.v1.product-takeover.zero-click-visible-hud-baseline-integration-v1`

Mission: integrate the terminal COMPLETE P37 zero-click native-marker auto-acquisition baseline into the maintained Alpha HUD as a strictly gated diagnostic/staging-visible path so Owner can see automatic P1/P2/P3 following again without any avatar click or manual seed, while preserving the authoritative production fail-closed boundary.

Fresh PM authority:
- P37 terminal COMPLETE testedCommit `64d5c3d2c1c84fffc7d9f59e701ec37fd1c68530`, classification `UNVERIFIED_AUTO_BASELINE`, exact native 384x224 TOP_LEFT_POSITIVE_DOWN coordinates, automatic P1/P2/P3 acquisition/reacquisition and explicit no-Y-inversion fixtures.
- P36 terminal COMPLETE testedCommit `162e50b6c65fd1d3901ad694854563b686b2ce22`, but real live renderer authority remains NOT_PROVEN until a unique direct runtime source surface is actually exposed and accepted.
- P32 remains historical terminal BLOCKED authority and must not be rewritten as PASS.
- Final product contract is zero click: no avatar/portrait click, no manual P1/P2/P3 selection, no manual seed.

Read latest main, root AGENTS.md, dedup/progress/result protocols, P37 RESULT and exact tested implementation, current maintained Alpha HUD/overlay renderer, P30 P9/P1 binding seam, P36 RESULT/proof boundary, and current staging injection/runtime paths.

Dedup-v2: if equivalent P39 ACTIVE/CLAIMED, return `ALREADY ACTIVE / CLAIMED — NO EXECUTION`; if COMPLETE/PASS, return `ALREADY COMPLETE — NO EXECUTION`; otherwise create canonical claim then stage claim with one fresh exact claimToken, read both back, then create PROGRESS.

Required work:
- wire the P37 zero-click tracker into the maintained Alpha HUD only through an explicit diagnostic/staging gate; production authoritative rendering semantics must remain unchanged when the gate is off;
- no Owner click, avatar selection, portrait seed or manual P1/P2/P3 selection is permitted;
- consume P37 native 384x224 coordinates with explicit TOP_LEFT_POSITIVE_DOWN semantics and prove that left/right/up/down HUD movement is not vertically inverted;
- show a visible diagnostic marker/warning near the automatically tracked player for P1/P2/P3 when unambiguous and fresh;
- stale/lost/ambiguous P37 states must hide or mark unavailable fail-closed; never silently pick first/nearest/order/timing;
- diagnostic output/status must remain unmistakably labeled `UNVERIFIED_AUTO_BASELINE` and must expose enough status for P41 evidence capture;
- never emit `rendererSourceProof`, never satisfy P29/P32/P36 authority, never make P34 retry-ready, and never authorize promotion;
- do not copy/reimplement P37 detection heuristics inside HUD if a narrow adapter/import/channel can reuse the tested P37 implementation;
- preserve maintained HUD existing authoritative P9/P16/P17 behavior and existing production warnings.

Focused deterministic tests must cover at least:
- zero-click startup and P1/P2/P3 diagnostic HUD attachment;
- exact coordinate transform including explicit non-inverted Y movement;
- stale/lost hide behavior and reacquisition;
- ambiguity fail-closed with no visible authoritative-looking marker;
- diagnostic gate off => production HUD behavior unchanged;
- proof boundary: no rendererSourceProof/P29/P32/P36/P34/promotion eligibility.

Scope boundaries:
- may modify maintained HUD and narrowly scoped staging/diagnostic wiring needed to consume P37;
- do not modify P36 renderer source observer/producer semantics, P29/P32 qualification criteria, P33/P34/P35/P38 candidate/readiness machinery, or promotion flows;
- no real WOF run, no Owner YES/NO, no RAM writes, no input injection, no alpha-live move, no global environment changes.

Terminal COMPLETE means an exact-byte-tested zero-click diagnostic-visible maintained-HUD path exists and is ready for one later bounded live verification. COMPLETE does not claim real-WOF correctness or renderer authority.

Before terminal-significant self-check create a durable tested candidate commit/tree and bind PROGRESS to it. Any implementation-byte change after test requires a new candidate and rerun.

Progress checkpointing must follow parallel/PM/ALPHA_WORKER_PROGRESS_CHECKPOINT_PROTOCOL_V1.md; keep parallel/PM/PROGRESS/<stageId>_PROGRESS.json current at mandatory milestones and before any non-terminal stop.
Terminal reporting must follow parallel/PM/ALPHA_WORKER_RESULT_FAST_FEEDBACK_PROTOCOL_V1.md.

# Alpha V1 P32 — Native Player Marker Renderer Anchor Qualification — START PROMPT

StageId:
`ALPHA_V1_PRODUCT_TAKEOVER_P32_NATIVE_PLAYER_MARKER_RENDERER_ANCHOR_QUALIFICATION`

DedupKey:
`alpha.v1.product-takeover.native-player-marker-renderer-anchor-qualification-v1`

Mission: investigate and implement the smallest deterministic renderer-side proof path that can use WOF's own native `1P` / `2P` / `3P` downward player marker as the player anchor source, instead of guessing body/head coordinates. The goal is to prepare one authoritative live-proof producer for the next bounded Owner run, not to fabricate proof offline.

Read latest main, root AGENTS.md, full dedup/progress/result protocols, the current final live gate, P29 terminal RESULT, P30/P31 active scopes, `parallel/RENDER_AUTHORITY_V2/**`, the maintained P9 canonical-anchor contract and its consumers, plus any exact checked-in live evidence/reasoning files relevant to renderer source qualification.

Dedup-v2: if equivalent ACTIVE/CLAIMED, return `ALREADY ACTIVE / CLAIMED — NO EXECUTION`; if COMPLETE/PASS, return `ALREADY COMPLETE — NO EXECUTION`; otherwise create canonical claim then stage claim with one fresh exact claimToken, read both back, then create PROGRESS.

Product hypothesis to qualify, not assume:
- the game already draws a native `1P` / `2P` / `3P` label plus downward arrow above the corresponding player;
- if that marker is emitted through the displayed CPS1 renderer/object submission, its native 384x224 renderer coordinates may be a cleaner player anchor than reconstructing body/head position;
- the label/arrow may be one renderer object or a deterministic multi-object cluster; support either only when proven by direct renderer evidence.

Ownership:
- primary ownership is a new marker-authority/proof-producer seam and focused deterministic tests;
- minimal integration into W3 capture/proof production is allowed only where necessary to emit a legitimate existing `wof-renderer-source-proof-v1`-compatible direct proof;
- do not weaken or rewrite P29 analyzer PASS criteria;
- do not modify P30 staging/P16/P9 binding readiness work;
- do not modify P31 Page/Worker/WASM association work;
- do not redesign HUD/P10/P12 downstream consumers.

Required work:
- trace how the native player marker reaches the displayed frame using source-traced pointer/direct renderer hook/exported renderer pointer or an equally authoritative existing contract path; a structural HEAP match alone is insufficient;
- identify marker object/cluster semantics without relying on first/last/order/timing/nearest-distance guesses;
- bind marker identity explicitly to `P1` / `P2` / `P3` actor association plus actor generation and exact runtimeEpoch/rendererEpoch/authorityKey;
- keep all coordinates native renderer 384x224; screenshot/OCR/template/world-projection coordinates are verification-only and can never become production authority;
- preserve fail-closed behavior when duplicate markers, stale frames, mixed epochs, ambiguous clusters, missing causal link, or missing generation binding occur;
- if direct displayed-frame causality is not available offline, implement the bounded read-only proof producer/instrumentation needed for exactly one later Owner live run and record the remaining live dependency truthfully;
- never synthesize `rendererSourceProof`, never promote a structural candidate, and never claim W3 PASS from fixtures alone.

Focused deterministic regressions must cover at least:
- one authoritative direct-frame marker object/cluster associated with an exact player generation;
- multi-object label+arrow cluster remains deterministic when row order changes;
- duplicate/ambiguous same-player markers fail closed;
- stale runtimeEpoch/rendererEpoch/authorityKey or generation mismatch is rejected;
- screenshot/OCR-only or structural-only marker evidence cannot qualify;
- no proof object is emitted when displayed-frame causal evidence is absent.

No real game run, no promotion, no alpha-live move, no Owner YES/NO, no screenshot-template production tracking, no RAM writes, no input injection, no global Python/browser/environment changes.

Before terminal-significant self-check create a durable tested candidate commit/tree and bind PROGRESS to it. Any implementation-byte change after test requires a new candidate and rerun of affected checks.

Terminal COMPLETE means the repo-side native-marker proof producer/qualification seam is durable, focused-tested, and ready for one bounded live verification. It does not mean the real game marker has been proven, W3 is PASS, Owner visual acceptance passed, or alpha-live moved. Preserve `realWofAcceptance=NOT_RUN`, `ownerVisualAcceptance=NOT_RUN`, `visibleProof=NOT_PROVEN`, `alphaLiveMoved=false`.

If authoritative marker causality cannot be prepared without violating the existing renderer proof contract, terminal BLOCKED is correct; name the exact missing causal edge and do not downgrade the requirement.

Progress checkpointing must follow parallel/PM/ALPHA_WORKER_PROGRESS_CHECKPOINT_PROTOCOL_V1.md; keep parallel/PM/PROGRESS/<stageId>_PROGRESS.json current at mandatory milestones and before any non-terminal stop.
Terminal reporting must follow parallel/PM/ALPHA_WORKER_RESULT_FAST_FEEDBACK_PROTOCOL_V1.md.

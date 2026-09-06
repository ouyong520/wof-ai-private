# Alpha V1 P40 — Native Marker Renderer Source Runtime Exposure — START PROMPT

StageId:
`ALPHA_V1_PRODUCT_TAKEOVER_P40_NATIVE_MARKER_RENDERER_SOURCE_RUNTIME_EXPOSURE`

DedupKey:
`alpha.v1.product-takeover.native-marker-renderer-source-runtime-exposure-v1`

Mission: take the terminal COMPLETE P36 zero-click source observer/proof producer and wire the smallest truthful read-only runtime exposure from the actual displayed CPS1 renderer/object submit path into the exact source surface P36 can discover. This task owns the missing live runtime exposure edge; it must not fabricate or weaken authority.

Fresh PM authority:
- P36 terminal COMPLETE testedCommit `162e50b6c65fd1d3901ad694854563b686b2ce22`, integrationReady=true. Its observer only accepts one unique explicit source surface and fails closed if absent/ambiguous/stale.
- P36 discovery surface contract includes `__WOF_NATIVE_MARKER_RENDERER_SUBMIT_SOURCE_V1__` or `WOFNativeMarkerRendererSubmitSourceV1` under the checked runtime roots, with derivation `SOURCE_TRACED_POINTER`, `DIRECT_RENDER_HOOK` or `EXPORTED_RENDERER_POINTER`, a subscribe hook, displayed-frame causality, native 384x224 coordinates and exact runtimeEpoch/rendererEpoch/authorityKey.
- P29/P32 authority remains unchanged: structural HEAP, screenshot/OCR/template, world projection, nearest/order/timing or guessed offsets cannot qualify.
- P37/P39 own the non-authoritative visible baseline; do not use their pixel tracker to mint renderer authority.

Read latest main, root AGENTS.md, dedup/progress/result protocols, P36 RESULT and exact source observer/producer/tests/docs, P29/P32 authority, current `wof_render_authority_capture_worker.js`, Page/Worker/WASM runtime discovery, WASM/JS glue, renderer bridge/export surfaces, WebGL/native draw submission path and any checked-in source-mapping/export metadata.

Dedup-v2: if equivalent P40 ACTIVE/CLAIMED, return `ALREADY ACTIVE / CLAIMED — NO EXECUTION`; if COMPLETE/PASS, return `ALREADY COMPLETE — NO EXECUTION`; otherwise create canonical claim then stage claim with one fresh exact claimToken, read both back, then create PROGRESS.

Required work:
- reverse-trace the actual runtime displayed renderer/object submit path far enough to identify a truthful source hook/export/pointer that can expose exact native player-marker submit events;
- expose exactly one P36-compatible source surface when and only when that direct source exists; absence must remain absent, not synthesized;
- every emitted event must be caused by an actual displayed renderer submission and carry native 384x224 x/y, displayedFrameId, submissionId, monotonic frameGeneration, explicit P1/P2/P3 actor generation association, runtimeEpoch, rendererEpoch and authorityKey;
- source metadata must truthfully identify hookSite, instrumentationId and sourceTrace; guessed=false; displayedFrameCausalLink=true; coordinateAuthority=`NATIVE_RENDERER_OBJECT_384X224`;
- zero click: no Owner avatar/portrait click, no manual seed, no manual P1/P2/P3 selection;
- ambiguity, duplicate candidate source, stale/mixed epoch, generation uncertainty or inability to bind marker identity must fail closed and emit no qualifying authority;
- integrate with the existing P36 observer/producer unchanged; do not relax P36/P32 tests or acceptance criteria;
- if checked-in runtime cannot truthfully expose the direct displayed submit edge without real live-only knowledge, implement the narrowest bounded read-only instrumentation needed for the later Owner run and terminal BLOCKED/COMPLETE truthfully according to what is proven repo-side.

Focused tests must cover at least:
- unique exact runtime source exposure and P36 discovery;
- P1/P2/P3 exact actor-generation event emission;
- native 384x224 bounds and direct displayed-frame IDs;
- stale/mixed authority rejection;
- ambiguity/missing source fail-closed;
- zero-click contract;
- no structural/pixel/screenshot fallback;
- bounded teardown/unsubscribe and no runtime mutation outside read-only instrumentation.

Scope boundaries:
- may modify narrowly scoped renderer/runtime/JS/WASM bridge surfaces needed to expose the direct source plus focused tests/docs;
- do not modify P29/P32/P36 acceptance criteria, P37/P39 pixel baseline/HUD ownership, P33/P34/P35/P38 candidate/readiness/provenance, or promotion flows;
- no real WOF run, no Owner YES/NO, no RAM writes, no input injection, no alpha-live move, no global environment changes.

Terminal COMPLETE means an exact-byte-tested runtime exposure/instrumentation path exists and the existing P36 observer can discover/consume it in deterministic tests, ready for one bounded real-WOF verification. It does not claim live authority has already passed. If no truthful checked-in/runtime hook can be exposed, terminal BLOCKED with the narrowest exact missing edge is correct.

Before terminal-significant self-check create a durable tested candidate commit/tree and bind PROGRESS to it. Any implementation-byte change after test requires a new candidate and rerun.

Progress checkpointing must follow parallel/PM/ALPHA_WORKER_PROGRESS_CHECKPOINT_PROTOCOL_V1.md; keep parallel/PM/PROGRESS/<stageId>_PROGRESS.json current at mandatory milestones and before any non-terminal stop.
Terminal reporting must follow parallel/PM/ALPHA_WORKER_RESULT_FAST_FEEDBACK_PROTOCOL_V1.md.

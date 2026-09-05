# Alpha V1 P36 — Native Marker Renderer Submit Source Trace — START PROMPT

StageId:
`ALPHA_V1_PRODUCT_TAKEOVER_P36_NATIVE_MARKER_RENDERER_SUBMIT_SOURCE_TRACE`

DedupKey:
`alpha.v1.product-takeover.native-marker-renderer-submit-source-trace-v1`

Mission: successor to terminal BLOCKED P32. Find and implement the smallest truthful read-only source-traced path from displayed CPS1 renderer/object submission to the exact native `1P` / `2P` / `3P` downward marker object or deterministic object cluster, preserving explicit actor generation and exact runtime authority identity. This task attacks the missing causal edge; it must not relax the P29/P32 qualification criteria.

Fresh PM authority:
- P32 is terminal BLOCKED, testedCommit `bd75c3b5f7fd20fe004fae21142a0fa19942e076`, blocker `NATIVE_PLAYER_MARKER_DIRECT_RENDERER_CAUSAL_EDGE_NOT_CHECKED_IN`.
- P32 already provides a fail-closed qualifier for exact P1/P2/P3 generation, native 384x224 coordinates, runtimeEpoch/rendererEpoch/authorityKey and deterministic single/multi-object cluster identity.
- P29 analyzer semantics are terminal COMPLETE and must remain unchanged: structural HEAP evidence alone is INCONCLUSIVE; stale/mixed authority is REJECTED; PASS requires direct displayed-frame renderer/object causal proof.
- P33 owns final candidate rebuild mechanism; P34 owns retry readiness gate; P35 owns accepted repair integration lineage.

Read latest main, root AGENTS.md, full dedup/progress/result protocols, P29 RESULT/qualification analyzer contract, P32 RESULT and qualifier module/tests/doc, current `wof_render_authority_capture_worker.js`, relevant Page/Worker/WASM discovery/runtime code, checked-in renderer/source evidence, and any available WASM/JS glue or exported renderer pointers.

Dedup-v2: this is a new successor, not P32 recovery. If equivalent P36 ACTIVE/CLAIMED, return `ALREADY ACTIVE / CLAIMED — NO EXECUTION`; if COMPLETE/PASS, return `ALREADY COMPLETE — NO EXECUTION`; otherwise create canonical claim then stage claim with one fresh exact claimToken, read both back, then create PROGRESS.

Required work:
- reverse-trace the actual displayed CPS1 renderer/object submission path in checked-in code/artifacts and identify the strongest exact hook/exported pointer/source-traced pointer available;
- implement the smallest read-only proof producer/instrumentation needed to emit displayed-frame object submissions with native 384x224 coordinates and exact runtimeEpoch/rendererEpoch/authorityKey;
- connect producer evidence to the existing P32 qualifier without weakening or redefining its proof contract;
- marker identity must be explicit and deterministic. One-object and multi-object cluster cases are both allowed, but no nearest-object, list-order, timing, screenshot/OCR/template, world-projection or guessed-offset selection;
- preserve explicit P1/P2/P3 actor generation association. If actor generation cannot be causally bound from checked-in source/runtime contracts, fail closed and name that exact missing edge;
- if static checked-in artifacts cannot expose the exact live renderer submit hook offline, it is acceptable to implement a bounded read-only live proof producer for one later Owner run, but fixtures must not be represented as live proof;
- retain P29 PASS/INCONCLUSIVE/REJECTED behavior and P32 qualifier fail-closed behavior; add focused tests for direct-source acceptance and structural/ambiguous/stale rejection;
- do not claim real marker authority unless direct displayed-frame causality is actually proven from authoritative runtime evidence.

Scope boundaries:
- may add/modify renderer capture/source-trace producer files needed for P36, including narrowly scoped wiring in `parallel/RENDER_AUTHORITY_V2/**`;
- do not modify P29 `qualification_analyzer.py` acceptance criteria;
- do not modify P31 Page/Worker/WASM association, P30 staging/P16/P9, P33 OWNER_ONECLICK rebuild, P34 readiness gate, P35 integration lineage, HUD layout or promotion flows;
- no real game run under this task, no Owner YES/NO, no RAM writes, no input injection, no alpha-live move, no global environment changes.

Terminal COMPLETE means a durable exact-byte-tested read-only source-trace/proof-producer exists and is ready for one bounded live verification. It does not mean the real native marker has already passed live authority. If the exact source-trace still cannot be implemented from available checked-in artifacts, terminal BLOCKED is correct and must identify the narrowest missing causal edge.

Before terminal-significant self-check create a durable tested candidate commit/tree and bind PROGRESS to it. Any implementation-byte change after test requires a new candidate and rerun.

Progress checkpointing must follow parallel/PM/ALPHA_WORKER_PROGRESS_CHECKPOINT_PROTOCOL_V1.md; keep parallel/PM/PROGRESS/<stageId>_PROGRESS.json current at mandatory milestones and before any non-terminal stop.
Terminal reporting must follow parallel/PM/ALPHA_WORKER_RESULT_FAST_FEEDBACK_PROTOCOL_V1.md.

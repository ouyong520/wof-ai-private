# Alpha V1 P46 — WASM/WebGL Call-Site Fingerprint Probe — START PROMPT

StageId:
`ALPHA_V1_PRODUCT_TAKEOVER_P46_WASM_WEBGL_CALLSITE_FINGERPRINT_PROBE`

DedupKey:
`alpha.v1.product-takeover.wasm-webgl-callsite-fingerprint-probe-v1`

Mission: add a bounded read-only diagnostic probe that fingerprints the actual JS/WASM call-site context reaching WebGL draw/buffer submission so the next live diagnostic can narrow the gstyphoon renderer call site beyond generic draw-state correlation. This is diagnostic evidence only and must not fabricate the missing P40 direct source export.

Fresh PM authority:
- P40 terminal BLOCKED: checked-in runtime has no truthful per-object gstyphoon CPS1 displayed-submit export/hook.
- P42 terminal COMPLETE testedCommit `7b523187a955179b04155b758847c82aaf569a0d` and already captures draw arguments, shader/program, buffers, attribs, textures, viewport/scissor, CPU payload/hash/offset and P39 correlation.
- P44 terminal COMPLETE: full reachable Git history has no `DIRECT_SOURCE_CANDIDATE`.
- P43 is separately ACTIVE and owns live harness/logging.
- P45 separately owns staging integration of P42/P39; do not duplicate it.

Dedup-v2: if equivalent P46 ACTIVE/CLAIMED, return `ALREADY ACTIVE / CLAIMED — NO EXECUTION`; if COMPLETE/PASS, return `ALREADY COMPLETE — NO EXECUTION`; otherwise acquire canonical then stage claim with one fresh exact claimToken and read both back before implementation.

Required work:
- instrument the narrow WebGL import/hook boundary around `drawArrays` / `drawElements` and relevant buffer-upload/attrib setup calls without changing rendered output;
- capture bounded raw call-stack text when available and normalize a deterministic call-site fingerprint;
- when browser stack exposes WebAssembly frames, preserve exact wasm-function index/name/offset text rather than guessing symbols;
- preserve JS wrapper/import function identity, Module/asm surface identity, draw-call sequence and exact runtimeEpoch/rendererEpoch/authorityKey binding;
- where feasible, associate buffer upload/setup call-site fingerprints with later draw-call fingerprints through exact object identity/state transitions; do not infer semantic object identity from timing alone;
- emit explicit `NOT_AVAILABLE`/`UNRESOLVED` fields when stack/function identity is unavailable instead of inventing a mapping;
- output a raw bounded diagnostic bundle suitable for P43 capture and later source-mapping analysis;
- deterministic teardown and strict stale/mixed binding rejection are required.

Authority boundary:
- this probe is correlation/mapping evidence only;
- must not create `__WOF_NATIVE_MARKER_RENDERER_SUBMIT_SOURCE_V1__`, `WOFNativeMarkerRendererSubmitSourceV1`, `rendererSourceProof`, P29 PASS or P32 qualification;
- stack proximity, timing, call order, pixel correlation, screenshot/OCR/template, nearest candidate or guessed wasm symbol/offset can never be promoted to authority;
- if only generic WebGL call sites are observable, report that truthfully.

Scope:
- prefer isolated files under `parallel/RENDER_AUTHORITY_V2/**` plus focused tests/docs;
- do not modify P43 harness, P45 staging integration, P29/P32/P36 criteria, P39 tracker/HUD semantics or promotion flows;
- no real game run, no Owner YES/NO, no RAM writes, no input injection, no alpha-live move, no global environment changes.

Before terminal-significant self-check create a durable tested candidate commit/tree and bind PROGRESS to it. Any implementation-byte change after test requires a new candidate and rerun.

Progress checkpointing must follow parallel/PM/ALPHA_WORKER_PROGRESS_CHECKPOINT_PROTOCOL_V1.md; keep parallel/PM/PROGRESS/<stageId>_PROGRESS.json current at mandatory milestones and before any non-terminal stop.
Terminal reporting must follow parallel/PM/ALPHA_WORKER_RESULT_FAST_FEEDBACK_PROTOCOL_V1.md.

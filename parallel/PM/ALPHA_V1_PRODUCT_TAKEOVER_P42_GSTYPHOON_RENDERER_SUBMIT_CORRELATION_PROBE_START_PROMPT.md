# Alpha V1 P42 — GStyphoon Renderer Submit Correlation Probe — START PROMPT

StageId:
`ALPHA_V1_PRODUCT_TAKEOVER_P42_GSTYPHOON_RENDERER_SUBMIT_CORRELATION_PROBE`

DedupKey:
`alpha.v1.product-takeover.gstyphoon-renderer-submit-correlation-probe-v1`

Mission: successor to terminal BLOCKED P40, not recovery. Build the smallest bounded, zero-click, read-only diagnostic probe that can expose enough real gstyphoon/WebGL/WASM renderer-submit detail during one later live run to identify the actual per-object native player-marker submission path. The probe may use P37/P39 visible marker tracking only as non-authoritative correlation input. It must never mint rendererSourceProof or weaken P29/P32/P36 authority.

Fresh PM authority:
- P36 terminal COMPLETE testedCommit `162e50b6c65fd1d3901ad694854563b686b2ce22`: bounded zero-click direct-source observer/proof producer exists, but real live source authority is not proven.
- P37 terminal COMPLETE testedCommit `64d5c3d2c1c84fffc7d9f59e701ec37fd1c68530`: zero-click auto P1/P2/P3 acquisition/reacquire baseline exists, classified `UNVERIFIED_AUTO_BASELINE`.
- P39 terminal COMPLETE testedCommit `ac5387f00d8c2382dcf3ed435ffcfa0acc1a2f05`: P37 baseline can be shown through maintained HUD in staging only, still non-authoritative.
- P40 terminal BLOCKED testedCommit `5a3b9bce01e794e030974a94f7511a39fa56e818`, blocker `NATIVE_PLAYER_MARKER_DISPLAYED_SUBMIT_SOURCE_EXPORT_NOT_PRESENT`.
- P40 proved maintained checked-in runtime exposes generic WebGL draw hooks plus HEAP/ROM/CPS RAM/world-projection surfaces, but no truthful exact per-object gstyphoon displayed-submit export carrying marker identity + actor generation + native 384x224 coordinates.

Read latest main, root AGENTS.md, dedup/progress/result protocols, P36/P37/P39/P40 terminal RESULTs, P36 observer/producer code, P37 tracker, P39 staging integration, current Page/Worker/WASM/bootstrap/WebGL hook code and any checked-in gstyphoon/WASM glue/artifacts.

Dedup-v2: this is a fresh successor to P40. If equivalent P42 ACTIVE/CLAIMED, return `ALREADY ACTIVE / CLAIMED — NO EXECUTION`; if COMPLETE/PASS, return `ALREADY COMPLETE — NO EXECUTION`; otherwise create canonical claim then stage claim with one fresh exact claimToken, read both back, then create PROGRESS.

Required work:
- instrument only read-only runtime observation surfaces needed to characterize actual renderer submissions during one later bounded run;
- capture deterministic frame-scoped WebGL/gstyphoon facts sufficient for reverse mapping, such as exact draw call, program/shader identity, bound buffers, buffer ranges/offsets, vertex attribute descriptors, texture/bank bindings where observable, viewport/scissor, frame/submission sequence, and read-only CPU-side typed-array payload identity when already present at the hook;
- keep capture bounded by explicit event/time limits and deterministic teardown;
- correlate those submissions with P37/P39 `UNVERIFIED_AUTO_BASELINE` P1/P2/P3 marker x/y only as diagnostic evidence to narrow the candidate submit path; pixel/visual correlation must be labeled diagnostic and can never become production coordinates or authority;
- emit a machine-readable diagnostic bundle such as schema `wof-gstyphoon-renderer-correlation-probe-v1` containing raw observations, correlation metadata, exact runtimeEpoch/rendererEpoch/authorityKey when available, and explicit `authorityEligible=false`;
- preserve enough raw payload/hash/offset/context detail that a later PM/Worker can determine whether one exact source-traced/exported per-object submit can be implemented, rather than only receiving a generic summary;
- never choose a candidate by nearest-only, list order, timing-only, screenshot/OCR/template-only, guessed offset, or silent heuristic. If multiple submit paths remain plausible, report ambiguity explicitly;
- do not create `__WOF_NATIVE_MARKER_RENDERER_SUBMIT_SOURCE_V1__` or `WOFNativeMarkerRendererSubmitSourceV1`; P42 is diagnostic mapping only. A future successor may create an authority source only after evidence supports one truthful mapping;
- add focused synthetic/deterministic tests for bounded capture, teardown, exact metadata capture, correlation labeling, ambiguity preservation, stale/mixed binding rejection, and proof-boundary non-impersonation.

Scope boundaries:
- prefer isolated files under `parallel/RENDER_AUTHORITY_V2/` or a new narrowly named diagnostic subdirectory;
- do not modify P29 analyzer acceptance criteria or P32 qualifier semantics;
- do not modify P36 authority contract, P37 detection heuristics, P39 maintained-HUD integration semantics, P40 terminal evidence, candidate/retry/promotion code, or alpha-live;
- no real game run under this Worker task; no Owner YES/NO; no RAM writes; no input injection; no global environment changes.

Terminal COMPLETE means an exact-byte-tested bounded diagnostic correlation probe is ready to be included in one later live diagnostic run. It does NOT mean the P40 blocker is solved. Terminal BLOCKED is correct if the checked-in runtime cannot even expose enough read-only draw/buffer context to build a useful bounded mapping probe.

Before terminal-significant self-check create a durable tested candidate commit/tree and bind PROGRESS to it. Any implementation-byte change after test requires a new candidate and rerun.

Progress checkpointing must follow parallel/PM/ALPHA_WORKER_PROGRESS_CHECKPOINT_PROTOCOL_V1.md; keep parallel/PM/PROGRESS/<stageId>_PROGRESS.json current at mandatory milestones and before any non-terminal stop.
Terminal reporting must follow parallel/PM/ALPHA_WORKER_RESULT_FAST_FEEDBACK_PROTOCOL_V1.md.

# Alpha V1 P44 — Historical GStyphoon Renderer Submit Export Archaeology — START PROMPT

StageId:
`ALPHA_V1_PRODUCT_TAKEOVER_P44_HISTORICAL_GSTYPHOON_RENDERER_SUBMIT_EXPORT_ARCHAEOLOGY`

DedupKey:
`alpha.v1.product-takeover.historical-gstyphoon-renderer-submit-export-archaeology-v1`

Mission: perform a bounded exact Git-history/source archaeology for any previously checked-in gstyphoon/CPS1 per-object renderer submit hook, exported renderer pointer, source-traced pointer, sprite/object submit bridge, or equivalent runtime surface that could materially resolve P40 blocker `NATIVE_PLAYER_MARKER_DISPLAYED_SUBMIT_SOURCE_EXPORT_NOT_PRESENT`. This lane is historical/source research only and must not overlap P42 probe implementation or P43 harness ownership.

Fresh PM authority:
- P39 is terminal COMPLETE and provides only `UNVERIFIED_AUTO_BASELINE` visible diagnostic HUD integration; it is not renderer authority.
- P40 is terminal BLOCKED because current maintained Page/Worker/WASM runtime exposes only generic WebGL draw callbacks plus HEAP/ROM/CPS RAM/world-projection paths, with no truthful per-object displayed-submit export carrying exact native marker identity/generation.
- P42 is ACTIVE and owns the new bounded renderer-submit correlation probe against current runtime.
- P43 is ACTIVE and owns the bounded zero-click live diagnostic harness/log capture.

Required preflight:
- read latest main, root AGENTS.md, dedup/progress/result protocols;
- read P36/P37/P39/P40 terminal RESULT authority and P42/P43 START prompts/progress before substantive work;
- perform dedup-v2 claim normally; if equivalent P44 ACTIVE/CLAIMED return `ALREADY ACTIVE / CLAIMED — NO EXECUTION`; if COMPLETE return `ALREADY COMPLETE — NO EXECUTION`.

Required work:
- search Git history broadly for gstyphoon/CPS1 renderer/object/sprite/tile submit surfaces, WebGL/WASM glue, exported pointers/functions, object lists, render queues, draw-object bridges, or any old source names that could be a genuine predecessor of `__WOF_NATIVE_MARKER_RENDERER_SUBMIT_SOURCE_V1__` / `WOFNativeMarkerRendererSubmitSourceV1`;
- inspect exact historical commits/blobs/functions, not only commit messages;
- include old maintained HUD/tracker eras where useful, including `6eeebf4a00ce7751ce9ba6008982e8136d1c4290` and `d30a071c668c716cd8d9b5d02932808c76c7a3a7`, but treat pixel/native-label tracking only as diagnostic context, never renderer authority;
- identify any historical coordinate transform or per-object data structure that may explain the Owner-observed old Y inversion, but do not change production coordinates in this task;
- for every plausible renderer-source candidate record exact commit, path, blob/function/symbol, source type, what semantics it actually exposes, and whether it could truthfully provide: displayed frame/submission identity, native 384x224 x/y, exact `1P/2P/3P + DOWN` marker/object identity, actor generation, runtimeEpoch/rendererEpoch/authorityKey;
- distinguish `DIRECT_SOURCE_CANDIDATE`, `CORRELATION_ONLY`, `STRUCTURAL_ONLY`, and `NOT_ELIGIBLE` explicitly;
- if an exact historical direct source exists, do not transplant or wire it here: publish the exact minimal handoff needed for a later successor, including whether the code can be restored byte-for-byte or requires adaptation;
- if no qualifying historical source exists, publish a bounded negative result with the exact search coverage and strongest non-qualifying candidates so P42/P40 are not sent in circles.

Scope boundaries:
- do not modify P42 correlation probe implementation/files;
- do not modify P43 harness/logging implementation/files;
- do not create or expose the P36 source surface;
- do not change P29/P32/P36 qualification semantics;
- do not integrate P39 into production authority;
- no real game run, no Owner click/seed, no promotion, no alpha-live movement, no global environment changes.

Deliverable:
- an isolated durable archaeology report under `parallel/RENDER_AUTHORITY_V2/**` (and an optional narrowly scoped deterministic history-audit helper/test if genuinely useful);
- exact commit/blob/path/function evidence for every retained candidate;
- terminal RESULT that is truthful whether positive or negative.

Terminal COMPLETE means the historical search itself is complete and exact evidence is durable. It does not mean renderer authority is solved. A negative search result may still be COMPLETE if the bounded coverage is explicit and reproducible.

Before any terminal-significant self-check, bind the report/helper bytes to a durable tested candidate. Any implementation-byte change after test requires a new candidate and rerun.

Progress checkpointing must follow parallel/PM/ALPHA_WORKER_PROGRESS_CHECKPOINT_PROTOCOL_V1.md; keep parallel/PM/PROGRESS/<stageId>_PROGRESS.json current at mandatory milestones and before any non-terminal stop.
Terminal reporting must follow parallel/PM/ALPHA_WORKER_RESULT_FAST_FEEDBACK_PROTOCOL_V1.md.

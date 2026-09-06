# Alpha V1 P43 — Bounded Zero-Click Live Diagnostic Harness — START PROMPT

StageId:
`ALPHA_V1_PRODUCT_TAKEOVER_P43_BOUNDED_ZERO_CLICK_LIVE_DIAGNOSTIC_HARNESS`

DedupKey:
`alpha.v1.product-takeover.bounded-zero-click-live-diagnostic-harness-v2`

Mission: clean successor to the failed pre-claim P41 attempt. Build the complete bounded zero-click live diagnostic harness for the next separately authorized real-WOF run, with exact raw evidence preservation so PM can determine the first failing gate and inspect original runtime/console/staging evidence instead of inferring from a single summary status.

Historical P41 note: the prior P41 canonical create-only attempt hit GitHub 409 before any canonical/stage claim, PROGRESS, RESULT, or implementation was created. Do not reuse the failed P41 dedup key or pretend it owned work.

Fresh PM authority:
- P36 terminal COMPLETE testedCommit `162e50b6c65fd1d3901ad694854563b686b2ce22`; its observer/producer must be captured unchanged.
- P37 terminal COMPLETE testedCommit `64d5c3d2c1c84fffc7d9f59e701ec37fd1c68530` and P39 terminal COMPLETE testedCommit `ac5387f00d8c2382dcf3ed435ffcfa0acc1a2f05`; their output is diagnostic `UNVERIFIED_AUTO_BASELINE` only.
- P40 terminal BLOCKED testedCommit `5a3b9bce01e794e030974a94f7511a39fa56e818`, blocker `NATIVE_PLAYER_MARKER_DISPLAYED_SUBMIT_SOURCE_EXPORT_NOT_PRESENT`.
- P42 is a separate parallel diagnostic correlation-probe successor to P40. P43 must not own P42 instrumentation, but the harness should preserve P42 output if such a probe is present in the selected candidate; absence must be recorded explicitly, not treated as success.

Read latest main, root AGENTS.md, dedup/progress/result protocols, P29/P30/P31/P32/P36/P37/P39/P40 terminal authority, P21/P28 staging/receipt code, current Page/Worker/WASM discovery, P16/P17/P9 gates, candidate manifest/attestation/provenance machinery, P36 observer/producer, P39 staging HUD bridge, and existing raw log capture paths.

Dedup-v2: this is a new v2 successor harness. If equivalent P43 ACTIVE/CLAIMED, return `ALREADY ACTIVE / CLAIMED — NO EXECUTION`; if COMPLETE/PASS, return `ALREADY COMPLETE — NO EXECUTION`; otherwise create canonical claim then stage claim with one fresh exact claimToken, read both back, then create PROGRESS. Any claim-create failure is fail-closed under the current protocol.

Required harness output for one later run:
- exact sourceCommit, candidate path/SHA256/Git blob, packageVersion, manifest path/SHA256, attestation path/SHA256, provenance/pointer identity and selected runtime pins;
- exact Page / Worker / WASM association evidence, including all considered page targets and authoritative association/rejection reasons;
- P16, P17 and P9 gate state with exact reasons and first transition to terminal pass/fail;
- exact runtimeEpoch, rendererEpoch and authorityKey values and any changes/stale mismatches;
- P36 source discovery raw state, discovered source candidates, rejection reasons, direct renderer-submit raw events, bounded capture metadata/teardown reason, producer result and unchanged P32 qualifier result;
- P37/P39 diagnostic tracker state for P1/P2/P3, visibility state, ambiguity/lost/stale/reacquire metadata and explicit `UNVERIFIED_AUTO_BASELINE` classification;
- if P42 probe exists, preserve its raw diagnostic bundle verbatim plus a hash/path; if absent, record `P42_CORRELATION_PROBE_NOT_PRESENT` without failing unrelated gates;
- raw runtime logs, browser/page console logs, staging logs and exact exception/error strings in original order with timestamps where available;
- machine-readable gate timeline identifying the first failing gate and all earlier successfully completed gates;
- final receipt JSON plus human-readable summary that references raw artifact filenames instead of replacing them.

Operational constraints:
- zero click / zero manual avatar seed / zero manual player selection;
- no implicit HEAD: run must require one exact source/candidate identity provided by the later authorized launcher command;
- no install logic; no deleting/modifying/upgrading/downgrading/reinstalling system Python, PATH, global site-packages or unrelated environments;
- reuse the existing dedicated WOF project venv/browser/runtime during the later run;
- bounded wall-clock/event/log limits with deterministic teardown and browser preservation policy;
- readOnly=true, ramWrites=0, inputInjection=false, alphaLiveMoved=false;
- this Worker task itself runs no real game, no Owner visual acceptance, no promotion.

Fail-closed semantics:
- never collapse multiple independent failures into only `FAILED_EVIDENCE_MISMATCH`; preserve each exact gate/error and identify the first causal stop;
- missing raw evidence that the harness contract says is mandatory must make the harness result incomplete/blocked, not silently omitted;
- diagnostic P37/P39/P42 output must never mint rendererSourceProof, P29 PASS, P32 qualification, P34 retry readiness or promotion eligibility;
- do not modify P29/P32/P36 authority criteria to make the run pass.

Focused tests must cover at least exact candidate binding, multi-page association recording, gate timeline ordering/first-failure selection, raw error preservation, P36 raw bundle preservation, P39 diagnostic state capture, optional-P42 absent/present behavior, bounded teardown, and receipt/human-summary consistency.

Terminal COMPLETE means the exact-byte-tested harness is ready for a separately authorized bounded live diagnostic run. It does not authorize that run by itself.

Before terminal-significant self-check create a durable tested candidate commit/tree and bind PROGRESS to it. Any implementation-byte change after test requires a new candidate and rerun.

Progress checkpointing must follow parallel/PM/ALPHA_WORKER_PROGRESS_CHECKPOINT_PROTOCOL_V1.md; keep parallel/PM/PROGRESS/<stageId>_PROGRESS.json current at mandatory milestones and before any non-terminal stop.
Terminal reporting must follow parallel/PM/ALPHA_WORKER_RESULT_FAST_FEEDBACK_PROTOCOL_V1.md.

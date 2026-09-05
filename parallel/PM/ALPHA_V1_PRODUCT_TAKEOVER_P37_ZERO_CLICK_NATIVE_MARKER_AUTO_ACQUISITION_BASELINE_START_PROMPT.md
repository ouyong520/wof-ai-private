# Alpha V1 P37 — Zero-Click Native Marker Auto-Acquisition Baseline — START PROMPT

StageId:
`ALPHA_V1_PRODUCT_TAKEOVER_P37_ZERO_CLICK_NATIVE_MARKER_AUTO_ACQUISITION_BASELINE`

DedupKey:
`alpha.v1.product-takeover.zero-click-native-marker-auto-acquisition-baseline-v1`

Mission: restore a deterministic zero-click automatic visible/diagnostic baseline for WOF native `1P` / `2P` / `3P` + downward-arrow tracking, using the historically working native-label tracker behavior as evidence, while keeping this baseline explicitly non-authoritative until P36 proves the direct renderer causal edge.

Fresh PM product requirement:
- final product must require **zero manual clicks and zero manual avatar/portrait seeding**;
- Owner should only start/play the game; automatic discovery must identify/reacquire P1/P2/P3 itself;
- historical repo evidence includes commit `6eeebf4a00ce7751ce9ba6008982e8136d1c4290` (`HUD v6: robust native player-label tracking through jumps`) and commit `d30a071c668c716cd8d9b5d02932808c76c7a3a7` (`anchor P1 danger directly to live screen-space head tracker`);
- Owner remembers an early visible tracker followed horizontally but inverted vertically, so Y-axis transform/orientation must be explicitly tested rather than guessed.

Read latest main, root AGENTS.md, dedup/progress/result protocols, P32 terminal BLOCKED RESULT, P36 START prompt, the exact historical commits above and their relevant files, current HUD/overlay coordinate conversion code, and current native 384x224 conventions.

Dedup-v2: if equivalent P37 ACTIVE/CLAIMED, return `ALREADY ACTIVE / CLAIMED — NO EXECUTION`; if COMPLETE/PASS, return `ALREADY COMPLETE — NO EXECUTION`; otherwise create canonical claim then stage claim with one fresh exact claimToken, read both back, then create PROGRESS.

Ownership is limited to an isolated zero-click auto-acquisition/diagnostic baseline and focused deterministic tests. Prefer a new isolated surface such as `parallel/AUTO_MARKER_BASELINE/**`; do not modify P36 renderer proof producer/qualifier semantics, P29 analyzer acceptance criteria, P33/P34/P35 candidate/readiness/integration code, production promotion flows, or alpha-live.

Required work:
- recover the exact useful ideas from the historical native-label/arrow tracker instead of reinventing from memory;
- automatic discovery must require no click, no portrait seed, no manual P1/P2/P3 selection;
- automatically produce deterministic candidate tracks for P1/P2/P3 native markers in native 384x224 coordinates and support bounded reacquisition after movement/jump/loss;
- explicitly model coordinate spaces and prove the Y transform/orientation with focused fixtures: left/right preserved, up means lower native Y / correct HUD movement, down means higher native Y / correct HUD movement as appropriate to the chosen canonical convention;
- preserve P1/P2/P3 distinction using deterministic marker/color/label/arrow structure available to the historical tracker; ambiguous scenes must fail closed or expose `AMBIGUOUS`, never silently choose first/nearest/order/timing;
- output must be visibly/structurally labeled `UNVERIFIED_AUTO_BASELINE` (or equally explicit) and must never emit or satisfy `rendererSourceProof`, P29 PASS, P32 authoritative marker qualification, P34 retry readiness, or promotion eligibility;
- screenshots/OCR/templates may not become production coordinates. This task is a diagnostic/functional baseline only; its purpose is to recover automatic visible tracking and provide high-value correlation data to P36;
- no real game run, no Owner YES/NO, no RAM writes, no input injection, no global environment changes.

Focused deterministic tests must cover at least:
- zero-click startup/acquisition path;
- P1/P2/P3 automatic distinction fixtures;
- loss/reacquire and jump-like movement;
- left/right coordinate preservation;
- explicit Y-axis non-inversion regression;
- ambiguity fail-closed;
- proof boundary: baseline can never qualify as authoritative renderer proof.

Terminal COMPLETE means the isolated zero-click baseline is durable, exact-byte tested, and ready to assist one later live diagnostic/verification run. It does **not** mean P36 is solved or real WOF authority is proven.

Before terminal-significant self-check create a durable tested candidate commit/tree and bind PROGRESS to it. Any implementation-byte change after test requires a new candidate and rerun.

Progress checkpointing must follow parallel/PM/ALPHA_WORKER_PROGRESS_CHECKPOINT_PROTOCOL_V1.md; keep parallel/PM/PROGRESS/<stageId>_PROGRESS.json current at mandatory milestones and before any non-terminal stop.
Terminal reporting must follow parallel/PM/ALPHA_WORKER_RESULT_FAST_FEEDBACK_PROTOCOL_V1.md.

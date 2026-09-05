# Alpha V1 Canonical Render Anchor — Parallel 3 Worker Dispatch V1

Status: ACTIVE DISPATCH AUTHORITY
Repository: `ouyong520/wof-ai-private`
Authority baseline observed before dispatch: `64fd6b44a0fa3cc106270e0e55073955ebca2115`

## Why this dispatch exists

The first Owner fixed-draw software chain is now implementation-complete through P4, but real-WOF visual acceptance remains intentionally unclaimed. Owner has directed implementation-first cadence: continue building coherent product capability now and defer broad/end-to-end testing until a meaningful product candidate exists.

W3 already owns renderer/object source qualification under its existing ACTIVE dedup authority. Do not create, revive, steal, modify, or parallelize an equivalent W3 claim. W3 has already implemented the fail-closed `DeterministicRenderObjectAnchor` consumer and bounded capture, but renderer source remains unproven until a later live observation.

This dispatch therefore works only on downstream product consumers. Every worker must preserve the invariant:

`renderer source unproven / stale / ambiguous -> canonical anchor SUPPRESSED -> no product label/warning drawn`

No worker may promote structural object candidates, screenshot/template tracking, world/camera projection, Y/Y-Z/Y+Z fitting, click calibration, nearest-sprite association, or guessed constants into canonical production position authority.

## Product direction

Target product flow after W3 eventually proves the source:

`proven exact renderer/object frame -> canonical native actor anchor (384x224) -> P1 top label -> enemy head target labels -> danger near affected player`

The current round builds those consumers now so the later W3 qualification only unlocks data; it should not require rewriting product presentation logic.

## Shared hard boundaries

- Alpha only.
- Do not read/run/modify/test Collector, Unified Collector, Training Farm / 10训.
- Do not modify W3 capture/producer ownership files unless a prompt explicitly permits a narrow import-only compatibility change; default is no W3 production-file edits.
- Do not modify W3 canonical/stage claims.
- Do not move or force-update `alpha-live`.
- Do not ask Owner to test in this worker round.
- Do not claim real-WOF product PASS.
- Preserve exact World 921031 binding and `readOnly=true`, `ramWrites=0`, `inputInjection=false`.
- Implementation first; minimum self-check only. No Fresh QA, second opinion, broad regression, release audit, or Owner acceptance task.
- Use RESULT protocol `wof-alpha-worker-result-v1` and exact manifest-declared RESULT paths.

## Worker split

### Slot 1 — P5 P1 canonical render-anchor wiring

Goal: make the maintained production HUD/runtime able to consume a `wof-render-object-anchor-v1` READY P1 anchor and draw the normal P1 top-of-head product marker through the maintained WebGL HUD path. Build a narrow adapter/bridge around the existing W3 consumer contract; do not change how renderer authority is proven.

Required behavior:
- accept only exact native `384x224` canonical anchors with matching authority/runtime/renderer epochs and safety fields;
- READY P1 anchor -> maintained HUD receives deterministic native anchor;
- SUPPRESSED/stale/revoked/ambiguous/unproven -> product marker hides immediately;
- no screenshot-template steady-state position authority;
- no old relative projection fallback;
- no manual calibration/click requirement;
- preserve fixed-draw gate behavior and normal mode behavior;
- leave a clean interface that W3 source qualification can feed without further HUD redesign.

Preferred scope: a new narrow Python bridge/adapter plus the smallest maintained-HUD API wiring needed. Avoid editing enemy/danger modules owned by P6/P7.

### Slot 2 — P6 enemy canonical render-anchor target-label consumer

Goal: migrate enemy target-label planning away from legacy world/camera/Y-model geometry to canonical render-object anchors while preserving target semantics.

Required behavior:
- consume canonical READY enemy anchors keyed by enemy actor/generation/slot;
- `target7E: 0 -> P1 -> 1P`, `4 -> P2 -> 2P`, `8 -> P3 -> 3P`;
- label position is the canonical enemy head anchor, not projected from P1/world/camera;
- stale, missing, ambiguous, unsafe, unproven, generation-mismatched anchors suppress the label;
- enemy label logic must not wait for P1 screenshot/head tracker;
- keep draw-plan output in maintained HUD drawing-buffer/native mapping contract;
- legacy projection APIs may remain for compatibility but canonical path must be a separate explicit path and must not silently fall back to legacy geometry.

Preferred scope: `product/alpha/wof_alpha_enemy_target_labels.js` plus minimal owned self-check fixture if needed. Do not edit common HUD runtime owned by P5 unless unavoidable; if unavoidable, stop and report exact integration dependency instead of racing.

### Slot 3 — P7 player danger canonical-anchor consumer

Goal: migrate player-head danger/warning placement away from legacy world/camera projection to canonical player anchors.

Required behavior:
- warnings remain grouped by affected player P1/P2/P3;
- consume canonical READY player anchor for the affected player;
- warning draw rectangle is derived from that canonical head anchor;
- stale/missing/ambiguous/unsafe/unproven/generation-mismatched anchor suppresses anchored warning rather than guessing;
- do not use screenshot-template steady state, old projection profile, Y model, camera sign, or calibration as canonical fallback;
- preserve warning semantics/content; this task changes position authority, not threat-model policy;
- expose an explicit canonical-anchor planning path so later runtime integration does not need geometry redesign.

Preferred scope: `product/alpha/wof_alpha_player_head_warning.js` plus minimal owned self-check fixture if needed. Do not edit common HUD runtime owned by P5 unless unavoidable.

## Acceptance for this implementation round

This round is successful when:
1. P5 can drive maintained HUD position from a valid canonical P1 anchor and fail closed otherwise;
2. P6 can build correct enemy `1P/2P/3P` plans from canonical enemy anchors without P1/world-camera geometry;
3. P7 can build player danger plans from canonical player anchors without legacy projection geometry;
4. all three preserve suppression while W3 source is still unproven;
5. no worker claims real-WOF PASS or moves `alpha-live`.

After all three are accepted, PM will integrate consumers, then later use the same permanent Owner channel for a bounded W3 source qualification and consolidated product acceptance instead of reopening geometry implementation.
# WOF Alpha V1 — Player-Head Danger Warning Production Integration

stageId: `ALPHA_V1_PLAYER_HEAD_WARNING_PRODUCTION_INTEGRATION_V1`
dedupProtocol: `v2`
dedupKey: `alpha.v1.player-head-danger-warning.production-integration`
dedupMode: `exclusive`

Priority: **P0 Alpha V1 mandatory product integration**

## Product decision

Re-read the current authoritative requirement:

`parallel/PM/ENEMY_TARGET_LOCK_HUD_REQUIREMENT.md`

Alpha V1 now requires **both**:

1. danger reminder above the targeted live player's head;
2. enemy-head current-target tracker `1P` / `2P` / `3P`.

The old statement that player-head warning could wait for Beta has been superseded. Fixed HUD remains only a fail-closed fallback / startup / diagnostic surface when a trustworthy player-head anchor is unavailable.

Any repeatable or clearly visible overlay drift during rapid movement, jump or whole-screen scrolling is a P0 release blocker.

## Start / canonical dedup

Before task work, re-read latest `main`, `parallel/PM/STAGE_DEDUP_GUARD.md`, current stage/canonical claims, relevant recent commits/results, and at minimum:

- current `parallel/PM/ENEMY_TARGET_LOCK_HUD_REQUIREMENT.md`;
- `parallel/HUDANCHOR_PLAYER_FOLLOW/RESULT.md`;
- `parallel/HUDANCHOR_PLAYER_FOLLOW_QA/RESULT.md`;
- `parallel/HUDANCHOR_PLAYER_FOLLOW_BOUNDS_QA/RESULT.md`;
- `parallel/HUDANCHOR_PLAYER_FOLLOW_QA_CONFIDENCE/RESULT.md`;
- current `parallel/HUDANCHOR_PLAYER_FOLLOW/src/**` and regression/stress fixtures;
- current `product/alpha/wof_alpha_real_worker.js`;
- current `product/alpha/wof_alpha_hud.js`;
- current loader/bootstrap/core/rules regression only as needed for compatibility;
- current target-label implementation/result so the two overlay paths do not conflict.

Search for any equivalent current Alpha production integration first. If already COMPLETE/current, stop `ALREADY COMPLETE — SAFE TO CLOSE`.

Otherwise first mutation is create-only canonical claim:

`parallel/PM/DEDUP_CLAIMS/alpha.v1.player-head-danger-warning.production-integration.json`

with fresh unpredictable `claimToken`; re-read from current `main` and verify exact ownership. Then create:

`parallel/PM/STAGE_CLAIMS/ALPHA_V1_PLAYER_HEAD_WARNING_PRODUCTION_INTEGRATION_V1.json`

Any ownership ambiguity fails closed as `ALREADY CLAIMED — SAFE TO CLOSE`.

## Integration goal

Integrate the already-researched HUDANCHOR player-follow model into the real Alpha production path without changing danger detection semantics.

For each current supported warning:

- use the warning's authoritative current target P1/P2/P3;
- resolve the corresponding current live player identity and fresh world/projection state;
- render the warning near/above that player's head on the game WebGL surface;
- retarget immediately: old player's anchored warning disappears before the new target can appear;
- if the new/current anchor cannot be proven valid, use the fixed HUD fallback rather than leaving a stale anchored warning;
- multiple supported warnings may aggregate per player if that preserves correctness and legibility;
- do not attach the danger reminder to the enemy; enemy-head `1P/2P/3P` remains a separate decorative tracker.

Do not modify warning rule thresholds, attack semantics, target semantics, transport authority, or game behavior.

## P0 dynamic/non-drift contract

Repository implementation and deterministic regression must model at least:

1. player left/right movement;
2. player depth/lane movement;
3. jump ascent/apex/descent/landing or equivalent vertical displacement series;
4. rapid forward/back movement;
5. camera/stage scrolling;
6. simultaneous player + camera movement;
7. resize/fullscreen/DPR/drawing-buffer remap;
8. P1/P2/P3 simultaneous presence;
9. death/respawn/player-object replacement;
10. P1 -> P2 -> P3 retarget with no stale old-owner frame/hold;
11. stale/malformed/non-finite/out-of-bounds player or projection state;
12. runtime/projection/drawing-buffer epoch mismatch;
13. rapid valid/invalid alternation without stale screen-coordinate reuse.

Do not use smoothing/hold to hide an authority gap. When fresh positioning cannot be proven, hide/fallback.

Do **not** blindly reuse a low publication cadence if it can create visible following lag. Re-read the actual detector/render cadence and choose a bounded current-snapshot publication/update scheme justified for dynamic head following. Keep payload and CPU cost bounded, but correctness/non-drift wins over cosmetic persistence. Record the exact chosen cadence and why it cannot reuse stale coordinates.

## Projection authority

Do not invent Browser constants.

Reuse only projection/player-coordinate facts that are already durably supported by current HUDANCHOR repository evidence. If a production activation profile still depends on unproved real Browser/WOF camera/Y-Z/head-offset facts, implement the path fail-closed and leave it inactive until the later bounded live proof.

Repository/synthetic PASS must never be described as proof that real WOF fast movement/jump/scroll visually does not drift.

## Expected production shape

Prefer a small reusable player-head warning model/helper rather than embedding untestable math directly in the renderer. Production changes may include only what is actually required, such as:

- `product/alpha/wof_alpha_real_worker.js` for current read-only player snapshot/projection metadata;
- `product/alpha/wof_alpha_hud.js` for anchored warning rendering + fixed fallback;
- a new narrowly-scoped `product/alpha/wof_alpha_player_head_warning.js` helper if useful;
- `product/alpha/wof_alpha_loader.js` only if a new helper must be loaded;
- `product/alpha/regression.mjs` and a focused player-head regression file if needed;
- a fail-closed player projection/profile file only when it accurately represents current proof state.

Do not touch Safe Transport, Formal, Unified, PYLAUNCH, OneClick or game code. If those interfaces require a semantic expansion rather than a presentation-only current snapshot addition, stop and report the exact blocker instead of silently widening authority.

## Safety invariants

Preserve exactly:

- read-only observer;
- `ramWrites=0`;
- input injection false;
- no Worker replacement;
- no Blob Worker rewrite;
- no gameplay target selection or enemy AI modification;
- current session/pair/generation/nonce/runtime-epoch authority;
- game WebGL state save/draw/restore discipline;
- base game unaffected on Alpha failure.

## Required evidence

Write implementation evidence only under:

- `parallel/ALPHA_V1_PLAYER_HEAD_WARNING_PRODUCTION_INTEGRATION/**`;
- this stage claim and canonical claim.

Record exact changed blobs, regression commands/results, chosen update cadence, fail-closed behavior and remaining real-live proof boundary.

No Browser/WOF launch in this implementation stage.

## Stop conditions

Success:

`COMPLETE — ALPHA V1 PLAYER-HEAD DANGER WARNING PRODUCTION INTEGRATED — READY FOR FRESH QA / BOUNDED DYNAMIC LIVE PROOF`

Failure:

`BLOCKED — ALPHA V1 PLAYER-HEAD DANGER WARNING PRODUCTION INTEGRATION — <precise blocker>`

Owner action: **NO**.

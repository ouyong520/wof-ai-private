# HUDANCHOR Player-Follow Long Stress Matrix Result

Stage: `HUDANCHOR_PLAYER_FOLLOW_LONG_STRESS_MATRIX_V1`

Status: **BLOCKED — HUDANCHOR PLAYER-FOLLOW LONG STRESS — invalid/non-finite projection confidence authorizes anchored rendering instead of fixed-HUD fail-closed fallback**

## Current-HEAD / SUT evidence

- testedHead: `1b6387e0061120d27820cbc02a4682292237c785`
- SUT: `parallel/HUDANCHOR_PLAYER_FOLLOW/src/player_follow_reference.js`
- SUT blob: `4beb7f8d4c9f815e125ed795aca536f02562f5d1`
- current-head re-read confirmed the SUT blob had not changed after the long-stress runner was added.

## Precise P1 blocker

The long-stress matrix explicitly requires coverage for `invalid projection confidence` and the authoritative product contract requires fixed HUD whenever player/camera/projection state is invalid or stale.

Current SUT does not fail closed for a non-finite projection confidence:

1. `confidenceOf(value, fallback = 1)` returns `fallback` for a non-finite value.
2. Therefore `projectionState.confidence = NaN` is normalized to `1` rather than treated as invalid.
3. The resolver still returns `ok: true` when coordinates, age, epoch and bounds are otherwise valid.
4. `AnchoredWarningRenderer` gates fallback on `!anchor.ok`; it does not reject the resulting invalid-confidence anchor.
5. Result: an invalid projection confidence can authorize a player-head anchored warning instead of the required fixed-HUD fallback.

This is P1 product-experience relevant because anchored rendering asserts spatial authority above a specific live player. If the projection confidence itself is invalid, retaining anchored authority can present a warning at an untrustworthy player-head position. Fixed HUD is the required fail-closed presentation in that state.

The same normalization behavior also applies to non-finite projected/player/drawing-buffer confidence values; this stage stops on the projection-confidence case required by the start prompt rather than widening scope.

## Durable stress assets

Added under the allowed stage-only directory:

- `matrix.json` — machine-readable 30-case coverage matrix and invariants;
- `long_stress_matrix.js` — dependency-free deterministic Node runner against the real public SUT module;
- `package.json` — `npm test` / `npm run stress` entry point.

The deterministic corpus is configured for:

- 16 fixed seeds;
- 1,024 transitions per seed;
- 16,384 transition steps total when the runner is allowed to complete;
- per-seed output for target player, player generation, projection generation, anchor validity, renderer mode, visible owner, and stale/clear reason.

Directed checks cover routing/retarget, stale and non-finite state, finite out-of-bounds anchor, near-edge valid anchor, resize/fullscreen/DPR mapping reset, lifecycle replacement, warning clear, unsupported targets, multi-warning isolation, and the invalid-projection-confidence fail-closed case.

## Why the stage stops here

The start prompt defines discovery of a precise P0/P1 product-experience blocker as an immediate valid stop condition. The confidence case is deterministic from the current committed SUT contract, so this lane must not modify the SUT or weaken the invariant to force a PASS.

The 16,384-step corpus is retained as a runnable regression asset for the fresh fix/QA lane. This stage does not claim `READY FOR REAL PROJECTION FREEZE` while the blocker exists.

## Scope / safety

Preserved:

- no modification to `parallel/HUDANCHOR/**` or the player-follow SUT;
- no Browser proof automation changes;
- no Alpha / Discovery / Recorder / PYLAUNCH changes;
- no RAM writes, gameplay input, or implementation capability added;
- no guessed Browser projection constants.

## Stop condition

**BLOCKED — HUDANCHOR PLAYER-FOLLOW LONG STRESS — invalid/non-finite projection confidence authorizes anchored rendering instead of fixed-HUD fail-closed fallback**

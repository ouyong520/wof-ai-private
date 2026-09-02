# WOF Alpha V1 — Player-Head Danger Warning Strict warningSampleAt Fix

stageId: `ALPHA_V1_PLAYER_HEAD_WARNING_STRICT_SAMPLEAT_FIX_V1`
dedupProtocol: `v2`
dedupKey: `alpha.v1.player-head-danger-warning.strict-warning-sampleat-fix`
dedupMode: `exclusive`

Priority: **P0 Alpha V1 release blocker fix**

## Purpose

Fresh Independent QA V1 is BLOCKED on one narrow fail-closed defect in the current player-head anchored warning helper: missing/malformed/coercible semantic `warningSampleAt` disables the retarget freshness barrier instead of failing closed, allowing older pre-retarget player/projection samples to authorize an anchored warning.

The authoritative blocker is:

`parallel/ALPHA_V1_PLAYER_HEAD_WARNING_QA/RESULT.md`

This is a narrow implementation fix. Preserve all already validated behavior and do not widen scope.

## Start / canonical dedup v2

Before substantive work re-read current `main`, `parallel/PM/STAGE_DEDUP_GUARD.md`, current stage/canonical claims, recent relevant commits, and at minimum:

- `parallel/ALPHA_V1_PLAYER_HEAD_WARNING_QA/RESULT.md`;
- `parallel/PM/STAGE_CLAIMS/ALPHA_V1_PLAYER_HEAD_WARNING_QA_V1.json`;
- `parallel/ALPHA_V1_PLAYER_HEAD_WARNING_PRODUCTION_INTEGRATION/RESULT.md`;
- current `product/alpha/wof_alpha_player_head_warning.js`;
- current `product/alpha/player_head_warning_regression.mjs`;
- current HUD/worker only if needed to verify the call contract.

If an equivalent fix is already COMPLETE on the current helper contract, stop `ALREADY COMPLETE — SAFE TO CLOSE`.

Otherwise first mutation must be create-only canonical claim:

`parallel/PM/DEDUP_CLAIMS/alpha.v1.player-head-danger-warning.strict-warning-sampleat-fix.json`

using a fresh unpredictable `claimToken`. Re-read current `main` and the exact canonical claim and verify all v2 ownership fields/token/state. Only then create:

`parallel/PM/STAGE_CLAIMS/ALPHA_V1_PLAYER_HEAD_WARNING_STRICT_SAMPLEAT_FIX_V1.json`

Any ambiguity => `ALREADY CLAIMED — SAFE TO CLOSE`.

## Required fix

Make semantic warning timing authority exact and fail-closed before any retarget freshness comparison.

At minimum:

1. `warningSampleAt` must be a primitive finite number for anchored player-head authorization;
2. missing / `null` / numeric string / boxed number / coercible object / `NaN` / `Infinity` must not bypass the barrier;
3. invalid `warningSampleAt` must route the warning to the existing fixed-HUD fallback / no anchored coordinate;
4. valid numeric `warningSampleAt` retains current behavior: player/projection samples older than the semantic warning sample fail closed;
5. preserve 20 ms active spatial publication, 80 ms player/projection freshness, zero hold/smoothing, current P1/P2/P3 aggregation, retarget behavior, lifecycle handling, confidence/bounds/epoch checks and current drawing-buffer mapping;
6. do not change danger-rule thresholds/selection, `target7E` semantics, Safe Transport authority, session/pair/generation/nonce/runtime-epoch authority, game input/AI or game RAM;
7. do not activate or guess the still-unproven projection profile.

Add focused committed regression coverage for the malformed timestamp attacks from QA plus valid numeric controls. Run the existing focused regression and relevant syntax/source-contract checks.

## Write boundary

Prefer changes only to:

- `product/alpha/wof_alpha_player_head_warning.js`;
- `product/alpha/player_head_warning_regression.mjs`;
- a dedicated result lane under `parallel/ALPHA_V1_PLAYER_HEAD_WARNING_STRICT_SAMPLEAT_FIX/**`;
- this stage/canonical claim updates.

Touch HUD/worker only if strictly necessary to preserve the same exact semantic authority contract, and document why.

No Browser/WOF launch.

## Stop

COMPLETE only when the narrow defect is fixed with regression evidence and all preserved behavior remains intact:

`COMPLETE — ALPHA V1 PLAYER-HEAD DANGER WARNING STRICT warningSampleAt FIX — READY FOR FRESH QA V2`

BLOCKED:

`BLOCKED — ALPHA V1 PLAYER-HEAD DANGER WARNING STRICT warningSampleAt FIX — <precise blocker>`

Owner action: **NO**.

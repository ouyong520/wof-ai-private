# WOF Alpha V1 — Enemy Target Head Labels Drawing-Buffer / Projection Epoch Fix

stageId: `ALPHA_ENEMY_TARGET_HEAD_LABELS_DRAWING_BUFFER_EPOCH_FIX_V1`
dedupProtocol: `v2`
dedupKey: `alpha.enemy-target-head-labels.drawing-buffer-projection-epoch-fix`
dedupMode: `exclusive`

Priority: **P0/P1 Alpha V1 release blocker fix**

## Purpose

Fresh QA V2 closed the strict raw-target coercion defect but found one remaining fail-closed bug: an internally-consistent stale drawing-buffer epoch such as `runtime-old/runtime-old` can still be accepted beside the current marker/projection epoch such as `runtime-a`, allowing a confident label instead of suppression.

This is a narrow implementation fix for that exact cross-epoch authority hole. Do not widen into Browser/WOF projection research or unrelated HUD refactors.

## Start / canonical dedup

Before task work, re-read latest `main`, `parallel/PM/STAGE_DEDUP_GUARD.md`, current stage/canonical claims, and at minimum:

- `parallel/ALPHA_ENEMY_TARGET_HEAD_LABELS_QA_V2/RESULT.md`;
- `parallel/PM/STAGE_CLAIMS/ALPHA_ENEMY_TARGET_HEAD_LABELS_QA_V2.json`;
- `parallel/ALPHA_ENEMY_TARGET_HEAD_LABELS_STRICT_TARGET_TYPE_FIX/RESULT.md`;
- current `product/alpha/wof_alpha_enemy_target_labels.js`;
- current `product/alpha/enemy_target_labels_regression.mjs`;
- current `product/alpha/wof_alpha_hud.js` only to understand how drawing-buffer state is constructed.

If an equivalent current fix is already COMPLETE on the current helper blob, stop `ALREADY COMPLETE — SAFE TO CLOSE`.

Otherwise first mutation is create-only canonical claim:

`parallel/PM/DEDUP_CLAIMS/alpha.enemy-target-head-labels.drawing-buffer-projection-epoch-fix.json`

with a fresh unpredictable `claimToken`. Re-read current `main` and verify exact token/metadata ownership. Only after canonical ownership is verified create:

`parallel/PM/STAGE_CLAIMS/ALPHA_ENEMY_TARGET_HEAD_LABELS_DRAWING_BUFFER_EPOCH_FIX_V1.json`

Any ownership ambiguity fails closed as `ALREADY CLAIMED — SAFE TO CLOSE`.

## Required fix

At the target-label consumer boundary, a confident plan may be produced only when all relevant current epoch authorities agree.

At minimum:

1. drawing-buffer state epoch/projectionEpoch must be exact-current relative to the projection epoch used for that plan;
2. an internally self-consistent stale pair (`runtime-old` / `runtime-old`) must not pass merely because the two drawing-buffer fields agree with each other;
3. marker epoch/projectionEpoch, projection epoch and drawing-buffer epoch/projectionEpoch must not form mixed generations;
4. missing, malformed, non-string/coercible or mismatched epoch authority must fail closed;
5. do not normalize/coerce an epoch into validity;
6. preserve strict primitive numeric raw target semantics from the previous fix;
7. preserve `0/4/8 -> 1P/2P/3P`, retarget, simultaneous-enemy, stale, confidence, bounds and resize fail-closed behavior;
8. keep `UNPROVEN` projection silent; do not promote or guess Browser projection constants.

Prefer fixing the reusable helper boundary in `wof_alpha_enemy_target_labels.js`. If the exact defect cannot be closed without changing a broader runtime/HUD contract, stop BLOCKED and name the smallest required owner lane instead of casually widening scope.

## Required regression

Add deterministic regression coverage including at least:

- current markers/projection/drawing-buffer all `runtime-a` => valid case remains valid;
- markers/projection `runtime-a`, drawing-buffer `runtime-old/runtime-old` => no label;
- drawing-buffer epoch `runtime-a`, projectionEpoch `runtime-old` => no label;
- projection missing/malformed epoch => no label;
- marker epoch mismatch => no label;
- strict raw target strings/boxed/coercible values remain rejected;
- normal retarget and simultaneous enemies remain green.

Run the current implementation regression plus focused new cases. Record exact product blobs and commands.

## Write boundary

Allowed production writes only:

- `product/alpha/wof_alpha_enemy_target_labels.js`;
- `product/alpha/enemy_target_labels_regression.mjs`.

Allowed evidence writes:

- `parallel/ALPHA_ENEMY_TARGET_HEAD_LABELS_DRAWING_BUFFER_EPOCH_FIX/**`;
- this stage claim and canonical claim updates.

Do not modify worker/HUD/loader/projection profile unless the narrow helper fix is demonstrably impossible; if broader change is required, stop BLOCKED rather than expanding.

No Browser/WOF launch.

## Drift / stop

Re-read current `main` before finalization. If relevant product blobs moved, rebase/retest against current facts rather than certifying stale evidence.

Success:

`COMPLETE — ALPHA ENEMY TARGET HEAD LABEL DRAWING-BUFFER EPOCH FIX — READY FOR FRESH QA V3`

Failure:

`BLOCKED — ALPHA ENEMY TARGET HEAD LABEL DRAWING-BUFFER EPOCH FIX — <precise blocker>`

Owner action: **NO**.

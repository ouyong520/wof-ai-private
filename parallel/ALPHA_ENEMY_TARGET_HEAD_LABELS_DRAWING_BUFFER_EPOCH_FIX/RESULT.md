# Alpha V1 Enemy Target Head Labels — Drawing-Buffer / Projection Epoch Fix Result

Stage: `ALPHA_ENEMY_TARGET_HEAD_LABELS_DRAWING_BUFFER_EPOCH_FIX_V1`

Status: **COMPLETE — ALPHA ENEMY TARGET HEAD LABEL DRAWING-BUFFER EPOCH FIX — READY FOR FRESH QA V3**

Owner action during this implementation stage: **NO**.

## Canonical dedup v2 / ownership

- `dedupKey`: `alpha.enemy-target-head-labels.drawing-buffer-projection-epoch-fix`
- start HEAD observed immediately before claim: `9331307842cf5871e57d501b8e4ab9286f8dea1c`
- canonical create-only claim commit: `7fcf476a4c1d34ba713ee532d7d514e6963498e6`
- stage create-only claim commit: `653aad3f55712f458931f19ae0f01474bf56d481`
- canonical claim was re-read from current `main` before task execution and its schema/key/effectiveKey/mode/stage/prompt/`ACTIVE` state plus this worker's exact private `claimToken` all matched.

No implementation work began before canonical ownership was verified.

## Blocking defect fixed

Fresh QA V2 had shown that the target-label helper accepted a locally self-consistent stale drawing-buffer pair such as:

- marker epoch / projection epoch: `runtime-a`;
- drawing-buffer `epoch`: `runtime-old`;
- drawing-buffer `projectionEpoch`: `runtime-old`.

The old helper only required the two drawing-buffer epoch fields to agree with each other. That allowed an old drawing-buffer mapping to be combined with a newer accepted projection and produce a confident label.

The reusable consumer boundary is now fail-closed across all three authorities.

## Narrow implementation

Only the two production files permitted by the start prompt were changed.

### `product/alpha/wof_alpha_enemy_target_labels.js`

- implementation commit: `5a218102acbcb56607deb4d626c6fa4c4cd6e711`
- resulting Git blob: `e6e1260559f735b85ce6f69e87803369f125b2de`

`validateDrawingBuffer()` now receives the current plan's `projection.epoch` and requires:

1. `drawingBufferState.epoch` is a non-empty primitive string;
2. `drawingBufferState.projectionEpoch` is a non-empty primitive string;
3. the current projection epoch is a non-empty primitive string;
4. drawing-buffer `epoch === projectionEpoch`;
5. drawing-buffer `epoch === current projection.epoch`.

Missing, empty, boxed, array, object/coercible, internally mismatched, or cross-generation epoch authority is rejected. No epoch normalization/coercion is performed.

The existing strict raw target boundary remains unchanged: only exact primitive numeric `0 / 4 / 8` are accepted as `P1 / P2 / P3`; strings, boxed numbers, coercible values, booleans, arrays, non-finite/fractional values and other malformed raw targets remain fail-closed.

### `product/alpha/enemy_target_labels_regression.mjs`

- regression commit: `a9b59edd24a9e13561bccb4727ccb8989c587abd`
- resulting Git blob: `410c6dabf317eb08bea07f77800fb4ef3e82ed2b`

Added deterministic coverage for:

- current marker/projection/drawing-buffer all `runtime-a` remains valid;
- current marker/projection `runtime-a` plus drawing-buffer `runtime-old/runtime-old` is suppressed;
- drawing-buffer `runtime-a/runtime-old` split is suppressed;
- missing/null/empty/boxed/array/coercible drawing-buffer epoch fields are suppressed;
- missing/null/empty/boxed/array/coercible projection epoch is suppressed;
- strict malformed raw-target cases remain rejected;
- existing retarget, simultaneous-enemy, stale, bounds and resize cases remain green.

No HUD/worker/loader/projection profile contract was widened.

## Regression evidence

Durable machine evidence:

- `parallel/ALPHA_ENEMY_TARGET_HEAD_LABELS_DRAWING_BUFFER_EPOCH_FIX/regression_result.json`
- evidence commit: `11a026c730e50fe8efacc48a9c1c3fa5f2d8d38d`

Exact changed-file reconstruction was verified by Git blob hashing:

- helper -> `e6e1260559f735b85ce6f69e87803369f125b2de`
- implementation regression -> `410c6dabf317eb08bea07f77800fb4ef3e82ed2b`
- HUD model -> `16641129ff651c2733aebc6fae09a280e4bac49b`
- projection profile -> `8de57739818503a0e14702d2fa0bb4eba58228d2`

Current unchanged static compatibility blobs were re-read directly from GitHub:

- real worker -> `924d02eb575d1031b168b3bb7450c34107447c85`
- HUD -> `b6f9cbf23ec1c00fe969aa2a2b59ad5e0d5433f4`
- loader -> `b1d2bd5cc3f5e4e7a3bed084d6d35ea71489717b`

Commands executed:

- `node --check product/alpha/wof_alpha_enemy_target_labels.js` -> PASS
- `node --check product/alpha/enemy_target_labels_regression.mjs` -> PASS
- `node product/alpha/enemy_target_labels_regression.mjs` -> PASS, **14 / 14**
- focused drawing-buffer/projection epoch matrix -> PASS

The regression harness reads worker/HUD/loader only as static compatibility text. The changed helper/regression and the HUD model/profile were reconstructed byte-for-byte; current GitHub source and blob identity were used to verify the unchanged static dependency assertions before execution. This follows the same repository-only execution boundary used by the preceding strict-target implementation stage.

## Preserved behavior

The implementation regression remains green for:

- exact `0 / 4 / 8 -> 1P / 2P / 3P` mapping;
- strict raw target exact-type rejection;
- unsupported target suppression;
- immediate `P1 -> P2 -> P3` retarget with no stale hold;
- simultaneous enemies;
- same-slot replacement;
- stale marker/projection suppression and marker epoch mismatch;
- invalid confidence / non-finite XYZ fail-closed;
- near-edge label rectangle clamp and out-of-bounds anchor suppression;
- resize/fullscreen drawing-buffer remap;
- fixed warning HUD compatibility;
- read-only safety and current Alpha/Formal transport compatibility.

## Projection / Browser boundary

`product/alpha/wof_alpha_enemy_head_projection.json` remains unchanged at blob `8de57739818503a0e14702d2fa0bb4eba58228d2` with:

- `verdict: UNPROVEN`
- `status: FAIL_CLOSED_UNTIL_IMPLEMENTATION_READY_PROOF`

No Browser/WOF process was launched. Repository/synthetic PASS here is not real Browser/WOF projection proof and does not promote any projection constants.

## Current-HEAD drift check

Before durable result finalization, `main` had advanced through unrelated concurrent work to `11a026c730e50fe8efacc48a9c1c3fa5f2d8d38d`. Re-read product blobs still matched the tested helper `e6e126...` and regression `410c6d...`; the unchanged worker/HUD/loader/profile blobs also remained current. No relevant product drift required rebase/retest.

## Downstream

The prior QA V2 BLOCKED result remains historical evidence and is not rewritten. This implementation stage is complete, but release consumers should require a **fresh independent QA V3** against the new helper/regression blobs before treating the Head Labels blocker as cleared.

## Stop condition

**COMPLETE — ALPHA ENEMY TARGET HEAD LABEL DRAWING-BUFFER EPOCH FIX — READY FOR FRESH QA V3**

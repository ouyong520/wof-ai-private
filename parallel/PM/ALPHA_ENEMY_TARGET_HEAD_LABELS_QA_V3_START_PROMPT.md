# WOF Alpha V1 — Enemy Target Head Labels Fresh Independent QA V3

stageId: `ALPHA_ENEMY_TARGET_HEAD_LABELS_QA_V3`
dedupProtocol: `v2`
dedupKey: `alpha.enemy-target-head-labels.post-drawing-buffer-epoch-fix-fresh-qa`
dedupMode: `exclusive`

Priority: **P0/P1 Alpha V1 release-gate fresh QA**

## Purpose

Fresh QA V2 validated the strict raw-target type fix but found one fail-closed blocker: an internally-consistent stale drawing-buffer epoch could be accepted alongside a current marker/projection epoch. The dedicated narrow fix stage is now COMPLETE and reports READY FOR FRESH QA V3.

This stage is the independent post-fix verification against the current exact product blobs. Do not reuse the implementation regression or the QA V2 verdict as proof.

## Start / canonical dedup v2

Before substantive QA, re-read current `main`, `parallel/PM/STAGE_DEDUP_GUARD.md`, current stage/canonical claims, recent commits, and at minimum:

- `parallel/ALPHA_ENEMY_TARGET_HEAD_LABELS_QA_V2/RESULT.md`;
- `parallel/ALPHA_ENEMY_TARGET_HEAD_LABELS_DRAWING_BUFFER_EPOCH_FIX/RESULT.md`;
- `parallel/PM/STAGE_CLAIMS/ALPHA_ENEMY_TARGET_HEAD_LABELS_DRAWING_BUFFER_EPOCH_FIX_V1.json`;
- current `product/alpha/wof_alpha_enemy_target_labels.js`;
- current `product/alpha/enemy_target_labels_regression.mjs`;
- current projection profile / HUD / real worker only as needed to establish interface facts.

If an equivalent current independent QA already COMPLETE/PASS on the same helper/projection/runtime contract, stop `ALREADY COMPLETE — SAFE TO CLOSE`.

Otherwise first mutation must be create-only canonical claim:

`parallel/PM/DEDUP_CLAIMS/alpha.enemy-target-head-labels.post-drawing-buffer-epoch-fix-fresh-qa.json`

with a fresh unpredictable `claimToken`. Re-read current `main` and exact canonical file and verify ownership. Only then create:

`parallel/PM/STAGE_CLAIMS/ALPHA_ENEMY_TARGET_HEAD_LABELS_QA_V3.json`

Any ownership ambiguity => `ALREADY CLAIMED — SAFE TO CLOSE`.

## Fresh independent QA matrix

Create an independent fixture/harness under this QA lane. At minimum verify:

1. primitive numeric raw targets exactly `0/4/8` map to `1P/2P/3P`;
2. numeric strings, boxed numbers, coercible objects, arrays, booleans, null/undefined, NaN/Infinity and fractions fail closed;
3. raw/normalized target mismatch fails closed;
4. all current marker epoch/projectionEpoch, projection epoch and drawing-buffer epoch/projectionEpoch equal `runtime-a` => valid synthetic label remains valid;
5. marker/projection `runtime-a` with drawing-buffer `runtime-old/runtime-old` => no label;
6. drawing-buffer epoch `runtime-a` with drawing-buffer projectionEpoch `runtime-old` => no label;
7. marker epoch/projectionEpoch mismatch => no label;
8. projection missing, malformed, non-string/coercible or mismatched epoch => no label;
9. drawing-buffer epoch missing, malformed, non-string/coercible or mismatched => no label;
10. P1 -> P2 -> P3 retarget updates with no old label hold;
11. simultaneous enemies retain independent correct targets;
12. disappearance / same-slot replacement cannot inherit stale label;
13. stale marker/projection, invalid confidence, non-finite coordinates, unsupported type/target, invalid/out-of-bounds anchor all suppress;
14. resize/fullscreen/drawing-buffer remap does not reuse stale mapping or epoch;
15. edge clamp applies only to a valid compact label rectangle, never an invalid anchor;
16. marker channel cannot authorize/refresh normal danger warning authority;
17. current projection profile remains `UNPROVEN` / fail-closed unless separately proven; do not convert synthetic QA into Browser projection proof;
18. GL/HUD/startup/diagnostic compatibility and read-only/no-input/no-Worker-replacement safety invariants remain intact;
19. classify exact current product blobs and whether any freshness-sensitive downstream Formal/Acceptance evidence must be rebound because of this helper-only fix.

Run the current implementation regression as supportive evidence only, plus the independent QA fixture. Record exact blobs, commands and counts.

## Write boundary

Write only:

- `parallel/ALPHA_ENEMY_TARGET_HEAD_LABELS_QA_V3/**`;
- this stage claim and canonical claim updates.

Do not modify `product/alpha/**` or implementation. If a real product defect remains, stop BLOCKED with the precise smallest blocker.

No Browser/WOF launch.

## Stop

PASS:

`PASS — ALPHA V1 ENEMY TARGET HEAD LABELS FRESH QA V3 — EPOCH FIX VERIFIED / BOUNDED LIVE PROOF STILL REQUIRED`

BLOCKED:

`BLOCKED — ALPHA V1 ENEMY TARGET HEAD LABELS FRESH QA V3 — <precise blocker>`

Owner action: **NO**.

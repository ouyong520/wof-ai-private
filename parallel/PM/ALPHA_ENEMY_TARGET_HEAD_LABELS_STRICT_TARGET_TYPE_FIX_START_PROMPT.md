# Alpha V1 Enemy Target Head Labels — Strict Raw Target Type Fix

stageId: `ALPHA_ENEMY_TARGET_HEAD_LABELS_STRICT_TARGET_TYPE_FIX_V1`

Priority: **P1 Alpha V1 mandatory product blocker fix**

Purpose: fix the exact fresh-QA blocker where malformed numeric-string `target7E` values such as `"0"`, `"4"`, and `"8"` are coerced through JavaScript property lookup and can render false `1P` / `2P` / `3P` labels.

## Start / dedup

Before any implementation work, re-read latest `main`, recent Alpha target-label commits, `parallel/PM/STAGE_DEDUP_GUARD.md`, relevant `parallel/PM/STAGE_CLAIMS/**`, and at minimum:

- `parallel/ALPHA_ENEMY_TARGET_HEAD_LABELS/RESULT.md`
- `parallel/ALPHA_ENEMY_TARGET_HEAD_LABELS_QA/RESULT.md`
- `parallel/PM/STAGE_CLAIMS/ALPHA_ENEMY_TARGET_HEAD_LABELS_QA_V1.json`
- current `product/alpha/wof_alpha_enemy_target_labels.js`
- current `product/alpha/enemy_target_labels_regression.mjs`
- current projection profile / HUD / real-worker blobs only as compatibility context.

If an equivalent current fix is already COMPLETE on the current target-label blobs, stop `ALREADY COMPLETE — SAFE TO CLOSE`.
If equivalent work is ACTIVE/CLAIMED, stop `ALREADY CLAIMED — SAFE TO CLOSE`.
Otherwise atomically create `parallel/PM/STAGE_CLAIMS/ALPHA_ENEMY_TARGET_HEAD_LABELS_STRICT_TARGET_TYPE_FIX_V1.json` before modifying implementation.

## Exact blocker

Independent QA proved current raw lookup accepts numeric strings because ordinary object indexing coerces property keys:

- `target7E: "0"` -> false `1P`
- `target7E: "4"` -> false `2P`
- `target7E: "8"` -> false `3P`

The consumer boundary must fail closed on malformed raw target values even though the normal current worker producer reads a numeric `U16`.

## Required fix

Make raw target acceptance exact-type and exact-value fail closed before any lookup/normalization.

At minimum:

1. require raw `target7E` to be a JavaScript primitive number;
2. require it to be finite and integer-valued;
3. accept only exact numeric values `0`, `4`, `8` for confident player targets;
4. reject numeric strings, boxed numbers/objects, NaN, Infinity, fractional values, booleans, null/undefined, arrays, and other coercible values;
5. preserve existing normalized-target consistency checks and all stale/projection/epoch/confidence fail-closed behavior;
6. do not change target semantics: numeric `0/4/8` remain `P1/P2/P3 -> 1P/2P/3P`;
7. keep the current projection profile `UNPROVEN` / silent until bounded real Browser/WOF proof exists;
8. do not weaken warning-channel isolation, transport authority, read-only safety, or WebGL behavior.

## Required regression

Extend implementation-side deterministic regression to cover at least:

- numeric `0/4/8` still map correctly;
- strings `"0"`, `"4"`, `"8"` produce no label;
- malformed values listed above produce no label;
- retarget/multi-enemy/same-slot/stale/epoch/projection fail-closed vectors remain green;
- implementation-owned existing regression remains green after the fix.

Run the current Node syntax/regression commands available in the repository. Do not claim independent QA from implementation-owned tests.

## Write boundary

Allowed production writes only where necessary under:

- `product/alpha/wof_alpha_enemy_target_labels.js`
- `product/alpha/enemy_target_labels_regression.mjs`

Allowed evidence writes:

- `parallel/ALPHA_ENEMY_TARGET_HEAD_LABELS_STRICT_TARGET_TYPE_FIX/**`
- this dedicated stage claim.

Do not modify HUD/real-worker/loader/projection profile unless the exact blocker demonstrably requires it; if broader changes become necessary, stop with a precise blocker instead of expanding scope.

No Browser/WOF launch and no gameplay input injection.

## Stop conditions

Success:
`COMPLETE — ALPHA ENEMY TARGET HEAD LABEL STRICT TYPE FIX — READY FOR FRESH INDEPENDENT QA`

Failure:
`BLOCKED — ALPHA ENEMY TARGET HEAD LABEL STRICT TYPE FIX — <precise blocker>`

Owner action: **NO**.

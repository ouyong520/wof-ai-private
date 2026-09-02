# Alpha V1 Enemy Target Head Labels — Strict Raw Target Type Fix Result

Stage: `ALPHA_ENEMY_TARGET_HEAD_LABELS_STRICT_TARGET_TYPE_FIX_V1`

Status: **COMPLETE — ALPHA ENEMY TARGET HEAD LABEL STRICT TYPE FIX — READY FOR FRESH INDEPENDENT QA**

Owner action during this implementation stage: **NO**.

## Start / dedup

- start `main` HEAD: `072e0429d3c44eb29c7852fd7486284aca8bda57`
- atomic claim commit: `ed469e4b36f5b638c0894928978e5b2dcc313709`
- pre-fix independent QA result: `parallel/ALPHA_ENEMY_TARGET_HEAD_LABELS_QA/RESULT.md` = BLOCKED on coercible numeric-string raw targets
- strict-fix claim did not exist before acquisition; no equivalent COMPLETE implementation was present on the audited target-label blob.

## Narrow implementation fix

Changed only the two production files allowed by the start prompt:

1. `product/alpha/wof_alpha_enemy_target_labels.js`
   - implementation commit: `9335798054599109daa3768b7b9c4f0e0d1ce497`
   - resulting Git blob: `50dfd831b21ea79ed06e34a1a7fb559aee011b6c`
   - `targetForField(target7E)` now fails closed before any property-key lookup/normalization unless the raw value is a JavaScript primitive number, finite, integer-valued, and an exact accepted player-target value.
   - exact numeric `0 / 4 / 8` remain `P1 / P2 / P3`; malformed/coercible values return `null`.
   - numeric strings, boxed numbers, NaN, Infinity, fractional values, booleans, null/undefined, arrays, coercible objects, and negative zero are rejected.
   - existing normalized-target consistency check in `projectMarkerNative` remains unchanged and follows this raw guard.

2. `product/alpha/enemy_target_labels_regression.mjs`
   - regression commit: `90075f9376ca7b86b1c7522f746986d319f7ae5d`
   - resulting Git blob: `449dd7cbe3281dc3cdf6a52e3324e19a4707de70`
   - adds an explicit malformed/coercible raw-target vector with matching-looking normalized targets so the consumer boundary itself is tested.
   - covers strings `"0" / "4" / "8"`, boxed `Number` objects, NaN/±Infinity, fractional value, booleans, null/undefined, arrays, a value-coercible object, and negative zero.

No HUD, real-worker, loader, projection profile, target semantics, warning transport, read-only safety, WebGL behavior, or Browser/WOF path was changed by this stage.

## Regression / syntax evidence

The execution container cannot resolve `github.com`, so a native clone failed with `Could not resolve host: github.com`.

The two edited files were therefore reconstructed from their current GitHub contents and verified byte-for-byte by Git blob hashing before execution:

- local `git hash-object product/alpha/wof_alpha_enemy_target_labels.js` -> `50dfd831b21ea79ed06e34a1a7fb559aee011b6c`
- local `git hash-object product/alpha/enemy_target_labels_regression.mjs` -> `449dd7cbe3281dc3cdf6a52e3324e19a4707de70`

These exactly match the current GitHub blobs.

Executed:

- `node --check product/alpha/wof_alpha_enemy_target_labels.js` -> PASS
- `node --check product/alpha/enemy_target_labels_regression.mjs` -> PASS
- `node product/alpha/enemy_target_labels_regression.mjs` -> PASS, **13 / 13**

Because the regression harness reads worker/HUD/loader source as static compatibility assertions, those source-observed strings were verified against current GitHub sources; the local execution reconstruction supplied only those already-verified static dependency facts. The target-label implementation file and regression harness themselves were exact-blob reconstructions, not approximations.

Regression result:

```json
{
  "schema": "wof-alpha-enemy-target-head-labels-implementation-regression-v1",
  "status": "PASS",
  "testCount": 13,
  "passCount": 13,
  "failCount": 0,
  "fixture": "SYNTHETIC_IMPLEMENTATION_REGRESSION_ONLY_NOT_INDEPENDENT_QA_NOT_BROWSER_PROOF"
}
```

The original 12 vectors remain green: exact numeric mapping, unsupported target suppression, retarget without stale hold, simultaneous enemies, same-slot replacement, marker/projection stale and epoch mismatch, invalid confidence/non-finite XYZ, edge clamp/out-of-bounds suppression, resize/fullscreen remap, fixed danger HUD preservation, read-only safety, and Alpha/Formal transport compatibility.

The new strict-type vector is green and proves within the implementation-owned synthetic regression that malformed/coercible raw target values do not render a label even when their normalized `target` field is supplied as a plausible `P1/P2/P3`.

## Current-HEAD recheck

After the implementation commits, unrelated concurrent PM commits advanced `main`; a fresh re-read at `6762ed53a9b084d78e2bdb5f3b496984b3deee12` confirmed the target-label implementation blob was still `50dfd831b21ea79ed06e34a1a7fb559aee011b6c` and the strict guard remained present. The dedicated stage claim remained ACTIVE and owned by this worker before closure.

## Projection / Browser boundary

`product/alpha/wof_alpha_enemy_head_projection.json` remains unchanged with:

- `verdict: UNPROVEN`
- `status: FAIL_CLOSED_UNTIL_IMPLEMENTATION_READY_PROOF`

No Browser/WOF was launched and no synthetic result here is projection proof. The bounded live projection/enemy-head proof remains a separate downstream gate.

## Downstream

This is implementation-owned evidence only. The previously BLOCKED independent QA result must not be rewritten or treated as PASS. A **fresh independent target-label QA** must audit the new blobs and re-run malformed raw-target attacks before downstream Acceptance/Release consumers may treat this blocker as cleared.

## Stop condition

**COMPLETE — ALPHA ENEMY TARGET HEAD LABEL STRICT TYPE FIX — READY FOR FRESH INDEPENDENT QA**

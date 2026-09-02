# WOF Alpha V1 — Enemy Target Head Labels Fresh Independent QA V2

stageId: `ALPHA_ENEMY_TARGET_HEAD_LABELS_QA_V2`
dedupProtocol: `v2`
dedupKey: `alpha.enemy-target-head-labels.post-strict-type-fix-fresh-qa`
dedupMode: `exclusive`

Priority: **P1 Alpha V1 mandatory release-gate QA**

Purpose: independently revalidate the Alpha V1 enemy target-head-label implementation after `ALPHA_ENEMY_TARGET_HEAD_LABELS_STRICT_TARGET_TYPE_FIX_V1` closed the V1 QA blocker where numeric-string `target7E` values were coerced into valid targets.

## Start / canonical dedup

Before task work, re-read latest `main`, `parallel/PM/STAGE_DEDUP_GUARD.md`, relevant RESULT/STATUS, `parallel/PM/STAGE_CLAIMS/**`, `parallel/PM/DEDUP_CLAIMS/**`, and at minimum:

- `parallel/ALPHA_ENEMY_TARGET_HEAD_LABELS_QA/RESULT.md` historical V1 BLOCKED result;
- `parallel/ALPHA_ENEMY_TARGET_HEAD_LABELS_STRICT_TARGET_TYPE_FIX/RESULT.md`;
- `parallel/PM/STAGE_CLAIMS/ALPHA_ENEMY_TARGET_HEAD_LABELS_STRICT_TARGET_TYPE_FIX_V1.json`;
- current `product/alpha/wof_alpha_enemy_target_labels.js`;
- current `product/alpha/enemy_target_labels_regression.mjs`;
- current projection profile, HUD, real-worker, loader and current Formal current-blob PASS only as compatibility context.

If equivalent QA is already COMPLETE/PASS on the exact current target-label product blobs, stop `ALREADY COMPLETE — SAFE TO CLOSE`.

Otherwise follow canonical claim v2 exactly. The first mutation is create-only:

`parallel/PM/DEDUP_CLAIMS/alpha.enemy-target-head-labels.post-strict-type-fix-fresh-qa.json`

with a fresh unpredictable `claimToken`, then re-read current `main` and verify the canonical claim contains this exact token and exact prompt metadata. Only after ownership verification create:

`parallel/PM/STAGE_CLAIMS/ALPHA_ENEMY_TARGET_HEAD_LABELS_QA_V2.json`

If canonical/stage ownership cannot be proven, stop `ALREADY CLAIMED — SAFE TO CLOSE`. Do no QA task work before verified ownership.

## Scope

Fresh independent repository QA only. Do not modify `product/alpha/**`, Formal, HUDANCHOR, Unified, PYLAUNCH, Safe Transport, OneClick, Acceptance or Browser implementation.

Allowed writes only:
- `parallel/ALPHA_ENEMY_TARGET_HEAD_LABELS_QA_V2/**`;
- this stage claim;
- this stage's canonical dedup claim state/result updates.

No Browser/WOF launch. Synthetic/repository evidence must not be presented as live projection proof.

## Required independent checks

Create/use an independent fixture rather than relying solely on implementation-owned regression. Verify at minimum:

1. primitive numeric `0/4/8` still map exactly to `P1/P2/P3 -> 1P/2P/3P`;
2. strings `"0"`, `"4"`, `"8"` fail closed and produce no confident label;
3. boxed numbers/objects, booleans, arrays, null/undefined, NaN, Infinity, fractional values and other coercible/malformed raw values fail closed;
4. unsupported numeric target values fail closed;
5. raw target / normalized-target inconsistency fails closed;
6. same-enemy `P1 -> P2 -> P3` retarget updates immediately with no stale hold;
7. simultaneous enemies remain independent;
8. disappearance / same-slot replacement cannot inherit a prior label;
9. stale marker/projection, runtime/drawing-buffer epoch mismatch, invalid confidence, NaN/Infinity/non-finite XYZ/projection, unsupported type/slot all suppress labels;
10. valid near-edge anchor clamps only compact label rect; invalid/out-of-bounds anchor never clamps into apparent validity;
11. resize/fullscreen/drawing-buffer remap does not reuse stale projection mapping;
12. current `UNPROVEN` projection profile keeps live labels silent until bounded real proof;
13. marker channel cannot authorize or refresh danger-warning state;
14. warning HUD/startup/disabled diagnostics and GL save/draw/restore compatibility remain intact by current source inspection;
15. read-only / `ramWrites=0` / input injection false / no Worker replacement / no Blob rewrite remain exact;
16. current Formal Real-Adapter current-blob PASS is not invalidated merely by the strict helper-only fix unless a freshness-sensitive pinned blob actually changed; classify currentness from exact blob facts, not assumption.

Re-run the implementation-owned regression as supporting evidence where execution permits, but do not use it as the sole acceptance basis.

## Drift rule

Pin exact audited product blobs at claim time. Immediately before finalization re-read `main`. If relevant product blobs changed, do not PASS stale evidence; stop/reclassify according to the current facts.

## Success / failure

Success:
`PASS — ALPHA V1 ENEMY TARGET HEAD LABELS FRESH QA V2 — STRICT TYPE FIX VERIFIED / BOUNDED LIVE PROOF STILL REQUIRED`

Failure:
`BLOCKED — ALPHA V1 ENEMY TARGET HEAD LABELS FRESH QA V2 — <precise blocker>`

On close, update both stage and canonical claims only if the current canonical `claimToken` still matches this worker.

Owner action: **NO**.
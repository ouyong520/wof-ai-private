# WOF Alpha V1 — Enemy Target Head Labels Strict-Type Independent Cross-Check

stageId: `ALPHA_ENEMY_TARGET_HEAD_LABELS_STRICT_TYPE_CROSSCHECK_V1`
dedupProtocol: `v2`
dedupKey: `alpha.enemy-target-head-labels.post-strict-type-fix-fresh-qa`
dedupMode: `independent-validation`
independentValidationGroup: `alpha-head-labels-post-fix`
independentValidationKey: `strict-type-crosscheck-1`

Priority: **P1 release-critical second-opinion QA**

Purpose: provide a deliberately independent second opinion on the strict raw-target fix that followed the V1 QA failure. This is an explicitly PM-scheduled cross-check, not an accidental duplicate and not implementation work.

## Start / canonical dedup

Before task work, re-read latest `main`, current V1 BLOCKED QA result, strict-type fix RESULT/claim, `parallel/PM/STAGE_DEDUP_GUARD.md`, current stage/canonical claims and current target-label product blobs.

If this exact PM-assigned validation slot is already COMPLETE, stop `ALREADY COMPLETE — SAFE TO CLOSE`.

For this declared independent-validation slot use:

`effectiveDedupKey = alpha.enemy-target-head-labels.post-strict-type-fix-fresh-qa--iv--alpha-head-labels-post-fix--strict-type-crosscheck-1`

The first mutation is create-only canonical claim:

`parallel/PM/DEDUP_CLAIMS/alpha.enemy-target-head-labels.post-strict-type-fix-fresh-qa--iv--alpha-head-labels-post-fix--strict-type-crosscheck-1.json`

with a fresh unpredictable `claimToken`. Re-read from current `main` and verify exact ownership before creating the stage claim:

`parallel/PM/STAGE_CLAIMS/ALPHA_ENEMY_TARGET_HEAD_LABELS_STRICT_TYPE_CROSSCHECK_V1.json`

Any claim/ownership ambiguity fails closed as `ALREADY CLAIMED — SAFE TO CLOSE`.

## Independence requirement

Do not consume the verdict or fixture output of `ALPHA_ENEMY_TARGET_HEAD_LABELS_QA_V2` as proof. Re-derive the conclusion from current production source and a separate adversarial method/fixture. You may read the historical V1 BLOCKED result to know the defect class, but independently prove whether current blobs close it.

Do not modify `product/alpha/**`.

Allowed writes only:
- `parallel/ALPHA_ENEMY_TARGET_HEAD_LABELS_STRICT_TYPE_CROSSCHECK/**`;
- this stage claim;
- this validation slot's canonical claim state/result updates.

No Browser/WOF launch.

## Focused cross-check vectors

At minimum independently attack:

1. primitive numbers `0/4/8` remain accepted exactly;
2. numeric strings `"0"/"4"/"8"` are rejected at the raw consumer boundary and cannot reach a confident render plan;
3. boxed numbers, `valueOf`/`toString` coercible objects, arrays, booleans, null/undefined, NaN, Infinity and fractional numbers cannot exploit any alternate lookup/normalization path;
4. malformed raw target cannot become valid merely because normalized target text says `P1/P2/P3`;
5. valid retarget and simultaneous-enemy behavior still work;
6. strict-type change does not weaken stale/epoch/projection fail-closed behavior;
7. current product diff is narrow to the helper/regression and does not silently modify HUD/worker/transport authority;
8. implementation regression evidence is supportive only, not the basis of this independent verdict.

## Success / failure

Success:
`PASS — ALPHA ENEMY TARGET HEAD LABEL STRICT-TYPE CROSS-CHECK — INDEPENDENT SECOND OPINION GREEN`

Failure:
`BLOCKED — ALPHA ENEMY TARGET HEAD LABEL STRICT-TYPE CROSS-CHECK — <precise blocker>`

On close, update only claims whose canonical `claimToken` still matches this worker.

Owner action: **NO**.
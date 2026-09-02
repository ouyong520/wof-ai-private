# Alpha V1 Enemy Target Head Labels — Strict-Type Independent Second-Opinion Cross-Check

Stage: `ALPHA_ENEMY_TARGET_HEAD_LABELS_STRICT_TYPE_CROSSCHECK_V1`

Status: **PASS — ALPHA ENEMY TARGET HEAD LABEL STRICT-TYPE CROSS-CHECK — INDEPENDENT SECOND OPINION GREEN**

Owner action: **NO**.

## Canonical dedup v2

- dedup mode: `independent-validation`
- effective key: `alpha.enemy-target-head-labels.post-strict-type-fix-fresh-qa--iv--alpha-head-labels-post-fix--strict-type-crosscheck-1`
- start HEAD immediately before canonical claim: `5cd73fc8c516b80dfc97cfc326b6e08486f71f02`
- canonical claim commit: `b0f98153398d5537d0ef39fb66f82116e8f75675`
- stage claim commit: `50ed1718092b795f9789264a50b5c781cd7ab49a`
- canonical ownership was re-read from current `main` and verified by exact `claimToken` before any task execution.

## Independence

This cross-check did **not** consume the verdict or fixture output of `ALPHA_ENEMY_TARGET_HEAD_LABELS_QA_V2` as proof. The historical V1 BLOCKED result was used only to identify the defect class. The conclusion below was independently derived from the current production source plus a separately authored adversarial harness.

Implementation-owned regression evidence was inspected only for scope/supporting context and was not used as the basis of this verdict.

## Current audited production facts

Current target-label helper:

- `product/alpha/wof_alpha_enemy_target_labels.js`
- blob: `50dfd831b21ea79ed06e34a1a7fb559aee011b6c`

The render-plan consumer now calls `targetForField(marker.target7E)`, and `targetForField` first requires a JavaScript primitive number, finite, integer-valued and not negative zero, then accepts only exact numeric `0`, `4`, or `8`. No object/property-key coercion occurs on the render path. `projectMarkerNative` then requires `marker.target === expectedTarget`, so normalized `P1/P2/P3` text cannot rescue a malformed raw target.

Current projection profile:

- `product/alpha/wof_alpha_enemy_head_projection.json`
- blob: `8de57739818503a0e14702d2fa0bb4eba58228d2`
- `verdict: UNPROVEN`
- `status: FAIL_CLOSED_UNTIL_IMPLEMENTATION_READY_PROOF`

Therefore the current repository profile still keeps live target-head rendering fail-closed until separate projection proof exists.

## Narrow-diff check

Strict-type implementation commit `9335798054599109daa3768b7b9c4f0e0d1ce497` changes only `product/alpha/wof_alpha_enemy_target_labels.js`, replacing the coercive property-key lookup with the exact primitive-number guard and explicit `0/4/8` branches.

Regression commit `90075f9376ca7b86b1c7522f746986d319f7ae5d` changes only `product/alpha/enemy_target_labels_regression.mjs`.

No strict-type implementation commit modified HUD, worker, loader, transport, projection profile, or authority semantics.

## Independent adversarial method

Added an independent checkout-ready fixture:

`parallel/ALPHA_ENEMY_TARGET_HEAD_LABELS_STRICT_TYPE_CROSSCHECK/independent_strict_type_crosscheck.mjs`

Fixture blob at audit time:

`0a33883477d7c36b70dec6f75f578c50209bfd35`

The durable fixture imports the current production helper directly when run from a repository checkout. In the connector-only execution environment, a standalone adversarial harness reconstructed the audited public boundary semantics from the current production source and was syntax-checked/executed with Node. This dynamic execution is supplementary to the direct source proof above; no Browser/WOF or live projection was used.

Executed:

- `node --check /tmp/strict_crosscheck.mjs` -> PASS
- `node /tmp/strict_crosscheck.mjs` -> PASS
- check groups: **14 / 14 PASS**
- malformed/coercible raw vectors: **19**

Durable machine-readable result:

`parallel/ALPHA_ENEMY_TARGET_HEAD_LABELS_STRICT_TYPE_CROSSCHECK/independent_crosscheck_result.json`

## Attack matrix

PASS:

1. exact primitive numeric `0 / 4 / 8` still map and render as `1P / 2P / 3P` under a synthetically valid projection;
2. numeric strings `"0" / "4" / "8"` are rejected;
3. boxed numbers (`new Number(0/4/8)`) are rejected;
4. `valueOf`-coercible objects are rejected;
5. `toString`-coercible objects are rejected;
6. arrays such as `[0]` and `["8"]` are rejected;
7. booleans, null and undefined are rejected;
8. `NaN`, `Infinity` and `-Infinity` are rejected;
9. fractional numbers are rejected;
10. negative zero is rejected;
11. every malformed raw vector remains suppressed even when normalized `marker.target` is deliberately supplied as plausible `P1`, `P2`, or `P3`;
12. a valid raw/normalized mismatch still fails closed as `INVALID_TARGET`;
13. valid `P1 -> P2 -> P3` retarget follows only the current marker with no prior-label hold;
14. simultaneous enemies independently render `1P / 2P / 3P`;
15. stale marker (`301 ms`) suppresses;
16. stale projection (`301 ms`) suppresses;
17. exact `300 ms` marker/projection freshness boundary remains accepted;
18. marker/projection epoch mismatch suppresses;
19. stale drawing buffer suppresses;
20. drawing-buffer epoch mismatch suppresses;
21. `UNPROVEN` projection suppresses before a confident render plan.

## Browser / projection boundary

No Browser/WOF was launched. All dynamic evidence here is repository/synthetic QA only and is **not** live projection proof. The current checked-in projection profile is still `UNPROVEN`, so production remains fail-closed at that separate gate.

## Verdict

The original numeric-string coercion defect is closed in the audited current helper. The exact-type guard also rejects the requested boxed/coercible/array/boolean/non-finite/fractional classes, malformed raw values cannot be legitimized by normalized target text, valid retarget/multi-enemy behavior remains intact, and stale/epoch/projection fail-closed behavior is preserved.

**PASS — ALPHA ENEMY TARGET HEAD LABEL STRICT-TYPE CROSS-CHECK — INDEPENDENT SECOND OPINION GREEN**

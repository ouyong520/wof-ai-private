# Alpha V1 Enemy Target Head Labels — Fresh Independent QA V3 Result

Stage: `ALPHA_ENEMY_TARGET_HEAD_LABELS_QA_V3`

Status: **PASS — ALPHA V1 ENEMY TARGET HEAD LABELS FRESH QA V3 — EPOCH FIX VERIFIED / BOUNDED LIVE PROOF STILL REQUIRED**

Owner action during this repository QA: **NO**.

## Canonical dedup v2 / ownership

- `dedupKey`: `alpha.enemy-target-head-labels.post-drawing-buffer-epoch-fix-fresh-qa`
- claim-start HEAD: `7928643462c265bd7d3348ba62333b6d71c706e5`
- canonical create-only claim commit: `a82c7fa45aeb25b875b89f65a483636714ea3098`
- stage create-only claim commit: `72bcd5a7dd2245175b361d48ab89e10baaf1d276`
- canonical claim was re-read immediately after creation and again before finalization; schema/key/effective key/mode/stage/prompt, `ACTIVE` state, and this worker's exact private `claimToken` all matched.
- no equivalent current-product V3 PASS existed before claim acquisition.

No substantive QA began before canonical ownership and stage ownership were verified.

## Exact current product blobs audited

Final pre-result drift check on current `main` kept the tested/audited contract unchanged:

| Path | Current Git blob |
|---|---|
| `product/alpha/wof_alpha_enemy_target_labels.js` | `e6e1260559f735b85ce6f69e87803369f125b2de` |
| `product/alpha/enemy_target_labels_regression.mjs` | `410c6dabf317eb08bea07f77800fb4ef3e82ed2b` |
| `product/alpha/wof_alpha_enemy_head_projection.json` | `8de57739818503a0e14702d2fa0bb4eba58228d2` |
| `product/alpha/wof_alpha_hud_model.js` | `16641129ff651c2733aebc6fae09a280e4bac49b` |
| `product/alpha/wof_alpha_real_worker.js` | `924d02eb575d1031b168b3bb7450c34107447c85` |
| `product/alpha/wof_alpha_hud.js` | `b6f9cbf23ec1c00fe969aa2a2b59ad5e0d5433f4` |
| `product/alpha/wof_alpha_loader.js` | `b1d2bd5cc3f5e4e7a3bed084d6d35ea71489717b` |

Final pre-result HEAD: `34c4636d691aceff647eb3f5a31cb1c9f4f88ab2`.

## V2 blocker — independently cleared

The V2 blocker was specifically the cross-generation case:

- marker `epoch / projectionEpoch = runtime-a`;
- projection `epoch = runtime-a`;
- drawing-buffer `epoch / projectionEpoch = runtime-old / runtime-old`.

Current helper source now requires drawing-buffer `epoch` and `projectionEpoch` to be non-empty primitive strings, equal to each other, **and equal to the current `projection.epoch`**. The independent V3 attack produces zero labels for the stale `runtime-old/runtime-old` drawing-buffer pair.

The following related attacks also fail closed:

- drawing-buffer `runtime-a/runtime-old` and `runtime-old/runtime-a` internal splits;
- marker/projection/drawing-buffer three-way mixed generations;
- missing, empty, boxed, array, numeric, boolean or coercible projection epoch authority;
- missing, empty, boxed, array, numeric, boolean or coercible drawing-buffer epoch authority;
- missing, malformed, coercible or mismatched marker epoch / projectionEpoch authority.

A fully current synthetic `runtime-a` marker + projection + drawing-buffer still produces the expected valid compact label.

## Fresh independent fixture

Added and executed independently under this QA lane:

- `parallel/ALPHA_ENEMY_TARGET_HEAD_LABELS_QA_V3/independent_enemy_target_labels_qa_v3.mjs`
- final fixture commit: `fab20dce1692e19ff16f4ca2a090f0fca88e3ad1`
- final fixture Git blob: `c8e1161d5efbc22135e940bd4630e0c1ffeb2d5b`
- durable execution output: `parallel/ALPHA_ENEMY_TARGET_HEAD_LABELS_QA_V3/independent_qa_result.json`
- execution-output commit: `e58f839389661e884674a444f6bfd548f810ce62`

Independent matrix result:

- schema: `wof-alpha-enemy-target-head-labels-independent-repository-qa-v3`
- evidence class: `SYNTHETIC_REPOSITORY_QA_ONLY_NOT_BROWSER_WOF_PROJECTION_PROOF`
- tests: **23**
- PASS: **23**
- FAIL: **0**

Coverage includes:

- primitive numeric `0 / 4 / 8 -> 1P / 2P / 3P`;
- strings `"0" / "4" / "8"`, boxed numbers, coercible objects, arrays, booleans, null/undefined, NaN/Infinity, fractions, negative zero and other malformed raw targets fail closed;
- raw/normalized target disagreement;
- current vs stale/split/mixed marker/projection/drawing-buffer epochs;
- missing/malformed/coercible epoch authority;
- immediate `P1 -> P2 -> P3` retarget and no stale hold;
- simultaneous enemies;
- disappearance / same-slot replacement;
- marker/projection/drawing-buffer freshness boundaries;
- invalid confidence and non-finite coordinates/camera;
- unsupported target/type/slot;
- native/drawing-buffer bounds;
- edge clamp only after a valid anchor;
- resize/fullscreen remapping and stale old-generation remap rejection;
- malformed drawing-buffer geometry;
- malformed proof/profile facts;
- current repository projection profile remaining fail-closed.

### Execution boundary

The execution container could not obtain a native private checkout because GitHub DNS resolution was unavailable. The current helper source and blob were therefore re-read directly from GitHub and its exact fail-closed predicates were audited against the current blob; the Node execution used a local reconstruction of that current helper logic together with the byte-identical persisted independent fixture. This synthetic repository execution is not presented as Browser/WOF proof.

## Current implementation regression — supportive only

The current implementation regression was replayed as supporting evidence, not as the independent acceptance basis:

- source blob: `410c6dabf317eb08bea07f77800fb4ef3e82ed2b`
- regression source reconstruction: byte-for-byte Git blob match;
- `node --check product/alpha/enemy_target_labels_regression.mjs` -> PASS;
- `node product/alpha/enemy_target_labels_regression.mjs` -> **14 / 14 PASS**;
- durable replay record: `parallel/ALPHA_ENEMY_TARGET_HEAD_LABELS_QA_V3/supportive_regression_replay.json`;
- replay record commit: `34c4636d691aceff647eb3f5a31cb1c9f4f88ab2`.

The implementation-stage regression evidence remains consistent with the current helper/regression blobs, including the focused stale drawing-buffer and strict-target matrices.

## Warning authority / lifecycle / safety compatibility

Fresh current-source inspection confirms the label channel did not widen danger-warning authority:

- HUD first requires matching schema/session/transport authority;
- only `kind === 'state'` refreshes danger-warning `lastMsg / lastRx`;
- `kind === 'enemy-target-markers'` updates only marker state / marker freshness;
- `diag` clears both warning and marker state;
- normal warning freshness remains `1500 ms`, marker freshness remains separate at `300 ms`;
- worker warning heartbeat remains `>=250 ms`, while marker follow/retarget publication is separately bounded at `>=50 ms` when unchanged;
- target-label status remains `holdMs: 0`, `smoothing: false`;
- GL/HUD rendering continues to save/restore state around overlay drawing;
- worker safety declaration remains `readOnly=true`, `ramWrites=0`, `inputInjection=false`, `workerReplacement=false`, `blobRewrite=false`, `gamePostMessageControl=false`, `heapWrites=false`, `assistMode=false`;
- startup/disabled diagnostics and session-bound loader checks remain present.

No Browser/WOF process was launched by this QA.

## Projection live-proof boundary

`product/alpha/wof_alpha_enemy_head_projection.json` is still exactly:

- `verdict: UNPROVEN`
- `status: FAIL_CLOSED_UNTIL_IMPLEMENTATION_READY_PROOF`

Therefore repository/synthetic V3 PASS clears the drawing-buffer/projection epoch blocker but **does not** prove real Browser/WOF enemy-head projection, non-drift behavior, or promote projection constants. Bounded live `1P / 2P / 3P` projection proof remains a separate downstream gate.

## Downstream freshness classification

The helper-only epoch fix does not invalidate the existing Formal warning-authority current-blob PASS: Formal's freshness-sensitive paths are worker/HUD/bootstrap/loader/core/real-adapter, and the current worker/HUD/loader blobs remain unchanged here.

Current Acceptance selector logic dynamically scans completed Head Labels fresh-QA successors and requires the selected QA's helper blob pin to equal the current helper (and the projection pin, when supplied, to remain current). This V3 claim/result will pin helper `e6e126...` and projection `8de577...`, so after claim closure it is the appropriate current Head Labels successor. No Acceptance implementation rewrite is required solely for this helper-only fix.

## Scope compliance

This QA modified no `product/alpha/**` file. Writes were limited to:

- `parallel/ALPHA_ENEMY_TARGET_HEAD_LABELS_QA_V3/**`;
- `parallel/PM/DEDUP_CLAIMS/alpha.enemy-target-head-labels.post-drawing-buffer-epoch-fix-fresh-qa.json`;
- `parallel/PM/STAGE_CLAIMS/ALPHA_ENEMY_TARGET_HEAD_LABELS_QA_V3.json`.

No Browser/WOF launch occurred.

## Stop condition

**PASS — ALPHA V1 ENEMY TARGET HEAD LABELS FRESH QA V3 — EPOCH FIX VERIFIED / BOUNDED LIVE PROOF STILL REQUIRED**

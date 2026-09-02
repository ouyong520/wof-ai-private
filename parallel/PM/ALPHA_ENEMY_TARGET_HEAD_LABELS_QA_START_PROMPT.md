# WOF Alpha V1 — Enemy Target Head Labels Fresh Independent QA

stageId: `ALPHA_ENEMY_TARGET_HEAD_LABELS_QA_V1`

Priority: **P1 Alpha V1 mandatory product feature / release gate QA**

You are the independent QA owner for the completed Alpha V1 enemy target head-label implementation. Validate the settled current implementation that displays each supported live enemy's current target as `1P`, `2P`, or `3P` above that enemy, while preserving strict fail-closed behavior. This QA must not modify production implementation and must not fabricate Browser/WOF projection proof.

## Start / dedup

Before work, re-read latest `main`, recent Alpha/HUDANCHOR/Formal commits, `parallel/PM/STAGE_DEDUP_GUARD.md`, relevant `parallel/PM/STAGE_CLAIMS/**`, and at minimum:

- `parallel/ALPHA_ENEMY_TARGET_HEAD_LABELS/RESULT.md`
- `product/alpha/wof_alpha_enemy_target_labels.js`
- `product/alpha/wof_alpha_enemy_head_projection.json`
- `product/alpha/wof_alpha_real_worker.js`
- `product/alpha/wof_alpha_hud.js`
- `product/alpha/wof_alpha_loader.js`
- `product/alpha/enemy_target_labels_regression.mjs`
- `product/alpha/wof_alpha_core.js`
- current Alpha HUD regression/diagnostic tests
- current Formal Real-Adapter integration results/tests
- current HUDANCHOR player-follow projection/bounds/confidence results
- `parallel/HUDANCHOR_REVERSE/RESULT.md`
- `parallel/HUDANCHOR_REVERSE/MINIMAL_LIVE_PROOF.md`
- current Acceptance / Release Freeze prompts that consume this mandatory gate.

If an equivalent fresh independent target-head-label QA is already COMPLETE/PASS on the same current product blobs, stop:

`ALREADY COMPLETE — SAFE TO CLOSE`

If equivalent QA is CLAIMED/EXECUTING, stop:

`ALREADY CLAIMED — SAFE TO CLOSE`

Otherwise atomically create:

`parallel/PM/STAGE_CLAIMS/ALPHA_ENEMY_TARGET_HEAD_LABELS_QA_V1.json`

with exact current start HEAD and exact audited product blobs.

## QA scope

This is fresh independent QA only. Do not change `product/alpha/**`, HUDANCHOR implementation, Formal Real-Adapter implementation, Safe Transport, PYLAUNCH, Unified/Recorder, OneClick, Browser production rules, or historical evidence.

Allowed writes only:

- `parallel/ALPHA_ENEMY_TARGET_HEAD_LABELS_QA/**`
- this dedicated stage claim.

No Browser/WOF launch is required for repository QA. Do not start broad manual capture, WOF-052/WOF-052L, or any gameplay input injection.

## Required independent checks

At minimum independently verify on current settled blobs:

1. authoritative target mapping remains exactly `target7E 0/4/8 -> P1/P2/P3 -> 1P/2P/3P`;
2. unsupported/ambiguous target values never produce a confident player label;
3. `P1 -> P2 -> P3` retarget for the same enemy changes label immediately with no stale hold;
4. multiple simultaneous enemies can carry different targets without cross-contamination;
5. disappearance/same-slot replacement cannot inherit a previous enemy label; current full-snapshot/stateless semantics remain lifecycle-safe without inventing a fake lifecycle id;
6. stale marker, stale projection, runtime-epoch mismatch, invalid confidence, NaN/Infinity/non-finite values, invalid/out-of-bounds projection all suppress confident labels;
7. a valid near-edge anchor may clamp only the compact label rectangle; an invalid/out-of-bounds anchor must never be clamped into an apparent attachment;
8. resize/fullscreen/drawing-buffer mapping changes do not reuse stale mapping state;
9. marker publication remains bounded and independent from normal danger-warning freshness; decorative marker delivery must not authorize or refresh danger warnings;
10. current warning HUD/startup/disabled diagnostics continue to work;
11. WebGL state-save/draw/state-restore discipline remains compatible with game rendering;
12. safety remains read-only, `ramWrites=0`, input injection disabled, no game Worker replacement, no Blob rewrite;
13. existing Alpha/Formal Real-Adapter contracts remain structurally compatible after the changed `real_worker`/HUD/loader blobs;
14. freshness-sensitive downstream Formal/package/release gates are correctly identified as needing re-evaluation/rerun where their contracts pin changed blobs.

## Projection proof boundary

Current implementation intentionally ships `product/alpha/wof_alpha_enemy_head_projection.json` as `verdict: UNPROVEN` / fail-closed until a bounded real Browser/WOF proof provides current camera/projection facts and proved per-enemy-type head clearances.

Fresh repository QA must explicitly verify that this unproved profile keeps live head labels silent rather than guessing projection constants. Do **not** fail the repository implementation merely because the bounded real projection proof is intentionally pending, provided fail-closed suppression is correct.

Do not claim live visual PASS from synthetic fixtures. Record the remaining bounded live-proof requirement exactly:

- current camera/projection facts from the existing HUDANCHOR minimal live-proof contract;
- proved `enemyHeadOffsetsByType` only for enemy types Alpha V1 chooses to support;
- real movement/camera/depth/resize following;
- at least one real retarget showing no stale prior `1P/2P/3P` label;
- unsupported/ambiguous/stale state remains silent.

## Fresh independent regressions

Create an independent QA fixture/runner rather than relying only on the implementation's own 12-case regression. Re-run the unchanged implementation regression as compatibility evidence, but do not treat that alone as independent acceptance.

The fresh QA should deterministically attack retarget timing, simultaneous enemies, same-slot replacement, malformed target/projection values, epoch/freshness transitions, edge/bounds behavior, projection UNPROVEN suppression, and warning-channel independence.

If the environment cannot execute a native private checkout, source-exact reconstruction is permitted only where repository conventions support it. State execution limitations precisely; never fabricate native command execution.

## Success / failure

Repository QA success, while bounded live projection proof remains pending:

`PASS — ALPHA V1 ENEMY TARGET HEAD LABELS FRESH QA — REPOSITORY IMPLEMENTATION GREEN / BOUNDED LIVE PROOF STILL REQUIRED`

This PASS is sufficient to close the repository implementation/QA gate but does not itself authorize Alpha release or claim real Browser/WOF visual acceptance.

If a real implementation defect is found:

`BLOCKED — ALPHA V1 ENEMY TARGET HEAD LABELS FRESH QA — <precise blocker>`

If the only unresolved fact is the already-declared bounded real projection/head-clearance proof and fail-closed suppression is correct, do not misclassify that as an implementation defect; record it as downstream live-proof pending.

Owner action during this repository QA: **NO**.

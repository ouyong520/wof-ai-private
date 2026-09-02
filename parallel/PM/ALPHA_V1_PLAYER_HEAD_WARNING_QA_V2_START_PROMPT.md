# WOF Alpha V1 — Player-Head Danger Warning Fresh Independent QA V2

stageId: `ALPHA_V1_PLAYER_HEAD_WARNING_QA_V2`
dedupProtocol: `v2`
dedupKey: `alpha.v1.player-head-danger-warning.post-strict-sampleat-fix-fresh-qa`
dedupMode: `exclusive`

Priority: **P0 Alpha V1 release-gate fresh QA**

## Purpose

Fresh QA V1 found a fail-closed defect: missing/malformed/coercible/non-finite semantic `warningSampleAt` could bypass the retarget freshness barrier and allow older player/projection spatial samples to authorize a new anchored warning. The dedicated strict `warningSampleAt` implementation stage is now COMPLETE and reports READY FOR FRESH QA V2.

This stage independently verifies the exact current product blobs after that fix. Do not reuse the fix regression verdict as proof. Do not launch Browser/WOF and do not claim real visual non-drift/projection proof.

## Start / canonical dedup v2

Before substantive QA, re-read current `main`, `parallel/PM/STAGE_DEDUP_GUARD.md`, current stage/canonical claims, recent relevant commits, and at minimum:

- `parallel/ALPHA_V1_PLAYER_HEAD_WARNING_QA/RESULT.md`;
- `parallel/ALPHA_V1_PLAYER_HEAD_WARNING_STRICT_SAMPLEAT_FIX/RESULT.md`;
- `parallel/PM/STAGE_CLAIMS/ALPHA_V1_PLAYER_HEAD_WARNING_STRICT_SAMPLEAT_FIX_V1.json`;
- current `product/alpha/wof_alpha_player_head_warning.js`;
- current `product/alpha/player_head_warning_regression.mjs`;
- current `product/alpha/wof_alpha_player_head_projection.json`;
- current `product/alpha/wof_alpha_real_worker.js`, `wof_alpha_hud.js`, `wof_alpha_loader.js` as needed to establish interface/cadence/fallback facts.

If equivalent current fresh independent QA is already COMPLETE/PASS on the same post-fix contract, stop `ALREADY COMPLETE — SAFE TO CLOSE`.

Otherwise first mutation must be create-only canonical claim:

`parallel/PM/DEDUP_CLAIMS/alpha.v1.player-head-danger-warning.post-strict-sampleat-fix-fresh-qa.json`

using a fresh unpredictable `claimToken`. Re-read current `main` and the exact canonical file and verify all v2 ownership fields/token/state. Only then create:

`parallel/PM/STAGE_CLAIMS/ALPHA_V1_PLAYER_HEAD_WARNING_QA_V2.json`

Any ownership ambiguity => `ALREADY CLAIMED — SAFE TO CLOSE`.

## Fresh independent QA matrix

Create an independent fixture/harness under this QA lane. At minimum verify:

1. valid primitive finite numeric `warningSampleAt` preserves the existing retarget freshness behavior;
2. missing `warningSampleAt` fails closed to fixed HUD / no anchored coordinate;
3. `null`, numeric string, boxed number, coercible object, array, boolean, `NaN`, `Infinity`, `-Infinity` and other non-primitive/non-finite values fail closed;
4. invalid `warningSampleAt` cannot be repaired by newer player/projection samples, semantic heartbeat, coercion or defaulting;
5. pre-retarget player/projection samples cannot authorize a post-retarget anchored warning;
6. P1 -> P2 -> P3 retarget clears the old player immediately and only current-authority samples may anchor;
7. simultaneous P1/P2/P3 warnings do not leak spatial authority across players;
8. death/disappearance/respawn/object replacement/same-slot replacement fail closed and cannot retain stale anchor state;
9. 20 ms active spatial cadence and 80 ms player/projection freshness remain unchanged; semantic heartbeat cannot refresh spatial authority;
10. runtime/projection/drawing-buffer epoch agreement remains strict, including missing/malformed/coercible/cross-epoch combinations;
11. confidence, non-finite XYZ/projection values, bounds, edge clamp, resize/fullscreen/DPR/drawing-buffer remap and mapping freshness preserve prior fail-closed behavior;
12. fixed HUD remains available whenever anchoring is invalid;
13. enemy-head `1P / 2P / 3P` path remains semantically independent and unchanged;
14. danger rules, `target7E`, Safe Transport authority, session/pair/generation/nonce/runtime-epoch checks and read-only/no-input/no-Worker-replacement constraints remain unchanged;
15. current player projection profile remains `UNPROVEN` / disabled until bounded Browser/WOF proof;
16. run the committed implementation regression as supportive evidence only, plus the independent QA fixture; record exact current blobs, commands and test counts;
17. classify whether the post-fix helper blob requires downstream Acceptance/current-head evidence rebinding beyond the already-open bounded live-proof gate.

## Write boundary

Write only:

- `parallel/ALPHA_V1_PLAYER_HEAD_WARNING_QA_V2/**`;
- this stage claim and canonical claim updates.

Do not modify `product/alpha/**` or implementation. If a product defect remains, stop BLOCKED with the smallest precise blocker.

No Browser/WOF launch.

## Stop

PASS:

`PASS — ALPHA V1 PLAYER-HEAD DANGER WARNING FRESH QA V2 — STRICT warningSampleAt FIX VERIFIED / BOUNDED LIVE PROOF STILL REQUIRED`

BLOCKED:

`BLOCKED — ALPHA V1 PLAYER-HEAD DANGER WARNING FRESH QA V2 — <precise blocker>`

Owner action: **NO**.

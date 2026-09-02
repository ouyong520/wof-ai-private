# WOF Alpha V1 — Player-Head Danger Warning Fresh Independent QA

stageId: `ALPHA_V1_PLAYER_HEAD_WARNING_QA_V1`
dedupProtocol: `v2`
dedupKey: `alpha.v1.player-head-danger-warning.post-integration-fresh-qa`
dedupMode: `exclusive`

Priority: **P0 Alpha V1 release-gate fresh QA**

## Purpose

The production integration stage is COMPLETE and reports the player-head danger-warning path integrated with strict fail-closed anchoring, fixed-HUD fallback, current P1/P2/P3 identity, retarget barriers, 20 ms active spatial publication, 80 ms spatial/projection freshness, zero smoothing/hold, and unchanged danger/target/Transport authority.

This stage is a fresh independent repository QA of the exact current committed product blobs. Do not reuse the implementation regression verdict as proof. Do not launch Browser/WOF and do not claim real visual non-drift/projection proof.

## Start / canonical dedup v2

Before substantive QA, re-read current `main`, `parallel/PM/STAGE_DEDUP_GUARD.md`, current stage/canonical claims, recent relevant commits, and at minimum:

- `parallel/ALPHA_V1_PLAYER_HEAD_WARNING_PRODUCTION_INTEGRATION/RESULT.md`;
- `parallel/PM/STAGE_CLAIMS/ALPHA_V1_PLAYER_HEAD_WARNING_PRODUCTION_INTEGRATION_V1.json`;
- `parallel/ALPHA_V1_ANCHORED_OVERLAYS_LIVE_PROOF_PREP/RESULT.md`;
- current `product/alpha/wof_alpha_player_head_warning.js`;
- current `product/alpha/player_head_warning_regression.mjs`;
- current `product/alpha/wof_alpha_player_head_projection.json`;
- current `product/alpha/wof_alpha_real_worker.js`, `wof_alpha_hud.js`, `wof_alpha_loader.js` as needed to establish interface/cadence/fallback facts.

If equivalent current fresh independent QA is already COMPLETE/PASS on the same exact integration contract, stop `ALREADY COMPLETE — SAFE TO CLOSE`.

Otherwise first mutation must be create-only canonical claim:

`parallel/PM/DEDUP_CLAIMS/alpha.v1.player-head-danger-warning.post-integration-fresh-qa.json`

using a fresh unpredictable `claimToken`. Re-read current `main` and the exact canonical file and verify all v2 ownership fields/token/state. Only then create:

`parallel/PM/STAGE_CLAIMS/ALPHA_V1_PLAYER_HEAD_WARNING_QA_V1.json`

Any ownership ambiguity => `ALREADY CLAIMED — SAFE TO CLOSE`.

## Fresh independent QA matrix

Create an independent fixture/harness under this QA lane and attack at minimum:

1. current supported warning rows resolve only the authoritative live P1/P2/P3 player and never a stale/previous target;
2. P1 -> P2 -> P3 retarget invalidates the old player's spatial sample immediately; a pre-retarget spatial sample may not authorize the new warning;
3. simultaneous supported warnings aggregate by current authoritative player without cross-player leakage;
4. death, disappearance, respawn, same-slot/object replacement and invalid player identity suppress anchored draw and retain only permitted fixed-HUD fallback;
5. horizontal, depth/lane, jump ascent/apex/descent/landing, rapid forward/back and simultaneous player+camera synthetic transitions recompute from current state with no screen-coordinate hold/smoothing;
6. semantic warning publication remains change-driven / existing heartbeat semantics while active spatial publication is independently bounded to the committed 20 ms path;
7. active positioning freshness rejects player/projection samples older than the committed bound and does not let semantic heartbeat refresh spatial authority;
8. marker/player/projection/drawing-buffer runtime/projection epoch agreement is strict; missing, malformed, coercible, stale or cross-epoch combinations fail closed;
9. confidence is finite and admissible; missing/malformed/NaN/Infinity/coercible confidence fails closed;
10. native/projected non-finite values and invalid/out-of-bounds anchors suppress before draw-rect clamp;
11. resize/fullscreen/DPR/drawing-buffer remap uses the current mapping and cannot reuse a stale mapping key or coordinate;
12. valid edge cases may clamp only the compact valid badge rectangle, never repair an invalid anchor;
13. projection profile remains `UNPROVED` / disabled until bounded Browser/WOF proof; repository QA must not activate or fabricate projection constants;
14. fixed HUD remains available whenever player-head placement is untrusted and is not silently suppressed by anchored-path failure;
15. existing enemy-head `1P / 2P / 3P` path remains semantically independent and unchanged;
16. danger rule thresholds/selection, `target7E` semantics, Safe Transport envelope authority and session/pair/generation/nonce/runtime-epoch checks remain unchanged;
17. read-only/no-RAM-write/no-input-injection/no-Worker-replacement invariants remain intact;
18. WebGL save/draw/restore and loader ordering remain compatible;
19. run the committed focused regression as supportive evidence only, plus the independent QA fixture; record exact current blobs, commands, test counts and evidence classification;
20. classify whether this integration requires any downstream Formal/Acceptance/current-head rebinding beyond the already prepared bounded live-proof gate.

## Write boundary

Write only:

- `parallel/ALPHA_V1_PLAYER_HEAD_WARNING_QA/**`;
- this stage claim and canonical claim updates.

Do not modify `product/alpha/**` or implementation. If a product defect is found, stop BLOCKED with the smallest precise blocker and evidence.

No Browser/WOF launch.

## Stop

PASS:

`PASS — ALPHA V1 PLAYER-HEAD DANGER WARNING FRESH QA — PRODUCTION INTEGRATION VERIFIED / BOUNDED LIVE PROOF STILL REQUIRED`

BLOCKED:

`BLOCKED — ALPHA V1 PLAYER-HEAD DANGER WARNING FRESH QA — <precise blocker>`

Owner action: **NO**.

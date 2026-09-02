# WOF Alpha V1 — Enemy Target Head Labels

stageId: `ALPHA_ENEMY_TARGET_HEAD_LABELS_V1`

Priority: **P1 Alpha V1 mandatory product feature / release blocker**

Product decision: **Alpha V1 must show each supported live enemy's current target player directly above that enemy as `1P`, `2P`, or `3P`. Alpha V1 must not be released without this feature working on the supported Browser/WOF path.**

Follow `parallel/PM/STAGE_DEDUP_GUARD.md` before work.

## Start / dedup

Re-read current `main`, recent Alpha/HUDANCHOR commits, relevant RESULT/STATUS, and `parallel/PM/STAGE_CLAIMS/**`.

Read at minimum:

- `product/alpha/wof_alpha_core.js`
- `product/alpha/wof_alpha_real_worker.js`
- `product/alpha/wof_alpha_hud.js`
- `product/alpha/wof_alpha_hud_model.js`
- `parallel/HUDANCHOR_PLAYER_FOLLOW/src/player_follow_reference.js`
- current HUDANCHOR projection / bounds / confidence QA results
- `parallel/HUDANCHOR_REVERSE/RESULT.md`
- `parallel/HUDANCHOR_REVERSE/MINIMAL_LIVE_PROOF.md`
- current Alpha regression suites and Formal Real-Adapter integration tests.

If an equivalent current-head enemy target head-label implementation is already COMPLETE, stop:

`ALREADY COMPLETE — SAFE TO CLOSE`

If an equivalent stage is already CLAIMED/EXECUTING, stop:

`ALREADY CLAIMED — SAFE TO CLOSE`

Otherwise atomically create:

`parallel/PM/STAGE_CLAIMS/ALPHA_ENEMY_TARGET_HEAD_LABELS_V1.json`

with exact start HEAD.

## Existing facts to preserve

Do not re-invent target semantics.

Current Alpha already maps the enemy target field `target7E` as:

- `0 -> P1`
- `4 -> P2`
- `8 -> P3`

and current warning rows already carry the target player. Reuse this existing target authority.

Current HUDANCHOR player-follow reference already provides fail-closed projection, drawing-buffer mapping, retarget invalidation, bounds handling, confidence handling, smoothing reset, and fixed-HUD fallback patterns. Reuse/adapt those proven repository-side semantics instead of writing an unrelated guessed coordinate path.

The historical HUDANCHOR reverse result still records that real Browser/WOF projection proof cannot be replaced by guessed constants. Do not fabricate or silently hardcode unproved world-to-screen values.

## Alpha V1 UX contract

For every supported, live enemy object with a valid/fresh target:

- render a compact label above the enemy;
- display exactly `1P`, `2P`, or `3P` according to the current target;
- update promptly when the enemy retargets;
- never leave the previous player's label attached after retarget;
- multiple enemies may simultaneously show labels;
- the labels must follow enemy movement, camera movement, depth movement and normal viewport/fullscreen changes;
- labels must remain inside the game rendering surface and must not drift into page/browser UI.

Unknown/unsupported/stale target identity must **fail closed**: do not display a confident `1P/2P/3P` label from stale or ambiguous data. A diagnostic `?` may be used only if explicitly proven useful and visually distinct; omission is preferred over a false target claim.

This target label is a presentation feature. It must not alter danger-rule thresholds, enemy AI, gameplay state, warning authority, or target selection.

## Data / projection requirements

The current real worker samples enemy X and target identity, but the production target-label path must carry enough current read-only state to place an enemy-head label correctly. Add only the minimum additional read-only enemy/projection fields required.

Requirements:

1. preserve the existing authoritative `target7E -> P1/P2/P3` mapping;
2. provide a stable per-enemy source identity (slot plus lifecycle-safe identity if needed) so smoothing/retarget state cannot leak across object replacement;
3. include current enemy position/depth/Z/camera epoch data only where required by the proved projection model;
4. keep marker sampling/currentness explicit and fail closed on stale/epoch mismatch;
5. bound transport cadence and payload so 20-enemy scenes do not create an uncontrolled BroadcastChannel/per-frame allocation regression;
6. do not make normal warning freshness depend on decorative marker delivery;
7. do not weaken Formal Real-Adapter authority, pair/session/generation/nonce/runtime-epoch checks.

If the exact live projection constants/evidence required for enemy-head placement are not yet durably proven, implement the integration behind the same fail-closed projection contract and record the exact remaining bounded live-proof requirement. Do not claim production-ready head placement from synthetic projection alone.

## Rendering requirements

Prefer the existing direct-game-WebGL rendering surface and state-save/state-restore discipline.

The renderer must:

- draw labels near the resolved enemy head/above-character anchor rather than in a fixed global box;
- preserve all WebGL state used by the game;
- handle drawing-buffer resize/fullscreen/DPR changes;
- reset smoothing on enemy lifecycle replacement, retarget, mapping change, camera discontinuity, or invalid->valid projection recovery;
- fail closed for invalid/non-finite/out-of-bounds projection rather than clamping a bad anchor into a fake attachment;
- keep the existing fixed danger HUD and startup/disabled diagnostics working.

## Required implementation-side regressions

Add focused deterministic tests covering at least:

1. target field `0/4/8` -> `1P/2P/3P`;
2. unsupported target -> no confident player label;
3. P1 -> P2 -> P3 retarget changes the same enemy label immediately with no stale hold;
4. simultaneous enemies targeting different players;
5. same slot/lifecycle replacement cannot inherit old label state;
6. stale marker/projection/camera epoch -> label suppressed/fail-closed;
7. invalid confidence / NaN / Infinity -> no anchored label;
8. valid near-edge anchor may clamp only the label rectangle, while invalid/out-of-bounds anchor never masquerades as attached;
9. resize/fullscreen mapping reset;
10. existing danger warning HUD still works;
11. read-only, `ramWrites=0`, input injection disabled, no Worker replacement, no Blob rewrite;
12. existing Alpha / Formal Real-Adapter regression suites remain contract-compatible.

Do not treat implementation-side tests as independent QA acceptance.

## Freshness impact / downstream gates

This feature will change release-consumed Alpha product blobs. Therefore before final release:

- freshness-sensitive Formal Real-Adapter QA must be re-evaluated/rerun against the changed blobs where required;
- a fresh independent target-label QA stage is mandatory;
- the bounded real Browser/WOF acceptance must visibly confirm labels follow real enemies and real retargets;
- Owner OneClick V3 must be generated only after these product blobs settle;
- Acceptance reconciliation and Release Freeze must consume the target-label PASS gate.

Do not invalidate the currently running Safe Transport 5h endurance merely because unrelated `product/alpha/**` presentation files change; apply its exact snapshot drift policy to the files it actually pins.

## Write boundary

Allowed implementation writes:

- `product/alpha/**` only as required for this feature and focused regression coverage;
- `parallel/ALPHA_ENEMY_TARGET_HEAD_LABELS/**` for implementation result/evidence;
- this stage claim.

Read/reuse HUDANCHOR reference files, but do not casually rewrite historical HUDANCHOR evidence or QA results.

Do not modify:

- Safe Transport implementation merely to make labels work;
- PYLAUNCH;
- Unified Live Proof / Recorder;
- Owner OneClick package snapshots;
- historical claims/results.

## Result / stop conditions

Record exact start/final HEAD, changed product blobs, target/position schema, rendering contract, focused test results, safety invariants, and freshness implications.

Success:

`COMPLETE — ALPHA V1 ENEMY TARGET HEAD LABELS IMPLEMENTED — READY FOR FRESH QA / BOUNDED LIVE PROOF`

If a precise implementation or projection blocker prevents a trustworthy first-release implementation:

`BLOCKED — ALPHA V1 ENEMY TARGET HEAD LABELS — <precise blocker>`

Owner action during implementation: **NO** unless the only remaining issue is the already-bounded real Browser/WOF projection proof; do not request broad manual exploration.
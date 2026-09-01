# WOF HUDANCHOR Player-Follow Bounds Fail-Closed Fix — Fresh Stage

stageId: `HUDANCHOR_PLAYER_FOLLOW_BOUNDS_FIX_V1`
priority: `P1`

## Dedup / claim
Read `parallel/PM/STAGE_DEDUP_GUARD.md` first.
If equivalent work is already complete, stop with:
`ALREADY COMPLETE — SAFE TO CLOSE — 当前线程空闲`
If already claimed, stop with:
`ALREADY CLAIMED — SAFE TO CLOSE — 当前线程空闲`
Otherwise claim `parallel/PM/STAGE_CLAIMS/HUDANCHOR_PLAYER_FOLLOW_BOUNDS_FIX_V1.json` before implementation.

## Why this stage exists
Fresh independent QA of `HUDANCHOR_PLAYER_FOLLOW_REFERENCE_IMPL_V1` found one precise repository-side blocker:

> finite out-of-bounds `anchorXNative` / `anchorYNative` can still be accepted when body coordinates remain in bounds, causing edge-clamped anchored output instead of fail-closed fixed-HUD fallback.

QA result:
- `parallel/HUDANCHOR_PLAYER_FOLLOW_QA/RESULT.md`
- blocker result commit: `3cc76b4cfe405b1d334ca8ad228052173e120d9f`

This is not a projection-research task and must not reopen broad geometry work.

## Write scope
Modify only:
- `parallel/HUDANCHOR_PLAYER_FOLLOW/**`
- mandatory stage claim file

Do not modify:
- `parallel/HUDANCHOR_PROOF/**`
- any active Browser-proof automation lane
- `product/alpha/**`
- PYLAUNCH / Recorder / Prospective / Browser Fleet / Transport

## Required fix
1. Validate the final resolved anchor coordinates themselves, not only player/body coordinates.
2. Finite but out-of-native-viewport anchor X/Y must be invalid.
3. Invalid/out-of-bounds anchor must route immediately to fixed-HUD fallback.
4. Never edge-clamp an invalid player-head anchor into an apparently valid attached cue.
5. Never reuse the previous valid player-head coordinate after invalidation.
6. Preserve correct clamping only for the final warning rectangle when the anchor itself is valid and near an edge.
7. Preserve immediate P1/P2/P3 retarget invalidation, lifecycle/respawn reset, camera discontinuity reset, stale/epoch fail-closed behavior, resize/fullscreen/DPR remap, and smoothing defaults.

## Mandatory regressions
Absorb the independent QA adversarial case and add at least:
- anchorXNative < 0 -> fixed fallback;
- anchorXNative >= native width -> fixed fallback;
- anchorYNative < 0 -> fixed fallback;
- anchorYNative >= native height -> fixed fallback;
- body/player position in bounds while derived head anchor out of bounds -> fixed fallback;
- valid anchor near viewport edge -> anchored rendering remains allowed and rectangle may be safely clamped;
- invalid anchor after one valid frame -> no last-coordinate reuse;
- retarget during invalid-anchor frame -> old player cue disappears immediately.

Run the existing full player-follow synthetic regression after the targeted tests.

## Safety / product semantics
Preserve the authoritative requirement:
`怪物锁定谁 -> 在被锁定角色 P1/P2/P3 头顶显示提示 -> 跟随角色 -> 不漂移 -> 换锁立即切换`

Preserve:
- read-only presentation semantics;
- no RAM writes;
- no input injection;
- no Worker replacement/wrap;
- no new danger semantics.

## Owner intervention
Repository-side only. No real Browser/WOF run is needed for this fix.

## Stop condition
Success:
`HUDANCHOR PLAYER-FOLLOW BOUNDS FIX READY — READY FOR FRESH QA`

Or stop with one exact blocker. Do not broaden scope.

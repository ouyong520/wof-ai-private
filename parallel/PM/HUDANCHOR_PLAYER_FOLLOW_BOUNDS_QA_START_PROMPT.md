# HUDANCHOR Player-Follow Bounds — Fresh Independent QA Start Prompt

## PM stage

- stageId: `HUDANCHOR_PLAYER_FOLLOW_BOUNDS_QA_V1`
- priority: **P1 product-experience mainline**
- product invariant: `怪物锁定谁 -> 在被锁定角色 P1/P2/P3 头顶显示提示 -> 跟随角色 -> 不漂移 -> 换锁立即切换`
- purpose: independently verify the just-delivered out-of-bounds fail-closed fix before PM counts this HUD blocker closed.
- Owner Browser/WOF: **NOT REQUIRED** for this repository-side bounds QA.

## Mandatory dedup / claim guard

Check `parallel/PM/STAGE_CLAIMS/HUDANCHOR_PLAYER_FOLLOW_BOUNDS_QA_V1.json` before substantive work.

- durable result exists -> `ALREADY COMPLETE — SAFE TO CLOSE — 当前线程空闲`
- exact stage ACTIVE elsewhere -> `ALREADY CLAIMED — SAFE TO CLOSE — 当前线程空闲`
- otherwise claim and continue.

Do not trust implementation READY or its 8/8 / 15/15 suites as independent proof.

## Read first

Re-read current HEAD and at minimum:

- `parallel/PM/PM_CORE_OPERATING_CHARTER.md`
- `parallel/PM/ENEMY_TARGET_LOCK_HUD_REQUIREMENT.md`
- `parallel/HUDANCHOR_PLAYER_FOLLOW_QA/RESULT.md`
- `parallel/HUDANCHOR_PLAYER_FOLLOW/RESULT.md`
- current `parallel/HUDANCHOR_PLAYER_FOLLOW/src/**` and relevant tests.

If implementation changes during QA, re-read affected blobs and rerun affected vectors.

## Write scope

Only:

- `parallel/HUDANCHOR_PLAYER_FOLLOW_BOUNDS_QA/**`
- `parallel/PM/STAGE_CLAIMS/HUDANCHOR_PLAYER_FOLLOW_BOUNDS_QA_V1.json`

Do not modify implementation.

## Fresh adversarial matrix

Independently validate at least:

1. final derived head anchor X below 0 -> anchored cue rejected, fixed-HUD fallback;
2. X exactly at nativeWidth and beyond -> fallback;
3. Y below 0 -> fallback;
4. Y exactly at nativeHeight and beyond -> fallback;
5. body/reference still valid while derived head anchor is invalid -> fallback, never edge-clamped anchored cue;
6. valid near-edge anchor remains anchored; only warning rectangle may clamp;
7. valid frame -> invalid frame clears smoothing/follow memory, old coordinate cannot be reused;
8. invalid frame during P1->P2/P2->P3 retarget: old target cue disappears immediately; new target may only anchor if valid;
9. NaN/Infinity/malformed dimensions and zero/negative viewport dimensions fail closed;
10. resize/fullscreen/DPR discontinuity cannot reuse pre-resize anchored coordinates;
11. camera discontinuity / respawn / object replacement reset follow state;
12. rapid alternating valid/out-of-bounds transitions never leave a stale cue at the screen edge;
13. P1/P2/P3 simultaneous routing/aggregation semantics remain intact;
14. read-only presentation invariants remain intact and no gameplay input/RAM writes are introduced.

This stage does **not** claim real Browser projection constants are correct. Do not convert synthetic bounds PASS into Browser-proof PASS.

## PM meaning

PASS closes the known out-of-bounds drift blocker and allows the player-head HUD path to advance to projection proof/integration. It should materially increase confidence in `不漂`, but the final real camera/Y-Z/head-offset proof remains separate.

## Stop conditions

PASS:

`PASS — HUDANCHOR PLAYER-FOLLOW BOUNDS FRESH QA — BOUNDS CLOSED; WAITING PROJECTION PROOF`

BLOCKED at first precise P0/P1 product blocker:

`BLOCKED — HUDANCHOR PLAYER-FOLLOW BOUNDS FRESH QA — <precise blocker>`

Owner action: `NO`.
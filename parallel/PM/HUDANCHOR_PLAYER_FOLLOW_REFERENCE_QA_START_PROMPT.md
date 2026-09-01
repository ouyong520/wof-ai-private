# HUDANCHOR Player-Follow Reference Implementation — Fresh Independent QA Start Prompt

stageId: `HUDANCHOR_PLAYER_FOLLOW_REFERENCE_QA_V1`
priority: `P1/P2 strategic accelerator`

## Dedup / claim
Read `parallel/PM/STAGE_DEDUP_GUARD.md` first.

If equivalent durable QA already exists, return exactly:
`ALREADY COMPLETE — SAFE TO CLOSE — 当前线程空闲`

If this stage is already claimed, return exactly:
`ALREADY CLAIMED — SAFE TO CLOSE — 当前线程空闲`

Otherwise claim under:
`parallel/PM/STAGE_CLAIMS/HUDANCHOR_PLAYER_FOLLOW_REFERENCE_QA_V1.json`

## Product requirement under QA
Authoritative semantic:

`怪物锁定谁 -> 在被锁定角色 P1/P2/P3 头顶显示提示 -> 跟随该角色 -> 不漂移 -> 换锁时立即切到新角色`

Marker is anchored to the player, not the enemy.

## Read first
- `parallel/HUDANCHOR_PLAYER_FOLLOW/**`
- `parallel/HUDANCHOR_REVERSE/RESULT.md`
- `parallel/HUDANCHOR_REVERSE/projection_candidate.json`
- `parallel/HUDANCHOR_PROOF/**` as read-only context
- `parallel/PM/ENEMY_TARGET_LOCK_HUD_REQUIREMENT.md`

## QA goal
Independently validate the player-follow reference implementation before real Browser projection constants are injected. Do not treat the implementation lane's own 15/15 as independent proof.

Build fresh adversarial/synthetic tests around the failure modes most likely to create visible drift or stale indicators:

1. continuous horizontal movement with independent camera scroll;
2. depth/lane movement;
3. jump/Z motion for all supported injected projection-model families;
4. rapid P1 -> P2 -> P3 -> P1 retarget with no old-player hold/residue;
5. simultaneous warnings routed to one target player;
6. two or three live players with independent coordinates;
7. player disappearance / death / respawn / slot reuse;
8. projection epoch/version change mid-frame;
9. camera discontinuity / stage transition;
10. drawing-buffer resize/fullscreen/letterbox changes;
11. CSS/DPR changes without using DPR as coordinate authority;
12. stale player state, stale projection state, stale drawing-buffer state;
13. invalid/out-of-bounds/non-finite anchors must fail closed to fixed-HUD fallback;
14. no last-known coordinate reuse after invalidation;
15. optional smoothing must reset at every lifecycle/projection/mapping discontinuity;
16. mapping from native -> drawing buffer -> WebGL clip must be internally reversible within defined tolerance;
17. target-lock identity must remain target-bound, not enemy-bound;
18. no danger-rule changes, RAM writes, input injection, Worker replacement, Blob/Data/ObjectURL rewrite.

Do not invent or certify real Browser camera/bias/Y-Z constants. Real projection truth remains owned by the active Browser proof lane.

## Write scope
Write only under:
- `parallel/HUDANCHOR_PLAYER_FOLLOW_QA/**`
- mandatory PM claim file

Do not modify:
- `parallel/HUDANCHOR_PLAYER_FOLLOW/**`
- `parallel/HUDANCHOR_PROOF/**`
- `parallel/HUDANCHOR_REVERSE/**`
- `product/alpha/**`
- PYLAUNCH / Recorder / Prospective / Browser Fleet

## Stop condition
Success:
`PASS — HUDANCHOR PLAYER-FOLLOW REFERENCE FRESH INDEPENDENT QA`

Or one precise blocker requiring a fresh fix lane.

Repository-side only. No Owner Browser/WOF run.
Owner action: `NO`.

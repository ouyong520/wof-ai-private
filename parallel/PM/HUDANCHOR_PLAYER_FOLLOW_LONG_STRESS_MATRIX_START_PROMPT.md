# HUDANCHOR Player-Follow Long Stress Matrix — Fresh Stage

stageId: `HUDANCHOR_PLAYER_FOLLOW_LONG_STRESS_MATRIX_V1`
priority: `P1 PRODUCT-EXPERIENCE LONG-RUN`

## 启动守卫

先读取：
- `parallel/PM/STAGE_DEDUP_GUARD.md`
- `parallel/PM/PM_DELIVERY_REASSESSMENT_GATE.md`
- `parallel/PM/ENEMY_TARGET_LOCK_HUD_REQUIREMENT.md`
- 最新 HUDANCHOR 默认分支状态与 claims

若 stop condition 已满足：
`ALREADY COMPLETE — SAFE TO CLOSE — 当前线程空闲`

若 claim ACTIVE：
`ALREADY CLAIMED — SAFE TO CLOSE — 当前线程空闲`

否则原子创建：
`parallel/PM/STAGE_CLAIMS/HUDANCHOR_PLAYER_FOLLOW_LONG_STRESS_MATRIX_V1.json`

## 产品目标

最终主显示形态不是固定 HUD，而是：
**怪物锁定谁 -> 在被锁定角色头顶显示 -> 跟随角色 -> 不漂 -> 换锁立即切换。**

固定 HUD 只作为 fail-closed fallback。

## 为什么现在做

Bounds fix、Projection Integration Prep、Browser proof automation 可以并行推进；本 lane 不改实现，只建立足够强的 adversarial/stress 验收矩阵，让真实投影常量一旦冻结即可立即做高强度回归，避免真人 proof 后再暴露大量边界问题。

## 写入范围

只允许写：
- `parallel/HUDANCHOR_PLAYER_FOLLOW_LONG_STRESS/**`
- 对应 stage claim

不得修改：
- `parallel/HUDANCHOR/**` 现有实现
- Browser proof automation 实现
- Alpha / Discovery / Recorder / PYLAUNCH

## 长任务矩阵

至少覆盖：

1. P1/P2/P3 单独锁定；
2. P1→P2→P3→P1 高频 retarget；
3. 同帧/邻帧锁定变化；
4. 横向移动；
5. 上下走位/depth；
6. jump/live Z；
7. camera scroll；
8. camera discontinuity；
9. resize；
10. fullscreen enter/exit；
11. DPR 1/1.25/1.5/2/高 DPI；
12. drawing-buffer 尺寸变化；
13. player death/respawn；
14. object replacement；
15. stale anchor；
16. NaN/Inf；
17. finite but out-of-bounds anchor；
18. near-edge valid anchor；
19. offscreen player；
20. invalid projection confidence；
21. stale camera mapping；
22. warning clear；
23. unsupported target；
24. multi-warning/multi-player isolation；
25. smoothing reset；
26. retarget 时旧 anchored hold 立即失效；
27. fallback 后重新恢复 anchored authority；
28. 禁止旧角色残影；
29. 禁止 edge clamp 冒充有效头顶位置；
30. 长序列随机但 deterministic 的 movement/retarget/resize/camera 组合。

## Stress / fuzz

构建 deterministic seed corpus，目标至少数千到数万 transition steps；如果 runner 能承受则扩大到更高数量。禁止用 sleep 凑时长。

每个 seed 输出：
- target player
- player generation
- projection generation
- anchor validity
- renderer mode anchored/fallback
- visible owner
- stale/clear reason

必须有 invariants：
- warning never stays on old target after retarget；
- invalid/stale/out-of-bounds anchor never remains anchored；
- fallback never becomes a screen-edge pseudo-anchor；
- valid anchor moves coherently with player/camera/projection；
- resize/fullscreen/DPR causes recompute, not stale reuse；
- respawn/object replacement clears old generation；
- no implementation/game input/write capability added。

## Current-HEAD 规则

如果 bounds fix 或 projection prep 在本 lane 执行期间提交新 HEAD：
- 重新读取影响到的 public contract；
- 更新测试适配层，不修改 SUT；
- 最终结果必须声明 testedHead 与 SUT blob。

## 第一 downstream consumer

- HUDANCHOR bounds fix fresh QA
- real projection integration QA
- Browser final visual acceptance

## Stop condition

发现精确 P0/P1 产品体验 blocker：
`BLOCKED — HUDANCHOR PLAYER-FOLLOW LONG STRESS — <precise blocker>`

或 current HEAD 对完整 stress matrix 无 blocker：
`PASS — HUDANCHOR PLAYER-FOLLOW LONG STRESS — READY FOR REAL PROJECTION FREEZE`

不得因为达到某个小时数自动 PASS。

## Kill / park

如果剩余唯一未知是只能从真实 Browser 画面获得的 camera/Y-Z/head-clearance 常量，停止在 `WAITING_BOUNDED_LIVE_PROOF`，不要扩大成无关逆向。

# HUDANCHOR Player-Follow Reference Implementation — Fresh Stage

stageId: `HUDANCHOR_PLAYER_FOLLOW_REFERENCE_IMPL_V1`
priority: `P1/P2 STRATEGIC ACCELERATOR`

## 启动去重守卫

先读取 `parallel/PM/STAGE_DEDUP_GUARD.md`、`parallel/PM/OWNER_INTERVENTION_GATE.md`、当前更正后的 target-lock HUD requirement、`parallel/HUDANCHOR/**` 和 GitHub 最新状态。

若 stop condition 已满足：`ALREADY COMPLETE — SAFE TO CLOSE — 当前线程空闲`，停止。
若 claim `parallel/PM/STAGE_CLAIMS/HUDANCHOR_PLAYER_FOLLOW_REFERENCE_IMPL_V1.json` 已存在：`ALREADY CLAIMED — SAFE TO CLOSE — 当前线程空闲`，停止。
否则原子 create-file claim；成功后才工作；完成/阻断更新 claim。

## 产品语义

`怪物锁定谁 -> 在被锁定角色 P1/P2/P3 头顶显示提示 -> 跟随该角色 -> 不漂移`

本线不得改攻击预测语义，只做 presentation/reference implementation。

## 写入范围

只允许：
- `parallel/HUDANCHOR_PLAYER_FOLLOW/**`
- mandatory PM claim

不要修改 `product/alpha/**`、PYLAUNCH、Recorder、Prospective、Browser Fleet。

## 目标

基于现有 HUDANCHOR contract，先把不依赖最终 Browser 常量的实现全部做完：

1. `PlayerAnchorResolver`
   - input: P1/P2/P3 live x/y/z + camera/projection state + drawing-buffer state;
   - output: anchor x/y + validity/freshness/confidence/reason;
   - projection constants/config 可注入、版本化；
   - stale / epoch mismatch / invalid viewport fail closed。

2. `TargetLockIndicatorRouter`
   - 根据当前 warning/target state 选择被锁定角色；
   - P1 -> P2/P3 retarget 时旧角色提示立即失效；
   - 不允许 target-bound hold 留在旧角色；
   - 多威胁时按当前产品语义聚合，不创造新预测规则。

3. `AnchoredWarningRenderer` reference
   - 直接 WebGL/drawing-buffer coordinate contract；
   - viewport clamp；
   - resize/fullscreen remap；
   - projection invalid 时 fixed HUD fallback；
   - 不依赖 DOM page coordinate 作为生产锚点。

4. 非漂移状态机
   - movement/depth/jump/camera scroll；
   - camera discontinuity；
   - player disappearance/respawn；
   - retarget；
   - fullscreen/DPR change；
   - smoothing only if needed，且不得造成 retarget 延迟。

5. synthetic regression
   - horizontal movement；
   - camera scroll；
   - depth；
   - jump；
   - P1/P2/P3；
   - retarget P1->P2->P3；
   - resize/fullscreen；
   - stale projection -> fixed fallback；
   - multi-warning；
   - no stale old-player marker。

如果最终 projection constants 尚未证明，使用明确标记的 synthetic fixture，不得猜值写死成“已证明”。

## Safety

保持 read-only presentation semantics；no RAM writes；no gameplay input；no Worker replacement；不修改 Alpha 产品代码。

## Stop condition

`HUDANCHOR PLAYER-FOLLOW REFERENCE IMPLEMENTATION READY`

要求：实现主体 + synthetic regression READY；剩余只允许是将已证明的真实 Browser projection constants/wiring 注入 reference implementation，而不是重新设计架构。
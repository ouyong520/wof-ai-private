# HUDANCHOR Player Projection Reverse Engineering — Fresh Stage

stageId: `HUDANCHOR_PLAYER_PROJECTION_REVERSE_V1`
priority: `P1/P2 STRATEGIC ACCELERATOR`

## 启动去重守卫

先读取：
- `parallel/PM/STAGE_DEDUP_GUARD.md`
- `parallel/PM/PRIORITY_POLICY.md`
- `parallel/PM/OWNER_INTERVENTION_GATE.md`
- `parallel/PM/PLAYER_TARGET_LOCK_HUD_REQUIREMENT.md`（若不存在，读取当前更正后的 target-lock HUD requirement）
- `parallel/HUDANCHOR/**`
- GitHub 默认分支最新状态

若 stop condition 已满足：输出 `ALREADY COMPLETE — SAFE TO CLOSE — 当前线程空闲` 并停止。
若 claim `parallel/PM/STAGE_CLAIMS/HUDANCHOR_PLAYER_PROJECTION_REVERSE_V1.json` 已存在：输出 `ALREADY CLAIMED — SAFE TO CLOSE — 当前线程空闲` 并停止。
否则原子 create-file claim；成功后才工作；完成/阻断更新 claim。

## 产品目标

最终显示语义：

`怪物锁定谁 -> 在被锁定角色 P1/P2/P3 头顶显示提示 -> 提示跟随该角色 -> 不漂移`

本线只解决“角色世界/游戏状态坐标如何稳定投影到真实 Browser 游戏画面”这一根问题，不研究无关字段。

## 写入范围

只允许新增/修改：
- `parallel/HUDANCHOR_REVERSE/**`
- mandatory PM claim

不要修改：
- `product/alpha/**`
- PYLAUNCH / Recorder / Browser Fleet / Prospective
- 当前正式 HUD 产品实现

## 必须优先复用现有证据

读取并交叉利用：
- `parallel/HUDANCHOR/**`
- GEO / HUD / Browser WebGL 已有证据
- 已知 player X/Y/Z 结构
- 已有 camera/projection candidate evidence
- WinKawaks bridge / local runtime 中可安全复用的 camera/player field 语义
- Browser 与 WinKawaks timing/coordinate audit
- 历史 captures / fixtures / probe output（如仓库已有）

禁止因为“想完整”而 broad reverse-engineer 整个游戏。

## 目标

尽可能在不要求 Owner 的情况下闭合：
1. player X -> native screen X 模型；
2. camera X address/read/sign/scale；
3. player Y/depth -> screen Y；
4. Z/jump -> screen Y 修正；
5. drawing-buffer/content viewport mapping；
6. resize/fullscreen/DPR mapping；
7. stable above-character clearance 的可证明范围；
8. P1/P2/P3 是否共享同一 projection model；
9. stale/camera epoch mismatch 时 fail-closed 条件。

允许：静态逆向、已有 ROM/bridge 逻辑分析、历史 trace replay、synthetic data、离线差分。

## 强制收敛

每个发现必须回答：它是否直接减少 `MINIMAL_BROWSER_PROBE.md` 仍需真人证明的未知量？

不得扩展到：
- 全 RAM map；
- 全角色动画系统；
- 无关攻击逻辑；
- 无关 HUD 美术。

如果某个常量/变换本质上只能由真实 Browser canvas + live camera 联合证明，精确列出并停止继续猜测。

## Stop condition

满足其一：

A. `HUDANCHOR PLAYER PROJECTION REVERSE READY — IMPLEMENTATION CONSTANTS DERIVED OFFLINE`

或

B. `HUDANCHOR PLAYER PROJECTION REVERSE READY — ONLY EXACT BOUNDED LIVE PROOF REMAINS`

必须输出 machine-readable projection candidate + 中文结论，并明确剩余真人 proof 是否仍不可避免。
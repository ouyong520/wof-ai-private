# HUDANCHOR One-Click Browser Proof Automation — Fresh Stage

stageId: `HUDANCHOR_ONECLICK_BROWSER_PROOF_AUTOMATION_V1`
priority: `P1 OWNER-TIME REDUCER / P2 ACCELERATOR`

## 启动去重守卫

先读取：
- `parallel/PM/STAGE_DEDUP_GUARD.md`
- `parallel/PM/OWNER_INTERVENTION_GATE.md`
- 当前更正后的 target-lock HUD requirement
- `parallel/HUDANCHOR/**`
- 当前 PYLAUNCH / CDP 只读 discovery 能力
- GitHub 默认分支最新状态

若 stop condition 已满足：输出 `ALREADY COMPLETE — SAFE TO CLOSE — 当前线程空闲` 并停止。
若 claim `parallel/PM/STAGE_CLAIMS/HUDANCHOR_ONECLICK_BROWSER_PROOF_AUTOMATION_V1.json` 已存在：输出 `ALREADY CLAIMED — SAFE TO CLOSE — 当前线程空闲` 并停止。
否则原子 create-file claim；成功后才工作；完成/阻断更新 claim。

## 背景

旧 `parallel/HUDANCHOR/MINIMAL_BROWSER_PROBE.md` 仍要求 Owner：
- Worker Console loader；
- Top page Console loader；
- 一次 calibration click；
- 手工观察 Y-Z/Y+Z/Y。

这不符合当前 Owner workload policy。目标是在不降低证据质量的前提下，把真人步骤压缩到最小。

## 写入范围

只允许：
- `parallel/HUDANCHOR_PROOF_AUTOMATION/**`
- mandatory PM claim

不要修改 Alpha、PYLAUNCH 核心、Recorder、Fleet、Prospective。

## 目标

利用现有 localhost CDP / page-session / Worker attach 能力，制作自动化 HUDANCHOR proof harness：

1. 自动发现当前 WOF page + native Worker；
2. 自动确认 exact World 921031；
3. 自动在 Worker 侧只读采 player x/y/z、camera candidates；
4. 自动在 Top page 获取 canvas/WebGL drawing buffer / content rect；
5. 自动同步两个 context 的 sample epoch；
6. 自动拟合/评分 X-camera、Y-depth、Z-jump candidate models；
7. 自动输出 machine-readable `HUDANCHOR_PROOF.json` + 中文摘要；
8. 自动 fail closed，无法证明时不能写 PASS；
9. readOnly=true / ramWrites=0 / inputInjection=false / no Worker replacement；
10. 不要求 DevTools、不要求 Owner 粘 JS。

## Owner interaction minimization

优先尝试完全自动化 calibration：
- 复用已证明 native player reference / projection evidence；
- 利用运动相关性和 drawing-buffer mapping 自动评分模型。

如果“人物头顶绝对视觉高度”本质上仍需要一次视觉 ground truth，则最多保留：

`双击一键文件 -> 正常移动/跳一下 -> 在人物头顶点一次 -> 自动完成 -> 只交一个 JSON`

不得要求 Worker Console / Top Console / 两次 loader / 长代码粘贴。

如连 calibration click 也可通过现有 sprite/reference evidence消除，则消除它。

## Offline tests

至少覆盖：
- two-context synchronization；
- camera scroll synthetic trace；
- depth trace；
- jump trace；
- wrong identity；
- stale epoch；
- resize/fullscreen mapping change；
- missing Worker/page；
- ambiguous model -> BLOCKED；
- exact good trace -> PASS；
- safety invariants。

## Stop condition

`HUDANCHOR ONE-CLICK BROWSER PROOF AUTOMATION READY`

必须明确：
- 最终是否还能完全无需 Owner；
- 若仍需 Owner，精确剩余步骤必须不超过一个 bounded action session；
- 不得为了“看起来自动”降低 proof 标准。
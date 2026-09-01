# WOF Alpha Fixed HUD Stability — Fresh Independent Offline QA

stageId: `ALPHA_FIXED_HUD_STABILITY_QA_V1`
priority: `P2`

## 启动去重守卫
先读取：
- `parallel/PM/STAGE_DEDUP_GUARD.md`
- `parallel/PM/OWNER_INTERVENTION_GATE.md`
- `parallel/PM/PM_CORE_OPERATING_CHARTER.md`
- GitHub 最新状态

若 stop condition 已满足：输出 `ALREADY COMPLETE — SAFE TO CLOSE — 当前线程空闲` 并停止。
若 `parallel/PM/STAGE_CLAIMS/ALPHA_FIXED_HUD_STABILITY_QA_V1.json` 已存在：输出 `ALREADY CLAIMED — SAFE TO CLOSE — 当前线程空闲` 并停止。
否则原子 create-file claim；成功后才工作；完成/阻断更新 claim。

## 背景
Owner 已明确第一个可用版本优先接受固定 HUD，只要稳定、不漂移；人物头顶锚定 HUD 不阻塞 Alpha。

## 写入范围
只允许新增/修改：
- `parallel/ALPHA_FIXED_HUD_QA/**`

只读检查：
- `product/alpha/**`
- `parallel/ALPHAACCEPT/**`
- `parallel/HUDANCHOR/**`

禁止修改产品 Alpha、PYLAUNCH、Recorder、Prospective、Unified Proof。

## QA 目标
独立验证当前 fixed in-game HUD 作为 Alpha fallback/首发显示方案是否具备“稳定不漂移”的 repository-side依据。

至少覆盖：
1. 固定 HUD 坐标不依赖 player X/Y/Z；
2. camera scroll 不改变固定 HUD 游戏画面锚点；
3. P1/P2/P3 warning row 切换不会让旧目标位置残留；
4. 多 warning 布局确定性；
5. canvas/drawing-buffer resize 后重新映射，不漂到页面/sidebar；
6. fullscreen / DPR / viewport 变化时 fixed HUD 使用当前 drawing-buffer，而不是历史 CSS 坐标；
7. WebGL state save/draw/restore 不污染游戏；
8. diag/stale/disable 时旧 warning 清理规则保持；
9. HUD renderer unavailable/failure 时 gameplay fail-open；
10. readOnly=true / ramWrites=0 / no input；
11. legacy HUD teardown 不残留；
12. anchored-HUD 未就绪时 fixed fallback 始终可用。

允许用 mock WebGL、synthetic resize/viewport vectors、静态代码审计和现有 RC5/RC4 QA harness。不要要求真人 Browser。

如果发现产品级缺陷：不要在本 QA 帖修 `product/alpha/**`；写精确 blocker 和最小复现，等待 PM 开 fresh fix stage。

## Stop condition
以下二选一：
- `PASS — FIXED HUD STABLE FOR ALPHA FALLBACK`
- `BLOCKED — <精确 P0/P1/P2 blocker>`

必须输出 machine-readable result + 中文摘要。
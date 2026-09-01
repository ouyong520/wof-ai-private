# WOF Future Danger AI — Product Mainline Roadmap

Updated: 2026-09-01

## Product north star

最终目标不是“完成更多工具”，而是：

**让 WOF Future Danger AI 在真实 WOF 中持续理解敌人/玩家状态，提前判断危险，给出正确目标/方向/时机，并逐步发展到能够稳定辅助甚至实现接近/达到 0 伤通关。**

工具、Recorder、Fleet、Validator、Launcher 都只是为这个核心产品服务。

## 关于 WOF-052 / WOF-052L

- `WOF-052L` 当前是**长时间、多房间、只读证据采集与研究数据管线**，不是最终用户核心程序本身。
- 它非常重要，因为它为危险预测规则、ordered sequence、覆盖率和 prospective validation 提供真实 Browser 数据。
- 最终用户核心仍是 **WOF Future Danger AI / Alpha -> Beta -> v1** 的实时 detector + warning/HUD + 后续 safe-path/assist 系统。

因此 PM 不应把“WOF-052L 工具做完”误当产品主线终点。它是核心研发基础设施的一部分。

## 阶段路线

### Stage A — 真人可用 Alpha：可靠预警

目标：普通用户可以一键启动，在真实 Browser WOF 中稳定看到**少量但可信**的危险预警。

必须具备：
- 自动识别真实 WOF page / native Worker / WASM / heap；
- exact World 921031 identity；
- safe transport；
- validated production rules only；
- per-enemy warning；
- target P1/P2/P3；
- left/right；
- supported lead time；
- UNKNOWN 静默；
- HUD；
- fail-open gameplay / fail-closed warning；
- read-only / ramWrites=0 / no input injection；
- normal user one-click Chinese UX。

Alpha **不要求**覆盖全游戏，也不要求 0 伤。

### Stage B — Beta：从“能提示”到“多数危险可用”

目标：常见危险事件覆盖率显著提高，实战中用户可以依赖系统进行躲避。

重点：
- WOF-052L 10-room / 1h+ natural capture；
- ordered sequence / ambiguous-state disambiguation；
- prospective multi-room validation；
- common dangerous-event coverage；
- lifecycle/retarget/session robustness；
- head/player anchored HUD；
- danger priority / multi-threat handling；
- approximate safe movement suggestion。

### Stage C — Safe Path / No-Damage Assist

目标：不仅告诉用户“危险来了”，还告诉用户：

**往哪里移动、什么时候移动、哪个敌人优先处理，才能最大概率不受伤。**

需要：
- player/enemy world geometry；
- attack hitbox / threat region / timing；
- reachable-space model；
- safe-position / safe-path planner；
- multi-enemy threat fusion；
- camera/scroll/scene handling；
- uncertainty-aware planning；
- real-time replanning。

### Stage D — 0 伤通关目标

分两种模式：

1. **Warning/Guidance mode**：系统指导真人操作，目标逐步逼近 0 伤；
2. **Optional Assist mode**（后 Alpha）：允许用户触发/授权 move command / one-key action / command injection，再进一步研究 closed-loop execution。

0 伤通关不是单一规则问题，而是：

`预测 + 几何 + 路线规划 + 多敌人决策 + 动作执行 + 全关卡覆盖 + 鲁棒性`

必须逐阶段证明，不直接跳到 autoplay。

## 当前距离 Alpha

当前不是从零开始。已经具备：
- RC5 safe bootstrap / room-entry repair QA PASS；
- Browser/CDP real Windows connection PASS；
- game remains playable while attached PASS；
- Alpha detector/HUD/regression 基础；
- Safe Transport contract READY；
- Browser Fleet / Recorder / Analyzer / Prospective tooling 基础；
- exact World 921031 golden identity；
- existing production-safe warning rules；
- one-click/Chinese UX tooling基础。

当前 Alpha 仍有 4 个实质 gate：

1. **Discovery V2 repository correctness/alignment**：关闭当前 Recorder/Prospective evidence-admission P0 和相关 P1 drift；
2. **ONE unified real Windows/WOF proof**：真实证明 page/Worker/WASM/heap/World 921031 + game playable；
3. **Alpha Safe Transport implementation + fresh QA**；
4. **bounded Browser Acceptance**：真实 warning/HUD/target/side/UNKNOWN 行为通过。

通过后才进入 Alpha release decision。

## PM priority implication

当前所有任务必须回答一个问题：

> 它是否直接缩短 Stage A 真人可用 Alpha，或为 Stage B/C 的核心危险预测/0伤路径提供不可替代证据？

如果不能，就降级/等待，不为了填并发槽位而启动。

## Owner intervention

遵守 `parallel/PM/OWNER_INTERVENTION_GATE.md`：

只有仓库侧代码/逆向/mock/QA/回归都做到极限后，才让 Owner 做一次不可模拟的真实运行或长采集。

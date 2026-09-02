# Alpha V1 Bounded Live Acceptance — Owner Flow V2

Status: **FINAL OWNER-FACING PROCEDURE DEFINED — EXECUTE ONLY AFTER CURRENT LIVE/PROOF GATES ARE GREEN**

目标：Owner 不需要 DevTools、不需要手工脚本、不需要自己打一整局，也不需要通关。

最终真人验收应当是：

`启动最终 OneClick -> 进入别人正在玩的活跃房间 -> 约 5–10 分钟完成关键观察/简单动作`

本流程只定义真人验收操作和判定，不改变 danger rules、target semantics、Transport、projection 常量或 OneClick 实现。

## 0. 开始前必须满足

1. 使用 PM 明确指定的**最终 OneClick acceptance candidate**，不得拿旧包、手工拼包或浏览器脚本替代。
2. OneClick 必须能够正常附着当前 WOF/runtime；Owner 只看正常启动/附着结果，不开 DevTools。
3. 当前 player-head / enemy-head live proof 与 proof-authority gate 必须已绿。任何 repository/synthetic 结果都不能代替真人 Browser/WOF 证据。
4. 当前 danger coverage authority 必须使用仓库已经证明的 production rule / move mapping；**禁止凭角色名、动画长相、attack ID 自己猜招式名称**。
5. 如果当前仓库还不能把 production rule 映射成 Owner 能肉眼确认的具体招式，则该场 session 的 danger-detection 项只能记 `NOT EXERCISED`，不能凭印象判 PASS 或 FAIL。

当前 core 快照本身只证明两条 production-enabled danger rule：

- `T18_5440_CYCLE_BODY7512_TM4_LEVEL_90`，type `18`，attack `5440`；
- `T18_5424_CYCLE_BODY7520_TM4_LEVEL_90`，type `18`，attack `5424`。

其余四条 frozen rule 当前为 quarantined / `production:false`，不会作为当前 production `[危险]` 规则发出 warning。本流程**不**给 type 18、5440、5424 擅自附加夏侯惇、曹仁、飞身、扑击、冲撞等中文名称；后续以 current danger coverage authority audit 的最终映射为准。

## 1. 5–10 分钟 Owner checklist

### A. 启动与进房（约 1 分钟）

- [ ] 启动最终 OneClick。
- [ ] 确认没有完整性/附着错误，当前 WOF/runtime 正常连接。
- [ ] 进入一个**已经有人正在玩的活跃房间**；不要求自己开房，不要求从头开始，也不要求通关。
- [ ] 先观察 10–20 秒：当前画面稳定，若有可支持敌人，怪物头顶应出现其当前目标 `1P / 2P / 3P`；若此时没有可支持敌人，先继续，不立即判 FAIL。

### B. 基础移动与头顶跟随（约 2 分钟）

依次做，动作不需要追求战绩，只需要让画面产生足够位移：

- [ ] 左右移动一段距离；
- [ ] 上下 / 纵深移动一段距离；
- [ ] 普通跳一次完整周期；
- [ ] **后跳 / rear jump 一次完整周期**：起跳 -> 反向水平移动 -> 最高点 -> 下落 -> 落地；
- [ ] 快速向前推进；
- [ ] 让镜头发生一次明显的整屏 / stage scroll。

观察规则：

- 有 `1P / 2P / 3P` 时，标签必须跟着**同一只正确怪物**移动，不能留在旧位置、跟错怪、明显拖尾或跨对象残留。
- 有真实 `[危险]` warning 时，且当前 authority 有效，`[危险]` 必须跟着**正确玩家头顶**移动；左右、纵深、普通跳、后跳、快速推进、卷屏中都不能出现可重复或明显漂移。
- 后跳特别看五个阶段：起跳、反向位移、最高点、下落、落地。warning 若恰好不在该动作期间出现，则后跳只完成 player projection 的运动压力子项；`[危险]` 本身仍需在别的真实 warning 窗口证明。

### C. Retarget（约 1 分钟，房间自然出现即可）

- [ ] 如果怪物在现场发生改锁，观察至少一次 `1P -> 2P`、`2P -> 3P` 或其他真实 retarget。
- [ ] 新目标必须马上显示；旧目标标签不能残留、不能 hold 在上一目标。

如果 5–10 分钟内房间没有自然发生 retarget：记 `NOT EXERCISED`，不是 FAIL；但不能把 retarget gate 写成 PASS。

### D. Resize / Fullscreen / DPR 映射（约 1–2 分钟）

- [ ] 改一次窗口大小（resize）。
- [ ] 切一次 fullscreen / 退出 fullscreen。
- [ ] 如果当前环境能在不破坏 session 的前提下自然产生 DPR / 显示缩放映射变化，则做一次；如果不能自然做到，DPR 子项记 `NOT EXERCISED`，禁止手工脚本伪造。

映射变化后：

- 当前有效 authority 下，头顶 overlay 必须使用**新映射**继续跟随；
- 不允许短暂回到旧 drawing-buffer / 旧 screen coordinate 后继续画；
- authority 若变 stale/invalid，必须 hide / fixed-HUD fallback，而不是继续用旧坐标画 anchored overlay。

### E. Death / respawn（自然出现才观察）

- [ ] 如果玩家自然死亡 / respawn，确认旧玩家头顶坐标、旧 calibration、旧 warning anchor 不残留；新 lifecycle 只使用新位置。

没有自然发生 death/respawn：记 `NOT EXERCISED`，不是 FAIL。

### F. Invalid / stale authority fail-closed

Owner 不使用 DevTools 或手工脚本制造 stale authority。

- 如果最终 OneClick acceptance mode 自己提供正常的 bounded stale/rebind exercise，只需要按 OneClick 提示观察；
- 或者 session 自然出现 reconnect / rebind / stale / invalid authority window 时观察。

正确行为：

- enemy head label：**hide / no-draw**；
- player warning：**fixed HUD fallback 或 hide**；
- 绝不能继续显示一个看起来“还在跟”的旧 anchored 坐标。

如果本次房间完全没有出现、且 OneClick 也没有自动产生可验证的 stale/invalid window：记 `NOT EXERCISED`。若该项仍是 release mandatory gate，则整体仍 `NOT RELEASED`，不能用 synthetic 替代。

## 2. `[危险]` 必须这样分类

### Detection PASS

只有在**当前 repository authority 已经明确证明为 production-enabled 的危险招式**确实发生，并且 warning 正常出现时，才可把该事件记为 detection PASS。

### Detection FAIL

当前明确支持、且 Owner 能依据仓库 authority **正向识别**的危险招式已经发生，但 warning 没有出现：

`DETECTION FAIL`

这是危险检测覆盖/触发失败，不是 projection failure。

### Projection FAIL

warning 已经真实存在，但 `[危险]`：

- 漂离正确玩家头顶；
- 明显拖尾；
- 停在起跳点 / 旧坐标；
- resize/fullscreen/DPR 后继续使用旧 mapping；
- retarget/lifecycle/authority 变化后仍画旧 anchor；

则记：

`PROJECTION FAIL`

### NOT EXERCISED

本次 5–10 分钟房间里**根本没有出现当前已明确支持、且可正向识别的 production danger move**：

`NOT EXERCISED`

不能假 PASS，也不能自动判 FAIL。

### Unsupported / unmapped attack

一个 unsupported / quarantined / research-only / 当前无法 authority-map 的 attack 没有 warning：

- **不是 projection failure**；
- 也不能据此判 production detection FAIL；
- 记录为 `UNSUPPORTED/UNMAPPED — NOT A PROJECTION FAILURE`，对应 production danger live item 仍按实际是否被 exercise 决定。

## 3. Surface 判定表

| Surface / subcase | PASS | FAIL | NOT EXERCISED |
|---|---|---|---|
| Danger detection | 已证明支持的 move 发生且 warning 出现 | 已证明支持的 move 发生但 warning 不出现 | 没遇到/无法 authority 正向识别支持 move |
| Player-head `[危险]` projection | warning 存在且在当前有效 authority 下始终贴正确玩家 | warning 存在但漂、拖尾、旧坐标、错 lifecycle/mapping | 本场没有真实 warning 窗口 |
| Enemy `1P/2P/3P` projection | 标签贴正确怪物并随运动/映射更新 | 错怪、错目标、漂移、旧标签残留、stale 仍画 | 本场没有可支持敌人/目标窗口 |
| Retarget | 真实改锁后立即切到新 `1P/2P/3P`，旧标签清除 | 改锁后旧标签残留/目标错误 | 本场没有真实 retarget |
| Rear jump | 完整五阶段无可见 anchor 漂移 | 任一阶段明显拖尾/停旧坐标/错位 | 对需要特定 surface 的子项，当时该 surface 没出现 |
| Resize/fullscreen/DPR | 当前 authority 使用新 mapping | 继续用旧 mapping 或明显错位 | 某项环境未自然 exercise |
| Death/respawn | 新 lifecycle 不复用旧 anchor/calibration | respawn 后旧位置/旧身份继续生效 | 本场未发生 |
| Stale/invalid authority | enemy hide；player fixed/hide | stale/invalid 时仍 anchored draw | 本场无该窗口且 OneClick 未自动 exercise |

## 4. 最终 session 结论

- `PASS`：所有 release-mandatory live gates 都有**真实 Browser/WOF**证据，且没有 detection/projection/identity/retarget/stale-authority FAIL。
- `FAIL`：出现任意明确可复现的 mandatory failure；该 failure 按上表归类，不把 detection 和 projection 混在一起。
- `NOT EXERCISED`：不是 bug verdict；表示这个房间没有提供该证据窗口。只要仍有 mandatory gate 是 `NOT EXERCISED`，整体就保持 **NOT RELEASED**，以后再用另一个 bounded active-room session 补齐，不能用 synthetic/repository fixture 顶替。

不要求 Owner 为了补一个 `NOT EXERCISED` 继续打一整局或通关。

## 5. 失败时留什么证据

正常 PASS 不要求 Owner 截一堆图。

出现 FAIL 时：

- 优先录 **5–15 秒短视频**，包含失败前后动作；
- 或截 1–2 张能看出“正确对象 + 错误 overlay 位置/目标”的图；
- 尽量保留发生场景：左右、纵深、普通跳、后跳、快速推进、卷屏、retarget、resize/fullscreen/DPR、death/respawn、stale/rebind。

不要求 DevTools、console log 或手工脚本。

## 6. Owner 一行报告格式

只发一行即可：

`PASS/FAIL/NOT EXERCISED | surface=危险检测/玩家[危险]/怪物目标/stale回退 | scene=后跳/卷屏/retarget/resize/... | symptom=一句话描述`

例：

`FAIL | surface=玩家[危险]-projection | scene=后跳下落 | symptom=[危险]停在起跳位置约半秒`

或：

`NOT EXERCISED | surface=危险检测 | scene=活跃房间8分钟 | symptom=未遇到仓库已确认支持的危险招式`

## 7. Fail-closed release rule

**没有真实 live evidence = NOT RELEASED。**

Repository QA、synthetic fixture、serialized candidate evidence、历史 Browser/WOF 片段都不能把本次 mandatory live gate 自动升级为 PASS。

最终 Owner 的工作量边界就是：启动最终 OneClick、进入活跃房间、做上面的简单动作/观察，约 5–10 分钟；不要求 DevTools、不要求手工脚本、不要求自己打完整局、不要求通关。

# WOF Future Danger AI — 项目总览 / 完整逻辑 / 当前进度

更新时间：2026-08-31  
仓库：`ouyong520/wof-ai-private`  
游戏：WOF / Warriors of Fate / 吞食天地II / 三国志II，World 921002 / MAME `wofr1`

> 这是项目的长期“项目总结 / MASTER PROGRESS”。  
> 新对话快速接手：先读 `WOF_AI_HANDOFF.md`；查看最新实验边界：读 `WOF_AI_CURRENT_FRONTIER.md`；理解历史逆向细节：读 `WOF_AI_REVERSE_PROCESS.md`；需要全局项目逻辑、方法演化、production 规则与当前进度：读本文件。

---

## 1. 项目最终目标

目标不是自动操作，而是做 **Future Danger AI / 未来危险预测层**。

核心任务：在敌人的攻击真正进入 ACTIVE 之前，读取 Browser/MAME 的 live RAM 与 ROM AI 状态，提前判断：

```text
哪个 enemy 即将产生危险
→ 可能是哪种 attack
→ 当前 target 是 P1 / P2 / P3 中谁
→ 左 / 右侧方向是否稳定
→ 距离 ACTIVE-start 大约还有多久
→ 最终供 Future Danger Map / Safe Path 使用
```

重点是降低误报。不能因为 P1 离敌人近，就在敌人实际上锁定 P2 时一直给 P1 报警。

当前研究已经从“攻击发生后解释过去”转成：

```text
enemy+0x70 仍为 0
→ 识别当前 zero-attack cycle 的真实前驱状态
→ 提前 arm warning
→ 同一个 enemy 未来真正发生 +0x70 0->nonzero
→ 正向验证 attack / target / side / lead / miss
```

这套 prospective forward validation 是当前 production 规则的权威验证方法。

---

## 2. 强制工作协议

主线协作规则：

1. GitHub 是项目权威状态。
2. 用户每轮只负责运行一条 Browser Console 命令，并上传 JSON / Console 输出。
3. Assistant 负责分析、GitHub 更新、版本推进、下一轮实验设计。
4. 每次回传首先严格校验：

```text
copyId
project
version
marker / expectedMarker
readOnly
ramWrites
```

要求：

```text
project = WOF-AI-PRIVATE
readOnly = true
ramWrites = 0
```

身份不匹配时，不能把数据算进当前证据。

5. 每轮只给用户 ONE Console command。
6. 每条命令必须有唯一 `// WOF-xxx` 标记。
7. 不要求用户手工编辑 JS；需要修改时直接改 GitHub。
8. 多房间结果必须保留 per-room 边界。
9. WinKawaks discovery 与 Browser production 主线隔离；本地 offset 不能直接升级 Browser production 结论。

---

## 3. Browser / WASM 运行环境

```text
网页
→ cycgo.js
→ Web Worker: gstyphoon.js
→ gstyphoon.wasm
→ CPS RAM + live 68000 ROM
```

live ROM 已能从 Worker 恢复并缓存：

```js
self.__WOF_ROM_LOC_CACHE
```

旧 offline DB 与 live ROM 地址关系：

```text
live = offline + 0x34
```

不再做一次性 256MB HEAP 全扫；优先复用 ROM cache / resume 脚本。

---

## 4. 已锁死的 RAM 基础地址

### 玩家对象

```text
P1 = 0xFFBE1C
P2 = 0xFFBEFC
P3 = 0xFFBFDC
stride = 0xE0
```

玩家自身 index：

```text
P1 +0x7C = 0
P2 +0x7C = 4
P3 +0x7C = 8
```

### Enemy pool

```text
base   = 0xFFC0BC
stride = 0xE0
slots  = 20
```

### Enemy 当前目标 selector

权威字段：

```text
enemy +0x7E
```

值：

```text
0 -> P1
4 -> P2
8 -> P3
```

**最终输出时必须实时重读 +0x7E。**

历史已经抓到 warning 后、ACTIVE 前约几十毫秒发生 retarget 的真实样本，所以 warning entry target 不能冻结成最终锁定目标。

`enemy+0x6A` 只可作为 supporting pointer-cache 证据；只有精确 BE1C / BEFC / BFDC 时有辅助价值，不能替代 `+0x7E`。

---

## 5. P1/P2/P3 selector 已严格解决

ROM 玩家指针表：

```text
0x010CF8 = P1
0x010CFC = P2
0x010D00 = P3
```

关键 selector：

```text
0x010E66 MOVE.W 126(A0),D1
0x010E6A LEA 0x010CF8,A1
0x010E6E MOVE.L 0(A1,D1.W),A1
```

因此：

```text
enemy+0x7E
→ 0 / 4 / 8
→ P1/P2/P3 pointer table
→ A1 = selected player object
```

至少还有 `0x010C82 / 0x010D2C / 0x010DDA` 等同类 selector 访问点。

`0x010E72 MOVE.W A1,506(A5)` 保存 selected-player 地址低 16 bit。多个 reader 会通过 `MOVEA.W` 符号扩展重新形成 `FFFFBE1C / FFFFBEFC / FFFFBFDC`，说明 506(A5) 是 selected-player scratch/cache；但它不是当前 dispatcher 的直接本地桥。

---

## 6. Dispatcher 架构已经解决

早期误区是把 47 个 type entry 当作直接函数入口。真实结构是两级 dispatch。

### dispatcher 0x25B6

```text
0x25B6  MOVE.W 32(A0),D1
0x25BA  ADD.W D1,D1
0x25BC  ADD.W D1,D1
0x25BE  MOVE.L 28(PC,D1.W),A4
0x25C2  MOVE.L 0(A4,D0.W),A4
0x25C6  RTS
```

### dispatcher 0x25C8

```text
0x25C8  MOVE.W 32(A0),D1
0x25CC  ADD.W D1,D1
0x25CE  ADD.W D1,D1
0x25D0  MOVE.L 10(PC,D1.W),A4
0x25D4  MOVE.L 0(A4,D0.W),A4
0x25D8  BRA 0x247C
```

语义：

```text
enemy type
→ type-specific level2 table
→ 上游已准备好的 D0 byte offset
→ descriptor / handler
```

`wof_dispatch_incoming_edges.js` 已确认：

```text
directIncomingEdges = 44
edges25B6 = 4
edges25C8 = 40
fallthrough = 0
```

大量入口直接 `MOVEQ #0/#4/#8/#12... ,D0` 后进入 dispatcher，证明真正 state offset 由上游 AI 状态机选择。

这些 44 条 incoming edge 已经解决，不要重新扫描。

---

## 7. State / action → dispatcher 链已接通

Selector 后存在两层状态分派：

```text
enemy+0x99
→ 第一层 state table
→ enemy+0x2A
→ 第二层 action table
→ 具体 AI routine
→ dispatcher 0x25C8
→ descriptor
```

已严格证明的一条路线：

```text
state99 = 0
→ first block 0x010BBC

action2A = 2
→ 0x010EC6
→ ...
→ dispatcher 0x25C8
```

这条 selector / state / action / dispatcher bridge 已经是结构性证明，不再是猜测。

---

## 8. Descriptor consumer 0x247C 已解决

`0x25C8` 选择的是 descriptor DATA，不是直接 handler code。

`0x247C` 的 descriptor 语义已确认：

```text
+0      frame / payload end -> enemy+0x12
+4      long                -> enemy+0x30
+8      timer / flag
bit15 clear  -> inline next
bit15 set    -> explicit next ptr at +0x0A
next         -> enemy+0x2C
timer        -> enemy+0x34
payload tail -> enemy+0x6C / +0x6E ...
```

`frameEnd` 是 DATA / payload boundary，不是代码入口。

---

## 9. ACTIVE 的当前定义

所有 prospective 规则统一使用：

```text
enemy +0x70 U16
0 -> nonzero
```

定义为：

**ACTIVE-start convention**

它不是：

```text
exact hitbox onset
exact collision frame
exact damage frame
```

因此所有 `leadMs` 只能解释成：

```text
距离 +0x70 ACTIVE-start 还有多少时间
```

不能说“X ms 后一定打中玩家”。

---

## 10. 方法论重大演化：fixed-lag → same-cycle

### 旧方法：fixed lag

早期使用：

```text
50 / 100 / 150 / 250 / 500ms lag
```

在 ACTIVE 发生后回看历史 fingerprint。

问题：某些 enemy state 可以长时间持续、甚至跨攻击周期，所以 `T-100ms` 看到的状态不一定属于本次攻击，可能是上一周期残留。

结论：

```text
fixed-lag fingerprint
terminal state
```

现在只能用于 discovery / correlation，不能直接 production。

### 新方法：attack-zero same-cycle miner

从 WOF-041 开始：

```text
enemy+0x70 == 0
→ 建立该 enemy 当前 zero-attack cycle
→ 记录该 cycle 真实经历的状态
→ 同一个 enemy 后来 0->nonzero ACTIVE
→ 才把状态归因给这个 ACTIVE
```

重要输出：

```text
cyclePrecursorTop
cyclePrecursorFocus
```

记录：

```text
type
activeAttack
signature
cycleCount
firstLeadSamples
lastLeadSamples
targetSameRate
sideStableRate
```

这套 same-cycle forward-chain 证据已经成为新规则 discovery 的主方法。

---

## 11. Held state 修正：edge trigger → once-per-cycle level arm

WOF-042 中 T24 A5424 曾出现：

```text
rawMatch > 0
transitionEntry = 0
signals = 0
```

原因不是规则失败，而是采样器第一次看到 enemy 时状态已经 held，传统 `previous != match && current == match` entry detector 会漏掉。

WOF-043 改成：

```text
当前 zero->ACTIVE cycle 第一次看到该状态
→ arm 一次
→ cycle-id 去重
```

也就是 **once-per-zero-cycle level arm**。

改完后 T24 A5424 直接 21/21 strict。

因此 held-state 类规则以后默认优先考虑：

```text
level visibility + cycle-id 去重
```

---

## 12. 多房采集系统

### WOF-039 的问题

WOF-039 使用 45s join window，导致后来进入的 2P 房没有加入同 batch；另外 Worker 没有 `document`，不能直接负责总 JSON download。

### WOF-040 起的正确架构

同一条 JS 自动双模式：

```text
gstyphoon.js Worker -> ROOM-COLLECT
top                 -> TOP-FINALIZE
```

特性：

```text
最多 5 rooms
每房约 120s
无短 join window
1P / 2P / 3P 均可加入
per-room 边界保留
heartbeat / stale-interrupted 判断
完成后 top 合并并只下载 ONE JSON
```

用户流程：

```text
每个目标房间 Worker 运行同一条
→ 看到 ✅ room N complete
→ 所有目标房完成后切 top
→ 再运行同一条
→ 合并并下载 WOF-xxx_<batchId>.json
```

如果还有 live room 在采集，top 会拒绝提前 finalize。

WOF-040 后已真实验证 1P / 2P / 3P context 都能进入批次。

---

## 13. 最近主线 WOF-039 → WOF-045 的演化

### WOF-039

关键结果：

- T20 B0->B255：23/23 最终 A5136，target/side 23/23，lead 约 442–781ms。
- D867BA：6/6 forward A3232，跨 T9/T36。
- D8811E：3/3 forward A3232，在新 type T11 成立。
- T16 B4：26/26 <=40ms 进入 danger ACTIVE，但攻击 25×A6432 + 1×A4840。

因此 T16 被修正为：

```text
强 imminent danger
≠ exclusive A6432
```

### WOF-040

多房采集工作流修正并证明 1P/2P/3P 均可采。

规则：

- D8811E 24/24 -> A3232，跨 T37/T11/T34。
- D867BA 33/33 -> A3232，跨 T36/T9/T33。

### WOF-041

same-cycle miner 找到两条真正 T24 前驱：

```text
T24 S2/A2/B4 BODY7512 FE8AF46 NX8A6D0 V180001 TM3
→ A5440
≈49–60ms
```

```text
T24 S2/A2/B4 BODY7520 FE8AF6C NX8A6E4 V180001 TM4
→ A5424
≈50–70ms
```

### WOF-042 / WOF-043

T24 A5440 prospective：11/11 strict，正式 production-shadow。

T24 A5424 在 WOF-042 因 held-state 导致 transitionEntry=0；WOF-043 改 cycle-level arm 后：

```text
21/21 strict
21/21 A5424
target 21/21
side 21/21
lead 60.8–71.5ms
```

因此第二条 T24 也正式 production-shadow。

### WOF-044

原计划输出 `cyclePrecursorFocus.T23/T18`，但 exporter 有 bug：model 文本声称存在，实际 result 没有字段。

因此 WOF-044 不能用于 focused T23 结论；这不是“T23 没前驱”，只是 exporter 缺陷。

不过 global same-cycle top 找到两条强 T18 discovery：

```text
T18 S2/A2/B4 BODY7512 FE8BBB2 NX8B290 V180001 TM4
→ A5440
9/9 cycles
≈60.2–70.5ms
```

```text
T18 S2/A2/B4 BODY7520 FE8BBDE NX8B2A4 V180001 TM4
→ A5424
9/9 cycles
≈60.7–71.1ms
```

### WOF-045 — 当前最新完成批次

Batch：

```text
b-c45e8d2d-d9d
```

身份严格通过：

```text
copyId = WOF-045
project = WOF-AI-PRIVATE
version = wof-future-danger-multiroom-coordinator-v45
marker = === WOF FUTURE DANGER MULTIROOM COORDINATOR V45 JSON ===
readOnly = true
ramWrites = 0
```

批次：

```text
5 joined
5 complete
0 error
0 interrupted
59994 polls
202612 enemy samples
1025 ACTIVE edges
```

结果：

```text
137 signals
137 strict
0 jitter
0 real-late
0 hard miss
0 censored
0 retarget
```

玩家 context：

```text
0P = 119
1P = 42
2P = 1179
3P = 1088
```

WOF-045 同时修复 WOF-044 focused export bug：真实 JSON 已存在 `cyclePrecursorFocus.T23/T18`。有 T23 的房间输出 populated T23 focus；T18 房输出 populated T18 focus；没有对应 type 的房间为空数组属于正常。

---

## 14. 当前 Production Shadow 集合

### 14.1 T16 B4 — imminent danger

规则：

```text
T16_B4_DANGER_40
```

WOF-045：23/23 strict danger timing，lead 约 9–29ms，本轮均 A6432。

但历史真实反例：

```text
A4832
A4840
```

以及 ACTIVE 前 retarget。

因此 production 语义只能是：

```text
T16 B4 -> 马上有危险
```

禁止：

```text
T16 B4 -> 必然 A6432
warning entry target -> 最终 target lock
```

### 14.2 T20 B0->B255 -> A5136

规则：

```text
T20_5136_B0_TO_B255_1250
```

WOF-045：

```text
10/10 strict
A5136 10/10
target 10/10
side 10/10
lead 460.0–1020.1ms
```

级别：

```text
production-shadow-coarse
```

历史 lead 已覆盖约 0.4–1.2s，因此这是粗粒度 early warning，不是固定 countdown。

`1250ms` 只是一条 audit horizon，不是 causal timing boundary。

### 14.3 D867BA TM6 -> A3232

descriptor family：

```text
BODY2872
FE867BA
NX85ECE
V100000
P6C2784
A4
B2
state99 2/4
TM6
```

WOF-045：

```text
41/41 strict
A3232 41/41
target 41/41
side 41/41
all 5 rooms
```

当前批次 type：T9/T33；历史还验证过 T36。

级别：`production-shadow`。

### 14.4 D8811E TM6 -> A3232

```text
BODY2872
FE8811E
NX879E2
V100000
P6C2784
A4
B2
state99 2/4
TM6
```

WOF-045：

```text
14/14 strict
A3232 / target / side = 14/14
lead 99.0–109.8ms
```

历史 WOF-044 有一条 clean 209.5ms tail hit，最终仍 A3232。

因此 production-shadow 继续有效；135ms 只是 audit horizon，不是 causal boundary。

### 14.5 T24 BODY7512/TM3 -> A5440

```text
T24_5440_CYCLE_BODY7512_TM3_80
```

WOF-045：

```text
14/14 strict
A5440 / target / side = 14/14
lead 49.1–59.4ms
```

级别：`production-shadow`。

### 14.6 T24 BODY7520/TM4 -> A5424

```text
T24_5424_CYCLE_BODY7520_TM4_S24_LEVEL_90
```

WOF-045：

```text
15/15 strict
A5424 / target / side = 15/15
lead 59.9–71.0ms
```

级别：`production-shadow`。

这是典型 held-state / once-per-zero-cycle level trigger。

### 14.7 T18 BODY7512/TM4 -> A5440

```text
T18_5440_CYCLE_BODY7512_TM4_LEVEL_90
```

signature：

```text
S2/A2/B4|BODY7512|FE8BBB2|NX8B290|V180001|TM4|P6C0
```

WOF-044 discovery：9/9 same-cycle。

WOF-045 direct prospective：

```text
10/10 strict
A5440 / target / side = 10/10
lead 60.5–70.4ms
```

WOF-046 起升级：`production-shadow`。

### 14.8 T18 BODY7520/TM4 -> A5424

```text
T18_5424_CYCLE_BODY7520_TM4_LEVEL_90
```

signature：

```text
S2/A2/B4|BODY7520|FE8BBDE|NX8B2A4|V180001|TM4|P6C0
```

WOF-044 discovery：9/9 same-cycle。

WOF-045 direct prospective：

```text
10/10 strict
A5424 / target / side = 10/10
lead 61.5–70.3ms
```

WOF-046 起升级：`production-shadow`。

---

## 15. T23 当前状态

### 15.1 旧 BODY4920/B0 规则已退役

旧规则：

```text
T23_4792_BODY4920_B0_ENTRY_180
```

多轮有大量 T23 samples 和真实 A4792 ACTIVE，但 `rawMatch=0 / signals=0`。

结论：`retired-no-forward-coverage`，不要复活。

### 15.2 新 short-lead A4792 候选

WOF-045 focused same-cycle mining 找到：

```text
T23
S0/A6/B4|BODY4976|FE84868|NX83F20|V0|TM5|P6C0
→ A4792
```

当前 discovery：

```text
4/4 same-cycle -> A4792
target 4/4
side 4/4
first lead = 79.3, 79.5, 81.1, 89.4ms
last lead  = 59.5, 71.0, 78.5, 79.3ms
```

这是 WOF-046 的主要 direct-forward 目标。

新 rule：

```text
T23_4792_BODY4976_A6_B4_TM5_LEVEL_100
once-per-zero-cycle level arm
horizon = 100ms
tail = 300ms
```

### 15.3 另一个长 lead T23 分支

另一个 T23 房间存在：

```text
S2/A4/B0|BODY0|FE84A98|NX83D14|V100000|TM20|P6C0
```

当前仅约 2 cycles，first lead 约 1.4–2.9s。

样本过少，并可能是更长 preparation/phase 状态。

策略：继续 focused mining，不 promotion。

---

## 16. 证据等级

### Level 1 — retrospective / correlation

```text
fixed-lag fingerprint
terminal state
```

只能 discovery。

### Level 2 — same-cycle discovery

状态必须真实出现在当前 `attack==0` cycle，且同 enemy 后来发生 0->nonzero ACTIVE。

这是强候选，但仍不是 production。

### Level 3 — prospective validation

提前 arm，然后未来等待 ACTIVE，验证：

```text
attack
target
side
lead
hard miss
```

这是 production-shadow 升级的核心证据。

### Level 4 — multi-room / cross-type confirmation

跨不同房间、target、side、enemy type 后仍稳定，是当前最强 production 证据。

---

## 17. 已排除 / 降级 / 禁止复活的方向

除非出现强新证据，否则不要重启：

```text
broad T16 FAST <=100ms
broad T16 MID <=250ms
broad T30_FAST
```

不要把：

```text
absDx / 距离
```

解释成 hitbox / causal timing threshold。

不要把：

```text
enemy+0x70
```

叫 exact damage / hitbox onset。

不要把 warning entry target 当最终 target lock。

不要声称 T16 B4 100% exclusive A6432。

不要把：

```text
T20 1250ms
D867 220ms
D881 135ms
```

解释成 causal boundary。

不要复活旧 fixed-lag T24 BODY5424/5440。

不要复活 old T23 BODY4920/B0。

不要因为 2 cycles 就 promotion T23 long-lead branch。

历史已解决、不应重复投入：

```text
P1/P2/P3 identity
enemy+0x7E selector
player pointer table
dispatcher 44 incoming edges
descriptor consumer 0x247C
Focus Multiroom
0x0080F2
0x11C26 bridge 假设
A0+0x40/+0x44 target XY writer 假设
AD5A/low4
all-ROM arbitrary-even-address opcode scan
```

---

## 18. WinKawaks 并行 discovery 研究

Browser 主线之外允许独立 WinKawaks lanes：

```text
GEO-*     人物几何 / 坐标
EFIELD-*  enemy 0xE0 字段地图
RAWMINE-* raw diff / transition / offset ranking
```

完整协议见：

```text
PARALLEL_RESEARCH.md
COLLECTOR_ROUTING.md
```

本地 Collector repo：

```text
ouyong520/wof-winkawaks-bridge
```

支持：

```text
capture_raw_snapshot
capture_raw_burst
```

关键原则：

```text
WinKawaks = discovery
Browser/Web = production proof
```

WinKawaks offset 与 Browser/WASM offset 是不同命名空间；本地发现必须回到 Browser/Web prospective 环境验证后才能进入 production-shadow。

并行 GEO / EFIELD / RAWMINE lane 不得推进或改写当前 WOF mainline coordinator / validator / production rules。

---

## 19. 当前工程进度估计

这不是正式统计覆盖率，只是工程进度判断：

```text
底层 selector / dispatcher / descriptor     约 90%+
采集 / 多房 / prospective 验证基础设施      约 90%+
Future Danger 常见攻击覆盖                  约 65–70%
```

当前真正瓶颈已经不是“怎么读 RAM / dispatcher 怎么走”，而是：

```text
扩大不同 enemy type / attack branch 的可靠 Future Danger production 覆盖
```

目前主攻 T23，同时持续 audit 已有 production 集合。

---

## 20. 当前 GitHub 权威状态

```text
resume = wof-resume-dispatch-selector-v56
nextCopyId = WOF-046
nextScript = wof_future_danger_multiroom_coordinator_v46.js
nextMarker = === WOF FUTURE DANGER MULTIROOM COORDINATOR V46 JSON ===
embedded = WOF-046R / wof_future_danger_cycle_validator_v46r.js
```

WOF-046 目的：

```text
1. 直接 prospective 验证新的 T23 A4792 short-lead rule
2. 两条 T18 规则以 production-shadow 身份继续 audit
3. cyclePrecursorFocus.T23 继续寻找 alternate branch
4. T16 / T20 / D867 / D881 / T24 继续 production audit
```

WOF-046R 已加入：

```text
T23_4792_BODY4976_A6_B4_TM5_LEVEL_100
```

---

## 21. WOF-046 当前唯一 Browser 命令

最多 5 个 live `gstyphoon.js Worker` 各运行一次；每房约 120 秒。全部目标房完成后切到 `top`，再运行同一条，生成唯一总 JSON。

```js
// WOF-046
await fetch('https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/wof_future_danger_multiroom_coordinator_v46.js?x='+Date.now(),{cache:'no-store'}).then(r=>r.text()).then(s=>(0,eval)(s));
```

收到 WOF-046 JSON 后必须首先验证：

```text
copyId = WOF-046
project = WOF-AI-PRIVATE
version = wof-future-danger-multiroom-coordinator-v46
expectedMarker = === WOF FUTURE DANGER MULTIROOM COORDINATOR V46 JSON ===
readOnly = true
ramWrites = 0
```

重点检查：

```text
T23_4792_BODY4976_A6_B4_TM5_LEVEL_100
signals
strictHit
jitter / realLate / hardMiss
expectedAttackRate
targetSameRate
sideStableRate
leads
roomsWithSignal
```

并继续分析 `cyclePrecursorFocus.T23`。

---

## 22. 一句话当前前沿

**WOF 的 selector / dispatcher / descriptor 与 5 房采集链已经基本解决；方法已经从风险较高的 fixed-lag retrospective 转为 same-cycle attack-zero mining + prospective forward validation；T16/T20/D867/D881/T24 与新 T18 两条攻击规则已经形成 production-shadow；WOF-045 完成 137/137 strict 并修复 focused T23/T18 exporter；当前最前沿是新发现的 T23 `S0/A6/B4 BODY4976 FE84868 NX83F20 TM5 -> A4792` 4/4 same-cycle、约79–89ms 前驱，下一轮 WOF-046 正在等待直接 prospective 验证。**

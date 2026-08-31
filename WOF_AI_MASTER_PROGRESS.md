# WOF Future Danger AI — 项目总览 / 完整逻辑 / 当前进度

更新时间：2026-08-31  
仓库：`ouyong520/wof-ai-private`  
游戏：WOF / Warriors of Fate / 吞食天地II / 三国志II，World 921002 / MAME `wofr1`

> 长期项目总结。新对话建议读取顺序：`WOF_AI_HANDOFF.md` → `WOF_AI_CURRENT_FRONTIER.md` → 本文件；历史逆向细节看 `WOF_AI_REVERSE_PROCESS.md`。

---

## 1. 项目最终目标

目标不是自动操作，而是做 **Future Danger AI / 未来危险预测层**：

```text
ROM 固定 AI / 招式逻辑
+ 当前 Browser/MAME CPS RAM
+ enemy type / state / action / descriptor / position
+ 当前锁定 P1/P2/P3
+ 当前 zero-attack cycle
→ 在攻击 ACTIVE 之前提前识别危险
→ 预测 attack / target / side / lead
→ Future Danger Map / Safe Path
```

核心要求是减少误报：不能仅因为某玩家离敌人近就报警，必须尽可能基于敌人真实 AI target 与未来攻击分支。

当前研究已经从“攻击发生后解释过去”推进到：

```text
enemy+0x70 == 0
→ 识别当前攻击周期真实经历的前驱状态/序列
→ 提前 arm
→ 同 enemy 未来真正 +0x70 0->nonzero
→ prospective 验证 attack / target / side / lead / miss
```

---

## 2. 强制协作协议

1. GitHub 是项目权威状态。
2. 用户每轮只负责运行一条 Browser Console 命令并上传结果。
3. Assistant 负责分析、GitHub 更新、版本推进和下一轮设计。
4. 每次回传先严格校验：
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
5. 每轮只给 ONE Console command。
6. 命令使用唯一 `// WOF-xxx` Copy ID。
7. 不让用户手工改 JS；需要修改直接写 GitHub。
8. 多房数据保留 per-room 边界。
9. WinKawaks discovery 与 Browser production 严格隔离。

---

## 3. Browser/WASM 环境

```text
网页
→ cycgo.js
→ Web Worker: gstyphoon.js
→ gstyphoon.wasm
→ CPS RAM + live 68000 ROM
```

live ROM 已能恢复并缓存：
```js
self.__WOF_ROM_LOC_CACHE
```

旧 offline DB 与 live ROM 地址关系：
```text
live = offline + 0x34
```

不再重复 256MB 全 HEAP 暴力扫；优先复用 ROM cache / resume。

---

## 4. 已锁死 RAM 基础

玩家：
```text
P1 = 0xFFBE1C
P2 = 0xFFBEFC
P3 = 0xFFBFDC
stride = 0xE0
```

玩家 self-index：
```text
P1 +0x7C = 0
P2 +0x7C = 4
P3 +0x7C = 8
```

Enemy pool：
```text
base   = 0xFFC0BC
stride = 0xE0
slots  = 20
```

Enemy 当前 target 权威字段：
```text
enemy +0x7E
0 -> P1
4 -> P2
8 -> P3
```

最终预测输出必须实时重读 `+0x7E`。历史已经抓到 warning 后、ACTIVE 前发生 retarget 的真实样本，所以 entry target 不能冻结。

`enemy+0x6A` 只可作为 pointer-cache supporting evidence，不能代替 `+0x7E`。

---

## 5. P1/P2/P3 selector 已解决

玩家 pointer table：
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
→ player pointer table
→ A1 = selected P1/P2/P3 object
```

`0x010E72 MOVE.W A1,506(A5)` 保存 selected-player 地址低16位；多个 reader 可通过 `MOVEA.W` 还原完整 `FFFFBE1C/BEFC/BFDC`，说明它是 selected-player scratch/cache，但不是当前 dispatcher 的直接本地桥。

---

## 6. Dispatcher / state / action 已解决

共享 dispatcher：
```text
0x25B6
0x25C8
```

核心语义：
```text
enemy type
→ type-specific level2 table
→ 上游准备好的 D0 byte offset
→ final descriptor / handler
```

`wof_dispatch_incoming_edges.js` 已确认：
```text
directIncomingEdges = 44
edges25B6 = 4
edges25C8 = 40
fallthrough = 0
```

大量入口直接 `MOVEQ #0/#4/#8/#12... ,D0` 后进入 dispatcher，说明 D0 state offset 是上游 AI 状态机选择的。

Selector 附近两层状态分派已接通：
```text
enemy+0x99
→ state table
→ enemy+0x2A
→ action table
→ AI routine
→ dispatcher 0x25C8
→ descriptor
```

严格证明路线之一：
```text
state99=0
→ first block 0x010BBC
action2A=2
→ 0x010EC6
→ ...
→ dispatcher 0x25C8
```

这些底层结构已经解决，不再作为主线瓶颈。

---

## 7. Descriptor consumer 0x247C

`0x25C8` 选择的是 descriptor DATA，不是直接 code handler。

已确认：
```text
+0      frame/payload end -> enemy+0x12
+4      long              -> enemy+0x30
+8      timer/flag
bit15 clear -> inline next
bit15 set   -> explicit next ptr +0x0A
next        -> enemy+0x2C
timer       -> enemy+0x34
payload tail -> enemy+0x6C/+0x6E ...
```

`frameEnd` 是数据边界，不是代码地址。

---

## 8. ACTIVE 定义

所有 prospective 验证统一：

```text
enemy +0x70 U16
0 -> nonzero
```

称为：
**ACTIVE-start convention**

它不是：
```text
exact hitbox onset
exact damage frame
exact collision frame
```

因此 `leadMs` 只能解释成距离 `+0x70 ACTIVE-start` 的时间，不能说“X ms 后一定打中”。

---

## 9. 方法论演化：fixed-lag → same-cycle

早期使用 50/100/150/250/500ms fixed lag，在攻击发生后回看历史 fingerprint。

问题：一个 state 可能持续很久并跨攻击周期，所以 `T-100ms` 状态可能只是上一周期残留。

结论：
```text
fixed-lag fingerprint / terminal state
= discovery / correlation only
```

从 WOF-041 起使用 attack-zero same-cycle miner：
```text
enemy+0x70 == 0
→ 建立当前 zero-attack cycle
→ 记录真实经历状态
→ same enemy 未来 0->nonzero
→ 才归因给当前 ACTIVE
```

关键输出：
```text
cyclePrecursorTop
cyclePrecursorFocus
```

这成为新规则 discovery 主方法。

---

## 10. Held-state 修正：entry edge → cycle-level arm

WOF-042 的 T24 A5424 出现：
```text
rawMatch > 0
transitionEntry = 0
signals = 0
```

不是规则失败，而是采样器第一次看到对象时状态已经 held。

WOF-043 改为：
```text
当前 zero->ACTIVE cycle 第一次看到状态
→ arm once
→ cycle-id 去重
```

即 once-per-zero-cycle level arm。

之后 T24 A5424 直接 21/21 strict。held-state 类候选不能只依赖 entry edge。

---

## 11. 多房采集系统

WOF-039 的 45s join-window 与 Worker download 设计已退役。

WOF-040 起 coordinator 正确架构：
```text
gstyphoon.js Worker -> ROOM-COLLECT
top                 -> TOP-FINALIZE
```

特性：
```text
最多5房
每房约120s
无短 join window
1P/2P/3P 都可加入
per-room boundary
heartbeat / stale interrupted
top 最终只下载 ONE merged JSON
```

同一条 JS 在 Worker 与 top 使用。若 live room 仍采集中，top 会拒绝提前 finalize。

---

## 12. 最近实验演化 WOF-039 → WOF-045

### WOF-039
- T20 B0->B255：23/23 最终 A5136，target/side23/23，lead约442–781ms。
- D867BA：6/6 forward A3232，跨 T9/T36。
- D8811E：3/3 forward A3232，新 type T11。
- T16 B4：26/26 danger <=40ms，但 25×A6432 +1×A4840。

因此 T16 语义修正为：
```text
强 imminent danger
≠ exclusive A6432
```

### WOF-040
多房链修正，1P/2P/3P 均可采。D881 24/24、D867 33/33，descriptor-family 泛化加强。

### WOF-041
same-cycle 找到真正 T24 前驱：
```text
T24 S2/A2/B4 BODY7512 FE8AF46 NX8A6D0 V180001 TM3
→ A5440 ≈49–60ms
```
```text
T24 S2/A2/B4 BODY7520 FE8AF6C NX8A6E4 V180001 TM4
→ A5424 ≈50–70ms
```

### WOF-042 / WOF-043
- A5440 prospective 11/11 strict → production-shadow。
- A5424 因 held-state 漏 entry；cycle-level arm 后 21/21 strict → production-shadow。

### WOF-044
`cyclePrecursorFocus` exporter bug：model 说有，实际 result 没字段，因此不能把缺失解释为 T23 无前驱。

但 global same-cycle 找到 T18：
```text
BODY7512 FE8BBB2 NX8B290 TM4 -> A5440 9/9
BODY7520 FE8BBDE NX8B2A4 TM4 -> A5424 9/9
```

### WOF-045
Batch `b-c45e8d2d-d9d`：
```text
5/5 complete
202612 enemy samples
1025 ACTIVE edges
137 signals / 137 strict / 0 miss
```

真正修复 `cyclePrecursorFocus.T23/T18` export。

T18 direct prospective：
```text
T18 BODY7512/TM4 -> A5440 = 10/10 strict
T18 BODY7520/TM4 -> A5424 = 10/10 strict
```
两条均升级 production-shadow。

WOF-045 focused T23 还发现：
```text
S0/A6/B4|BODY4976|FE84868|NX83F20|V0|TM5|P6C0
→ A4792
4/4 same-cycle
first lead 79.3..89.4ms
```
于是 WOF-046 建 direct prospective rule。

---

## 13. WOF-046 — 当前最新完成证据

这次用户回传两个独立 WOF-046 batch。

### Batch A `b-65a0db92-24c`
```text
identity valid
readOnly=true
ramWrites=0
5 joined / 4 complete / 1 interrupted / 0 error
47998 polls
181961 enemy samples
989 ACTIVE edges
294 signals / 294 strict / 0 hard miss
```

完成房主要为 2P；interrupted 房为 3P。

### Batch B `b-b1f1a5a3-92c`
```text
identity valid
readOnly=true
ramWrites=0
4 joined / 4 complete / 0 interrupted / 0 error
48000 polls
168660 enemy samples
958 ACTIVE edges
110 signals
108 strict +1 jitter +1 real-late
0 hard miss
```

player histogram：
```text
[0P0,1P490,2P489,3P983]
```

两批所有 completed embedded WOF-046R identity validations 均通过。

---

## 14. 当前 Production Shadow 集合

以下为两个 WOF-046 batch 合并 audit。

### T16 B4 — imminent danger
```text
225/225 danger tail hits
224 strict +1 jitter
A6432 = 223
A4840 = 2
target/side = 225/225
lead = 8.5..40.9ms
```

结论：
```text
T16 B4 -> 马上危险
```
禁止：
```text
T16 B4 -> 必然 A6432
entry target -> final lock
```

### T20 B0->B255 -> A5136
```text
14/14 strict
A5136/target/side = 14/14
lead = 460.8..700.4ms
```
级别：`production-shadow-coarse`。

历史 lead 可到约1.2s，1250ms 只是 audit horizon，不是 countdown。

### D867BA TM6 -> A3232
```text
16/16 strict
A3232/target/side = 16/16
lead = 99.1..119.6ms
```
级别：`production-shadow`。历史已跨 T9/T33/T36 等 type。

### D8811E TM6 -> A3232
```text
21/21 eventual A3232/target/side
20 strict
1 real-late = 209.5ms
0 miss
```
级别：`production-shadow`。135ms 只是 audit horizon。

### T24 BODY7512/TM3 -> A5440
```text
28/28 strict
A5440/target/side 28/28
lead48.5..68.5ms
```

### T24 BODY7520/TM4 -> A5424
```text
34/34 strict
A5424/target/side34/34
lead59.9..71.8ms
```

### T18 BODY7512/TM4 -> A5440
```text
33/33 strict
A5440/target/side33/33
lead59.1..78.5ms
```

### T18 BODY7520/TM4 -> A5424
```text
33/33 strict
A5424/target/side33/33
lead58.2..71.3ms
```

当前这些 production 规则没有出现 hard miss。

---

## 15. T23 当前真实状态

### 15.1 旧 BODY4920/B0
旧：
```text
T23_4792_BODY4920_B0_ENTRY_180
```
多轮 T23 与 A4792 真实覆盖下仍 rawMatch0，继续 `retired-no-forward-coverage`。

### 15.2 WOF-045 short candidate
```text
T23_4792_BODY4976_A6_B4_TM5_LEVEL_100
S0/A6/B4|BODY4976|FE84868|NX83F20|V0|TM5|P6C0
```

两个 WOF-046 batch 都：
```text
rawMatch = 0
signals = 0
```

这叫 **zero coverage，不是 forward failure**。

特别是 Batch B：
```text
T23 samples = 7379
T23 A4792 ACTIVE = 12
```
说明 T23/A4792 确实出现，但走了其它状态分支。

### 15.3 为什么不能继续用“单一 T23 fingerprint”硬猜

WOF-046 focused data 证明常见 single-state 会跨 attack。

例：
```text
S2/A4/B0|BODY0|FE84A98|NX83D14|V100000|TM20|P6C0
```
同一 signature 在当前数据可通往：
```text
A4792 = 4 cycles
A4920 = 2 cycles
A5848 = 1 cycle
```

而 A4792 long branch 还出现：
```text
targetSame = 0/4
```
说明这个长 preparation state 连 target 都可能在后续变化，不适合作 target-specific production warning。

另一状态：
```text
S0/A4/B2|BODY4936|FE84060|NX83C60|VFFFF|TM1|P6C4944
```
同样同时出现在 A4792 与 A4920。

因此当前 T23 研究问题已经升级为：

```text
不是找“哪个单一 state = A4792”
而是找“哪条 ordered transition sequence 能区分 A4792 / A4920 / A5848”
```

---

## 16. WOF-047 的方法升级：T23 ordered cycle traces

WOF-047R 新增：
```text
t23CycleTraces
```

每个房间记录最多120个 resolved T23 zero->ACTIVE cycle。

每 cycle 保存：
```text
activeAttack
cycleDuration
startedMidCycle
targetStart / targetAtActive
sideStart / sideAtActive
retargets
最多48个 distinct states，按真实时间顺序
每 state firstLeadMs / lastLeadMs
tail1 / tail2 / tail3
finalPreActiveSignature
```

目的：
1. 对 A4792 / A4920 / A5848 的真实 pre-ACTIVE 路径做 sequence 对齐。
2. 自动寻找 attack-specific transition pair / triple。
3. 找到稳定 sequence 后，下一版再写 prospective sequence validator。

`T23_4792_BODY4976_A6_B4_TM5_LEVEL_100` 仍保留 audit；若对应 branch 再出现，可以继续直接 forward。

重要：
```text
t23CycleTraces = discovery evidence
```
不能直接 production。

---

## 17. 证据等级

### Level 1
retrospective fixed-lag / terminal correlation：只 discovery。

### Level 2
same-cycle discovery：状态真实出现在当前 attack==0 cycle，且 same enemy 后来 ACTIVE。

### Level 3
prospective validation：先 arm，再等待未来 ACTIVE，验证 attack/target/side/lead/miss。

### Level 4
multi-room / cross-type confirmation：跨场景仍稳定，最强 production evidence。

对于 T23 目前还新增一个实际要求：**如果单一 state 跨多个 attack branch，就必须继续到 sequence/transition discriminator，不能 promotion。**

---

## 18. 禁止复活 / 禁止误判

不要重启：
```text
broad T16 FAST <=100ms
broad T16 MID <=250ms
broad T30_FAST
```

不要：
```text
absDx/距离 = hitbox / causal timing law
enemy+0x70 = exact hitbox/damage onset
warning entry target = final target lock
T16 B4 = exclusive A6432
T20 1250ms / D867220 / D881135 = causal boundary
```

不要复活：
```text
old fixed-lag T24 BODY5424/5440
old T23 BODY4920/B0
```

不要把 WOF-046 short T23 rawMatch0 称为失败；它没有覆盖。

不要把当前 attack-ambiguous T23 single-state 直接 promotion。

历史已解决、不再重复投入：
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

## 19. WinKawaks 并行 discovery lanes

```text
GEO-*     人物几何/坐标
EFIELD-*  enemy 0xE0 字段地图
RAWMINE-* raw diff/transition/offset ranking
```

入口：
```text
PARALLEL_RESEARCH.md
COLLECTOR_ROUTING.md
ouyong520/wof-winkawaks-bridge/docs/COLLECTOR_V1_CONTRACT.md
```

原则：
```text
WinKawaks = discovery
Browser/Web = production proof
```

并行 lane 不得修改/推进 Browser mainline coordinator/validator/production rules。

---

## 20. 当前工程进度

工程估计，不是正式覆盖率：

```text
底层 selector / dispatcher / descriptor    约90%+
采集 / 多房 / prospective 基础设施         约90%+
Future Danger 常见攻击 coverage            约65–70%
```

瓶颈已经从“怎么读 RAM”转为：
```text
扩大不同 enemy type / attack branch 的可靠 production coverage
```

当前主攻 T23 sequence discriminator。

---

## 21. 当前 GitHub 权威状态

```text
resume = wof-resume-dispatch-selector-v57
nextCopyId = WOF-047
nextScript = wof_future_danger_multiroom_coordinator_v47.js
nextMarker = === WOF FUTURE DANGER MULTIROOM COORDINATOR V47 JSON ===
embedded = WOF-047R / wof_future_danger_cycle_validator_v47r.js
```

详细 WOF-046 两批分析：
```text
reports/WOF-046_ANALYSIS.md
```

WOF-047 使用 fresh IndexedDB v9。

---

## 22. WOF-047 当前唯一 Browser 命令

最多5个 live `gstyphoon.js Worker` 各运行一次；每房约120秒。全部目标房完成后切 `top`，再运行同一条生成唯一 JSON。

```js
// WOF-047
await fetch('https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/wof_future_danger_multiroom_coordinator_v47.js?x='+Date.now(),{cache:'no-store'}).then(r=>r.text()).then(s=>(0,eval)(s));
```

收到 WOF-047 后先校验：
```text
copyId = WOF-047
project = WOF-AI-PRIVATE
version = wof-future-danger-multiroom-coordinator-v47
expectedMarker = === WOF FUTURE DANGER MULTIROOM COORDINATOR V47 JSON ===
readOnly = true
ramWrites = 0
```

重点分析：
```text
t23CycleTraces
t23TraceDiagnostics
```

将 A4792 / A4920 / A5848 traces 按最后若干 distinct states 对齐，rank attack-specific pair/triple，并决定下一版 prospective sequence rule。

---

## 23. 一句话当前前沿

**WOF selector/dispatcher/descriptor 与多房采集链已经基本解决；现有 T16/T20/D867/D881/T24/T18 production-shadow 在两个 WOF-046 batch 继续无 hard miss；WOF-045 的 T23 short candidate 在 WOF-046 没有覆盖，而新的 focused 数据证明常见 T23 单一 state 可同时通往 A4792/A4920/A5848，因此主线已从“单 fingerprint”升级到“ordered same-cycle transition sequence”研究，WOF-047 将直接采集每个 T23 zero->ACTIVE 周期的完整有序 state trace，为下一版 attack-specific prospective sequence validator 提供证据。**

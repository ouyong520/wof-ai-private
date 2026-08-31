# WOF Future Danger AI — 项目总览 / 完整逻辑 / 当前进度

更新时间：2026-09-01  
仓库：`ouyong520/wof-ai-private`  
游戏：WOF / Warriors of Fate / 吞食天地II / 三国志II，World 921002 / MAME `wofr1`

> 长期项目总结。新对话建议读取：`WOF_AI_HANDOFF.md` → `WOF_AI_CURRENT_FRONTIER.md` → 本文件；历史静态逆向细节见 `WOF_AI_REVERSE_PROCESS.md`。

---

## 1. 最终目标

项目不是 autoplay，而是 **Future Danger AI / 未来危险预测层**：

```text
ROM AI / 招式逻辑
+ Browser/MAME live CPS RAM
+ enemy type/state/action/descriptor/position
+ 当前 P1/P2/P3 target
+ 当前 zero-attack cycle
→ 在 ACTIVE 前预测未来危险
→ attack / target / side / lead
→ Future Danger Map / Safe Path
```

核心要求是降低误报：预测必须尽量跟随敌人真实 AI target 与攻击分支，而不是简单按“谁最近”报警。

---

## 2. 强制协作协议

1. GitHub 是权威状态。
2. 用户每轮只运行 ONE 条 Browser Console 命令并上传结果。
3. Assistant 负责分析、GitHub 更新、版本推进、下一轮设计。
4. 每次结果先严格校验：
```text
copyId
project
version
marker / expectedMarker
readOnly
ramWrites
```
要求：`project=WOF-AI-PRIVATE`、`readOnly=true`、`ramWrites=0`。
5. 身份不对不算当前证据。
6. 多房保留 per-room 边界。
7. WinKawaks discovery 与 Browser production 严格隔离。

---

## 3. 已锁死 Browser RAM / selector 基础

玩家：
```text
P1 = 0xFFBE1C
P2 = 0xFFBEFC
P3 = 0xFFBFDC
stride = 0xE0
```

player self-index：
```text
P1+0x7C=0
P2+0x7C=4
P3+0x7C=8
```

Enemy pool：
```text
base = 0xFFC0BC
stride = 0xE0
slots = 20
```

Enemy 当前 target 权威字段：
```text
enemy+0x7E
0 -> P1
4 -> P2
8 -> P3
```
最终输出必须实时重读 `+0x7E`；历史已抓到 warning 后、ACTIVE 前 retarget，所以 entry target 不能冻结。

玩家 pointer table：
```text
0x010CF8=P1
0x010CFC=P2
0x010D00=P3
```

关键 selector：
```text
0x010E66 MOVE.W 126(A0),D1
0x010E6A LEA 0x010CF8,A1
0x010E6E MOVE.L 0(A1,D1.W),A1
```

=> `enemy+0x7E -> 0/4/8 -> P1/P2/P3 object` 已严格解决。

---

## 4. Dispatcher / state / descriptor 已解决

共享 dispatcher：`0x25B6 / 0x25C8`。

`wof_dispatch_incoming_edges.js` 已确认：
```text
directIncomingEdges=44
edges25B6=4
edges25C8=40
fallthrough=0
```

上游状态链：
```text
enemy+0x99
→ state table
→ enemy+0x2A
→ action table
→ AI routine
→ dispatcher0x25C8
→ descriptor
```

严格证明路线之一：
```text
state99=0
action2A=2
→ 0x010EC6
→ ...
→ 0x25C8
```

Descriptor consumer `0x247C` 已确认：
```text
+0 frame/payload end -> enemy+0x12
+4 long              -> enemy+0x30
+8 timer/flag
next                 -> enemy+0x2C
timer                -> enemy+0x34
payload tail         -> enemy+0x6C/+0x6E...
```
`frameEnd` 是 DATA boundary，不是代码地址。

这些底层不再是主线瓶颈。

---

## 5. ACTIVE 定义

当前所有 prospective validator 统一使用：
```text
enemy+0x70 U16
0 -> nonzero
```
称为 **ACTIVE-start convention**。

它不是 exact hitbox / collision / damage onset。`leadMs` 只能表示距离 `+0x70 ACTIVE-start` 的时间。

---

## 6. 方法论演化

### fixed-lag 已降级
早期在 ACTIVE 后回看50/100/150/250/500ms fingerprint。后来发现状态可能持续并跨 cycle，因此 fixed-lag 只能 discovery/correlation，不能直接 production。

### same-cycle miner
从 WOF-041 起：
```text
attack==0
→ 建当前 zero-attack cycle
→ 记录当前 cycle 真实经历状态
→ same enemy 未来0->nonzero
→ 才归因给该 ACTIVE
```
关键输出：`cyclePrecursorTop / cyclePrecursorFocus`。

### held-state level arm
WOF-042 T24 A5424 证明只看 entry edge 会漏 held state。WOF-043 改成：
```text
当前 zero->ACTIVE cycle 第一次看见状态
→ arm once
→ cycle-id 去重
```
之后 T24 A5424 21/21 strict。

### ordered sequence
WOF-046 进一步证明 T23 常见 single-state 会跨多个 attack，因此 WOF-047 开始采 `t23CycleTraces`，从单 fingerprint 升级到 ordered transition sequence。

---

## 7. 多房采集基础设施

WOF-040 起 dual-mode coordinator 已稳定：
```text
gstyphoon.js Worker = collect (~120s/room)
top                 = finalize + one merged JSON
max rooms = 5
no short join window
1P/2P/3P allowed
```
同一条 JS 在 Worker 和 top 使用。top 遇到仍 live 的采集房会拒绝提前 finalize。

---

## 8. 最近主线演化 WOF-039 → WOF-047

### WOF-039
- T20 B0->B255：23/23 最终 A5136，target/side23/23，lead约442–781ms。
- D867 6/6 A3232，跨 T9/T36。
- D881 3/3 A3232，新 T11。
- T16 26/26 danger<=40ms，但有 A4840 反例，因此只能是 imminent danger，不是 exclusive A6432。

### WOF-040
多房链修正，1P/2P/3P 均可采；D867/D881 跨 type 泛化继续增强。

### WOF-041
same-cycle 找到真正 T24 前驱：
```text
T24 BODY7512 FE8AF46 NX8A6D0 TM3 -> A5440 ≈49–60ms
T24 BODY7520 FE8AF6C NX8A6E4 TM4 -> A5424 ≈50–70ms
```

### WOF-042 / 043
- T24 A5440 prospective 11/11 -> production-shadow。
- A5424 用 cycle-level arm 后21/21 -> production-shadow。

### WOF-044 / 045
WOF-044 focused exporter 有 bug；WOF-045 修复 `cyclePrecursorFocus.T23/T18`。

T18：
```text
BODY7512 FE8BBB2 NX8B290 TM4 -> A5440
BODY7520 FE8BBDE NX8B2A4 TM4 -> A5424
```
WOF-044 discovery各9/9，WOF-045 direct prospective各10/10，因此两条升级 production-shadow。

WOF-045 T23 发现 short candidate：
```text
S0/A6/B4|BODY4976|FE84868|NX83F20|V0|TM5|P6C0
-> A4792
4/4 same-cycle
first lead79.3..89.4ms
```

### WOF-046
两批结果均有效。合并：
```text
T16 225/225 danger tail hits
T20 14/14 A5136
D867 16/16 A3232
D881 21/21 eventual A3232
T24 A5440 28/28
T24 A5424 34/34
T18 A5440 33/33
T18 A5424 33/33
```
全部 production audit 0 hard miss。

但 WOF-045 short T23 candidate 在两批 WOF-046 都 rawMatch0/signals0：**zero coverage，不是 failure**。

更重要：focused 数据发现同一 T23 state 可通往 A4792/A4920/A5848，因此单 fingerprint 不足。

---

## 9. WOF-047 — 最新完成证据

Batch：`b-fbbbc59d-cea`

```text
copyId=WOF-047
project=WOF-AI-PRIVATE
version=coordinator-v47
readOnly=true
ramWrites=0
3 joined / 3 complete
0 error / 0 interrupted
35996 polls
113581 enemy samples
644 ACTIVE edges
144 signals =143 strict +1 jitter
0 hard miss / 0 censored
player histogram [0,0,579,902]
```
全部3个 embedded WOF-047R identity validations 通过。

### production audit
```text
T16: 94/94 danger tail hits =93 strict+1 jitter
      A6432=93,A4832=1,target/side94/94,lead9.0..40.5ms
T20: 0 coverage，本轮不作负判断
D867: 23/23 strict A3232/target/side, lead98.8..119.5ms
D881: 19/19 strict A3232/target/side, lead99.4..120.4ms
T24 A5440: 3/3 strict
T24 A5424: 3/3 strict
T18 A5440: 1/1 strict
T18 A5424: 1/1 strict
```

---

## 10. 当前 Production Shadow 集合

### T16 B4
`T16_B4_DANGER_40`

语义：**马上危险**。历史有 A4832/A4840 与 retarget，禁止解释为100% A6432或 frozen target。

### T20 B0->B255
`T20_5136_B0_TO_B255_1250`

`production-shadow-coarse`，预测 A5136 的粗粒度 early warning。1250ms 只是 audit horizon，不是 countdown。

### D867BA TM6
-> A3232，跨 T9/T33/T36 等，production-shadow。

### D8811E TM6
-> A3232，production-shadow。135ms 只是 audit horizon；历史存在 clean 209.5ms late hit。

### T24
```text
BODY7512/TM3 -> A5440
BODY7520/TM4 -> A5424
```
均 production-shadow。

### T18
```text
BODY7512/TM4 -> A5440
BODY7520/TM4 -> A5424
```
均 production-shadow。

---

## 11. T23 当前真实状态

旧 `T23_4792_BODY4920_B0_ENTRY_180` 已 retired。

WOF-045 short candidate `BODY4976/A6/B4/TM5 -> A4792` 在 WOF-046、WOF-047 都没有新 coverage，因此仍只是 branch-specific discovery，不算 forward failure。

### WOF-047 ordered traces
唯一有 T23 的 room 产生8个 resolved zero->ACTIVE cycles：
```text
A4792=3
A4920=3
A5888=2
0 dropped
```

A4920 final branches至少包括：
```text
S0/A4/B0 BODY4976 FE84868 NX83c56 V1
S0/A6/B4 BODY4976 FE84868 NX83f20 V0
S0/A4/B10 BODY4952 FE84102 NX83c7e V0
```

A5888 final branches：
```text
S2/A6/B4 BODY4936 FE84060 NX83c60 Vffff
S0/A6/B4 BODY4936 FE84060 NX83c60 Vffff
```

一个关键 A5888 tail3：
```text
S0/A8/B2 BODY4936
-> S0/A2/B0 BODY4936
-> S0/A6/B4 BODY4936
-> A5888
```
但 `S0/A8/B2 BODY4936` 本身也出现在 A4792，因此**order 比单 state 更重要**。

A4792 三个 cycle 自己也有不同尾部：
1. BODY4952/FE84140 family：`A6/B0 -> A6/B4 -> A2/B0`。
2. terminal `S0/A8/B2 BODY4936 FE84060...`。
3. `S2/A4/B10 BODY4952 FE841b4 -> S2/A2/B0 -> S2/A8/B2 BODY4936`。

结论：当前没有 universal A4792 short sequence；不能 promotion。

---

## 12. WOF-047 tracer correction

WOF-047 有一个仅影响 trace instrumentation 的小问题：如果 target 在 ACTIVE 0->nonzero 的同一 poll 改变，`targetStable=false` 正确，但旧 `retargets[]` 可能为空，因为 observer 只在 attack==0 时跑。

WOF-048R 已修：resolve cycle 前若 `lastTarget7E != targetAtActive7E`，追加：
```text
retargets[].atActiveEdge = true
```

这不改变 production rules，只修 trace 记录完整性。

---

## 13. WOF-048 方法

WOF-048 继续 WOF-047 ordered traces，并新增 `t23SequenceSummary`。

对每个 T23 trace：
- 把 timer 归一化成 `TM*`，减少同一结构仅因 timer 不同被拆碎。
- 按 activeAttack 聚合：
```text
finalFamilyTop
tail2FamilyTop
tail3FamilyTop
transitionTop
tripleTop
```
- 同时继续保留原始 ordered states / lead / target / side。

目标：先用更多 T23 cycle 找到重复、attack-specific 的 pair/triple，再做下一版 prospective sequence validator。

`t23SequenceSummary` 仍是 discovery evidence，不直接 production。

---

## 14. 证据等级

1. retrospective fixed-lag / terminal correlation：discovery only。
2. same-cycle discovery：当前 attack==0 cycle 内真实出现，并在同 enemy 后续 ACTIVE。
3. prospective validation：提前 arm，未来验证 attack/target/side/lead/miss。
4. multi-room / cross-type confirmation：当前最强 production evidence。

对于 T23：single-state 跨 attack 时必须继续到 ordered sequence discriminator。

---

## 15. 禁止复活 / 禁止误判

不要重启：
```text
broad T16 FAST/MID
broad T30_FAST
```

不要把：
```text
absDx = causal timing/hitbox
enemy+0x70 = exact hitbox/damage onset
warning entry target = final lock
T16 B4 = exclusive A6432
T20 1250 / D867220 / D881135 = causal boundary
```

不要复活：
```text
old fixed-lag T24 BODY5424/5440
old T23 BODY4920/B0
```

不要把 zero coverage 当 forward failure。
不要用当前仅8条 T23 ordered trace 就 promotion。

历史已解决、不再重复投入：P1/P2/P3 identity、+0x7E selector、player table、dispatcher44、0x247C consumer、Focus Multiroom、0x0080F2、0x11C26 bridge、A0+0x40/+0x44 targetXY、AD5A/low4、全ROM arbitrary-even opcode scan。

---

## 16. WinKawaks 并行 discovery lanes

```text
GEO-*     人物几何/坐标
EFIELD-*  enemy 0xE0 字段地图
RAWMINE-* raw diff/transition/offset ranking
```
入口：`PARALLEL_RESEARCH.md`、`COLLECTOR_ROUTING.md`、`ouyong520/wof-winkawaks-bridge/docs/COLLECTOR_V1_CONTRACT.md`。

原则：
```text
WinKawaks = discovery
Browser/Web = production proof
```
并行 lane 不得修改 mainline coordinator/validator/production rules。

---

## 17. 工程进度估计

不是正式覆盖率：
```text
底层 selector/dispatcher/descriptor       约90%+
多房/采集/prospective infrastructure      约90%+
Future Danger 常见攻击 coverage           约65–70%
```
当前瓶颈是扩大不同 enemy type / attack branch 的可靠 production coverage，主攻 T23 sequence discriminator。

---

## 18. 当前 GitHub 权威状态

```text
resume = wof-resume-dispatch-selector-v58
nextCopyId = WOF-048
nextScript = wof_future_danger_multiroom_coordinator_v48.js
nextMarker = === WOF FUTURE DANGER MULTIROOM COORDINATOR V48 JSON ===
embedded = WOF-048R / wof_future_danger_cycle_validator_v48r.js
```

详细最新分析：
```text
reports/WOF-046_ANALYSIS.md
reports/WOF-047_ANALYSIS.md
```

WOF-048 fresh IndexedDB v10。

---

## 19. 当前唯一 Browser 命令

最多5个 live `gstyphoon.js Worker` 各运行一次；每房约120秒。全部目标房完成后切 `top` 再运行同一条。

```js
// WOF-048
await fetch('https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/wof_future_danger_multiroom_coordinator_v48.js?x='+Date.now(),{cache:'no-store'}).then(r=>r.text()).then(s=>(0,eval)(s));
```

收到 WOF-048 后先校验 identity/readOnly/ramWrites，然后重点分析：
```text
t23CycleTraces
t23TraceDiagnostics
t23SequenceSummary
```
并按 A4792/A4920/A5888 对比 timer-normalized final/tail2/tail3/pair/triple，寻找可进入下一版 prospective sequence validator 的 discriminator。

---

## 20. 一句话当前前沿

**WOF 的 selector/dispatcher/descriptor 与多房 prospective 基础设施已经基本解决；T16/T20/D867/D881/T24/T18 production-shadow 继续稳定；T23 已从 ambiguous single-state 研究升级为 ordered same-cycle sequence discrimination。WOF-047 首次拿到8条完整 T23 attack-labelled traces（A4792=3/A4920=3/A5888=2），证明 late sequence 比单 state 更有判别力，但 A4792 本身也存在多分支，尚不足 promotion。WOF-048 将继续扩大 T23 traces、修 active-edge retarget 记录，并自动聚合 timer-normalized tail/pair/triple，为下一版 prospective sequence validator 选出真正 attack-specific 分叉序列。**

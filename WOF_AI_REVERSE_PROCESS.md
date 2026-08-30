# WOF AI 逆向过程复盘 / 可复用方法

更新时间：2026-08-31（UTC+8）

> 本文件记录 **WOF Future Danger AI 项目的逆向过程、证据链、失败路线和可复用方法**。
>
> 它不是最新运行状态 handoff 的替代品。新对话仍应先读 `WOF_AI_HANDOFF.md`；本文件用于回答“我们是怎么逆到这里的、哪些坑已经踩过、以后逆其它 AI 分支应该怎么做”。

---

## 1. 为什么要单独记录“过程”

这个项目真正困难的地方不是某一个地址，而是从一个几乎完全黑箱的网页模拟器环境，逐步建立出：

```text
浏览器 Worker / live ROM
→ enemy RAM 结构
→ enemy type dispatch
→ 二级 state/handler table
→ D0 state offset
→ dispatcher
→ incoming CFG edges
→ 上游 selector
→ P1/P2/P3 player table
→ selected-player 数据流
```

过程中出现过很多“非常像答案”的假候选。如果只保存最后地址，以后逆 Boss、projectile、攻击起手或其它状态分支时，很容易重新踩一遍旧坑。

因此本文件重点记录：

1. 哪些事实已经被多种证据确认。
2. 哪些路线已经明确排除。
3. 为什么当时要换方向。
4. 哪些扫描/分析方法可以复用。
5. 68000 静态解码中有哪些特别危险的误判。

---

# 2. 项目目标与逆向问题

游戏：**Warriors of Fate / 吞食天地II / 三国志II**，当前确认 ROM 为 **WOF World 921002 / MAME `wofr1`**。

最终项目不是单纯做作弊或自动按键，而是 Future Danger AI：

```text
敌人当前 AI 决策
+ 当前 target/focus
+ state / handler
+ attack startup / active / projectile
+ 玩家和敌人位置
↓
预测未来约 0~1000ms
↓
判断真正会威胁 P1/P2/P3 中谁
↓
计算安全方向 / Safe Path
↓
HUD 提示
```

其中最难的核心问题之一一直是：

```text
“这个敌人现在真正准备攻击 P1、P2、P3 中的谁？”
```

如果这个问题无法解决，仅靠“最近玩家”“敌人移动方向”会产生大量误报。

---

# 3. 已确认的运行环境和固定玩家对象

网页实际运行架构：

```text
网页
↓
cycgo.js
↓
Web Worker: gstyphoon.js
↓
gstyphoon.wasm
↓
CPS RAM + live 68000 ROM
```

逆向/测试代码主要在 DevTools 的 **`gstyphoon.js` Console** 执行。

当前版本固定玩家对象：

```text
P1 = 0xFFBE1C
P2 = 0xFFBEFC
P3 = 0xFFBFDC
stride = 0xE0
```

因此：

```text
P2 = P1 + 0xE0
P3 = P2 + 0xE0
```

Enemy pool 已确认大约：

```text
base   = 0xFFC0BC
stride = 0xE0
slots  ≈ 20
```

注意：浏览器/WASM HEAP 的宿主物理位置可能每次不同，但游戏内部 68000 地址（例如 `0xFFBE1C`）在当前 ROM 版本中是固定的。

---

# 4. 第一阶段：从运行时 RAM 猜 target 字段

最早的思路很自然：如果怪物有“当前目标玩家”，它可能直接保存在 enemy `0xE0` 结构某个 offset 中。

因此做过 Focus Multiroom、动态字段相关性、player-handle、运动预测等大量测试。

重点候选曾包括：

```text
+0x3A
+0x68
+0x6A
+0x9C
```

### 4.1 `+0x3A / +0x6A`

它们经常出现“像玩家 handle”的数值，因此一度非常可疑。

动态 handle probe 后发现：

- `+0x3A` 很多样本确实等于某个玩家相关值。
- `+0x6A` 也有明显相关性。
- 但当把它们和敌人未来运动方向/追击方向比较时，持续预测能力很差。
- switch 后也不能稳定预测下一段追击。

结论：

```text
+0x3A / +0x6A 更像碰撞、交互、攻击接触或短期引用
≠ 稳定 target
```

### 4.2 `+0x9C`

统计上看起来 switch 很漂亮，但后来发现和位置/X 变化强相关，是典型混杂变量。

结论：假 target。

### 4.3 这一阶段真正得到的价值

虽然没有找到简单 `enemy+offset = P1/P2/P3`，但这是重要结果：

> **没有证据支持 enemy E0 结构中存在一个简单、长期保存的 target pointer 字段。**

这直接推动项目从“继续收更多房间统计”转向 **ROM AI 控制流逆向**。

因此：以后不要重新无休止扫描 E0 结构找一个神奇 target offset，除非新的 ROM 代码明确指出某字段。

---

# 5. 第二阶段：定位 live ROM 和地址映射

通过 Worker HEAP 扫描，成功定位网页当前运行的 live 68000 ROM。

关键事实：

```text
layout = swap16
```

并发现当前 live ROM 相对旧离线 DB 地址存在统一偏移：

```text
liveAddress = offlineAddress + 0x34
```

即：

```text
offlineDelta = +0x34
```

后续必须遵守：

- 在网页运行 ROM 上分析：用 **live 地址**。
- 只有和旧 `future_attack_db_v3.json` 对照时才减 `0x34`。

### 性能教训

早期同步扫整个超大 HEAP 会造成明显卡顿和 GC 压力。

后续固定采用：

```text
分片扫描
+ 缓存 self.__WOF_ROM_LOC_CACHE
+ 新 Worker 时自恢复
```

不要重新引入一次性同步暴力扫描全部 HEAP。

---

# 6. 第三阶段：最重要的误判之一——0x0080F2

P1/P2/P3 ROM 引用扫描曾找到多个 player-ref cluster，其中：

```text
live 0x0080F2
offline 0x0080BE
```

同时包含：

```text
P1 ref ×1
P2 ref ×1
P3 ref ×1
CMP-family ≈ 8
```

看起来非常像 multiplayer target selector，因此一度成为主候选。

但“看起来像”不够，必须证明 enemy AI 真正能到达它。

### 6.1 第一次 direct type trace

从旧的 47 type entry 出发追 direct JSR/BSR：

```text
directTypePaths = 0
```

这已经是警告，但当时还不能彻底排除，因为随后发现我们对 type table 的语义理解还不完整。

### 6.2 真正确认排除

后来重新解析 `0x25DC` 后，得到真正的第二级 handler roots，再从这些 roots 做 direct-call reachability：

```text
level2Pointers = 625
uniqueRealHandlers = 348
decodedRoutines ≈ 356
handlerPaths → 0x0080F2 = 0
typesReaching80F2 = 0
```

至此可以正式结论：

```text
0x0080F2 不是当前 enemy target selector 主线
```

它可能仍然是其它多人逻辑 helper，但不要再把它作为 enemy selector 主线复活。

### 可复用教训

一个函数同时引用 P1/P2/P3 + CMP 很诱人，但必须问：

```text
“真实 enemy AI 控制流能不能到它？”
```

**xref 相似性不能代替 CFG reachability。**

---

# 7. 第四阶段：重新理解 0x25DC——两级 handler dispatch

这是项目最关键的结构突破之一。

最初 47 个 `0x25DC` 表项被误当作“每个敌人类型的函数入口”。

随后严格检查两个 table ref，发现真实序列是：

```text
0x25DC[type × 4]
→ A4 = 每个 enemy type 的二级表基址

0(A4,D0.W)
→ A4 = 真正 handler pointer
```

因此：

```text
0x25DC
不是 “type → function”
而是 “type → state/handler subtable”
```

完整结构：

```text
enemy type
↓
0x25DC[type × 4]
↓
per-type secondary table
↓
D0 = table offset
↓
0(A4,D0.W)
↓
real handler
```

扫描全部类型后得到：

```text
47 enemy types
625 valid second-level pointers
348 unique real handlers
≈356 reachable routines
```

这一层以后可以作为其它 AI 分支的公共高速公路，不需要重新找。

---

# 8. 第五阶段：动态 movement / state 研究——有用但不能直接当 selector

为了找 D0/state 来源，项目做过多轮动态字段测试。

## 8.1 +0x3E / +0x42

动态 XY probe 中，`+0x3E/+0x42` 对未来运动方向具有非常高预测性。

一开始像“waypoint”，后来语义测试更支持：

```text
movement vector / movement target-like state
```

而不是直接 player XY。

静态 writer 扫描曾做：

- reachable handlers writer scan
- alias-aware writer scan
- global ROM writer scan
- pair cluster validation

最终没有得到可信的同 routine X/Y writer pair。

结论：这条路线对理解移动行为有价值，但不适合作为 target selector 主线。

## 8.2 高相关 state 字段

动态 waypoint/state probe 曾找到一个和运动状态变化高度相关的 word/byte 字段，并且对 type+D0 handler mapping 命中率很高。

一度推测：

```text
field = stateIndex
```

但随后出现关键矛盾：

```text
staticReadsNearDispatch = 0
```

也就是说，它虽然和行为状态高度相关，却没有证据证明 dispatcher 直接读取它来生成 D0。

多轮 writer/alias/overlap scan 也没有在真实 handler CFG 中找到可靠 writer。

因此最终策略调整为：

> **不要再从“相关字段”反推 D0，直接从 dispatcher 的真实控制流反向追 D0。**

### 可复用教训

高统计相关性 ≠ 控制流因果。

只有“这个字段被真实指令读取 → 进入决策/索引”的数据流才算硬证据。

---

# 9. 第六阶段：68000 指令边界误判——非常重要的坑

`wof_dispatch_d0_trace.js` 曾经在 dispatcher 附近每 2 字节尝试解码，得到看似漂亮的 D0 writer：

```text
0x25C0 MOVE.B (A4)+,D0
0x25C4 ORI.B #0x4E75,D0
0x25D2 MOVE.B A2,D0
0x25D6 ORI.B #0x6000,D0
```

后来根据已确认的真实指令边界发现，这些几乎全是假解码。

原因：68000 指令有 extension words。

例如已知：

```text
0x25BE ... [extension word at 0x25C0]
0x25C2 MOVEA.L 0(A4,D0.W),A4 [extension at 0x25C4]

0x25D0 ... [extension word at 0x25D2]
0x25D4 MOVEA.L 0(A4,D0.W),A4 [extension at 0x25D6]
```

因此把 `0x25C0/0x25C4/0x25D2/0x25D6` 当作新 opcode 起点，会把 extension word 解成完全假的“指令”。

### 以后必须遵守

对于关键 68000 控制流：

1. 从已知真实 boundary 顺序 decode。
2. 不要仅因为某个偶数地址能解码就认为它是 opcode start。
3. branch target / function entry / 前一条指令长度必须共同证明 boundary。
4. extension word 内产生的 MOVE/CMP/ORI 等候选全部视为不可信，直到 boundary 验证。

这是整个项目最重要的逆向方法论之一。

---

# 10. 第七阶段：D0 不是 dispatcher 内生成，而是上游传入

严格边界确认后，`0x25B6 / 0x25C8` 一带的结构变清楚：

```text
32(A0) → D1
D1 × 4
0x25DC[D1] → A4
0(A4,D0.W) → A4
```

关键结论：

```text
D0 在进入 dispatcher 前已经准备好
```

并且因为二级表是 long pointer table，D0 实际表现为 4-byte 对齐的 handler/state offset。

因此真正问题变成：

```text
谁在上游决定 D0？
```

而不是继续盯 dispatcher 内部找 state 字段。

---

# 11. 第八阶段：普通 caller 为 0 → 改查 incoming CFG edge

首先尝试找对 `0x25B6 / 0x25C8` 的 direct JSR/BSR caller。

结果：

```text
direct caller = 0
```

这个结果非常重要，因为它告诉我们：

```text
0x25B6 / 0x25C8 不应按普通独立函数入口理解
```

可能通过：

- BRA/Bcc
- JMP
- state-machine shared code
- fall-through/内部 label
- pointer/jump table

进入。

因此扫描策略从：

```text
“谁 CALL 它？”
```

改成：

```text
“所有控制流 incoming edge 是什么？”
```

全 ROM / 真实 CFG 扫描得到：

```text
44 direct incoming control-flow edges
0x25B6: 4
0x25C8: 40
pointer32 refs: 17（当时扫描结果）
```

而且大量 edge 前直接出现：

```text
MOVEQ #8,D0
MOVEQ #12,D0
MOVEQ #16,D0
MOVEQ #20,D0
...
→ branch into dispatcher
```

这成为非常强的证据：

```text
上游 AI path 直接选择 state/handler offset D0
```

---

# 12. 第九阶段：44 条 edge 收敛到少数异常路径

对 44 条 incoming edge 做局部真实路径扫描，检查：

```text
P1/P2/P3 refs
CMP
Bcc
D0 provenance
```

局部结果：

```text
edgesWithPlayerRefs = 0
strongPlayerCmpEdges = 0
edgesWithCmp = 1
nonImmediateD0 = 1
```

意义不是失败，而是：

> target selector 不在 dispatcher edge 紧邻的几十条指令里，而在更上游 CFG predecessor。

所以后续转向：

```text
edge-seeded reverse CFG
→ multi-boundary reverse CFG
→ strict D0 source decode
→ strict opcode target validation
```

这一轮非常重要，因为开始从“局部线性反汇编”升级为真正的 **CFG predecessor 数据流追踪**。

---

# 13. 第十阶段：严格验证后的关键上游区域

在 reverse CFG / strict decode 过程中，逐步锁定并验证了一批关键地址/区域。

特别重要的是后续确认的 dispatcher frontier edge：

```text
0x010F48
0x010FA2
```

围绕这些 edge，又追过：

- D0 来源
- A1/D1 provenance
- `0x01AD5A` helper / low-nibble classification chain
- `0x0111B4` 一带的 A5 provenance / compare
- `0x011190` state table / A5 role

这些分析虽然不是最后的 player-table 证据，但帮助建立了上游寄存器角色和 selector 周边控制流。

### 关于 A5 路线

A5 相关链曾经非常可疑，但最终不能因为某个 A5 compare 就直接宣布 A5 是 target。

它的真正价值是把我们带入更接近 selector 的代码区域，并暴露后续 selected-player slot / player-table 数据流。

因此记录为：

```text
有价值的中间线索
≠ 单独足以证明 target selector
```

---

# 14. 第十一步：真正的三玩家 ROM pointer table 出现

这是 selector 主线目前最硬的结构证据之一。

发现 ROM 中存在完整连续的 3 个 long：

```text
0x010CF8 = 0xFFBE1C  // P1
0x010CFC = 0xFFBEFC  // P2
0x010D00 = 0xFFBFDC  // P3
```

即：

```text
0x010CF8
↓
[P1 pointer, P2 pointer, P3 pointer]
```

这和以前“搜到三个散落的 player refs”完全不同。

它具有明确的数据结构语义：

```text
3-player pointer table
```

更关键的是，它位于已经确认的重要 dispatcher frontier：

```text
0x010F48
0x010FA2
```

附近几百字节内。

因此 selector 搜索第一次从：

```text
“哪里同时出现 P1/P2/P3？”
```

升级为：

```text
“谁在真实代码中索引这一张 3-player table？”
```

这是质变。

---

# 15. 第十二步：从 player table 做真实 xref，而不是搜重复表

发现 `0x010CF8` 后，策略明确收窄：

```text
只追 0x010CF8 这张表
不扫其它重复 P1/P2/P3 常量组
```

新增的真实 xref 分析会检查：

- PC+d16
- PC+index
- abs.L EA
- index register
- table load 的目的寄存器
- 从 xref forward CFG 是否能到 `0x010F48 / 0x010FA2`

这一步方法非常重要：

> **真正 selector 的关键不是表存在，而是找到“index → table → selected pointer → downstream decision”的完整 data/control chain。**

相关脚本：

```text
wof_player_table_10cf8_xrefs.js
```

对应提交：

```text
624fbed13125382fac5efa3713a619c5efa62709
```

随后进一步增加 table xref → dispatcher edge 的真实路径追踪：

```text
93827ee0be105a7c4f958c22d79123f031892b4e
```

---

# 16. 第十三步：selector index / selected-player slot 继续上溯

在 player table xref 之后，分析继续向“index 从哪里来、选出的 player 放到哪里”推进。

最新相关方向包括：

```text
A0 + 0x7E
A5 + 0x1FA
```

专用扫描器用于统计：

- `A0+0x7E` 的所有真实 reads/writes
- selector site 附近 `D1` load
- 是否存在 0 / 4 / 8 这种直接适配 3×long table 的 index 写入
- `A5+0x1FA` 的 selected-player slot reads/writes

相关提交：

```text
53455e8aab6316a422a64c50a4906f55e5463024
Trace A0+0x7E player selector and A5+0x1FA selected-player slot
```

随后继续向上追：

```text
A0 + 0x7C
```

并重点查：

```text
A0+0x7C 的 writers
0 / 4 / 8 immediate selector values
0x01AA14 附近 copy-to-7E 链
```

相关提交：

```text
693839e19965b1212b657333743a666b2122e03f
Trace A0+0x7C as upstream player selector source
```

### 当前方法论意义

如果最终证明链类似：

```text
A0+0x7C
→ A0+0x7E / D1
→ 0 / 4 / 8
→ 0x010CF8[D1]
→ P1/P2/P3 pointer
→ selected-player slot/register
→ state/D0 decision
→ 0x010F48 / 0x010FA2
→ dispatcher
```

那么这就是完整 selector 数据流。

在没有运行时最终验证前，应区分：

```text
“代码结构高度支持”
vs
“2P/3P 实战已经证明”
```

不要提前把推断写成最终真值。

---

# 17. 这次逆向为什么越来越快

前半段耗时长，是因为同时不知道：

```text
ROM 在哪里
地址是否偏移
47 type entries 是什么
handler 怎么调度
D0 是什么
函数边界在哪里
dispatcher 是 call 还是 branch
player target 是否保存在 enemy struct
```

现在这些底座大部分已经知道。

以后逆某个具体敌人动作，不需要再重新找整套架构。

典型后续流程可以直接变成：

```text
已知 enemy type
↓
0x25DC 找该 type secondary table
↓
已知 D0/state offset
↓
定位 real handler
↓
追 handler 的进入条件 / outgoing state
↓
如果涉及玩家，优先查已知 player-selector / selected-player 数据流
↓
标注语义：approach / turn / startup / active / recovery / projectile...
```

因此：

- 普通近战动作：局部 handler 逆向。
- 弓箭/炸弹/流星锤：handler + projectile spawn/trajectory。
- Boss：可能有独立 state machine，但仍复用大量底层设施。

不会每次都重新经历 selector 这次的大海捞针。

---

# 18. 明确不要重复的失败路线

以后任何新对话/新模型接手时，应优先阅读这一节。

## 18.1 不要重新追 `0x0080F2` 为 enemy selector

已用真实 348 handler roots 做过 reachability：0 paths。

## 18.2 不要重新靠 Focus Multiroom 无限加房间找固定 target offset

统计路线已经完成使命：说明简单 E0 target 字段不可靠。

## 18.3 不要把 `+0x3A/+0x6A/+0x9C` 重新包装成 target

都已有反证或强混杂证据。

## 18.4 不要把高相关 movement/state 字段直接当 dispatcher state source

必须有真实静态 read/dataflow。

## 18.5 不要每 2 byte 独立解码 68000 后把结果当真

必须尊重真实 instruction boundary 和 extension word。

## 18.6 不要只找 JSR/BSR caller

dispatcher 已证明存在大量 branch/incoming edge 结构。

## 18.7 不要只因为出现 P1/P2/P3 三个常量就宣布 selector

必须证明：

```text
index → player table → selected pointer → downstream decision
```

---

# 19. 推荐的标准逆向模板（以后其它 AI 分支直接复用）

## Step A：先确定问题属于哪一层

```text
目标选择？
state transition？
具体动作 handler？
projectile spawn？
碰撞/active frame？
```

不要所有问题都从 RAM 全局扫描开始。

## Step B：从已经确认的结构进入

```text
Type
→ 0x25DC
→ secondary table
→ D0
→ real handler
```

## Step C：严格建立真实 CFG

优先信任：

```text
已知 function/branch target
顺序 decode
真实 predecessor/successor
```

不要信任：

```text
任意偶数地址的“可解码指令”
```

## Step D：做 provenance，而不是只做附近搜索

例如要找 target：

```text
谁写 index？
→ index 到哪张 table？
→ table load 写哪个寄存器？
→ 该寄存器/slot 被谁读？
→ 哪个 CMP/距离/state decision 使用？
```

## Step E：静态证据后必须做动态验证

selector 最终至少应验证：

```text
P1 only
P1 + P2
P1 + P2 + P3
玩家分开站位
敌人明显切换目标
```

并确认静态预测的 selected player 与实际追击/攻击目标同步。

## Step F：只有验证后才写入 Future Danger runtime

不要把仍在逆向阶段的“候选字段”直接变成 HUD 真值。

---

# 20. 关键脚本 / 提交索引

下面是这次 selector 主线中具有方法论价值的一部分文件/提交，便于以后回看。

### 两级 dispatch / handler roots

```text
wof_rom_focus_level2_tables.js
0788e5c9615ff4044e59ddf12631d61135025f84

wof_rom_focus_handler_trace.js
ce0a681ed0536b4b0e84266f076b27e98b0664d0
```

### selector 静态扫描 / upstream

```text
wof_rom_focus_selector_scan.js
ff5d80ce49b93f765f81847594d0380bce2a35ff

wof_rom_focus_selector_ea.js
bd96cf8e29dd1b31cf3608182ed729bb02a80096

wof_rom_focus_upstream_selector.js
3b40754b1f8a1b0922617838bab91d73a575a6a5
```

### 动态 target/movement 验证

```text
wof_target_dynamic_probe.js
wof_target_handle_probe_v2.js
wof_target_xy_probe_v3.js
wof_waypoint_state_probe.js
```

### D0 / dispatcher

```text
wof_dispatch_d0_trace.js
77b9988ef38d126ec8648bae46849ed50627176d

wof_dispatch_caller_d0_trace.js
95a3828547a9026a039224a4ec8fb5bc2dc92f4d

wof_dispatch_incoming_edges.js
44899fa29b10c97387ba49bc07ac2e055d3e4315

wof_dispatch_edge_selector_scan.js
1603f88ff635b5cbac45f61cc643657e39d7ede2
```

### reverse CFG / strict frontier

```text
592bfc6140c5028579892cce5305730d2d90709e
Add dispatcher predecessor selector scan

7be302141c862782513d5ba49adb29d15537848f
Add multi-boundary reverse CFG selector scan

1db1e8492ed3d6791491a3302294c75a12055222
Add focused D0 source decoder for reverse CFG frontier

260aac54f14fc51bb951d707330a3ff7f73a2455
Validate dispatcher frontier edges against strict opcode targets

510681b9f6a32968e1441a81be60f6f5e10de836
Add strict decoder for the two validated dispatcher edges
```

### player table / selector 数据流

```text
wof_player_table_10cf8_xrefs.js
624fbed13125382fac5efa3713a619c5efa62709
Trace real xrefs to 0x10CF8 P1/P2/P3 pointer table

93827ee0be105a7c4f958c22d79123f031892b4e
Trace real xrefs from 0x010CF8 player table to dispatcher edges

wof_player_selector_7e_1fa_flow.js
53455e8aab6316a422a64c50a4906f55e5463024
Trace A0+0x7E player selector and A5+0x1FA selected-player slot

wof_player_selector_7c_source.js
693839e19965b1212b657333743a666b2122e03f
Trace A0+0x7C as upstream player selector source
```

---

# 21. 当前最重要的固定结构（速查）

```text
Players:
P1 = 0xFFBE1C
P2 = 0xFFBEFC
P3 = 0xFFBFDC
stride = 0xE0

Enemy pool:
base ≈ 0xFFC0BC
stride = 0xE0

Type dispatch base:
0x25DC

Dispatch model:
type → per-type secondary table → D0 offset → real handler

Scale discovered:
47 types
625 level2 pointers
348 unique real handlers
≈356 reachable routines

Validated selector-side player table:
0x010CF8 = 0xFFBE1C
0x010CFC = 0xFFBEFC
0x010D00 = 0xFFBFDC

Important dispatcher-frontier region:
0x010F48
0x010FA2
```

---

# 22. 逆向完成后的整合方向

selector 真正闭环并通过 2P/3P 动态验证后，不是另起一个项目，而是直接接回已经存在的 Future Danger 系统：

```text
真实 selected player
↓
AI state / handler
↓
attack family
↓
startup / active / projectile
↓
未来 hit geometry
↓
只对真正受威胁的 P1/P2/P3 报警
↓
Safe Path
↓
角色头顶 HUD
```

这也是为什么这次 selector 逆向值得投入这么多时间：它解决的不是一个孤立地址，而是整个多人 Future Danger 系统缺失的上游“谁是目标”真值来源。

---

# 23. 最终方法论总结

这次 WOF 逆向最值得保留的经验，可以浓缩成下面几句：

```text
统计相关性只能产生候选，不能证明因果。

P1/P2/P3 xref 同时出现，不等于 enemy selector。

真实 handler root + CFG reachability，优先级高于“长得像”。

68000 extension word 是高危假指令来源，必须严格尊重 boundary。

dispatcher 不一定是 CALL 入口，要扫描所有 incoming control-flow edges。

找到 table 后，不要停在 table；必须追 index、selected pointer 和 downstream use。

静态链闭环后，还必须用真实 2P/3P gameplay 做最终验证。
```

从项目角度，这次工作已经把 WOF AI 从“靠观察猜行为”的黑箱，推进到“可以沿 type → state → handler → player selection 数据流逐层解释”的结构化逆向阶段。

以后逆其它分支，优先复用这套结构和方法，不要从零开始。

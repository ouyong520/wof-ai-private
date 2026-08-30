# WOF Future Danger AI — 完整逻辑、逆向过程与当前进度

更新时间：2026-08-31
仓库：`ouyong520/wof-ai-private`
游戏：WOF / Warriors of Fate / 吞食天地II / 三国志II，World 921002 / MAME `wofr1`

> 这份文件是当前项目的“完整总览”。新对话如果要快速接手，先读 `WOF_AI_HANDOFF.md`；需要理解为什么走到现在、哪些方向已经排除、selector / dispatcher 到底怎样连接，再读本文件。

---

## 1. 项目最终目标

目标不是自动操作，而是做 **Future Danger AI**：

```text
ROM 固定 AI / 招式逻辑
+ 当前 CPS RAM
+ enemy type/state/action/position
+ 当前锁定的 P1/P2/P3 target
+ 未来攻击起手 / movement / projectile / active window
→ 预测未来约 0~1000ms
→ 判断真正会威胁 P1 / P2 / P3 中谁
→ 只有真正需要躲时才提示
→ Future Danger Map / Safe Path
```

核心要求是减少误报：怪真正准备打 P2 时，不能仅因为 P1 更近就一直给 P1 报警。

---

## 2. 浏览器运行环境与固定地址

运行链：

```text
网页
→ cycgo.js
→ Web Worker: gstyphoon.js
→ gstyphoon.wasm
→ CPS RAM + live 68000 ROM
```

DevTools Console 必须切到 `gstyphoon.js` Worker。

### 玩家对象

```text
P1 = 0xFFBE1C
P2 = 0xFFBEFC
P3 = 0xFFBFDC
player stride = 0xE0
```

### 敌人池

```text
enemy pool = 0xFFC0BC
enemy stride = 0xE0
slots = 20
```

### ROM

live ROM 已能从 Worker 恢复，通常 `swap16`，缓存：

```js
self.__WOF_ROM_LOC_CACHE
```

旧 offline DB 与 live ROM 地址关系：

```text
live = offline + 0x34
```

不要再做一次性 256MB HEAP 全扫；优先复用缓存 / 恢复脚本。

---

## 3. 已经解开的 dispatcher 架构

早期最大误区是把 47 个 type entry 当成函数入口。真实结构是两级 dispatch：

```text
enemy type
→ 一级 type table
→ 每个 type 对应的二级 state/handler table
→ D0 作为已乘 4 的 byte offset
→ final handler
```

已解析规模：

```text
47 types
625 level2 pointers
348 unique real handlers
约 356 个可达 routine（不同 decoder/root policy 下略有浮动）
```

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
32(A0) = enemy type
D1 = type * 4
A4 = type-specific level2 table
D0 = 上游已经准备好的 state byte offset
0(A4,D0.W) = final handler
```

**D0 不是在 dispatcher 内生成，而是上游 AI 状态机选择出来的。**

---

## 4. 44 条 dispatcher incoming edges

`wof_dispatch_incoming_edges.js` 已确认：

```text
directIncomingEdges = 44
edges25B6 = 4
edges25C8 = 40
pointer32Refs = 17
fallthrough = 0
```

大量入口前直接是：

```text
MOVEQ #0,D0
MOVEQ #4,D0
MOVEQ #8,D0
MOVEQ #12,D0
MOVEQ #16,D0
MOVEQ #20,D0
...
→ 0x25B6 / 0x25C8
```

说明上游状态机直接决定下一个 state offset，然后进入共享 dispatcher。

早期 edge-local selector scan：

```text
edges = 44
player refs = 0
CMP edges = 1
strong player/CMP = 0
nonImmediateD0 = 1
```

这一步说明真正 P1/P2/P3 selector 不在 dispatcher 入口几条指令附近，而在更上游。

---

## 5. 已排除 / 降级的方向

### 5.1 Focus Multiroom

已经做过多轮多房间 RAM correlation。早期候选：

```text
+0x3A
+0x6A
+0x68
+0x9C
```

都不能证明是“持续 P1/P2/P3 target selector”。不要继续把 Focus Multiroom 当主线。

### 5.2 movement / action 字段

`enemy +0x3E / +0x42` 对未来运动方向很强，但语义更像 movement/action，而不是 target player。

### 5.3 0x0080F2

已正式排除：

```text
625 level2 pointers
348 unique real handlers
扩展 real handler CFG
→ 0x0080F2 handlerPaths = 0
```

不要复活这条线。

### 5.4 A0+0x40 / +0x44 target XY writer 假设

全 real handler graph / alias / overlap writer 扫描都没找到可信 writer，已降级，不要再重复。

### 5.5 0x11C26 helper

曾怀疑 selector 选出 A1 后调用 `0x11C26`，可能是 target→dispatcher bridge。

最终否定：helper 内会自己覆盖 A1：

```text
0x11C5C MOVE.L D1,A1
0x11C68 LEA ...,A1
```

所以传入的 selected-player A1 不会作为这条 helper 的主数据继续流向 dispatcher。

---

## 6. 真实 P1/P2/P3 selector 的发现

这是项目目前最重要的突破。

### 6.1 ROM 中存在完整 P1/P2/P3 pointer table

ROM 里有多份完整连续的：

```text
FFBE1C  FFB EFC  FFBFDC
```

当前主线使用：

```text
0x010CF8 = 0xFFBE1C  (P1)
0x010CFC = 0xFFBEFC  (P2)
0x010D00 = 0xFFBFDC  (P3)
```

### 6.2 selector 访问点

至少 4 个真实点读取 `A0+0x7E`：

```text
0x010C82 MOVE.W 126(A0),D1
0x010C86 MOVE.L table(D1.W),A1

0x010D2C MOVE.W 126(A0),D1
0x010D30 MOVE.L table(D1.W),A1

0x010DDA MOVE.W 126(A0),D1
0x010DDE ... player table ...

0x010E66 MOVE.W 126(A0),D1
0x010E6A LEA 0x010CF8,A1
0x010E6E MOVE.L 0(A1,D1.W),A1
```

因此：

```text
enemy + 0x7E
→ D1.W
→ P1/P2/P3 pointer table
→ A1 = selected player object
```

### 6.3 玩家自身 +0x7C 是固定 self-index

动态 probe 2 秒、101 samples / player：

```text
P1+0x7C = 0x0000   101/101
P2+0x7C = 0x0004   101/101
P3+0x7C = 0x0008   101/101
selfIndex048Exact = true
```

所以 `player+0x7C` 的语义已经锁死：

```text
P1 = 0
P2 = 4
P3 = 8
```

这是恰好能直接作为 long-pointer table byte offset 的 0/4/8。

### 6.4 敌人 +0x7E 是运行时当前 target selector

动态 6 秒 / 301 samples，当前房间 3 个 active-like enemy slots：

```text
slot 14: +0x7E = 8   301/301
slot 11: +0x7E = 0   301/301
slot 15: +0x7E = 0   301/301
```

3 个活跃 slot：

```text
valid048Pct = 1.0
allLiveMostly048 = true
```

与最近玩家匹配率约：

```text
1.000 / 0.797 / 0.767
```

这说明 `enemy+0x7E` 不是普通状态值，而是实际运行时 P1/P2/P3 target index。

### 6.5 +0x7C → +0x7E 的关系

静态 writer scan 一度看到：

```text
0x01AA14 MOVE.W 124(A0),126(A0)
```

但动态结果证明敌人 `+0x7C` 与 `+0x7E` 可以长期不同，例如：

```text
slot14 +0x7C = 0
slot14 +0x7E = 8
持续 6 秒
```

因此 `+0x7C→+0x7E` 只是部分复制 / 初始化 / 对象传播路径，不是当前 target 更新的全部机制。

### 6.6 对象复制模式

扫描到多处：

```text
MOVE.W 124(A0),D0
MOVE.W D0,126(A1)
```

以及：

```text
MOVE.W 124(A0),124(A1)
```

这和“玩家自身 +0x7C = 0/4/8，被复制到敌人 / 新对象的 +0x7E”非常一致。

---

## 7. 选中玩家指针 scratch：506(A5)

`0x010E6E` 选出 A1 后：

```text
0x010E72 MOVE.W A1,506(A5)
```

这里保存的是 player address 的低 16 bit。

已找到 4 个 reader：

```text
0x016D3E
0x016FC6
0x017662
0x0176B2
```

至少 3 条真实路径会重新变成地址寄存器：

```text
0x016FCC MOVEA.W D0,A0
0x01766E MOVEA.W D1,A0
0x0176BE MOVEA.W D1,A0
```

因为 player 地址都是 `0xFFFFxxxx`，68000 `MOVEA.W` 会符号扩展，所以低 16-bit：

```text
BE1C / BEFC / BFDC
```

能还原成：

```text
FFFFBE1C / FFFFBEFC / FFFFBFDC
```

结论：`506(A5)` 是 selected-player pointer scratch / cache。

但这些 reader 附近没有 `0x25B6/0x25C8`，所以它不是目前 dispatcher 的直接本地桥，更多是 selected-player 在其它系统里的共享缓存。

---

## 8. selector 附近的状态机

### 8.1 0x10E66 选出玩家

严格结构：

```text
0x10E66 MOVE.W 126(A0),D1
0x10E6A LEA 0x10CF8,A1
0x10E6E MOVE.L 0(A1,D1.W),A1
0x10E72 MOVE.W A1,506(A5)
```

### 8.2 A0+0x99 第一层状态分派

后续在：

```text
0x10EA8 MOVE.B 0x99(A0),D0
0x10EAC MOVE.W 6(PC,D0.W),D1
0x10EB0 JMP 2(PC,D1.W)
```

表基址：`0x10EB4`，9 项：

```text
index 0  -> 0x10BBC
index 2  -> 0x10BD0
index 4  -> 0x10BE4
index 6  -> 0x10BD0
index 8  -> 0x10BF8
index 10 -> 0x10C0C
index 12 -> 0x10BD0
index 14 -> 0x10BD0
index 16 -> 0x10BD0
```

共 5 个 unique target。

### 8.3 每个 state99 block 还有 A0+0x2A 第二层分派

这 5 个 block 全部匹配同一结构：

```text
MOVE.B 42(A0),D0
MOVE.W table(PC,D0.W),D1
JMP table(PC,D1.W)
```

所以状态结构是：

```text
A0+0x99
→ 第一层 state99 jump
→ A0+0x2A
→ 第二层 action jump
→ 具体 AI routine
```

5 个 block 的第二层目标合并后共有 9 个 unique final targets：

```text
0x010EC6
0x011078
0x011190
0x0112C2
0x011456
0x01156A
0x011656
0x01178E
0x011908
```

---

## 9. 已严格接通的一条 state → dispatcher 路线

当前最重要的严格证明：

```text
state99 index = 0
→ first block = 0x010BBC

action2A index = 2
→ table entry 0x010BCA = 0x02FE
→ final target = 0x010EC6
```

然后 `0x010EC6` 到 dispatcher 的关键 opcode 全 exact-word 验证通过：

```text
0x10EC6 CMPI.W #0,2(A0)
0x10ECC BNE 0x10ED2
0x10ECE JSR 0x1B02
0x10ED2 TST.B 43(A0)
0x10ED6 BNE 0x10F08
...
0x10F08 MOVE.W 64(A0),D1
0x10F0C ADD.W D1,4(A0)
0x10F10 SUBQ.B #1,31(A0)
0x10F14 BNE 0x10F5C
0x10F16 MOVEQ #0,D0
...
0x10F24 BTST #4,114(A0)
0x10F2A BEQ 0x10F4C
0x10F2C JSR 0x1426
0x10F30 BCS 0x10F40
...
0x10F40 MOVE.W #0x0600,42(A0)
0x10F46 MOVEQ #24,D0
0x10F48 JMP 0x25C8
```

因此已经严格证明：

```text
state99=0 + action2A=2
→ 0x10EC6
→ D0 = 24
→ 0x25C8
→ type-specific level2 handler
```

脚本 verdict：

```text
allState2APatternsValid = true
routes = 36
uniqueFinalTargets = 9
routesTo10EC6 = 1
strictBridge10EC6To10F48 = true
bridgeD0 = MOVEQ #24,D0
dispatcher = 0x25C8
```

这是目前第一次把 selector 所在同一区域的状态机严格接到真实 dispatcher。

---

## 10. 0x10FA2 → 0x25B6 分支

同一区域还存在：

```text
0x10FA0 MOVEQ #8,D0
0x10FA2 JSR 0x25B6
```

已确认这是真 dispatcher edge，但当前还没有像 `0x10F48 → 0x25C8` 那样完成完整 state99/action2A 路由归属证明。

它仍是后续要补齐的第二条本地主线。

---

## 11. 当前“完整链”到底证明到什么程度

### 已经证明

1. `player+0x7C` 的固定 self index：P1=0 / P2=4 / P3=8。
2. `enemy+0x7E` 在真实运行时是 0/4/8 target selector。
3. `enemy+0x7E → D1.W → 0x10CF8 player table → A1=selected player`。
4. selected player 低 16-bit 会写进 `506(A5)`，并可在其它代码中恢复为真正 player pointer。
5. selector 附近存在 `A0+0x99 → A0+0x2A` 两层状态机。
6. 其中一条明确 route：`state99=0/action2A=2 → 0x10EC6 → D0=24 → 0x25C8`。
7. `0x25C8` 使用 D0 作为 level2 state offset，按 enemy type 取最终 handler。

### 还没有完全证明

还差“同一次实际执行中”的最终端到端因果闭环：

```text
enemy+0x7E 某个 P1/P2/P3 selector 值
→ selected player A1
→ 哪些 target-dependent 比较 / helper
→ 如何决定或影响 A0+0x99 / A0+0x2A
→ 走到某个 D0
→ 0x25B6 / 0x25C8
```

换句话说：

- selector 本身已锁死；
- dispatcher 本身已锁死；
- selector 所在状态机的一条 route 已接到 dispatcher；
- 现在差最后“selector 值怎样影响状态选择”的因果层。

这也是 `wof_selector_end_to_end_proof.js` 当前要做的事。

---

## 12. 当前最新端到端脚本

### `wof_selector_end_to_end_proof.js`

commit：

```text
31dea3a6a1a89799ba86724321c7a5db618d5596
```

目标：把这些已知事实一次性 strict 验证成一条结构链：

```text
0x10E66 enemy+0x7E selector
→ 0x10CF8 P1/P2/P3 table
→ state99
→ action2A
→ proven 0x10EC6 route
→ MOVEQ #24,D0
→ 0x10F48
→ 0x25C8
```

当前用户还没执行它的最终 JSON；所以不要在新对话里假设 `endToEndStructuralProof=true`，必须先跑一次确认。

执行：

```js
await fetch('https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/wof_selector_end_to_end_proof.js?x='+Date.now(),{cache:'no-store'}).then(r=>r.text()).then(s=>(0,eval)(s));
```

预期：

```text
=== SELECTOR END-TO-END JSON ===
```

关键字段：

```text
selectorStrict
playerTableOk
state99Strict
action2AStrict
bridgeStrict
endToEndStructuralProof
```

---

## 13. 新房间 / 新 Worker 恢复流程

最新 `wof_resume_dispatch_selector.js` 已更新到当前 frontier。

换房间时，先只执行：

```js
await fetch('https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/wof_resume_dispatch_selector.js?x='+Date.now(),{cache:'no-store'}).then(r=>r.text()).then(s=>(0,eval)(s));
```

它负责恢复 ROM cache / dispatcher 基础状态。恢复成功后不要重跑旧 Focus / 0x80F2 / 44-edge 大扫。

---

## 14. 关键脚本时间线

### dispatcher / CFG

```text
wof_dispatch_incoming_edges.js
wof_dispatch_edge_selector_scan.js
wof_dispatch_predecessor_selector.js
wof_dispatch_reverse_cfg_selector.js
wof_dispatch_d0_source_focus.js
wof_dispatch_a1_d1_trace.js
wof_dispatch_frontier_validate.js
wof_dispatch_two_edge_strict_decode.js
wof_dispatch_edge_seed_reverse_selector.js
```

### 排除旧分支

```text
wof_dispatch_ad5a_inspect.js
wof_dispatch_ad5a_leaf_decode.js
wof_dispatch_low4_chain.js
wof_dispatch_targetxy_local_writers.js
wof_state_writer_overlap_v4.js
```

### 111xx / player selector 发现

```text
wof_dispatch_111fa_42c2_focus.js
wof_dispatch_111c2_call_provenance.js
wof_dispatch_111b4_a5_provenance.js
wof_dispatch_111b4_entry_incoming.js
wof_dispatch_111190_table_a5_role.js
wof_player_table_10cf8_xrefs.js
wof_player_selector_7e_1fa_flow.js
wof_player_selector_7c_source.js
wof_player_selector_5f6ba_d45_provenance.js
```

### 动态 selector 锁定

```text
wof_player_selector_7e_runtime_probe.js
wof_player_self_index_probe.js
wof_player_selector_7e_alias_writers.js
wof_player_selector_7c_alias_writers.js
```

### selector → state → dispatcher

```text
wof_selector_11c26_dispatch_bridge.js
wof_selector_1fa_consumers_bridge.js
wof_selector_10e66_dispatch_local_raw.js
wof_selector_state99_jump_cfg.js
wof_selector_state2a_dispatch_bridge.js
wof_selector_end_to_end_proof.js
```

---

## 15. 最重要的 68000 解析坑

1. **偶地址不等于指令边界。** 多次把 extension word 误扫成 ORI / branch；所有关键路径必须 exact target + raw words / strict decode 验证。
2. 例如 `0xEB6C = 0x3031 0x1000`，`0xEB6E` 是 extension word，不是独立 opcode。
3. PC-relative indexed 的 base 要按 68000 实际 PC 规则算。
4. indexed `.W` 值要 sign-extend。
5. `MOVEA.W` 会 sign-extend，所以 `BE1C` 能恢复成 `FFFFBE1C`。
6. raw full-ROM opcode hit 只能当候选，不能直接当 CFG evidence。
7. 不要因为某 field offset 在不同结构体都存在，就假设语义相同；`0x05F6BA` 就曾因相同 `+0x7C` 偏移造成误导。

---

## 16. 当前进度判断

工程进度估计：**约 90%–93%**。

已经完成：

```text
真实 dispatcher
真实 two-level type/state dispatch
44 incoming edges
真实 player pointer table
P1/P2/P3 self index 0/4/8
真实 enemy target selector +0x7E
selected player A1
selected-player scratch 506(A5)
selector 邻近 state99/action2A 两层状态机
至少 1 条 state route → D0 → 0x25C8 的严格桥
```

剩余核心：

```text
1. 跑完 end-to-end structural proof。
2. 找 selector 值影响 state99/action2A 的真正 target-dependent compare / decision。
3. 把 0x10FA2 → 0x25B6 第二条分支也归属到具体状态路线。
4. 做动态因果验证：target selector 变化时，后续 state/action/D0 是否按预期变化。
5. 把 target + state + handler 映射成 Future Danger 0~1000ms 预测特征。
6. 最后才回 HUD / Future Danger Map / Safe Path。
```

---

## 17. 下一步唯一主线

先执行 `wof_selector_end_to_end_proof.js`。

如果：

```text
endToEndStructuralProof = true
```

则静态结构层收口，不再继续找“selector 在哪”。下一阶段改为：

```text
selector 值 0/4/8
→ 选中哪个 player
→ target-dependent comparison
→ state99/action2A transition
→ D0
→ dispatcher
→ handler
→ future attack / threat semantics
```

动态验证优先读-only 观察；只有必要时再做最小 RAM perturbation。

---

## 18. 一句话总结

目前已经不再是“猜敌人打谁”。游戏内部真实 target selector 已经找到并动态验证：

```text
P1/P2/P3 自身 +0x7C = 0/4/8
enemy +0x7E = 当前目标玩家 0/4/8
enemy+0x7E → 0x10CF8 player table → A1 = selected player
```

同一区域的状态机也已被拆成：

```text
A0+0x99
→ 第一层 state jump
→ A0+0x2A
→ 第二层 action jump
→ specific AI routine
→ D0
→ 0x25B6 / 0x25C8
```

并且已经严格证明其中一条：

```text
state99=0 + action2A=2
→ 0x10EC6
→ D0=24
→ 0x10F48
→ 0x25C8
```

现在只差最后的因果闭环：**当前 target selector 怎样影响 state/action 决策，从而选择最终 D0 / handler。**

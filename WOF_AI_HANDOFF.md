# WOF Future Danger AI — 项目交接 / 新对话续接说明

更新时间：2026-08-31（UTC+8）

> **这是当前唯一有效交接。** 新对话必须先完整读本文件，再检查仓库 `main` 最新脚本。不要从头重分析，不要让用户重新解释，不要回 Focus Multiroom/HUD，不要复活 `0x0080F2`，也不要再从 44 条 dispatcher edge 重新找 selector。

## 0. 接手规则

用户只负责在 **`gstyphoon.js` DevTools Console** 执行测试命令并返回截图/JSON。

- 能直接修改 GitHub 就自己修改。
- 每次尽量只给用户 **一条准确 Console 命令 + 预期 marker**。
- 不要求用户手改 JS。
- 新房间 / Worker 丢状态时先运行 `wof_resume_dispatch_selector.js`。
- 不调 HUD；当前阶段只做 ROM AI / Future Danger target/state 逆向。
- 不继续 Focus Multiroom。
- 不重新扫 44 dispatcher incoming edges。
- 不重新追 `0x0080F2`。
- 68000 任意偶地址不等于指令边界；extension word/data 误解已经多次发生，必须 exact-word/CFG 验证。

当前进度已从旧 handoff 的 80%–85% 推进到约 **93%–96%**：真正 P1/P2/P3 target selector 已动态+静态锁死，并且已经严格接通一条 selector 所在状态机 → `D0=#24` → `0x25C8` 的 dispatcher 路线。

---

## 1. 项目最终目标

游戏：**吞食天地II / Warriors of Fate / WOF / 三国志II**，版本 **WOF World 921002 / MAME `wofr1`**。

目标：Future Danger AI（观察/预测/HUD），不是自动操作。

```text
ROM 固定 AI / 招式逻辑
+ 当前 CPS RAM
+ enemy type/state/action/position
+ 真正 target P1/P2/P3
+ future attack / active / projectile
→ 预测未来约 0~1000ms
→ 判断攻击真正威胁谁
→ 只有真正需要躲时才提示
→ Future Danger Map + Safe Path
```

用户最在意：**减少误报**。怪实际打 P2 时不能因为 P1 更近就一直提示 P1。

---

## 2. 浏览器运行环境 / RAM 固定事实

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

Console 必须切到 **gstyphoon.js**。

固定 RAM：

```text
P1 = 0xFFBE1C
P2 = 0xFFBEFC
P3 = 0xFFBFDC
player stride = 0xE0

enemy pool = 0xFFC0BC
enemy stride = 0xE0
20 slots
```

ROM live image 通常 `swap16`，缓存：

```js
self.__WOF_ROM_LOC_CACHE
```

live/offline 旧 DB 地址关系：

```text
live = offline + 0x34
```

现有 CPS RAM 读取方式：

```js
const M=_0x515056.HEAPU8;
const R=_0x515056.HEAPU32[0x2e39e4>>>2]>>>0;
// 0xFFxxxx byte 映射使用 ^1
```

---

## 3. 已彻底解开的 dispatcher 架构

真实结构：

```text
enemy type
→ type table
→ type-specific level2 state/handler pointer table
→ D0 是已乘4的 byte offset
→ final handler
```

已解析：

```text
47 types
625 level2 pointers
348 unique real handlers
约 356 reachable routines
```

### `0x0025B6`

```text
0x25B6 MOVE.W 32(A0),D1
0x25BA ADD.W D1,D1
0x25BC ADD.W D1,D1
0x25BE MOVE.L 28(PC,D1.W),A4
0x25C2 MOVE.L 0(A4,D0.W),A4
0x25C6 RTS
```

### `0x0025C8`

```text
0x25C8 MOVE.W 32(A0),D1
0x25CC ADD.W D1,D1
0x25CE ADD.W D1,D1
0x25D0 MOVE.L 10(PC,D1.W),A4
0x25D4 MOVE.L 0(A4,D0.W),A4
0x25D8 BRA 0x247C
```

结论：`D0` 在进入 dispatcher 前由上游 state machine 决定。

---

## 4. 历史 44 incoming edge 结论（不要重做）

`wof_dispatch_incoming_edges.js`：

```text
directIncomingEdges = 44
edges25B6 = 4
edges25C8 = 40
pointer32Refs = 17
fallthrough = 0
```

`wof_dispatch_edge_selector_scan.js` 当时只在 edge-local 看到：

```text
edgesWithPlayerRefs = 0
edgesWithCmp = 1
nonImmediateD0 = 1
```

这是旧 frontier。现在已经越过它并找到真正 selector；**不要再从这 44 条重新开始。**

---

## 5. 旧 interesting-edge 分支结论（不要重复）

- `0x00EB70`：`A0+0x24 → D1 → EA5E 小表 [-24,-16,12,0,4] → D0 → 25C8`，属于 enemy state remap，不是 player selector。
- `0x01ACDE`：`AD0A + AD5A` movement/spatial/classification 链，`AD5A` low4 lookup，不是 P1/P2/P3 selector。
- `0x111B4 CMP.B 422(A5),D0` 曾追 A5，但 A5 实际长期作为 `0xFFFF8000` 全局 base，不能当 player pointer。
- `0x11C26` 曾怀疑是 selector→dispatcher helper，已排除：进入 helper 后会覆盖 A1，属于全局/搬运类逻辑，不是选中玩家数据桥。
- `A0+0x40/+0x44` writer 分支已全 CFG 扫描为 0，不再追。
- `0x05F6BA` 虽写 `+0x7C`，但属于 fixed-point/另一结构逻辑；不是 enemy target selector 生成点。

---

## 6. 真正 P1/P2/P3 selector 已锁死

### 6.1 ROM 玩家指针表

ROM 有完整连续表：

```text
0x010CF8 = 0xFFBE1C  (P1)
0x010CFC = 0xFFBEFC  (P2)
0x010D00 = 0xFFBFDC  (P3)
```

真实 selector 取表代码至少 4 处，其中明确的 PC+index：

```text
0x010C82 MOVE.W 126(A0),D1
0x010C86 MOVE.L [0x010CF8 + D1.W],A1

0x010D2C MOVE.W 126(A0),D1
0x010D30 MOVE.L [0x010CF8 + D1.W],A1
```

另有：

```text
0x010DDA / 0x010DDE...
0x010E66 / 0x010E6A / 0x010E6E...
```

### 6.2 动态证明 `enemy+0x7E` 就是 target selector

脚本：`wof_player_selector_7e_runtime_probe.js`

实测 3 个 live-like enemy slot，301 samples / ~6s：

```text
slot14 enemy+0x7E = 8  (100%)
slot11 enemy+0x7E = 0  (100%)
slot15 enemy+0x7E = 0  (100%)
```

所有 live slot 的 `+0x7E` 都 100% 属于 `0/4/8`。

结论：

```text
enemy +0x7E = 当前目标玩家 index byte offset
0 = P1
4 = P2
8 = P3
```

### 6.3 动态证明玩家自身 `+0x7C` 就是身份编号

脚本：`wof_player_self_index_probe.js`

101 samples：

```text
P1 +0x7C = 0x0000 100%
P2 +0x7C = 0x0004 100%
P3 +0x7C = 0x0008 100%
selfIndex048Exact = true
```

所以：

```text
player+0x7C = 玩家自身 0/4/8 身份编号
enemy+0x7E  = 当前目标 0/4/8
```

之前 handoff 中“enemy struct 内没有简单 target 字段”的历史结论已经被新证据推翻；**现在必须以 `enemy+0x7E` 为准。**

---

## 7. Selector → 玩家指针的严格路径

当前最清晰的一处：

```text
0x010E66 MOVE.W 126(A0),D1          ; enemy+0x7E target id
0x010E6A LEA 0x010CF8,A1           ; P1/P2/P3 pointer table
0x010E6E MOVE.L 0(A1,D1.W),A1      ; A1 = selected player
0x010E72 MOVE.W A1,506(A5)          ; 缓存低16-bit player pointer
0x010E76 BSR 0x011C26
...
0x010EA8 MOVE.B 153(A0),D0          ; state99
0x010EAC MOVE.W table(PC,D0.W),D1
0x010EB0 JMP table(PC,D1.W)
```

`506(A5)` 后来有真实 consumer：

```text
0x016FC6 MOVE.W 506(A5),D0
0x016FCC MOVEA.W D0,A0

0x017662 MOVE.W 506(A5),D1
0x01766E MOVEA.W D1,A0

0x0176B2 MOVE.W 506(A5),D1
0x0176BE MOVEA.W D1,A0
```

这证明 `506(A5)` 的确保存的是选中玩家低16-bit pointer scratch；但这些 consumer 不在 dispatcher 近旁，所以不是当前主线。

---

## 8. state99 第一层状态表

`0x010EA8` 读取 `A0+0x99` 后，`0x010EB0` 是 indexed JMP。

第一层 9 项表 `0x010EB4`：

```text
state99 index 0  -> 0x010BBC
2  -> 0x010BD0
4  -> 0x010BE4
6  -> 0x010BD0
8  -> 0x010BF8
10 -> 0x010C0C
12 -> 0x010BD0
14 -> 0x010BD0
16 -> 0x010BD0
```

5 个 unique target：

```text
0x010BBC
0x010BD0
0x010BE4
0x010BF8
0x010C0C
```

---

## 9. `A0+0x2A` 第二层状态表

这 5 个 state99 target 全部严格符合相同 pattern：

```text
MOVE.B 42(A0),D0
MOVE.W table(PC,D0.W),D1
JMP table(PC,D1.W)
```

也就是：

```text
A0+0x99  第一层状态
→ state block
→ A0+0x2A  第二层 action/state
→ 9 个 final target 中一个
```

9 个 unique final targets：

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

## 10. 已严格接通一条 selector-state → dispatcher 路线

脚本：

```text
wof_selector_state2a_dispatch_bridge.js
commit: 7cf1e1eda14b30a5fd520491c1ce990e1a4cdee6
```

结果：

```text
state99Blocks = 5
allState2APatternsValid = true
routes = 36
uniqueFinalTargets = 9
routesTo10EC6 = 1
strictBridge10EC6To10F48 = true
bridgeD0 = MOVEQ #24,D0
dispatcher = 0x0025C8
```

严格成立的组合：

```text
state99 = 0
action2A = 2
→ 0x010BBC 第二层表 entry 0x010BCA = +0x02FE
→ 0x010EC6
→ ...
→ 0x010F40 MOVE.W #0x0600,42(A0)
→ 0x010F46 MOVEQ #24,D0
→ 0x010F48 JMP 0x0025C8
```

关键 `0x010EC6 → 0x010F48` 每个关键 opcode 都做了 exact-word check，全部 `ok=true`。

因此现在已经严格证明：

```text
selector 所在 AI 状态机
→ state99/action2A 两层状态分派
→ D0=#24
→ 0x25C8
```

注意措辞：这是**结构/执行路线证明**；当前还不要宣称“P1/P2/P3 selector 数值本身直接计算 D0=24”。target selector 和 state/action 分派在同一 AI 状态系统中，但 D0 还由 state99/action2A/条件逻辑共同决定。

---

## 11. 当前最新一步：端到端严格证明

新脚本：

```text
wof_selector_end_to_end_proof.js
commit: 31dea3a6a1a89799ba86724321c7a5db618d5596
```

它把以下全部一次 exact-check：

```text
enemy+0x7E
→ D1
→ 0x010CF8 P1/P2/P3 pointer table
→ A1 selected player
→ 0x010EA8 state99 dispatch
→ state99=0 -> 0x010BBC
→ action2A=2 -> 0x010EC6
→ MOVEQ #24,D0
→ 0x010F48
→ 0x0025C8
```

预期 marker：

```text
=== SELECTOR END-TO-END JSON ===
```

最关键 verdict：

```text
selectorStrict
playerTableOk
state99Strict
action2AStrict
bridgeStrict
endToEndStructuralProof
```

如果全部 true，则当前 mainline 的结构证明收口，下一步应转入 **动态 force/causal validation + Future Danger 语义映射**，而不是继续静态找 selector。

---

## 12. 新房间 / Worker 恢复

`wof_resume_dispatch_selector.js` 已更新到 v2：

```text
commit: b5bafb5d79887feb6b995179b5e6177f45a670c0
```

执行：

```js
await fetch('https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/wof_resume_dispatch_selector.js?x='+Date.now(),{cache:'no-store'}).then(r=>r.text()).then(s=>(0,eval)(s));
```

它现在恢复 ROM cache 后打印：

```text
=== CURRENT SELECTOR FRONTIER ===
```

不会再告诉下一位从 44-edge interesting frontier 重做。

---

## 13. 关键最新脚本 / commit

```text
wof_selector_end_to_end_proof.js
  31dea3a6a1a89799ba86724321c7a5db618d5596

wof_resume_dispatch_selector.js
  b5bafb5d79887feb6b995179b5e6177f45a670c0

wof_selector_state2a_dispatch_bridge.js
  7cf1e1eda14b30a5fd520491c1ce990e1a4cdee6

wof_selector_state99_jump_cfg.js
  5178563dd8600d83a4882bc02f3a9c6680b67bfb

wof_selector_10e66_dispatch_local_raw.js
  b305c777e8db19654c4a259174d6023cd617ff72

wof_selector_1fa_consumers_bridge.js
  2306e7e043bb1f974f01455d7bb22d7a231b9ce2

wof_selector_11c26_dispatch_bridge.js
  950aea6a25251f1ac7bcf22d9289e7ecbd47d7ac

wof_player_self_index_probe.js
  6211a575d50069c369a56baac913ba9d254119dc

wof_player_selector_7e_runtime_probe.js
  43edb9f3f1befc860bc4d3ba5a139dc0afe67644

wof_player_table_10cf8_xrefs.js
  624fbed13125382fac5efa3713a619c5efa62709
```

历史 incoming/edge 脚本仍保留，但不是当前 frontier。

---

## 14. 已踩坑（必须记住）

1. 68000 extension word/data 不能因为地址偶数就当 opcode。
2. `0x111B0` 曾是假入口：它其实是 `0x111AE CMP.W ...` 的 extension word。
3. raw full-ROM `ORI`/MOVE 命中没有 CFG/边界验证不可信。
4. 同一 struct offset 在不同对象类型上语义可以完全不同；`0x05F6BA` 的 `+0x7C` 就是例子。
5. `0x11C26` 会覆盖 A1，不是 selected-player data bridge。
6. `506(A5)` 是 player pointer scratch，但其远端 consumer 不是当前 dispatcher bridge。
7. `enemy+0x7E` 已有动态 0/4/8 100% 证据，不要再怀疑/重扫 selector 字段。
8. `player+0x7C` 已有 P1=0/P2=4/P3=8 100% 动态证据。
9. `0x0080F2` 已正式排除，不得复活。
10. 不要回 Focus Multiroom/HUD。

---

## 15. 当前唯一主线一句话

```text
真正 target selector 已解决：player+0x7C = 0/4/8，enemy+0x7E = 当前 P1/P2/P3 target；0x010CF8 是玩家指针表；已严格接通 state99=0 + action2A=2 → 0x010EC6 → MOVEQ #24,D0 → 0x010F48 → 0x25C8。现在先跑 wof_selector_end_to_end_proof.js 收口结构证明；若全 true，下一步做动态 causal/force-target validation，再进入 Future Danger 语义映射。
```

# WOF Future Danger AI — 项目交接 / 新对话续接说明

更新时间：2026-08-30 23:30（UTC+8）

> **这是当前唯一有效交接。** 新对话必须先完整读本文件，再检查仓库 `main` 的最新脚本；不要从头重新分析，不要让用户重新解释，不要回到 Focus Multiroom/HUD，也不要复活已经排除的 `0x0080F2` 主线。

## 0. 新对话接手规则（最重要）

用户只负责在 **`gstyphoon.js` DevTools Console** 执行测试命令并截图结果。

工作方式：

- 能直接修改 GitHub 就自己修改。
- 尽量每次只给用户 **一条准确命令 + 预期结果**。
- 不要要求用户手工改 JS。
- 不要调 HUD；当前主线是 ROM AI / target selector 逆向。
- 不要继续 Focus Multiroom。
- 不要重新让用户解释项目历史。
- 新 Worker / 新房间时优先使用自恢复脚本，不要让用户重跑十几步。

当前进度主观估计约 **80%–85%**：AI dispatch 架构已经解开，剩下核心是把 dispatcher 上游接到真正的 P1/P2/P3 selector。

---

## 1. 项目最终目标

游戏：**吞食天地II / Warriors of Fate / WOF / 三国志II**，版本 **WOF World 921002 / MAME `wofr1`**。

目标：Future Danger AI（观察/预测/HUD），不是自动操作。

```text
ROM 固定 AI / 招式逻辑
+ 当前 CPS RAM
+ enemy type/state/action/position
+ target/focus/未来攻击起手/active/projectile
→ 预测未来约 0~1000ms
→ 判断未来攻击真正威胁 P1/P2/P3 中谁
→ 只有真正需要躲时才提示
→ 后续 Future Danger Map + Safe Path
```

用户最在意：**减少误报**。如果怪实际准备打 P2，不能因为 P1 离得近就一直提示 P1。

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

关键 RAM：

```text
P1 = 0xFFBE1C
P2 = 0xFFBEFC
P3 = 0xFFBFDC
player stride = 0xE0

enemy pool = 0xFFC0BC
enemy stride = 0xE0
20 slots
```

ROM live image 已定位，通常 `swap16`；缓存：

```js
self.__WOF_ROM_LOC_CACHE
```

网页 live ROM 与旧 offline DB 地址关系已确认：

```text
live = offline + 0x34
```

不要再做一次性同步 256MB HEAP 扫描；已有分片定位/缓存。

---

## 3. 已完成但不要再作为主线的方向

### 3.1 Focus Multiroom / enemy struct target 字段统计

已经做过多轮动态统计，结论：**没有证据证明 enemy E0 struct 内存在一个简单固定字段 `enemy+?? = P1/P2/P3 target`**。

已排除/弱化：

```text
+0x3A：经常装玩家 handle，但 future-motion 相关为负，不是持续 chase target
+0x6A：同样负相关，更差
+0x68：弱间接关联
+0x9C：位置/X 混杂假候选
```

不要继续铺房间或调 Focus Multiroom 阈值。

### 3.2 动态 movement/action 字段

曾锁到：

```text
enemy +0x3E / +0x42
```

对未来运动方向预测非常强（meanToward≈0.998 / winRate≈1），但后来语义判断为 **movement-vector / action movement**，不是 P1/P2/P3 的绝对 target XY。

另一个动态 byte 字段与 handler 映射高度相关（约 98.9%），但：

- dispatcher 附近没有直接读取；
- direct/alias/overlap writer 扫描在真实 handler CFG 中均为 0；

因此现在把它视作 **同步 action/status 字段**，不要再当真正 dispatcher state 输入。

### 3.3 `0x0080F2` 已正式排除主线

历史候选：

```text
live 0x0080F2
offline 0x0080BE
P1/P2/P3 都有引用
CMP-family = 8
```

但最终正确入口解析后：

```text
625 level2 pointers
348 unique real handlers
扩展真实 direct-call graph
→ 0x0080F2
handlerPaths = 0
```

并且 `0x0080F2` 也不在 level2 handler table 中直接命中。

**结论：不要再追 `0x0080F2`。**

---

## 4. 当前真正解开的 AI dispatch 架构

最关键的新事实：早期把 47 个 type entry 当“函数入口”是错的。

真实结构是两级表：

```text
enemy type
→ type table
→ 每个 type 的二级 state/handler pointer table
→ D0 作为已乘4的 byte offset
→ 取最终 handler
```

已解析：

```text
47 types
625 level2 pointers
348 unique real handlers
后续扫描器可达 routine 数约 356（不同 decoder/root policy 下曾扩到约 376）
```

### 两个真实 dispatcher

#### live `0x0025B6`

```text
0x25B6  MOVE.W 32(A0),D1
0x25BA  ADD.W  D1,D1
0x25BC  ADD.W  D1,D1
0x25BE  MOVE.L 28(PC,D1.W),A4
0x25C2  MOVE.L 0(A4,D0.W),A4    <<< level2 dispatch
0x25C6  RTS (word 0x4E75)
```

#### live `0x0025C8`

```text
0x25C8  MOVE.W 32(A0),D1
0x25CC  ADD.W  D1,D1
0x25CE  ADD.W  D1,D1
0x25D0  MOVE.L 10(PC,D1.W),A4
0x25D4  MOVE.L 0(A4,D0.W),A4    <<< level2 dispatch
0x25D8  BRA 0x00247C
```

含义：

```text
32(A0) = enemy type
D1 = type * 4
PC-relative table around 0x25DC → A4 = 该 type 的二级表
D0 = 进入 dispatcher 前已经准备好的 state byte-offset（通常 0,4,8,12,16...）
0(A4,D0.W) → A4 = final handler
```

**重要纠正：D0 不是在 dispatcher 内生成；D0 是上游路径传进来的。**

---

## 5. Dispatcher incoming edge 已经找到

脚本：

```text
wof_dispatch_incoming_edges.js
commit: 44899fa29b10c97387ba49bc07ac2e055d3e4315
```

结果：

```text
directIncomingEdges = 44
edges25B6 = 4
edges25C8 = 40
pointer32Refs = 17
fallthroughEdges = 0
```

也就是说 `0x25B6 / 0x25C8` 并不是只有普通函数 caller；全 ROM 中有大量直接 JSR/JMP/branch 入口。

很多入口前面直接出现：

```text
MOVEQ #0,D0
MOVEQ #4,D0
MOVEQ #8,D0
MOVEQ #12,D0
MOVEQ #16,D0
MOVEQ #20,D0
...
→ JSR/JMP 0x25B6/0x25C8
```

这非常像：**上游 AI 代码直接选择下一 state offset，然后进入共享 type→handler dispatcher。**

---

## 6. 当前最前沿：44 条 edge 上游 selector 扫描

脚本：

```text
wof_dispatch_edge_selector_scan.js
commit: 1603f88ff635b5cbac45f61cc643657e39d7ede2
```

它对 44 条 incoming edge 的局部真实线性路径统计：

- P1/P2/P3 引用
- CMP
- Bcc
- D0 root / transform

当前 verdict：

```text
edges = 44
edgesWithPlayerRefs = 0
edgesWithCmp = 1
strongPlayerCmpEdges = 0
nonImmediateD0 = 1
```

含义：

- dispatcher 入口附近本身 **没有直接 P1/P2/P3 selector**；
- 真 selector 还在更上游；
- 目前只剩 **1 条带 CMP 的 edge** + **1 条非 immediate D0 edge** 值得先排干净；
- 其它绝大多数 edge 是直接 `MOVEQ #stateOffset,D0`。

**当前不要重新扫 44 条大表。**

---

## 7. 新对话第一件事：只看 1–2 条 interesting edge

已新增一键恢复脚本：

```text
wof_resume_dispatch_selector.js
commit: 007f9058dea6ce72f308d10eeede9f40fe6dbf20
```

它会自动恢复：

```text
ROM cache
→ incoming edges
→ edge selector scan
→ 只打印 cmp>0 或 non-immediate D0 的 1–2 条 edge
```

新房间 / 新 Worker 在 `gstyphoon.js` Console 只执行：

```js
await fetch('https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/wof_resume_dispatch_selector.js?x='+Date.now(),{cache:'no-store'})
  .then(r=>r.text()).then(s=>(0,eval)(s));
```

预期最终：

```text
=== RESUME FRONTIER VERDICT ===
=== ONLY INTERESTING EDGES ===
```

### 下一步决策

拿到那 1–2 行后：

#### A. CMP edge 是真实决策链

沿该 edge 的 **CFG predecessors 向上扩一层**，找：

```text
P1/P2/P3 或 player table/player stride 引用
+ CMP/距离/状态判断
→ 选择 D0
→ dispatcher
```

#### B. nonImmediateD0 只是 `D0→D0` / 假 provenance

立即排除，不要浪费时间；然后从 44 条 edge 的 **predecessor/upstream routine** 统一向上扩一层。

### 真正需要寻找的最终链

```text
P1/P2/P3（或共享 player-pointer table）
↓
目标/距离/状态比较
↓
决定 action/state offset D0
↓
0x25B6 / 0x25C8
↓
type-specific level2 handler
```

找到 selector 后，再解最终目标玩家留在哪个 A/D 寄存器或 RAM 字段，并做 2P/3P 动态验证。

---

## 8. 最近关键脚本 / commit（按当前价值）

```text
wof_resume_dispatch_selector.js
  007f9058dea6ce72f308d10eeede9f40fe6dbf20

wof_dispatch_edge_selector_scan.js
  1603f88ff635b5cbac45f61cc643657e39d7ede2

wof_dispatch_incoming_edges.js
  44899fa29b10c97387ba49bc07ac2e055d3e4315

wof_dispatch_caller_d0_trace.js
  95a3828547a9026a039224a4ec8fb5bc2dc92f4d

wof_dispatch_d0_trace.js
  77b9988ef38d126ec8648bae46849ed50627176d

wof_state_writer_overlap_v4.js
  e801e4428d3447d110abbd7b75a8084ea73f9add

wof_state_writer_alias_v3.js
  1934cd338b17f821c5e0b93b804d9f5e43dd7714

wof_rom_focus_level2_tables.js
wof_rom_focus_handler_trace.js
wof_rom_focus_selector_scan.js
wof_rom_focus_selector_ea.js
```

旧脚本仍有历史价值，但新对话不要从旧 Focus/0x80F2 路线重启。

---

## 9. 已经踩过的坑（不要重复）

1. 47 个 type entry 不是函数入口，而是一级/二级 dispatch 数据结构的一部分。
2. `MOVEA.L 0(A4,D0.W),A4` 不是简单 A4 kill；它是二级 handler 取值。
3. 不要只扫 32-bit P1/P2/P3 地址；68000 可能用 abs.W / player table / stride。但当前 edge 附近仍没有 direct player refs。
4. 不要把 ROM 任意偶地址都当指令边界；之前出现过 extension word 被误解成 `ORI.B`。
5. raw 全 ROM opcode hit 没有 CFG 验证时不可信。
6. dynamic correlation ≠ dispatcher field；前面的高映射 action/status 字段已经证明这一点。
7. 新脚本曾出现 JS 重复声明语法错误；后续生成脚本尽量保持简单并做语法自检思维。
8. 不要回 DOM HUD；游戏 HUD 已经走 WebGL canvas，但本阶段不碰 HUD。

---

## 10. 对下一位 ChatGPT 的明确要求

接手后请这样做：

1. **先完整读 `WOF_AI_HANDOFF.md`。**
2. 检查 `main` 最新的：
   - `wof_resume_dispatch_selector.js`
   - `wof_dispatch_edge_selector_scan.js`
   - `wof_dispatch_incoming_edges.js`
3. 不要重新分析 `0x0080F2`。
4. 不要继续 Focus Multiroom。
5. 不要让用户重跑旧 35/40/45 秒动态 probe，除非最终 selector 动态验证需要。
6. 当前第一步只拿到 `=== ONLY INTERESTING EDGES ===` 的 1–2 行。
7. 然后沿真实 CFG predecessor 向上扩，不要再扫整个 ROM。
8. 用户每次尽量只执行一条 Console 命令。

当前唯一主线一句话：

```text
44 dispatcher incoming edges 已锁定；入口附近无 direct P1/P2/P3；现在只排 1 条 CMP edge + 1 条 non-immediate D0 edge，然后向上扩 predecessor，找到真正 player selector → D0 → 0x25B6/0x25C8。
```

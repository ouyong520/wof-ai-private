# WOF Future Danger AI — 最新交接 / 新房间续接说明

更新时间：2026-08-31
仓库：`ouyong520/wof-ai-private`

> **新对话第一份必须完整读本文件。**
> 完整历史、所有关键结论、踩坑和脚本时间线见：`WOF_AI_MASTER_PROGRESS.md`。
> 不要从头重做，不要让用户重新解释，不要回 Focus Multiroom / HUD，不要复活 `0x0080F2`。

---

## 0. 用户工作方式

用户只负责在 **`gstyphoon.js` DevTools Console** 执行一条测试命令并回传 JSON / 截图。

原则：

- 能直接修改 GitHub 就自己修改。
- 每轮尽量只给用户一条准确命令。
- 不要求用户手工编辑 JS。
- 新房间 / 新 Worker 先恢复 ROM cache，不重跑历史 probe。
- 关键 68000 结论必须 strict validate；不要把任意偶地址当指令边界。

---

## 1. 最终目标

Future Danger AI：根据 ROM AI + CPS RAM 预测未来约 0~1000ms 的真实威胁目标 P1/P2/P3，并减少误报。

不是自动操作；最后才回 Future Danger HUD / Map / Safe Path。

---

## 2. 固定地址

```text
P1 = 0xFFBE1C
P2 = 0xFFBEFC
P3 = 0xFFBFDC
player stride = 0xE0

enemy pool = 0xFFC0BC
enemy stride = 0xE0
20 slots
```

ROM cache：

```js
self.__WOF_ROM_LOC_CACHE
```

live/offline：

```text
live = offline + 0x34
```

---

## 3. 已锁定 dispatcher

### 0x25B6

```text
32(A0) enemy type
→ type * 4
→ type-specific level2 table
→ 0(A4,D0.W)
→ final handler
```

### 0x25C8

同样结构，最后继续 BRA 0x247C。

核心事实：

```text
D0 = 上游 AI 已经选好的 state byte offset
```

不是 dispatcher 内生成。

44 direct incoming edges 已确认：

```text
44 total
4 → 0x25B6
40 → 0x25C8
```

不要重扫 44 edge。

---

## 4. 已排除主线

不要再追：

```text
Focus Multiroom
HUD
0x0080F2
A0+0x40/+0x44 target XY writer
AD5A / low4 classification
0x11C26 作为 selector→dispatcher bridge
```

`0x11C26` 内部会覆盖 A1，不保留传入 selected-player A1。

---

## 5. 真正 P1/P2/P3 selector 已锁死

### 玩家 pointer table

主表：

```text
0x010CF8 = P1 0xFFBE1C
0x010CFC = P2 0xFFBEFC
0x010D00 = P3 0xFFBFDC
```

### 玩家自身 self-index

动态 101/101 samples：

```text
P1+0x7C = 0
P2+0x7C = 4
P3+0x7C = 8
```

### 敌人当前 target selector

动态 301 samples / 3 active enemy slots：

```text
enemy+0x7E ∈ {0,4,8}
valid048Pct = 1.0
```

因此语义已锁定：

```text
enemy+0x7E = 当前目标玩家 slot offset
0 → P1
4 → P2
8 → P3
```

### selector 使用

最清楚的一处：

```text
0x010E66 MOVE.W 126(A0),D1
0x010E6A LEA 0x010CF8,A1
0x010E6E MOVE.L 0(A1,D1.W),A1
```

即：

```text
enemy+0x7E
→ D1.W
→ P1/P2/P3 pointer table
→ A1 = selected player
```

随后：

```text
0x010E72 MOVE.W A1,506(A5)
```

`506(A5)` 是 selected-player 低 16-bit pointer scratch；已找到多处 reader 会 `MOVEA.W` 恢复为真正 player pointer。

---

## 6. selector 附近真实状态机

selector 后不是直接进 dispatcher，而是两层状态分派。

### 第一层：A0+0x99

```text
0x10EA8 MOVE.B 0x99(A0),D0
0x10EAC MOVE.W table(PC,D0.W),D1
0x10EB0 JMP table(PC,D1.W)
```

9 项 → 5 个 unique block：

```text
0x10BBC
0x10BD0
0x10BE4
0x10BF8
0x10C0C
```

### 第二层：A0+0x2A

5 个 block 都是同一结构：

```text
MOVE.B 42(A0),D0
MOVE.W table(PC,D0.W),D1
JMP table(PC,D1.W)
```

合并后 9 个 unique final targets：

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

## 7. 已严格证明的一条 state → D0 → dispatcher 路线

最新关键结果：

```text
state99=0
→ 0x010BBC

action2A=2
→ table 0x010BCA = 0x02FE
→ 0x010EC6
```

然后 exact-word 全通过：

```text
0x10EC6 ...
→ 0x10F40 MOVE.W #0x0600,42(A0)
→ 0x10F46 MOVEQ #24,D0
→ 0x10F48 JMP 0x25C8
```

verdict：

```text
allState2APatternsValid = true
routes = 36
uniqueFinalTargets = 9
routesTo10EC6 = 1
strictBridge10EC6To10F48 = true
bridgeD0 = MOVEQ #24,D0
dispatcher = 0x25C8
provenRoute = state99=0, action2A=2 -> 0x10EC6 -> 0x10F48 -> 0x25C8
```

这意味着 selector 所在同一区域的状态机已经第一次严格接到真实 dispatcher。

---

## 8. 另一条本地 dispatcher edge

```text
0x10FA0 MOVEQ #8,D0
0x10FA2 JSR 0x25B6
```

真实存在，但尚未像 `0x10F48→0x25C8` 那样完成完整 state99/action2A route 归属。

后续需要补。

---

## 9. 当前静态证明边界

已经锁死：

```text
player+0x7C = P1/P2/P3 self index 0/4/8
enemy+0x7E = 当前 target selector
+0x7E → player table → A1 selected player
selector 邻近存在 state99/action2A 两层 AI state machine
其中一条 state route → D0=24 → 0x25C8
```

还没完全闭环的是：

```text
当前 selector 值 0/4/8
→ 哪些 target-dependent compare / decision
→ 如何影响 state99 / action2A
→ 最终选哪个 D0 / handler
```

所以不要再寻找“selector 在哪”；selector 已找到。下一阶段是找 selector **如何影响决策**。

---

## 10. 当前最新脚本：先跑这个

```text
wof_selector_end_to_end_proof.js
commit: 31dea3a6a1a89799ba86724321c7a5db618d5596
```

用户尚未回传它的最终 JSON。

新房间恢复后，当前第一测试应执行：

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

如果：

```text
endToEndStructuralProof = true
```

则静态结构层正式收口，下一步转动态因果 / target-dependent decision，不再继续结构性找 selector。

---

## 11. 新房间恢复

如果 Worker 状态丢失，先执行：

```js
await fetch('https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/wof_resume_dispatch_selector.js?x='+Date.now(),{cache:'no-store'}).then(r=>r.text()).then(s=>(0,eval)(s));
```

恢复成功后直接跑 `wof_selector_end_to_end_proof.js`。

不要重跑 Focus、0x80F2、旧 44-edge scan 或旧几十秒 probe。

---

## 12. 关键脚本 / commit

```text
wof_selector_state2a_dispatch_bridge.js
  7cf1e1eda14b30a5fd520491c1ce990e1a4cdee6

wof_selector_end_to_end_proof.js
  31dea3a6a1a89799ba86724321c7a5db618d5596

wof_selector_state99_jump_cfg.js
  5178563dd8600d83a4882bc02f3a9c6680b67bfb

wof_selector_10e66_dispatch_local_raw.js
  b305c777e8db19654c4a259174d6023cd617ff72

wof_player_selector_7e_runtime_probe.js
  43edb9f3f1befc860bc4d3ba5a139dc0afe67644

wof_player_self_index_probe.js
  6211a575d50069c369a56baac913ba9d254119dc

wof_player_selector_7e_alias_writers.js
  6102e57d09c9bcab65dd72a4ec8b0e4af0764d4c

wof_player_selector_7c_alias_writers.js
  79010c8cb59ec702b3fa26f143f53a01bca75606

wof_player_table_10cf8_xrefs.js
  624fbed13125382fac5efa3713a619c5efa62709

wof_resume_dispatch_selector.js
  最新 main 版本已改到当前 frontier
```

完整时间线见 `WOF_AI_MASTER_PROGRESS.md`。

---

## 13. 当前进度

工程进度估计：**90%–93%**。

已经完成：dispatcher、真实 target selector、player table、selected player、两层状态机、至少一条 D0→0x25C8 严格路线。

剩余：

```text
1. end-to-end structural proof 最终确认
2. selector→state99/action2A 的 target-dependent 因果决策
3. 0x10FA2→0x25B6 路线归属
4. 动态因果验证
5. handler / attack / future danger 语义映射
6. 最后回 HUD / Future Danger Map
```

---

## 14. 一句话主线

```text
enemy+0x7E = P1/P2/P3 target selector
→ 0x10CF8 player table
→ selected player A1
→ target-dependent AI decision（当前最后缺口）
→ A0+0x99 state
→ A0+0x2A action
→ D0 state offset
→ 0x25B6 / 0x25C8
→ type-specific final handler
→ Future Danger
```

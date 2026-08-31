# WOF Future Danger AI — 最新交接 / 新房间续接说明

更新时间：2026-08-31
仓库：`ouyong520/wof-ai-private`
游戏：WOF / Warriors of Fate / 吞食天地II / 三国志II，World 921002 / MAME `wofr1`

> 新对话先读本文件。不要从头重做，不要回 Focus Multiroom / HUD，不要复活 `0x0080F2`，不要重扫 44 dispatcher incoming edges。

---

## 0. 用户工作方式

用户只负责在 `gstyphoon.js` DevTools Console 执行每轮一条命令，然后回传 JSON / 截图。

- 能直接改 GitHub 就自己改。
- 不要求用户手工编辑 JS。
- 新房间 / 新 Worker 优先用 `wof_resume_dispatch_selector.js` 恢复。
- 重要 68000 结论只能从真实 instruction boundary / exact raw / runtime 验证得出；不能把任意偶地址当 opcode。

---

## 1. 最终目标

Future Danger AI：结合 ROM AI + CPS RAM，预测未来约 0~1000ms 哪个敌人真正会威胁 P1/P2/P3 中谁，并识别攻击 startup / active / recovery，最终用于 Future Danger Map / Safe Path。不是自动操作。

---

## 2. 固定 RAM

```text
P1 = 0xFFBE1C
P2 = 0xFFBEFC
P3 = 0xFFBFDC
player stride = 0xE0

enemy pool = 0xFFC0BC
enemy stride = 0xE0
slots = 20
```

ROM cache：`self.__WOF_ROM_LOC_CACHE`。旧 offline DB → live ROM：`live = offline + 0x34`。

---

## 3. P1/P2/P3 target selector 已完全锁死

玩家 identity 动态严格证明：

```text
P1+0x7C = 0
P2+0x7C = 4
P3+0x7C = 8
```

敌人 target selector 动态严格证明：

```text
enemy+0x7E = 0 / 4 / 8
0 → P1
4 → P2
8 → P3
```

player pointer table：

```text
0x010CF8 = P1
0x010CFC = P2
0x010D00 = P3
```

严格 selector load：

```text
0x010E66 MOVE.W 126(A0),D1
0x010E6A LEA 0x010CF8,A1
0x010E6E MOVE.L 0(A1,D1.W),A1
```

即 `enemy+0x7E → selected P1/P2/P3 → A1`。

不要再找 selector。

---

## 4. selected-player pointer cache 新主线

动态 + 静态已证明：

```text
enemy+0x6A = selected-player pointer low16
P1 = BE1C
P2 = BEFC
P3 = BFDC
```

三个真实 reader：

```text
0x0112AA
0x0065E2
0x006834
```

最强 bridge：

```text
0x006834 MOVEA.W 106(A0),A1
0x006838 CMPI.B #4,41(A1)
0x00683E BEQ 0x006850
0x006850 MOVEQ #0,D0
0x006852 MOVE.B 42(A0),D0
0x006856 MOVE.W table(PC,D0.W),D1
0x00685A JMP indexed
```

所以已经严格成立：

```text
enemy+0x6A
→ selected player
→ selectedPlayer+0x29 compared with 4
→ enemy+0x2A action dispatch
```

不要给 selectedPlayer+0x29 强行命名；目前只称 selected-player state/flag byte。

---

## 5. action2A=2 → D0=16/20 已锁死

`0x6850` action table 只有两项：

```text
action2A=0 → 0x6862
action2A=2 → 0x6904
```

在 action2A=2 路径：

```text
0x006A10 MOVEQ #16,D0
0x006A12 JSR 0x25C8

0x006A62 MOVEQ #20,D0
0x006A64 JSR 0x25C8
```

因此 D0 provenance 是 exact opcode proof，不是推测。

---

## 6. dispatcher 语义修正：0x25C8 选的是 descriptor，不是代码 handler

原先把 type-specific level2 entry 称为 final handler，这个命名已修正。

`0x25C8`：

```text
enemy type
→ type table
→ type-specific table
→ 0(A4,D0.W)
→ A4 = action descriptor pointer
→ BRA 0x247C
```

`0x247C` 从真实边界解出：

```text
0x247C MOVEA.L (A4)+,A6
0x247E MOVE.L  (A4)+,0x30(A0)
0x2482 MOVE.W  (A4)+,D1
```

如果 D1 bit15=0：timer 写 enemy+0x34，next descriptor 是 inline record。

如果 D1 bit15=1：

```text
0x249E ANDI.W #0x7FFF,D1
0x24A2 timer → enemy+0x34
0x24A6 MOVEA.L (A4),A4
0x24A8 A4 → enemy+0x2C
```

即显式 next-descriptor pointer。

A6 不是代码地址，而是 frame/payload end pointer：

```text
0x2490 A6 → enemy+0x12
0x2494 LEA enemy+0x6C,A4
0x2498 MOVE.W -(A6),(A4)+
0x249A MOVE.L -(A6),(A4)+
```

所以 frameEnd 前 6 bytes 被复制到 enemy+0x6C..+0x71。

---

## 7. type35 D0=16/20 descriptor 已完整解析

Type35 table base：

```text
0x081774
shared by type7/type35
```

合法连续 D0 prefix 只有：

```text
0  → 0x81876
4  → 0x81884
8  → 0x818CA
12 → 0x81906
16 → 0x81864
20 → 0x81856
24 → 0x81892
```

D0=28 开始是机器数据，不允许继续把后面当 table。

### D0=16

```text
descriptor = 0x81864
frameEnd = 0x825D0
value30 = 0
timerRaw = 0xFFFF
timer = 32767
next = 0x81864 self-loop
```

强语义：长时间 hold / self-loop descriptor。

### D0=20

```text
descriptor = 0x81856
frameEnd = 0x825D0
value30 = 0
timerRaw = 0x8010
timer = 16
next = 0x817CC
```

后续 chain：

```text
0x81856 timer16
→ 0x817CC timer1
→ 0x817D6 timer5
→ 0x817E0 timer5
→ 0x817EA timer5
→ 0x817F4 timer5
→ 0x817FE timer5
→ 0x81808 timer5
→ 0x817D6 loop
```

首次进入约 47 tick；之后约 30-tick loop。

---

## 8. D0=20 已有历史实战 startup 证据

旧 Multiroom / Future AI 数据并不是当前因果 proof，但能做独立语义验证。

D0=20 chain 中的多个 type35 frame 已在旧实战里出现：

```text
531402: attack=0, startupTop=T35_F01/T35_F02
531464: attack=0, startupTop=T35_F01/T35_F02
531620: attack=0
531690: attack=0, startupTop=T35_F01/T35_F02
```

因此当前最强语义是：

```text
D0=20 = pre-active / attack startup descriptor chain
```

不是 active attack，也不像 recovery。仍需新的 live RAM 因果顺序把 `selected player → action2A → D0=20 descriptor` 抓在同一个事件上。

---

## 9. 旧 state99/action2A structural route 仍有效

另一条已严格证明的 structural route：

```text
state99=0
action2A=2
→ 0x010EC6
→ 0x10F40 MOVE.W #0x0600,42(A0)
→ 0x10F46 MOVEQ #24,D0
→ 0x10F48 JMP 0x25C8
```

注意 action2A 入路径时是 2，但 0x10F40 会写 word `0x0600`，所以之后 byte +0x2A 变 6。不要混淆 pre/post action value。

`0x10FA2 → 0x25B6` 仍第二优先级，不要抢当前主线。

---

## 10. 动态 transition 已知结论

干净 transition 已证明：target reselection 常与 action transition boundary 同帧/近帧发生，state99 不要求变化。

`enemy+0x6A` 会随 target 同步变成目标玩家低16 pointer：BE1C/BEFC/BFDC。

16ms/20ms JS sampling 只能证明时间窗口，不能单凭同一个 sample 宣称 exact CPU instruction order。

---

## 11. 当前房间最新情况

`wof_type35_descriptor_chain_runtime_v1.js` 的静态 descriptor proof 全通过，但当前 10 秒窗口：

```text
type35SlotsSeen = []
eventCount = 0
```

这只表示当前房间当时没有 type35 enemy，不是链失败。

因此下一步改成 **全类型 runtime descriptor correlation**，不再等 type35。

---

## 12. 当前下一条脚本

```text
wof_d016_20_descriptor_runtime_alltypes_v1.js
```

它会对当前所有 active enemy type：

```text
从 type table 自动算各自 D0=16 / D0=20 descriptor
+ 实时读取 target7E
+ ptr6A selected player
+ selectedPlayer+0x29
+ state99
+ action2A
+ enemy+0x12/+0x2C/+0x30/+0x34/+0x6C..+0x71
```

只在语义状态/descriptor 改变时记录，不会每个 timer tick 灌爆 JSON。

目标是抓到：

```text
selected player condition
→ action2A transition
→ D0=16 / D0=20 descriptor fingerprint
```

的同一实时事件。

---

## 13. 新房间恢复

先运行：

```js
await fetch('https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/wof_resume_dispatch_selector.js?x='+Date.now(),{cache:'no-store'}).then(r=>r.text()).then(s=>(0,eval)(s));
```

当前 resume 应显示：

```text
wof-resume-dispatch-selector-v12
nextScript = wof_d016_20_descriptor_runtime_alltypes_v1.js
```

不要重跑过去几十个旧 probe。

---

## 14. 绝对不要重做

```text
Focus Multiroom
HUD 调整
0x0080F2
44 dispatcher incoming edge scan
重新寻找 enemy+0x7E
重新证明 player+0x7C
重新证明 0x10CF8 player table
0x11C26 bridge
0x05F6BA
A0+0x40/+0x44 target XY
AD5A / low4 classification
全 ROM raw-even-address opcode 扫描
把 A5 默认当 player
把 A5+1FA 当唯一主线
```

---

## 15. 当前一句话主线

```text
enemy+0x7E target P1/P2/P3
→ enemy+0x6A selected-player pointer cache
→ selectedPlayer+0x29 compare
→ enemy+0x2A action dispatch
→ action2A=2 → 0x6904
→ D0=16 / D0=20
→ 0x25C8 type-specific descriptor selection
→ 0x247C descriptor engine
→ D0=20 pre-active/startup chain
→ 实时 target-aware Future Danger
```

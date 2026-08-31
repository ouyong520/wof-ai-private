# WOF Future Danger AI — 最新交接 / 新对话 START HERE

更新时间：2026-08-31
仓库：`ouyong520/wof-ai-private`
项目：Project A — Browser/MAME Future Danger
游戏：Warriors of Fate / 吞食天地II / 三国志II，World 921002 / MAME `wofr1`

> **新对话第一步：读本文件，再读 `WOF_AI_CURRENT_FRONTIER.md` 和 `wof_resume_dispatch_selector.js`。不要从头重做。**
>
> 本项目与 `ouyong520/wof-winkawaks-bridge` 是两个项目；不要把 WinKawaks 的 M3/M4 / LOCAL_TO_WEB 数据混进来。

---

## 0. 用户协作方式 / 强制协议

用户主要负责在 live `gstyphoon.js` Worker Console 执行测试，然后发回 JSON / 截图。

必须遵守：

- 每轮只给 **一条可执行 Console 命令**。
- 第一行必须有唯一 copy ID，例如 `// WOF-034`。
- Assistant 自己管理 ID ↔ script/version/test。
- 收到结果后，**先校验** `copyId/project/version/marker`，不匹配就判为旧结果/发错，不作当前证据。
- 能直接改 GitHub 就自己改，不要求用户手工编辑 JS。
- 用户经常换房间，所以优先设计 coverage-adaptive 测试，不要让固定类型 validator 白跑。
- 默认测试脚本 read-only；`ramWrites=0`。

---

## 1. 最终目标

Future Danger AI：

```text
ROM AI / descriptor / state
+ CPS RAM live enemy data
+ enemy+0x7E 当前 P1/P2/P3 target
+ enemy/target XY
+ 攻击前 terminal state
→ 预测未来约0~1000ms真实威胁
→ 判断打谁、来自哪侧、多久进入 ACTIVE
→ Future Danger Map / Safe Path
```

不是 auto-play。

---

## 2. 固定地址 / 已锁死 ground truth

```text
P1 = 0xFFBE1C
P2 = 0xFFBEFC
P3 = 0xFFBFDC
player stride = 0xE0

enemy pool = 0xFFC0BC
enemy stride = 0xE0
slots = 20
```

玩家 self index：

```text
P1+0x7C = 0
P2+0x7C = 4
P3+0x7C = 8
```

敌人 target selector：

```text
enemy+0x7E = 0/4/8 → P1/P2/P3
```

**+0x7E 永远是 authoritative live target。**

player pointer table：

```text
0x010CF8 = P1
0x010CFC = P2
0x010D00 = P3
```

selector strict route：

```text
0x010E66 MOVE.W 126(A0),D1
0x010E6A LEA 0x010CF8,A1
0x010E6E MOVE.L 0(A1,D1.W),A1
```

`enemy+0x6A` 是 selected-player pointer cache low16，只有值严格等于 `BE1C/BEFC/BFDC` 时才作为 supporting evidence，不替代 +0x7E。

---

## 3. dispatcher / descriptor 已解决，不要重做

AI 两层 state/action：

```text
enemy+0x99
→ state table
→ enemy+0x2A
→ action table
→ AI routine
```

严格 route 之一：

```text
state99=0 / action2A=2
→ 0x10EC6
→ 0x10F40 writes #0600 to enemy+0x2A word
→ 0x10F46 MOVEQ #24,D0
→ 0x25C8
```

`0x25C8` 选择的是 **descriptor data**，不是 direct code handler。

`0x247C` 是 descriptor consumer：

```text
descriptor +0  long → frame/payload end pointer → enemy+0x12
           +4  long → enemy+0x30
           +8  word → timer / flag
bit15 clear → inline next descriptor
bit15 set   → explicit next pointer at +0x0A
next → enemy+0x2C
timer → enemy+0x34
frameEnd payload tail → enemy+0x6C/+0x6E...
```

**frameEnd 不是代码地址。**

Dispatcher incoming edges 已完整：44 direct edges；不要重扫。

---

## 4. ACTIVE 统一约定

```text
enemy+0x70 U16: 0 → nonzero
```

作为 ACTIVE-start convention。

它不是 exact damage / hitbox onset，所以 leadMs 只能说“距离 ACTIVE 起点”，不能说“距离命中”。

---

## 5. 已验证 production-shadow：T16 exact terminal B4

Broad T16 FAST/MID 已经被 V25 的 late/hard miss 否定，不能再当 production。

V26 找到真正 terminal phase：

```text
type16
attack=0
body=4856
frameEnd=0x851AE
next=0x84C44
value30=0xFFFF
timer34=1
action2A=4
b2B=4
state99 ∈ {0,2,4}
```

规则：

```text
T16_6432_B4_40
```

WOF-030 prospective：

```text
65/65 strict <=40ms
65/65 attack6432
65/65 target stable
65/65 side stable
lead≈9.0..21.1ms
0 late
0 hard miss
```

WOF-032 又 2/2 strict：10.0 / 19.8ms，均 attack6432。

所以：

```text
T16 exact B4 = production-shadow
```

注意目前 T16 entry side 的强样本仍主要是 LEFT，RIGHT symmetry 尚缺直接强覆盖。

---

## 6. T33/T34 attack3232：当前最强新候选

WOF-031 mining 找到 clean countdown。

### T34

```text
type34
attack0
body2872
FE8811E
NX879E2
V100000
P6C2784
action2A=4
b2B=2
state99 2/4
TM6
```

WOF-032 prospective：

```text
3/3 strict
lead 99.9 / 101.6 / 102.4ms
attack3232 3/3
target stable 3/3
side stable 3/3
```

状态：`production-shadow-candidate`。

### T33

```text
type33
attack0
body2872
FE867BA
NX85ECE
V100000
P6C2784
action2A=4
b2B=2
state99 2/4
TM6
```

WOF-032 prospective：

```text
5/5 strict
lead 100 / 100 / 100.5 / 107.4 / 108.4ms
attack3232 5/5
target stable 5/5
side stable 5/5
LEFT 4 + RIGHT 1
```

状态：`production-shadow-candidate`。

需要更多独立覆盖后再升 production-shadow。

---

## 7. T30：broad 规则已降级

旧：

```text
type30 + attack0 + body1800 + state99=0 + action2A=0 + b2B=0
```

早期数据很强，但 WOF-032 出现：

```text
10 evaluable
8 strict
2 hard miss
```

两个 hard miss：

```text
TM1, absDx190
TM1, absDx151
```

而 TM1 strict 样本曾有：

```text
absDx125 / 89 / 51
```

所以 broad T30 不能 production。

WOF-033 原计划拆：

```text
TM3~6
TM1 + absDx<=130
TM1 + absDx>130 diagnostic
```

但该房间所有 exact T30 split match 都是0，因此没有新证据。

**absDx130 只是 provisional diagnostic split，不是 hitbox，不是 exact attack range。**

---

## 8. T27 / T23

WOF-031 发现：

### T27 → attack5064

```text
BODY5048 / FE9A32C / NX99CB0 / VFFFF / TM1 / P6C5056
```

B4 曾出现在约20ms和约100ms前；尚缺足够 prospective coverage。

### T23 → attack5888

```text
BODY4936 / FE84060 / NX83C60 / VFFFF / TM1 / P6C4944
```

同样缺 coverage。

状态都保持 discovery/prospective，不得直接 production。

---

## 9. WOF-033 最新结果 / 为什么切换策略

正确 WOF-033：

```text
duration ≈120000.8ms
interval 10ms
enemySamples 32989
ACTIVE edges 291
signals 0
```

主要 room types：

```text
T24 13492
T18 8544
T21 8746
T30 1724
```

但所有固定 validator exact match：0。

这不是规则失败，是 **coverage=0**。

工程结论：以后不能继续让用户每换房间就固定等 T16/T33/T34/T27/T23；否则可能白跑120秒。

---

## 10. 当前 next：WOF-034 adaptive terminal miner

当前 resume 已更新：

```text
version = wof-resume-dispatch-selector-v44
nextCopyId = WOF-034
nextScript = wof_future_danger_adaptive_terminal_miner_v34.js
nextMarker = === WOF FUTURE DANGER ADAPTIVE TERMINAL MINER V34 JSON ===
```

WOF-034 的作用：**无论房间有什么 enemy type，都能产出攻击前证据。**

它会对每个真实 ACTIVE edge：

```text
抓最后 attack=0 terminal state
记录最近 pre-ACTIVE transition chain
回看约20/50/100/150/250/500ms fingerprint
按 type + actual attack 聚合
target/side stability 一起统计
```

同时 opportunistically 验证已知 T16/T33/T34。

目标优先挖当前常见：

```text
T24 / T18 / T21 / T30
```

WOF-034 mining 出来的新 signature **只能算 discovery evidence**；下一轮必须另写 prospective validator 才能升级。

---

## 11. 新对话接手后的实际工作

按顺序：

1. 读本文件。
2. 读 `WOF_AI_CURRENT_FRONTIER.md`，里面有完整过程和 exclusions。
3. 读 `wof_resume_dispatch_selector.js`，确认 `v44 / WOF-034`。
4. 让用户跑 WOF-034。
5. 收到 JSON 后先校验 ID/version/marker/readOnly/ramWrites。
6. 分析 strongest terminal fingerprints，优先选择重复多、lead 窄、actual attack identity 稳定的候选。
7. 写下一版 prospective validator，只验证最强 2~4 个候选。
8. 规则通过独立 prospective 样本后再升 production-shadow。
9. 当 production rules 覆盖足够，再做最终 multi-enemy Future Danger Map / Safe Path。

当前 WOF-034 Console 命令：

```js
// WOF-034
await fetch('https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/wof_future_danger_adaptive_terminal_miner_v34.js?x='+Date.now(),{cache:'no-store'}).then(r=>r.text()).then(s=>(0,eval)(s));
```

运行约120秒，最后应出现：

```text
=== WOF FUTURE DANGER ADAPTIVE TERMINAL MINER V34 JSON ===
```

---

## 12. 不要重做 / 不要误判

不要重做：

```text
Focus Multiroom
HUD
0x0080F2
44 dispatcher incoming edges
selector +0x7E
player identity +0x7C
player table 0x010CF8
0x11C26
0x05F6BA
A0+0x40/+0x44 target XY
AD5A/low4
全 ROM 任意偶地址 opcode scan
```

不要误判：

```text
+0x70 = exact hitbox/damage onset       ❌
frameEnd = code                         ❌
descriptor = direct handler code        ❌
broad T16 FAST/MID = production         ❌
T16 4840 divergence = production        ❌
broad T30 = production                  ❌
absDx130 = exact attack range/hitbox     ❌
WOF-033 zero match = T33/T34 rule失败   ❌
WOF-034 mined correlation = causal proof ❌
```

---

## 13. 一句话 current frontier

```text
selector/dispatcher/descriptor 已解；
T16 exact B4 已 production-shadow；
T33/T34 3232 TM6 已 prospective 全命中候选；
T30 broad 已有 hard miss 被降级；
当前不再固定等某种 enemy，而是 WOF-034 coverage-adaptive mining，
从任何房间每个 ACTIVE edge 挖 terminal fingerprint，
再做 prospective validation 扩大 Future Danger 覆盖。
```

# WOF Future Danger AI — 当前逻辑、进度、过程与新对话交接

更新时间：2026-08-31
仓库：`ouyong520/wof-ai-private`
项目：浏览器 / MAME `wofr1` 的 Future Danger AI（Project A）
游戏：Warriors of Fate / 吞食天地II / 三国志II，World 921002

> 这是当前最重要的“新对话接手文件”。新对话不要从头逆向。先读本文件、`WOF_AI_HANDOFF.md` 和 `wof_resume_dispatch_selector.js`，然后直接继续当前 nextScript。
>
> **不要把本项目与 `ouyong520/wof-winkawaks-bridge` 混在一起。** WinKawaks bridge 是另一个独立项目。

---

## 1. 最终目标

目标不是自动玩游戏，而是做 **Future Danger AI**：

```text
ROM AI / descriptor / state machine
+ CPS RAM live enemy state
+ 当前敌人锁定的 P1/P2/P3
+ 敌人位置 / 目标位置 / 攻击 startup
+ 已验证的未来攻击前置状态
→ 预测未来约 0~1000ms 的真实威胁
→ 判断威胁的是 P1 / P2 / P3 中谁
→ 判断攻击来自哪一侧、何时进入 ACTIVE
→ 最后合成为 Future Danger Map / Safe Path
```

核心原则：**宁可少报，也不要因为“敌人靠近玩家”就制造大量假警报。** 预警必须尽量来自 AI 内部真实攻击准备阶段，而不是只靠距离猜测。

---

## 2. 当前总体进度

当前阶段已经不是“找内存字段/找 selector”的早期逆向，而是：

```text
底层 selector / dispatcher / descriptor 结构已基本打通
→ 攻击 ACTIVE 起点有统一观测约定
→ 已有一个强 production-shadow 规则（T16）
→ 已有 T33/T34 两个高质量 prospective candidates
→ T30 broad 规则已被真实反例否定，正在做分支判别
→ 当前进入 coverage-adaptive mining：无论房间出现什么敌人，都自动挖攻击前 terminal fingerprint
```

粗略进度（只是工程估计，不是数学完成率）：

```text
底层逆向 / 数据链：约 92~95%
Future Danger 核心框架：约 80%
大范围敌人/攻击规则覆盖：约 65~70%
整个项目综合：约 75~80%
```

接下来最大的工作量不是重新找底层，而是 **扩大可靠攻击规则覆盖 + 把规则合成实时 danger map**。

---

## 3. 运行环境与固定地址

运行链：

```text
网页
→ cycgo.js
→ Worker: gstyphoon.js
→ gstyphoon.wasm
→ CPS RAM + live 68000 ROM
```

DevTools Console 必须切到正在运行游戏的 `gstyphoon.js` Worker。

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

```text
ROM cache = self.__WOF_ROM_LOC_CACHE
旧 offline DB → live ROM: live = offline + 0x34
通常 ROM mapping = swap16
```

WASM module 历史名通常是 `_0x515056`，但新脚本必须允许动态扫描 `self` 找到 `HEAPU8/HEAPU32` 同 buffer 的 module，不能只依赖裸全局名。

---

## 4. 已完全解决：P1/P2/P3 target selector

这是底层 ground truth，不要再重做。

### 玩家 self index

```text
P1 +0x7C = 0
P2 +0x7C = 4
P3 +0x7C = 8
```

动态验证为严格 0/4/8。

### 敌人当前 target

```text
enemy +0x7E = 0 → P1
enemy +0x7E = 4 → P2
enemy +0x7E = 8 → P3
```

**`enemy+0x7E` 是当前实时 target identity 的 authoritative source。**

即使 target 在攻击准备过程中改变，也必须实时读取 +0x7E，不要缓存旧目标。

### player pointer table

```text
0x010CF8 = 0x00FFBE1C
0x010CFC = 0x00FFBEFC
0x010D00 = 0x00FFBFDC
```

严格 selector route：

```text
0x010E66  MOVE.W 126(A0),D1
0x010E6A  LEA 0x010CF8,A1
0x010E6E  MOVE.L 0(A1,D1.W),A1
```

也就是：

```text
enemy+0x7E
→ 0/4/8
→ P1/P2/P3 pointer table
→ A1 = selected player
```

### enemy+0x6A

`enemy+0x6A` 是 selected-player pointer cache 的低16位，常见：

```text
BE1C / BEFC / BFDC
```

但它可能存在 transition/stale 情况，所以策略是：

```text
+0x7E = authoritative
+0x6A = supporting cache only when exactly BE1C/BEFC/BFDC
```

---

## 5. 已解决：state/action → dispatcher → descriptor engine

### state99 / action2A 两层分派

已有严格结构：

```text
enemy+0x99
→ first-level state table
→ enemy+0x2A
→ second-level action table
→ specific AI routine
```

state99 blocks：

```text
0x10BBC
0x10BD0
0x10BE4
0x10BF8
0x10C0C
```

最终 action targets：

```text
0x10EC6
0x11078
0x11190
0x112C2
0x11456
0x1156A
0x11656
0x1178E
0x11908
```

### 已严格接通的一条 route

```text
state99 = 0
action2A = 2
→ 0x10EC6
→ 0x10F40 writes #0x0600 to enemy+0x2A word
→ action byte 从 2 变 6
→ 0x10F46 MOVEQ #24,D0
→ 0x25C8
```

另有：

```text
0x10FA0 MOVEQ #8,D0
→ 0x25B6
```

优先级较低，不要重新把它当当前主线。

### dispatcher 0x25C8 的关键修正

`0x25C8` 选择的不是“代码 handler”，而是 **descriptor data**：

```text
enemy type
→ type-specific descriptor table
→ D0 byte offset
→ A4 = descriptor
→ 0x247C descriptor consumer
```

### 0x247C descriptor consumer

已严格解析：

```text
+0 long → A6，再写 enemy+0x12 = frame/payload end pointer
+4 long → enemy+0x30
+8 word → timer/flag
```

bit15 clear：

```text
timer → enemy+0x34
inline next descriptor = current + 10
→ enemy+0x2C
```

bit15 set：

```text
clear bit15
剩余 timer → enemy+0x34
显式 long at descriptor+0x0A → enemy+0x2C
record len = 14
```

frameEnd 前 6 bytes 复制到：

```text
enemy+0x6C word
enemy+0x6E long region
```

**frameEnd 是 payload/frame 数据边界，不是代码地址。不要把 frameEnd 当 68000 code 解。**

---

## 6. ACTIVE 攻击统一观测约定

当前所有 Future Danger validator 使用：

```text
enemy+0x70 U16: 0 → nonzero
```

作为 **ACTIVE-start convention**。

这已经被大量 runtime 数据验证为很适合统一比较 startup lead time，但必须记住：

```text
它不是精确 damage frame
不是 exact hitbox onset
不是“玩家已经受伤”的时间
```

因此输出里的 leadMs 表示“距我们统一定义的 ACTIVE 起点”，不要把它写成“距命中还有 X ms”。

---

## 7. Future Danger timing 研究过程：为什么现在不再使用 broad 规则

### V18 / V20 / V21：早期 broad T16/T30 signatures

早期数据看到一些 T16 FAST / MID 状态经常很快进入攻击，因此建立：

```text
T16 FAST ≈ <=100ms
T16 MID ≈ <=250ms
T30 FAST ≈ <=100ms
```

当时样本非常漂亮，但还不足以证明 universal。

### V22

`wof_future_danger_map_production_shadow_v22.js`

T16 FAST / MID 大部分成功，但开始出现 deadline 外样本：

```text
FAST 101/105ms 等
MID 259ms
T30 119ms
```

这一步告诉我们不能只看聚类均值。

### V23

`wof_future_danger_deadline_tail_validator_v23.js`

继续做 tail 分类：

```text
T16 FAST: 47 evaluable → 46 ontime, 1 late 103ms
MID: 10/10 <=250
T30: 2/2 <=100
```

### V24

`wof_future_danger_sampling_jitter_validator_v24.js`

10ms sampling 验证 T30，5/5 严格，说明旧的 T30 119ms 不是简单因为 20ms polling 抖动就能解释。

### V25：关键反证

`wof_future_danger_t16_coverage_jitter_validator_v25.js`

真正高覆盖 10ms T16 数据直接否定 broad FAST/MID universal：

```text
FAST: 11 evaluable
6 strict
3 real late: 180.2 / 260 / 440.4ms
2 hard miss

MID: 9 evaluable
6 strict
1 real late: 320.4ms
2 hard miss
```

结论：

```text
旧 T16 FAST/MID 只能保留为 discovery signature
不能直接用于 production warning
```

### V26：找到真正 terminal B4 phase

`wof_future_danger_t16_timer_phase_discriminator_v26.js`

V26 把 broad T16 事件做 trace 后发现：所有 **16 个 strict FAST → attack6432** 都在 ACTIVE 前约 10~20ms 进入同一个极精确状态：

```text
type = 16
attack = 0
body = 4856
frameEnd = 0x851AE
next = 0x84C44
value30 = 0xFFFF
timer34 = 1
action2A = 4
b2B = 4
state99 ∈ {0,2,4}
```

唯一 late FAST 是另一条 attack4840 分支，ACTIVE 前发生：

```text
frameEnd = 0x851AE
next = 0x84DD0
value30 = 0x200
```

所以真正有价值的不是 broad FAST tuple，而是 **exact terminal B4 gate**。

### V27 / V28 / V29：coverage lesson

多个房间里 T16 coverage 为0，说明固定敌人类型 validator 容易白跑。

V28 仅按 type=16 定位还曾误命中 stale slot；后来改成要求 live object。

这段经历直接推动后面的 mixed validator / adaptive miner。

### V30：T16 exact gate 被强 prospective 验证

`wof_future_danger_mixed_production_validator_v30.js`

最关键结果：

```text
T16_6432_B4_40
signals = 65
evaluable = 65
strictHit = 65
realLate = 0
hardMiss = 0
expected attack6432 = 65/65
target stable = 65/65
side stable = 65/65
lead ≈ 9.0 .. 21.1ms
```

P1/P2/P3 target 都出现过；state99 0/2/4 都出现过。

因此这个 exact B4 gate 被正式提升为：

```text
production-shadow
```

注意 V30 的 entry side 都是 LEFT，T16 opposite-side symmetry 仍缺直接样本。

### V31：不再只盯 T16，开始全类型 fingerprint mining

`wof_future_danger_production_shadow_fingerprint_miner_v31.js`

120s：

```text
enemySamples = 51115
ACTIVE edges = 282
```

对每个 ACTIVE edge 回看：

```text
20 / 50 / 100 / 250 / 500ms
```

发现新候选：

#### T34 → attack3232

非常干净的 countdown：

```text
BODY2872
FE8811E
NX879E2
V100000
P6C2784
A4 / B2
TM15 ≈ 250ms
TM6  ≈ 100ms
TM3  ≈ 50ms
TM1/2 ≈ 20ms
```

#### T33 → attack3232

类似 countdown：

```text
BODY2872
FE867BA
NX85ECE
V100000
P6C2784
```

#### T27 → attack5064

发现：

```text
BODY5048
FE9A32C
NX99CB0
VFFFF
TM1
P6C5056
```

B4 在约20ms和约100ms样本里都出现，所以不能贸然只定40ms。

#### T23 → attack5888

发现 lower-count exact B4 fingerprint：

```text
BODY4936
FE84060
NX83C60
VFFFF
TM1
P6C4944
```

#### 明确不推广的 broad states

```text
T20 attack5136 某 broad signature 从20ms到500ms都存在
T34 attack5336 TM60 broad state 也可持续几百ms
```

这些不是 imminent terminal gate，不能因为“经常在攻击前看见”就直接做 warning。

### V32：prospective 验证 T33/T34，并发现 T30 broad 真问题

`wof_future_danger_next_rule_prospective_validator_v32.js`

120s / 10ms / 206 ACTIVE edges。

#### T16

```text
2/2 strict
lead = 10.0 / 19.8ms
attack = 6432
目标/方向稳定
```

进一步巩固 T16 production-shadow。

#### T34 attack3232 TM6

```text
3/3 strict
lead = 99.9 / 101.6 / 102.4ms
attack3232 = 3/3
target stable = 3/3
side stable = 3/3
```

#### T33 attack3232 TM6

```text
5/5 strict
lead = 100 / 100 / 100.5 / 107.4 / 108.4ms
attack3232 = 5/5
target stable = 5/5
side stable = 5/5
```

并出现一个 RIGHT side 样本，说明 T33 的该规则不是只在 LEFT 成立。

因此 T33/T34 都提升到：

```text
production-shadow-candidate
```

但样本还不够多，尚未像 T16 一样正式 production-shadow。

#### T30 broad FAST 被再次否定

旧 broad：

```text
type30
attack0
body1800
state99=0
action2A=0
b2B=0
```

V32：

```text
10 evaluable
8 strict <=100ms
2 hard miss
```

两个 hard miss 都是：

```text
timer34 = 1
absDx = 190 / 151
```

而成功的 TM1 样本包含：

```text
absDx = 125 / 89 / 51
```

所以 broad T30 不能升级，必须找额外 branch discriminator。

### V33：固定 validator 再次暴露 coverage 问题

`wof_future_danger_countdown_and_t30_discriminator_v33.js`

结果正确，120s / 10ms：

```text
enemySamples = 32989
ACTIVE edges = 291
```

房间主要类型：

```text
T24 13492
T18 8544
T21 8746
T30 1724
```

但所有固定规则的 exact match 都为0：

```text
T16 = 0
T34 = 0
T33 = 0
T30 split = 0
T27 = 0
T23 = 0
```

这不是规则失败；这是 **无覆盖**。

重要工程结论：

```text
不能继续让用户每换一个房间，就用固定规则白跑120秒。
```

因此下一步正式切到 coverage-adaptive miner。

---

## 8. 当前规则状态表

### A. 已可作为 production shadow

#### `T16_6432_B4_40`

条件：

```text
type16
attack=0
body4856
FE851AE
NX84C44
VFFFF
TM1
A4/B4
state99 ∈ {0,2,4}
```

预期：

```text
attack6432
通常约 9~21ms 后进入 ACTIVE
production horizon = 40ms
```

现有最强 prospective 证据：V30 65/65；V32 再 2/2。

### B. production-shadow candidates

#### `T34_3232_TM6_120`

```text
type34
attack0
body2872
FE8811E
NX879E2
V100000
P6C2784
A4/B2
state99 2/4
TM6
```

V32：3/3，约100~102ms → attack3232。

#### `T33_3232_TM6_120`

```text
type33
attack0
body2872
FE867BA
NX85ECE
V100000
P6C2784
A4/B2
state99 2/4
TM6
```

V32：5/5，约100~108ms → attack3232，已有 LEFT + RIGHT。

### C. 仍在 discovery / prospective 阶段

#### T27 attack5064 B4

V31 mined，V32/V33 没拿到覆盖。继续等待 adaptive miner 自然遇到。

#### T23 attack5888 B4

同上。

### D. 已明确不能当 production warning

#### Broad T16 FAST/MID

V25 已有 real late + hard miss。只做 discovery。

#### T16 4840 divergence

样本太少且 WOF-030 4次只有2次<=80ms，另有约200/220ms，且混入 attack6392。只做 discovery。

#### Broad T30 FAST

V32 8/10，2 hard miss。已降级。

#### absDx=130

只是根据 V32 样本用于诊断的临时 split，**不是 exact attack range，不是 hitbox，不是 causal boundary**。

---

## 9. 当前 next step：WOF-034 adaptive terminal miner

当前 resume：

```text
version = wof-resume-dispatch-selector-v44
nextCopyId = WOF-034
nextScript = wof_future_danger_adaptive_terminal_miner_v34.js
nextMarker = === WOF FUTURE DANGER ADAPTIVE TERMINAL MINER V34 JSON ===
```

WOF-034 的设计目标：**任何房间都不再白跑。**

它会：

1. 继续 opportunistically 检查已知 T16/T33/T34 gate。
2. 对每一个真实 ACTIVE edge，自动保存最近的 attack=0 terminal state。
3. 回看近似：

```text
20 / 50 / 100 / 150 / 250 / 500ms
```

4. 记录每次攻击前的 state/action/body/frameEnd/next/value/timer/payload。
5. 记录 pre-ACTIVE transition chain。
6. 按：

```text
enemy type + 实际 active attack + fingerprint
```

做聚合。
7. 同时统计 target P1/P2/P3 和 side 稳定性。

目标是优先从当前常见的：

```text
T24 / T18 / T21 / T30
```

中找出新的 terminal attack rules。

**WOF-034 产出的新 signature 仍然只是 discovery evidence。不能直接升 production。**

后续必须：

```text
WOF-034 mining
→ 找高重复、短 lead、攻击 identity 稳定的 exact fingerprint
→ 写新的 prospective validator
→ 独立房间/独立事件验证 strict/late/hard miss
→ 达标后才升 production-shadow
```

---

## 10. 新对话后面的工作顺序

新对话接手后不要自由发挥，优先按以下顺序：

### 第1步：核对当前 frontier

先读：

```text
WOF_AI_HANDOFF.md
WOF_AI_CURRENT_FRONTIER.md
wof_resume_dispatch_selector.js
```

确认：

```text
resume v44
next = WOF-034
```

### 第2步：让用户跑 WOF-034

用户只需要在 live `gstyphoon.js` Worker Console 执行一条命令：

```js
// WOF-034
await fetch('https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/wof_future_danger_adaptive_terminal_miner_v34.js?x='+Date.now(),{cache:'no-store'}).then(r=>r.text()).then(s=>(0,eval)(s));
```

正常玩约120秒，把完整 JSON 发回。

### 第3步：先验证 ID，再分析

必须先检查：

```text
copyId == WOF-034
project == WOF-AI-PRIVATE
version == wof-future-danger-adaptive-terminal-miner-v34
expectedMarker == === WOF FUTURE DANGER ADAPTIVE TERMINAL MINER V34 JSON ===
readOnly == true
ramWrites == 0
```

任何 ID/version/marker 不匹配：

```text
直接判定“发错结果 / 旧轮结果”
不要把它当当前证据
```

### 第4步：从 WOF-034 找新候选

优先选择同时满足：

```text
重复次数高
同一个 type + active attack
terminal fingerprint 高一致
lead 分布窄
目标稳定率高
方向稳定率高
不是长期 persistent state
```

不要为了凑规则选择只出现1次的随机 fingerprint。

### 第5步：prospective validator

对 WOF-034 最强的 2~4 个候选写下一版 validator。

prospective validator 至少要输出：

```text
signals
evaluable
strictHit
jitterBandHit
realLateHit
hardMiss
censored
expectedAttackRate
targetSameRate
sideStableRate
lead samples
entry state/timer/geometry diversity
```

### 第6步：逐渐形成 production rule registry

当规则样本充分后，形成：

```text
IMMINENT: 约0~50ms
NEAR: 约50~150ms
EARLY: 约150~500ms（只有足够可靠才启用）
```

不要为了“看起来更先进”硬把500ms broad state 当预警。

### 第7步：规则覆盖足够后再做最终 danger map

最终再把：

```text
validated rule
+ live target7E
+ enemy/target XY
+ side
+ remaining lead time
```

组合成多敌人 Future Danger Map / Safe Path。

---

## 11. 每轮 Console 命令协议

这是用户特别要求的，必须遵守。

1. 每轮只给 **一条可执行 Console 命令**。
2. 每条命令第一行必须有唯一 ID，例如：

```js
// WOF-034
```

3. Assistant 自己记住 ID ↔ script/version/test。
4. 用户回传 JSON 后，先校验：

```text
copyId
project
version
marker
```

5. 如果发错旧结果，不做技术解释，只指出 mismatch，并重新给当前命令。
6. 不要求用户手工修改 JS；能通过 GitHub connector 写代码就直接写。
7. 用户换房间是正常行为，脚本必须尽量对 coverage 变化鲁棒。
8. 新脚本默认 read-only；如果未来真的要写 RAM，必须显式说明，不能悄悄改变安全性质。

---

## 12. 重要方法论 / 证据标准

### 可以称“严格/结构 proof”的条件

应来自：

```text
真实 68000 instruction boundary
exact opcode / CFG / table data
runtime temporal order
重复的方向性 transition
```

### 不能称 causal proof 的东西

```text
单次相关样本
只因为攻击前500ms也出现了某 state
经验距离 rectangle
任意 raw byte discriminator
任意偶地址 decode 成 opcode
```

### timing 分级必须保留

必须区分：

```text
strict hit
jitter-band hit
real late
hard miss
censored
```

不要把 tail 内任何 attack 都算成功。

---

## 13. 绝对不要重做 / 已排除方向

除非出现真正新证据，否则不要重新花时间：

```text
Focus Multiroom
HUD 重做
0x0080F2
44 dispatcher incoming edges 重扫
重新找 enemy+0x7E target
重新证明 player+0x7C identity
重新找 0x010CF8 player table
0x11C26
0x05F6BA
A0+0x40/+0x44 target XY writer
AD5A / low4
全 ROM 任意偶地址 opcode 扫描
把 A5 默认当 player
把 A5+1FA 当唯一 bridge
把 descriptor 当 code handler
把 frameEnd 当 code
把 +0x70 当 exact hitbox/damage onset
把 broad T16 FAST/MID 当 production
把 broad T30 FAST 当 production
把 absDx130 当 exact range/hitbox
把 T20 5136 或 T34 5336 persistent state 当 imminent warning
```

---

## 14. 项目分离规则

本文件只属于：

```text
Project A = ouyong520/wof-ai-private
Browser / gstyphoon.js / Future Danger
WOF-0xx command IDs
```

另一个：

```text
Project B = ouyong520/wof-winkawaks-bridge
WinKawaks / 本地 bridge / M3/M4...
```

Project B 的 LOCAL_TO_WEB / M3/M4 结果不能拿来证明 Project A 的 Future Danger，反之亦然。

---

## 15. 新对话一句话主线

```text
底层 target/AI descriptor 已解开；
T16 exact terminal B4 已 production-shadow；
T33/T34 attack3232 TM6 已 prospective 全命中候选；
T30 broad 已被 hard miss 否定；
现在不要继续固定等某种敌人，而是运行 WOF-034 coverage-adaptive terminal miner，
从任何房间的每个 ACTIVE edge 自动挖 terminal fingerprint，
再把最强候选做 prospective validation，逐步扩大 Future Danger 覆盖。
```

---

## 16. 新对话首次回复建议

新对话读完仓库后，应直接告诉用户：

```text
已接上 Project A，不会重做 selector/dispatcher。
当前 resume v44，下一步 WOF-034。
这轮无论房间出现什么敌人都会采到攻击前 terminal evidence，避免再白跑120秒。
```

然后只给一条 WOF-034 Console 命令，等结果。

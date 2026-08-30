# WOF AI 项目交接 / 新对话接手说明

更新时间：2026-08-30 20:18（UTC+8）

> 给下一条 ChatGPT / Codex 对话直接接手。不要从头重做项目方向，也不要重新让用户解释。先读本文件，再检查仓库 `main` 当前代码。

## 1. 项目最终目标

游戏：**吞食天地II / Warriors of Fate / WOF / 三国志II**，已确认版本为 **WOF World 921002 / MAME `wofr1`**。

目标不是 hitbox viewer，而是 Future Danger AI：

```text
ROM 固定招式/AI逻辑
+ 当前 CPS RAM
+ enemy type/state/anim/action/X/Y/Z/facing
+ 未来攻击起手 / active / projectile
→ 预测未来约 0~1000ms
→ 判断攻击未来是否真的会碰到玩家
→ 只有真正需要躲时才给方向提示
→ 后续 Future Danger Map + Safe Path
```

当前正式范围：**观察 / 预测 / HUD 提示**。不要自动控制 P1/P2/P3，不自动按键，不自动 AB。

用户最在意的不是“能不能报警”，而是 **减少无意义误报**：普通小兵只是靠近不应该一直提示；怪物若实际上锁定 P2，即使离 P1 很近也不应该一直提示 P1。

---

## 2. 浏览器运行架构和关键 RAM

```text
网页
↓
cycgo.js
↓
Web Worker: gstyphoon.js
↓
gstyphoon.wasm
↓
CPS RAM / live 68000 ROM
```

Worker 侧测试代码必须在 DevTools 的 **`gstyphoon.js` Console** 执行。

RAM 读取：

```js
B(a)=HEAPU8[R+((((a-0xFF0000)&0xFFFF)^1))]
R=_0x515056.HEAPU32[0x2e39e4>>>2]
```

关键地址：

```text
P1 base = 0xFFBE1C
P2 base = 0xFFBEFC
P3 base = 0xFFBFDC
player stride = 0xE0

enemy pool = 0xFFC0BC
20 slots
enemy stride = 0xE0

HP = playerBase + 0x83
facing: 255 => -X，否则 +X
```

敌人已知字段至少包括：

```text
+0x04 X
+0x08 Y
+0x20 type
+0x28/+0x2A state相关
+0x70 attack
+0x82附近 HP/flags
```

不要再把这些位置相关字段当成 target 候选。

---

## 3. 预测核心 / HUD 已完成到什么程度

### 预测基线

冻结基线：

```text
branch: baseline-v4.10.1
commit: 7e945b2469cae6f726fbddbd80c390136c521960
```

当前 runtime 大约 `offline-dynamic-spectator-calibrated-v4.11.4`。已有 startup predictor、attack families、damage attribution、watch/action 等体系。不要随便大改已有几何基线。

历史统计中真实掉血前 warning attribution 覆盖曾约 93%+、首次 warning lead 约 300ms 级，但这不是“真人必然可躲准确率”。当前主要问题仍是 warning 太吵、普通小兵接近误报、特殊投射物和真实 target 未解决。

### Canvas/WebGL HUD

旧 DOM HUD 已判失败，不要继续修 `wof_hud_overlay.js`。

真实游戏画面已经确认是 WebGL：

```text
I_GF1TC = 实际 game canvas (#whathis)
I_fdC8Q = WebGL/WebGL2 context
I_b1EdF / I_FHW46 = 真正 frame/render path
```

`wof_canvas_probe.js` 已经在真实游戏画面里成功显示过 `WOF HUD OK`。

`wof_canvas_hud.js` 当前 v6 已成功在游戏内部显示：

```text
HUD 已加载 · xx s
```

60 秒 load-confirm 已工作。不要回退 DOM overlay。

HUD 用户偏好必须保留：

```text
注意
↑ 上
↓ 下
← 左
→ 右
AB
前方怪 / 后方怪
左侧 / 右侧
P1/P2/P3 一次只显示一个
```

不要主要依赖颜色表达危险等级。

---

## 4. 当前实战逻辑缺口

用户明确指出：

1. 夏侯惇丢炸弹：起手、头顶落点、爆炸命中提示不够好。
2. 弓箭 / 流星锤 / 炸弹应走 projectile/trajectory 逻辑。
3. 普通近战小兵只是接近，不应不断报警。
4. 不同敌人攻击距离不同：普通近战 < 长兵器 < 弓手/远程。
5. 最关键：**怪物有“要打谁”的 focus/target**。如果目标是 P2，P1 不应因为距离近就一直报警。
6. 压墙/绕后场景证明“当前移动方向 ≠ 攻击焦点”。

目标状态机应逐步做成：

```text
TARGET P1/P2/P3
↓
APPROACH / 绕路
↓
进入该敌人自己的攻击距离
↓
STARTUP
↓
ACTIVE
↓
RECOVERY / reselect
```

特殊 projectile 一旦生成，实际轨迹能伤到谁就警告谁，不受最初 target 限制。

---

## 5. Focus Multiroom 统计路线：已基本完成使命，不再作为主攻

文件：

```text
wof_focus_multiroom_collect.js   # 当前 focus-multiroom-v4
wof_focus_multiroom_export.js    # 当前 export-v4
```

v1 问题：running session 详细数据没有被 exporter 使用。
v2 修复可恢复 snapshot，但 100ms 运动方向容易假 switch。
v3 要求连续 700ms 每帧高置信，过严，几乎 stableCommits=0。
v4 改为约 1.3 秒窗口累计追击证据，已正常产生 stableCommits / strongLabels / switches。

一批较好的 v4 数据得到过：

```text
10 个可用 v4 sessions
strongLabels ≈ 1462
stableCommits ≈ 257
有效追击证据 ≈ 3421
稳定 target switch ≈ 24
```

关键结论：

- `0x3A` 不是可靠 target。
- `0x6A` 不是可靠 target。
- `0x68` 最多只是间接关联，没有证实。
- `0x9C` 虽然 switch 统计很好，但与 X/位置变化同步，是假候选。
- 其他高 purity offset 也大多是 enemy type/state/position 的混杂。

因此目前**没有证据证明 enemy E0 结构内存在一个简单的 `enemy+?? = P1/P2/P3` 固定 target 字段**。

结论：不要继续为了这个目标铺更多房间或不停调 focus-v4 阈值。统计路线已经告诉我们应该转 **ROM AI 逆向**。

---

## 6. ROM live image 已成功定位

这是当前主线。

文件：

```text
wof_rom_focus_probe.js
wof_rom_focus_bootstrap.js
wof_rom_focus_deep.js
wof_rom_focus_inspect.js
wof_rom_focus_trace.js
```

### 已确认 ROM 事实

live ROM 在当前 Worker HEAP 中成功找到过，例如：

```text
heap base ≈ 0xC08748
layout = swap16
SP = 0x00FF62EE
PC = 0x0000754A
```

`type dispatch table` 仍在：

```text
ROM offset 0x25DC
47 entries
47/47 valid
```

非常关键的新发现：网页 live ROM 的 type entry 相对离线 `future_attack_db_v3.json` **统一 +0x34**。

例：

```text
type 0  live 0x06F518  -> offline 0x06F4E4
type 1  live 0x074980  -> offline 0x07494C
type 9  live 0x085D0E  -> offline 0x085CDA
```

即：

```text
liveAddress = offlineAddress + 0x34
```

`wof_rom_focus_probe.js` v5 已接受这一映射，字段是：

```text
offlineDelta = +0x34
```

后续逆当前网页 AI **必须用 live 地址**；只有和旧 DB 对照时再减 `0x34`。

### 性能注意

早期 probe 同步扫描 256MB HEAP 导致游戏卡住几秒 / GC 压力。现版本采用安全分片扫描，并缓存：

```text
self.__WOF_ROM_LOC_CACHE
```

不要重新引入一次性同步扫描全 HEAP。

---

## 7. P1/P2/P3 ROM 引用扫描结果

`wof_rom_focus_probe.js` 成功扫描出：

```text
direct 32-bit P1/P2/P3 refs = 12
```

明显形成 **4 组 P1/P2/P3 三连引用**。

另外有 low-16 refs，但当前最有价值的是 12 个 direct32 refs。

原本从 type entry 前约 0x700 字节寻找 common helper，结果：

```text
commonHelpers = 0
```

这不代表失败，只表示“从 type entry 直接调用公共 helper”的假设太浅。因此 deep v2 改为：

```text
P1/P2/P3 direct refs
→ 聚类成函数
→ 建 1MB ROM reverse call graph
→ 反向追 enemy AI
```

---

## 8. 当前最重要的新候选：live 0x0080F2

`wof_rom_focus_deep.js` v2 + inspect 得到 4 个 player-ref clusters。

当前唯一 `STRONG TARGET SELECTOR CANDIDATE`：

```text
cluster = 1
live func = 0x0080F2
offline func = 0x0080BE
depth = 0
function size ≈ 342 bytes
P1 refs = 1
P2 refs = 1
P3 refs = 1
CMP-family count = 8
E0 evidence = 0
DBcc = 0
count2 ≈ 2
count3 = 0
```

inspect 汇总还观察到大约：

```text
direct callers / callers ≈ 24
pointer refs ≈ 2
external branch entrants ≈ 24
```

意义：`0x0080F2` **确实像一个被很多地方复用、会同时比较 P1/P2/P3 的多人逻辑 helper**。

但非常重要：**还不能宣布它就是 enemy target selector**。

原因：

- 它没有 E0 stride 循环证据。
- 它离 enemy type entries 很远。
- 目前还没有拿到“47 个 enemy type 是否能沿真实 direct JSR/BSR 调用链到达它”的最终 verdict。

所以目前状态是：

```text
0x0080F2 = 高价值候选
≠ 已证明 target selector
```

---

## 9. 当前正在做但尚未拿到最终结果：type → 0x0080F2 reachability trace

最新文件：

```text
wof_rom_focus_trace.js
```

最新创建该 trace 的 commit：

```text
bdfb6c6a4e2c6f81c1c16191cb571cf24852d139
```

它会自动：

```text
恢复 inspect/deep 状态（Worker 重建也可恢复）
↓
确定 candidate 0x0080F2
↓
打印 P1/P2/P3 引用 opcode context
↓
列 CMP/branch map
↓
找 direct callers
↓
从 47 个 enemy type entry 出发
最多追 6 层 direct JSR/BSR/JMP.L
↓
输出 ENEMY TYPE → CANDIDATE PATHS
↓
输出 TRACE VERDICT INPUT
```

当前对话最后一次运行时只截图到了 bootstrap 的 `live type table`，**没有拿到最终 `__WOF_ROM_FOCUS_TRACE` verdict**。

因此新对话的第一优先事项不是重做扫描，而是**把这个 trace 跑完并读取最终结果**。

如果当前 Worker 中 trace 已完成，可直接：

```js
(()=>{
  const x=self.__WOF_ROM_FOCUS_TRACE;
  if(!x)return console.log('trace state missing');
  console.table([x.candidate]);
  console.table(x.paths);
})()
```

如果状态不存在（Worker 重建），在 `gstyphoon.js` Console 重新加载 `main/wof_rom_focus_trace.js`：

```js
await fetch('https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/wof_rom_focus_trace.js?x='+Math.random())
  .then(r=>r.text()).then(s=>(0,eval)(s));
await WOFFOCUSTRACE.run();
```

然后看：

```text
=== TRACE VERDICT INPUT ===
directTypePaths
typeIds
directCallers
playerRefs
cmpBranchOps

=== ENEMY TYPE → CANDIDATE PATHS ===
```

### 分支 A：directTypePaths > 0

如果至少一个 enemy type 能 direct-call 到 `0x0080F2`：

1. 把具体 type → call path 固定下来。
2. 对 `0x0080F2` 做真正 68000 指令级反汇编，不再只统计 CMP-family。
3. 识别三处 P1/P2/P3 地址是 LEA/MOVEA/PEA 到哪个 A 寄存器。
4. 解码 8 个 CMP 比较的实际 operands，判断是在比较距离、状态、HP、存活还是别的。
5. 找比较完成后“胜出玩家”最终保留在哪个 A/D 寄存器或 RAM 临时位置。
6. 再做 live 动态验证：让多人房间里敌人目标从 P1 切到 P2，看该寄存器/临时值是否同步改变。
7. 验证成功后把 target 接入 `wof_hud_worker.js`，实现：`target != 当前玩家 && 非ACTIVE轨迹` 时 suppress 普通近战接近 warning。

### 分支 B：directTypePaths == 0

如果 47 个 enemy type 在 6 层 direct JSR/BSR 都到不了 `0x0080F2`：

1. 不再把 `0x0080F2` 当主 target selector。
2. 转查 **间接调用 / JMP(Ax) / 地址表 / state dispatch / function pointer**。
3. 从 4 个 P1/P2/P3 cluster 的 pointerRefs 和 external branch entrants 反向追。
4. 尤其检查 enemy AI 是否通过 state table / type subtable 间接跳到这些 player comparison helpers。
5. 必要时扫描 68000 `JMP (An)`、`JSR (An)`、indexed jump-table 形式，而不是只支持 direct long/BSR。
6. 如果最终证明 target 只存在执行时 A0/A1 等寄存器，不需要强求 RAM 字段；直接在选目标 routine 的调用点/出口做动态采样即可。

---

## 10. ROM 逆向当前相关 commits

重要阶段 commit：

```text
4e6f32865302d2ed390f129b5c66123fdf5f04d0  wof_rom_focus_probe v5，live/offline +0x34
6d386d549f96dcb6d48e632b50fa80b30ffec4ae  bootstrap v2
E1b334f... / e1b334fcf0a556d7c1b5d986d50137e5a2585caa  deep v2 reverse callgraph
2b6956fbcfe5df7f21bcd1a70f69ce72ee4d6b06  inspect v2 self-recover
bdfb6c6a4e2c6f81c1c16191cb571cf24852d139  trace v1 type reachability
```

以仓库 `main` 当前文件为准；上面的 commit 主要用于理解演进。

---

## 11. 后续真正产品化顺序

当前主线优先级：

```text
1. 证明/排除 0x0080F2 是否 enemy target selector
2. 若不是，追间接 AI 调用链，抓真实 target selection
3. target 成功后接入普通近战 warning suppress
4. 建 enemy class 攻击距离模型：MELEE / POLEARM / RANGED / PROJECTILE / BOSS
5. 弓箭、流星锤、夏侯惇炸弹：startup + projectile trajectory/landing/explosion
6. 再做 camera/player-follow 精确映射
7. 最后 Future Danger Map / Safe Path
```

不要把 facing 问题作为当前第一优先，用户已允许暂缓。

整体粗略进度曾估计约 55%~65%；如果真实 target/selector 突破，整体可接近 70%。

---

## 12. 新对话工作方式

用户偏好：

- 中文。
- 直接、短、按步骤。
- 最好“一条精确命令 + 预期结果”。
- 能直接改 GitHub 就直接改，不要让用户手工编辑 JS。
- 用户负责在浏览器 DevTools 跑测试并截图。
- 不要重新解释整个项目，不要回退已判失败路线。
- Worker 经常重建，所以工具脚本应尽量 self-recover，避免依赖上一条 Console 对象永远存在。
- 大扫描必须分片 yield，不能再次同步扫 256MB HEAP 把游戏卡住。

---

# 新对话第一句话应该怎么接

直接说：

> 我先读 `WOF_AI_HANDOFF.md` 和当前 `wof_rom_focus_trace.js`，然后继续完成 `0x0080F2` 的 enemy-type reachability 验证。先不要重做 focus multiroom，也不要继续调 HUD。我要先拿到 `directTypePaths`；如果 >0 就反汇编 0x0080F2 找最终 target 寄存器，如果 =0 就转间接 JMP / 地址表 AI 调用链。

这就是当前唯一正确的继续点。

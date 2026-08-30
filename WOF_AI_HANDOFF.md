# WOF AI 项目交接 / 新对话接手说明

更新时间：2026-08-30

> 这份文件是给下一条 ChatGPT / Codex 对话直接接手用的。不要从头重新讨论项目方向，先读完这里，再检查仓库当前文件。

## 1. 项目目标

游戏：**吞食天地II / Warriors of Fate / WOF / 三国志II**

已确认版本：**WOF World 921002 / MAME `wofr1`**。

目标不是 Hitbox Viewer，而是类似斯诺克辅助线的 **未来攻击轨迹预测 AI**：

```text
ROM = 固定招式剧本
RAM = 当前现场

怪物 type
+ 当前动作 / 动画
+ 当前 X/Y/Z
+ Facing
+ 招式起手
+ 固定运动轨迹
+ ATTACK 生效时间
+ 投射物生成
→ 模拟未来 0~1000ms
→ 判断未来攻击轨迹是否会碰到玩家
→ 打不到就不理
→ 会打到则提前提示安全移动方向
→ 最终 Future Danger Map + Safe Path
```

当前阶段只做 **预测 / 提示**，不做自动控制，不自动按键，不自动 AB。

用户既会旁观别人，也会自己下场测试；最终产品应面向真人玩家使用 HUD。

---

## 2. 浏览器 / Worker 架构

链路：

```text
网页
→ cycgo.js
→ Worker gstyphoon.js
→ gstyphoon.wasm
→ CPS RAM
```

运行预测代码必须在 Chrome DevTools 的 **`gstyphoon.js` Worker Console**。

页面刷新 / Worker 重建后粘贴代码会消失；目前使用 GitHub raw + `fetch(...).then(eval)` 方式安装。

运行时 RAM 读取方式：

```js
B(a)=HEAPU8[R+((((a-FF0000)&FFFF)^1))]
R=_0x515056.HEAPU32[0x2e39e4>>>2]
```

关键 RAM：

```text
P1 = FFBE1C
P2 = FFBEFC
P3 = FFBFDC
player stride = E0

敌人对象池 base = FFC0BC
20 slots
stride = E0

玩家 HP = base + 0x83
Facing: 255 => -X，否则 +X
ATTACK: 0 -> 非0 是起手
```

玩家 Y 方向移动速度经验值约 38。

---

## 3. 当前预测核心状态

### 冻结基线

**V4.10.1** 是冻结行为基线。

基线分支：

```text
baseline-v4.10.1
```

基线 commit：

```text
7e945b2469cae6f726fbddbd80c390136c521960
```

从 V4.11.0 到 V4.11.4 主要是 **盲测 / 审计 / HUD 负担诊断**，原则上没有改变 V4.10.1 的预测几何与动作决策核心。

### V4.11.0

加入 blind evaluation：

- decisionLoad：NONE / SAFE / WATCH / UP / DOWN / AB 时间占比
- materializationRate
- naturalPathChangeRate
- unchangedPrecision
- playerProfiles

重要解释：

- `changed` 不是自动等于 false positive；它代表玩家自然路线变化。
- `materializationRate` 不是独立几何准确率。
- 高手房有明显行为偏差，不能用低掉血简单证明模型 100% 准。

### V4.11.1

解决 HP 标签污染：

- `maxPlausibleHp = 128`
- `hpBaselineReset`
- `nonEnemyDamage`
- `safeMiss` 只保留真正有敌人证据的情况
- miss retention 扩到 120
- warning source 分类：
  - ACTION
  - GUARD
  - TAIL
  - SHADOW
  - BRIDGE
  - PHASE
  - GEOMETRY
  - EDGE
  - WATCH

### V4.11.2

加入真实掉血前 350ms 的 warning attribution：

- any
- latest
- exclusive
- lead time buckets
- avg first warning lead

关键观察：

- 实际伤害前稳定预警覆盖很高，部分批次约 93%~98%。
- GUARD / GEOMETRY 很吵，但不能整体删除，因为有真实伤害是它们独占覆盖。
- 平均首次预警 lead 接近 300ms+。

### V4.11.3

进一步拆 GUARD / GEOMETRY 的诊断子类，继续保持核心不动。

一批约 28.8 分钟数据中，两段完整 session 的稳定掉血预警覆盖约 95.5% / 98.3%，但 warning 占屏时间仍约 40%~44%。

### V4.11.4

加入 HUD shadow simulation：

- L1: GUARD / GEOMETRY / SHADOW
- L2: TAIL / BRIDGE / PHASE / EDGE
- L3: ACTION

模拟 180ms pulse / 900ms repeat 等 HUD 方案。

结论：即使脉冲化，L1 仍然太吵；不能单纯靠颜色或频繁 WATCH 做最终 UI。

---

## 4. 多房间盲测采集

文件：

```text
wof_multiroom_collect.js
wof_multiroom_export.js
```

每个房间的 Worker Console：

```js
fetch("https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/wof_multiroom_collect.js?"+Date.now()).then(r=>r.text()).then(s=>(0,eval)(s))
```

采集器行为：

- 默认 10 分钟
- 每 10 秒 checkpoint
- IndexedDB: `wof-multiroom-audit-v1`
- store: `sessions`
- 保存 start summary / checkpoints / final / misses / metadata
- 房间关闭时最多损失最后约 10 秒尾部

导出在任意普通页面 `top` Console：

```js
fetch("https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/wof_multiroom_export.js?"+Date.now()).then(r=>r.text()).then(s=>(0,eval)(s))
```

### 当前“自动上传记录”状态

**现在没有自动上传到 GitHub / ChatGPT / 服务器。**

当前做的是：

```text
Worker 自动采集
→ 自动每10秒保存到浏览器 IndexedDB
→ 用户手动运行 exporter
→ 浏览器生成 / 下载 JSON
→ 用户手动把 JSON 发给 ChatGPT
```

也就是说：**自动保存本地有，自动网络上传没有。**

不要为了“自动上传”把 GitHub token 直接写进网页 JS；这是不安全的。如果以后要自动上传，应该走用户自己的后端 / 临时上传接口，或继续保持手动导出。

---

## 5. 历史数据与 Family DB

离线 Campaign 大致规模：

```text
~6 rooms
79.4 room-min
238,033 frames
38 enemy types
25,382 ATTACK changes
2,439 spawn/identity
~275 player damage
7,584 full active windows
35 attack types
403 attack Families
```

Runtime DB：

```text
403 Families
1367 exact startup contexts
1083 coarse contexts
403 activeStart
```

Family damage-hit 分布很稀疏：

```text
>=1 hit: 85 families
>=2: 39
>=3: 21
>=4: 9
>=5: 4
>=10: 1
318 families 没有直接 linked damage hit
```

holdout 曾观察：

```text
hazard >= 0.5：约 81.47% unseen-room attack coverage，median advance ~259ms
hazard >= 0.8：约 71.16%，median advance ~179ms
```

不要把这些数字当作最终真人准确率。

---

## 6. Runtime 重要 API

当前 `WOFV4` 主要 API：

```js
WOFV4.status()
WOFV4.tracked()
WOFV4.spectateAll()
WOFV4.audit()
WOFV4.auditFamilies()
WOFV4.calibration()
WOFV4.exportCalibration()
WOFV4.snapshot()
WOFV4.summary()
WOFV4.evaluation()
WOFV4.decisionLoad()
WOFV4.misses()
WOFV4.report()
WOFV4.reportShort()
WOFV4.quiet(true/false)
WOFV4.pause()
WOFV4.resume()
WOFV4.resetCalibration()
WOFV4.stop()
```

运行预测核心：

```js
fetch("https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/wof_v4_install_once.js?"+Date.now()).then(r=>r.text()).then(s=>(0,eval)(s))
```

---

## 7. HUD 尝试历史：V1~V11 已整体判失败

已经试过：

- 顶部大条 HUD
- sticky 1.6s
- 单选 P1/P2/P3
- RAM X/Y/Z 头顶定位
- 视觉识别原生 1P/2P/3P 标签
- 跳跃安全视觉跟踪
- 固定 Y + X 跟随
- RAM X 校准
- 固定位置 HUD
- 前方怪 / 后方怪 / 左右侧提示
- 绑定 Canvas DOM rect

用户最终评价：**“整体无法用”**。

主要失败原因：

1. DOM Overlay 和游戏内部坐标不是同一坐标系。
2. RAM 世界坐标受镜头滚动影响，不能直接映射为浏览器屏幕坐标。
3. 视觉跟踪原生 P 标签会被跳跃 / 前跳 / 后跳 / 遮挡 / 同色 sprite 干扰。
4. 页面右侧功能栏、全屏、缩放进一步增加偏移。
5. 颜色式提示用户不接受；用户要直接文字 / 方向，不想靠颜色理解状态。
6. HUD 提示太快、太远、太吵时真人根本看不清。

**不要继续在 V1~V11 DOM HUD 上打补丁。**

---

## 8. 新 HUD 路线：直接进入游戏 Canvas 绘制

重新检查 `cycgo.js` 后确认真实绘制链：

```text
I_n3jTY()      = 页面游戏绘制函数
I_KkacD        = 游戏 Canvas 2D context
I_QKG4Q.Pad    = 游戏画面在页面 Canvas 内的绘制偏移
I_Aj3M8        = 游戏源画面 / source canvas
```

`I_n3jTY()` 会通过 `I_KkacD.drawImage(...)` 把游戏画面画出来。

因此正确路线应是：

```text
Worker WOFV4 预测
→ BroadcastChannel
→ top 页面收到预测
→ hook I_n3jTY()
→ 在原游戏 render 结束后
→ 直接用 I_KkacD.fillText / stroke / path 绘制 HUD
```

这样至少 HUD 本身和游戏画面共享 Canvas 坐标，不再被网页右栏 / CSS DOM overlay 坐标体系拖走。

### 当前 probe

文件：

```text
wof_canvas_probe.js
```

当前 probe 会 hook `I_n3jTY()`，在：

```js
x = I_QKG4Q.Pad.X + 12
y = I_QKG4Q.Pad.Y + 24
```

画：

```text
WOF HUD OK
```

运行：

```js
fetch("https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/wof_canvas_probe.js?"+Date.now()).then(r=>r.text()).then(s=>(0,eval)(s))
```

停止：

```js
WOFCANVAS?.stop?.()
```

### 注意：probe 目前还没有被最终确认成功

用户最近一张截图仍然能看到旧 DOM HUD 的“注意 / 后方怪 / P1”组件，截图中没有明确确认 `WOF HUD OK`。

因此新对话的 **第一件事** 不是继续开发完整 Canvas HUD，而是先保证旧 HUD 全部卸载，再验证 probe：

```js
WOFHUD?.destroy?.()
WOFCANVAS?.stop?.()
```

然后重新加载 probe。

如果 Canvas 内部稳定出现 `WOF HUD OK`，才正式废弃 DOM overlay 路线。

---

## 9. 当前 HUD 文件状态

仓库目前可能仍有这些文件：

```text
wof_hud_worker.js
wof_hud_overlay.js
wof_canvas_probe.js
```

`wof_hud_overlay.js` 当前属于已失败的 DOM HUD 实验，不要作为正式方案继续优化。

`wof_hud_worker.js` 最近版本还加入过：

- threatSide: LEFT / RIGHT / CENTER
- threatFacing: 前方怪 / 后方怪
- enemyX
- playerFace

关系判断基于敌人 slot 的 X 与玩家 Facing。

这个“前方 / 后方怪”信息后续可以复用到 Canvas HUD，但先验证方向判断是否符合真人观察。

---

## 10. 最终 HUD 用户偏好（必须保留）

用户已经明确反馈：

- 不要靠颜色告诉他“危险等级”。
- 想看到直接文字：`注意`。
- 真正要动时显示明确方向：
  - `↑ 上躲`
  - `↓ 下躲`
  - 以后如果核心真的支持左右，再显示 `← / →`
  - `AB`
- 希望能知道危险来自：
  - 前方怪
  - 后方怪
  - 左侧 / 右侧
- 提示不能瞬间闪，要能被真人看清。
- 最好贴近战斗视线，但不要再用不可靠的 DOM 人物跟随。
- 一次只看自己选中的 P1/P2/P3。

不要为了凑功能乱猜 LEFT / RIGHT；当前核心主要决策仍是 CONTINUE / UP / DOWN / AB。

---

## 11. 当前对预测核心的判断

底层不是“已经证明完美”，但已经有足够证据进入真人 UI 阶段：

- 多批盲测显示伤害前稳定 warning coverage 很高。
- WATCH 广泛导致 HUD 负担过大。
- GUARD / GEOMETRY 不能一刀切删除。
- 真人 HUD 会改变玩家行为，因此继续无限用旁观玩家调指标会过拟合。

所以不要再做几十轮相同 blind tuning。

当前策略：

```text
冻结底层预测核心
→ 先把真正可用的 Canvas HUD 做出来
→ 真人下场 3~5 轮
→ 记录“看得见 / 来得及 / 方向对不对 / 是否帮助躲避”
→ 只针对明确新盲点再回到底层
```

如果出现新投射物 / 新攻击类，再追加 1~2 个针对性 batch，而不是无休止调参。

---

## 12. 下一对话最优先 TODO

### TODO 1：彻底清理旧 DOM HUD，验证 Canvas probe

在 top Console：

```js
WOFHUD?.destroy?.()
WOFCANVAS?.stop?.()
```

再加载：

```js
fetch("https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/wof_canvas_probe.js?"+Date.now()).then(r=>r.text()).then(s=>(0,eval)(s))
```

要求：

- `WOF HUD OK` 必须画在游戏内部。
- 窗口变化 / 右侧栏 / 游戏运行时不漂。
- 不要再出现旧 DOM “注意 / P1”组件。

### TODO 2：如果 probe 成功，做 `wof_canvas_hud.js`

不要复用旧 overlay DOM。

最低版本只画一个选中玩家：

```text
P1
注意
后方怪 · 右侧
```

或：

```text
P1
↑ 上躲
前方怪 · 左侧
250ms
```

先固定在游戏内部一个清晰位置，确保读得懂；暂时不要追人物头顶。

### TODO 3：把 Worker warning 数据接入 Canvas HUD

继续用 BroadcastChannel：

```text
wof-ai-hud-v1
```

建议重新写一个干净的 `wof_canvas_hud.js`，而不是继续修改 `wof_hud_overlay.js`。

### TODO 4：找到真正 camera / screen transform 后，再做人物跟随

不要再猜。

优先从 `cycgo.js` / 渲染链中找：

- 游戏内部 scroll X / scroll Y
- source rectangle / destination rectangle
- sprite HUD / 原生 1P/2P/3P 的真正绘制逻辑

如果能拿到游戏自己的 camera transform：

```text
screenX = worldX - cameraX
screenY = worldY - cameraY - z / sprite offset
```

然后再做真正的人物头顶 HUD。

---

## 13. 不要做的事

- 不要恢复 local-player-only 逻辑；旁观模式仍应支持 RAM 中存在的 P1/P2/P3。
- 不要把 P2 离开当死亡。
- 不要要求玩家故意死亡。
- 不要猜 A/B 按键。
- 不要启用自动控制。
- 不要把高手房低掉血当 100% 准确率证明。
- 不要把 materializationRate 当独立 counterfactual 准确率。
- 不要用模型自己预测的东西再反过来证明模型准确。
- 不要继续在同一批数据上反复调到指标好看。
- 不要继续修 V1~V11 的 DOM 坐标跟随。
- 不要用颜色作为最终主要信息通道。

---

## 14. 输入链历史（当前不要启用）

已找到部分输入链：

```text
I_H3DNk.X_
→ I_Y088A
→ I_cdWPk
→ I_s10h9
→ I_iXPHN(mask)
```

方向 mask：

```text
UP    = 0x10
DOWN  = 0x20
LEFT  = 0x04
RIGHT = 0x08
```

另有：

```text
_0x11a3f7(mask,timestamp)
_0x423e73.Pe(mask, playerNo)
```

但当前项目交付是预测 / HUD，不是自动按键。

---

## 15. 用户工作方式

用户希望助手直接推进工程，不要每一步长篇解释。

常用模式：

```text
助手检查 / 改代码 / 提交 GitHub
→ 到需要真人测试时
→ 只告诉用户运行哪条命令、看什么现象
→ 用户截图 / 发 JSON
→ 助手继续修改
```

用户曾明确表示：

```text
你不用说直接做就行
做到要测试的时候跟我说
```

所以新对话请保持简洁、连续，不要重复问已经确定的项目目标。

---

## 16. Repo

```text
ouyong520/wof-ai-private
```

主线运行文件：

```text
wof_v4_install_once.js
wof_multiroom_collect.js
wof_multiroom_export.js
wof_hud_worker.js
wof_hud_overlay.js          # 已失败 DOM HUD，保留仅作历史
wof_canvas_probe.js          # 当前新路线 probe
```

这份交接文件：

```text
WOF_AI_HANDOFF.md
```

新对话开始时，优先读取本文件和上述当前 JS，再继续工作。

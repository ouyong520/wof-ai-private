# WOF WinKawaks 单人操作基础采集 / 全关卡 Sweep 指南

更新时间：2026-09-01

目的：让一个人操作 WinKawaks，把本地基础 raw 数据先系统采完；采完后 Browser Future Danger 主线可以直接读取 GitHub 里的 task/result/raw 对接，不需要重新让操作者上传、解释或重复采集。

> 这里的“单人操作”指 **一个人操作模拟器**，不等于游戏只开 1P。为了增加出怪量，第一遍默认仍使用 **3P 都进入 + 3P 无敌 + 只手动操作 P1**。P2/P3 只作为存在的 target/出怪条件，不要求同时手操。

---

## 1. 数据源边界

WinKawaks 本地采集用于 discovery：

```text
大量 raw RAM
场景/波次/敌人类型覆盖
attack/state/descriptor transition
候选字段/候选 sequence
```

Browser/Web 仍负责最终 production proof：

```text
本地发现候选
-> Browser 真实在线房 prospective validation
-> 验证 attack / live target / side / lead / miss
-> 才能 promotion
```

禁止把 WinKawaks 数字 offset 直接当 Browser/WASM offset。

---

## 2. 当前 Collector 固定能力

Collector v1：

```text
repo = ouyong520/wof-winkawaks-bridge
START = START_WOF_COLLECTOR.bat
READY = READY_WOF_TASK.bat
STOP  = STOP_WOF_COLLECTOR.bat
```

每帧 raw：

```text
P1 + P2 + P3 + 20 enemies
23 objects
stride = 0xE0
5152 bytes/frame
```

推荐 sweep 任务：

```text
action = capture_raw_burst
seconds = 60
hz = 60
uploadRawStream = true
readOnly = true
```

每个 wave/scene 使用唯一 taskId，建议：

```text
BASECAP-SWEEP-S01-W01-<timestamp>
BASECAP-SWEEP-S01-W02-<timestamp>
...
```

raw 永久路径：

```text
captures/<taskId>.jsonl.gz
```

绝不复用旧 taskId，绝不覆盖旧 raw。

---

## 3. 开始前一次性准备

1. 启动 WinKawaks，进入 WOF / 三国志II。
2. 让 P1/P2/P3 都进入游戏。
3. 开启 3P 无敌/不会死亡的金手指。
4. P2/P3 暂时不操作，留在战场中即可。
5. 只人工操作 P1。
6. 启动：

```text
START_WOF_COLLECTOR.bat
```

7. Collector 窗口保持打开，不要每波重启。
8. 不在采集中清怪；清怪只在本波 capture 完成后进行。

---

## 4. 每一波固定采集流程

每遇到一批新的敌人，按下面同一流程执行。

### A. 准备场景

```text
敌人已经正常出现
P1/P2/P3 都活着
无敌已开
暂时不要攻击
不要清怪
```

P2/P3 可以站着不动；P1 准备人工移动。

### B. 释放当前任务

当 Collector 的 active task 对应当前 wave 后，运行一次：

```text
READY_WOF_TASK.bat
```

必须看到类似：

```text
Operator ready accepted for task: <exact taskId>
```

只认当前 exact taskId。

### C. READY 后先静止 12 秒

Collector v1 默认 queue poll 周期约 10 秒，READY 被接受和正式 RUNNING 并不是同一瞬间。

因此：

```text
READY accepted
-> 12 秒不按任何游戏键
-> 再开始本波移动
```

这样可以保证人工动作发生在正式 raw capture 窗口内。

60 秒 burst 中，第一版实际得到约 45–48 秒主动走位数据已经足够做全游戏 discovery sweep。

### D. P1 走位，不主动攻击

目标不是打死敌人，而是让敌人自己暴露 AI 分支、target、距离、左右和 Y 差异。

推荐约 48 秒动作：

```text
0–12 秒：P1 在敌群左侧附近，上下移动
12–24 秒：从敌群上方绕到右侧，不要直穿敌人身体
24–36 秒：P1 在敌群右侧附近，上下移动
36–48 秒：从敌群下方绕回左侧
```

允许偶尔靠近/拉远，但：

```text
不要主动攻击
不要跳跃/AB/特殊动作
不要故意抓人
不要一直贴着敌人
不要直线穿过敌人身体换边
```

直穿敌人容易触发抓取/抱人，影响 normal enemy-AI baseline，所以换边用上方/下方弧线绕过去。

如果偶然被抓，不必整波重采：脱离后继续；如果长时间被抓或场景严重异常，后面把该 wave 标记 confounder 即可。

### E. Capture 完成后才清怪

等本 wave Collector 完成后：

```text
status/by_task/<taskId>.json -> DONE/PASS
results/by_task/<taskId>.json -> matching PASS
```

然后才：

```text
打开金手指菜单
-> 游戏暂停没有关系
-> 清怪
-> 关闭菜单恢复游戏
-> 往前推进
-> 等下一波出现
```

因为 capture 已经结束，所以此时菜单暂停不会污染本波有效数据。

然后进入下一 wave，重复 A→E。

---

## 5. 第一遍不要做复杂自动化

第一遍目标是最快建立全游戏 atlas，不要求三个人自动同步走位。

默认：

```text
3P 都进入
3P 都无敌
P2/P3 基本不动
人工只控制 P1
```

这样已经同时获得：

```text
3P 条件下更高出怪量
P1/P2/P3 多 target 存在
所有 20 enemy slots 并行 raw
P1 不同 X/Y/side/distance 刺激
```

第一遍完成后再看覆盖缺口；只有缺 target/retarget/特殊多人分支时，第二遍才做指定 scene 的 3P 分散/同步或自动化。

---

## 6. Boss 第一遍规则

普通 wave：60 秒一个 burst。

Boss 第一遍也先只做一个 60 秒 full-HP/no-attack discovery burst，优先完成全游戏覆盖。

如果后处理发现 Boss 有明显血量阶段/变身/特殊 phase，再只针对这些 Boss 追加：

```text
2/3 HP
1/3 HP
near-death / phase transition
```

不要在第一遍就把每个 Boss 拉成长实验。

---

## 7. 每个 wave 必须保留的标签

为了以后不重复采集，每个 reusable wave 至少记录：

```text
taskId
rawPath
stage / scene / wave（人工可识别名称即可）
player config = 3P joined / 3P invincible / manual P1 only
capture duration / Hz
operator action = P1 low-contact left/up/down/right arc sweep
whether attack/jump was intentionally avoided
whether grab/contact anomaly happened
whether cheat/menu was used only after capture
visible enemy composition if known
known confounders
VALID / SUPERSEDED / INVALID
```

不要仅凭 raw 字节反推缺失的 scene 标签。

---

## 8. 基础采集完成后的“立即对接”

当操作者完成一批或完成全游戏第一遍后，不需要手工把 raw JSON 发给 ChatGPT。

只需要告诉项目控制器：

```text
WinKawaks 基础 sweep 已完成，可以开始对接分析。
```

AI 直接从 GitHub 读取：

```text
parallel/BASECAP/BASE_CAPTURE_CATALOG.md
tasks/queue/BASECAP-SWEEP-*.json
status/by_task/BASECAP-SWEEP-*.json
results/by_task/BASECAP-SWEEP-*.json
captures/BASECAP-SWEEP-*.jsonl.gz
```

然后立即进入：

```text
1. taskId + taskBlobSha + PASS 完整性校验
2. stage/scene/wave -> raw capture 建索引
3. 每 wave enemy type census
4. attack==0 -> ACTIVE transition 统计
5. state/action/body/frameEnd/next/timer ordered sequence mining
6. 建 stage/scene/wave -> internal Txx -> attack/sequence atlas
7. 自动列 coverage gaps / rare attacks / missing target branches
8. 选高价值候选
9. 回 Browser 多房 prospective validation
10. 只有 Browser 通过后才进入 production-shadow
```

这就是本地基础采集与当前 Browser Future Danger 主线的正式接口。

---

## 9. 第一遍完成标准

第一遍不追求“每个敌人所有动作 100% 已覆盖”。完成条件是：

```text
全关卡都走过
主要 scene/wave 都至少有一个 retained raw
普通 wave 约60秒
3P 条件优先
P1 产生左右/上下/近远变化
raw 已上传 GitHub
每个 task 有 scene/wave 标签
没有把清怪菜单暂停混进有效 capture
```

之后由分析程序生成缺口清单，再只补缺口，不重扫整游戏。

---

## 10. 操作者最简记忆版

```text
3P进场 + 3P无敌
START Collector（只开一次）

每波：
敌人出现
-> READY
-> 静止12秒
-> P1不攻击，绕怪上下左右约45–48秒
-> 等 capture 完成
-> 金手指清怪
-> 前进
-> 下一波

全游戏扫完
-> 告诉 AI“基础 sweep 完成”
-> AI 直接读 GitHub raw 接上 Browser Future Danger
```

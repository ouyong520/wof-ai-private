# BASECAP — Shared Labeled WinKawaks Capture Dataset

Updated: 2026-09-01

## 状态

BASECAP v1 基础采集已完成。权威索引见：

```text
parallel/BASECAP/BASE_CAPTURE_CATALOG.md
```

当前基础覆盖：B00、B10、B11、B12、B13、B20、B30、B31、B32、B40-P2、B40-P3。后续 GEO / EFIELD / RAWMINE 应优先复用这些 retained raw，不要重复向操作者采同一基础场景。

## 职责

BASECAP 只负责：

- 审计已有 raw；
- 建立一次采集、长期保存、多 AI 复用的基础数据集；
- 保存可验证的场景标签、操作协议、task/result/raw 身份；
- 只在确有覆盖缺口时新建 `BASECAP-*` 采集任务。

BASECAP 不负责解释字段语义，不修改 GEO / EFIELD / RAWMINE 研究结论，不修改生产规则，不写游戏 RAM。

## 写入边界

BASECAP 文档写入范围：

```text
parallel/BASECAP/**
```

Collector 侧只允许为 BASECAP 采集流程创建/维护 `BASECAP-*` 队列任务，或修复采集控制流本身。不得伪造 status/result/raw。

## Raw 不可变规则

每个采集使用全局唯一 `taskId`。标准 retained raw 路径：

```text
captures/<taskId>.jsonl.gz
```

默认：

```text
uploadRawStream = true
readOnly = true
writesGameMemory = false
layout = P1 + P2 + P3 + 20 enemies
stride = 0xE0
bytesPerFrame = 5152
```

绝不复用旧 taskId，绝不覆盖历史 raw。重采必须使用新 taskId，并在目录中说明旧数据为什么 INVALID / SUPERSEDED / NONCANONICAL。

## 标签证据规则

Collector `PASS` 只证明机械采集健康，不自动证明人工动作按要求发生。

一个人工场景只有在以下证据闭合后才能标记 `VALID`：

1. authoritative queue task；
2. matching task blob SHA；
3. `DONE` status；
4. matching `PASS` result；
5. retained gzip raw；
6. `readErrors=0`、`frameSizeErrors=0`、`writesGameMemory=false`；
7. 人工场景还必须有操作者对关键可观察条件/动作完成的确认。

禁止仅根据 raw 数值反推出操作者做过什么。

## 当前 Collector 单窗口流程

现在使用 Collector v2 单窗口流程：

```text
启动 START_WOF_COLLECTOR.bat
-> Collector 自动轮询任务
-> 新任务自动在主窗口显示中文名称和完整中文步骤
-> 操作者先准备游戏场景
-> 在同一个主窗口按一次回车
-> 看到“采集已开始”后执行指定动作
-> 自动采集、压缩、上传、写 result/status
-> 自动返回等待并显示下一任务
```

`READY_WOF_TASK.bat` 已废弃，不再参与任务启动。

单窗口回车是明确的当前任务启动点，因此不再需要旧 Collector v1 的 READY 后 12 秒防竞态延迟。历史 v1 数据仍按当时真实协议保留，不重写历史事实。

详细规则：

```text
parallel/BASECAP/OPERATOR_INSTRUCTION_STANDARD.md
parallel/BASECAP/OPERATOR_GATE_TIMING_NOTE.md
```

## 人工指令硬规则

所有给操作者看的任务说明必须使用中文。技术标识如 taskId、文件名、JSON 字段名可以保留英文。

任何主动输入步骤必须明确写出：

- 哪个玩家；
- 哪个按键；
- 是轻点还是持续按住；
- 按住多久；
- 何时松开；
- 松开后静止多久；
- 重复次数；
- 可观察确认条件；
- 禁止输入；
- P1/P2/P3 其他玩家是否必须保持不动。

禁止使用“按左两秒”“攻击几次”“移动一下”这类可产生多种理解的描述。

## 复用原则

新研究开始前按以下顺序：

1. 先查 `BASE_CAPTURE_CATALOG.md`；
2. 再查已 retained 的 GEO / EFIELD / RAWMINE raw；
3. 能复用就复用；
4. 只有真正缺少场景/判别条件时才新增采集。

B30/B31/B32 当前复用 `EFIELD-003-passive-retarget-60s60`，其中 B31 只可表述为 typed-enemy episode enter/exit diversity；不得未经 EFIELD 证据把这些边缘直接改称语义上的 spawn/death。

## 完成标准

BASECAP v1 当前满足完成条件：

- 基础套件已经覆盖；
- 新采 B13/B20/P2/P3 全部 retained raw + PASS + 操作证据闭合；
- 旧时序失败/无标签尝试保留为历史非 canonical；
- 下游 AI 可以直接从目录引用 raw，不需要操作者搬运机器可读数据；
- 不再存在必须由 BASECAP 当前继续采集的基础场景缺口。

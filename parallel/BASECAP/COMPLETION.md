# BASECAP v1 Completion

Completed: 2026-09-01
Verdict: **COMPLETE**

## 已完成目标

BASECAP 已建立一套可长期复用的 WinKawaks 基础 raw 数据集，并完成以下基础覆盖：

```text
B00 idle
B10 P1 horizontal
B11 P1 floor/depth
B12 facing/minimal displacement
B13 ordinary attack/action animation
B20 camera scroll
B30 natural gameplay/combat diversity
B31 typed-enemy lifecycle enter/exit diversity
B32 retarget diversity
B40-P2 controlled P2 horizontal/depth movement
B40-P3 controlled P3 horizontal/depth movement
```

权威数据目录：

```text
parallel/BASECAP/BASE_CAPTURE_CATALOG.md
```

## 本轮新闭环 capture

```text
BASECAP-B13-attack-12s60-20260901-0558Z
BASECAP-B20-camera-scroll-16s60-20260901-0559Z
BASECAP-B40-P2-xy-16s60-20260901-0600Z
BASECAP-B40-P3-xy-16s60-20260901-0601Z
```

四项均已得到 matching `PASS` result、retained gzip raw、0 read errors、0 frame-size errors、`writesGameMemory=false`。

额外人工标签证据：

- B13：操作者按任务要求在“采集已开始”后完成 4 次普通攻击轻点；
- B20：操作者明确确认按右推进期间发生明显背景/整个画面横向滚动；
- P2/P3：操作者按指定 RIGHT/LEFT/UP/DOWN 持续 2 秒 + 松开/静止协议完成。

## Reuse captures

B10/B11 复用：

```text
RAWMINE-005-p1-depth-wide-window-40s60-20260901-0048Z
```

B30/B31/B32 复用：

```text
EFIELD-003-passive-retarget-60s60
```

B31 的标签严格限制为 typed-enemy episode enter/exit diversity，不把 enter/exit 未经证明地改称 semantic spawn/death。

## 控制流修复

本轮暴露并修复了旧 Collector v1 的人工门控问题：

```text
READY accepted != capture started
```

当前使用 Collector v2 单窗口模式：

```text
任务自动显示
-> 准备场景
-> 主窗口回车一次
-> 看到“采集已开始”
-> 执行动作
-> 自动采集/上传/result/status
-> 自动下一任务
```

`READY_WOF_TASK.bat` 已废弃。

操作员标准：

```text
parallel/BASECAP/OPERATOR_INSTRUCTION_STANDARD.md
parallel/BASECAP/OPERATOR_GATE_TIMING_NOTE.md
```

## Historical quarantine

以下关键历史尝试不作为 canonical 基础标签：

```text
BASECAP-B12-facing-minimal-8s60-20260901-0518Z
BASECAP-B13-standing-attack-delayed-30s60-20260901-0536Z
BASECAP-B13R-standing-attack-ungated-60s60-20260901-0543Z
```

原因和 retained/raw 状态见 `BASE_CAPTURE_CATALOG.md`。历史数据不覆盖、不删除、不重新命名为成功标签。

## 下游交接

GEO / EFIELD / RAWMINE / future lanes 在请求新的基础人工采集前必须先查 `BASE_CAPTURE_CATALOG.md`。

BASECAP 提供的是：

```text
raw + immutable task identity + acquisition label + operator evidence
```

BASECAP 不提供：

```text
字段语义结论
Browser/WASM production proof
offset promotion
游戏内存写入
```

P2/P3 controlled raw 已经可供 GEO 直接筛选同结构/同 offset 候选，但是否同结构/同 offset 必须由 GEO 自己证明。

## 已知文档兼容注意

仓库根部或其它并行线若仍存在旧 Collector v1 / `READY_WOF_TASK.bat` 操作说明，应视为历史工作流。对 BASECAP 新任务，以本目录的 v2 单窗口规则为准；BASECAP 不越权修改其它 lane / mainline 文档。

## Final verdict

BASECAP v1 基础采集任务已结束。当前不需要继续占用操作者或 WinKawaks 进行基础场景采集。只有未来下游发现一个**目录中确实不存在的判别场景**时，才应以新 `BASECAP-*` taskId 增量扩展本数据集。

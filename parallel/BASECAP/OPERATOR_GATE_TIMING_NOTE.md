# BASECAP 操作门控时序说明

Updated: 2026-09-01

## 当前结论

Collector v2 已切换为单窗口、回车即开始当前任务的操作流。

当前标准流程：

```text
Collector 自动发现并显示任务
-> 操作者准备游戏场景
-> 在同一个 Collector 主窗口按一次回车
-> Collector 立即把当前任务置为运行并进入采集
-> 主窗口显示“采集已开始”
-> 操作者执行动作
```

因此新 BASECAP 任务不再使用：

```text
READY_WOF_TASK.bat
OPERATOR_READY.json
READY 后固定等待 12 秒
```

新任务的人工动作必须以主窗口明确出现“采集已开始”为起点。

## 为什么旧流程不安全

旧 Collector v1 中：

```text
READY_WOF_TASK.bat
-> 写 runtime/OPERATOR_READY.json
-> Collector 在自己的 poll loop 中稍后读取
-> 才正式进入 RUNNING / capture
```

READY “已接受”与真实 capture start 不是同一时刻。旧默认轮询可达到约 10 秒，因此短动作可能在正式采集前就已经做完。

这属于控制平面时序问题，不代表 raw 读取本身损坏。Collector PASS 只能证明机械采集健康。

## 历史 12 秒规则

在 v2 完成以前，BASECAP 曾临时采用：

```text
READY accepted
-> 12 秒所有游戏键保持松开
-> 再执行短动作
```

其目的只是保证旧 v1 至少经历一次约 10 秒轮询机会。该规则现在只用于解释历史 capture，不再用于新任务。

## 历史数据如何判定

历史 raw 不得因为当前 v2 已修复就追溯性改标签。

### `BASECAP-B12-facing-minimal-8s60-20260901-0518Z`

机械 PASS，但任务要求 READY 后立即做 facing taps。由于旧 v1 存在 READY->capture 延迟，无法保证动作进入 retained 8 秒窗口，因此该数据对 canonical B12 标签为 INVALID/NONCANONICAL。

### `BASECAP-B12R-facing-delayed-30s60-20260901-0527Z`

使用旧 12 秒保护协议，随后执行 minimal facing taps，机械 PASS、raw retained、操作者完成确认，因此保留为 canonical B12 VALID。

### 旧 B13 门控尝试

`BASECAP-B13-standing-attack-delayed-30s60-20260901-0536Z` 暴露了旧 READY 工作流的控制问题，没有形成新的 canonical B13 标签。

### 旧 B13 ungated 尝试

`BASECAP-B13R-standing-attack-ungated-60s60-20260901-0543Z` 机械 PASS 且 raw retained，但由于 `operatorGate.required=false`，Collector 在操作者动作前自动运行，不能作为 B13 人工攻击标签。

### v2 闭环 B13

`BASECAP-B13-attack-12s60-20260901-0558Z` 使用单窗口回车启动。操作者看到“采集已开始”后执行四次明确轻点普通攻击，结果 PASS/raw retained，因此 canonical B13 时序闭环。

## v2 操作硬规则

1. 新任务自动显示，不按回车刷新；
2. 操作者先准备场景；
3. 回车只按一次，用于开始屏幕上已经显示的当前任务；
4. 必须看到“采集已开始”后再做游戏动作；
5. 采集完成后不需要额外确认，Collector 自动上传、写结果并轮询下一任务；
6. `READY_WOF_TASK.bat` 不参与任何新 BASECAP 任务。

## 仍然需要人工标签确认的情况

即使 v2 时序已经明确，下列条件仍不能由 `PASS` 自动推出：

- 是否真的发生镜头滚动；
- 是否真的使用了指定玩家；
- 是否错误按了其它键；
- 是否发生了任务要求避免的战斗/干扰；
- 其它纯肉眼可观察条件。

这些条件需要任务元数据加操作者确认共同支持。不得从 raw 数值反推人工行为。

## 范围

本说明只定义 BASECAP 的操作门控时序。它不授权自动按键、游戏 RAM 写入，也不改变 GEO / EFIELD / RAWMINE 的字段语义结论。

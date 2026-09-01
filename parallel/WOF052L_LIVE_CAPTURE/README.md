# WOF-052L 10 房间真人长采集入口

目标：把 Browser Fleet、WOF-052L Recorder 和 WOF-052L Analysis 拼成一个 owner 中文入口。

## Owner 正常路径

双击：

`RUN_10_ROOM_LONG_CAPTURE.cmd`

流程：

1. 自动准备 Python 环境；
2. 自动做 Recorder discovery-v2 硬预检；
3. 第一次选择 JSON 保存目录，以后自动记住；
4. 输入 `1 / 5 / 10`，默认 `10`；
5. 自动启动互相隔离的 Browser Fleet；
6. 自动为每个 Fleet CDP endpoint 启动独立 Recorder；
7. 自动启动 WOF-052L Analysis `--watch`；
8. owner 只需在各浏览器窗口正常进入 WOF 房间；
9. CMD 持续显示在线浏览器、正在采集、已完成、T18、candidate、A4704、A4712、T23、只读/RAM writes；
10. `Ctrl+C` 安全结束采集、写最终 fleet merged JSON，并做一次最终分析。

不需要 DevTools、Worker Console、粘贴 JavaScript，也不需要逐房间点击 Start。

## 关键保护：禁止白跑

长采集入口不会因为 Browser Fleet 能打开 10 个窗口就宣布可采。

启动前必须确认当前 `parallel/WOF052L_RECORDER/recorder.py` 已具备：

- exact World 921031 SHA-256 gate；
- `Target.setAutoAttach`；
- related target / iframe -> Worker discovery-v2；
- 只读 CDP allowlist；
- 无 `Input.*`；
- 无 `Runtime.callFunctionOn`；
- 无 `Page.addScriptToEvaluateOnNewDocument`。

如果 Recorder 仍是旧的顶层 `Target.getTargets -> type=worker + gstyphoon URL` 路径，入口会在启动任何长采之前退出，并明确显示 discovery-v2 blocker。

## 多房间隔离

沿用 Browser Fleet / Fleet Recorder 已有约束：

- 每个浏览器实例独立 profile；
- 每个实例独立 localhost CDP port；
- 每个 endpoint 独立 RecorderManager；
- 一个 endpoint 掉线不影响其他 endpoint；
- Worker reload/replacement 只重置该房间；
- 新 Worker/房间可以在运行中加入；
- per-room / checkpoint / child merged / fleet merged 自动保存。

## 自动分析

如果 `parallel/WOF052L_ANALYSIS/analyzer.py --self-test` 通过，入口会自动启动：

`analyzer.py <保存目录> --watch --interval 5`

采集 JSON 变化后自动刷新：

- `analysis/analysis.json`
- `analysis/分析结果.txt`

停止采集时再执行一次最终分析。

## 安全边界

固定保持：

- `readOnly=true`
- `ramWrites=0`
- `inputInjection=false`
- no `window.Worker` replacement/wrap
- no Blob/Data/ObjectURL Worker rewrite
- no game speed control
- no `product/alpha/**` modification

本入口是采集/项目加速工具，不修改游戏逻辑，也不自动晋级攻击规则。

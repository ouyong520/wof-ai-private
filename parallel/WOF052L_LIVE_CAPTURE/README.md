# WOF-052L 10 房间真人长采集入口

目标：把 Browser Fleet、WOF-052L Recorder 和 WOF-052L Analysis 拼成一个 owner 中文入口。

## Owner 正常路径

双击：

`RUN_10_ROOM_LONG_CAPTURE.cmd`

流程：

1. 自动准备 Python 环境；
2. 自动安装并硬预检 Recorder Discovery V2；
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

入口会先加载 `parallel/WOF052L_RECORDER/discovery_v2_sync.py`，对 Recorder runtime 执行 `install(recorder)`，然后确认：

- exact World 921031 SHA-256 gate；
- `Target.setAutoAttach` 已进入只读 CDP allowlist；
- page / related target / iframe -> Worker Discovery V2 已安装；
- 无 `Input.*`；
- 无 `Runtime.callFunctionOn`；
- 无 `Page.addScriptToEvaluateOnNewDocument`。

Recorder 默认 Windows 入口也已通过 `owner_v2_zh_cn.py` 安装同一 Discovery V2；本长采集入口仍显式安装一次，避免未来入口路由变化导致长采集退回旧 Worker 发现逻辑。

如果 Discovery V2 缺失或安全门槛异常，入口会在启动任何长采之前退出并显示精确 blocker，避免用户白跑长采。

## 多房间隔离

沿用 Browser Fleet / Fleet Recorder 已有约束：

- 每个浏览器实例独立 profile；
- 每个实例独立 localhost CDP port；
- 每个 endpoint 独立 RecorderManager；
- 一个 endpoint 掉线不影响其他 endpoint；
- Worker reload/replacement 或 Worker CDP error 只完成该房间，其他房间继续；
- 新 Worker/房间可以在运行中加入；
- per-room / checkpoint / child merged / fleet merged 自动保存。

Browser Fleet 自己的 Worker 状态仅是 cheap indicator；是否真正进入采集以 Recorder 的 WASM / heap / exact World 921031 准入为准。

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

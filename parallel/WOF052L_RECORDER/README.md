# WOF-052L 自动多房间事件采集器

这是 PM 已批准的 WOF-052L 长时间只读采集工具。正常 owner 工作流默认使用简体中文。

## 你实际怎么用

1. 双击 `RUN_WOF052L_RECORDER.cmd`。
2. 第一次运行时，选择保存 JSON 的目录。
3. 在采集器连接/启动的 Chrome 或 Edge 中正常进入 WOF 房间。
4. 不需要逐个房间点“开始”。支持的 `gstyphoon*.js` Worker 会在 WASM/heap 就绪后自动发现和连接。
5. 可以运行几分钟、几小时或过夜。
6. 完成时按 `Ctrl+C`。采集器会结束所有在线房间，并自动写入最终合并 JSON。

记住的保存目录位于：

`%LOCALAPPDATA%\WOF052LRecorder\settings.json`

以后要重新选择目录：

```bat
RUN_WOF052L_RECORDER.cmd --reset-output
```

或者直接指定：

```bat
RUN_WOF052L_RECORDER.cmd --output-dir D:\WOF_CAPTURE
```

中文路径同样支持，例如：

```bat
RUN_WOF052L_RECORDER.cmd --output-dir "D:\WOF采集结果"
```

## Browser Fleet 多房间模式

正常双击 CMD 会经过中文 owner 入口 `owner_zh_cn.py`，底层继续复用现有 `fleet_recorder.py` / `recorder.py`，不改变采集逻辑。

如果 `%LOCALAPPDATA%\WOF Future Danger\Fleet\instances.json` 中存在 Browser Fleet 房间：
- 每个编号的 localhost CDP endpoint 都拥有独立 `RecorderManager`；
- 房间/profile/端口隔离保持不变；
- 一个浏览器房间重启或断开，只影响它自己的 Worker session；
- 其他房间继续采集；
- 新加入的 Fleet 房间会自动发现；
- 每个子采集器保留自己的合并 JSON；
- 停止时另外生成一个 Fleet 总合并/index JSON。

如果没有 Fleet manifest，工具会自动使用原有单浏览器模式。

可选高级参数：

```bat
RUN_WOF052L_RECORDER.cmd --fleet-manifest D:\path\to\instances.json
RUN_WOF052L_RECORDER.cmd --ignore-browser-fleet
```

## 浏览器连接行为

没有 Browser Fleet 时，采集器会扫描本机 Chrome/Edge CDP 端口，优先 `9223` 和 `9222`。

- 如果已有兼容浏览器在运行，直接连接；
- 否则可以启动独立 Chrome/Edge；
- 在该浏览器正常进入 WOF 房间即可；
- 不替换 `window.Worker`；
- 不创建 Blob Worker；
- 不改写 Worker URL；
- 只有真实 `gstyphoon*.js` Worker 和 WASM/CPS RAM 就绪后才附加；
- 连接失败是 fail-open：游戏不受影响，采集器继续等待/重试。

可选参数：

```bat
RUN_WOF052L_RECORDER.cmd --cdp-port 9223
RUN_WOF052L_RECORDER.cmd --browser edge
RUN_WOF052L_RECORDER.cmd --browser chrome
RUN_WOF052L_RECORDER.cmd --no-launch-browser
RUN_WOF052L_RECORDER.cmd --game-url https://example.invalid/your-wof-page
```

## 中文状态说明

单浏览器模式会持续显示类似：

```text
浏览器 已连接 | 在线房间 7 | 已完成房间 12 | T18 样本 3456 | 候选周期 8 | A4704 3 | A4712 5 | T23 周期 4 | 只读模式 开启 / 游戏内存写入 0
```

Fleet 模式还会显示：
- 集群房间数量；
- 正在运行的采集进程数量；
- 每个 Fleet 房间的浏览器连接状态。

错误会先显示中文说明，再显示：

`技术详情：...`

这样普通操作不要求看懂英文异常栈。

## 房间生命周期

每个支持的 Worker 都是独立采集状态：
- 新 Worker：先严格确认 World 921031，再自动开始；
- 房间关闭 / 刷新 / Worker 重建：只结束该 Worker；
- 其他房间继续；
- 替换出来的新 Worker 会作为新 session 自动加入；
- 新房间可随时加入；
- 没有固定一小时或 120 秒自动停止；
- 实际房间数量主要受浏览器/电脑资源限制。

严格身份仍是：

`Warriors of Fate (World 921031)`

完整 CPU-logical ROM SHA-256：

`5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62`

## 保存的数据

采集器不会保存长时间逐帧完整 RAM 历史。

主要保存：
- T18 `BODY4728/A4/B2/TM1 -> A4704 / A4712` 有序证据；
- T18/T23 有界序列证据；
- enemy type / attack 频率；
- 玩家数量与 target 样本；
- bounded descriptor+attack edge；
- 场景/敌人类型集合覆盖；
- 每房间 checkpoint 和最终 JSON；
- 全局 rolling / final merged JSON。

所有 ordered discovery 都仍然只是研究证据，不会自动提升为 Alpha 产品规则。

## 输出文件

保存目录下：

```text
rooms/
  <timestamp>_<room-id>.json

checkpoints/
  <run-id>_<room-id>.checkpoint.json

runs/
  <run-id>_merged.json
```

内部 JSON key / schema 为了兼容继续使用英文，例如：
- `schema`
- `runId`
- `status`
- `counts`
- `readOnly`
- `ramWrites`
- `inputInjection`
- `rooms`

中文化只发生在你看到的 CLI、窗口、错误和说明层，不改机器消费格式。

## 安全边界

固定安全约束：
- `readOnly=true`
- `ramWrites=0`
- `inputInjection=false`
- 不注入键盘/手柄输入；
- 不改游戏速度；
- 不替换/拦截 Worker；
- 不依赖 Alpha bootstrap；
- 不修改 `product/alpha/**`；
- 不做长时间完整 raw RAM dump。

Python CDP client 仍然只允许 target discovery/attach/detach、`Runtime.enable` 和 `Runtime.evaluate` 等现有只读方法。

## 离线自检

不打开浏览器也可以执行：

```bat
RUN_WOF052L_RECORDER.cmd --self-test
```

中文默认输出：

```text
自检通过 — WOF-052L 采集器安全约束与序列汇总正常
```

自检继续验证序列汇总、原子 JSON 写入、无固定采集时长和只读 CDP method 边界。

## 真人验证

单浏览器模式：
1. 双击 `RUN_WOF052L_RECORDER.cmd`；
2. 第一次选择保存目录；
3. 打开一个或多个 WOF 房间；
4. 观察“在线房间”自动增加并出现 JSON/checkpoint；
5. 关闭/刷新一个房间，确认只有该房间进入“已完成”；
6. 按 `Ctrl+C`，确认 `runs/<run-id>_merged.json`。

Browser Fleet 模式：先启动 Fleet，再双击同一个 Recorder CMD。应自动为每个 Fleet endpoint 启动独立采集，不需要 Worker Console，也不需要粘贴 JavaScript。

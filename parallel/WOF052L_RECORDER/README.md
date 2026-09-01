# WOF-052L 自动多房间事件采集器

这是 WOF-052L 长时间只读采集工具。默认 owner 工作流使用简体中文，并已同步 **Worker Discovery V2**。

## 你实际怎么用

1. 双击 `RUN_WOF052L_RECORDER.cmd`。
2. 第一次运行时选择 JSON 保存目录。
3. 在采集器连接/启动的 Chrome 或 Edge 中正常进入 WOF 房间。
4. 不需要 DevTools、Worker Console、手选 Worker 或粘贴 JavaScript。
5. Recorder 会自动从 page / iframe / Worker topology 找到真实游戏运行时；通过 WASM/heap + 精确 World 921031 SHA-256 后才开始采集。
6. 可以运行几分钟、几小时或过夜；完成时按 `Ctrl+C` 写入最终合并 JSON。

记住的保存目录位于：

`%LOCALAPPDATA%\WOF052LRecorder\settings.json`

重新选择目录：

```bat
RUN_WOF052L_RECORDER.cmd --reset-output
```

直接指定：

```bat
RUN_WOF052L_RECORDER.cmd --output-dir "D:\WOF采集结果"
```

## Worker Discovery V2

默认 CMD 入口现在是：

`RUN_WOF052L_RECORDER.cmd -> owner_v2_zh_cn.py -> discovery_v2_sync.py -> 原 Recorder/Fleet`

发现顺序：

```text
Browser CDP endpoint
-> page target
-> page session Target.setAutoAttach
-> related iframe / worker target tree
-> read-only WASM / heap preflight
-> exact World 921031 SHA-256
-> 原有 WOF-052L worker_probe.js
-> 开始采集
```

兼容路径包括：
- 旧式 browser-level direct worker；
- root `Target.getTargets` 没有 Worker、但 page-attached Worker 可见；
- page -> iframe -> Worker；
- `worker` / `shared_worker` / `service_worker`；
- Worker URL shape variation，不再要求唯一固定的 `gstyphoon*.js` 顶层 URL 形状。

仍然 fail closed：
- Blob/Data/JavaScript Worker URL 不接受；
- 同一页面出现多个通过身份门的 Worker 而关联不唯一时，不采集；
- direct Worker 无法唯一关联页面时，不采集；
- WASM/heap 未就绪时继续等待；
- World 921031 SHA-256 不匹配时拒绝；
- reload / Worker replacement 使用新的 target/session 独立重发现，不继承旧 target identity cache。

每个房间 JSON 可额外包含向后兼容的 `topologyDiagnostics` 和 `target.discoveryPath`。原采集 schema、T18/T23 字段与研究语义不变。

## Browser Fleet 多房间模式

如果 `%LOCALAPPDATA%\WOF Future Danger\Fleet\instances.json` 中存在 Browser Fleet 房间：
- 每个 localhost CDP endpoint 拥有独立 `RecorderManager`；
- 每个 child 只使用自己的 host/port/client，不跨 endpoint 搜索；
- 一个房间关闭、刷新、Worker replacement 或浏览器断开，只结束该房间；
- 其他房间继续；
- 新 Fleet endpoint 会自动加入；
- 停止时生成每个 child run JSON 和 Fleet 总 index JSON。

因此 10 个 Fleet endpoint 可以同时独立运行 Discovery V2。

如果没有 Fleet manifest，自动使用单浏览器模式。

高级参数：

```bat
RUN_WOF052L_RECORDER.cmd --fleet-manifest D:\path\to\instances.json
RUN_WOF052L_RECORDER.cmd --ignore-browser-fleet
RUN_WOF052L_RECORDER.cmd --cdp-port 9223
RUN_WOF052L_RECORDER.cmd --browser edge
RUN_WOF052L_RECORDER.cmd --browser chrome
RUN_WOF052L_RECORDER.cmd --no-launch-browser
```

## 身份与安全门

唯一允许采集的版本：

`Warriors of Fate (World 921031)`

完整 CPU-logical ROM SHA-256：

`5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62`

固定安全约束：
- `readOnly=true`
- `ramWrites=0`
- `inputInjection=false`
- 不替换/包装 `window.Worker`
- 不创建或改写 Blob/Data/ObjectURL Worker
- 不使用 `Input.*`
- 不使用 `Runtime.callFunctionOn`
- 不写游戏 RAM
- 不控制游戏速度
- 不修改 `product/alpha/**`

Discovery V2 仅新增 `Target.setAutoAttach` 到现有 CDP allowlist，用于只读 topology/session discovery。

## 房间生命周期

每个通过身份门的 Worker 是独立采集 session：
- 新 Worker：重新做 WASM/heap + World SHA 准入；
- reload / replacement：旧 session 结束，新 targetId 独立验证；
- Worker poll/session 失效：只结束该房间；
- 定期重新审计 live page topology；若出现多 Worker 关联歧义，立即 fail closed，避免跨房间串采；
- 没有固定一小时或 120 秒自动停止。

## 保存的数据

原 WOF-052L 采集语义保持不变，主要保存：
- T18 `BODY4728/A4/B2/TM1 -> A4704 / A4712` 有序证据；
- T18/T23 有界序列证据；
- enemy type / attack 频率；
- 玩家数量与 target 样本；
- bounded descriptor+attack edge；
- 场景/敌人类型集合覆盖；
- 每房间 checkpoint / final JSON；
- rolling / final merged JSON。

不会保存长时间逐帧完整 RAM history。Ordered discovery 仍是研究证据，不会自动提升为 Alpha 产品规则。

## 输出目录

```text
rooms/
  <timestamp>_<room-id>.json
checkpoints/
  <run-id>_<room-id>.checkpoint.json
runs/
  <run-id>_merged.json
```

内部 JSON keys 为兼容可继续使用英文；owner 可见菜单、状态、错误默认简体中文。

## 离线回归

基础 Recorder 自检：

```bat
RUN_WOF052L_RECORDER.cmd --self-test
```

Discovery V2 专项回归：

```bat
.venv\Scripts\python.exe -m unittest -v test_discovery_v2_sync.py test_fleet_recorder.py
```

覆盖：direct worker、page-attached worker、iframe Worker、URL variation、ambiguity、wrong identity、WASM not ready、reload replacement、10 endpoint isolation、read-only allowlist。

## 真人长采集 proof

仓库侧 Discovery V2 已完成。下一阶段只需：

1. 启动 Browser Fleet（目标 10 房间）；
2. 双击 `RUN_WOF052L_RECORDER.cmd`；
3. 正常进入 WOF 房间；
4. 确认 10 个 endpoint 各自自动通过 page / Worker / WASM / World 921031 准入并生成 checkpoint；
5. 做一次房间刷新/replacement，确认该房间独立重发现、其他 9 房不受影响；
6. 开始长时间采集。

不需要 DevTools、Worker Console 或手工 JavaScript。

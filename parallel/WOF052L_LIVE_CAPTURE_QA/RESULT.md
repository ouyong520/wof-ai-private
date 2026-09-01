# WOF-052L 10-Room Long Capture — Fresh Independent QA Result

Date: 2026-09-01

## Verdict

**BLOCKED — P1 owner-facing 简体中文验收失败：10-room 正常长采集入口会直接输出 English-only Fleet Recorder 状态/错误。**

本轮是独立 QA。没有修改 `parallel/WOF052L_LIVE_CAPTURE/**`、`parallel/WOF052L_RECORDER/**`、`parallel/BROWSER_FLEET/**`、`parallel/WOF052L_ANALYSIS/**` 或 `product/alpha/**` 的核心实现。

## 精确 blocker

`parallel/PM/CHINESE_UI_UX_REQUIREMENT.md` 明确要求：

- owner-facing WOF 工具默认使用简体中文；
- 状态、警告、错误、CMD 文本应尽量中文；
- 正常 owner workflow 若仍要求理解 English-only status/error，则不能视为 owner-ready。

但是当前 `parallel/WOF052L_RECORDER/fleet_recorder.py` 的 `FleetRecorderManager` 在正常 multi-room supervisor 路径会直接 `print()`：

- `Fleet #<id>: WAITING <host>:<port>; other rooms continue.`
- `Fleet #<id>: CDP connect failed safely: <error>`
- `Fleet #<id>: Browser OK — <endpoint>`
- `WOF-052L fleet recorder #<id> -> <host>:<port>`

这些不是 internal JSON key / schema / protocol identifier，而是直接出现在 owner CMD 的状态/错误文本。

当前 `parallel/WOF052L_LIVE_CAPTURE/live_capture.py` 只：

1. 安装 Recorder Discovery V2；
2. 使用 `ChineseFleetManager` 启动 Browser Fleet；
3. 创建 `fleet_recorder.FleetSupervisor(...)`；
4. `supervisor.sync_manifest()` 启动 `FleetRecorderManager` child threads。

它没有加载任何会把上述 `FleetRecorderManager` 输出翻译成中文的 wrapper/patch。因此 1 / 5 / 10-room 正常 owner path 都可触发该 P1；10-room 时最多会由 10 个 child recorder 输出这些 English-only 状态/错误。

## 最小复现

不需要真人 WOF、DevTools、Worker Console 或一小时采集即可确认：

1. 从 `live_capture.py` 进入 normal long-capture path；
2. `FleetSupervisor.sync_manifest()` 为 manifest endpoint 创建 `FleetRecorderManager`；
3. endpoint 尚未 ready 时，`ensure_browser()` 输出 English-only `WAITING ... other rooms continue.`；
4. CDP connect exception 时输出 English-only `CDP connect failed safely`；
5. endpoint ready 时输出 English-only `Browser OK`；
6. child recorder thread 启动时输出 English-only `WOF-052L fleet recorder`。

因此该问题在真实 10-room 一小时采集前即可静态/离线确定，不应让 owner 白跑长采集后才发现。

## QA 判断

这是 **P1**，因为本次 Fresh QA 的明确验收项包含 `owner-facing 全中文`，而项目级中文 UX requirement 明确规定该条件未满足时工具不能判定 owner-ready。

这不否定当前 Discovery V2、World 921031 identity gate、read-only/no-input 或 multi-room orchestration 的已有实现结果；但 Fresh QA 不能在存在此 P1 时给出 `PASS — READY FOR ONE REAL 10-ROOM LONG CAPTURE`。

## Fresh fix stage 的最小修复范围建议

由 fresh fix stage 修改核心实现（本 QA 不修改）：

- 将 `FleetRecorderManager.ensure_browser()` / `run_managed()` 的 owner-visible 状态和错误改为简体中文；
- 保留 endpoint、CDP、WOF-052L 等必要技术标识；
- error UX 第一层必须是中文可理解说明，技术详情第二层保留；
- 同时检查 `FleetSupervisor.run()` 的 owner-visible English 文本，避免单独启动 supervisor 时再次违反同一 requirement；
- 修复后重新跑本 Fresh QA，再继续 10-room failure-isolation pressure regression。

## Safety

本 QA 未授权也未执行：

- RAM writes；
- gameplay input injection；
- `window.Worker` replacement；
- Alpha rule 修改；
- attack research 扩展。

**Stop condition reached: BLOCKED — P1 owner-facing 简体中文验收失败。**

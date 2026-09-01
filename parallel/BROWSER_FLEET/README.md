# WOF 多房间浏览器管理器

状态：**BROWSER FLEET DISCOVERY V2 READY（仓库侧）**；只保留一次最小真人 Windows 集群验证。

这个工具只用于项目操作加速。它启动多个普通 Chrome/Edge WOF 浏览器实例，不修改 Alpha、不替换 `window.Worker`、不写游戏 RAM，也不注入游戏输入。

## 你实际怎么用

正常情况下只需要双击：

`RUN_WOF_FLEET.cmd`

然后：
1. 输入 `1`、`5`、`10`，或其他 `1-50` 的数量；直接回车默认 `10`；
2. 工具自动查找 Chrome/Edge；
3. 自动为每个房间创建独立配置目录和本机 CDP 端口；
4. 自动排列窗口；
5. 进入中文管理界面查看每个房间状态。

第一次使用不要求先设置游戏网址。没有配置网址时会打开可供 WOF 使用的空白浏览器窗口，你可以正常进入游戏页面。

## 中文状态说明

界面会显示：
- 浏览器：已连接 / 未连接；
- WOF 页面：已找到 / 等待中；
- Worker：已找到 / 等待中；
- PID；
- 独立配置目录；
- 永久安全提示：`只读模式：开启｜游戏内存写入：0｜游戏输入注入：无｜window.Worker 替换：无`。

界面会同时明确提示：**Worker 状态只用于快速发现；World 921031 身份确认仍以 PYLAUNCH 只读验证为准。**

如果出现错误，第一行先给出中文说明，随后才显示 `技术详情：...`。跨房间 CDP 端口异常会被安全拒绝，不会静默串到另一个房间。

## Discovery V2 做了什么

旧 Fleet Worker 状态只看 `/json/list` 中 `worker/shared_worker + URL 包含 gstyphoon`，会漏掉真实 Chrome/WOF runtime surface。

现在每个实例都只连接自己的 localhost CDP 端口，并执行轻量、只读 discovery_v2：
- 页面发现与 Worker 发现解耦；
- 从 WOF page 使用 flattened `Target.setAutoAttach` 发现 related target；
- 支持 `iframe -> worker` 的关联拓扑；
- Worker URL 变化时，可通过只读 Emscripten `HEAPU8/HEAPU32` 结构探测成为快速状态候选；
- 保留 direct `gstyphoon*.js` Worker 的向后兼容；
- reload / recreated Worker 每次刷新重新发现，不继承旧 Worker 成功状态；
- 一个房间 discovery 异常只影响该房间，其他实例继续刷新。

Fleet 不运行完整 ROM SHA-256 身份计算，所以不会冒充 PYLAUNCH 的权威 World 921031 proof。

## 中文管理命令

- `S` — 刷新状态；
- `R` — 重启一个编号房间；
- `X` — 关闭一个编号房间；
- `A` — 关闭全部管理中的浏览器并退出；
- `Q` — 只退出管理器，保留已经打开的浏览器窗口。

## 房间隔离方式

每个房间都有自己独立的：
- `%LOCALAPPDATA%\WOF Future Danger\Fleet\Profiles\Fleet_XX` 用户配置目录；
- 本机 CDP 端口（默认从 `9323` 开始）；
- 浏览器进程；
- 窗口位置；
- manifest 条目。

不同房间不共享 profile。每次状态刷新只访问该实例的 `127.0.0.1:<port>`。如果 `/json/version` 返回的 browser websocket 指向另一个 Fleet 端口，管理器会拒绝连接。一个浏览器房间崩溃、关闭、重载或 Worker 重建不会阻断其他房间。

## 给其他工具发现房间

集群状态写入：

`%LOCALAPPDATA%\WOF Future Danger\Fleet\instances.json`

内部格式版本保持：

`wof-browser-fleet-v1`

内部 JSON key / schema 为兼容性继续使用英文。安全字段固定为：
- `readOnly: true`
- `ramWrites: 0`
- `inputInjection: false`
- `windowWorkerReplacement: false`
- `workerStatusAuthority: "cheap-indicator-only"`
- `world921031IdentityAuthoritative: false`

PYLAUNCH 和 WOF-052L Recorder 可以继续读取同一个 manifest，但消费者必须独立重新 probe endpoint。Fleet 的状态不能替代 PYLAUNCH 的 Worker/WASM/heap/World 921031 验证。

详细格式见 `DISCOVERY_CONTRACT.md`。

## 可选高级命令

正常用户不需要下面这些命令。只有调试时才需要：

```bat
py -3 fleet_owner_zh_cn.py start 10 --interactive
py -3 fleet_owner_zh_cn.py configure
py -3 fleet_owner_zh_cn.py status
```

内部核心实现：
- `fleet_manager.py`
- `fleet_discovery_v2.py`
- 中文 owner 入口：`fleet_owner_zh_cn.py`

## 安全边界

本工具不会：
- 修改 `product/alpha/**`；
- 替换或包装 `window.Worker`；
- 创建 Blob Worker 或改写 Worker URL；
- 写游戏 RAM；
- 发送键盘/鼠标/手柄游戏输入；
- 调整游戏速度；
- 注入攻击逻辑。

Discovery 只使用 target/session attach、auto-attach、Runtime enable/evaluate 的只读表达式。CDP 只绑定 localhost。即使 discovery 或管理器失败，游戏本身应继续运行。

## 离线回归

仓库根目录可执行：

```bat
py -3 -m unittest discover parallel\BROWSER_FLEET\tests -v
```

本次 discovery_v2 仓库侧回归：**15/15 PASS**。

覆盖：
- direct worker backward compatibility；
- related-target-only；
- URL mismatch but related runtime；
- iframe -> worker；
- reload/recreated worker；
- 10 instance isolation；
- stale/missing endpoint；
- no cross-port association；
- 一个实例 discovery 异常不影响其他实例；
- 原有窗口排列、数量保护、设置持久化、独立 profile/port、manifest 安全字段。

## 真人 Windows 验证 — 唯一剩余 bounded proof

1. 双击 `RUN_WOF_FLEET.cmd`；
2. 输入 `10`；
3. 确认 10 个窗口出现并自动排列；
4. 至少在两个窗口正常进入 WOF 房间；
5. 按 `S`，确认对应房间逐步显示“浏览器：已连接 / WOF 页面：已找到 / Worker：已找到”；
6. 用 `R` 重启其中一个房间，确认另一个房间不受影响；
7. 用 `A` 全部关闭。

不需要 DevTools、不需要 Worker Console、不需要粘贴 JS、不需要手工 RAM 检查，也不会注入游戏输入。

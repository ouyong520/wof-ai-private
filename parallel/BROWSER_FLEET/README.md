# WOF 多房间浏览器管理器

状态：仓库侧工具已就绪；还需要一次真人 Windows 集群验证。

这个工具只用于项目操作加速。它会启动多个普通 Chrome/Edge WOF 浏览器实例，不修改 Alpha、不替换 `window.Worker`、不写游戏 RAM，也不注入游戏输入。

## 你实际怎么用

正常情况下只需要双击：

`RUN_WOF_FLEET.cmd`

然后：
1. 输入 `1`、`5`、`10`，或其他 `1-50` 的数量；直接回车默认 `10`；
2. 工具自动查找 Chrome/Edge；
3. 自动为每个房间创建独立配置目录和本机 CDP 端口；
4. 自动排列窗口；
5. 进入中文管理界面查看每个房间状态。

第一次使用不要求先设置游戏网址。没有配置网址时，会打开可供 WOF 使用的空白浏览器窗口，你可以正常进入游戏页面。

## 中文状态说明

界面会显示：
- 浏览器：已连接 / 未连接；
- WOF 页面：已找到 / 等待中；
- Worker：已找到 / 等待中；
- PID；
- 独立配置目录；
- 永久安全提示：`只读模式：开启｜游戏内存写入：0｜游戏输入注入：无｜window.Worker 替换：无`。

如果出现错误，第一行会先给出中文说明，随后才显示 `技术详情：...`，方便排查但不要求你看懂英文异常。

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

不同房间不共享 profile。一个浏览器房间崩溃、关闭或重载，不会主动停止其他房间。

## 给其他工具发现房间

集群状态写入：

`%LOCALAPPDATA%\WOF Future Danger\Fleet\instances.json`

内部格式版本保持：

`wof-browser-fleet-v1`

内部 JSON key / schema 为兼容性继续使用英文，例如：
- `id`
- `host`
- `port`
- `endpoint`
- `profileDir`
- `status`
- `readOnly`
- `ramWrites`
- `inputInjection`
- `windowWorkerReplacement`

其中安全字段继续固定为：
- `readOnly: true`
- `ramWrites: 0`
- `inputInjection: false`
- `windowWorkerReplacement: false`

这些内部字段不会为了中文界面而改名。中文化只发生在你看到的显示层。

PYLAUNCH 和 WOF-052L Recorder 可以继续读取同一个 manifest。Fleet Manager 里的 Worker 状态只是轻量目标列表提示；权威 Worker/WASM/heap/World 921031 校验仍由现有只读探测链路负责。

## 可选高级命令

正常用户不需要下面这些命令。只有调试时才需要：

```bat
py -3 fleet_owner_zh_cn.py start 10 --interactive
py -3 fleet_owner_zh_cn.py configure
py -3 fleet_owner_zh_cn.py status
```

内部核心实现仍是 `fleet_manager.py`，中文 owner 入口是 `fleet_owner_zh_cn.py`。

## 安全边界

本工具不会：
- 修改 `product/alpha/**`；
- 替换或包装 `window.Worker`；
- 创建 Blob Worker 或改写 Worker URL；
- 写游戏 RAM；
- 发送键盘/鼠标/手柄游戏输入；
- 调整游戏速度；
- 注入攻击逻辑。

CDP 只绑定本机 localhost。即使管理器退出，游戏和浏览器也应继续正常使用。

## 离线回归

仓库根目录可执行：

```bat
py -3 -m unittest discover parallel\BROWSER_FLEET\tests -v
```

回归覆盖窗口排列、数量/端口保护、独立 profile/端口分配、设置持久化、manifest 安全字段和中文 owner UX smoke test。

## 真人 Windows 验证

后续真人验证只需要：
1. 双击 `RUN_WOF_FLEET.cmd`；
2. 输入 `10`；
3. 确认 10 个窗口出现并自动排列；
4. 至少在两个窗口正常进入 WOF 房间；
5. 按 `S`，确认对应房间逐步显示“浏览器：已连接 / WOF 页面：已找到 / Worker：已找到”；
6. 用 `R` 重启一个房间，确认其他房间不受影响；
7. 用 `A` 全部关闭。

不需要 DevTools、不需要 Worker Console、不需要手工 RAM 检查，也不会注入游戏输入。

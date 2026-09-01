# Recommended WOF Alpha User Bootstrap Path

更新时间：2026-09-01

## 目标 UX

普通 Alpha 用户不需要知道 `gstyphoon.js`、Worker console、execution context、`fetch(...).then(eval)`。

### 一次性准备

安装 **WOF Alpha Bootstrap** Chrome/Chromium 扩展。

正式给 Alpha 用户的分发应优先：

1. Chrome Web Store private/unlisted；或
2. 组织/测试组受控安装。

不推荐把“打开 chrome://extensions -> Developer mode -> Load unpacked”当普通用户正式流程；它可以用于 RC2 工程验收，但不能作为最终关闭 `ALPHAQA-004` 的用户文档。

扩展权限应最小化：

- `debugger`；
- 仅 WOF 游戏站点所需的 host/origin 权限；
- 如扩展后台直接获取 canonical loader，再加精确的 GitHub raw host 权限。

---

## 用户每次启动

### 支持路径

1. 用户正常打开 WOF 游戏页面。
2. 正常启动/进入游戏，让 emulator 运行。
3. 点击浏览器工具栏的 **WOF Alpha** 图标。
4. 点击 **启动 WOF Alpha**。
5. UI 显示短暂状态：
   - `正在连接游戏…`
   - `正在启动 Alpha…`
6. 成功后只显示：
   - `WOF Alpha 已启用`
7. 游戏内 HUD 进入正常 Alpha 行为。

用户不需要打开 DevTools，也不需要复制任何 Console 命令。

### 可选后续优化

RC2 先做显式点击最安全。待实机稳定后可以增加：

- “在此站点自动启动 Alpha”用户开关；
- 自动等待 `gstyphoon.js` Worker 出现后启动；
- 页面 reload 后自动恢复。

但自动启动不是关闭 `ALPHAQA-004` 的必要条件。

---

## 扩展内部时序

### 0. User gesture

只由用户点击“启动 WOF Alpha”触发 debugger attach。

### 1. Validate tab

- 当前 tab URL 必须在支持 origin allowlist；
- 不满足则显示 `此页面不是受支持的 WOF 游戏页面`，不 attach。

### 2. Attach root tab

```text
chrome.debugger.attach({tabId}, "0.1")
```

若 Chrome 已被 DevTools/其他 debugger 占用而 attach 失败：

- 不继续；
- 显示明确错误；
- 不伪装成 Alpha 已加载。

### 3. Auto-attach related workers

监听 `Target.attachedToTarget`，再调用：

```text
Target.setAutoAttach
  autoAttach = true
  waitForDebuggerOnStart = false
  flatten = true
  filter = worker targets
```

关键点：`setAutoAttach` 对已经存在的相关 worker 也能附加，所以用户不需要“在 Worker 创建前”抢时机。

### 4. Select exactly one game Worker

候选必须同时满足：

- `targetInfo.type == "worker"`；
- 与当前 tab 相关联；
- URL basename/path 匹配 `gstyphoon.js`（query 可变）；
- 只读 runtime probe 与当前批准的 Emscripten/WASM identity predicate 相符。

结果：

- 0 个：`尚未检测到游戏 Worker，请确认游戏已启动后重试`；
- 1 个：继续；
- >1 个：`检测到多个候选 Worker，Alpha 未启动`，fail closed。

不要通过“第一个 Worker”“最大的 HEAP”“最近创建”之类启发式强行选一个。

### 5. Obtain canonical loader

Bootstrap 不包含 predictor 逻辑。

获取当前 RC2 release descriptor 指定的 canonical loader source，并验证：

- HTTP success；
- releaseId；
- expected loader release；
- 若 release descriptor 提供 digest，则校验 digest。

失败则不执行。

### 6. Inject Worker first

对 selected Worker CDP session：

```text
Runtime.evaluate(canonical loader source)
```

然后单独读取 Worker runtime status，例如：

```text
self.WOFALPHA?.status?.()
```

至少确认：

- 对象存在；
- mode 是 Worker/runtime 模式；
- release/version 与 release descriptor 一致；
- engine/running 为 true；
- 没有 unsupported-runtime diagnostic；
- 产品 read-only invariant 保持成立。

Worker 检查失败：

- 不安装 top HUD；
- 显示 `Alpha 未启用：游戏运行时不受支持/启动失败`；
- detach。

### 7. Inject top page second

Worker 成功后，在 root page target 运行同一 canonical loader。

然后读取：

```text
window.WOFALPHA
window.WOFALPHAHUD?.status?.()
```

至少确认：

- top loader object 存在；
- mode 是 top HUD；
- HUD WebGL hook 成功；
- 无 HUD initialization error。

### 8. End-to-end freshness handshake

**这是关闭 ALPHAQA-004 最重要的 success gate。**

不能用以下任一条件单独判断成功：

- console 打印 `HUD installed`；
- `window.WOFALPHA` 存在；
- 游戏画面出现“Alpha 已加载”；
- Worker eval 没抛异常。

必须等到 top HUD 确认收到当前 Worker 的 fresh state/ready signal。

当前 RC1 已有 `WOFALPHAHUD.status().connected` 的概念；RC2 若引入 per-session nonce/channel，则应验证当前 session 的 ready/state，而不是只验证固定 channel 上“某处有消息”。

推荐 success predicate：

```text
workerRuntimeOk
&& topHudOk
&& hudConnected
&& hudMessageAge <= stale threshold
&& session/release identity matches
```

只有全部为 true：扩展 UI 才显示 `WOF Alpha 已启用`。

### 9. Detach

无论成功还是失败，都在 bootstrap 流程结束时：

```text
chrome.debugger.detach({tabId})
```

Alpha runtime/HUD 应继续自行运行；扩展不持续调试。

---

## 失败 UX

失败必须简短、可恢复、fail closed。

| 情况 | 用户看到 | 行为 |
|---|---|---|
| 游戏尚未启动 | `尚未检测到游戏，请启动游戏后重试` | 不注入 |
| 没有 gstyphoon Worker | `尚未检测到游戏 Worker` | 不注入 |
| 多个候选 Worker | `无法唯一确认游戏 Worker` | 不注入 |
| runtime probe 不通过 | `当前游戏运行时不受支持` | 不注入 |
| Worker loader 失败 | `Alpha runtime 启动失败` | 不安装 HUD |
| top HUD 失败 | `Alpha HUD 启动失败` | 不宣称成功；可调用产品 stop/dispose 清理 |
| HUD 没收到 fresh state | `Alpha 未连接到游戏数据` | 不宣称成功 |
| debugger attach 失败 | `浏览器当前无法启动 Alpha；请关闭 DevTools/其他调试器后重试` | 不继续 |

绝不允许失败状态只留下“看得见 HUD，所以似乎成功”。

---

## 为什么这比 Worker hook 更适合 RC2

Worker constructor hook 的最佳情况仍要求在 Worker 创建前运行，并且真正注入代码通常需要 wrapper/replacement worker。对当前 WOF emulator，这会引入未证明的 Emscripten asset/URL/CSP 兼容性。

CDP 路径：

- 直接作用于真实 `gstyphoon.js` Worker；
- Worker 已创建也能发现；
- 不改变 game worker URL；
- 与当前人工 DevTools Worker-console eval 行为最接近；
- 把“研究员手工操作”变成“扩展自动操作”。

这正是 RC2 所需的最小可靠产品支持层。

---

## Alpha 之后的长期方向

如果未来获得游戏宿主启动代码的正式控制权，首选迁移到第一方 bootstrap contract：

```text
page/game host
  -> 创建 gstyphoon Worker
  -> Worker 内置受限 WOF bootstrap message/loader hook
  -> top HUD 正式入口
```

那时可移除 `debugger` 权限和扩展注入层。

在当前仓库/架构下，不应为了追求“看起来更轻”而使用未经 Browser 证明的 Worker wrapper。
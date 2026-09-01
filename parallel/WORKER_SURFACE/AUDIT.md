# WOF Chrome Worker Surface / CDP Target 暴露审计

更新时间：2026-09-01  
状态：**AUDIT COMPLETE — 根因已缩小到一组可判别的 CDP surface 假设；只剩一次最小真人 Windows 一键诊断。**

## 1. 本线范围

本线只审计真实 Chrome/Edge 中 WOF runtime 的 Worker / target / execution-context 暴露方式。

明确不做：
- 不修改 `parallel/PYLAUNCH/**`；
- 不修改 `parallel/BROWSER_FLEET/**`；
- 不修改 `parallel/WOF052L_RECORDER/**`；
- 不修改 `product/alpha/**`；
- 不替换 `window.Worker`；
- 不写游戏 RAM；
- 不注入游戏输入。

真人已有事实：Chrome 151 localhost CDP 已连接，游戏可以正常进入房间并运行；PYLAUNCH `browser_connected=true`、`read_only=true / ram_writes=0 / input_injection=false`，但 `wof_page_found=false / worker_found=false`，诊断为 `no gstyphoon worker target`。

## 2. 先纠正两个容易误读的事实

### 2.1 `wof_page_found=false` 不是“Chrome 没有 WOF page”的独立证据

当前 `parallel/PYLAUNCH/wof_launcher/probe.py` 先：
1. `Target.getTargets`；
2. 只筛 `type == "worker"` 且 URL 匹配 `gstyphoon*.js`；
3. 如果 0 个，立即返回 `TargetChoice(None, None, ..., "no gstyphoon worker target")`。

因此当前 proof 的 `wof_page_found=false` 主要是 Worker 早退的副产品。主修复必须把 page discovery 与 worker discovery 解耦。

### 2.2 不能把问题简单归因为“Chrome 151 的 Target.getTargets 看不到 dedicated Worker”

Chromium 当前 Target domain 的 `getTargets` 遍历 `DevToolsAgentHost::GetOrCreateAll()`；当前 Chromium 源码中 `GetOrCreateAll()` 明确加入 DedicatedWorker、SharedWorker、ServiceWorker、RenderFrame、WebContents 等 agent hosts。

Protocol 默认 TargetFilter 也不是只看 page；未显式指定时默认是“排除 browser/tab，其余包含”。

因此：**对于一个稳定存在、已创建 agent host 的 dedicated worker，`Target.getTargets` 理论上应具备暴露能力。**

这意味着真人失败更可能发生在：
- 当前 PYLAUNCH 的 `type + URL` 前置过滤；
- target 的生命周期 / URL 更新；
- related target / frame execution-context surface；
- 或 WOF runtime 实际已不再位于当前假设的独立 dedicated worker context。

## 3. 当前仓库的结构性发现

### A. 三个工具共享了同一类硬过滤假设

PYLAUNCH 只接受 `type == "worker"`，且 TargetInfo URL 必须正则匹配 `gstyphoon*.js`，匹配前完全不做 module/heap probe。

WOF-052L 同样先按 `worker + gstyphoon URL` 筛选。

Browser Fleet 的 `/json/list` 只把 `worker/shared_worker + URL 包含 gstyphoon` 算作 Worker OK。

因此三个工具的“Worker WAIT”不是三份独立证据，它们高度相关地依赖同一 surface 假设。

### B. PYLAUNCH 当前 CDP client 丢弃全部 protocol events

`parallel/PYLAUNCH/wof_launcher/cdp.py` 的接收线程只处理带整数 `id` 的 command response。

所有无 `id` 的事件都会被静默丢弃，包括：
- `Target.targetCreated`；
- `Target.targetInfoChanged`；
- `Target.targetDestroyed`；
- `Target.attachedToTarget`；
- `Runtime.executionContextCreated`。

所以当前实现即使以后只把 `setDiscoverTargets` / `setAutoAttach` 加进 allowlist，也仍然无法工作；必须先保留/路由 event stream。

### C. Worker -> page 关联先看 `openerId` 是错误模型

当前 `_find_page_for_worker()` 首先读取 Worker 的 `openerId`。

现代 CDP `TargetInfo` 把：
- `openerId` 定义为 opener target；
- `parentId` 定义为 parent target；
- `parentFrameId` 明确用于 `iframe` 和 `worker`，表示创建 Worker 的祖先 frame。

Chromium worker agent host 本身也保存 `parent_id` / `parent_frame_id`。

因此 Worker 归属关系应以 `parentId / parentFrameId` + frame/context 映射为主，`openerId` 不能作为 Worker 主关联键。

### D. Worker TargetInfo URL 存在真实生命周期窗口

Chromium dedicated worker DevToolsAgentHost 可以在 renderer worker thread 真正建立前就创建；后续 `ChildWorkerCreated()` 才写入真实 URL/name。

所以 `targetCreated` 时 URL 为空/暂态、后续 `targetInfoChanged` 更新，是一个真实可存在的 surface。

旧 PYLAUNCH 只轮询快照，且在 URL 不匹配时完全不 probe，这会放大这一风险。

### E. 历史仓库只证明“构造参数 URL”曾匹配 gstyphoon，不证明 Chrome 151 的 TargetInfo.url 必然相同

RC3 旧 bootstrap 曾在 page 侧拦截 `new Worker(url, options)`，只有构造参数的绝对 URL 匹配 `gstyphoon*.js` 才进入 wrapper 路径。这证明游戏宿主过去确实创建过 gstyphoon Worker。

但 RC5 已移除 Worker replacement，而 CDP 的 `TargetInfo.url` 可能反映 worker 最终 URL / redirect / 生命周期中的当前 URL；因此不能把 page constructor URL predicate 当成 CDP target identity authority。

## 4. 最可能根因排序

### #1 — Target URL / type 前置过滤漏掉真实 runtime surface

**当前最高概率。**

理由：真游戏正常运行；历史宿主确实创建 gstyphoon Worker；当前实现却在 module probe 前就因 `type=="worker" + TargetInfo.url` 不匹配而完全放弃。

真人诊断如果发现某个 worker-like target 的只读 Emscripten module probe 成功、但 TargetInfo.url 不含 gstyphoon，即可锁死。

### #2 — 需要 related-target / auto-attach / event surface 才能可靠观察与关联

**高概率。**

CDP 官方提供 `Target.setAutoAttach(autoAttach=true, flatten=true)` 专门自动附加已有/新出现的直接相关 iframe/worker，并通过 `Target.attachedToTarget` 通知。

当前代码不启用 auto-attach、不保留事件、不递归关联 child sessions。

### #3 — target lifecycle / `targetInfoChanged` 时序

**中高概率。** Dedicated worker agent host 可以先存在、URL 后补。如果真人 JSON 出现 `targetCreated(url="") -> targetInfoChanged(url=...)` 且模块只在后阶段可 probe，则单快照 + URL 预筛存在时序漏洞。

### #4 — WOF runtime 位于 page/iframe execution context，而不是独立 Worker target

**中概率，必须排除。** Chrome debugger/CDP 文档明确：同进程 iframe 可能共享同一个 target，只在 Runtime execution contexts 中区分；OOPIF/worker 则可能是关联 target。

### #5 — Worker 确实存在，但 WASM/HEAP 尚未 ready 或 runtime globals 变形

**较低概率。** 此时应看到 worker-like target，但 module probe 失败。主修复不能凭 URL 接受，仍应等待 module readiness / exact identity。

### #6 — Chromium/WOF 平台根本不暴露可附着 runtime surface

**当前最低概率。** Chromium 源码和 CDP protocol 都存在 dedicated worker target/auto-attach surface；在没有真人 raw topology 之前，不支持宣布平台限制。

## 5. 给 PYLAUNCH 主修复帖的可实施建议

以下是建议，**不在本审计线修改 PYLAUNCH**。

### 5.1 Discovery 层

1. page discovery 与 Worker discovery 解耦，任何时候都独立报告 page。
2. CDP client 必须支持 protocol event queue/callback，不能继续丢无 `id` 消息。
3. browser-level 使用 `Target.setDiscoverTargets(discover=true, broad filter)`，跟踪 `targetCreated / targetInfoChanged / targetDestroyed`；`Target.getTargets` 只作为 snapshot，不作为唯一来源。
4. 对候选 WOF page/iframe attach with `flatten=true`，再 `Target.setAutoAttach(autoAttach=true, waitForDebuggerOnStart=false, flatten=true)`，处理 `attachedToTarget`；对 child session 递归建立关联，防止 nested worker/iframe 漏失。
5. reconnect 时清空 target/session/context cache。

### 5.2 Candidate 选择

不要再把 `gstyphoon URL` 当 acceptance gate，把它降级为 hint。

候选至少覆盖：
- `worker`；
- `shared_worker`；
- 与 WOF page/frame 有 parent 关系的其他 attachable target；
- 必要时 page/iframe execution context。

对候选只读执行：
- Worker/global `location.href`；
- Emscripten module structure：`HEAPU8 instanceof Uint8Array`、`HEAPU32 instanceof Uint32Array`、共用 buffer；
- heap size / module key。

最终 authority 仍必须是：
1. 唯一 module-ready runtime；
2. 唯一可关联 WOF page/session；
3. exact World 921031 full CPU-logical SHA-256；
4. 多候选/歧义 => fail closed。

### 5.3 Page/Worker 关联

优先关系：
1. `parentId`；
2. `parentFrameId`；
3. page `Page.getFrameTree` / execution-context `auxData.frameId`；
4. WOF page game-surface probe。

不要把 Worker `openerId` 当 parent。

### 5.4 Execution-context fallback

对 page/iframe session：
- `Runtime.enable`；
- 记录 `Runtime.executionContextCreated`；
- 对 default/main-world context 做同一只读 module probe；
- 通过 `auxData.frameId` 映射 frame。

这样可覆盖 same-process iframe 不单独成为 target 的情况。

### 5.5 安全边界

新增 discovery 方法仍必须限定为只读/附着类：Target discovery/attach/detach/auto-attach、Runtime enable/evaluate（只读表达式）、Page frame-tree introspection。

继续禁止 `Input.*`、游戏 RAM 写、Worker replacement、page startup interception、Chrome native process-memory hook。

## 6. 一键真人诊断

新增：`parallel/WORKER_SURFACE/RUN_WORKER_SURFACE_DIAG.cmd`

行为：
1. 自动找已经开放 localhost CDP 的 Chrome/Edge（含 PYLAUNCH/Fleet 常用端口）；
2. 找不到则自动启动专用 debug Chrome/Edge；
3. 中文提示 owner 只需正常进入 WOF 房间；
4. 自动同时采集 HTTP `/json/list`、broad `Target.getTargets`、target discover lifecycle events、related auto-attach targets、`parentId / parentFrameId / openerId`、page/iframe frame tree、Runtime execution contexts，以及每个可附着 surface 的只读 Emscripten module/heap-length probe；
5. 输出唯一文件 `parallel/WORKER_SURFACE/WORKER_SURFACE_DIAG.json`。

它不会打开 DevTools、要求选 Worker、要求粘 JS、读/写游戏 RAM 内容、发送游戏输入或改 Worker。

## 7. 真人 JSON 的判定表

| JSON 证据 | 根因判定 |
|---|---|
| module-ready Worker，但 TargetInfo.url 不含 gstyphoon | `WORKER_URL_FILTER_MISMATCH` 锁死 |
| module-ready related target 不在 direct snapshot | `RELATED_TARGET_ONLY` 锁死 |
| module 在 page/iframe execution context | `RUNTIME_IN_PAGE_OR_FRAME_CONTEXT` 锁死 |
| targetCreated 空/旧 URL，随后 targetInfoChanged | `TARGET_INFO_LIFECYCLE` 成立 |
| direct gstyphoon Worker + module 已存在 | 旧 proof 更像时序/旧路径/连接时刻问题 |
| worker-like target 有、module 无 | 继续查 module readiness/global 形态 |
| 三种 surface 全无 | 才开始考虑宿主/Chromium平台级限制 |

## 8. 文档依据

主要协议/源码依据：
- Chrome DevTools Protocol Target domain：`Target.getTargets`、`setDiscoverTargets`、`setAutoAttach`、`TargetInfo.parentId/parentFrameId`；
- Chromium `TargetHandler::GetTargets`：遍历 `DevToolsAgentHost::GetOrCreateAll()`；
- Chromium `DevToolsAgentHost::GetOrCreateAll()`：包含 dedicated/shared/service workers、frames、web contents；
- Chromium TargetFilter 默认：排除 browser/tab，其余包含；
- Chromium DedicatedWorkerDevToolsAgentHost：保存 parent frame，并允许 worker thread 建立后通过 `ChildWorkerCreated` 补 URL/name；
- Chrome debugger/CDP guidance：related worker/iframe 使用 `attachedToTarget` + `setAutoAttach`，same-process iframe 可能通过 Runtime execution contexts 区分。

## 9. Stop condition

**已满足提示中的停止条件：只剩一个最小真人诊断。**

仓库/官方源码已足够排除“单纯 Chrome 151 不支持 dedicated worker CDP”的泛化结论，也已确认当前实现存在：
- 过早的 type/URL hard filter；
- event stream 丢弃；
- Worker parent 关联字段使用错误。

但旧 proof 没保存 raw topology，因此不能从现有证据诚实地在 #1/#2/#3/#4 中唯一选择。

下一步不再需要更多离线发散。只运行一次中文 CMD，返回一个 JSON，即可给 PYLAUNCH 主修复帖锁定真实 Chrome/WOF surface。

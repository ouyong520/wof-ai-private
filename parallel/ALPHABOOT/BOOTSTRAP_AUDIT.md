# WOF Alpha Bootstrap Audit

更新时间：2026-09-01

## 1. 审计问题

目标不是重新设计 Alpha predictor，也不是改变 `product/alpha/**`。本审计只回答：

> 怎样让普通用户在不知道 DevTools Worker execution context 的情况下，同时启用 live `gstyphoon.js` Worker 内的 Alpha runtime 与 top-page HUD？

当前 RC1 的支持路径要求同一 `wof_alpha_loader.js`：

- 在 `gstyphoon.js` Worker 运行一次；
- 在 top page 运行一次。

这在技术上能工作，但产品上属于 researcher/developer workflow。

---

## 2. 当前架构边界

### 2.1 Worker 是 detector/runtime 所在地

`product/alpha/wof_alpha_loader.js` 在非 Window context：

- 解析/验证 WASM/Emscripten module；
- 读取 CPS RAM；
- 启动 Alpha engine；
- 通过 `BroadcastChannel` 发布 state / diagnostic。

过去的 `wof_v19_bootstrap.js`、`wof_v4_install_once.js`、`wof_hud_worker.js` 也都遵循同一事实：RAM/runtime 在 live emulator Worker 内。

### 2.2 top page 是 HUD 所在地

`product/alpha/wof_alpha_loader.js` 在 Window context：

- 加载 `wof_alpha_hud.js`；
- HUD 使用 top-page game WebGL canvas/context；
- 通过 BroadcastChannel 接收 Worker state。

`wof_canvas_probe.js` / `wof_canvas_hud.js` 已证明 top page 可以稳定向游戏 WebGL 输出 HUD，但这不等于 top page 拥有 Worker 的 JS execution context。

### 2.3 当前 Window loader 没有 Worker 注入口

Window 分支只安装 HUD并返回。它没有：

- 保存 `new Worker(...)` 返回对象；
- 识别 live `gstyphoon.js` Worker；
- Worker-side `eval` RPC；
- 预置 bootstrap `postMessage` handler。

所以“同一 URL 可以在两个 context 执行”不代表“从一个 context 可以自动跨到另一个 context”。

---

## 3. 候选方案审计

### A. 保持当前双 Console

**结论：淘汰。**

优点：已经证明技术可运行。

缺点：正是 `ALPHAQA-004`；用户必须理解 DevTools execution context、识别 `gstyphoon.js`、粘贴两次。错误 context 还可能出现 HUD 已加载但 detector 未运行的假成功。

### B. top-page 单粘贴，拿 Worker 对象后 `postMessage` loader

**结论：当前架构不可用。**

父页面标准 Worker API 可以 `postMessage()`，但 Worker 必须已经存在一个知道如何解释 bootstrap message 的 handler。当前 `gstyphoon.js` / Alpha 产品路径没有仓库证据表明存在此 handler。

因此拿到 Worker object ≠ 获得 Worker global scope 的任意代码执行能力。

### C. bookmarklet / top-page 单粘贴提前 monkeypatch `window.Worker`

**结论：不选为 RC2 支持路径。**

只有在 emulator Worker 创建前执行才有机会拦截。若 Worker 已存在就太晚；普通用户难以判断时机。

更关键的是，为了真正向 Worker 注入 Alpha，需要把原 Worker 包进 blob/data/wrapper worker 或改写 worker source。这样可能改变：

- worker script URL；
- `self.location`；
- Emscripten scriptDirectory / wasm/asset 相对路径解析；
- CSP / `worker-src` / blob 行为；
- classic/module worker 行为。

当前仓库没有真实 Browser 证据证明 `gstyphoon.js` 在这种 wrapper 下仍与原 worker 等价。把这个当 RC2 主路径会引入新的 emulator bootstrap 风险。

### D. userscript `document-start` Worker hook

**结论：不选为 RC2 支持路径。**

它比 bookmarklet 更早，但核心问题仍和 C 相同：userscript 可以拦截构造，却不能凭标准 page API 对原始、已运行 Worker 任意 evaluate。若采用 wrapper，仍承担 Emscripten URL/context 风险；而且 userscript 的 isolated-world / MAIN-world 注入本身增加浏览器差异。

### E. 修改游戏 Worker，让它原生接受 Alpha bootstrap message

**结论：不是当前可实施边界。**

这是最干净的长期站点集成方式之一，但意味着要控制/修改游戏端 `gstyphoon.js` 或它的宿主启动代码。当前任务只允许 Alpha 支持侧方案，而且仓库没有该站点产品源作为可修改入口。

### F. Chrome/Chromium 扩展 + `chrome.debugger` / CDP

**结论：SELECTED。**

这是唯一一个同时满足以下条件、且不需要改写原 emulator Worker 的候选：

- Worker 已经存在也可以处理；
- 用户不打开 DevTools；
- 用户不识别 execution context；
- 不替换 `gstyphoon.js` URL；
- 不复制 emulator worker；
- 可以在真实 Worker target 上执行 canonical Alpha loader；
- 可以在真实 top page target 上执行同一 loader；
- 可以在完成后立即 detach。

Chrome 官方 `chrome.debugger` API 是 CDP 的扩展传输层。`Target.setAutoAttach` 可以附加页面关联的 existing/new workers；`Runtime.evaluate` 可以在对应 target 的 global object 执行 expression。这与目前人工在 DevTools Worker console eval 的语义最接近，只是把 execution-context discovery 自动化。

代价：

- 扩展需要 `debugger` 权限；
- 启动期间 Chrome 可能显示 debugger attached 提示；
- 必须严格限定只在用户主动启动的当前 tab 上工作，并在成功/失败后 detach。

对 Alpha 阶段来说，这个代价小于要求每个用户学习 Worker console；以后若游戏宿主可提供正式 Worker bootstrap hook，可以再移除 debugger 权限。

---

## 4. Selected architecture

```text
User
  |
  | click “启动 WOF Alpha”
  v
WOF Alpha Bootstrap extension
  |
  | chrome.debugger.attach(current tab)
  | Target.setAutoAttach(type=worker, flatten=true)
  v
related targets
  |-- top page target
  `-- worker target(s)
          |
          | filter URL / target identity
          `--> exactly one gstyphoon.js candidate

Extension fetches/pins canonical Alpha loader source
          |
          +--> Runtime.evaluate in gstyphoon Worker
          |       -> WOFALPHA worker runtime
          |       -> BroadcastChannel state
          |
          `--> Runtime.evaluate in top page
                  -> WOFALPHAHUD
                  -> receives Worker state

Extension verifies:
  worker WOFALPHA.status() OK
  top WOFALPHA mode/top HUD OK
  HUD status.connected == true (or RC2 equivalent session handshake)

Only then:
  show “Alpha 已启用”
  chrome.debugger.detach()
```

---

## 5. Worker identification

Bootstrap 不得“找到第一个 Worker 就注入”。最低过滤：

1. target 必须是当前 tab 直接/关联的 `worker` target；
2. target URL pathname/basename 必须匹配 `gstyphoon.js`（允许 query string）；
3. 必须只有一个候选；
4. 在注入前执行只读 runtime probe，至少确认 worker global 中存在与现有 loader 判定兼容的 Emscripten/WASM module 候选：
   - `HEAPU8 instanceof Uint8Array`；
   - `HEAPU32 instanceof Uint32Array`；
   - 两者 `.buffer` 相同；
5. 若 0 个或 >1 个候选、probe 不通过、target 在过程中消失：**不注入，fail closed**。

不要把本 bootstrap 审计升级成 `wofr1 / World 921002` 身份研究；更严格 runtime identity 由对应 PM lane 提供。Bootstrap 只消费已批准 identity predicate。

---

## 6. 注入顺序

推荐：**Worker first, top HUD second**。

理由：

- 当前失败模式之一是 top HUD 存在但 Worker detector 不存在；
- 先证明 Worker runtime 成功，再装 HUD，可减少假成功窗口；
- top HUD 安装后应很快收到 Worker state，便于 end-to-end handshake。

步骤：

1. attach；
2. enumerate/auto-attach related worker targets；
3. unique worker identity probe；
4. worker `Runtime.evaluate(canonicalLoader)`；
5. worker 读取 `self.WOFALPHA?.status?.()`，核对 release/mode/running；
6. top-page `Runtime.evaluate(canonicalLoader)`；
7. top 读取 `window.WOFALPHA` / `window.WOFALPHAHUD.status()`；
8. 等待 fresh Worker message / connected；
9. success UI；
10. detach。

任何一步异常都执行清理 + detach，并明确显示“Alpha 未启用”。

---

## 7. canonical loader 与 release pinning

Bootstrap extension 只负责 transport / target selection / verification，**不得复制 predictor、RAM offsets、HUD logic 或 warning rules**。

它应消费 canonical `product/alpha/wof_alpha_loader.js`。

RC2 实现时应有一个 release descriptor，至少包含：

```text
releaseId
loaderUrl or immutable commit URL
expectedLoaderRelease
optional sha256
supported game origin(s)
worker URL predicate
runtime identity predicate version
```

如果 canonical loader 自己仍从 `main` 拉内部文件，那么“loader source 被 pin”仍不等于完整 bundle immutable；这属于 RC2 release owner 需要解决的产品发布细节，本审计不修改产品代码。

---

## 8. 安全/边界要求

- 用户必须主动点击启动；不要静默 attach 任意 tab。
- host allowlist 必须窄，只接受 WOF 游戏 origin。
- worker URL / runtime probe 不唯一则 fail closed。
- 不执行输入注入；保持 Alpha read-only / `ramWrites=0` 产品边界。
- 不修改游戏 Worker source，不 terminate/recreate live emulator worker。
- 失败后不得保留“HUD 看起来正常但 detector 未运行”的 UI。
- attach 仅覆盖启动窗口；完成/失败都 detach。
- 不把 `debugger` 权限用于网络抓取、DOM 监控或其他与启动无关用途。

---

## 9. 结论

**RC2 普通用户支持路径应采用 Chrome/Chromium Bootstrap extension + CDP target injection。**

这是一个实现就绪的设计：它自动化当前已验证的两-context loader 语义，同时避免不受证据支持的 Worker wrapper/replacement。
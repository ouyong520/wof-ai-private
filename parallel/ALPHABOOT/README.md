# ALPHABOOT — WOF Alpha 普通用户加载审计

更新时间：2026-09-01

## 范围

本目录只负责 `ALPHAQA-004`：让普通 Alpha 用户不再需要手动找到 DevTools 的 live `gstyphoon.js` Worker execution context，再分别在 Worker / top page 两处执行 Alpha loader。

`product/alpha/**` 在本审计中保持只读；本目录不修改 Alpha 产品代码。

> 原任务引用 `parallel/PM/ALPHA_BOOTSTRAP_START_PROMPT.md`；当前仓库实际文件名为 `parallel/PM/ALPHA_BOOTSTRAP_AUDIT_START_PROMPT.md`，本审计按后者执行。

## 结论

推荐唯一支持路径：**Chrome/Chromium 小型 WOF Alpha Bootstrap 扩展，通过 `chrome.debugger` + Chrome DevTools Protocol (CDP) 自动找到当前标签页关联的 `gstyphoon.js` dedicated Worker，并在 Worker 与 top page 自动执行同一 canonical Alpha loader。**

普通用户路径应收敛为：

1. 一次性安装 WOF Alpha Bootstrap 扩展（正式 Alpha 应使用签名/私有或 unlisted 分发，不要求用户开启开发者模式）。
2. 正常打开游戏并进入可运行状态。
3. 点击一次扩展里的“启动 WOF Alpha”（也可以以后做成受控自动启动）。
4. 扩展短暂附加当前 tab，自动定位唯一 `gstyphoon.js` Worker。
5. 扩展先在 Worker 执行 canonical `product/alpha/wof_alpha_loader.js`，再在 top page 执行同一 loader。
6. 只有在 Worker runtime + top HUD + HUD-to-Worker freshness handshake 全部成立后显示“Alpha 已启用”。
7. 启动完成即 `chrome.debugger.detach()`；扩展不持续调试游戏。

用户不需要：

- 打开 DevTools；
- 切 execution-context dropdown；
- 识别 `gstyphoon.js`；
- 粘贴两次代码；
- 知道 Window / Worker 的运行边界。

## 为什么不是 top-page 单粘贴 / bookmarklet

当前 `wof_alpha_loader.js` 的 Window 分支只安装 HUD，然后明确要求在 live Worker 再运行同一 loader；它没有拿到 Worker execution context，也没有现成的 worker-side bootstrap message handler。

标准 `Worker` 父页面接口只有消息/事件/终止等能力，父页面拿到 `Worker` 对象并不等于可以向一个已经运行中的 Worker 任意 `eval`。要靠 `postMessage()` 注入，Worker 自己必须已经实现对应的 bootstrap handler；当前产品路径没有这个入口。

因此：

- **游戏已经创建 Worker 之后**，普通 page script / bookmarklet 无法可靠复刻 DevTools Worker-console `eval`。
- **游戏创建 Worker 之前** monkeypatch `window.Worker` 并改成 blob/wrapper worker 理论上可研究，但会改变 worker script URL / `self.location` / Emscripten 相对资源加载环境，并且当前仓库没有证明 `gstyphoon.js` 可以安全被 wrapper 化；不应作为 RC2 的“可靠普通用户路径”。
- CDP 方案直接附加真实、原始的 Worker target，不改 worker URL，也不重建 emulator Worker，因此风险更小、与当前已验证的手工 Worker-console 加载语义最接近。

## 仓库证据摘要

- `parallel/ALPHAQA/FINDINGS.md` 的 `ALPHAQA-004` 已把“手工选择 live Worker + 再切 top page”列为 P1 普通用户阻断。
- `product/alpha/wof_alpha_loader.js` 已经实现同一 loader 的 Window / Worker 两分支，但 Window 分支没有 Worker 注入能力。
- `wof_hud_worker.js` 与 `wof_canvas_hud.js` 的历史证明 Worker 负责 RAM/runtime、top page 负责游戏 WebGL HUD，两侧通过 BroadcastChannel 通信；它们仍然需要分别进入两个 execution context。
- `WOF_AI_NEW_THREAD_START.md` 明确要求不要声称 JS 能自动改变 DevTools execution-context dropdown。

## 外部浏览器能力依据

- MDN Worker API：父页面侧 `Worker` 公开的关键控制接口是 `postMessage()` / `terminate()`，不是远程 `eval`：
  - https://developer.mozilla.org/en-US/docs/Web/API/Worker
  - https://developer.mozilla.org/en-US/docs/Web/API/Worker/postMessage
- Chrome `chrome.debugger`：扩展可以附加 tab 并发送 CDP command：
  - https://developer.chrome.com/docs/extensions/reference/api/debugger
- CDP `Target.setAutoAttach`：可自动附加与页面关联的 existing/new workers：
  - https://chromedevtools.github.io/devtools-protocol/tot/Target/#method-setAutoAttach
- CDP `Runtime.evaluate`：可在目标 execution context 的 global object 上执行 expression：
  - https://chromedevtools.github.io/devtools-protocol/tot/Runtime/#method-evaluate

## 本目录文件

- `BOOTSTRAP_AUDIT.md`：架构、候选方案与淘汰理由。
- `RECOMMENDED_USER_PATH.md`：普通用户最终路径与实现时序。
- `RC2_ACCEPTANCE_REQUIREMENTS.md`：交给 RC2 owner 的可测试验收条件。

## 决策状态

**SELECTED / IMPLEMENTATION-READY DESIGN**

仍需要 RC2 owner 实现并做一次真实 Chrome/Chromium Browser acceptance；本审计不修改 `product/alpha/**`。
# WOF Worker Surface Audit — Result

更新时间：2026-09-01

结论：**AUDIT COMPLETE — STOP CONDITION REACHED：只剩一次最小真人 Windows 一键诊断。**

## 已锁定的实现缺陷

1. 当前 PYLAUNCH 在任何 module/heap probe 前，硬要求 `type == "worker"` 且 `TargetInfo.url` 匹配 `gstyphoon*.js`。
2. `wof_page_found=false` 不是独立 page 失败证据；当前 discovery 在 0 个 gstyphoon worker 时直接返回 page=None。
3. 当前 CDP receiver 丢弃全部无 command id 的事件，因此无法消费 Target/Runtime 的 discovery/auto-attach/context 事件。
4. 当前 Worker -> page 关联优先使用 `openerId`；CDP 对 worker 提供的是 parent 关系（尤其 `parentFrameId`），该关联模型需要主修复线改正。
5. Browser Fleet 与 WOF-052L 也共享相近的 type/URL prefilter，所以它们的 Worker WAIT 不能视为独立验证。

## 官方 Chromium/CDP 审计结论

- `Target.getTargets` 在现代 Chromium 仍是有效 browser-level target snapshot。
- Chromium 的 `GetOrCreateAll()` 包含 dedicated worker agent hosts。
- 默认 TargetFilter 排除 browser/tab，但包含其余 target 类型。
- `Target.setDiscoverTargets` 提供 target lifecycle events。
- `Target.setAutoAttach` 用于 existing/new related iframes/workers，flat session 通过 `attachedToTarget` 暴露。
- Worker TargetInfo 有 `parentId/parentFrameId`；`openerId` 不是 worker parent。
- Dedicated worker agent host 可先创建、后在 `ChildWorkerCreated` 更新 URL/name，故 `targetInfoChanged` 是必须审计的 surface。

所以不能把当前 P0 归因成“Chrome 151 没有 Worker CDP 支持”。

## 根因排序

1. `TargetInfo.type/url` hard filter 漏掉真实 module-ready runtime。
2. related target / auto-attach / event surface 未被当前 client 消费。
3. targetCreated -> targetInfoChanged 生命周期窗口。
4. runtime 位于 page/iframe execution context。
5. Worker 已看到但 WASM/module 尚未 ready 或 global 形态变化。
6. 真正的平台级不可附着限制（目前证据最弱）。

## 已生成真人诊断

双击：

`parallel/WORKER_SURFACE/RUN_WORKER_SURFACE_DIAG.cmd`

owner 只需在自动连接/启动的浏览器正常进入 WOF 房间。

不需要：
- DevTools；
- Worker Console；
- 手选 execution context；
- 粘贴 JS；
- RAM 检查；
- 游戏输入测试。

输出唯一需要返回的文件：

`parallel/WORKER_SURFACE/WORKER_SURFACE_DIAG.json`

诊断会同时保存 direct targets、discover lifecycle、related auto-attach、execution contexts、frame tree 与只读 module/heap-length surface probe。

## 离线回归

`worker_surface_diag.py --self-test` 已在实现阶段通过。

新增 `tests/test_worker_surface_diag.py` 覆盖：
- Worker URL mismatch；
- related-target-only；
- page/iframe execution-context runtime；
- `targetCreated -> targetInfoChanged` 生命周期；
- read-only allowlist 不含 `Input.*` / `Runtime.callFunctionOn`。

## 安全

固定：
- `readOnly=true`
- `ramWrites=0`
- `inputInjection=false`
- `workerReplacement=false`
- 无 `Input.*`
- 无游戏 RAM 写
- 无 `product/alpha/**` 修改

## 给 PYLAUNCH 修复线

不要在真人 JSON 前继续猜 target URL/type。

拿到 JSON 后，按 `AUDIT.md` 判定表锁定：
- `WORKER_URL_FILTER_MISMATCH`
- `RELATED_TARGET_ONLY`
- `RUNTIME_IN_PAGE_OR_FRAME_CONTEXT`
- `TARGET_INFO_LIFECYCLE`
- 或真正的 `NO_WORKER_SURFACE_OBSERVED`

然后主修复线只实现被证据支持的兼容路径，同时保留唯一 module/heap + exact World 921031 SHA-256 fail-closed gate。

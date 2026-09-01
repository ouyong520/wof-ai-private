# WOF Python Launcher — Fresh Real Chrome Worker Discovery Fix

你负责一个全新的 PYLAUNCH 修复阶段。

仓库：
- `ouyong520/wof-ai-private`

## 开始前必须读取

- `parallel/PYLAUNCH/**` 最新状态
- `parallel/PYLAUNCH/RESULT.md`
- `parallel/PM/ACTIVE_PRIORITIES.md`
- `parallel/PM/RELEASE_READINESS.md`
- `parallel/PM/CHINESE_UI_UX_REQUIREMENT.md`
- Browser Fleet 当前 discovery contract / manifest 支持

## 已有真人 Windows 证据

Owner 已真实运行一键 Windows Proof，并正常进入 WOF 房间。

当时状态：

```json
{
  "browser_connected": true,
  "browser_name": "Chrome/151.0.7922.174",
  "browser_endpoint": "http://127.0.0.1:9223",
  "wof_page_found": false,
  "worker_found": false,
  "wasm_module_found": false,
  "heap_found": false,
  "world_921031": false,
  "identity_reason": "no gstyphoon worker target",
  "read_only": true,
  "ram_writes": 0,
  "input_injection": false,
  "state": "WAITING_WOF"
}
```

游戏本身可正常进入并运行。

因此：
- 浏览器/CDP连接是真实成功的；
- 当前 P0 是 Launcher 对真实 Chrome 151/WOF runtime target topology 的 Worker 自动发现不完整；
- 不要把问题归因给 owner 操作；
- 不要让 owner 打开 DevTools、Worker Console 或粘贴 JS。

## 目标

修复真实 Browser 下 WOF page / native gstyphoon Worker / WASM / heap 的自动发现，使同一个一键真人 Proof 能达到：

```text
浏览器：已连接
WOF 页面：已找到
Worker：已找到
WASM / 内存：已找到
游戏版本：World 921031 已确认
只读模式：开启
游戏内存写入：0
```

并保持游戏正常可玩。

## 必须做

1. 独立审计真实 Chromium CDP target discovery 假设。
2. 不要只假定目标一定以当前 `type=worker + gstyphoon*.js URL` 形式直接出现在 browser-level `Target.getTargets`。
3. 在不影响游戏的前提下，增加足够的只读诊断来识别真实 target 类型、父子/opener/session 关系和 URL 形态。
4. 支持实际 WOF runtime 暴露方式，但必须保持唯一、可验证、fail-closed 的 page/Worker 关联。
5. 最终仍必须通过 WASM/module/heap + exact World 921031 SHA-256 gate 才能接受。
6. 多 tab / 多 worker 情况不能“取第一个”；歧义必须静默/失败关闭。
7. 连接失败、目标找不到、识别失败都只能影响 Launcher，不能影响游戏。
8. 所有 owner-facing UI / tray / status / CMD / error 文本改为简体中文；内部 JSON key 可以保持英文。
9. 技术错误前必须先给中文人话说明，例如：
   `未找到 WOF 游戏 Worker，游戏本身没有受到影响。`
10. 保持一键入口，不要增加 owner 操作复杂度。

## 安全边界

绝对禁止：
- 修改 `product/alpha/**`；
- 修改 WOF-052L Recorder；
- 替换/包装 `window.Worker`；
- Blob/Data/ObjectURL Worker；
- Worker URL rewrite；
- 游戏 RAM 写入；
- `Input.*` 或任何游戏输入注入；
- native Chrome process memory hook；
- 一键出招 / Assist Mode。

继续保持：
- localhost CDP only；
- readOnly=true；
- ramWrites=0；
- inputInjection=false；
- exact World 921031 golden SHA-256：
  `5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62`。

## 测试要求

必须新增离线/模拟 target-topology 回归，包括至少：
- 原有 direct worker target；
- URL 形态差异；
- 多 page / 多 worker；
- stale target；
- opener/parent 可用和不可用；
- target type 与当前假设不同但仍可安全附着的真实兼容路径；
- ambiguity fail-closed；
- WASM 未就绪；
- wrong World identity；
- disconnect/reconnect；
- read-only allowlist 不扩展到输入/写路径。

## Owner UX

最终再次把真人验证压缩成：

```text
下载/双击一个中文一键文件
-> 自动打开专用 Chrome/Edge
-> owner 正常进入 WOF 房间
-> Launcher 自动显示中文状态
```

不要要求 owner 找 GitHub 目录。
如果可能，提供一个可以直接下载的自举 CMD 或最小 ZIP。

## Stop condition

直到满足其一：

1. **FIX READY — 只剩一次新的真人 Windows 一键 Proof**，并给 PM/owner 一个直接下载/双击入口；或
2. 已获得真人 PASS 并写回 GitHub；或
3. 找到一个明确、不可绕过的 Chromium/WOF 平台限制，并给出最小下一步。

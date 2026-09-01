# Discovery V2 Current-HEAD Long Soak Audit — 中文结论

Stage: `DISCOVERY_V2_CURRENT_HEAD_LONG_SOAK_AUDIT_V1`

## 结论

**BLOCKED — DISCOVERY V2 CURRENT-HEAD LONG SOAK — Owner One-Click manifest pins pre-authority-fix Discovery V2 runtimes**

严重度：**P1**

Blocker ID：`P1-OWNER-ONECLICK-STALE-DISCOVERY-V2-AUTHORITY-RUNTIME`

Owner action：**NO**

## 精确 blocker

当前仓库里的 Discovery V2 实现已经继续前进：

- PYLAUNCH `discovery_v2.py` 当前 blob：`ec9d27bfe26557a11187a23853893b898a3366d1`
  - 已包含 `Page.getFrameTree` / `parentFrameId` 页面归属 authority；
  - 每次 `discover()` 开始会清空跨 generation 的 identity cache authority。
- PYLAUNCH `monitor.py` 当前 blob：`4430f7e927265cd3366fd70ce560c375aa878993`
- PYLAUNCH `cdp.py` 当前 blob：`def308bed2a5609be1da26505a15d621395b66aa`
- Recorder 当前 `owner_zh_cn.py` 会安装 `discovery_v2_sync` 与 `hardening_v2`。

但是 Owner 中文一键入口当前读取 `main` 上的：

`parallel/OWNER_ONECLICK/package_manifest.json`

该 manifest 仍固定：

- `packageVersion = 2026.09.01.5`
- `sourceCommit = 7b10867f14f59ca9ab95c0fa6d30530008409371`
- PYLAUNCH `discovery_v2.py = cee0bdef0fe461ab0cb003e6ae198db8c19a5ec2`
- PYLAUNCH `monitor.py = 5ee0ce9a84988d7841799d907ebdfe2a3e68ea56`
- PYLAUNCH `cdp.py = 06480f3aa7ab9261d7f91ab09074e96b4a6befc9`

因此 Owner 一键工具并不会安装 current HEAD 的 authority/generation 修复，而会按照 manifest 的 immutable `baseUrl` 下载历史 commit 的 runtime。

这直接违反本审计要求的：

- current-head authority/generation contract；
- downstream consumer 不能消费旧 authority；
- `owner-facing Chinese path 不退化`。

## 最小复现

1. 在 current HEAD 读取 `parallel/OWNER_ONECLICK/package_manifest.json`。
2. 取 `parallel/PYLAUNCH/wof_launcher/discovery_v2.py` 的 manifest blob：
   `cee0bdef0fe461ab0cb003e6ae198db8c19a5ec2`。
3. 读取 current HEAD 同文件 blob：
   `ec9d27bfe26557a11187a23853893b898a3366d1`。
4. 两者不相等。
5. 当前 `parallel/OWNER_ONECLICK/test_package.py` 的 `PackageTests.test_current_pylaunch_runtime_cannot_outgrow_package` 明确要求 current runtime blob 必须与 manifest blob 相等，因此该 freshness contract 在这个 surface 上确定失败。
6. `parallel/OWNER_ONECLICK/bootstrap_v2.ps1` 从 `main` 下载 manifest，随后使用 `manifest.baseUrl` 和 manifest file list 下载 runtime；所以真实中文一键路径会选择旧 runtime，而不是 current HEAD。

## 为什么是 P1，而不是仅文档漂移

这不是 README/RESULT 过期：manifest 是 Owner 安装器的实际数据平面。

旧包仍能通过自身 blob 完整性校验，但它完整地安装的是**历史 Discovery V2 authority 实现**。也就是说 repository-side P1 修复已经存在，Owner-facing consumer 却仍可能运行修复前版本；formal integration / release preflight 不能把这种路径当成 current-head 证明。

## 已确认的 current-head 状态

- 旧 conformance harness 在 `250ccae3...` 上记录的 PYLAUNCH direct `parentFrameId` P1，当前实现已出现对应生产修复与回归测试，因此本次没有复用旧 blocker。
- 最新 PYLAUNCH identity-cache generation 修复结果记录了 repository-side 28/28 targeted regression；current `discover()` 也能看到 generation-start cache invalidation。
- Recorder current blobs已继续前进：
  - `discovery_v2_sync.py = a66731dbf9dd1c6eac8666b2c42ebe8f3f61eddf`
  - `hardening_v2.py = 4ade786786ec815a0c165c82b25cf41e07f218db`
  - `owner_zh_cn.py = 0e0001b1b9e9ea1239450b1c2a14544ced580c1a`
- Prospective current `live_validator_v2.py = 512c6635d2a8c1bf99cd7f4a5e3f9e45b9b2b3d0`。
- 安全审计 lane 保持只读：`readOnly=true / ramWrites=0 / inputInjection=false`；未修改任何实现组件。

## HEAD drift

- claim 起始 HEAD：`82e08b7bcebf4299781f1a6d9b04679e70789ce8`
- blocker 最终测试 HEAD：`b565af5d490182fb155c7fcc4ad47a2dc3445ce5`
- 审计期间 HEAD 持续前进；PYLAUNCH identity-cache 结果/claim 已落地。
- 从最后一次 blocker 验证到 RESULT 提交之间只出现本审计结果、HUDANCHOR long-stress artifact 与 PM claim 元数据，没有 Owner One-Click manifest / PYLAUNCH / Recorder / Prospective 相关改动，因此 blocker 未被并发提交消除。

## 修复归属

本 lane 的写范围不允许修改：

- `parallel/OWNER_ONECLICK/**`
- `parallel/PYLAUNCH/**`
- `parallel/WOF052L_RECORDER/**`

因此只记录 blocker，不越权修复。

需要由对应 Owner One-Click/package refresh lane：

1. 把 manifest/sourceCommit 刷新到包含 current PYLAUNCH parentFrame + generation authority 修复的提交；
2. 纳入 current Recorder Discovery V2 / hardening 依赖；
3. 更新/保持 fail-closed package freshness contract；
4. 重跑 Owner One-Click integrity + Windows 中文路径；
5. 再启动 fresh current-head audit 验证。

## 停止原因

启动 prompt 明确规定：发现 P0/P1 时立即写精确 blocker 和最小复现，并可按停止条件 A 结束；不得为了“长跑时长”继续消耗工作量。

所以剩余 full/adversarial soak matrix 标记为 `NOT_RUN_STOP_CONDITION_A`，不是被当成 PASS。

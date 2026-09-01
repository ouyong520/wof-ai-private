# WOF Python Launcher — Real Chrome Worker Discovery Fresh Fix Result

Date: 2026-09-01
Status: **FIX READY — 只剩一次新的真人 Windows 一键 Proof**

## Root cause closed in repository

Real Windows evidence proved Chrome/CDP connection and room playability, but the old launcher required browser-level `Target.getTargets` to directly expose a target matching `type=worker + gstyphoon*.js`. If that match was absent, discovery returned before even probing the WOF page.

The fresh fix adds `wof_launcher/discovery_v2.py` and switches the monitor to it.

Preferred discovery now is:

```text
browser CDP
-> page targets
-> page session Target.setAutoAttach
-> related iframe / worker target tree
-> fixed read-only Worker WASM/heap probe
-> exact World 921031 SHA-256 gate
```

The original direct Worker path remains a compatibility fallback.

## Safety retained

Unchanged and enforced:
- localhost CDP only;
- readOnly=true;
- ramWrites=0;
- inputInjection=false;
- no `product/alpha/**` modification;
- no WOF-052L modification;
- no `window.Worker` replacement/wrapping;
- no Blob/Data/ObjectURL Worker creation;
- no Worker URL rewrite;
- no Chrome native process-memory hook;
- no game RAM writes;
- no `Input.*` gameplay injection;
- no one-key moves / Assist Mode.

Exact authoritative World 921031 SHA-256 remains:

`5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62`

## Discovery behavior

The fix now supports:
- original direct worker target;
- page-related `worker` / `shared_worker` / `service_worker` target types;
- Worker URL shape differences;
- page -> iframe -> Worker recursion;
- parentId/opener relationships when available;
- page discovery even while Worker is not yet surfaced;
- reload/recreated Worker target IDs without stale identity inheritance;
- bounded topology diagnostics for real Chrome follow-up.

Acceptance remains fail-closed:
- multiple exact supported page/Worker pairs are ambiguous and rejected;
- wrong World identity is rejected;
- WASM not ready remains WAITING;
- Blob/Data/JavaScript Worker URLs are rejected;
- direct Worker without unique page association is rejected.

## Offline regression

Fresh discovery-v2 + Windows proof regression: **13/13 PASS**.

Coverage includes:
- direct worker backward compatibility;
- shared-worker / URL variation;
- missing root worker while page is found;
- nested iframe -> Worker;
- multiple page/Worker ambiguity;
- WASM not ready;
- wrong World identity;
- stale/replaced Worker lifecycle;
- disconnect state reset;
- read-only allowlist rejects `Input.dispatchKeyEvent` and `Runtime.callFunctionOn`;
- proof PASS still requires all six checks and ramWrites=0.

## Simplified Chinese owner UX

Updated owner-facing PYLAUNCH surfaces:
- tray status/menu;
- settings and diagnostics;
- launcher CLI help/errors;
- `RUN_WINDOWS_PROOF.cmd`;
- `RUN_WOF_LAUNCHER.bat`;
- proof JSON adds `ownerSummaryZh` and `checksZh` while preserving machine-compatible English keys/schema.

Technical errors are secondary to Chinese human-readable explanations and always state that the game itself is unaffected where appropriate.

## New direct one-click entry

New standalone bootstrap:

`parallel/PYLAUNCH/WOF_ONECLICK_PROOF_CN.cmd`

Owner flow:

```text
直接下载 WOF_ONECLICK_PROOF_CN.cmd
-> 双击
-> 自动下载当前最新仓库快照
-> 自动准备 Launcher
-> 自动打开/连接专用 Chrome/Edge
-> 正常进入 WOF 房间
-> 托盘自动验证 Browser / page / Worker / WASM / World 921031 / READ ONLY
```

No Git, GitHub Desktop, repository-directory knowledge, DevTools, Worker Console, or pasted JavaScript is required.

## Remaining live gate

Repository-side fix is ready. One real Windows run is still required to prove Chrome 151's actual WOF target topology reaches all six checks simultaneously while the room remains playable.

Expected final status:

```text
浏览器：已连接
WOF 页面：已找到
Worker：已找到
WASM / 内存：已找到
游戏版本：World 921031 已确认
只读模式：开启
游戏内存写入：0
```

If it does not reach PASS, return only the generated `WINDOWS_PROOF_STATUS.json`; the new `targetTopology` field should provide the needed read-only real-Chrome topology evidence without DevTools.

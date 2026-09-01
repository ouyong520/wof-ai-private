# WOF-052L Recorder Worker Discovery V2 Sync — Implementation Result

Date: 2026-09-01

## Verdict

**WOF-052L DISCOVERY V2 READY — 可进入 10 房间真人长采集 proof**

本次只修改 `parallel/WOF052L_RECORDER/**`。没有修改 `parallel/PYLAUNCH/**`，没有修改 `product/alpha/**`。

## 已完成

WOF-052L Recorder 已从旧的 browser-level `Target.getTargets -> type=worker + gstyphoon*.js` 假设升级为与最新 PYLAUNCH 一致的 topology discovery 思路：

```text
Browser CDP endpoint
-> page target
-> page session Target.setAutoAttach
-> related iframe / worker target tree
-> read-only WASM / heap preflight
-> exact World 921031 SHA-256
-> existing WOF-052L worker_probe.js
-> capture
```

同时保留 direct Worker 兼容 fallback。

支持：
- direct worker；
- root Worker 缺失但 page-attached Worker 可见；
- page -> iframe -> Worker；
- worker / shared_worker / service_worker；
- Worker URL shape variation；
- reload / Worker replacement 后新 target/session 独立重发现；
- Browser Fleet 每个 CDP endpoint 独立 discovery/client/session。

## Fail-closed 准入

开始 WOF-052L 采集前必须同时满足：
- WASM module 可用；
- heap 可用；
- CPS RAM base 在 heap 内；
- 唯一 page/Worker 关联；
- 精确 `Warriors of Fate (World 921031)`；
- SHA-256：`5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62`。

拒绝/等待：
- 多个通过身份门的 Worker 对同一 page 关联不唯一；
- direct Worker 页面关联不唯一；
- wrong identity；
- WASM/heap 尚未 ready；
- Blob/Data/JavaScript Worker URL。

Live page topology 会周期性重新审计；如果原本唯一的关联后来变成歧义，当前房间立即结束准入/采集，防止跨房间串采。

## 生命周期

- identity cache 只按当前 manager 内的 `targetId` 保存；
- replacement 获得新 `targetId` 后必须重新做 identity preflight；
- page-autoattach session 同时保留 page owner session，维持 child Worker CDP session 生命周期；
- page 关闭/reload、Worker CDP poll 失效、browser disconnect 都只结束对应房间；
- 其他 Fleet endpoint 不受影响。

## 输出兼容

没有改变原 WOF-052L 采集字段、T18/T23 研究语义或基础 schema。

仅新增向后兼容 diagnostics：
- `topologyDiagnostics`
- `target.discoveryPath`

原 `worker_probe.js` 仍负责最终 identity gate 和原采集逻辑。

## Owner 简体中文 UX

默认双击入口：

`RUN_WOF052L_RECORDER.cmd`

现在进入：

`owner_v2_zh_cn.py`

正常 owner 流程无需：
- DevTools；
- Worker Console；
- 手工选 target；
- 粘贴 JavaScript。

新增 discovery 状态/错误均先显示简体中文，技术详情只作为第二层信息。

## Safety

保持：
- `readOnly=true`
- `ramWrites=0`
- `inputInjection=false`
- no Worker replacement/wrap
- no Blob URL rewrite
- no game speed/input control
- no `Input.*`
- no `Runtime.callFunctionOn`

CDP allowlist 只新增 `Target.setAutoAttach` 用于 target topology discovery，不写游戏 RAM、不注入输入。

## Offline regression

Discovery V2 专项回归已通过，覆盖启动提示要求的矩阵：

1. old direct-worker compatibility — PASS
2. root worker missing / page-attached worker — PASS
3. iframe -> Worker — PASS
4. Worker URL shape variation — PASS
5. ambiguity fail closed — PASS
6. wrong World identity — PASS
7. WASM not ready — PASS
8. reload / replacement identity reset — PASS
9. 10 Fleet endpoint isolation — PASS
10. read-only allowlist — PASS

同时保留原 `test_fleet_recorder.py` 的 localhost manifest/isolation约束。

专项测试文件：

`parallel/WOF052L_RECORDER/test_discovery_v2_sync.py`

## Remaining gate

仓库侧没有剩余 discovery blocker。

下一步不是继续修改 Recorder，而是做一次真实 Windows / Chrome 151 / Browser Fleet 的 **10 房间长采集 proof**，确认真实 topology 下：
- 每个 endpoint 自动发现自己的 WOF page/Worker；
- WASM/heap + World 921031 identity 全部通过；
- 10 房间不会串采；
- reload/replacement 只重启对应房间采集；
- checkpoint/merged JSON 持续生成；
- `ramWrites=0`。

**WOF-052L DISCOVERY V2 READY — 可进入 10 房间真人长采集 proof**

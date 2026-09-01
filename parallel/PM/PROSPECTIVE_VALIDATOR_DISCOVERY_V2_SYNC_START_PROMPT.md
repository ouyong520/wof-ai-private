# WOF Prospective Validator — Worker Discovery V2 Sync Fresh Start Prompt

你负责 Prospective Validator 的独立 Worker Discovery V2 兼容修复线。

仓库：`ouyong520/wof-ai-private`

## 背景

真人 Windows 已证明旧的 browser-level `Target.getTargets` + `type=worker/shared_worker` + `gstyphoon*.js URL` 硬过滤可能漏掉真实 WOF Worker surface。

当前已经完成：
- `parallel/PYLAUNCH/**` Discovery V2；
- `parallel/BROWSER_FLEET/**` Discovery V2；
- `parallel/WOF052L_RECORDER/**` Discovery V2；
- `parallel/PROSPECTIVE_VALIDATOR/**` framework repository-side READY。

但是 Prospective Validator 的 live path 仍需要重新审计，不能假设它已经自动继承上述修复。

## 开始前读取

- `parallel/WORKER_SURFACE/**`
- `parallel/PYLAUNCH/wof_launcher/discovery_v2.py`（只读参考）
- `parallel/BROWSER_FLEET/fleet_discovery_v2.py`（若存在，只读参考）
- `parallel/WOF052L_RECORDER/discovery_v2_sync.py`（只读参考）
- `parallel/PROSPECTIVE_VALIDATOR/**`
- `parallel/PM/CHINESE_UI_UX_REQUIREMENT.md`

## 写入范围

仅：`parallel/PROSPECTIVE_VALIDATOR/**`

禁止修改：
- `parallel/PYLAUNCH/**`
- `parallel/BROWSER_FLEET/**`
- `parallel/WOF052L_RECORDER/**`
- `product/alpha/**`

## 目标

让 Prospective Validator 的真人 Browser live path 不再依赖旧 direct Worker URL/type 假设。

必须支持：
- direct Worker backward compatibility；
- page-session `Target.setAutoAttach`；
- page -> iframe -> Worker related topology；
- Worker URL shape 变化；
- Worker/shared_worker/service_worker 等真实相关 surface 的安全枚举；
- reload / recreated Worker；
- 多房间严格 endpoint/session 隔离；
- wrong/missing/ambiguous Worker fail-closed；
- WASM/heap readiness；
- exact World 921031 SHA-256 gate；
- prospective session freeze / candidate manifest hash 边界保持；
- discovery evidence 不能污染 prospective evidence；
- 一个房间失败不影响其他房间；
- owner-facing 简体中文。

## 安全

固定：
- `readOnly=true`
- `ramWrites=0`
- `inputInjection=false`
- no `window.Worker` replacement/wrap
- no Blob/Data/ObjectURL Worker rewrite
- no game RAM writes
- no gameplay input injection
- no production rule auto-promotion

## Regression

至少覆盖：
1. direct worker；
2. related-target-only；
3. iframe -> worker；
4. URL mismatch but valid related runtime；
5. WASM not ready；
6. wrong World identity；
7. ambiguous Workers；
8. Worker replacement/reload；
9. two/ten room endpoint isolation；
10. frozen manifest mutation rejection；
11. pre-freeze discovery corpus 不得变 prospective；
12. read-only allowlist 不包含 gameplay Input methods。

## Stop condition

直到：

**PROSPECTIVE VALIDATOR DISCOVERY V2 READY**

并给出 repository-side regression PASS；真人 Browser 只保留一个与未来真实 prospective session 合并执行的 bounded proof，不单独浪费 owner 操作。
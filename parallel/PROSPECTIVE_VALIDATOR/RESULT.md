# WOF Prospective Validator — Result

更新时间：2026-09-01

## Verdict

**PROSPECTIVE VALIDATOR DISCOVERY V2 READY**

Prospective Validator 的真人 Browser owner path 已从旧的 `Target.getTargets -> type=worker -> gstyphoon*.js URL` 硬过滤切换到独立 Discovery V2。原 prospective manifest / freeze / evidence / verdict 引擎保持不变。

owner 仍使用：

`RUN_PROSPECTIVE_VALIDATOR.cmd candidate.json`

该入口现在执行 `live_validator_v2.py`。

## Discovery V2 delivered

- `discovery_v2.py`
  - direct Worker backward compatibility；
  - page-session `Target.setAutoAttach`；
  - page -> iframe -> Worker / shared_worker / service_worker related topology；
  - Worker URL 不再是身份 gate，允许 hashed / changed / blob 等 URL shape；
  - WASM/module/heap readiness gate；
  - exact World 921031 SHA-256 gate：`5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62`；
  - wrong / missing / ambiguous Worker fail-closed；
  - direct Worker page association 优先 parent/opener，再用唯一 browserContext，再用单 page fallback；
  - related ancestry session ownership，避免 iframe -> Worker session 生命周期被误拆；
  - discovery diagnostics 固定 `evidenceClass=discovery-only`；
  - CDP event receiver 仅增加 `Target.setAutoAttach`，没有 gameplay `Input.*`。

- `live_validator_v2.py`
  - 每个 Browser Fleet / localhost endpoint 独立 discovery、session、room map；
  - 2 / 10 room targetId 即使相同也不会跨 endpoint 合并；
  - direct Worker 消失 -> 结束该 room；
  - related Worker path 以 page 生命周期 + Worker session drain 健康度处理 reload/recreated Worker；
  - 周期性 live topology audit，若同一 page 出现多个通过身份 gate 的 Worker，立即 fail-closed；
  - 单房间 discovery / attach / CDP 失败不影响其他 endpoint / room；
  - prospective probe 启动前再次 `validate_session()`；
  - 写 corpus 前再次校验 frozen candidate manifest SHA-256；
  - discovery diagnostics 只保存在内存 endpoint diagnostics，不写入 prospective corpus；
  - owner-facing 正常状态 / 错误 / PASS path 使用简体中文。

- `RUN_PROSPECTIVE_VALIDATOR.cmd`
  - 原一键入口保持；
  - 现在明确显示 Discovery V2；
  - 默认 UTF-8 / 简体中文；
  - 调用 `live_validator_v2.py`。

## Regression

新增 `test_discovery_v2.py`，离线执行结果：**12/12 PASS**。

覆盖：

1. direct worker backward compatibility — PASS；
2. related-target-only — PASS；
3. iframe -> worker — PASS；
4. URL mismatch but valid related runtime — PASS；
5. WASM not ready fail-closed — PASS；
6. wrong World identity fail-closed — PASS；
7. ambiguous Workers fail-closed — PASS；
8. Worker replacement / reload liveness — PASS；
9. two / ten endpoint isolation — PASS；
10. discovery evidence explicitly non-prospective — PASS；
11. read-only allowlist excludes gameplay Input / `Runtime.callFunctionOn` — PASS；
12. Worker URL shape is not identity gate — PASS。

既有 `test_validator.py` 的 repository-side framework regression 保留不变，其中已经覆盖启动提示要求的两个关键边界：

- frozen manifest mutation rejection；
- pre-freeze discovery corpus 不得变 prospective。

因此 Discovery V2 改动没有修改 candidate hashing、session freeze、prospective evidence classification 或 production promotion policy。

推荐仓库回归命令：

`cd parallel/PROSPECTIVE_VALIDATOR && python -m unittest -v test_validator.py test_discovery_v2.py`

## Safety

固定不变：

- `readOnly=true`；
- `ramWrites=0`；
- `inputInjection=false`；
- no `window.Worker` replacement / wrap；
- no Blob/Data/ObjectURL Worker rewrite；
- no game RAM writes；
- no gameplay input injection；
- no production rule auto-promotion。

本线写入仅发生在：

`parallel/PROSPECTIVE_VALIDATOR/**`

没有修改：

- `parallel/PYLAUNCH/**`；
- `parallel/BROWSER_FLEET/**`；
- `parallel/WOF052L_RECORDER/**`；
- `product/alpha/**`。

## Remaining real-browser proof

不再单独要求 owner 为 discovery 做一次额外真人操作。

唯一保留的真人 Browser proof 是：未来第一次真实 prospective candidate session 正常运行时，同时确认一次 Discovery V2 的 page / iframe / Worker admission、World 921031 identity、read-only safety 与 prospective trace 输出。该 proof 与真实 prospective session 合并执行，不额外浪费 owner 操作。

## Stop condition

**PROSPECTIVE VALIDATOR DISCOVERY V2 READY**

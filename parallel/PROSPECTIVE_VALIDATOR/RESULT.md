# WOF Prospective Validator — Result

更新时间：2026-09-01

## Verdict

**PROSPECTIVE VALIDATOR DISCOVERY V2 HARDENING READY — P0/P1 CLOSED IN REPOSITORY**

本阶段在既有 Discovery V2 基础上关闭 cross-page shared Worker 证据归属 P0，以及 endpoint/direct-fallback/manifest gate P1。Owner 不需要额外真人 Browser 操作。

## P0 — endpoint-level Worker↔page relation uniqueness

新增 `discovery_v2_hardening.py`，在原 Discovery V2 exact supported candidate 扫描之后建立 endpoint-level Worker↔page relation graph：

- 同一个 Worker `targetId` 若关联到超过一个 page，所有这些 relation 全部 fail closed；
- 不再按 page scan order 选择 evidence owner；
- 诊断为 `cross-page-worker-association-ambiguous`；
- 诊断固定 `evidenceClass=discovery-only`；
- `ambiguous_page_ids()` 同时覆盖原单页多 Worker 歧义和跨页共享 Worker 歧义。

`live_validator_v2_hardened.py` 在加载 V2 live path 时安装该 hardening。既有 `live_validator_v2.py::discover_and_poll()` 会在每次 topology audit 中先检查 ambiguity，再 finalize 相关 live room，之后才 drain remaining rooms。因此一旦发现 live room 变成 cross-page ambiguous，该 room 会先 censor/finalize，不再继续接收 prospective evidence。

两页/两个不同 exact supported Worker 不受影响，仍独立准入。

## P1 — endpoint confinement

Hardened endpoint connect 现在要求：

- assigned host 必须是 loopback；
- `/json/version` / probe 返回 websocket host 也必须是 loopback；
- 返回 websocket port 必须与请求 endpoint port 完全一致；
- localhost / 127.0.0.1 / ::1 作为 loopback alias 兼容；
- remote host 或 cross-port websocket fail closed。

不会 silent fallover 到另一 Browser Fleet room/port。

## P1 — direct Worker association

Direct compatibility fallback 不再使用 Worker `openerId` 作为 parent authority。

优先级现在是：

1. `parentId` -> exact page target；
2. `parentFrameId` -> 可唯一映射 page/frame；
3. 否则仅 endpoint 上唯一可识别 WOF page 才允许兼容 direct Worker；
4. 其余情况 fail closed。

existing blob/data/hashed/no-extension Worker 的 URL-hint 语义保持不变：Worker URL shape 仍不是身份 gate，最终仍由 runtime readiness + exact World 921031 SHA-256 决定。

## P1 — conservative manifest gates

`validator.py` 的最终 verdict 现在执行全部当前受支持 conservative gates：

- `minProspectiveSignals`
- `minProspectiveRooms`
- `requireZeroHardMiss`
- `minDistinctTargets`
- `minObservedTypes`
- `requireLifecycleReset`

result JSON 对每个 gate 均输出：

- `required`
- `observed`
- `passed`

未知 conservative gate 不再静默忽略；`validate_manifest()` 直接 fail closed，返回明确 unsupported gate 错误。

`minDistinctTargets` 从 prospective matched evidence 的 target identity 统计；`minObservedTypes` 从 matched enemy type 统计；`requireLifecycleReset` 只在 prospective matched evidence 明确携带 `lifecycleReset=true` 时满足。

PASS 仍固定为 `PROSPECTIVE_PASS_RESEARCH_ONLY`，`productionPromotionAllowed=false`。

## Freeze / evidence / safety invariants

保持：

- candidate canonical freeze/hash；
- manifest mutation after freeze reject；
- pre-freeze discovery exclusion；
- post-freeze prospective inclusion；
- discovery diagnostics 不进入 prospective corpus；
- research-only；
- no production auto-promotion；
- `readOnly=true`；
- `ramWrites=0`；
- `inputInjection=false`；
- no `window.Worker` replacement；
- no Blob/Data/ObjectURL Worker rewrite。

## Owner entrypoints

- `RUN_PROSPECTIVE_VALIDATOR.cmd` -> `live_validator_v2_hardened.py`
- direct `python live_validator.py ...` -> hardened V2
- hardened wrapper installs relation-graph, direct-fallback, and endpoint confinement guards before V2 main starts。

## Regression

Repository regression surface now totals **40 test cases**:

- existing `test_validator.py`: 12 cases；
- existing `test_discovery_v2.py`: 12 cases；
- existing `test_entrypoint_v2.py`: 4 cases；
- new `test_discovery_v2_hardening.py`: 5 cases；
- new `test_validator_hardening.py`: 7 cases。

New hardening coverage includes：

1. shared Worker under two pages => no admission；
2. two pages / two distinct exact Workers => independent admission；
3. misleading openerId cannot become parent authority；
4. real parentId remains authoritative；
5. remote/cross-port websocket reject + normalized loopback accept；
6. all declared conservative gates satisfied => research-only PASS；
7. target shortfall => insufficient；
8. observed type shortfall => insufficient；
9. lifecycle reset shortfall => insufficient；
10. zero-hard-miss remains enforced；
11. unknown conservative gate => fail closed；
12. discovery rows never satisfy new prospective gates。

Local repository-equivalent smoke checks executed during this stage passed for：

- validator syntax/targeted conservative-gate behavior；
- legacy ordered-tail/current-level verdict behavior；
- freeze hash mutation rejection；
- relation graph shared-Worker rejection；
- endpoint same-port/loopback checks；
- direct fallback openerId non-authority。

Existing Discovery V2 blob/data/hashed/no-extension URL semantics were not removed or weakened。

## Write scope

本阶段只写：

`parallel/PROSPECTIVE_VALIDATOR/**`

以及 mandatory PM stage claim state。

没有修改 Recorder、PYLAUNCH、Browser Fleet、Beta manifests 或 `product/alpha/**`。

## Stop condition

**PROSPECTIVE VALIDATOR DISCOVERY V2 HARDENING READY — P0/P1 CLOSED IN REPOSITORY**

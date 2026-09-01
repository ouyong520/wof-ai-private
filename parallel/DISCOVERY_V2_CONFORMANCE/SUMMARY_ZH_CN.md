# Discovery V2 Cross-Component Conformance — 中文摘要

更新时间：2026-09-01

## Harness 结论

**DISCOVERY V2 CONFORMANCE HARNESS READY**

Harness 已能用 fixture/mock/synthetic CDP topology 对四个当前组件角色生成统一 machine-readable matrix，不要求 Owner 真人 Browser，也不会为了绿色结果吞掉 FAIL。

当前基线测试/审计 HEAD：

`250ccae3be8430fd84875093fef700819d82cf6c`

规范重跑入口：

`python parallel/DISCOVERY_V2_CONFORMANCE/run_current_head.py`

输出：

- `parallel/DISCOVERY_V2_CONFORMANCE/RESULT.json`
- `parallel/DISCOVERY_V2_CONFORMANCE/SUMMARY_ZH_CN.md`

## 当前矩阵汇总

- `PASS`: **71**
- `EXPECTED_ROLE_DIFFERENCE`: **8**
- `FAIL`: **1**
- Safety invariants: **4 / 4 PASS**

`EXPECTED_ROLE_DIFFERENCE` 不等于失败，也不会被伪装成普通 PASS：

- Browser Fleet 只提供 `cheap-indicator-only`，不承担 exact World 921031 SHA-256 authority；
- PYLAUNCH 是单选择 authoritative proof，多个 exact pair 会 fail closed；
- Recorder / Prospective 可以保留独立 page/room 候选，但同一个 exact Worker 跨 page 关联必须全局 fail closed；
- Prospective 的 discovery diagnostics 仍是 `discovery-only`，不能自动变成 prospective/production authority。

## 当前真实 drift — 1 个 P1

### PYLAUNCH / direct Worker fallback — FAIL

Blocker：

`P1-DIRECT-PARENTFRAMEID-AUTHORITY-NOT-REACHABLE`

独立 adversarial fixture 已证明：

- endpoint 有两个都已确认的 WOF page；
- exact World 921031 direct Worker 的 `parentFrameId` 唯一指向 page B；
- fake CDP 提供 `Page.getFrameTree`，足以建立唯一 frame -> page 关系；
- 当前 PYLAUNCH discovery 没有读取该 frame mapping；
- 因而仍返回 direct-worker-page-ambiguous，而不是选择 page B。

所以 Harness 在 `direct-worker-fallback` 的 PYLAUNCH cell 明确输出 `FAIL`。

这个 blocker **不需要 Owner 操作**。修复范围属于未来新的 `parallel/PYLAUNCH/**` fix stage；本 Harness stage 不越界修改 PYLAUNCH。

## 其他组件当前证据

### Browser Fleet

- repository Discovery V2 regression：**15 / 15 PASS**；
- 每个 Fleet endpoint 独立；
- cross-port websocket fail closed；
- stale endpoint 只清本房间；
- Worker 状态明确是 advisory cheap indicator，不冒充 exact identity authority。

### WOF-052L Recorder

最新 hardening 结果：**READY**。

- hardening regression：**21 / 21 PASS**；
- 两页面 / 同一 shared exact Worker -> admit none；
- mid-capture ambiguity 只 finalize 受影响房间；
- remote/cross-port fail closed；
- blob/data/hashed/no-extension existing Worker 进入 runtime + exact identity gate；
- misleading `openerId` 不再是 parent authority；
- `RUN_WOF052L_RECORDER.cmd -> owner_zh_cn.py` 当前公开入口会安装 `discovery_v2_sync` + `hardening_v2`；
- Windows `Owner Tools Chinese UX` run `33516087731`：**SUCCESS**。

### Prospective Validator

- Discovery V2 hardening：P0/P1 repository-side 已关闭；
- regression surface：**40 test cases**；
- cross-page shared Worker relation graph fail closed；
- endpoint confinement / direct fallback / conservative research-only gates 已覆盖；
- production auto-promotion 仍禁止。

## 统一安全不变量

四组件当前均保持：

```json
{
  "readOnly": true,
  "ramWrites": 0,
  "inputInjection": false,
  "workerReplacementOrWrap": false,
  "blobDataObjectUrlCreationOrRewrite": false,
  "productionAutoPromotion": false
}
```

观察已经存在的 `blob:` / `data:` Worker 不算创建或改写 Worker；Harness 禁止的是创建、替换、包装、Blob/ObjectURL rewrite、RAM 写入和 gameplay input injection。

## Owner intervention

`你现在需要操作：NO`

当前唯一 Discovery V2 conformance FAIL 是 repository-side PYLAUNCH P1，不需要真人 Browser 才能定位或复现。

## Stop condition

**DISCOVERY V2 CONFORMANCE HARNESS READY**

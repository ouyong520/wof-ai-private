# WOF Prospective Validator Discovery V2 Hardening — Fresh Stage

stageId: `PROSPECTIVE_VALIDATOR_DISCOVERY_V2_HARDENING_V1`

## 启动去重守卫（必须最先执行）

先读取 `parallel/PM/STAGE_DEDUP_GUARD.md`、GitHub 默认分支最新状态和本 stage 等价结果。

- stop condition 已满足：`ALREADY COMPLETE — SAFE TO CLOSE — 当前线程空闲`，停止。
- `parallel/PM/STAGE_CLAIMS/PROSPECTIVE_VALIDATOR_DISCOVERY_V2_HARDENING_V1.json` 已存在：`ALREADY CLAIMED — SAFE TO CLOSE — 当前线程空闲`，停止。
- 否则原子 create-file claim；失败则按已认领处理并停止。
- claim 成功后才工作；完成更新 COMPLETE，精确 blocker 更新 BLOCKED。
- 不得因重复任务自行扩 scope。

## 背景

读取最新：
- `parallel/DISCOVERY_V2_AUDIT/RESULT.md`
- `parallel/PM/BETA_MANIFEST_SET_QA_RESULT.md`
- `parallel/PROSPECTIVE_VALIDATOR/**`
- `parallel/BETA_MANIFESTS/**`

当前必须一次关闭同一写入域内的两组问题：

### P0 Discovery admission
Recorder/Prospective 在“两个 page 关联同一个 exact supported shared Worker”时可能按 scan order 选一个 page，未做 endpoint-level relation uniqueness，属于证据归属 P0。

### P1 Prospective gate enforcement
READY manifests 已声明 `minDistinctTargets`、`minObservedTypes`、`requireLifecycleReset`，但 Validator 最终 verdict 目前只执行 signals/rooms/zero-hard-miss，可能过早给 `PROSPECTIVE_PASS_RESEARCH_ONLY`。

另有 P1 drift：
- returned websocket endpoint confinement；
- direct fallback 不得把 Worker openerId 当 parent authority。

Prospective V2 对 existing blob/data/hashed Worker 的 URL-hint语义已经正确，必须保留，不要回退。

## 写入范围

只允许：
- `parallel/PROSPECTIVE_VALIDATOR/**`

不要修改 Recorder、PYLAUNCH、Fleet、Beta manifests、Alpha。

## 必须完成

1. 建 endpoint-level Worker<->page relation graph；同一 Worker target 关联 >1 page 时，这些 relation 全部 fail closed，不得 scan-order 选主。
2. live prospective room 若后来变成 cross-page ambiguous，先 censor/finalize，之后不得继续收 prospective evidence。
3. ambiguity diagnostic 只能是 discovery-only，不能进入 prospective corpus。
4. endpoint 必须 loopback 且 returned websocket 同 endpoint host/port；cross-port fail closed。
5. direct fallback 不使用 Worker openerId 作为 parent authority；优先 page-rooted topology / parentId / parentFrameId；否则仅唯一 WOF page 才可兼容 direct Worker。
6. Validator verdict 必须真正执行 manifest 中声明且受支持的全部 conservative gates；至少：
   - minProspectiveSignals
   - minProspectiveRooms
   - requireZeroHardMiss
   - minDistinctTargets
   - minObservedTypes
   - requireLifecycleReset
7. result JSON 对每个 gate 明确输出 required / observed / passed；未知 gate 不得静默忽略，必须 fail closed 或明确 unsupported。
8. 保持 candidate freeze/hash、pre-freeze discovery exclusion、post-freeze prospective inclusion、research-only、no production auto-promotion。
9. 保持 existing blob/data/hashed/no-extension Worker 的 read-only Discovery V2 支持。
10. readOnly=true / ramWrites=0 / inputInjection=false / no Worker replacement。

## 回归

至少：
- shared Worker under two pages => no admission；
- two pages / two distinct exact Workers => independent admission；
- ambiguity appears mid-session => censor/finalize before more evidence；
- remote/cross-port websocket reject；
- misleading openerId no misassociation；
- signals/rooms满足但 target不足 => INSufficient；
- observed type不足 => insufficient；
- lifecycle reset未满足 => insufficient；
- all gates satisfied => research-only PASS；
- unknown conservative gate => fail closed；
- freeze mutation / discovery evidence isolation regressions继续 PASS；
- blob/data exact supported runtime continue PASS。

不要要求 owner 真人 Browser。

## Stop condition

`PROSPECTIVE VALIDATOR DISCOVERY V2 HARDENING READY — P0/P1 CLOSED IN REPOSITORY`

把结果写回 Validator lane，并列出完整回归数量。
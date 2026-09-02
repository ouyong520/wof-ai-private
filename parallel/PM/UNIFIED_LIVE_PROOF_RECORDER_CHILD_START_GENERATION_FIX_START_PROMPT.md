# Unified Live Proof Recorder Child-Start Generation Fix — Start Prompt

stageId: `UNIFIED_LIVE_PROOF_RECORDER_CHILD_START_GENERATION_FIX_V1`

你负责修复 Unified Live Proof 当前最新 fresh QA 暴露的 Recorder generation P1：新 Recorder child 已启动后、reader 尚未绑定新 generation 的窗口里，旧 generation 仍可接受延迟 heartbeat 并续期 authority。

这是一个窄范围 implementation fix。不要做独立 QA 自验收，不要扩大到 PYLAUNCH、Alpha Transport、Owner OneClick、WOF-052/052L 长采集或 Browser/WOF 真人运行。

## 开始前

必须重新读取 `main` 当前最新 HEAD，并直接检查：

- `parallel/PM/PM_CORE_OPERATING_CHARTER.md`
- `parallel/PM/STAGE_DEDUP_GUARD.md`
- `parallel/PM/STAGE_CLAIMS/**`
- `parallel/LIVE_PROOF_BUNDLE_QA_RECORDER_GENERATION/RESULT.md`
- `parallel/LIVE_PROOF_BUNDLE_QA_RECORDER_GENERATION/RESULT.json`
- `parallel/LIVE_PROOF_BUNDLE/RECORDER_AUTHORITY_GENERATION_FIX_RESULT.md`
- 当前 `parallel/LIVE_PROOF_BUNDLE/unified_live_proof.py`
- 与 Recorder child start / reader / generation / heartbeat authority 有关的近期 commits 和测试

先做等价任务去重。若已有等价 COMPLETE 结果，立即 `ALREADY COMPLETE — SAFE TO CLOSE`；若等价 stage 已 CLAIMED/EXECUTING，立即 `ALREADY CLAIMED — SAFE TO CLOSE`。

确认仍需执行后，原子创建：

`parallel/PM/STAGE_CLAIMS/UNIFIED_LIVE_PROOF_RECORDER_CHILD_START_GENERATION_FIX_V1.json`

获得 claim 后再修改实现。

## 要解决的问题

Fresh QA 已证明：generation 2 child 已 start/allocate 后，在 generation-2 reader 进入 `begin_source_generation(...)` 之前，`RecorderEvidence` 仍把 generation 1 当作 active source；这时延迟到达的 generation-1 trusted heartbeat 仍能续期 authority。

修复后的语义必须是：**新的 Recorder child generation 一旦进入 authoritative child-start 边界，旧 generation authority 立即失效；不能等 reader 后续开始消费 stdout 才 revoke。**

重点保证：

- child-start generation rollover 与 authority revoke/bind 在同一可靠边界完成；
- generation N+1 启动后，generation N 的 heartbeat/admission/stdout 永远不能重新获得或续期 authority；
- 新 generation 在自己的有效 evidence 到达前继续 fail-closed，不因为提前切 generation 而制造假 healthy；
- child/restart 失败时不能偷偷恢复旧 generation authority；
- 保持 monotonic generation/order、已有 freshness/fail-closed/read-only 语义和当前 Unified preflight contract；
- 不通过放宽 validator、忽略 stale evidence 或关闭 generation 检查来“修测试”。

实现方式由你基于当前代码决定，优先最小、清晰、可证明的 orchestration change。

## 实现侧验证

允许在 implementation lane 增加/更新针对本修复的回归测试，至少覆盖真实 orchestration 窗口：

1. generation 1 healthy；
2. generation 2 child start；
3. generation-2 reader 尚未开始；
4. generation-1 延迟 trusted heartbeat 到达；
5. 必须被拒绝且不能续期 authority。

同时跑与本改动直接相关的现有 Recorder generation / heartbeat / Unified regression。实现线程只能证明“实现侧回归已绿”，不能把自己标成 independent QA PASS。

## 写入边界

只允许修改本修复确实需要的：

- `parallel/LIVE_PROOF_BUNDLE/**`
- `parallel/LIVE_PROOF_BUNDLE_RECORDER_CHILD_START_GENERATION_FIX/**`
- 本 stage claim

不要修改 `parallel/LIVE_PROOF_BUNDLE_QA_RECORDER_GENERATION/**` 的 fresh independent QA 证据。

完成后写 durable result，明确：

- 修复前精确 failure boundary；
- 改动后的 generation-start authority 语义；
- 修改文件/blob/commit；
- 实现侧测试结果；
- `Owner action: NO`；
- 状态只能是 `READY FOR FRESH INDEPENDENT QA`，不能自称 release gate PASS。

## 停止条件

满足以下任一即停止：

- `COMPLETE — RECORDER CHILD-START GENERATION FIX — READY FOR FRESH INDEPENDENT QA`
- `BLOCKED — <精确 repository-side blocker>`
- `ALREADY COMPLETE — SAFE TO CLOSE`
- `ALREADY CLAIMED — SAFE TO CLOSE`

严格持续执行直到上述停止条件之一。
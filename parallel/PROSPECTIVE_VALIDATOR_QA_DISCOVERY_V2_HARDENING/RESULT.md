# WOF Prospective Validator Discovery V2 Hardening — Fresh Independent QA Result

stageId: `PROSPECTIVE_VALIDATOR_DISCOVERY_V2_HARDENING_QA_V1`

## Verdict

**BLOCKED — PROSPECTIVE VALIDATOR HARDENING QA — P0 live topology ambiguity audit gap permits post-ambiguity prospective evidence**

Owner 真人 Browser：**不需要**。

## Exact P0

实现已经正确补上 endpoint-level shared-Worker relation graph：如果同一次完整扫描里同时看到 `page-a -> worker-shared` 与 `page-b -> worker-shared`，两条 relation 都会 fail closed。

但 live orchestration 仍存在一个时序窗口：

- `parallel/PROSPECTIVE_VALIDATOR/live_validator_v2.py` 定义 `AUDIT_LIVE_TOPOLOGY_INTERVAL = 10.0`；
- 非 full-audit 轮次把现有 live page 放进 `skip_page_ids=live_page_ids`；
- 因此 live room 原本唯一、随后第二个 page 关联到同一个 Worker 时，非 full-audit 扫描无法同时重建两条 relation；
- ambiguity 只有在后续 full audit 才能进入 `ambiguous_page_ids(diag)` 并触发 `finalize_room(...)`；
- 但是 discovery block 之后，所有尚存 room 会继续执行 `__WOF_PROSPECTIVE_VALIDATOR.drain()`，随后 `ingest(...)`。

结果：**从 topology 真正变成 ambiguous 的时刻，到下一次 10 秒 full audit 之间，旧 room 仍可能继续摄入 prospective evidence。**

这违反本 QA requirement 11：

> live topology 从唯一关系变歧义时，现有 room 必须先 censor/finalize，不能继续 prospective evidence。

并且这是 P0，而不仅是诊断延迟：这段 post-ambiguity evidence 仍可进入 prospective counters，从而参与 `minProspectiveSignals`、`minProspectiveRooms`、`minDistinctTargets`、`minObservedTypes`、`requireLifecycleReset` 等 gate，存在错误 research PASS 的可能。

## Independent adversarial fixture

新增：

- `fixtures/live_unique_to_shared_worker.json`
- `test_live_topology_transition.py`

fixture 固定重现：

1. `t=100`：`page-a -> worker-shared` 已合法连接，刚完成一次 full audit；
2. `t=101`：出现 `page-b -> worker-shared`，ownership 已经变成 ambiguous；
3. `t=105`：仍在 10 秒 audit gap 内，live `page-a` 被 skip；完整 relation graph 无法看到两条 page relation；
4. room 未 finalize；随后 `drain()` 仍执行，构成 forbidden post-ambiguity prospective ingest；
5. 直到 `t>=110` full audit 才能发现 shared-Worker ambiguity 并在该轮 drain 前 finalize。

独立 QA 线程还用提取后的实际控制流做了最小行为复现：`t=105` => `audit_live=false / skip page-a / finalized=false / drains=1`；`t=110` => `audit_live=true / finalized=true / drains=0`。

## Checks independently re-read before stop

在命中 P0 stop condition 前，已重新读取/核对：

- hardening relation graph：同一扫描内 shared Worker 双 page 会全部 reject；
- two pages / two distinct Workers 保持独立；
- `openerId` 不再作为 parent authority；
- `parentId` 优先，`parentFrameId` 唯一映射 fallback；
- endpoint assigned host / websocket host 必须 loopback，websocket port 必须 exact same port；
- wrong World SHA 与 admission safety mismatch fail closed；
- discovery-only evidence 不进入 prospective counters；
- 六个 conservative gates 都在 validator verdict 中真实执行，unknown gate name fail closed；
- PASS 固定 `PROSPECTIVE_PASS_RESEARCH_ONLY`，`productionPromotionAllowed=false`；
- admission 仍检查 `readOnly=true / ramWrites=0 / inputInjection=false / windowWorkerReplacement=false`。

由于已经命中精确 P0，本 fresh independent QA 按 prompt stop condition 停止；剩余完整 PASS matrix 必须在 fresh fix 完成后由 **新的 fresh QA stage** 重新覆盖，不能在本 QA 线程修实现。

## Required fix property

修复线程必须保证：

**任何一次 prospective `drain()/ingest()` 之前，都已经用当前 topology 重新证明该 live room 的 Worker↔page ownership 仍唯一。只要已经变歧义，必须先 censor/finalize，不能存在正长度 audit gap。**

允许优化扫描成本，但不能以继续接收 prospective evidence 为代价。

## Write scope

本 QA 只写：

- `parallel/PROSPECTIVE_VALIDATOR_QA_DISCOVERY_V2_HARDENING/**`
- mandatory PM stage claim

没有修改：

- `parallel/PROSPECTIVE_VALIDATOR/**`
- Recorder / PYLAUNCH / Fleet / Alpha / LIVE_PROOF_BUNDLE

## Stop condition

**BLOCKED — PROSPECTIVE VALIDATOR HARDENING QA — P0 live topology ambiguity audit gap permits post-ambiguity prospective evidence**

# Alpha Formal Real-Adapter Integration Fresh QA Recovery V2 — Start Prompt

stageId: `ALPHA_TRANSPORT_FORMAL_REAL_ADAPTER_INTEGRATION_FRESH_QA_RECOVERY_V2`

你负责接管 **Alpha Formal Real-Adapter Integration 的 fresh independent QA**。

原 `ALPHA_TRANSPORT_FORMAL_REAL_ADAPTER_INTEGRATION_FRESH_QA_V1` 在仓库里留下了 `ACTIVE` claim，但控制 PM 已确认原执行线程当前不再实际运行；目前没有对应 durable QA result。这个 stage 是对“遗留 ACTIVE claim / 无 durable result”的恢复，不是重复执行同一个 stage，也不要修改旧 claim 来伪造完成历史。

## 开始前

必须重新读取当前 `main` 最新 HEAD，并直接检查：

- `parallel/PM/PM_CORE_OPERATING_CHARTER.md`
- `parallel/PM/STAGE_DEDUP_GUARD.md`
- `parallel/PM/STAGE_CLAIMS/ALPHA_TRANSPORT_FORMAL_REAL_ADAPTER_INTEGRATION_FRESH_QA_V1.json`
- `parallel/PM/ALPHA_TRANSPORT_FORMAL_REAL_ADAPTER_INTEGRATION_FRESH_QA_START_PROMPT.md`
- `parallel/PM/STAGE_CLAIMS/ALPHA_TRANSPORT_FORMAL_REAL_ADAPTER_INTEGRATION_RECOVERY_V2.json`
- `parallel/ALPHA_TRANSPORT_FORMAL_INTEGRATION/RESULT.md`
- Recovery V2 相关 RESULT / STATUS / commits
- detector-local identity / same-targetId replacement regression fixture
- 当前 Alpha Transport / real adapter / real worker 相关 blobs 和最近 commits

先检查原 V1 在你启动前是否已经出现新的 durable PASS/BLOCKED result 或完成 claim：

- 如果 V1 已经有等价 durable COMPLETE/PASS/BLOCKED 结果，立即停止并返回 `ALREADY RESOLVED BY V1 — SAFE TO CLOSE`；
- 如果本 recovery V2 已经 CLAIMED/EXECUTING/COMPLETE，按 duplicate guard 停止；
- 如果 V1 仍只有遗留 ACTIVE claim、没有 durable result，则允许继续本 recovery V2，不把旧 ACTIVE claim 当作正在执行的有效 worker。

确认需要恢复后，创建新的原子 claim：

`parallel/PM/STAGE_CLAIMS/ALPHA_TRANSPORT_FORMAL_REAL_ADAPTER_INTEGRATION_FRESH_QA_RECOVERY_V2.json`

## QA 目标

这是 fresh independent QA，不是 implementation fix。

独立验证 Recovery V2 在当前 HEAD 上是否真正关闭旧 Formal Integration adversarial blocker，重点至少覆盖：

1. detector-local exact World identity / SHA-256 authority 在 observer/install 边界是当前且 fail-closed；
2. same-targetId runtime replacement 不能继续使用旧 Discovery / identity authority；
3. replacement / reload / stale runtime 期间 warning/transport 不得假 healthy；
4. real adapter 与 current worker 的 identity / lifecycle / generation 契约一致；
5. Recovery V2 声称的回归 fixture 必须对当前 blobs 仍有效，而不是只证明历史 snapshot；
6. 旧 adversarial BLOCKED verdict 是否已被当前 successor implementation + fresh QA 真正 supersede；
7. 保持 read-only、RAM writes=0、input injection disabled、fail-open gameplay / fail-closed warnings；
8. 不需要 Owner Browser/WOF 真人运行即可完成 repository-side QA。

必须使用独立 QA fixture/runner 或独立 adversarial inspection，不得只引用 implementation thread 自己的测试结果。

## 写入边界

只允许写：

- `parallel/ALPHA_TRANSPORT_FORMAL_INTEGRATION_QA_RECOVERY_V2/**`
- 本 recovery stage claim

不要修改 Alpha Transport / real adapter / worker implementation，不要顺手修 bug。

如果发现 blocker，只记录精确证据并停止，后续另开 fresh fix stage。

## 结果要求

结果必须记录：

- audited current HEAD；
- tested production blobs；
- 独立 adversarial vectors / runner 结果；
- old BLOCKED 是否 superseded；
- 是否解锁 True 5h endurance / current-head release gates；
- `Owner action: NO`。

## 停止条件

- `PASS — ALPHA FORMAL REAL-ADAPTER FRESH QA RECOVERY V2 — READY FOR NEXT RELEASE GATES`
- `BLOCKED — ALPHA FORMAL REAL-ADAPTER FRESH QA RECOVERY V2 — <precise blocker>`
- `ALREADY RESOLVED BY V1 — SAFE TO CLOSE`
- `ALREADY CLAIMED — SAFE TO CLOSE`
- `ALREADY COMPLETE — SAFE TO CLOSE`

严格持续执行直到上述停止条件之一。
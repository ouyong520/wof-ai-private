# Unified Live Proof Recorder In-Flight Generation Atomicity — Fresh QA Start Prompt

stageId: `UNIFIED_LIVE_PROOF_RECORDER_INFLIGHT_GENERATION_ATOMICITY_QA_V1`

你负责对最新 Recorder in-flight generation atomicity fix 做 **fresh independent QA**。

这是独立 QA，不修改 implementation，不替 implementation 线程自验收。目标是确认旧 Recorder reader 的事件即使已经进入处理流程，也不能在新 generation rollover 完成后继续修改当前 generation 的 fatal / revocation / admission / freshness / authorityGeneration 状态，同时保证当前 generation 的正常路径和 fail-closed 语义没有回归。

## 开始前

必须重新读取当前 `main` 最新 HEAD，并直接检查：

- `parallel/PM/PM_CORE_OPERATING_CHARTER.md`
- `parallel/PM/STAGE_DEDUP_GUARD.md`
- `parallel/PM/STAGE_CLAIMS/**`
- `parallel/LIVE_PROOF_BUNDLE_RECORDER_INFLIGHT_GENERATION_ATOMICITY_FIX/RESULT.md`
- `parallel/LIVE_PROOF_BUNDLE_QA_RECORDER_GENERATION_V2/RESULT.md`
- 当前 `parallel/LIVE_PROOF_BUNDLE/unified_live_proof.py`
- `test_recorder_inflight_generation_atomicity.py`
- `test_recorder_authority_generation.py`
- `test_recorder_authority_heartbeat.py`
- `test_unified_live_proof.py`
- 当前 Unified preflight / freshness / fail-closed 相关测试和近期 commits

先做等价任务去重：

- 若已有等价 fresh QA durable PASS/BLOCKED 结果，立即停止；
- 若本 stage 已 CLAIMED/EXECUTING/COMPLETE，按 duplicate guard 停止；
- 否则原子创建：

`parallel/PM/STAGE_CLAIMS/UNIFIED_LIVE_PROOF_RECORDER_INFLIGHT_GENERATION_ATOMICITY_QA_V1.json`

## 必测边界

至少独立验证以下并发窗口：

1. generation N 已 admitted + healthy；
2. generation N 的 trusted heartbeat 已进入 `feed()` 并停在 authority mutation 之前；
3. generation N+1 child-start rollover 完成；
4. 旧 heartbeat 恢复执行；
5. 不得更新 N+1 的 freshness / authorityGeneration / current health；
6. 对 fatal 做同样 interleaving，旧 fatal 不得 revoke 新 generation；
7. 对 admission 做同样 interleaving，旧 admission 不得使新 generation admitted；
8. 合法的 N+1 admission + heartbeat 随后仍能正常建立健康 authority；
9. failed Recorder child start 仍保持新 generation fail-closed，不能恢复旧 generation；
10. non-Recorder child start 不得错误触发 Recorder generation rollover。

Fresh QA 不得只引用 implementation thread 的 4/4 或其他自测结果。优先复用 QA V2 的真实 in-flight race fixture，并增加必要的独立断言/runner；不得修改 production 来让测试通过。

## 回归范围

在并发边界绿后，继续运行与本改动直接相关的：

- Recorder generation regression；
- Recorder heartbeat regression；
- Unified live-proof regression；
- freshness / fatal-revocation / fail-closed regression；
- current Unified preflight 相关 suite。

确认：

- read-only；
- RAM writes = 0；
- input injection disabled；
- `longCaptureAutoStarted=false`；
- Owner action 仍为 NO；
- 不需要 Browser/WOF 真人运行。

## 写入边界

只允许写：

- `parallel/LIVE_PROOF_BUNDLE_QA_RECORDER_INFLIGHT_ATOMICITY/**`
- 本 stage claim

不要修改：

- `parallel/LIVE_PROOF_BUNDLE/**` production implementation；
- Alpha Transport / PYLAUNCH / Owner OneClick / HUD；
- WOF-052 / WOF-052L 长采集路径。

发现 implementation blocker 时，只记录精确证据并停止，后续另开 fresh fix stage。

## 结果要求

Durable result 必须记录：

- audited current HEAD；
- tested production blob；
- independent concurrency vectors / runner results；
- QA V2 原 blocker 是否被当前 fix 真正关闭；
- generation / heartbeat / Unified / preflight 回归结果；
- safety invariants；
- `Owner action: NO`。

## 停止条件

- `PASS — RECORDER IN-FLIGHT GENERATION ATOMICITY FRESH QA — READY FOR CURRENT-HEAD UNIFIED PREFLIGHT`
- `BLOCKED — RECORDER IN-FLIGHT GENERATION ATOMICITY FRESH QA — <precise blocker>`
- `ALREADY COMPLETE — SAFE TO CLOSE`
- `ALREADY CLAIMED — SAFE TO CLOSE`

严格持续执行直到上述停止条件之一。
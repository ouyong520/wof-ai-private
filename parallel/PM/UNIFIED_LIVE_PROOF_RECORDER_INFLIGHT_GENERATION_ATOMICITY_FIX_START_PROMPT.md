# Unified Live Proof Recorder In-Flight Generation Atomicity Fix — Start Prompt

stageId: `UNIFIED_LIVE_PROOF_RECORDER_INFLIGHT_GENERATION_ATOMICITY_FIX_V1`

你负责修复 Unified Live Proof 当前 Recorder generation 并发切换问题。

Fresh QA V2 已证明：旧 generation 的 reader 事件如果已经进入 `feed()`、通过 generation 检查，但在真正修改 fatal / heartbeat / authority 状态前发生新 generation rollover，那么这个旧事件仍可能在 rollover 之后修改当前 generation 的状态。

这是一个窄范围 implementation fix。不要做独立 QA 自验收，不要扩大到 PYLAUNCH、Alpha Transport、Owner OneClick、Browser/WOF 或 WOF-052/052L 长采集。

## 开始前

重新读取当前 `main` 最新 HEAD，并直接检查：

- `parallel/PM/PM_CORE_OPERATING_CHARTER.md`
- `parallel/PM/STAGE_DEDUP_GUARD.md`
- `parallel/PM/STAGE_CLAIMS/**`
- `parallel/LIVE_PROOF_BUNDLE_QA_RECORDER_GENERATION_V2/RESULT.md`
- `parallel/LIVE_PROOF_BUNDLE_QA_RECORDER_GENERATION_V2/RESULT.json`
- `parallel/LIVE_PROOF_BUNDLE_RECORDER_CHILD_START_GENERATION_FIX/RESULT.md`
- 当前 `parallel/LIVE_PROOF_BUNDLE/unified_live_proof.py`
- 当前 Recorder generation / heartbeat / freshness / fail-closed tests
- 最近与 Recorder generation / feed / child-start 有关的 commits

先按 duplicate guard 检查等价 stage：

- 等价 COMPLETE：`ALREADY COMPLETE — SAFE TO CLOSE`
- 等价 CLAIMED / EXECUTING：`ALREADY CLAIMED — SAFE TO CLOSE`

确认仍需执行后创建：

`parallel/PM/STAGE_CLAIMS/UNIFIED_LIVE_PROOF_RECORDER_INFLIGHT_GENERATION_ATOMICITY_FIX_V1.json`

## 修复目标

修复后的核心不变量：

**generation N+1 rollover 完成之后，任何 generation N 事件，包括已经在旧 reader 的 `feed()` 内部处理中但尚未完成状态修改的事件，都不能再修改当前 slot 的 fatal、revocation、admission、authority freshness 或 authority generation。**

实现必须保证 generation transition 与 authority event 的校验/修改之间具备可靠的原子性。

实现方式由你基于当前代码选择，优先最小且清晰的同步方案，例如：

- 对同一 `RecorderEvidence` 的 generation transition 与 event validation+mutation 使用统一锁；或
- 使用等价的 generation epoch / token compare-and-recheck 机制，确保旧 event 不能跨 rollover 提交状态。

不能通过放宽 validator、忽略旧事件、关闭 generation 检查或把 fail-closed 改成 fail-open 来让测试通过。

同时必须保持：

- 新 generation 在合法 evidence 到来前 fail-closed；
- current-generation 正常 admission / heartbeat / fatal 语义不被破坏；
- child start rollover 仍在可靠的启动边界完成；
- failed child start 不能恢复旧 generation authority；
- non-Recorder child start 不影响 Recorder generation；
- read-only、RAM writes=0、input injection disabled；
- `longCaptureAutoStarted=false`；
- Owner gates / current preflight contract 不被放宽。

## 实现侧回归

允许在 implementation lane 增加/更新聚焦本问题的回归测试，至少覆盖：

1. generation 1 healthy；
2. generation-1 heartbeat 已进入 `feed()` 并通过旧 generation 检查；
3. 在 heartbeat 真正修改 authority 前暂停；
4. generation 2 rollover 完成；
5. 旧 heartbeat 恢复执行；
6. 旧 heartbeat 不能刷新 generation 2 freshness / authority generation；
7. 同样覆盖旧 generation fatal，不能在 rollover 后 revoke generation 2；
8. generation 2 合法事件仍正常；
9. child-start / failed-start / non-Recorder-start 现有回归继续绿色。

同时运行与本改动直接相关的 Recorder generation / heartbeat / Unified regression。

实现线程只能声明 implementation regression green，不能自称 independent QA PASS。

## 写入边界

只允许修改：

- `parallel/LIVE_PROOF_BUNDLE/**`
- `parallel/LIVE_PROOF_BUNDLE_RECORDER_INFLIGHT_GENERATION_ATOMICITY_FIX/**`
- 本 stage claim

不要修改：

- `parallel/LIVE_PROOF_BUNDLE_QA_RECORDER_GENERATION_V2/**`
- Alpha Transport
- PYLAUNCH
- Owner OneClick
- Browser production rules
- WOF-052 / WOF-052L

完成后写 durable RESULT，记录：

- precise failure boundary；
- chosen atomicity mechanism；
- modified files / commits / blobs；
- implementation-side regression results；
- `Owner action: NO`；
- next state 只能是 `READY FOR FRESH INDEPENDENT QA`。

## 停止条件

- `COMPLETE — RECORDER IN-FLIGHT GENERATION ATOMICITY FIX — READY FOR FRESH INDEPENDENT QA`
- `BLOCKED — <precise repository-side blocker>`
- `ALREADY COMPLETE — SAFE TO CLOSE`
- `ALREADY CLAIMED — SAFE TO CLOSE`

严格持续执行直到上述停止条件之一。
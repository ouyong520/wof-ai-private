# Unified Live Proof Recorder Authority Generation — Fresh QA V2 Start Prompt

stageId: `UNIFIED_LIVE_PROOF_RECORDER_AUTHORITY_GENERATION_QA_V2`

你这次负责 **Recorder authority generation 的第二轮 fresh independent QA**。

前一轮 QA 已经证明 child-start 到 reader 接管之间存在 authority rollover 空窗；后续 implementation stage `UNIFIED_LIVE_PROOF_RECORDER_CHILD_START_GENERATION_FIX_V1` 已 COMPLETE，并声称把 generation advance / revoke 提前到 Recorder child-start 边界。你的任务是独立验证这个修复是否真的关闭了原 blocker，同时没有破坏当前合法 generation、fail-closed 和 Unified preflight 语义。

## 开始前

必须重新读取 `main` 当前最新 HEAD，并直接检查当前仓库事实，至少包括：

- `parallel/PM/PM_CORE_OPERATING_CHARTER.md`
- `parallel/PM/STAGE_DEDUP_GUARD.md`
- `parallel/PM/STAGE_CLAIMS/**`
- `parallel/LIVE_PROOF_BUNDLE_QA_RECORDER_GENERATION/RESULT.md`
- `parallel/LIVE_PROOF_BUNDLE_RECORDER_CHILD_START_GENERATION_FIX/RESULT.md`
- 当前 `parallel/LIVE_PROOF_BUNDLE/unified_live_proof.py`
- 当前 Recorder generation / heartbeat / Unified live-proof / freshness / fail-closed / preflight tests
- 与 child start、generation rollover、authority heartbeat/admission 有关的近期 commits

先执行 duplicate protection。若等价 V2 QA 已 COMPLETE，立即 `ALREADY COMPLETE — SAFE TO CLOSE`；若已经 CLAIMED / EXECUTING，立即 `ALREADY CLAIMED — SAFE TO CLOSE`。只有确认这是新的未完成 QA stage 才创建：

`parallel/PM/STAGE_CLAIMS/UNIFIED_LIVE_PROOF_RECORDER_AUTHORITY_GENERATION_QA_V2.json`

## 角色边界

这是 **fresh independent QA**，不要修改 `parallel/LIVE_PROOF_BUNDLE/**` implementation，也不要顺手修发现的问题。若发现 blocker，留下精确 durable evidence 后停止。

## 必须独立验证

至少覆盖：

1. generation 1 已 admitted + healthy；
2. generation 2 Recorder child 进入 launch/start authoritative boundary；
3. generation-2 reader 尚未开始消费 stdout；
4. 延迟 generation-1 trusted heartbeat / admission / fatal / diagnostic stdout 到达；
5. 旧 generation 必须全部无法续期、恢复、回滚或污染 current authority；
6. generation 2 在自己的合法 evidence 到达前必须保持 fail-closed；
7. generation-2 合法 admission + heartbeat 到达后必须正常恢复 healthy；
8. Recorder child spawn failure 后不得恢复 generation 1 authority；
9. 非 Recorder child start 不得错误推进 Recorder generation；
10. 连续至少 generation 1 -> 2 -> 3 rollover 仍保持 monotonic；
11. arbitrary stdout、CR-only、partial fragments、unrelated JSON 仍不能续期 authority；
12. current-generation fatal/revocation 仍保持最高优先级；
13. 重新运行或独立覆盖现有 Recorder generation、Recorder heartbeat、Unified live-proof、freshness、fail-closed、current preflight 相关回归；
14. 保持 read-only、RAM writes=0、input injection disabled、`longCaptureAutoStarted=false`、Owner double gates 和当前中文 Owner UX。

不要只引用 implementation 自测。决定性 PASS 证据必须来自 QA-only 独立 fixtures / runner。

## 写入边界

只允许写：

- `parallel/LIVE_PROOF_BUNDLE_QA_RECORDER_GENERATION_V2/**`
- 本 stage claim

禁止修改：

- `parallel/LIVE_PROOF_BUNDLE/**` implementation
- PYLAUNCH
- Alpha Transport
- Owner OneClick
- HUD
- Browser production rules
- WOF-052/WOF-052L 长采集

## 交付判断

PASS 只有在原 child-start blocker 被独立证明关闭，并且当前 generation 正常路径、fatal/revoke、preflight 与相关回归都没有真实 blocker 时才成立。

PASS 后明确说明：

- Recorder generation release gate 是否关闭；
- current-head Unified preflight 是否 unblocked；
- Owner action 是否仍为 `NO`。

## 停止条件

满足以下任一即停止：

- `PASS — UNIFIED LIVE PROOF RECORDER AUTHORITY GENERATION FRESH QA V2 — READY FOR CURRENT-HEAD PREFLIGHT`
- `BLOCKED — UNIFIED LIVE PROOF RECORDER AUTHORITY GENERATION FRESH QA V2 — <精确 blocker>`
- `ALREADY COMPLETE — SAFE TO CLOSE`
- `ALREADY CLAIMED — SAFE TO CLOSE`

Owner action: **NO**。

严格持续执行直到上述停止条件之一。
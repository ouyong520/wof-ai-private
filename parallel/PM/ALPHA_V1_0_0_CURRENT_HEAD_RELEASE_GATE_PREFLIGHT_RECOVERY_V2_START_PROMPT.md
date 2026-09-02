# Alpha V1.0.0 Current-HEAD Release Gate Preflight — Recovery V2

stageId: `ALPHA_V1_0_0_CURRENT_HEAD_RELEASE_GATE_PREFLIGHT_RECOVERY_V2`
dedupProtocol: `v2`
dedupKey: `alpha.v1.0.0.current-head-release-gate-preflight-recovery-v2`
dedupMode: `exclusive`

PM-authorized recovery of the stopped/stale prior preflight:

- superseded stage: `ALPHA_V1_0_0_CURRENT_HEAD_RELEASE_GATE_PREFLIGHT_V1`
- superseded dedupKey: `alpha.v1.0.0.current-head-release-gate-preflight`
- superseded canonical claim: `parallel/PM/DEDUP_CLAIMS/alpha.v1.0.0.current-head-release-gate-preflight.json`

The historical ACTIVE claim must remain intact. Do not overwrite, delete, reuse or steal it.

你这次负责 **Alpha V1.0.0 Current-HEAD Release Gate Preflight Recovery V2**。

目标：基于当前 `main` 重新核 V1.0.0 玩家测试版所有真实 release gates，输出一份 durable 当前事实，不沿用聊天口头判断，不重复 implementation，不启动 Browser/WOF。

开始前重新读取：

- 当前 `main` HEAD 与近期 commits；
- `parallel/PM/PM_CORE_OPERATING_CHARTER.md`；
- `parallel/PM/STAGE_DEDUP_GUARD.md`；
- superseded preflight canonical/stage claim；
- Player-head strict warningSampleAt fix + Fresh QA V2 RESULT/claims；
- Enemy target head labels latest QA V3 RESULT/claims；
- `ALPHA_V1_ANCHORED_OVERLAYS_LIVE_PROOF_PREP/RESULT.md`；
- original + recovery status for One-Session Live-Proof Tooling；
- V1.0.0 user-test release prep RESULT/claim；
- latest Acceptance / Release Freeze evidence；
- Transport true 5h endurance Recovery V2 workflow, checkpoints, artifacts/result/claim；
- Unified Live Proof current-head/preflight successor evidence as relevant。

如果当前仓库已经有一个更新的等价 durable preflight RESULT 覆盖当前 HEAD 与当前 gates，则 `ALREADY COMPLETE — SAFE TO CLOSE`。

否则先 create-only：
`parallel/PM/DEDUP_CLAIMS/alpha.v1.0.0.current-head-release-gate-preflight-recovery-v2.json`

生成 fresh unpredictable claimToken，重新读取验证 exact ownership 后，再创建：
`parallel/PM/STAGE_CLAIMS/ALPHA_V1_0_0_CURRENT_HEAD_RELEASE_GATE_PREFLIGHT_RECOVERY_V2.json`

必须把 gate 分成：

- `CLOSED`
- `ACTIVE/PENDING`
- `BLOCKED`
- `OWNER ACTION REQUIRED`

特别要求：

1. 5h endurance 只按 GitHub durable workflow/checkpoint/result/claim 判定；口头 PASS 不算，旧 BLOCKED 也不能机械继承。
2. 若 workflow 已有足够 >=5h PASS evidence 但 RESULT/claim 尚未收口，明确写 `evidence complete / durable closure pending`，不要自行宣告 release gate CLOSED。
3. One-Session tooling recovery 若在执行，只记录依赖，不抢 implementation。
4. 真实 Browser/WOF dual-overlay dynamic non-drift proof 未完成前，V1.0.0 必须保持 `NOT RELEASED`。
5. Player-head QA V2 与 enemy labels QA 已 durable PASS 的，不得重开普通 QA。
6. 不创建 filler work；若只剩 tooling -> fresh QA -> owner live proof -> final acceptance/freeze，就明确写这条最短路径。
7. 输出新的 durable RESULT，例如 `parallel/ALPHA_V1_0_0_CURRENT_HEAD_RELEASE_GATE_PREFLIGHT_RECOVERY_V2/RESULT.md`，记录 current HEAD、每个 gate 的证据路径/commit/run、最短 release path。

成功：
`PASS — ALPHA V1.0.0 CURRENT-HEAD RELEASE PREFLIGHT RECOVERY V2 — REPOSITORY GATES RECONCILED / RELEASE REMAINS FAIL-CLOSED ON LISTED OPEN GATES`

阻断：
`BLOCKED — ALPHA V1.0.0 CURRENT-HEAD RELEASE PREFLIGHT RECOVERY V2 — <precise blocker>`

不修改 `product/alpha/**`、Transport、HUDANCHOR implementation；不启动 Browser/WOF。

严格执行 canonical dedup v2，持续到 PASS / BLOCKED / duplicate stop。
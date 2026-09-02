# Alpha V1 Anchored Overlays One-Session Live Proof Tooling — Recovery V2

stageId: `ALPHA_V1_ANCHORED_OVERLAYS_ONE_SESSION_LIVE_PROOF_TOOLING_RECOVERY_V2`
dedupProtocol: `v2`
dedupKey: `alpha.v1.anchored-overlays.one-session-live-proof-tooling-recovery-v2`
dedupMode: `exclusive`

PM-authorized recovery of the stopped/stale prior stage:

- superseded stage: `ALPHA_V1_ANCHORED_OVERLAYS_ONE_SESSION_LIVE_PROOF_TOOLING_V1`
- superseded dedupKey: `alpha.v1.anchored-overlays.one-session-live-proof-tooling`
- superseded canonical claim: `parallel/PM/DEDUP_CLAIMS/alpha.v1.anchored-overlays.one-session-live-proof-tooling.json`

The historical ACTIVE claim must remain intact. Do not overwrite, delete, reuse or steal it.

你这次负责 **Alpha V1 双头顶 One-Session Live-Proof Tooling Recovery V2**。

目标不是重做 prep，而是基于当前 `main` 接回停止的 P0 tooling implementation，只完成最终 Browser/WOF non-drift proof 真正缺的仓库工具。

开始前重新读取：

- 当前 `main`、近期相关 commits；
- `parallel/PM/STAGE_DEDUP_GUARD.md`；
- superseded canonical/stage claim；
- `parallel/ALPHA_V1_ANCHORED_OVERLAYS_LIVE_PROOF_PREP/RESULT.md`；
- `ONE_SESSION_DYNAMIC_PROOF_CONTRACT.md`；
- `LIVE_PROOF_EVIDENCE_SCHEMA.json`；
- 原 `ALPHA_V1_ANCHORED_OVERLAYS_ONE_SESSION_LIVE_PROOF_TOOLING_START_PROMPT.md`；
- current `parallel/HUDANCHOR_PROOF/**` / `HUDANCHOR_REVERSE/**`；
- current player-head / enemy-head production helper/profile and latest QA results。

如果当前 `main` 已经存在等价 COMPLETE tooling + durable RESULT，立即 `ALREADY COMPLETE — SAFE TO CLOSE`，不要重复实现。

否则先 create-only：
`parallel/PM/DEDUP_CLAIMS/alpha.v1.anchored-overlays.one-session-live-proof-tooling-recovery-v2.json`

生成 fresh unpredictable claimToken，重新读取并验证 exact ownership 后，再创建：
`parallel/PM/STAGE_CLAIMS/ALPHA_V1_ANCHORED_OVERLAYS_ONE_SESSION_LIVE_PROOF_TOOLING_RECOVERY_V2.json`

只做缺失实现：

- 在同一未来 runtime 复用 common HUDANCHOR camera/X/YZ/WebGL/remap proof；
- 真实观察/记录 Alpha player-head warning draw/no-draw；
- 真实观察/记录 enemy-head `1P / 2P / 3P` draw/no-draw + retarget clear；
- 绑定 identity / target / warningSampleAt / freshness / runtime+projection+drawing-buffer epoch / confidence / bounds / mapping；
- live 收集 player head-clearance / Y split 与 supported enemy `enemyHeadOffsetsByType`，禁止猜常量；
- invalid authority 必须记录 no-draw/fallback；
- 输出一个符合既有 schema 的 terminal JSON；
- repository-only deterministic tests 覆盖 observer correlation、profile binding fail-closed、invalid/no-draw、schema generation、existing HUDANCHOR compatibility。

硬边界：

- 不启动 Browser/WOF；
- 不改 danger rules、target semantics、Transport authority、game input/AI/RAM；
- synthetic/candidate evidence 不能激活 production profile；
- 不凭空写 camera/Y/head offset 常量；
- 尽量不改 `product/alpha/**`；若只读 diagnostics 暴露确有必要，必须最小化且不改变任何产品语义。

完成：
`COMPLETE — ALPHA V1 ANCHORED OVERLAYS ONE-SESSION LIVE PROOF TOOLING RECOVERY V2 — READY FOR FRESH QA / BOUNDED LIVE RUN`

阻断：
`BLOCKED — ALPHA V1 ANCHORED OVERLAYS ONE-SESSION LIVE PROOF TOOLING RECOVERY V2 — <precise blocker>`

Owner action: **NO**。

严格执行 canonical dedup v2，持续到 COMPLETE / BLOCKED / duplicate stop。
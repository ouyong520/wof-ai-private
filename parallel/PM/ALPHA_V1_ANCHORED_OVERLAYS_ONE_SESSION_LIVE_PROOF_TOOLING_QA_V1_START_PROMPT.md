# Alpha V1 Anchored Overlays One-Session Live-Proof Tooling — Fresh Independent QA

stageId: `ALPHA_V1_ANCHORED_OVERLAYS_ONE_SESSION_LIVE_PROOF_TOOLING_QA_V1`
dedupProtocol: `v2`
dedupKey: `alpha.v1.anchored-overlays.one-session-live-proof-tooling-recovery-v2-fresh-qa`
dedupMode: `exclusive`

你这次负责 **Alpha V1 双头顶 One-Session Live-Proof Tooling Fresh Independent QA**。

前置条件：

- `ALPHA_V1_ANCHORED_OVERLAYS_ONE_SESSION_LIVE_PROOF_TOOLING_RECOVERY_V2` 必须已经有 durable COMPLETE RESULT，且 canonical/stage claim 已正确收口；
- 若 recovery 仍 ACTIVE、BLOCKED、RESULT 缺失或实现仍在变化，立即停止：`PREREQUISITE NOT COMPLETE — SAFE TO CLOSE`；不要抢 implementation，也不要对未完成代码做验收。

目标：基于 recovery 完成后的当前 `main`，独立验证未来一次 Browser/WOF session 所依赖的 dual-overlay proof tooling 不会产生假 PASS、跨 epoch/identity/target 串线、invalid authority 下残留 anchored draw，也不会凭 synthetic/candidate evidence 激活 production profile。

开始前重新读取：

- 当前 `main` 与 Recovery V2 COMPLETE RESULT / claims / commits；
- `parallel/PM/STAGE_DEDUP_GUARD.md`；
- `parallel/ALPHA_V1_ANCHORED_OVERLAYS_LIVE_PROOF_PREP/RESULT.md`；
- `ONE_SESSION_DYNAMIC_PROOF_CONTRACT.md`；
- `LIVE_PROOF_EVIDENCE_SCHEMA.json`；
- current `parallel/HUDANCHOR_PROOF/**` / `HUDANCHOR_REVERSE/**`；
- current player-head / enemy-head helpers, projection profiles and latest QA V2/V3 results only as needed to verify observational contracts。

若已有等价 fresh QA PASS 覆盖 recovery 完成后的 exact tooling blobs，立即 `ALREADY COMPLETE — SAFE TO CLOSE`。

否则严格 canonical dedup v2：先 create-only canonical claim
`parallel/PM/DEDUP_CLAIMS/alpha.v1.anchored-overlays.one-session-live-proof-tooling-recovery-v2-fresh-qa.json`
生成 fresh unpredictable claimToken，重新读取验证 exact ownership，再创建 stage claim。

独立攻击至少包括：

1. terminal schema/JSON 生成必须严格符合 committed evidence schema；
2. player warning observer 与 enemy label observer 必须彼此隔离，不能串 identity/target/sample/epoch；
3. P1/P2/P3 retarget 后旧 enemy label 必须立即清；
4. warningSampleAt freshness barrier 不能被 heartbeat、新 drawing-buffer 或 coercion 绕过；
5. runtime / projection / drawing-buffer epoch 任意缺失、malformed、boxed/coercible、cross-epoch、internally split 都 fail closed；
6. stale / nonfinite / low-confidence / out-of-bounds / invalid mapping authority 必须记录 no-draw 或 fixed fallback，不能保留旧 anchored coordinate；
7. resize/fullscreen/DPR remap 必须要求 current mapping generation，旧 mapping 不得复用；
8. player head-clearance / Y split 与 enemy type head offset 必须只有 live-observed authority 才能进入 candidate/frozen payload；missing/incomplete observation 必须给 precise `INCOMPLETE_OBSERVATION:<component>`；
9. synthetic/candidate fixture 无论多完整，都不得产生 production profile activation；
10. `IMPLEMENTATION_READY` 只能在 evidence contract 所需真实 live observations 完整且 authority 全部有效时生成；repository QA 本身绝不能伪造该 terminal；
11. existing common HUDANCHOR proof thresholds/384x224/camera/X/YZ/WebGL/remap contract 不得被 tooling 静默放宽；
12. 不修改 danger rules、target semantics、Transport authority、game input/AI/RAM。

QA 必须使用独立 fixture / adversarial matrix；implementation 自带 regression 只能作为 supportive evidence。

不启动 Browser/WOF，不修改 `product/alpha/**` implementation，不修改 recovery tooling implementation；只写 QA lane + claim/result。

PASS：
`PASS — ALPHA V1 ANCHORED OVERLAYS ONE-SESSION LIVE PROOF TOOLING FRESH QA — RECOVERY V2 VERIFIED / READY FOR BOUNDED LIVE RUN`

BLOCKED：
`BLOCKED — ALPHA V1 ANCHORED OVERLAYS ONE-SESSION LIVE PROOF TOOLING FRESH QA — <precise blocker>`

Owner action: **NO**。

严格持续执行到 PASS / BLOCKED / prerequisite stop / duplicate stop。
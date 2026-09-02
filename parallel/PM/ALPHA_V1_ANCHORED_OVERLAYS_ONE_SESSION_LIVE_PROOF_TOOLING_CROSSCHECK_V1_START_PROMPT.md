# Alpha V1 Anchored Overlays One-Session Live-Proof Tooling — Independent Cross-Check V1

stageId: `ALPHA_V1_ANCHORED_OVERLAYS_ONE_SESSION_LIVE_PROOF_TOOLING_CROSSCHECK_V1`
dedupProtocol: `v2`
dedupKey: `alpha.v1.anchored-overlays.one-session-live-proof-tooling-recovery-v2-crosscheck`
dedupMode: `independent-validation`
independentValidationGroup: `alpha-v1-dual-overlay-tooling-recovery-v2`
independentValidationKey: `second-opinion-adversarial-v1`

你这次负责 **Alpha V1 双头顶 One-Session Live-Proof Tooling Recovery V2 独立 second-opinion cross-check**。

这是 PM 明确授权的独立第二意见，不是 Fresh QA V1 的重复线程。不得读取或继承 Fresh QA V1 的 verdict、fixture 或断言结果作为自己的证明；只能把 Recovery V2 COMPLETE RESULT、当前实现和正式 contract/schema 当作被测对象。

前置事实必须重新从当前 `main` 验证：

- `ALPHA_V1_ANCHORED_OVERLAYS_ONE_SESSION_LIVE_PROOF_TOOLING_RECOVERY_V2` 已 durable COMPLETE；
- canonical/stage claim 已 COMPLETE；
- 当前 tooling blobs 与 `RUN_MANIFEST.json` 一致；
- 若实现已在 Recovery COMPLETE 后发生 release-relevant drift，记录精确 drift 并停止，不对移动目标给 PASS。

开始前读取：

- `parallel/PM/STAGE_DEDUP_GUARD.md`
- Recovery V2 prompt / RESULT / claims
- `parallel/ALPHA_V1_ANCHORED_OVERLAYS_ONE_SESSION_LIVE_PROOF_TOOLING/**`
- `parallel/ALPHA_V1_ANCHORED_OVERLAYS_LIVE_PROOF_PREP/RESULT.md`
- `ONE_SESSION_DYNAMIC_PROOF_CONTRACT.md`
- `LIVE_PROOF_EVIDENCE_SCHEMA.json`
- current HUDANCHOR proof common lane
- current player warning / enemy target-label helpers and current projection profiles，仅用于校验 observational boundary

严格执行 canonical dedup v2 independent-validation，effective key 必须隔离于主 Fresh QA。

独立攻击重点：

1. **False IMPLEMENTATION_READY**：构造缺 phase、缺 live head facts、缺 visual confirmation、缺 stale-authority exercise、缺 retarget、缺 resize/remap 等 evidence，任何一种都不得生成 `IMPLEMENTATION_READY`。
2. **Synthetic promotion**：repository fixture/candidate/replay 无论多完整都不得激活 production profile，也不得冒充 Browser/WOF live evidence。
3. **Player/enemy observer isolation**：player warning 与 enemy label 的 identity/target/sampleAt/epoch/mapping 不得交叉借权。
4. **warningSampleAt**：missing/null/string/boxed/coercible/NaN/Infinity/旧 sample + 新 heartbeat/新 drawing-buffer 均必须 fail closed。
5. **Epoch authority**：runtime/projection/drawing-buffer 任意 missing/malformed/coercible、三方 cross-epoch、drawing-buffer 内部自洽但与当前 projection 旧 epoch 混用，都不能产生 anchored proof PASS。
6. **Retarget/identity replacement**：P1→P2→P3、enemy same-slot replacement、player respawn/object replacement 后旧标签/旧 anchored coordinate/旧 proof authority 必须立即失效。
7. **Head-fact capture**：player body/reference click 与 enemy type head click 必须绑定当前 live identity；ambiguous overlap、未观察 type、重复 capture spread >4 native px 必须 precise incomplete/fail closed，绝不能猜常量。
8. **Stale-authority exercise**：停止 observer 的窗口内必须观察 player fixed fallback + enemy no-draw/suppression；任何 anchored draw 都是 blocker；恢复必须走 official transport install API。
9. **Manifest drift**：当前被测 blobs 与 RUN_MANIFEST 任一不一致必须 preflight fail closed。
10. **Read-only**：不得引入 RAM write、input injection、Worker replacement、Blob rewrite、danger-rule/target-semantics 改写。

必须自建独立 adversarial fixture/matrix；Recovery 自带 19/19 regression 只能作为 supportive evidence，不能作为 cross-check 的独立证明。

只做 repository-only validation，不修改 tooling implementation，不修改 `product/alpha/**`，不启动 Browser/WOF。

PASS：
`PASS — ALPHA V1 ANCHORED OVERLAYS ONE-SESSION LIVE PROOF TOOLING INDEPENDENT CROSS-CHECK — NO FALSE-PASS / AUTHORITY-LEAK DEFECT FOUND`

BLOCKED：
`BLOCKED — ALPHA V1 ANCHORED OVERLAYS ONE-SESSION LIVE PROOF TOOLING INDEPENDENT CROSS-CHECK — <precise blocker>`

Owner action: **NO**。

严格持续到 PASS / BLOCKED / duplicate stop。
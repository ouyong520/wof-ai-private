# Alpha V1 Live Acceptance — Owner Calibration + Local Identity Recovery V1

stageId: `ALPHA_V1_LIVE_ACCEPTANCE_OWNER_CALIBRATION_IDENTITY_RECOVERY_V1`
dedupProtocol: `v2`
dedupKey: `alpha.v1.live-acceptance.owner-calibration-identity-recovery-v1`
dedupMode: `exclusive`

你负责 **Alpha V1 Live Acceptance Owner Calibration + Local Identity Recovery V1**。

这是 2026-09-02 successor package `2026.09.02.3aad0e9d3167` 的真实 Owner 实机测试暴露出的窄 implementation recovery。不是 Fresh QA，不是 second opinion，不重做已经 COMPLETE 的 Overlay + Re-entry Recovery / Execution Recovery V2。

仓库：`ouyong520/wof-ai-private`

开始前重新读取 current `main`、`parallel/PM/STAGE_DEDUP_GUARD.md`、`parallel/PM/TESTING_CADENCE_POLICY.md`、以下 COMPLETE authority：

- `parallel/PM/RESULTS/ALPHA_V1_LIVE_ACCEPTANCE_OVERLAY_REENTRY_RECOVERY_V1_EXECUTION_RECOVERY_V2_RESULT.md`
- `parallel/PM/DEDUP_CLAIMS/alpha.v1.live-acceptance.overlay-reentry-recovery-v1.execution-recovery-v2.json`
- current `parallel/OWNER_ONECLICK/package_manifest.json`
- package source `3aad0e9d316701e30cda65dc4a45ab00f0e3d1c3`
- current `product/alpha/**`
- current `parallel/HUDANCHOR_PROOF/**`
- current `parallel/PYLAUNCH/**`
- current `parallel/OPTOOLKIT/**`

## Canonical ownership

第一项 mutation 必须 create-only：

`parallel/PM/DEDUP_CLAIMS/alpha.v1.live-acceptance.owner-calibration-identity-recovery-v1.json`

使用 fresh unpredictable `claimToken`，re-read current main 验证 exact ownership 后，再 create-only：

`parallel/PM/STAGE_CLAIMS/ALPHA_V1_LIVE_ACCEPTANCE_OWNER_CALIBRATION_IDENTITY_RECOVERY_V1.json`

已有等价 ACTIVE/COMPLETE successor => duplicate stop，禁止抢 claim。

---

# 最新真实 Owner evidence

Owner 使用正式 successor package：

- packageVersion `2026.09.02.3aad0e9d3167`
- sourceCommit `3aad0e9d316701e30cda65dc4a45ab00f0e3d1c3`

实机诊断窗口确认：

- Browser：已连接
- WOF 页面：已找到
- Worker：已找到
- WASM / 内存：已找到
- 游戏版本：`World 921031` 已确认
- readOnly：开启
- 游戏内存写入：0
- 输入注入：关闭
- discovery path：`cached-runtime-health`
- exact World SHA-256：`5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62`

但 Alpha release activation 失败，真实错误为：

`检测器本地 World 921031 身份校验失败：P1/P2/P3 local identity mismatch`

因此这是 **World/Worker/WASM 已 authoritative accepted，但 detector-local player identity gate 误拒绝 Alpha activation** 的实机 defect。

同一实机 session 的 bounded projection calibration UI 曾显示：

`WOF 头顶定位一次校准`

`正常左右移动，让背景明显滚动；正在自动识别 Camera。`

`samples 29 / NEED_MORE_SAMPLES`

Owner 正常继续操作后没有得到下一步“点击 P1 头顶”等提示，之后画面也没有继续显示有效校准引导；最终无 `1P/2P/3P`、无 `[危险]`。

不要把这次无 overlay 误判为 danger rule 未触发：Alpha activation 已被 local identity gate 明确拒绝，且 calibration flow 同时没有完成。

---

# 已确认 package-source truth

在 source `3aad0e9d316701e30cda65dc4a45ab00f0e3d1c3`：

`product/alpha/wof_alpha_loader.js`

读取：

`selfIndexes=[U16(0xFFBE1C+0x7C), U16(0xFFBEFC+0x7C), U16(0xFFBFDC+0x7C)]`

然后将三个值无条件送入 `validateIdentityProbe()`。

`product/alpha/wof_alpha_core.js`

当前无条件要求：

`selfIndexes == [0,4,8]`

否则加入：

`P1/P2/P3 self-index mismatch`

并使整个 detector identity fail-closed。

这条 live defect 高度提示：**unused/inactive player slots 或当前实际 player lifecycle 状态不应被误当作 World ROM identity 的硬失败条件**。但禁止直接假设具体运行值；必须从现有 recorder / topology / player lifecycle authority 和 deterministic fixtures 证明正确语义，再修。

`parallel/HUDANCHOR_PROOF/wof_owner_projection_top.js` 当前 calibration state machine：

- Camera quality 未 `ok` 时持续显示 sample/reason；
- 只有 Camera ready 后才提示点击一次 P1 头顶；
- 后续还要求 horizontal/depth/jump/WebGL/resize/enemyHeadEvidence；
- 不能伪造这些 live proof。

本次真实现场证明：Owner 可进入 `NEED_MORE_SAMPLES`，但流程可能长期无可理解进展或 UI/authority lifecycle 中断，导致 novice Owner 看不到下一步。

---

# Recovery goals

把下面两个真实 field defect 作为一个 coherent live-acceptance recovery 做完整。

## A. Detector-local P1/P2/P3 identity false rejection

1. 追 current authority，明确 `+0x7C` 的 player-local identity 字段在：
   - P1 active；
   - P2/P3 inactive / not joined；
   - player death/respawn；
   - room leave/re-entry；
   - same runtime generation / new generation
   时的 authoritative semantics。
2. 禁止简单删除 `selfIndexes` gate 或把任何值都当通过。
3. 保持 World identity 的真正硬门不放宽：
   - exact World 921031 SHA-256；
   - Browser/WASM/heap authority；
   - generation / stale authority；
   - ROM locator sanity；
   仍必须严格 fail-closed。
4. 把 player-local identity sanity 从“无条件要求三个 slot 同时为 0/4/8”修成 **与实际 active/authoritative player lifecycle 一致** 的严格规则；如果 unused slots 没有 authoritative identity，不得因为未初始化值而拒绝整个 World。
5. P1/P2/P3 target semantics仍保持：`0 -> 1P`、`4 -> 2P`、`8 -> 3P`；禁止改变 target7E 语义。
6. 要有 deterministic fixtures 覆盖至少：
   - one-player live topology；
   - P2/P3 inactive；
   - P2/P3 joined；
   - malformed active player self-index fail-closed；
   - stale/respawn/re-entry generation；
   - wrong World / wrong SHA 仍拒绝；
   - accepted exact World + valid active player topology 可以启动 Alpha。

## B. Owner calibration `NEED_MORE_SAMPLES` / prompt continuity recovery

1. 追 package-selected HUDANCHOR + PYLAUNCH projection recovery 生命周期，解释为什么实机可停在 `samples 29 / NEED_MORE_SAMPLES` 后没有清晰下一步，且 calibration UI/引导没有持续到 terminal result。
2. 不降低 Camera/projection proof 的真实性要求，不硬编码 camera address/scale/bias，不 synthetic promote。
3. novice Owner 流程必须保持可见、可恢复、可终止：
   - Camera 尚未 ready 时持续显示明确中文动作；
   - 显示“还差什么”而不是只有内部 reason；
   - 有 bounded progress/timeout watchdog；
   - 若场景无法产生足够 camera scroll evidence，明确告诉 Owner 如何继续或自动等待合适场景；
   - 不允许 UI 静默消失然后后台永久等待；
   - Worker/page/runtime generation 变化时，旧 calibration authority 必须失效并自动重新进入清晰步骤；
   - Alpha activation 暂时失败时，projection calibration 不能留下无状态/无提示的半流程。
4. Camera ready 后的最小 Owner 操作仍保持：
   - 点一次 P1 头顶；
   - 正常横向/卷屏；
   - 一次纵深；
   - 一次跳跃；
   - 一次 resize/fullscreen + recovery；
   - 至少一个可见敌人类型；
   - 最终选择唯一稳定 Y-Z / Y+Z / Y，或明确失败。
5. 自动 evidence/ZIP 必须记录 calibration 的每个阶段、reason、timeout/restart、terminal result；不要求 Owner按 7/8。

## C. Integration / package

1. 修复必须 package-selected 进入新的 immutable successor package；旧 `2026.09.02.3aad0e9d3167` 不再让 Owner重复测试。
2. 保持 room re-entry Worker rediscovery / Alpha reactivation 已完成能力，不回退。
3. 保持 cheap cached-runtime-health，不重新引入周期 full heap/ROM scan。
4. 保持 automatic evidence/ZIP。
5. 安全边界必须保持：
   - `readOnly=true`
   - `ramWrites=0`
   - `inputInjection=false`
6. Windows portable：中文路径/空格路径、first-run、second-run local/offline、mutation rejection、last-known-good 必须继续 PASS。

## D. Testing cadence

这是 implementation recovery + module-owned self-check，不开 Fresh QA / second opinion / cross-check。

不要启动 Browser/WOF，不要伪造这次真实 live calibration PASS。repository tests 只证明状态机与 gate 行为；最终仍需一次 focused Owner live retest。

至少做：

- detector local identity topology matrix；
- exact World SHA remains mandatory；
- inactive player slots do not false-reject if repository authority proves that semantics；
- malformed active player identity still fail-closed；
- calibration NEED_MORE_SAMPLES continuity；
- bounded timeout/progress guidance；
- UI does not silently disappear before terminal/restart；
- generation replacement resets old calibration authority；
- valid bounded calibration consumer path；
- re-entry regression；
- automatic evidence/ZIP；
- Windows portable/package integrity；
- readOnly/ramWrites/inputInjection boundaries。

---

# Durable RESULT

写：

`parallel/PM/RESULTS/ALPHA_V1_LIVE_ACCEPTANCE_OWNER_CALIBRATION_IDENTITY_RECOVERY_V1_RESULT.md`

RESULT 必须明确：

- live `P1/P2/P3 local identity mismatch` 的真实 root cause；
- `+0x7C` 在 active/inactive player slots 的 authoritative语义；
- 修复后的 strict identity rule；
- exact World SHA/ROM authority 未放宽；
- calibration `NEED_MORE_SAMPLES` / UI continuity root cause 和修复；
- re-entry/Alpha reactivation是否保持；
- successor package exact pins；
- workflow / Windows portable / self-check结果；
- safety boundaries；
- precise Owner next step。

matching claimToken 才能关闭 canonical/stage claim。

最终只允许：

`COMPLETE — ALPHA V1 LIVE ACCEPTANCE OWNER CALIBRATION + LOCAL IDENTITY RECOVERY V1 — SUCCESSOR PACKAGE READY — READY FOR ONE FOCUSED OWNER LIVE RETEST`

或：

`BLOCKED — ALPHA V1 LIVE ACCEPTANCE OWNER CALIBRATION + LOCAL IDENTITY RECOVERY V1 — <exact concrete blocker>`

少汇报、不要中断、持续执行；不要停在 claim、单个 patch、单次测试、workflow in-progress、manifest 未验证或 RESULT 未收口阶段。完整 implementation、integration、自测、successor package、durable RESULT、canonical/stage claim 全部完成后再停止。
# Alpha V1 Live Acceptance Overlay + Re-entry Recovery V1 — Execution Recovery V2

stageId: `ALPHA_V1_LIVE_ACCEPTANCE_OVERLAY_REENTRY_RECOVERY_V1_EXECUTION_RECOVERY_V2`
dedupProtocol: `v2`
dedupKey: `alpha.v1.live-acceptance.overlay-reentry-recovery-v1.execution-recovery-v2`
dedupMode: `exclusive`

你负责 **Alpha V1 Live Acceptance Overlay + Re-entry Recovery V1 — Execution Recovery V2**。

这是 PM-authorized implementation continuation recovery。原 V1 worker 已完成主要 implementation，并在最终 implementation-source workflow / Windows portable / immutable successor package / durable RESULT / claim closeout 前停止于 `LOCKED`。本 recovery 只从 current `main` 接续剩余工作；不要重做已完成实现，不开 QA，不启动 Browser/WOF，不让 Owner 测旧包。

仓库：`ouyong520/wof-ai-private`

## Superseded historical ownership

历史 canonical claim：

`parallel/PM/DEDUP_CLAIMS/alpha.v1.live-acceptance.overlay-reentry-recovery-v1.json`

历史 stage claim：

`parallel/PM/STAGE_CLAIMS/ALPHA_V1_LIVE_ACCEPTANCE_OVERLAY_REENTRY_RECOVERY_V1.json`

两者当前仍为 `ACTIVE`，属于已停止 worker 的历史 ownership evidence。禁止覆盖、删除、重用、窃取旧 claimToken。由本 V2 recovery generation 建立新的 successor authority；旧 ACTIVE records 保留原样，并在本 recovery RESULT 中明确 superseded。

原 START_PROMPT：

`parallel/PM/ALPHA_V1_LIVE_ACCEPTANCE_OVERLAY_REENTRY_RECOVERY_V1_START_PROMPT.md`

原任务已落地主体范围包括：

- bounded projection authority / Owner-friendly proof integration；
- room re-entry Worker rediscovery；
- Alpha revoke / automatic reactivation；
- stable cheap runtime health，不恢复周期性重型扫描；
- automatic live evidence collection / organization / ZIP；
- secure Git upload only when existing safe authority is available, otherwise local-only graceful fallback；
- successor package selection/self-check work already underway。

已观察到的相关 current commits包括但不限于：

- `43f13c0cda5181e3cdf041ad5c39f234713f7236` — deep Worker rediscovery after page-only；
- `9f82463b2f62f62e3a75346f7a0132da0b17c7aa` — automatic live evidence session packager；
- `ba39db6a32bc669289803566670b3f6487837b2c` — live acceptance auto collect/package；
- `f92147853c6f6437c7cb07b0c4f4eff977f6f2d2` — select overlay re-entry recovery runtime；
- `5936234157c09480850490df51122fe58bb5f38a` — overlay/re-entry recovery self-checks；
- `680da83bae06bd0393f1594dfeb0f422f64b0b53` — CI coverage；
- `3aad0e9d316701e30cda65dc4a45ab00f0e3d1c3` — successor package content assertions。

这些 commit 仅是恢复定位线索；必须以 current `main` 为准重新核对，不得假设其仍为最终 candidate。

## Recovery ownership

第一项 mutation 必须 create-only：

`parallel/PM/DEDUP_CLAIMS/alpha.v1.live-acceptance.overlay-reentry-recovery-v1.execution-recovery-v2.json`

使用 fresh unpredictable `claimToken`，re-read current main 并验证 exact ownership 后，再 create-only：

`parallel/PM/STAGE_CLAIMS/ALPHA_V1_LIVE_ACCEPTANCE_OVERLAY_REENTRY_RECOVERY_V1_EXECUTION_RECOVERY_V2.json`

如等价 recovery 已 COMPLETE，返回 `ALREADY COMPLETE — SAFE TO CLOSE`；如本 recovery claim 已被占用，返回 `ALREADY CLAIMED — SAFE TO CLOSE`。

## Required continuation

1. 重新读取 current `main`、`STAGE_DEDUP_GUARD.md`、`TESTING_CADENCE_POLICY.md`、原 V1 START_PROMPT、历史 V1 canonical/stage claim、相关 implementation commits、current package manifest、current workflow state。
2. 确认已经落地的 projection/re-entry/auto-evidence implementation 没有 material regression；不要为了“再确认”重做整个实现。
3. 找到原 worker 所指的最终 implementation-source workflow / Windows portable validation 的 exact run/candidate：
   - 如果 workflow 已 terminal success，立即继续，不要停在“已通过”汇报；
   - 如果 workflow 已 terminal failure，读取 exact failed job/step/log，只修本 recovery scope 内真实 implementation/package defect，然后只重跑受影响检查；
   - 如果 workflow 仍在运行，不要把 `LOCKED` / `WAITING` 当任务终态；在本次执行中持续重新读取其状态直到得到 terminal state，除非遇到明确无法由本 worker解决的外部 blocker。
4. 完成 immutable successor manifest/package：
   - 新 packageVersion / source identity，不能复用已被 live retest 否决的 `2026.09.02.91be86ade8d4`；
   - exact selected blobs pin；
   - projection proof/authority consumer、re-entry rediscovery/reactivation、auto evidence/ZIP 都必须实际 selected；
   - package mutation/stale payload fail-closed。
5. 完成 Windows portable/current candidate validation：
   - 中文路径、空格路径；
   - first-run install；
   - second-run local/offline direct launch；
   - menu 6 正常流程自动建立 session evidence、自动整理并自动 ZIP；menu 7/8 仅 manual fallback；
   - 无 safe Git authorization 时 local-only graceful fallback，不要求 Owner 配 token；
   - readOnly=true / ramWrites=0 / inputInjection=false。
6. 不伪造 bounded live projection proof。如果 current repository authority 仍要求一次真实 Owner calibration，则 successor package 必须做到 `READY FOR ONE MINIMAL OWNER CALIBRATION/LIVE RETEST`，并只保留现有 MINIMAL_LIVE_PROOF 所要求的最少中文引导动作；repository self-check 不能冒充 live proof。
7. 写 durable RESULT：

`parallel/PM/RESULTS/ALPHA_V1_LIVE_ACCEPTANCE_OVERLAY_REENTRY_RECOVERY_V1_EXECUTION_RECOVERY_V2_RESULT.md`

RESULT 必须记录：

- current exact candidate/source/package pins；
- 原 V1 已完成实现如何被复用；
- exact workflow run(s) 与 terminal conclusion；
- Windows portable validation；
- projection authority 当前状态与是否仍需一次 bounded Owner calibration；
- re-entry Worker rediscovery / Alpha reactivation；
- periodic hitch regression boundary；
- auto evidence/ZIP；
- Git upload authority结论；
- self-check/validation exact results；
- safety：readOnly=true / ramWrites=0 / inputInjection=false；
- 历史 V1 ACTIVE canonical/stage 保留原样并由本 V2 successor authority supersede；
- precise next step。
8. 用本 recovery matching claimToken 完整关闭本 V2 canonical/stage claim。

## Stop discipline

不要停止在：

- claim acquired；
- 单个 patch；
- 单次 self-check；
- workflow queued/in_progress；
- `LOCKED` / `WAITING`；
- package manifest 生成但未验证；
- RESULT 写了但 claim 未收口。

持续执行到完整模块 continuation、immutable successor package、必要验证、durable RESULT、本 recovery canonical/stage claim 全部收口。

禁止：

- 新开 Fresh QA / second opinion / cross-check；
- 重做已完成 projection/re-entry/evidence implementation 仅为增加信心；
- 启动 Browser/WOF；
- 让 Owner 测旧包；
- 修改/关闭历史 V1 ACTIVE claim/token；
- 猜 projection 常量、伪造 live proof、放宽 fail-closed；
- 将 secret/token 写入 repo/package/log/result ZIP。

最终只允许：

`COMPLETE — ALPHA V1 LIVE ACCEPTANCE OVERLAY + REENTRY RECOVERY V1 EXECUTION RECOVERY V2 — SUCCESSOR PACKAGE/RESULT DURABLE — READY FOR ONE MINIMAL OWNER CALIBRATION/LIVE RETEST`

或如果 current repository authority 已足够无需 calibration：

`COMPLETE — ALPHA V1 LIVE ACCEPTANCE OVERLAY + REENTRY RECOVERY V1 EXECUTION RECOVERY V2 — SUCCESSOR PACKAGE/RESULT DURABLE — READY FOR ONE FOCUSED OWNER LIVE RETEST`

或：

`BLOCKED — ALPHA V1 LIVE ACCEPTANCE OVERLAY + REENTRY RECOVERY V1 EXECUTION RECOVERY V2 — <exact concrete blocker>`

少汇报、不要中断、持续执行；不要在 workflow 仍可继续推进时以 LOCKED/WAITING 停止。
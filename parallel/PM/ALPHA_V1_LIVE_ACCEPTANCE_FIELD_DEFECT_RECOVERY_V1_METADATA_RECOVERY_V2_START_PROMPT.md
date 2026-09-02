# Alpha V1 Live Acceptance Field Defect Recovery V1 — Dedup Metadata Recovery V2

stageId: `ALPHA_V1_LIVE_ACCEPTANCE_FIELD_DEFECT_RECOVERY_V1_METADATA_RECOVERY_V2`
dedupProtocol: `v2`
dedupKey: `alpha.v1.live-acceptance.field-defect-recovery-v1`
dedupMode: `exclusive`

你负责 **Alpha V1 Live Acceptance Field Defect Recovery V1 — Dedup Metadata Recovery V2**。

这是 PM 对上一份 START_PROMPT 的 **metadata-only recovery**。上一份：

`parallel/PM/ALPHA_V1_LIVE_ACCEPTANCE_FIELD_DEFECT_RECOVERY_V1_START_PROMPT.md`

缺少 `stageId` / `dedupProtocol` / `dedupMode` 的 mandatory canonical dedup v2 声明，因此 worker 正确 fail-closed；该 BLOCKED 发生在 claim acquisition 之前，不是 implementation defect，也没有授权任何 implementation/result mutation。

截至 PM 修复时，canonical path：

`parallel/PM/DEDUP_CLAIMS/alpha.v1.live-acceptance.field-defect-recovery-v1.json`

不存在。因此本 V2 **保持同一个 logical dedupKey**，不制造新的 recovery key 来绕过 canonical exclusion。`stageId` 使用新的 metadata-recovery stage identity；canonical claim 的 `promptPath` 必须指向本 V2 START_PROMPT。

仓库：

`ouyong520/wof-ai-private`

开始时必须重新读取 current `main`，然后严格读取：

- `parallel/PM/STAGE_DEDUP_GUARD.md`
- `parallel/PM/TESTING_CADENCE_POLICY.md`
- `parallel/PM/PM_CORE_OPERATING_CHARTER.md`
- `parallel/PM/ALPHA_V1_LIVE_ACCEPTANCE_FIELD_DEFECT_RECOVERY_V1_START_PROMPT.md`

本 V2 只修 dedup authority metadata；**V1 START_PROMPT 的全部现场事实、implementation scope、禁止项、自测要求、successor package、durable RESULT 与 terminal condition 全部继续有效**。

严格按 canonical dedup v2：

1. 重新读取 current main / relevant claims / results，先做 duplicate/DONE preflight；
2. 对 exact canonical path 做 create-only claim；
3. fresh `claimToken`；
4. create 成功后重新读取 current main 中 claim，并验证 `schema / dedupKey / effectiveDedupKey / dedupMode / stageId / promptPath / claimToken / state`；
5. 验证通过后才 create-only stage claim：
   `parallel/PM/STAGE_CLAIMS/ALPHA_V1_LIVE_ACCEPTANCE_FIELD_DEFECT_RECOVERY_V1_METADATA_RECOVERY_V2.json`；
6. stage claim 也成功并复核后，才允许开始 V1 implementation recovery；
7. 如果 canonical path 在此期间被等价 worker 占用或已有 COMPLETE successor，按 guard duplicate stop，不抢 claim、不改旧 claim。

这是 **implementation recovery**，不是 Fresh QA、second opinion 或 cross-check。不要因为这次 metadata correction 新开 QA 链。

Owner 已经承担过一次失败真人 WOF 验收；implementation coherent candidate 完成前禁止要求 Owner 再进游戏。保持 `readOnly=true / ramWrites=0 / inputInjection=false`，不改 danger rules、target semantics，不碰 Training Farm / Collector。

完成后必须继续满足 V1 要求：完整 implementation + integration + module self-check + new successor OneClick/portable candidate + durable RESULT + matching-token canonical/stage claim 收口。

最终只允许：

`COMPLETE — ALPHA V1 LIVE ACCEPTANCE FIELD DEFECT RECOVERY V1 — <self-check summary> — READY FOR ONE FOCUSED OWNER LIVE RETEST`

或：

`BLOCKED — ALPHA V1 LIVE ACCEPTANCE FIELD DEFECT RECOVERY V1 — <精确具体 blocker>`

或 canonical duplicate stop。

少汇报、不要中断、持续执行，不要反复确认；不要停在 claim、检查、单个 patch 或单次测试阶段。
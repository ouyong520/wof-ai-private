# WOF Beta Prospective Manifest Set — Fresh Independent QA Start Prompt

你负责全新的独立 QA，不修改候选 manifest，不修改生产规则。

开始前重新读取最新：
- `parallel/BETA_TRIAGE/**`
- `parallel/BETA_MANIFESTS/**`
- `parallel/PROSPECTIVE_VALIDATOR/**`
- `parallel/SEQMINER/**` 与相关 WOF-046/047/049/050/051 报告
- `parallel/PM/CHINESE_UI_UX_REQUIREMENT.md`

目标：独立确认当前 Beta manifest set 是否可以安全交给 Prospective Validator 做 research-only validation。

必须检查：
1. 每个 manifest 都符合 `wof-prospective-candidate-v1` schema。
2. identity 只能是 `Warriors of Fate (World 921031)` + 黄金 SHA-256 `5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62`。
3. `promotion` 必须保持 `research-only`，任何自动 production promotion 都应 FAIL。
4. T notation 必须按 Browser canonical raw decimal：T16=0x10、T20=0x14、T23=0x17、T24=0x18；不能把旧 local bare T 标签错映射。
5. T18 BODY4728 的 single-state ambiguity 不能被编译成 A4704-specific manifest；未解决分支必须继续 NOT_READY。
6. T23 A5888 BODY4936 必须保持 ordered tail3，不能退化成 constituent single-state rule。
7. current-level candidates 与 sequence/history candidates 的 lifecycle/reset 约束不能混淆。
8. T16 必须保持 `IMMINENT DANGER` 语义，不可伪装成 A6432-specific。
9. D867BA / D8811E 等 descriptor family 的支持数、时间窗、target/type gate 与 source evidence 不得明显矛盾。
10. 每个 READY manifest 的 gate 必须足够保守：multi-room、signal/support、hard miss、必要的 target/type/lifecycle 条件。
11. index 中 READY / NOT_READY 状态和实际文件一致。
12. Validator 能解析 READY manifest；不需要修改 Validator core。
13. 只允许 fresh prospective evidence 满足 prospective gate；旧 discovery corpus 不能重标为 prospective。
14. owner-facing checklist/入口默认简体中文。

允许：独立 QA fixtures、schema validation、mock runs、cross-check 报告。
禁止：修改 `parallel/BETA_MANIFESTS/**`、修改 Alpha、改生产规则、RAM writes、输入注入、攻击研究扩展。

发现问题后不要自己修，写精确 blocker 并停止。

停止条件：
- `PASS — BETA PROSPECTIVE MANIFEST SET READY FOR VALIDATION`
或
- `BLOCKED — P0/P1 <precise blocker>`

把最终 QA 结果写回 GitHub。
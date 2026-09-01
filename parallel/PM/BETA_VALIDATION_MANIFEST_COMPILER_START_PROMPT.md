# WOF Beta Validation Manifest Compiler — Fresh Start Prompt

你负责把 Beta Rule Candidate Triage 的机器队列转换成 Prospective Validator 可直接消费的 research-only candidate manifests。

读取：
- `parallel/BETA_TRIAGE/**`
- `parallel/PROSPECTIVE_VALIDATOR/**`
- `parallel/SEQMINER/**`
- `parallel/COVERAGE/**`
- 当前 WOF-051/052 权威证据

写入范围：仅 `parallel/BETA_MANIFESTS/**`。

## 目标

- 等待/读取当前 Beta machine-readable validation queue；
- 只对明确标记为 `prospective-ready` 或已有足够 ordered/current-level predicate 定义的候选生成 manifest；
- 每个 manifest 记录来源证据、candidate id、type `T<decimal>(0xHH)`、期望 attack、predicate/ordered sequence、支持样本、禁止自动 production promotion；
- T18 BODY4728 若没有新 ordered discriminator，不得生成 A4704/A4712 specific prospective manifest；
- T23 A5888 BODY4936 tail3 可按已有研究证据作为 research-only manifest candidate；
- 已经 production 的两条 Alpha T18 current-level rules只可作为 regression/example，不进入新的 Beta discovery queue；
- 对证据不足项输出 `NOT_READY` 原因，不伪造 predicate；
- manifests 必须能通过 `parallel/PROSPECTIVE_VALIDATOR` schema/loader validation；
- 输出中文 `清单.txt` + machine-readable index JSON。

## 不做

- 不新采集；
- 不改 Alpha；
- 不自动跑真人 Browser；
- 不自动晋级 production；
- 不把 retrospective/discovery 重新标成 prospective。

## Stop condition

`BETA PROSPECTIVE MANIFEST SET READY`

如果 Beta triage 尚未达到 READY，则先兼容已有 queue schema，并明确等待，不要猜。
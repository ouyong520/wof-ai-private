# WOF-052L Analysis -> Prospective Validator Automatic Handoff — Fresh Start Prompt

你负责把已经 READY 的 WOF-052L 自动分析器和 Prospective Validator Framework 真正拼起来。

读取：
- `parallel/WOF052L_ANALYSIS/**`
- `parallel/PROSPECTIVE_VALIDATOR/**`
- `parallel/WOF052L_RECORDER/**`
- `parallel/BROWSER_FLEET/**`
- 当前 T18 BODY4728 ambiguity 权威证据
- `parallel/PM/BETA_RULE_CANDIDATE_TRIAGE_START_PROMPT.md`

写入范围：仅 `parallel/WOF052L_PROSPECTIVE_HANDOFF/**`。

## 目标

当长采集分析器判定：
- T18 判别已解决；
- A4704/A4712 两边都有足够支持；
- 找到满足门槛的 ordered tail2/tail3/pair/triple；

则自动：
1. 从 `analysis.json` 生成 research-only candidate manifest；
2. 冻结 manifest SHA/timestamp；
3. 明确 discovery corpus 与 prospective corpus 分离；
4. 调用现有 Prospective Validator Framework；
5. 使用 Browser Fleet 做多房间 prospective；
6. 输出中文状态和一个机器 JSON。

如果分析仍不足，必须停止在 `WAITING_FOR_MORE_DISCOVERY_EVIDENCE`，绝不能凭 single state 生成 A4704-specific production candidate。

## 安全/证据边界

- discovery 不能冒充 prospective；
- prospective 不能自动晋级 production；
- T18 BODY4728 single state 永远保持 attack-ambiguous；
- candidate manifest 只能来自分析器明确输出的 ordered discriminator；
- readOnly=true / ramWrites=0 / no input injection；
- no product Alpha modification；
- no Validator core rewrite；
- no Recorder core rewrite。

## Stop condition

`AUTOMATIC DISCOVERY -> PROSPECTIVE HANDOFF READY`

以后长采集数据一够，链路应自动进入 prospective，不再等 PM 开一个人工转换帖。
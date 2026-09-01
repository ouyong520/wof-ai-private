# WOF-052L -> Prospective Handoff — Fresh Independent QA Start Prompt

你负责 `parallel/WOF052L_PROSPECTIVE_HANDOFF/**` 的 fresh independent QA。

这是独立 QA。不要修改 Handoff、Analyzer、Prospective Validator、Recorder、Browser Fleet 或 Alpha 核心实现。

## 读取

- `parallel/WOF052L_PROSPECTIVE_HANDOFF/**`
- `parallel/WOF052L_ANALYSIS/**`
- `parallel/PROSPECTIVE_VALIDATOR/**`
- `parallel/PM/WOF052L_TO_PROSPECTIVE_HANDOFF_START_PROMPT.md`
- WOF-051 / WOF-052 关于 T18 BODY4728 ambiguity 的权威结论
- World 921031 黄金 SHA-256 requirement

## 写入范围

仅：
- `parallel/WOF052L_PROSPECTIVE_HANDOFF_QA/**`

不允许修改任何被测核心实现。

## QA 目标

独立证明这条自动链不会因为自动化而破坏证据等级：

`discovery -> ordered discriminator -> research-only candidate -> freeze -> fresh prospective`

重点必须验证：

1. evidence 不足时只返回 `WAITING_FOR_MORE_DISCOVERY_EVIDENCE`；
2. evidence 不足时绝不创建 candidate manifest；
3. `exact_final` / `tm_final` / single-state feature 永久不能自动转 prospective rule；
4. T18 BODY4728 single-state ambiguity 不能被包装成 A4704-specific rule；
5. candidate 必须来自 Analyzer 明确的 exclusive ordered discriminator；
6. `oppositeSupport > 0` 必须拒绝；
7. wrong World / wrong SHA / wrong schema / unsafe flags 必须 fail closed；
8. discovery corpus 不能计入 prospective evidence；
9. manifest freeze 前后 canonical SHA 一致；
10. freeze 后 mutation 必须拒绝；
11. prospective session 必须发生在 handoff freeze 之后；
12. live Validator 实际使用的 candidate SHA 必须与 handoff frozen SHA 一致；
13. multi-room prospective evidence 必须保持 room/session isolation；
14. prospective PASS 仍必须是 research-only，绝不自动 production promotion；
15. owner-facing正常路径简体中文；
16. readOnly=true / ramWrites=0 / inputInjection=false / no Worker replacement。

## 测试要求

尽量使用 fixture / mock / frozen corpus 做独立验证，不要求 owner 真人 Browser，也不要等待 10-room 长采集。

至少覆盖：
- insufficient corpus；
- exact tail2 valid candidate；
- TM* tail3/triple valid candidate；
- single-state rejection；
- opposite-support rejection；
- wrong identity；
- mutation after freeze；
- pre-freeze evidence exclusion；
- post-freeze prospective inclusion；
- candidate SHA mismatch；
- production promotion rejection；
- two-room isolation。

## Stop condition

只能给出以下之一：

`PASS — AUTOMATIC DISCOVERY TO PROSPECTIVE HANDOFF QA`

或者：

`BLOCKED — P0/P1 <精确问题>`

若发现 P0/P1，只记录，不修；由 PM 再开 fresh fix stage。

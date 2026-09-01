# WOF Beta Rule Candidate Triage — Fresh Start Prompt

你负责一个不阻塞 Alpha、但提前加速 Beta 的并行线：只消费现有证据，整理下一批最值得验证的 Future Danger rule candidates。

读取现有：
- WOF-047/049/050/051/052 报告与结果
- `parallel/SEQMINER/**`
- `parallel/COVERAGE/**`
- `parallel/SWEEPATLAS/**`
- `parallel/RAWMINE/**`
- `parallel/EFIELD/**`
- 当前 Alpha rules manifest / freeze spec（只读）

写入范围：仅 `parallel/BETA_TRIAGE/**`。

目标：
- 不做新采集；
- 不修改 Alpha；
- 不自动晋级任何 production rule；
- 把现有证据按“用户价值 × 覆盖频率 × 预测强度 × 验证成本”排序；
- 明确哪些已经够做 prospective validator；
- 明确哪些仍需要 ordered sequence；
- 明确哪些应该永久放弃/低优先；
- 规范 T<decimal>(0xHH) 类型记法，避免 T18/T12 等历史混淆；
- 输出 Top 10 下一步 Beta validation queue；
- 每项给出最小 prospective test 设计；
- 标注能否利用即将进行的 WOF-052L 10-room long capture 顺手覆盖；
- 所有结论基于已有数据，不要求用户重新大规模采集。

重点保留：T18 BODY4728 ambiguity 必须 ordered context，不能把 single state 当 A4704-specific rule。

停止条件：`BETA VALIDATION QUEUE READY`。

不改 `product/alpha/**`，不写 RAM，不注入输入。
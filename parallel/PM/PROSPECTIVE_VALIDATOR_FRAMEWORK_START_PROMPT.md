# WOF Prospective Validator Framework — Fresh Start Prompt

你负责 WOF 项目新的独立加速线：Prospective Validator Framework。

仓库：
- `ouyong520/wof-ai-private`

开始前重新读取：
- `parallel/PM/PARALLEL_EXECUTION_BOARD.md`
- `parallel/PM/WOF052L_ANALYSIS_AUTOMATION_START_PROMPT.md`
- `parallel/WOF052L_RECORDER/**`
- 当前 WOF-051 / WOF-052 / T18 / T23 报告与候选规则资料

## 目标

提前建立一个通用、只读、可复用的 prospective validation 框架，让 WOF-052L 或其他分析线一旦给出候选 ordered sequence，就不需要再新写一套验证器。

框架必须能够：
- 读取一个候选规则 JSON/manifest；
- 支持 ordered state tail2 / tail3 / pair / triple 条件；
- 支持 current-level predicate；
- 支持 target / side / retarget 元数据；
- 支持多房间并行；
- 自动统计 signal / strict / jitter / late / hard miss / censored；
- 自动区分 discovery evidence 与 prospective evidence；
- 自动生成紧凑 result JSON；
- 任何候选默认 research-only，不自动晋升 production；
- 可以直接消费未来 WOF-052L analysis 输出；
- 能复用 Browser Fleet / localhost CDP，但不得修改它们。

## 安全边界

- read-only；
- ramWrites=0；
- no gameplay input injection；
- 不替换 `window.Worker`；
- 不修改 `product/alpha/**`；
- 不修改 `parallel/PYLAUNCH/**`；
- 不修改 `parallel/WOF052L_RECORDER/**`；
- 不扩展攻击研究本身，只做验证基础设施；
- 不把 T18 BODY4728 单状态直接当 A4704-specific 规则。

## 优先测试

用已有 corpus/mock 数据证明框架至少能表达：
1. T18 BODY4728 歧义候选的 ordered tail；
2. T23 A5888 BODY4936 tail3；
3. 一个简单 current-level predicate。

## 停止条件

做到：未来分析线一旦产出一个候选 manifest，新的 prospective validation 执行帖只需要提供候选文件，不需要重新开发验证器。

最终写回独立目录（建议 `parallel/PROSPECTIVE_VALIDATOR/**`）及 RESULT.md。
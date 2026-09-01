# WOF Repository Regression Orchestrator — Fresh Start Prompt

你负责 WOF 项目新的独立加速线：Regression Orchestrator / 全仓库回归编排器。

仓库：`ouyong520/wof-ai-private`

## 目的

当前 Browser Fleet、PYLAUNCH、WOF-052L、Owner Toolkit、中文 UX、Evidence Ingestor、Project Status、Prospective Validator 等并行线快速变化。各 lane 自测 PASS 不等于组合后一定 PASS。

你的任务不是改这些组件，而是建立一个统一的一键回归入口，把当前可离线/CI 运行的测试全部串起来并生成一个统一结果。

## 写入范围

仅 `parallel/REGRESSION_ORCH/**`，必要时可新增独立 GitHub Actions workflow。
不要修改各组件核心实现。
不要修改 `product/alpha/**`。

## 必须发现并编排

优先自动发现并运行当前存在的：
- PYLAUNCH discovery/proof tests；
- Browser Fleet tests；
- WOF-052L self-test / Fleet tests；
- Prospective Validator tests；
- Owner Chinese UX tests；
- Owner One-Click package tests；
- Operator Toolkit tests；
- Evidence Ingestor tests；
- Project Status Scanner tests；
- Alpha RC5 product regression / independent QA harness（只运行现有 harness，不修改 Alpha）。

未来新 `parallel/**/tests` 可尽量自动发现，但禁止盲目执行任意不可信脚本；使用明确 allowlist/manifest。

## 输出

一键中文入口，例如：
`parallel/REGRESSION_ORCH/RUN_ALL_REGRESSION.cmd`

生成：
- `REGRESSION_SUMMARY.json`
- `回归结果.txt`

每个 suite 显示：PASS / FAIL / SKIPPED / BLOCKED、耗时、失败命令/日志位置。

总结果规则：
- 一个安全关键 suite FAIL => overall FAIL；
- 缺少仅真人环境可跑的 proof => BLOCKED/NOT_RUN，不伪报 PASS；
- 单个测试崩溃不能阻止其他 suite 收集结果；
- 所有 owner-facing 文字简体中文。

## 安全

- read-only；
- ramWrites=0；
- no gameplay input injection；
- no Worker replacement；
- 不自动进入游戏；
- 不做真人 Browser 证明；
- 不修改生产规则。

## Stop condition

**REGRESSION ORCHESTRATOR READY**：一条命令/双击即可得到当前全仓库离线回归汇总，后续 PM/QA 不需要逐目录手工跑测试。
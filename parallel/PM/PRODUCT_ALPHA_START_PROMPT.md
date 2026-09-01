# PRODUCT / ALPHA Implementation Thread Bootstrap

Use this as the bootstrap for one bounded product-engineering thread.

```text
你负责 WOF / Warriors of Fate / 三国志II Future Danger AI 的 PRODUCT / ALPHA 实现工作流。

仓库：
- ouyong520/wof-ai-private
- ouyong520/wof-winkawaks-bridge

开始前必须读取：
- wof-ai-private/WOF_AI_CURRENT_FRONTIER.md
- wof-ai-private/WOF_AI_MASTER_PROGRESS.md
- wof-ai-private/parallel/PM/README.md
- wof-ai-private/parallel/PM/ALPHA_FREEZE_SPEC.md
- wof-ai-private/parallel/PM/ALPHA_ENGINEERING_TASKS.md
- wof-ai-private/parallel/PM/RELEASE_READINESS.md
- wof-ai-private/parallel/PM/RISK_REGISTER.md

并只读审计当前：
- wof_canvas_hud.js
- production-shadow / danger-map / HUD bridge 相关 Browser 文件
- 最新 WOF-0xx coordinator / resume 文件，仅用于提取已经审计过的 production predicate 与 target/retarget 逻辑

你的职责不是继续研究攻击规则，不是重新做 GEO/EFIELD/RAWMINE/SEQMINER，也不是创建 Collector。

唯一目标：把现有高证据 production-shadow 子集做成一个保守、只读、fail-closed、普通用户可以加载的 Alpha Release Candidate。

严格按 parallel/PM/ALPHA_ENGINEERING_TASKS.md 的 A1→A10 顺序执行。

原则：
- production 与 experimental/discovery 必须隔离；
- T18 BODY4728/A4/B2/TM1 不得作为 A4704-specific production rule；
- T16 B4 只能按 danger rule 表达，不得宣称 A6432-exclusive；
- UNKNOWN 必须沉默；
- live target 必须持续 reread，并正确处理 retarget；
- 不写游戏 RAM，不自动输入；
- unsupported runtime/build 必须 fail closed；
- 优先复用现有 HUD/runtime assets，不重造已经存在的东西；
- release regression 必须针对最终 release artifact，而不是仅针对 research coordinator。

写入范围：
- 优先创建独立的 product/** 发布目录；
- 不修改 parallel/其它研究 lane；
- 若必须读取 WOF-0xx，只读；
- 不擅自 promotion 新研究候选。

持续推进直到：
- Alpha RC 形成，或
- 只剩必须真人 Browser acceptance 的 gate。

只有真的需要项目所有者真人操作时才停止并给出一条具体操作。
```

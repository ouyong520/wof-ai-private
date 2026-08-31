# RAWMINE — New Thread Prompt

你负责 WOF 的 RAWMINE 并行线。

先读取：
- `WOF_AI_HANDOFF.md`
- `PARALLEL_RESEARCH.md`
- `COLLECTOR_ROUTING.md`
- bridge `docs/COLLECTOR_V1_CONTRACT.md`
- `parallel/RAWMINE/START_HERE.md`
- `parallel/RAWMINE/CANDIDATE_FRONTIER.md`
- 最新 `parallel/GEO/**`、`parallel/EFIELD/**`（只读）

你的工作：RAWMINE 只做 GEO/EFIELD 的自动候选筛选与证据分析，不自己给字段定最终语义。

对已有 raw 自动输出：offset change frequency、zero/nonzero 边沿、值域、U8/U16/U32 最小合理宽度、同帧/邻帧联动、event window、pair/cluster correlation，以及每个具体问题的 Top 10 候选 offset。

优先继续当前问题：
- GEO P1 X / Y 候选筛选
- EFIELD execution-boundary companion
- EFIELD retarget precursor

结果只写 `parallel/RAWMINE/**`；不要改 GEO/EFIELD 文件、Browser 主线、production-shadow，也不要写游戏内存。

我发“继续”时，直接检查最新 GitHub/raw/result，自动推进并更新 RAWMINE 候选报告，不要停下来问我搬日志或 JSON。

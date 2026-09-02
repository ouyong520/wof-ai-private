# Alpha V1.0.0 Current-HEAD Release Gate Preflight — Start Prompt

stageId: `ALPHA_V1_0_0_CURRENT_HEAD_RELEASE_GATE_PREFLIGHT_V1`
dedupProtocol: `v2`
dedupKey: `alpha.v1.0.0.current-head-release-gate-preflight`
dedupMode: `exclusive`

你这次负责 **Alpha V1.0.0 Current-HEAD Release Gate Preflight**。

目标：基于当前 `main` 重新核对 V1.0.0 玩家测试版全部 release gate，把仍未关闭的 blocker 压成一张最短、可执行清单。只做 repository / GitHub evidence reconciliation；不要修改 production implementation，不启动 Browser/WOF，不把 synthetic QA 当成真实 non-drift proof。

必须重新读取并核对：

- 当前 `main` HEAD 与近期相关 commits；
- `parallel/PM/PM_CORE_OPERATING_CHARTER.md`；
- `parallel/PM/STAGE_DEDUP_GUARD.md`；
- `parallel/PM/STAGE_CLAIMS/**` 与相关 canonical claims；
- Player-head strict `warningSampleAt` fix + Fresh QA V2 RESULT/claim；
- Enemy target head labels 最新 Fresh QA V3 RESULT/claim；
- `ALPHA_V1_ANCHORED_OVERLAYS_ONE_SESSION_LIVE_PROOF_TOOLING_V1` 当前状态；
- Alpha V1 anchored overlays live-proof prep/result；
- V1.0.0 user-test release prep RESULT/claim；
- Alpha Acceptance 当前 superseding/current-head gate 结果；
- Alpha Transport true 5h endurance / recovery V2 的 workflow run、artifact/result/claim 当前事实；
- 当前 release freeze / finalization checklist。

特别要求：

1. 对 5h endurance 不接受聊天口头 PASS，也不机械继承旧 BLOCKED；直接按当前 GitHub workflow/result/claim durable evidence 判定。若 run 已成功但 claim/result 未收口，要明确分类为“evidence exists, durable closure pending”；若 API 仍显示 queued/null，则明确写出证据冲突，不能自行宣告 PASS。
2. Player-head QA V2 已有后续提交时，必须按当前 durable RESULT/claim 判定，不沿用旧 QA BLOCKED。
3. One-Session Live-Proof Tooling 若仍 ACTIVE，不得抢占、修改或替代该 stage；只记录它对最终 Browser/WOF proof 的依赖关系。
4. 真实 Browser/WOF dynamic non-drift proof 未完成时，V1.0.0 必须保持 `NOT RELEASED`。
5. 输出必须区分：`CLOSED`、`ACTIVE/PENDING`、`BLOCKED`、`OWNER ACTION REQUIRED`，并给出从当前 HEAD 到 V1.0.0 player-test release 的最短串行路径。
6. 若发现除 live proof / 5h durable closure 外还有新的 P0/P1 gate，必须给出精确文件/commit/claim 证据；不要创造 filler work。

最终写入一个 durable RESULT，明确给出类似：

- `PASS — V1.0.0 REPOSITORY PREFLIGHT CURRENT; RELEASE STILL NOT ADMITTED UNTIL <remaining gates>`；或
- `BLOCKED — <precise unresolved repository gate>`。

仓库：
`ouyong520/wof-ai-private`

开始前严格执行 canonical dedup v2：先重新读取当前 `main`、等价 RESULT / claims / canonical claims；若等价工作已完成则 `ALREADY COMPLETE — SAFE TO CLOSE`。否则创建并重新读取 canonical claim，验证 exact `claimToken` 后再创建 stage claim并开始工作。任何 create/verification 失败都 fail-closed 停止。

持续执行到 `PASS / BLOCKED / duplicate stop`。
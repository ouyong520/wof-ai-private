# WOF Training Farm R0.1 — Stable-Retro + FBNeo Bootstrap

stageId: `TRAINING_FARM_R0_1_STABLE_RETRO_FBNEO_BOOTSTRAP_V1`
dedupProtocol: `v2`
dedupKey: `training.farm.r0.1.stable-retro-fbneo-bootstrap`
dedupMode: `exclusive`

你这次负责 **WOF Training Farm R0.1 Stable-Retro + FBNeo 最小 bootstrap**。

这是与 Alpha V1.0.0 完全隔离的内部 R&D accelerator。目标不是训练 AI，也不是改玩家产品，而是把我们刚确定的开源底座落成一个最小、可继续二次开发的仓库实现。

只做窄 scope：

- 以 `Stable-Retro + FBNeo` 为首选底座，不从零写模拟器；
- 建立薄 WOF adapter / host 边界，至少明确并实现可测试接口形状：`reset / step / read_ram / save_state / load_state`；
- 输入必须走 emulator/core API，不使用全局键盘焦点注入；
- 为 WOF ROM 使用本地外部路径/环境变量入口，绝不提交 ROM、BIOS、受版权保护游戏数据或第三方二进制；
- 加依赖/环境 probe，明确 Windows/Linux 的最小启动前置条件和失败原因；
- 加 deterministic repository smoke：在没有 WOF ROM 时也能验证 adapter 边界、配置、错误处理与 state API contract；
- 如果执行环境合法提供了 WOF ROM，可额外做 one-instance runtime probe，但不得把缺 ROM 误判成实现缺陷；
- 不上 PPO/SB3，不做 10 worker，不做训练策略，不做 safe-route search；
- 不修改 `product/alpha/**`、Transport、HUDANCHOR、Browser/WOF release proof、V1 release gates；
- 本 stage 不能声称 Training Farm R0.1 已完整达到真实 WOF deterministic proof，只能在真实 one-instance runtime 未验证时标为 `BOOTSTRAP READY FOR LOCAL WOF PROOF`。

仓库：
`ouyong520/wof-ai-private`

必须读取：

- `parallel/PM/WOF_TRAINING_FARM_OPEN_SOURCE_BASELINE_DECISION.md`
- `parallel/PM/PRODUCT_VERSION_ROADMAP.md`
- `parallel/PM/STAGE_DEDUP_GUARD.md`

建议新增内容保持在独立目录，例如：

- `training/farm/**` 或等价隔离路径；
- `parallel/TRAINING_FARM_R0_1/**` 用于 fixture / RESULT / smoke evidence。

完成标准：

1. repo 中存在可复用的薄 adapter/host bootstrap，而不是只有设计文档；
2. 无 ROM 情况下有确定性的配置/contract/error-path smoke；
3. 不把 Stable-Retro/FBNeo 大仓库 vendor 进来；
4. 不修改 Alpha production；
5. 记录实际 dependency/version assumptions、测试命令、PASS/限制；
6. 输出 `parallel/TRAINING_FARM_R0_1/RESULT.md`。

成功停止：

`COMPLETE — TRAINING FARM R0.1 STABLE-RETRO/FBNEO BOOTSTRAP — READY FOR LOCAL WOF ONE-INSTANCE PROOF`

如果发现 Stable-Retro 当前 FBNeo Arcade 路径无法满足 RAM/state/frame/input 基础能力，或仓库约束使最小 bootstrap 不可成立，则：

`BLOCKED — TRAINING FARM R0.1 BOOTSTRAP — <precise blocker>`

严格执行 canonical dedup v2：先重新读取当前 `main`、相关 RESULT/STATUS、`STAGE_CLAIMS/**` 和 canonical claim；先 create-only canonical claim、重新读取验证 exact `claimToken`，再建 stage claim，之后才开始 implementation。持续到 COMPLETE / BLOCKED / duplicate stop。

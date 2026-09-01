# WOF Alpha Safe Transport Mock Harness Prep — Fresh Start Prompt

你负责下一阶段 Alpha Safe Transport Integration 的独立 mock/test harness 预备线。

重要：当前真人 PYLAUNCH Windows proof 还没有重新 PASS，因此**禁止修改或实现 `product/alpha/**` transport**，也禁止修改 `parallel/PYLAUNCH/**` 主实现。

开始前读取：
- `parallel/PM/ALPHA_SAFE_TRANSPORT_INTEGRATION_CONTRACT.md`
- `parallel/PM/ALPHA_SAFE_TRANSPORT_INTEGRATION_START_PROMPT.md`
- RC5 QA / regression 结果
- 当前 Alpha core/bootstrap/HUD 测试结构（只读）
- 最新 PYLAUNCH RESULT（只读）

写入范围：新目录，例如 `parallel/ALPHA_TRANSPORT_MOCK/**`。

目标：提前把 future transport implementation 所需的 mock vectors / fixtures / result schema / regression harness 做好，让真人 PYLAUNCH proof 一 PASS，集成工程帖可以直接写实现并跑完整测试，而不是再花时间搭测试框架。

必须覆盖合同中的核心向量：
- valid session + pairGeneration + pairNonce；
- wrong session ignored；
- old generation ignored；
- wrong nonce ignored；
- valid diag immediate warning clear；
- ordinary stale 1500ms / silent at 1501ms；
- rebind immediately revokes old authority；
- Worker/runtime epoch replacement；
- exact World 921031 dual identity gate；
- wrong SHA fail closed；
- no HUD load before first valid current-pair state；
- first valid state may pair/load HUD；
- multi-warning aggregation；
- same-type slot replacement no inheritance；
- target/side/UNKNOWN safety；
- detector tick backpressure: max one in flight / no catch-up queue；
- disconnect/reconnect fresh pair；
- readOnly=true / ramWrites=0 / inputInjection=false；
- no Worker replacement/Blob URL rewrite。

要求：
- fixtures 与 expected results 机器可读；
- 能被未来 integration stage 直接复用；
- 不复制/改写生产 warning predicates；
- 不新增攻击规则；
- 不声称 transport 已实现；
- 最终产出一个明确 `RESULT.md`，状态应为 `MOCK HARNESS READY — WAITING FOR REAL PYLAUNCH PROOF / TRANSPORT IMPLEMENTATION`。

安全边界：
- no product/alpha changes
- no PYLAUNCH implementation changes
- no RAM writes
- no input injection
- no Worker replacement

停止条件：mock harness / fixtures / expected results 全部仓库侧 PASS，可直接交给下一 fresh Alpha transport implementation stage。

# WOF Unified Windows Live Proof — Fresh Independent QA Start Prompt

你负责全新的独立 QA。不要复用开发帖结论，不修改核心实现。

开始前重新读取最新：
- `parallel/LIVE_PROOF_BUNDLE/**`
- `parallel/PYLAUNCH/**` 当前 RESULT / Discovery V2
- `parallel/BROWSER_FLEET/**` 当前 RESULT / Discovery V2
- `parallel/WOF052L_RECORDER/**` 当前 RESULT / Discovery V2
- `parallel/PM/CHINESE_UI_UX_REQUIREMENT.md`
- `parallel/PM/ALPHA_SAFE_TRANSPORT_INTEGRATION_CONTRACT.md`

目标：在 owner 真人运行前，独立判断 `RUN_WOF_UNIFIED_LIVE_PROOF.cmd` 是否真的适合作为一次合并真人 Proof。

必须独立验证：
1. 只需要一个 owner 入口；不要求 Git、DevTools、Worker Console、粘 JS。
2. Fleet Worker 只能是 cheap indicator，不能冒充 World identity authority。
3. PYLAUNCH 必须作为 Worker/WASM/heap/World 921031 权威证明。
4. Recorder Discovery V2 admission 必须独立成立。
5. exact World 921031 SHA-256 gate 保持：`5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62`。
6. `readOnly=true / ramWrites=0 / inputInjection=false / no Worker replacement`。
7. 任一子项失败时总结果 fail closed，但保留已取得证据和精确 blocker。
8. 不能把 repository/CI PASS 当成真人 live PASS。
9. 不能自动开始 10-room long capture。
10. owner-facing 正常流程默认简体中文，错误第一层中文、技术详情第二层。
11. 只在所有自动项通过后询问一次“当前 WOF 房间是否仍能正常运行？Y/N”。
12. 最终只需要 owner 返回一个 JSON 或一张最终状态截图。
13. direct-download / fresh install / Chinese path / spaces / rerun / stale cache 相关路径不要明显失效。

允许：
- 新增独立 QA 目录、fixtures、mock、静态/离线测试、QA 报告。

禁止：
- 修改 `parallel/LIVE_PROOF_BUNDLE/**` 核心实现；
- 修改 PYLAUNCH / Browser Fleet / Recorder；
- 修改 `product/alpha/**`；
- RAM write、输入注入、Worker replacement、攻击研究扩展。

如果发现 P0/P1，写出精确 blocker，停止并要求 fresh fix stage；不要自己修。

停止条件只能是：
- `PASS — READY FOR ONE OWNER UNIFIED WINDOWS/WOF PROOF`
或
- `BLOCKED — P0/P1 <precise blocker>`

把最终结果写回 GitHub。
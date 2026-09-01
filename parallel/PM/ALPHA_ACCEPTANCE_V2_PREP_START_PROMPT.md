# WOF Alpha Transport-Aware Browser Acceptance Prep — Fresh Start Prompt

你负责未来 Alpha Safe Transport Integration 完成后的 Browser Acceptance 预备线。

现在不要修改 `product/alpha/**`，不要假装 transport 已经实现。

读取：
- `parallel/PM/ALPHA_SAFE_TRANSPORT_INTEGRATION_CONTRACT.md`
- `parallel/PM/ALPHA_SAFE_TRANSPORT_INTEGRATION_START_PROMPT.md`
- `parallel/ALPHAACCEPT/**`
- RC5 QA PASS
- 当前 PYLAUNCH / Browser Fleet / Toolkit 现状
- 中文 UX 要求

写入范围：`parallel/ALPHAACCEPT/**`，但只做验收工具/fixture/结果 schema/操作流程准备，不改产品 Alpha。

目标：让 future transport integration 一旦 offline PASS，真人 Browser Acceptance 不需要重新设计流程。

必须提前准备：
- transportVersion / session / pairGeneration / pairNonce 验收字段；
- page/Worker/WASM/World 921031 状态；
- detector-local identity accepted；
- HUD first valid current-pair state；
- stale 1500ms；
- diag immediate clear；
- reconnect/rebind fresh pair；
- old generation/nonce rejected；
- gameplay fail-open；
- readOnly=true / ramWrites=0 / inputInjection=false；
- room remains playable；
- 一份最终 compact acceptance JSON；
- 简体中文 owner 操作界面/提示。

目标 UX：未来用户只做一次最小操作，工具自动产出一个 JSON，QA/PM直接判断 PASS/FAIL。

不要要求 DevTools、Worker Console、粘 JS。
不要增加攻击研究。
不要修改 WOF-052L。

停止条件：`ACCEPTANCE PREP READY — WAITING FOR TRANSPORT INTEGRATION`。
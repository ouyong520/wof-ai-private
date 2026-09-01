# WOF-052L Analysis -> Prospective Automatic Handoff

状态：**AUTOMATIC DISCOVERY -> PROSPECTIVE HANDOFF READY（仓库侧）**。

这条线把已经 READY 的 `parallel/WOF052L_ANALYSIS/**` 和 `parallel/PROSPECTIVE_VALIDATOR/**` 自动拼接起来，不修改 Analyzer core、Validator core、Recorder core、Browser Fleet core，也不修改 `product/alpha/**`。

## 最短使用方式

双击：

```text
RUN_WOF052L_TO_PROSPECTIVE_HANDOFF.cmd
```

工具会持续执行：

```text
WOF-052L Recorder 保存目录
-> 自动刷新 WOF052L_ANALYSIS/analyzer.py
-> 读取 analysis/analysis.json
-> 不足：WAITING_FOR_MORE_DISCOVERY_EVIDENCE
-> 足够：从 analyzer 明确输出的 ordered discriminator 生成 research-only manifest
-> 冻结 manifest SHA-256 + handoff timestamp
-> 调用现有 PROSPECTIVE_VALIDATOR/live_validator.py
-> 使用默认 Browser Fleet instances.json / localhost CDP discovery
-> 产生冻结后的新 live prospective corpus
```

因此未来 10-room long capture 一旦让 Analyzer 的 T18 判别达到保守门槛，不再需要 PM 人工开“把 discovery 候选转 prospective manifest”的转换帖。

## 硬门槛

Handoff 不自己发明候选，只消费 `analysis.json` 的：

```text
t18.verdict == resolved
t18.prospectiveValidator.worthEntering == true
t18.prospectiveValidator.candidate
```

并再次 fail closed 检查：

- `analysis.schema == wof-052l-analysis-v1`；
- A4704 / A4712 各自达到 Analyzer 的 `minCandidateCyclesPerOutcome`；
- World 仅为 `Warriors of Fate (World 921031)`；
- 黄金 SHA-256 必须为 `5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62`；
- `analysisReadOnly=true`；
- `ramWrites=0`；
- `inputInjection=false`；
- Analyzer 没有 `inputSafetyViolations`；
- BODY4728 single-state ambiguity guardrail 仍为 true；
- candidate 必须是 exclusive；
- `oppositeSupport == 0`；
- support 达到 Analyzer 的 `minExclusiveSequenceSupport`；
- feature 只能是 ordered `exact/tm tail2/tail3/pair/triple`。

`exact_final` / `tm_final` 永远不会被自动转换。即使有人手改 `analysis.json` 把 verdict 伪造为 resolved，single-state/final feature 仍会被 Handoff 拒绝。

## Candidate manifest

生成格式仍是现有 Validator 要求的：

```text
schema: wof-prospective-candidate-v1
promotion: research-only
identity: World 921031 + golden SHA-256
rule.sequence: tail2 / tail3 / pair / triple
rule.currentPredicates: type == 18
outcome.expectedAttacks: [4704] 或 [4712]
```

Analyzer 的 exact feature 转为 `signature` matcher；timer-normalized `tm_*` feature 转为 `family` matcher。Handoff 只转换 Analyzer 明确输出的 `pattern`，不从 single state 推测 A4704-specific rule。

Manifest 额外保留 discovery provenance：analysis SHA、analysis generatedAt、handoff freeze timestamp、feature、pattern、support、oppositeSupport、purity 以及 single-state guardrail。

## Discovery / prospective 隔离

边界固定：

- 用来发现 ordered discriminator 的 `analysis.json` 和历史 WOF-052L Recorder corpus 永远是 **discovery**；
- discovery 只允许生成 research-only manifest，不能满足 prospective gate；
- Handoff 在启动 live Validator 之前固定 manifest 内容和 canonical SHA-256；
- 启动前重新计算 canonical SHA，冻结后若 manifest 被改动则直接拒绝；
- 现有 `live_validator.py` 启动时再创建权威 prospective session，并记录同一个 candidate SHA + session `frozenAt`；
- Handoff 在 live corpus 结束后再次核对 Validator 实际 candidate SHA；不一致则报错；
- 只有该 session 启动后的 live evidence 才进入 `wof-prospective-corpus-v1`；
- live Validator 每个 Browser Fleet endpoint / Worker 独立验证；
- 即使 prospective result PASS，也仍是 `PROSPECTIVE_PASS_RESEARCH_ONLY`，不会自动晋级 production。

## 输出

默认 runtime 输出放在：

```text
%LOCALAPPDATA%\WOF Future Danger\ProspectiveHandoff\
```

其中：

```text
handoff_status.json
<candidate-id>.candidate.json
<candidate-id>.candidate.live_corpus.json
<candidate-id>.candidate.live_corpus.result.json
```

`handoff_status.json` 是 Handoff 的**唯一机器状态 JSON**，状态包括：

- `WAITING_FOR_MORE_DISCOVERY_EVIDENCE`
- `AUTOMATIC_DISCOVERY_TO_PROSPECTIVE_HANDOFF_READY`
- `PROSPECTIVE_VALIDATION_RUNNING`
- `PROSPECTIVE_VALIDATION_FINISHED`
- `HANDOFF_ERROR`

Console owner 状态默认简体中文。

## 等待状态

证据不足时工具只输出：

```text
WAITING_FOR_MORE_DISCOVERY_EVIDENCE
```

并列出 Analyzer 当前不满足的门槛。此状态下：

- 不生成 candidate manifest；
- 不启动 Validator；
- 不把 BODY4728 single state 当成 A4704-specific rule；
- 不要求用户人工转换 discovery evidence；
- 继续自然长采集即可。

## 手工/审计模式

只消费一个已有 analysis，不刷新 Analyzer：

```bat
py -3 handoff.py --analysis D:\WOF_CAPTURE\analysis\analysis.json --no-refresh-analysis --prepare-only
```

指定 Browser Fleet manifest：

```bat
py -3 handoff.py --watch --fleet-manifest "D:\path\instances.json"
```

自定义 runtime 输出：

```bat
py -3 handoff.py --watch --output-dir "D:\WOF_PROSPECTIVE_HANDOFF"
```

`--prepare-only` 只用于测试/审计；正常双击入口会在达到门槛后真正调用现有 live Validator。

## 离线回归

在本目录运行：

```bat
py -3 -m unittest -v test_handoff.py
```

覆盖：

- exact tail2 -> research-only manifest；
- TM* triple -> family matcher；
- insufficient -> WAITING；
- single-state/final feature 永久拒绝；
- opposite support 非 0 永久拒绝；
- wrong World identity 拒绝；
- insufficient 不落 candidate 文件；
- freeze timestamp 与 canonical manifest SHA 固定。

本实现提交前离线回归：**8/8 PASS**。

## 安全边界

固定：

- `readOnly=true`；
- `ramWrites=0`；
- `inputInjection=false`；
- `windowWorkerReplacement=false`；
- 不写游戏 RAM；
- 不创建游戏输入；
- discovery 不能冒充 prospective；
- prospective 不能自动晋级 production；
- 不修改 `product/alpha/**`；
- 不修改 Analyzer / Validator / Recorder / Browser Fleet core。

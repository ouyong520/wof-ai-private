# WOF-052L 自动分析器

这条工具线只负责“采完自动得结论”。它不修改 WOF-052L Recorder、不修改 `product/alpha/**`，也不会把研究候选自动晋级成生产规则。

## 最简单用法

直接双击：

```text
RUN_WOF052L_ANALYSIS.cmd
```

分析器会优先读取 Recorder 已经记住的保存目录：

```text
%LOCALAPPDATA%\WOF052LRecorder\settings.json
```

然后持续监控该目录。新的 per-room / merged / Browser Fleet merged JSON 出现或更新时，会自动刷新：

```text
<Recorder保存目录>\analysis\分析结果.txt
<Recorder保存目录>\analysis\analysis.json
```

按 `Ctrl+C` 停止监控。

## 一次性分析

```bat
python analyzer.py D:\WOF_CAPTURE
python analyzer.py D:\WOF_CAPTURE\runs\run_merged.json
python analyzer.py D:\A.json D:\B.json --output-dir D:\WOF_ANALYSIS
```

目录会递归扫描 JSON。若同一 run 同时存在 room JSON 和 merged JSON，主统计优先 merged，避免重复计数；room 文件只补 merged 没保存的 T23 trace 与 rare descriptor+attack detail。

## 自动输出内容

`分析结果.txt` 会直接给出：

- `T18 判别：已解决 / 仍不足`
- candidate 支撑周期数
- A4704 / A4712 分布
- exact final / tail2 / tail3
- timer-normalized `TM*` final / tail2 / tail3
- exact 与 `TM*` ordered pair / triple
- candidate first / last lead min / median / max
- 目标 / 侧向 / 重定向稳定性
- 最强区分序列候选
- 是否值得进入新的前瞻验证器
- T18/T23 次级覆盖
- enemy type / attack frequency
- 0P/1P/2P/3P occupancy
- rare descriptor+attack

`analysis.json` 保存同一结论的机器可读版本，供 Toolkit、后续 validator 或项目状态扫描器消费。

## 保守判定规则

WOF-051 已经直接证明：

```text
S0/A4/B2|BODY4728|FE8b660|NX8b204|Vffff|TM1|P6C4736
```

同一个 exact single state 可以最终进入 A4704，也可以最终进入 A4712。因此本工具固定执行：

```text
single state 不能单独推进 A4704-specific rule
```

默认只有同时满足以下条件，`T18 判别` 才会输出 `已解决`：

1. candidate-containing T18 周期中，A4704 至少 2 个；
2. A4712 至少 2 个；
3. 找到至少支持 2 个周期、且对另一最终攻击 0 命中的 ordered tail/pair/triple；
4. 两类样本的目标 / 侧向稳定率为 100%；
5. 两类样本的重定向为 0（retarget-free rate = 1.0）；
6. 输入房间身份只包含 World 921031 黄金 SHA-256；
7. 输入安全元数据仍满足 read-only / `ramWrites=0` / no input injection。

达到 `已解决` 只代表“值得建立新的前瞻验证器”。它仍然**不会自动修改 Alpha 或生产规则**。

阈值可用于研究性重跑，但默认值保持保守：

```bat
python analyzer.py D:\WOF_CAPTURE --min-per-outcome 2 --min-sequence-support 2
```

## Browser Fleet

1、5、10+ 房间使用同一个分析器。Fleet merged 内嵌的 T18 candidate evidence 可以直接分析；如果 child merged / room 文件也在保存目录中，分析器会优先使用更完整的 child merged，并自动避免同一 candidate trace 重复计数。

## 离线自检

```bat
python analyzer.py --self-test
python -m unittest -v test_analyzer.py
```

自检覆盖：

- single state ambiguity guardrail；
- A4704/A4712 重复互斥 ordered sequence；
- target/side instability；
- World 921031 identity gate；
- merged/room 去重与 T23/rare detail 补全；
- T18 零覆盖必须输出“仍不足”。

## 安全边界

固定：

- 离线 JSON 分析；
- `readOnly=true`；
- `ramWrites=0`；
- `inputInjection=false`；
- 不启动或修改游戏 Worker；
- 不修改 Recorder 采集逻辑；
- 不修改 `product/alpha/**`；
- 不做生产规则自动晋级。

# WOF-052L Automatic Analysis — Fresh Start Prompt

你负责 WOF-052L 的独立并行分析工具线。

Recorder 负责采；你负责“采完立刻自动得结论”。不要修改 Recorder 采集逻辑。

读取：
- `parallel/WOF052L_RECORDER/**`
- `reports/WOF-052_ANALYSIS.md`
- WOF-051/WOF-052 已有证据
- T18 BODY4728 ambiguity authoritative notes
- 当前 WOF-052L 输出 schema

写入范围：仅 `parallel/WOF052L_ANALYSIS/**`。

目标：
- 自动读取一个或多个 per-room / merged / fleet merged JSON；
- 自动统计 T18 BODY4728/A4/B2/TM1 candidate；
- 分别统计最终 A4704 / A4712；
- 自动计算 exact tail2/tail3；
- 自动计算 timer-normalized TM* tail2/tail3；
- 自动统计 ordered pairs/triples；
- 自动计算 candidate first/last lead；
- 自动检查 target/side/retarget stability；
- 自动判断证据是否仍然不足；
- 禁止仅凭 single state 推进 A4704-specific rule；
- 同时输出 secondary coverage：T18/T23、type/attack frequency、occupancy、rare descriptor+attack；
- 自动生成中文 `分析结果.txt` + 机器可读 `analysis.json`；
- 对 1、5、10+ 房间都适用；
- 可以持续监控保存目录，新 merged JSON 出现后自动更新结果；
- 所有用户可见提示默认简体中文。

要求最终当长采集结束后，不需要再开人工分析帖，脚本自己给出：
- `T18 判别：已解决 / 仍不足`
- 支撑样本数
- A4704/A4712 分布
- 最强区分序列候选
- 是否值得进入新的 prospective validator

不修改 `product/alpha/**`。
不修改 Recorder。
不做生产规则自动晋级。
read-only / no input injection。
# WOF Future Danger AI — CURRENT FRONTIER

更新时间：2026-08-31
仓库：`ouyong520/wof-ai-private`
项目：Project A — Browser / MAME / gstyphoon.js Future Danger

## 当前阶段
底层 selector / dispatcher / descriptor 已解决，不再重做。当前工作是扩大高可靠 Future Danger 攻击规则覆盖，并最终合成实时 danger map / safe path。

## 固定 ground truth
- P1 `0xFFBE1C`, P2 `0xFFBEFC`, P3 `0xFFBFDC`
- enemy pool `0xFFC0BC`, stride `0xE0`, slots 20
- player `+0x7C = 0/4/8`
- enemy `+0x7E = 0/4/8 → P1/P2/P3`，authoritative live target
- player pointer table `0x010CF8`
- `enemy+0x6A` 仅 supporting cache
- dispatcher incoming 44 edges 已完整
- descriptor consumer `0x247C` 已解析
- `enemy+0x70 U16 0→nonzero` 仅 ACTIVE-start convention，不是 exact hitbox/damage onset

## 已验证状态
- T16 exact B4 → attack6432：production-shadow；WOF-030 65/65 strict <=40ms，target/side 65/65 stable。
- T33/T34 exact TM6 → attack3232：production-shadow-candidates；WOF-032 prospective 全命中样本。
- broad T16 FAST/MID：已被 late/hard miss 否定。
- broad T30_FAST：WOF-032 8/10 strict + 2 hard miss，已降级。
- absDx130：仅旧 diagnostic split，不是 hitbox/range。
- T16 4840 divergence：discovery-only。

## WOF-034 discovery
WOF-034 adaptive mining 抓到 150 ACTIVE edges，并在 T24 上发现四条高质量 exact ~100ms TM2 fingerprints：
- `T24 S2/A2/B4 BODY5424 FE8AEEC NX8A6C6 V180001 TM2 P6C0` → eventual A5440，5/5 near100ms，target/side stable，LEFT+RIGHT。
- `T24 S2/A2/B4 BODY5440 FE8AF28 NX8A6DA V180001 TM2 P6C0` → eventual A5424，5/5 near100ms，target/side stable，LEFT+RIGHT。
- `BODY5440 FE8AF28 NX8A756 V100001 TM2` → A5424，4/4 near100ms，RIGHT-only discovery。
- `BODY5424 FE8AEEC NX8A76A V100001 TM2` → A5440，4/4 near100ms，RIGHT-only discovery。

这些仍是 discovery/correlation evidence。部分 T24 TM3/TM4 exact states 会同时出现在 eventual A5424/A5440 前，不能作为 attack-identity production rule。

## WOF-035 — latest completed run
身份严格通过：
```text
copyId=WOF-035
project=WOF-AI-PRIVATE
version=wof-future-danger-t24-exact-prospective-validator-v35
marker==== WOF FUTURE DANGER T24 EXACT PROSPECTIVE VALIDATOR V35 JSON ===
readOnly=true
ramWrites=0
```

运行：120001.4ms / 10ms；enemySamples=48326；ACTIVE edges=194。
main type samples：T23 993, T20 2221, T7 11684, T30 9773, T16 4453, T22 4453, T28 4453, T10 5561, T9 4735。
**T24 samples=0**。
因此四条 T24 exact candidates 均 rawMatchSamples=0、transitionEntries=0、signals=0、evaluable=0。
结论：WOF-035 对 T24 candidates **没有任何正/负证据**；不能因为 0 signals 降级候选。

值得利用的当前房间 attack coverage：
- T16|A6432 = 22，T16|A4832 = 2
- T30|A6200 = 10，T30|A2536 = 18，T30|A2528 = 6
- T7|A2536 = 25，T7|A2528 = 12
- T9|A3232 = 15，T10|A3232 = 17
- 另有 T22/T28 多种攻击

## Engineering correction after WOF-035
固定等 T24 再次造成 120 秒规则 coverage=0，虽然 active edges 很多。因此下一轮不再只等一个 type。恢复 adaptive miner，同时把所有已知高价值规则作为 opportunistic validators 嵌入。

## Current next
```text
resume version = wof-resume-dispatch-selector-v46
nextCopyId = WOF-036
nextScript = wof_future_danger_adaptive_terminal_miner_v36.js
nextMarker = === WOF FUTURE DANGER ADAPTIVE TERMINAL MINER V36 JSON ===
```

### WOF-036 design
120s / 10ms。
Opportunistic validators：
- T16 exact B4 production-shadow
- T33/T34 TM6 production-shadow-candidates
- 四条 T24 exact ~100ms prospective candidates

同时对所有真实 ACTIVE edge mining：
- last attack=0 terminal fingerprint
- 20/50/100/150/250/500ms pre-ACTIVE fingerprints
- recent pre-ACTIVE transition chain
- type + actual attack 聚合
- target stability / side stability

因此即使当前房间继续没有 T24，也能从 T7/T30/T16/T22/T28/T10/T9/T23/T20 得到有效 evidence。尤其当前 T16 A6432 coverage 很强，可顺带继续验证 exact B4。

## Evidence policy
- WOF-035 zero T24 coverage ≠ T24 rule failure。
- WOF-036 新挖出的 signature 仍只是 discovery/correlation evidence，不是 causal proof。
- 新候选必须另写 prospective validator，检查 strict / jitter / late / hard miss / expected attack / target stability / side stability 后才能升 production-shadow。

## Exclusions / do not redo
- 不重做 P1/P2/P3 identity、enemy+0x7E selector、player table、dispatcher 44 edges、descriptor consumer、Focus Multiroom、0x0080F2。
- 不称 +0x70 为 exact hitbox/damage onset。
- 不恢复 broad T16 FAST/MID、broad T30_FAST、absDx130 hitbox/range、T16 4840 divergence。
- 不把 mined fingerprint 直接当 causal proof。
- 不把 ambiguous T24 TM3/TM4 states 当 attack identity rule。

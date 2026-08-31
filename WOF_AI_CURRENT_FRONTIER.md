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

## WOF-033 lesson
固定 validator 在 T24/T18/T21/T30-heavy 房间里 291 ACTIVE edges 但所有 fixed exact match=0。结论是 coverage problem，不是 T16/T33/T34 rule failure。因此切换 coverage-adaptive mining。

## WOF-034 — latest completed run
结果身份严格通过：
```text
copyId=WOF-034
project=WOF-AI-PRIVATE
version=wof-future-danger-adaptive-terminal-miner-v34
marker==== WOF FUTURE DANGER ADAPTIVE TERMINAL MINER V34 JSON ===
readOnly=true
ramWrites=0
```

运行：120000.5ms / 10ms；enemySamples=28271；ACTIVE edges=150。
主要 type samples：T19 5041, T31 2537, T12 3057, T24 5685, T18 3276, T7 2807, T9 2096, T11 2744, T10 1028。
T24 attack coverage：A4704=13, A5440=13, A5424=9, A4712=6。

### T24 strongest discovery fingerprints
#### Candidate A — expected 5440
```text
T24
attack=0
state99=2 action2A=2 b2B=4
BODY5424 FE8AEEC NX8A6C6 V180001 TM2 P6C0
```
WOF-034 100ms fingerprint：5/5 eventual A5440；lead sampling约98.8..100.0ms；target/side stable 5/5；包含 LEFT+RIGHT。

#### Candidate B — expected 5424
```text
T24
attack=0
state99=2 action2A=2 b2B=4
BODY5440 FE8AF28 NX8A6DA V180001 TM2 P6C0
```
WOF-034 100ms fingerprint：5/5 eventual A5424；约99.1..100.1ms；target/side stable 5/5；包含 LEFT+RIGHT。

#### Candidate C — expected 5424
```text
BODY5440 FE8AF28 NX8A756 V100001 TM2
```
4/4 discovery near100ms；当前仅 RIGHT coverage。

#### Candidate D — expected 5440
```text
BODY5424 FE8AEEC NX8A76A V100001 TM2
```
4/4 discovery near100ms；当前仅 RIGHT coverage。

### Important ambiguity correction
不要把 WOF-034 中所有漂亮的 T24 TM3/TM4 countdown 直接提升。交叉查看 activeEdgeEvents 后发现，部分完全相同的 exact state 会同时出现在 eventual A5424 和 A5440 前，只是 lead 不同。例如部分 V180001 / V100001 TM3 状态具有 attack identity ambiguity。因此 WOF-035 只验证上面四条更早、在 WOF-034 sampled fingerprints 中保持单一 eventual attack 的 exact TM2 fingerprints。

## Current next
```text
resume version = wof-resume-dispatch-selector-v45
nextCopyId = WOF-035
nextScript = wof_future_danger_t24_exact_prospective_validator_v35.js
nextMarker = === WOF FUTURE DANGER T24 EXACT PROSPECTIVE VALIDATOR V35 JSON ===
```

WOF-035 parameters：120s / 10ms / horizon 140ms / jitter 15ms / tail 400ms。
必须输出每条 rule 的 signals/evaluable/strict/jitter/realLate/hardMiss/censored/expectedAttackRate/targetSameRate/sideStableRate/lead distribution/side coverage。

只有独立 prospective 通过后才能升级 production-shadow。

## Exclusions / do not redo
- 不重做 P1/P2/P3 identity、enemy+0x7E selector、player table、dispatcher 44 edges、descriptor consumer、Focus Multiroom、0x0080F2。
- 不称 +0x70 为 exact hitbox/damage onset。
- 不恢复 broad T16 FAST/MID、broad T30_FAST、absDx130 hitbox/range、T16 4840 divergence。
- 不把 WOF-034 mined fingerprint 当 causal proof；它是 discovery/correlation evidence。
- 不把 ambiguous T24 TM3/TM4 states 当 attack identity rule。

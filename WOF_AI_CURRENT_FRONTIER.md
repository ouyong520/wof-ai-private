# WOF Future Danger AI — CURRENT FRONTIER

更新时间：2026-08-31
仓库：`ouyong520/wof-ai-private`
项目：Project A — Browser / MAME / gstyphoon.js Future Danger

## 当前阶段
selector / dispatcher / descriptor 已解决。当前只做 Future Danger 规则扩展、跨 type 泛化和 forward prospective validation。

## Ground truth / exclusions
- enemy `+0x7E` authoritative target；P1/P2/P3 = 0/4/8
- `enemy+0x70 U16 0->nonzero` 仅 ACTIVE-start convention，不是 exact hitbox/damage onset
- T16 exact B4 = production-shadow
- broad T16 FAST/MID 已否定
- broad T30_FAST 已降级
- absDx130 不是 hitbox/range
- T16 4840 divergence 不是 production
- retrospective lag correlation 不能冒充 forward predictor

## WOF-037 — latest completed
身份严格通过：`WOF-037 / WOF-AI-PRIVATE / wof-future-danger-t20-t23-hybrid-prospective-validator-v37 / marker`；readOnly=true；ramWrites=0。
运行 120002.3ms / 10ms；40039 enemy samples；140 ACTIVE edges。

### T20 A5136 — promoted to production-shadow-candidate
Forward rule：`T20_5136_B0_TO_B255_700`
- 6 signals / 6 evaluable
- 6 strict / 0 jitter / 0 late / 0 hard miss
- expected A5136 = 6/6
- target stable = 6/6
- side stable = 6/6
- LEFT1 / RIGHT5
- lead 418.6, 458.6, 530.1, 647.8, 670.1, 680.1ms

=> 独立 prospective PASS，可升 `production-shadow-candidate`。
=> 由于 lead 418.6..680.1ms 较宽，只定义为 **coarse early warning**，不称精确 countdown。
=> entry absDx 182..306 与 lead 不呈稳定单调关系，禁止生成 distance threshold。

### T23/T20 A4792 narrow rules
WOF-037 中：
- T23 B0 entry = 0 entries
- T20 TM6->TM5 = 0 entries
- T20 TM3->TM2 = 0 entries
不是 hard miss，也不是 falsification；只是本轮 exact entry 没出现。优先级下降。

### 3232 descriptor-family discovery
WOF-037 fallback mining：

#### Family 867BA / 85ECE
Current T9 exact state：
`S2/A4/B2 | BODY2872 | FE867BA | NX85ECE | V100000 | TM6 | P6C2784`
3 retrospective ~100ms samples -> A3232；lead 99.8..100.6ms；target 3/3；side 2/3 stable。

Historical relation：T33 candidate 使用相同 descriptor/body/value/action/b2/payload + TM6，WOF-032 prospective 5/5 attack3232。

#### Family 8811E / 879E2
Current T11 exact state：
`S2/A4/B2 | BODY2872 | FE8811E | NX879E2 | V100000 | TM6 | P6C2784`
2 retrospective ~100ms samples -> A3232；lead 99.6..100.8ms；target/side 2/2。

Historical relation：T34 candidate 使用相同 descriptor/body/value/action/b2/payload + TM6，WOF-032 prospective 3/3 attack3232。

=> 现在的假设是 **descriptor family 可能比 enemy type 更基础**。但 WOF-037 当前证据对 T9/T11 仍是 retrospective discovery，所以必须 WOF-038 live-forward 验证。

## Current next
```text
resume = wof-resume-dispatch-selector-v48
nextCopyId = WOF-038
nextScript = wof_future_danger_descriptor_family_validator_v38.js
nextMarker = === WOF FUTURE DANGER DESCRIPTOR FAMILY VALIDATOR V38 JSON ===
```

## WOF-038 rules
- `T16_6432_B4_40` — production-shadow opportunistic
- `T20_5136_B0_TO_B255_700` — production-shadow-candidate reconfirmation
- `D867BA_3232_TM6_120` — type-agnostic descriptor-family prospective
- `D8811E_3232_TM6_120` — type-agnostic descriptor-family prospective
- T23 B0 prospective retained opportunistically
- four T24 exact TM2 prospective rules retained opportunistically

Descriptor-family rules只在 live forward **首次进入 exact TM6 state** 时 arm；不限制 enemy type。输出 `entryTypeCounts`，用于直接检查跨 T9/T11/T33/T34 等 type 的泛化。

同时保留 fallback terminal + 50/100/150/250/500ms mining，避免新房间无固定规则 coverage 时白跑；fallback 仍是 discovery/correlation。

## Do not redo / do not revive
- P1/P2/P3 identity / +0x7E selector / player table / dispatcher44 / descriptor consumer
- broad T16 FAST/MID
- broad T30_FAST
- absDx130 hitbox/range
- T16 4840 divergence
- ambiguous T24 TM3/TM4
- persistent-state retrospective lag = fixed-time warning
- distance threshold from WOF-037 T20 A5136 entryAbsDx

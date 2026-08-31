# WOF Future Danger AI — 最新交接 / START HERE

更新时间：2026-08-31
仓库：`ouyong520/wof-ai-private`
项目：Project A — Browser/MAME/gstyphoon.js Future Danger

> 与 `ouyong520/wof-winkawaks-bridge` 完全分开。不要混入 M3/M4。

## 强制协议
- 用户每轮只在 live `gstyphoon.js` Worker Console 执行一条命令。
- 命令第一行唯一 `// WOF-xxx`。
- 回传先校验 `copyId / project / version / marker`；不匹配不作当前证据。
- 默认 read-only；`ramWrites=0`。
- Assistant 负责分析、GitHub 修改、下一版测试。

## 已锁死底层，不重做
- P1/P2/P3 `0xFFBE1C / 0xFFBEFC / 0xFFBFDC`
- enemy pool `0xFFC0BC`, stride `0xE0`, 20 slots
- player `+0x7C=0/4/8`
- enemy authoritative target `+0x7E=0/4/8 -> P1/P2/P3`
- player pointer table `0x010CF8`
- selector route、dispatcher 44 incoming edges、descriptor consumer `0x247C` 已解决
- `enemy+0x70 U16 0->nonzero` 仅 ACTIVE-start convention，不是 exact hitbox/damage onset

## 当前 production / candidates
- T16 exact B4 -> attack6432 = `production-shadow`
  - WOF-036 再次 13/13 strict；LEFT11 + RIGHT2，RIGHT symmetry 已补强。
- T20 `B0 -> B255` -> attack5136 = **`production-shadow-candidate`**
  - WOF-037 独立 forward prospective：6/6 strict；expected attack 6/6；target 6/6；side 6/6；LEFT1 RIGHT5；lead 418.6..680.1ms。
  - 定义为 **coarse early warning**，不是精确倒计时。
- T33/T34 TM6 attack3232 = type-specific `production-shadow-candidates`
- 四条 T24 exact TM2 = prospective-candidates，仍待 coverage
- T23 A4792 exact B0 = prospective-candidate，WOF-037 本轮无 entry coverage

## WOF-037 正确结果
身份：
- copyId `WOF-037`
- project `WOF-AI-PRIVATE`
- version `wof-future-danger-t20-t23-hybrid-prospective-validator-v37`
- marker `=== WOF FUTURE DANGER T20 T23 HYBRID PROSPECTIVE VALIDATOR V37 JSON ===`
- readOnly `true`
- ramWrites `0`

运行：120002.3ms / 10ms；40039 enemy samples；140 ACTIVE edges。

### T20 -> A5136 forward prospective PASS
`T20_5136_B0_TO_B255_700`
- signals 6 / evaluable 6
- strict 6 / jitter 0 / late 0 / hard miss 0
- expected attack5136 6/6
- target stable 6/6
- side stable 6/6
- entry sides LEFT1 / RIGHT5
- leads: 418.6, 458.6, 530.1, 647.8, 670.1, 680.1ms

Entry absDx 分别约 305,306,182,252,264,229，和 lead 不呈可信单调关系；禁止据此造 distance threshold。

### WOF-037 零 entry 的规则
- T23 A4792 exact B0 entry：0
- T20 A4792 TM6->TM5：0
- T20 A4792 TM3->TM2：0
这些不是 hard miss/反证，只是本轮没有出现这些预定义 entry；优先级下降，但不判失败。

### 新 descriptor-family 发现（仍是 discovery/correlation）
WOF-037 当前房间出现大量 attack3232：
- T9 `FE867BA / NX85ECE / BODY2872 / V100000 / A4/B2 / P6C2784 / TM6`：3 个 retrospective ~100ms 样本，eventual A3232；lead约99.8..100.6ms。
- T11 `FE8811E / NX879E2 / BODY2872 / V100000 / A4/B2 / P6C2784 / TM6`：2 个 retrospective ~100ms 样本，eventual A3232；lead约99.6..100.8ms。

这与历史 T33/T34 的 exact TM6->A3232 prospective candidates 使用同一 descriptor 结构一致，因此下一步不再只写死 enemy type，而是验证 **descriptor family 是否跨 type 泛化**。

## 当前 frontier
```text
version = wof-resume-dispatch-selector-v48
nextCopyId = WOF-038
nextScript = wof_future_danger_descriptor_family_validator_v38.js
nextMarker = === WOF FUTURE DANGER DESCRIPTOR FAMILY VALIDATOR V38 JSON ===
```

## WOF-038 目标
Forward prospective：
1. `D867BA_3232_TM6_120`：不限制 enemy type，exact descriptor/body/value/action/b2/timer/payload；live 首次进入 TM6 才 arm。
2. `D8811E_3232_TM6_120`：同上。
3. 继续独立复验 `T20_5136_B0_TO_B255_700`（现 production-shadow-candidate）。
4. opportunistic 保留 T16 exact B4、T23 B0、四条 T24 exact TM2。
5. 输出 `entryTypeCounts`，用于判断 descriptor-family 是否真的跨 T9/T11/T33/T34 等 type 泛化。
6. 继续 fallback terminal/fixed-lag mining，避免换房间白跑；fallback 永远只算 discovery/correlation。

## 禁止恢复/误判
- broad T16 FAST/MID ❌
- broad T30_FAST ❌
- absDx130 = hitbox/range ❌
- 用 T20 A5136 的 absDx 造 timing threshold ❌
- T16 4840 divergence production ❌
- retrospective lag fingerprint = fixed-time predictor ❌
- mined correlation = causal/prospective proof ❌
- descriptor-family 在 WOF-038 forward prospective 前直接升 production ❌

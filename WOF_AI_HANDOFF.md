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
- T16 exact terminal B4 -> attack6432 = production-shadow
- WOF-036 再次 13/13 strict，attack/target/side 全 13/13；entry side LEFT11 + RIGHT2，因此 T16 RIGHT symmetry 已有直接强覆盖
- T33/T34 TM6 attack3232 = production-shadow-candidates
- 四条 T24 exact TM2 仍 prospective-candidates；WOF-035/036 均因 T24 coverage=0，没有正负证据

## WOF-036 最新完成结果
身份正确：`WOF-036 / WOF-AI-PRIVATE / wof-future-danger-adaptive-terminal-miner-v36 / marker`；readOnly=true；ramWrites=0。
120004.3ms / 10ms；33569 enemy samples；156 ACTIVE edges。
主要 type：T7/T9/T16/T30/T20/T44/T23。

### T16 reconfirmation
`T16_6432_B4_40`：13 signals / 13 evaluable / 13 strict / 0 jitter / 0 late / 0 hard miss；attack6432 13/13；target stable 13/13；side stable 13/13；lead 10.2..20.1ms；LEFT11 RIGHT2。

### 新 discovery：T20 -> A5136
强 exact state：
`T20 S2/A4/B255 BODY0 FE839C4 NX82B0A V100000 TM20 P6C0`
terminal 22；20/50/100/150/250ms retrospective fingerprint 都 22/22，500ms 仍 19/19，target/side 全稳定。

重要修正：这是 persistent phase，不能因为 100ms lag 中 22/22 就称“固定还有100ms”。真正 forward transition：
`S2/A4/B0 ... -> S2/A4/B255 ...`
在 WOF-036 mining 中 17 次 eventual A5136，lead 369.4..659.2ms，target/side 17/17 stable。只能算 discovery/correlation，需 prospective。

### 新 discovery：T23 -> A4792
`T23 S0/A0/B0 BODY4920 FE848E2 NX83C56 V140000 TM1 P6C7904`
在 ~100ms retrospective bucket 7/7 eventual A4792，target/side 7/7 stable；含 RIGHT 样本。仍需 forward prospective entry validation。

### 新 discovery：T20 -> A4792 countdown
`S0/A6/B4 BODY4976 FE83824 NX82D38 V0 P6C0`
TM6->TM5 transition 小样本约70..80ms；TM3->TM2 小样本约20..30ms；已有 LEFT+RIGHT discovery coverage。必须 prospective。

## 当前 frontier
```text
version = wof-resume-dispatch-selector-v47
nextCopyId = WOF-037
nextScript = wof_future_danger_t20_t23_hybrid_prospective_validator_v37.js
nextMarker = === WOF FUTURE DANGER T20 T23 HYBRID PROSPECTIVE VALIDATOR V37 JSON ===
```

WOF-037 预先定义的 forward rules：
1. T20 A5136 exact B0->B255 entry，horizon700ms / tail1100ms
2. T23 A4792 exact BODY4920 B0 state entry，horizon180ms / tail500ms
3. T20 A4792 exact TM6->TM5，horizon110ms / tail300ms
4. T20 A4792 exact TM3->TM2，horizon60ms / tail220ms
并 opportunistically 继续 T16 exact B4。

WOF-037 同时做轻量 adaptive terminal/fixed-lag mining，避免换房间完全白跑；但 fallback mining 仍只是 discovery/correlation。只有 forward prospective ruleStats 可升级规则。

## 禁止恢复/误判
- broad T16 FAST/MID ❌
- broad T30_FAST ❌
- absDx130 = hitbox/range ❌
- T16 4840 divergence production ❌
- retrospective lag fingerprint = fixed-time predictor ❌（尤其 persistent state）
- WOF-034/036 mining correlation = causal proof ❌

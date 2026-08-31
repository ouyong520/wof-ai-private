# WOF Future Danger AI — CURRENT FRONTIER

更新时间：2026-08-31  
仓库：`ouyong520/wof-ai-private`

## 阶段
底层 selector/dispatcher/descriptor 已解决。当前是 **production-shadow 扩展 + 同周期 forward 验证**。

## WOF-042
身份严格通过，5/5 complete，0 error，0 interrupted，`readOnly=true`，`ramWrites=0`。  
59816 polls / 190429 enemy samples / 1018 ACTIVE edges / 93 signals / 92 strict +1 jitter /0 miss。

player histogram `[0,105,1058,1264]` = 0P/1P/2P/3P。

## Production set
- **T16 B4 imminent danger**：56/56 timing hit；但2次在ACTIVE边缘 retarget，所以 danger 强、entry-target lock 不是100%。实时 `+0x7E` 才是目标真值。
- **T20 B0->B255 -> A5136**：WOF-042 6/6 strict A5136/target/side，lead420.6..580.6ms；结合历史证据升 `production-shadow-coarse`。1250ms 仅 audit window。
- **D867BA TM6 -> A3232**：14/14 strict，本轮 T9/T33；production-shadow。
- **D8811E TM6 -> A3232**：6/6 strict at135ms audit；production-shadow。
- **T24 BODY7512/TM3 S2 -> A5440**：11/11 strict，A5440/target/side11/11，lead49.0..58.2ms，2 rooms；升 production-shadow。

## T24 A5424 next
旧 edge matcher：
`T24_5424_CYCLE_BODY7520_TM4_90`
- rawMatch17
- transitionEntry0
- signals0

same-cycle evidence：
- S2 BODY7520/TM4 -> A5424：6 cycles，first lead61.6..71.6ms，target/side6/6
- S4 BODY7520/TM4 -> A5424：5 cycles，first lead61.5..71.2ms，target/side5/5

=> 不是负面证据，而是 entry detector 看不到“首次观察时已经 held 的状态”。WOF-043 改用 once-per-cycle level arm (`match=base(s)`，cycle id 去重)，并允许 state99=2/4。

## T23
旧 BODY4920/B0 rule 在5116 T23 samples、15 A4792下仍 rawMatch0。退役。继续 same-cycle mining，不再复活旧 fixed-lag 候选。

## Current next — WOF-043
```text
resume = wof-resume-dispatch-selector-v53
nextCopyId = WOF-043
nextScript = wof_future_danger_multiroom_coordinator_v43.js
nextMarker = === WOF FUTURE DANGER MULTIROOM COORDINATOR V43 JSON ===
embedded = WOF-043R
```

### WOF-043
- Worker=collect / top=finalize+one JSON
- fresh IndexedDB v5
- T24 A5440 production-shadow
- T24 A5424 state99 2/4 cycle-level prospective validation
- T20 coarse shadow
- D867/D881 shadows
- T16 retarget audit
- same-cycle discovery continues

## Exclusions
- +0x70 ≠ exact hitbox/damage onset
- absDx ≠ causal timing law
- warning entry target ≠ final lock
- T16 B4 ≠ exclusive A6432
- T20 1250ms ≠ countdown boundary
- retired fixed-lag T24 BODY5424/5440 不复活
- old T23 BODY4920/B0 不复活

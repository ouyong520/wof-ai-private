# WOF Future Danger AI — CURRENT FRONTIER

更新时间：2026-08-31  
仓库：`ouyong520/wof-ai-private`

## 阶段
底层 selector/dispatcher/descriptor 已解决。当前是 **production-shadow 扩展 + focused same-cycle mining**。

## WOF-043
身份严格通过：5/5 complete，0 error，0 interrupted，`readOnly=true`，`ramWrites=0`。  
59894 polls / 182907 enemy samples / 889 ACTIVE edges / 112 signals / 112 strict / 0 miss。

player histogram `[18,458,1465,484]` = 0P/1P/2P/3P；本轮再次包含1P/2P/3P context。

## Production set
- **T16 B4 imminent danger**：20/20 strict；本轮20次均A6432，target20/20、side19/20。历史非6432样本仍禁止 exclusive attack 语义。
- **T20 B0->B255 -> A5136**：9/9 strict A5136/target/side，lead458.6..800.2ms，3 rooms；`production-shadow-coarse`。
- **D867BA TM6 -> A3232**：35/35 strict，A3232/target35/35、side34/35；T9/T33/T36；all5 rooms；production-shadow。
- **D8811E TM6 -> A3232**：9/9 strict A3232/target/side；T34/T37/T11；production-shadow。
- **T24 BODY7512/TM3 S2 -> A5440**：18/18 strict，A5440/target/side18/18，lead49.4..58.7ms，3 rooms；production-shadow。
- **T24 BODY7520/TM4 state99 2/4 level -> A5424**：21/21 strict，A5424/target/side21/21，lead60.8..71.5ms，3 rooms；production-shadow。

## T24 A5424 issue resolved
WOF-042 had raw visibility but no transition-edge entry. WOF-043 switched to once-per-zero-cycle level arm and immediately produced21/21 forward hits.

=> Previous zero-signal result was an entry-detector blind spot. Both real same-cycle T24 rules are now production shadows.

## T23
Old BODY4920/B0 rule again rawMatch0/signals0 despite6490 samples and9 A4792 edges.

=> Explicitly retired. Global `cyclePrecursorTop` can crowd out lower-frequency types, so WOF-044 adds dedicated `cyclePrecursorFocus.T23` and `.T18` per room.

## Current next — WOF-044
```text
resume = wof-resume-dispatch-selector-v54
nextCopyId = WOF-044
nextScript = wof_future_danger_multiroom_coordinator_v44.js
nextMarker = === WOF FUTURE DANGER MULTIROOM COORDINATOR V44 JSON ===
embedded = WOF-044R
```

### WOF-044 protocol
- Worker=collect / top=finalize+one JSON
- fresh IndexedDB v6
- both T24 rules production-shadow
- T20 coarse / D867 / D881 / T16 continue audit
- old T23 rule retired
- focused same-cycle arrays retain up to80 T23 and80 T18 candidates per room so new rules cannot be crowded out by global top100

## Exclusions
- +0x70 ≠ exact hitbox/damage onset
- absDx ≠ causal timing law
- warning entry target ≠ final lock
- T16 B4 ≠ exclusive A6432
- T20 1250ms ≠ countdown boundary
- retired fixed-lag T24 BODY5424/5440 不复活
- old T23 BODY4920/B0 不复活

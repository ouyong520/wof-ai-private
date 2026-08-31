# WOF Future Danger AI — CURRENT FRONTIER

更新时间：2026-08-31  
仓库：`ouyong520/wof-ai-private`

## 阶段
底层 selector/dispatcher/descriptor 已解决。当前是 **production-shadow 扩展 + focused same-cycle mining + T23 forward validation**。

## WOF-045
身份严格通过：5/5 complete，0 error，0 interrupted，`readOnly=true`，`ramWrites=0`。  
59994 polls / 202612 enemy samples / 1025 ACTIVE edges / 137 signals / **137 strict** / 0 miss。

player histogram `[119,42,1179,1088]` = 0P/1P/2P/3P；本轮包含1P/2P/3P context。

## Production set
- **T16 B4 imminent danger**：23/23 strict；本轮23次均A6432、target/side23/23。历史非6432/retarget样本仍禁止 exclusive/frozen-target 语义。
- **T20 B0->B255 -> A5136**：10/10 strict A5136/target/side，lead460.0..1020.1ms；`production-shadow-coarse`。
- **D867BA TM6 -> A3232**：41/41 strict A3232/target/side；all5 rooms；production-shadow。
- **D8811E TM6 -> A3232**：14/14 strict A3232/target/side；production-shadow。
- **T24 BODY7512/TM3 -> A5440**：14/14 strict A5440/target/side；production-shadow。
- **T24 BODY7520/TM4 level -> A5424**：15/15 strict A5424/target/side；production-shadow。
- **T18 BODY7512/TM4 -> A5440**：WOF-045 direct forward 10/10 strict、A5440/target/side10/10，lead60.5..70.4ms；结合 WOF-044 discovery9/9，WOF-046 起升 production-shadow。
- **T18 BODY7520/TM4 -> A5424**：WOF-045 direct forward10/10 strict、A5424/target/side10/10，lead61.5..70.3ms；结合 WOF-044 discovery9/9，WOF-046 起升 production-shadow。

## Focus exporter fixed
WOF-045 实际 result 已有 `cyclePrecursorFocus`：两个 T23 房间均有 populated T23 arrays，T18 房间有 populated T18 array。WOF-044 missing-field bug 已解决。

## T23
旧 BODY4920/B0 继续 retired。

WOF-045 focus miner 找到一个新的短 lead A4792 current-cycle candidate：
`S0/A6/B4|BODY4976|FE84868|NX83F20|V0|TM5|P6C0`
- 4/4 cycles -> A4792
- first lead79.3..89.4ms
- target/side4/4

WOF-046 将直接 once-per-zero-cycle level-arm 验证：
`T23_4792_BODY4976_A6_B4_TM5_LEVEL_100`
- horizon100ms
- tail300ms
- expected A4792

另一个 T23 房间出现不同的长 lead branch（约1.4–2.9s，当前2 cycles），继续 focused mining，不 promotion。

## Current next — WOF-046
```text
resume = wof-resume-dispatch-selector-v56
nextCopyId = WOF-046
nextScript = wof_future_danger_multiroom_coordinator_v46.js
nextMarker = === WOF FUTURE DANGER MULTIROOM COORDINATOR V46 JSON ===
embedded = WOF-046R
```

### WOF-046 protocol
- Worker=collect / top=finalize+one JSON
- fresh IndexedDB v8
- T18 A5440/A5424 rules production-shadow
- new T23 A4792 TM5 prospective level-trigger validation
- focused `cyclePrecursorFocus.T23/T18` continues
- T16/T20/D867/D881/T24 production audit continues

## Exclusions
- +0x70 ≠ exact hitbox/damage onset
- absDx ≠ causal timing law
- warning entry target ≠ final lock
- T16 B4 ≠ exclusive A6432
- T20 1250ms / D867220 / D881135 ≠ causal boundary
- retired fixed-lag T24 BODY5424/5440 不复活
- old T23 BODY4920/B0 不复活
- long-lead T23 branch 2 cycles 不 promotion

# WOF Future Danger AI — CURRENT FRONTIER

更新时间：2026-08-31  
仓库：`ouyong520/wof-ai-private`

## 阶段
底层 selector/dispatcher/descriptor 已解决。当前是 **production-shadow 扩展 + focused same-cycle mining**。

## WOF-044
身份严格通过：5/5 complete，0 error，0 interrupted，`readOnly=true`，`ramWrites=0`。  
59988 polls / 211029 enemy samples / 1057 ACTIVE edges / 132 signals / 130 strict / 1 real-late / 1 censored / 0 hard miss。

player histogram `[49,0,1412,979]` = 0P/1P/2P/3P；本轮主要2P/3P。

## Production set
- **T16 B4 imminent danger**：47/47 timing hit；A6432=46、A4832=1；1次 ACTIVE-edge retarget。danger强，entry-target lock不是100%。
- **T20 B0->B255 -> A5136**：13/13 strict A5136/target/side，lead410.5..869.5ms；`production-shadow-coarse`。
- **D867BA TM6 -> A3232**：39/39 strict A3232/target/side；all5 rooms；production-shadow。
- **D8811E TM6 -> A3232**：14/14 A3232/target/side；13 strict<=135ms +1 clean 209.5ms tail hit；production-shadow，135ms不是因果阈值。
- **T24 BODY7512/TM3 -> A5440**：9 evaluable/9 strict，另1 end-of-run censored；所有解析结果 A5440/target/side；production-shadow。
- **T24 BODY7520/TM4 level -> A5424**：9/9 strict A5424/target/side；production-shadow。

## Focused mining correction
WOF-044 的 model 声称输出 `cyclePrecursorFocus.T23/T18`，但实际 result 对象没有该字段。故 WOF-044 没有完成 focused T23 capture；这是导出 bug，不是 T23 负证据。

old T23 BODY4920/B0 在3810 T23 samples /15 A4792下仍 rawMatch0，继续 retired。

## T18 WOF-044 discovery
Global same-cycle top 找到：
- `T18 S2/A2/B4 BODY7512 FE8BBB2 NX8B290 V180001 TM4 -> A5440`: 9/9 cycles，first lead60.2..70.5ms，target/side9/9。
- `T18 S2/A2/B4 BODY7520 FE8BBDE NX8B2A4 V180001 TM4 -> A5424`: 9/9 cycles，first lead60.7..71.1ms，target/side9/9。

=> WOF-045 直接 forward 验证。

## Current next — WOF-045
```text
resume = wof-resume-dispatch-selector-v55
nextCopyId = WOF-045
nextScript = wof_future_danger_multiroom_coordinator_v45.js
nextMarker = === WOF FUTURE DANGER MULTIROOM COORDINATOR V45 JSON ===
embedded = WOF-045R
```

### WOF-045
- Worker=collect / top=finalize+one JSON
- fresh IndexedDB v7
- independent focused miner 真正输出 `cyclePrecursorFocus.T23/T18`
- direct T18 A5440/A5424 level-trigger forward validation
- T16/T20/D867/D881/T24 production audit continues

## Exclusions
- +0x70 ≠ exact hitbox/damage onset
- absDx ≠ causal timing law
- warning entry target ≠ final lock
- T16 B4 ≠ exclusive A6432
- T20 1250ms / D867220 / D881135 ≠ causal boundary
- retired fixed-lag T24 BODY5424/5440 不复活
- old T23 BODY4920/B0 不复活
- WOF-044 missing focus arrays 不能解释成 T23 无前驱

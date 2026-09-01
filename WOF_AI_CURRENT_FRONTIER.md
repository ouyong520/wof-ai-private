# WOF Future Danger AI — CURRENT FRONTIER

更新时间：2026-09-01  
仓库：`ouyong520/wof-ai-private`

## 阶段
底层 selector/dispatcher/descriptor 已解决。当前是 **production-shadow audit + T23 ordered sequence discrimination**。

## WOF-049
Batch `b-106c5a3c-819`：
- identity valid
- 5 joined / 5 complete / 0 error / 0 interrupted
- readOnly=true / ramWrites=0
- embedded WOF-049R identity passed
- mixed player histogram `[27,1087,196,1134]`; room peaks `3,1,3,1,3`
- 60000 polls / 194328 enemy samples / 1166 ACTIVE edges
- 106 signals / **106 strict** / 0 jitter / 0 late / 0 hard miss / 0 censored

## Production audit
- **T16 B4 danger**：31/31 strict；lead10.0..21.6ms；target/side31/31。
- **T20 B0->B255 -> A5136**：4/4 strict A5136/target/side；lead430.2..629.1ms；production-shadow-coarse。
- **D867BA -> A3232**：13/13 strict A3232/target/side；lead29.9..120.1ms；T9=11/T33=2；P1/P2/P3 均覆盖。
- **D8811E -> A3232**：4/4 strict A3232/target/side；lead100.0..108.8ms；本批 T11=4。
- **T24 BODY7512/TM3 -> A5440**：19/19 strict；lead49.2..59.3ms。
- **T24 BODY7520/TM4 -> A5424**：21/21 strict；target21/21；side20/21；唯一变化是 CENTER-entry -> RIGHT-ACTIVE，不是 hard miss。
- **T18 BODY7512/TM4 -> A5440**：7/7 strict；lead60.0..70.6ms。
- **T18 BODY7520/TM4 -> A5424**：7/7 strict；lead68.9..70.5ms。

## T23 current
WOF-047 仍是最新正面 ordered-sequence evidence：8 resolved cycles = A4792 3 / A4920 3 / A5888 2；单-state 不足。

WOF-049 五个房间 dedicated T23 tracer 全部：
```text
t23Samples = 0
attackZeroStarts = 0
activeEdges = 0
resolvedCycles = 0
t23CycleTraces = []
t23SequenceSummary.totalCycles = 0
```
aggregate type census 同样没有 T23。因此 WOF-049 没有新增 T23 sequence evidence。这再次表明瓶颈是 **scene/room coverage**，不是 tracer correctness。

active-edge retarget fix、exact timer tails 与 timer-normalized TM* final/tail2/tail3、pair/triple summaries 继续保留。

## Current next — WOF-050
```text
resume = wof-resume-dispatch-selector-v60
nextCopyId = WOF-050
nextScript = wof_future_danger_multiroom_coordinator_v50.js
nextMarker = === WOF FUTURE DANGER MULTIROOM COORDINATOR V50 JSON ===
embedded = WOF-050R
IndexedDB = wof-future-danger-multiroom-v12
```

### WOF-050 protocol
- Worker=collect / top=finalize+one JSON
- semantic repeat of current instrumentation
- production audits continue
- T23 ordered traces continue
- active-edge retarget logging retained
- exact-TM + TM* ordered summaries retained
- no T23 promotion until repeated attack-specific sequence evidence appears
- **Prefer up to5 parallel rooms**；目标是拿到真正包含 T23 的 room/scene

Detailed report: `reports/WOF-049_ANALYSIS.md`

## Exclusions
- +0x70 ≠ exact hitbox/damage onset
- absDx ≠ causal timing law
- warning entry target ≠ final lock
- T16 B4 ≠ exclusive A6432
- T20 1250ms / D867220 / D881135 ≠ causal boundary
- retired fixed-lag T24 BODY5424/5440 不复活
- old T23 BODY4920/B0 不复活
- zero coverage 不等于 failure
- sparse T23 traces 不直接 promotion

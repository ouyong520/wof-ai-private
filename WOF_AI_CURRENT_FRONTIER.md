# WOF Future Danger AI — CURRENT FRONTIER

更新时间：2026-09-01  
仓库：`ouyong520/wof-ai-private`

## 阶段
底层 selector/dispatcher/descriptor 已解决。当前是 **production-shadow audit + T23 ordered sequence discrimination**。

## WOF-048
Batch `b-bdb16c09-b10`：
- identity valid
- 1 joined / 1 complete / 0 error / 0 interrupted
- readOnly=true / ramWrites=0
- embedded WOF-048R identity passed
- pure 3P: player histogram `[0,0,0,495]`
- 11997 polls / 39546 enemy samples / 164 ACTIVE edges
- 19 signals / **19 strict** / 0 jitter / 0 late / 0 hard miss / 0 censored

## Production audit
- **T20 B0->B255 -> A5136**：6/6 strict A5136/target/side，lead481.0..799.5ms；production-shadow-coarse。
- **D867BA -> A3232**：11/11 strict A3232/target/side，lead99.2..111.3ms；T33=1,T9=10；production-shadow。
- **D8811E -> A3232**：2/2 strict A3232/target/side，lead99.9/109.3ms；production-shadow。
- T16/T24/T18 本房没有 raw coverage；不构成负证据。

## T23 current
WOF-047 已证明 ordered tracer 可工作，并得到8个 resolved cycles：A4792=3/A4920=3/A5888=2；单一 state 不足，必须比较 ordered tail/pair/triple。

WOF-048 本房 dedicated T23 trace probe 完全没有 T23：
```text
t23Samples = 0
attackZeroStarts = 0
activeEdges = 0
resolvedCycles = 0
t23CycleTraces = []
t23SequenceSummary.totalCycles = 0
```
所以本轮 **没有新增 T23 sequence evidence**。这只是 scene/coverage absence，不是 WOF-048 sequence logic failure。

WOF-048 active-edge retarget fix 与 TM* normalized sequence summary 保持启用，但因为0个 T23 cycle，本批没有实际 exercise。

## Current next — WOF-049
```text
resume = wof-resume-dispatch-selector-v59
nextCopyId = WOF-049
nextScript = wof_future_danger_multiroom_coordinator_v49.js
nextMarker = === WOF FUTURE DANGER MULTIROOM COORDINATOR V49 JSON ===
embedded = WOF-049R
```

### WOF-049 protocol
- Worker=collect / top=finalize+one JSON
- fresh IndexedDB v11
- semantic repeat of WOF-048 instrumentation
- production audits continue
- T23 ordered traces continue
- active-edge retarget logging retained
- `t23SequenceSummary` retains timer-normalized TM* final/tail2/tail3, transition pair/triple counts by attack
- no promotion until repeated attack-specific sequence evidence appears
- **Prefer multiple rooms, ideally up to5 parallel**, because WOF-048 only sampled one room and saw no T23 at all

Detailed report: `reports/WOF-048_ANALYSIS.md`

## Exclusions
- +0x70 ≠ exact hitbox/damage onset
- absDx ≠ causal timing law
- warning entry target ≠ final lock
- T16 B4 ≠ exclusive A6432
- T20 1250ms / D867220 / D881135 ≠ causal boundary
- retired fixed-lag T24 BODY5424/5440 不复活
- old T23 BODY4920/B0 不复活
- zero coverage 不等于 failure
- current sparse T23 traces 不直接 promotion

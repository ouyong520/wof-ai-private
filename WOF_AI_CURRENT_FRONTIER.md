# WOF Future Danger AI — CURRENT FRONTIER

更新时间：2026-09-01  
仓库：`ouyong520/wof-ai-private`

## 阶段
底层 selector/dispatcher/descriptor 已解决。当前是 **production-shadow audit + T23 ordered sequence discrimination**。

## WOF-047
Batch `b-fbbbc59d-cea`：
- identity valid
- 3 joined / 3 complete / 0 error / 0 interrupted
- readOnly=true / ramWrites=0
- 35996 polls / 113581 enemy samples / 644 ACTIVE edges
- 144 signals =143 strict +1 jitter /0 late /0 hard miss /0 censored
- player histogram `[0,0,579,902]` = 0P/1P/2P/3P
- all3 embedded WOF-047R validations passed

## Production audit
- **T16 B4 imminent danger**：94/94 tail hits =93 strict+1 jitter；A6432=93,A4832=1；target/side94/94；lead9.0..40.5ms。attack 仍不 exclusive。
- **T20 B0->B255 -> A5136**：本轮没有 coverage；保持 production-shadow-coarse，不作负判断。
- **D867BA -> A3232**：23/23 strict A3232/target/side，lead98.8..119.5ms；T33/T9；all3 rooms。
- **D8811E -> A3232**：19/19 strict A3232/target/side，lead99.4..120.4ms；T34。
- **T24 A5440**：3/3 strict。
- **T24 A5424**：3/3 strict。
- **T18 A5440**：1/1 strict。
- **T18 A5424**：1/1 strict。

## T23 current
- old BODY4920/B0 remains retired。
- WOF-045 short candidate `S0/A6/B4 BODY4976 FE84868 NX83F20 V0 TM5 -> A4792` again rawMatch0/signals0；仍是 zero coverage，不是 failure。

### Ordered traces
WOF-047 `t23CycleTraces` 在唯一 T23 房间成功记录8个 resolved cycles：
```text
A4792 = 3
A4920 = 3
A5888 = 2
```
0 dropped。

当前最重要结论：**单一 terminal state 仍不足，late ordered tail 才可能区分 branch。**

示例：
- A5888 一个 tail3：`S0/A8/B2 BODY4936 -> S0/A2/B0 BODY4936 -> S0/A6/B4 BODY4936`。
- 但第一个 `S0/A8/B2 BODY4936` 本身也出现在 A4792 cycle，因此必须用 order。
- A4920 已看到至少3种不同 final branch。
- A4792 三个 cycle 也有三种不同 late tail；当前没有 universal A4792 short sequence。

因此本轮不 promotion 新 T23 production rule。

## Instrumentation correction
WOF-047 tracer 在 target 恰好于 ACTIVE-edge poll 改变时，会有 `targetStable=false` 但 `retargets=[]`。原因是 observer 只在 attack==0 时运行。

WOF-048R 已修：active-edge target change 会追加 `retargets[].atActiveEdge=true`。

## Current next — WOF-048
```text
resume = wof-resume-dispatch-selector-v58
nextCopyId = WOF-048
nextScript = wof_future_danger_multiroom_coordinator_v48.js
nextMarker = === WOF FUTURE DANGER MULTIROOM COORDINATOR V48 JSON ===
embedded = WOF-048R
```

### WOF-048 protocol
- Worker=collect / top=finalize+one JSON
- fresh IndexedDB v10
- all existing production audits continue
- T23 ordered traces continue
- active-edge retarget logging fixed
- new `t23SequenceSummary` by attack:
  - timer-normalized `TM*` families
  - final-family counts
  - tail2/tail3 counts
  - transition pair counts
  - transition triple counts
- summary remains discovery only; build prospective sequence validator only after repeated attack-specific discriminator evidence

Detailed report: `reports/WOF-047_ANALYSIS.md`

## Exclusions
- +0x70 ≠ exact hitbox/damage onset
- absDx ≠ causal timing law
- warning entry target ≠ final lock
- T16 B4 ≠ exclusive A6432
- T20 1250ms / D867220 / D881135 ≠ causal boundary
- retired fixed-lag T24 BODY5424/5440 不复活
- old T23 BODY4920/B0 不复活
- zero coverage 不等于 failure
- 当前8条 T23 trace 不足以 promotion

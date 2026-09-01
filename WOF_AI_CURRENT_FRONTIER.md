# WOF Future Danger AI — CURRENT FRONTIER

更新时间：2026-09-01  
仓库：`ouyong520/wof-ai-private`

## 阶段
底层 selector/dispatcher/descriptor 已解决。当前是 **production-shadow audit + coverage expansion + ordered sequence discrimination**。

## WOF-051
Batch `b-2f39eb3f-4a7`：
- identity valid
- 3 joined / 3 complete / 0 error / 0 interrupted
- readOnly=true / ramWrites=0
- all embedded WOF-051R passed
- player histogram `[0,488,488,492]` = effectively pure3P + pure1P + pure2P rooms
- 35999 polls / 108463 enemy samples / 558 ACTIVE edges
- 145 signals / 144 strict / 0 jitter / 1 realLate / 0 hard miss / 0 censored

## Production audit
- **T16 B4 danger**：98/98 strict；lead8.9..21.0ms；A6432=97/A4840=1；target/side98/98。仍是 imminent danger，不是 attack-exclusive。
- **T20 B0->B255 -> A5136**：5/5 strict；lead380.9..639.7ms；target/side5/5。
- **D867BA -> A3232**：10/10 strict；lead99.1..109.4ms；T33=8/T9=2；P1/P2/P3 targets covered。
- **D8811E -> A3232**：22/22 strict；lead98.6..119.2ms；T34=15/T11=7。
- **T24**：两条 zero coverage。
- **T18 BODY7512/TM4 -> A5440**：4/4 strict；lead62.3..70.9ms。
- **T18 BODY7520/TM4 -> A5424**：4/4 strict；lead69.1..70.0ms。

## T23
WOF-047 仍是最新正面 ordered-sequence evidence：8 cycles = A4792 3 / A4920 3 / A5888 2。

WOF-051 三房继续：
```text
t23Samples=0
attackZeroStarts=0
activeEdges=0
resolvedCycles=0
```
aggregate type census 无 T23。WOF-049+050+051 连续11个房间没有 T23；这是 scene/room coverage absence，不是 tracer correctness 问题。

## Critical T18 result
WOF-050 broad same-cycle discovery state：
```text
S0/A4/B2|BODY4728|FE8b660|NX8b204|Vffff|TM1|P6C4736
```
曾看似指向 A4704。

WOF-051 direct prospective level-arm：
```text
2 signals / 2 evaluable
A4704 @19.9ms
A4712 @100.4ms
expected A4704 = 1/2
target stable = 2/2
side stable = 2/2
hard miss = 0
```

所以 exact single state 是 forward-relevant 但 attack-ambiguous。**不 promotion；不再把它当 A4704-specific rule。** 下一步必须看 candidate 之后的 ordered state sequence/context。

## Current next — WOF-052
```text
resume = wof-resume-dispatch-selector-v62
nextCopyId = WOF-052
nextScript = wof_future_danger_multiroom_coordinator_v52.js
nextMarker = === WOF FUTURE DANGER MULTIROOM COORDINATOR V52 JSON ===
embedded = WOF-052R
IndexedDB = wof-future-danger-multiroom-v14
```

### WOF-052 protocol
- Worker=collect / top=finalize+one JSON
- production audits continue unchanged
- T23 ordered tracer continues
- active-edge retarget fix retained
- exact-TM + TM* T23 summaries retained
- new T18 ordered candidate-context tracer:
  - record all T18 zero->ACTIVE cycles
  - mark exact BODY4728/A4/B2/TM1 state
  - preserve ordered distinct states
  - summarize only candidate-containing cycles by eventual activeAttack
  - exact/TM* final/tail2/tail3 + transition pair/triple
  - seek A4704 vs A4712 post-candidate discriminator
- sequence output remains discovery only; later prospective validator required
- prefer up to5 rooms, especially rooms with T18

Detailed report: `reports/WOF-051_ANALYSIS.md`

## Exclusions
- +0x70 ≠ exact hitbox/damage onset
- absDx ≠ causal timing law
- warning entry target ≠ final lock
- T16 B4 ≠ exclusive A6432
- audit horizons ≠ causal boundaries
- retired fixed-lag T24 rules / old T23 BODY4920/B0 stay retired
- zero coverage ≠ failure
- single-state BODY4728/A4/B2/TM1 ≠ A4704-specific predictor
- ordered discovery ≠ production proof

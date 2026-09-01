# WOF Future Danger AI — CURRENT FRONTIER

更新时间：2026-09-01  
仓库：`ouyong520/wof-ai-private`

## 阶段
底层 selector/dispatcher/descriptor 已解决。当前是 **production-shadow audit + coverage expansion + T23 ordered sequence discrimination**。

## WOF-050
Batch `b-f8bbda7c-fae`：
- identity valid
- 3 joined / 3 complete / 0 error / 0 interrupted
- readOnly=true / ramWrites=0
- embedded WOF-050R all passed
- player histogram `[112,0,868,488]`
- 36000 polls / 104337 enemy samples / 495 ACTIVE edges
- 98 signals / 96 strict / 0 jitter / 2 realLate / 0 hard miss / 0 censored

## Production audit
- **T16 B4 danger**：72/72 strict；lead9.7..21.2ms；A6432=71/A4832=1；target/side72/72。再次确认非 attack-exclusive。
- **T20 B0->B255 -> A5136**：4/4 strict；lead599.4..989.7ms。
- **D867BA -> A3232**：18/18 strict；lead79.7..110.1ms；T9=12/T36=1/T33=5。
- **D8811E -> A3232**：2/2 strict；lead109.7/110.8ms；T11=2。
- **T24**：两条 zero coverage。
- **T18 A5440**：1 clean correct tail hit @138.6ms。
- **T18 A5424**：1 clean correct tail hit @128.5ms。
  两个 T18 event 均 expected attack/target/side 全正确且在250ms tail内；90ms 只应视为 legacy audit horizon，不是 causal boundary。

## T23
WOF-047 仍是最新正面 ordered-sequence evidence：8 cycles = A4792 3 / A4920 3 / A5888 2。

WOF-050 三个房间：
```text
t23Samples = 0
attackZeroStarts = 0
activeEdges = 0
resolvedCycles = 0
```
aggregate type census 无 T23。WOF-049+050 连续8个房间没有 T23，说明当前瓶颈仍是 scene/room coverage。

## New candidate from WOF-050
Broad same-cycle miner 发现：

```text
T18 A4704
S0/A4/B2|BODY4728|FE8b660|NX8b204|Vffff|TM1|P6C4736
```

证据：
- 18 resolved attack-zero cycles
- targetSame18/18
- sideSame18/18
- last-seen lead29.6..51.1ms，median40.5
- first-seen lead50.5..188.6ms，median80.3

下一步直接 prospective，而不是继续 retrospective 解释。

## Current next — WOF-051
```text
resume = wof-resume-dispatch-selector-v61
nextCopyId = WOF-051
nextScript = wof_future_danger_multiroom_coordinator_v51.js
nextMarker = === WOF FUTURE DANGER MULTIROOM COORDINATOR V51 JSON ===
embedded = WOF-051R
IndexedDB = wof-future-danger-multiroom-v13
```

### WOF-051 protocol
- Worker=collect / top=finalize+one JSON
- production audits continue
- T23 ordered tracer continues
- active-edge retarget fix retained
- exact-TM + TM* sequence summaries retained
- add `T18_4704_BODY4728_A4_B2_TM1_LEVEL_80`
  - expected A4704
  - horizon80 / tail250
  - once-per-zero-cycle level arm
  - live target/side check
- no promotion until direct forward confirmations exist
- prefer up to5 rooms

Detailed report: `reports/WOF-050_ANALYSIS.md`

## Exclusions
- +0x70 ≠ exact hitbox/damage onset
- absDx ≠ causal timing law
- warning entry target ≠ final lock
- T16 B4 ≠ exclusive A6432
- audit horizons ≠ causal boundaries
- retired fixed-lag T24 rules / old T23 BODY4920/B0 stay retired
- zero coverage ≠ failure
- same-cycle discovery ≠ production proof

# WOF Future Danger AI — 最新交接 / START HERE

更新时间：2026-09-01  
仓库：`ouyong520/wof-ai-private`  
项目：Project A — Browser/MAME/gstyphoon.js Future Danger

## 强制协议
- 回传先校验 `copyId/project/version/marker/readOnly/ramWrites`。
- 必须 `project=WOF-AI-PRIVATE`, `readOnly=true`, `ramWrites=0`。
- 用户每轮只运行 ONE 条 Browser Console 命令并上传 JSON；Assistant 负责分析、GitHub 修改、版本推进。
- 多房结果保留 per-room 边界。
- `enemy+0x7E` 是 authoritative target，最终输出必须实时重读，warning entry target 不能冻结。
- WinKawaks discovery 与 Browser production 严格隔离。

## 已锁死底层
- P1/P2/P3 `0xFFBE1C / 0xFFBEFC / 0xFFBFDC`
- enemy pool `0xFFC0BC`, stride `0xE0`, 20 slots
- enemy target `+0x7E=0/4/8 -> P1/P2/P3`
- selector / player table / dispatcher44 / descriptor consumer `0x247C` 已解决
- `enemy+0x70 U16 0->nonzero` = ACTIVE-start convention，不是 exact hitbox/damage onset

## 方法论
权威路线：
```text
attack==0 current cycle
-> same-cycle state/ordered-sequence mining
-> prospective arm
-> same enemy 0->nonzero ACTIVE
-> verify attack / target / side / lead / miss
```
fixed-lag fingerprint 只能 discovery/correlation；held state 优先 once-per-zero-cycle level arm。

## 多房 coordinator
WOF-040 起稳定：
```text
Worker = collect (~120s/room)
top    = finalize + download exactly one merged JSON
max 5 rooms
no short join window
1P/2P/3P allowed
```
同一条 JS 在 Worker 与 top 使用。

## Current production set
- `T16_B4_DANGER_40`: imminent-danger production-shadow；历史非 A6432 反例存在，禁止 attack-exclusive 语义。
- `T20_5136_B0_TO_B255_1250`: production-shadow-coarse；约0.4–1.2s coarse warning，1250ms 不是 causal boundary。
- `D867BA_3232_TM6_220`: production-shadow。
- `D8811E_3232_TM6_135`: production-shadow；135ms 仅 audit horizon。
- T24 BODY7512/TM3 -> A5440: production-shadow。
- T24 BODY7520/TM4 -> A5424: production-shadow。
- T18 BODY7512/TM4 -> A5440: production-shadow。
- T18 BODY7520/TM4 -> A5424: production-shadow。

## T23 state before WOF-048
- old BODY4920/B0 rule retired。
- WOF-045 short candidate `S0/A6/B4 BODY4976 FE84868 NX83F20 V0 TM5 -> A4792` 在 WOF-046/047 新批次均 rawMatch0/signals0：zero coverage，不是 failure。
- WOF-047 ordered tracer 在唯一 T23 房间记录8个 resolved cycles：A4792=3, A4920=3, A5888=2。
- 单 state 明显 attack-ambiguous；当前研究必须使用 ordered tail/transition pair/triple。
- WOF-048R 增加 active-edge retarget 修复和 `t23SequenceSummary`：timer-normalized TM* final/tail2/tail3、pair、triple。

## WOF-048 — completed
Batch `b-bdb16c09-b10`：
- identity valid: WOF-048 / WOF-AI-PRIVATE / coordinator-v48
- readOnly=true / ramWrites=0
- 1 joined / 1 complete / 0 error / 0 interrupted
- embedded WOF-048R identity passed
- pure 3P room, player histogram `[0,0,0,495]`
- 11997 polls / 39546 enemy samples / 164 ACTIVE edges
- 19 signals / **19 strict** / 0 jitter / 0 late / 0 hard miss / 0 censored

### WOF-048 production audit
- T20: 6/6 strict A5136/target/side，lead481.0..799.5ms。
- D867: 11/11 strict A3232/target/side，lead99.2..111.3ms，T33=1/T9=10。
- D881: 2/2 strict A3232/target/side，lead99.9/109.3ms。
- T16/T24/T18 had zero coverage in this room only; no negative evidence。

### WOF-048 T23 result
Dedicated trace probe had:
```text
t23Samples = 0
attackZeroStarts = 0
activeEdges = 0
resolvedCycles = 0
t23CycleTraces = []
t23SequenceSummary.totalCycles = 0
```
Therefore WOF-048 adds **no T23 discriminator evidence**. This is pure coverage absence, not a sequence-model failure. The WOF-048 retarget fix / TM* sequence summary were not exercised for T23 in this batch.

## Current next — WOF-049
```text
resume = wof-resume-dispatch-selector-v59
nextCopyId = WOF-049
nextScript = wof_future_danger_multiroom_coordinator_v49.js
nextMarker = === WOF FUTURE DANGER MULTIROOM COORDINATOR V49 JSON ===
embedded = WOF-049R / wof_future_danger_cycle_validator_v49r.js
```

### WOF-049 purpose
- semantic repeat of WOF-048 sequence instrumentation with fresh IndexedDB v11。
- continue all production audits。
- continue T23 ordered traces + active-edge retarget logging + TM* sequence summary。
- no new T23 rule is promoted before repeated attack-specific sequence evidence exists。
- **Prefer several rooms, ideally up to5 in parallel**: WOF-048 had only one room and zero T23, so current bottleneck is scene/coverage probability rather than sampling logic。

Detailed reports:
- `reports/WOF-047_ANALYSIS.md`
- `reports/WOF-048_ANALYSIS.md`

## 禁止误判
- +0x70 = exact hitbox/damage onset ❌
- absDx = causal timing law ❌
- warning entry target = final lock ❌
- T16 B4 = exclusive A6432 ❌
- T20 1250 / D867220 / D881135 = causal boundary ❌
- retired fixed-lag T24 rules / old T23 BODY4920/B0 复活 ❌
- zero coverage = forward failure ❌
- 当前少量 T23 traces 就直接 promotion ❌

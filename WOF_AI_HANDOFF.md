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

## T23 current
- old BODY4920/B0 rule retired。
- WOF-045 short candidate `S0/A6/B4 BODY4976 FE84868 NX83F20 V0 TM5 -> A4792` 后续多批 rawMatch0/signals0；在无 T23 的批次属于 zero coverage，不是 failure。
- WOF-047 ordered tracer 仍是最新正面 T23 sequence evidence：唯一 T23 房间 8 resolved cycles，A4792=3 / A4920=3 / A5888=2。
- 单 state attack-ambiguous；必须使用 ordered tail / transition pair / triple。
- active-edge retarget logging fix 与 exact-TM + TM* sequence summaries 保持启用。

## WOF-049 — completed
Batch `b-106c5a3c-819`：
- identity valid: WOF-049 / WOF-AI-PRIVATE / coordinator-v49
- readOnly=true / ramWrites=0
- 5 joined / 5 complete / 0 error / 0 interrupted
- embedded WOF-049R identity passed
- mixed player histogram `[27,1087,196,1134]`; room peakPlayers `3,1,3,1,3`
- 60000 polls / 194328 enemy samples / 1166 ACTIVE edges
- 106 signals / **106 strict** / 0 jitter / 0 late / 0 hard miss / 0 censored

### WOF-049 production audit
- T16: 31/31 strict，lead10.0..21.6ms；本批 A6432=31/31，target/side31/31。
- T20: 4/4 strict A5136/target/side，lead430.2..629.1ms。
- D867: 13/13 strict A3232/target/side，lead29.9..120.1ms；T9=11/T33=2；P1/P2/P3 均覆盖。
- D881: 4/4 strict A3232/target/side，lead100.0..108.8ms；本批 T11=4。
- T24 A5440: 19/19 strict；T24 A5424: 21/21 strict，target21/21，side20/21；唯一 side mismatch 是 CENTER entry -> RIGHT ACTIVE，不是 hard miss。
- T18 A5440: 7/7 strict；T18 A5424: 7/7 strict。

### WOF-049 T23 result
五个房间 **全部没有 T23**：
```text
per-room t23Samples = 0
attackZeroStarts = 0
activeEdges = 0
resolvedCycles = 0
t23CycleTraces = []
t23SequenceSummary.totalCycles = 0
```
aggregate type census 也没有 T23。故 WOF-049 没有新增 T23 discriminator evidence；这是 room/scene coverage absence，不是 sequence logic failure。

## Current next — WOF-050
```text
resume = wof-resume-dispatch-selector-v60
nextCopyId = WOF-050
nextScript = wof_future_danger_multiroom_coordinator_v50.js
nextMarker = === WOF FUTURE DANGER MULTIROOM COORDINATOR V50 JSON ===
embedded = WOF-050R / wof_future_danger_cycle_validator_v50r.js
IndexedDB = wof-future-danger-multiroom-v12
```

### WOF-050 purpose
- semantic coverage-repeat of current production + T23 ordered-sequence instrumentation。
- no production demotion; no T23 promotion。
- keep active-edge retarget logging and exact-TM + TM* final/tail2/tail3/pair/triple summaries。
- **Prefer up to5 rooms in parallel**；当前唯一瓶颈是拿到真正含 T23 的 scene/room。
- 若出现 T23，优先比较 A4792/A4920/A5888 的 repeated ordered sequence families，再决定是否生成 prospective discriminator。

Detailed reports:
- `reports/WOF-047_ANALYSIS.md`
- `reports/WOF-048_ANALYSIS.md`
- `reports/WOF-049_ANALYSIS.md`

## 禁止误判
- +0x70 = exact hitbox/damage onset ❌
- absDx = causal timing law ❌
- warning entry target = final lock ❌
- T16 B4 = exclusive A6432 ❌
- T20 1250 / D867220 / D881135 = causal boundary ❌
- retired fixed-lag T24 rules / old T23 BODY4920/B0 复活 ❌
- zero coverage = forward failure ❌
- 当前 sparse T23 traces 直接 promotion ❌

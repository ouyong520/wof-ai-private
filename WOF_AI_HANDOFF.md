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
```text
attack==0 current cycle
-> same-cycle state / ordered-sequence discovery
-> prospective arm
-> same enemy future 0->nonzero ACTIVE
-> verify attack / live target / side / lead / miss
```
fixed-lag 只能 discovery/correlation；held state 使用 once-per-zero-cycle level arm。单 state 若跨多个 attack，必须升级到 ordered sequence/context。

## 多房 coordinator
```text
Worker = collect (~120s/room)
top    = finalize + download exactly one merged JSON
max 5 rooms
no short join window
1P/2P/3P allowed
```
同一条 JS 在 Worker 与 top 使用。

## Current production set
- `T16_B4_DANGER_40`: imminent-danger production-shadow；禁止解释为 A6432-exclusive。
- `T20_5136_B0_TO_B255_1250`: production-shadow-coarse；1250ms 只是 audit horizon。
- `D867BA_3232_TM6_220`: production-shadow。
- `D8811E_3232_TM6_135`: production-shadow；135ms 只是 audit horizon。
- T24 BODY7512/TM3 -> A5440: production-shadow。
- T24 BODY7520/TM4 -> A5424: production-shadow。
- T18 BODY7512/TM4 -> A5440: production-shadow。
- T18 BODY7520/TM4 -> A5424: production-shadow。

## T23 current
- old BODY4920/B0 rule retired。
- WOF-047 ordered tracer 仍是最新正面 T23 sequence evidence：8 resolved cycles，A4792=3 / A4920=3 / A5888=2。
- 单 state attack-ambiguous；必须使用 ordered tail / transition pair / triple。
- active-edge retarget fix 与 exact-TM + TM* sequence summaries 保持启用。
- WOF-049 的5房 + WOF-050 的3房 + WOF-051 的3房都没有 T23；这是 scene/room coverage absence，不是 tracer failure。

## WOF-051 — completed
Batch `b-2f39eb3f-4a7`：
- identity valid: WOF-051 / WOF-AI-PRIVATE / coordinator-v51
- readOnly=true / ramWrites=0
- 3 joined / 3 complete / 0 error / 0 interrupted
- all embedded WOF-051R validations passed
- player histogram `[0,488,488,492]`; effectively one pure3P room + one pure1P room + one pure2P room
- 35999 polls / 108463 enemy samples / 558 ACTIVE edges
- 145 signals / 144 strict / 0 jitter / 1 realLate / 0 hard miss / 0 censored
- the lone realLate belongs to the experimental T18 A4704 candidate, not an existing production rule

### WOF-051 production audit
- T16: 98/98 strict danger, lead8.9..21.0ms；A6432=97/A4840=1；target/side98/98。
- T20: 5/5 strict A5136/target/side，lead380.9..639.7ms。
- D867: 10/10 strict A3232/target/side，lead99.1..109.4ms；T33=8/T9=2；P1/P2/P3 targets covered。
- D881: 22/22 strict A3232/target/side，lead98.6..119.2ms；T34=15/T11=7。
- T24 两条 zero coverage，不是负证据。
- T18 A5440: 4/4 strict，lead62.3..70.9ms；target/side4/4。
- T18 A5424: 4/4 strict，lead69.1..70.0ms；target/side4/4。

### WOF-051 T23
三个房间 dedicated tracer 全部：
```text
t23Samples = 0
attackZeroStarts = 0
activeEdges = 0
resolvedCycles = 0
```
aggregate type census 也没有 T23。

## Critical result: WOF-050 T18 A4704 single-state candidate is ambiguous
WOF-050 discovery state：
```text
S0/A4/B2|BODY4728|FE8b660|NX8b204|Vffff|TM1|P6C4736
```
WOF-051 direct prospective once-per-zero-cycle arm produced exactly 2 evaluable cycles：
```text
A4704 @ 19.9ms
A4712 @ 100.4ms
```
- expected A4704 rate = 1/2
- target stable 2/2
- side stable 2/2
- 0 hard miss

结论：该 state 确实是 forward-relevant，但**不是 A4704-specific**。禁止 promotion，也不再作为 A4704 predictor。必须研究它之后的 ordered transition/context 来区分 A4704 vs A4712。

## Current next — WOF-052
```text
resume = wof-resume-dispatch-selector-v62
nextCopyId = WOF-052
nextScript = wof_future_danger_multiroom_coordinator_v52.js
nextMarker = === WOF FUTURE DANGER MULTIROOM COORDINATOR V52 JSON ===
embedded = WOF-052R / wof_future_danger_cycle_validator_v52r.js
IndexedDB = wof-future-danger-multiroom-v14
```

### WOF-052 purpose
1. 保持全部 production audits。
2. 保持 T23 ordered tracer / exact-TM + TM* summaries。
3. 移除 BODY4728/A4/B2/TM1 作为 A4704 predictor 的 promotion 路线；只视为 attack-ambiguous discovery state。
4. 新增 ordered T18 candidate-context tracer：
   - record all T18 zero->ACTIVE cycles；
   - mark exact BODY4728/A4/B2/TM1 occurrence；
   - preserve ordered distinct states；
   - `t18CandidateSequenceSummary` 仅聚合 candidate-containing cycles；
   - 按 eventual activeAttack 分组 exact/TM* final/tail2/tail3 + transition pair/triple；
   - 优先寻找 A4704 vs A4712 的 post-candidate discriminator。
5. 新 sequence 仍是 discovery only，之后必须另建 prospective ordered validator 才能 promotion。
6. prefer multiple rooms, ideally up to5；最好至少一个含 T18 的房间。

Detailed reports:
- `reports/WOF-049_ANALYSIS.md`
- `reports/WOF-050_ANALYSIS.md`
- `reports/WOF-051_ANALYSIS.md`

## 禁止误判
- +0x70 = exact hitbox/damage onset ❌
- absDx = causal timing law ❌
- warning entry target = final lock ❌
- T16 B4 = exclusive A6432 ❌
- audit horizon = causal boundary ❌
- retired fixed-lag T24 rules / old T23 BODY4920/B0 复活 ❌
- zero coverage = forward failure ❌
- sparse sequence discovery 直接 production ❌
- T18 BODY4728/A4/B2/TM1 = A4704-specific predictor ❌

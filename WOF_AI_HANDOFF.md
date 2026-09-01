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
- `T16_B4_DANGER_40`: imminent-danger production-shadow；禁止 attack-exclusive 语义。
- `T20_5136_B0_TO_B255_1250`: production-shadow-coarse；1250ms 不是 causal boundary。
- `D867BA_3232_TM6_220`: production-shadow。
- `D8811E_3232_TM6_135`: production-shadow；135ms 仅 audit horizon。
- T24 BODY7512/TM3 -> A5440: production-shadow。
- T24 BODY7520/TM4 -> A5424: production-shadow。
- T18 BODY7512/TM4 -> A5440: production-shadow。
- T18 BODY7520/TM4 -> A5424: production-shadow。

## T23 current
- old BODY4920/B0 rule retired。
- WOF-047 ordered tracer 仍是最新正面 T23 sequence evidence：8 resolved cycles，A4792=3 / A4920=3 / A5888=2。
- 单 state attack-ambiguous；必须使用 ordered tail / transition pair / triple。
- active-edge retarget logging fix 与 exact-TM + TM* sequence summaries 保持启用。
- WOF-049 的5房 + WOF-050 的3房都没有 T23；这是 scene/room coverage absence，不是 tracer failure。

## WOF-050 — completed
Batch `b-f8bbda7c-fae`：
- identity valid: WOF-050 / WOF-AI-PRIVATE / coordinator-v50
- readOnly=true / ramWrites=0
- 3 joined / 3 complete / 0 error / 0 interrupted
- embedded WOF-050R identity all passed
- player histogram `[112,0,868,488]`，本批有效游戏覆盖为 2P/3P
- 36000 polls / 104337 enemy samples / 495 ACTIVE edges
- 98 signals / 96 strict / 0 jitter / 2 realLate / 0 hard miss / 0 censored

### WOF-050 production audit
- T16: 72/72 strict，lead9.7..21.2ms；A6432=71/A4832=1；target/side72/72。再次确认 danger rule 不可解释为 A6432-exclusive。
- T20: 4/4 strict A5136/target/side，lead599.4..989.7ms。
- D867: 18/18 strict A3232/target/side，lead79.7..110.1ms；T9=12/T36=1/T33=5。
- D881: 2/2 strict A3232/target/side，lead109.7/110.8ms；T11=2。
- T24 两条本批 zero coverage，不是负证据。
- T18 A5440: 1 correct tail hit，lead138.6ms；T18 A5424: 1 correct tail hit，lead128.5ms。两者 expected attack/target/side 全正确，均在250ms tail内，只是超出 legacy 90ms audit horizon；不降级，90ms 不是 causal boundary。

### WOF-050 T23
三个房间 dedicated tracer 全部：
```text
t23Samples = 0
attackZeroStarts = 0
activeEdges = 0
resolvedCycles = 0
```
aggregate type census 也没有 T23。

## WOF-050 新 discovery：T18 A4704
Broad `cyclePrecursorTop` 得到：

```text
T18 -> ACTIVE A4704
S0/A4/B2|BODY4728|FE8b660|NX8b204|Vffff|TM1|P6C4736
```

same-cycle evidence：
- 18 resolved cycles
- attack-zero only
- target 18/18
- side 18/18
- first-seen lead 50.5..188.6ms, median80.3
- last-seen lead 29.6..51.1ms, median40.5

此证据足够进入 prospective candidate，但尚未 promotion。

## Current next — WOF-051
```text
resume = wof-resume-dispatch-selector-v61
nextCopyId = WOF-051
nextScript = wof_future_danger_multiroom_coordinator_v51.js
nextMarker = === WOF FUTURE DANGER MULTIROOM COORDINATOR V51 JSON ===
embedded = WOF-051R / wof_future_danger_cycle_validator_v51r.js
IndexedDB = wof-future-danger-multiroom-v13
```

### WOF-051 purpose
1. 保持全部 production audits。
2. 保持 T23 ordered traces / exact-TM + TM* summaries。
3. 新增 prospective candidate：
   `T18_4704_BODY4728_A4_B2_TM1_LEVEL_80`
   - exact state as above
   - expected ACTIVE A4704
   - horizon80ms / tail250ms
   - once-per-zero-cycle level arm
   - live +0x7E target / side validation
4. 不因 WOF-050 T18 128–139ms 的 clean tail hits 降级旧 T18 rules。
5. prefer multiple rooms, ideally up to5。

Detailed reports:
- `reports/WOF-048_ANALYSIS.md`
- `reports/WOF-049_ANALYSIS.md`
- `reports/WOF-050_ANALYSIS.md`

## 禁止误判
- +0x70 = exact hitbox/damage onset ❌
- absDx = causal timing law ❌
- warning entry target = final lock ❌
- T16 B4 = exclusive A6432 ❌
- T20 1250 / D867220 / D881135 / T18 legacy90 = causal boundary ❌
- retired fixed-lag T24 rules / old T23 BODY4920/B0 复活 ❌
- zero coverage = forward failure ❌
- sparse T23 traces 直接 promotion ❌
- WOF-050 T18 A4704 same-cycle discovery 直接当 production ❌

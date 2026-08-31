# WOF Future Danger AI — 最新交接 / START HERE

更新时间：2026-08-31  
仓库：`ouyong520/wof-ai-private`  
项目：Project A — Browser/MAME/gstyphoon.js Future Danger

## 强制协议
- 回传先校验 `copyId/project/version/marker/readOnly/ramWrites`。
- RAM 默认只读，`ramWrites=0`。
- Assistant 负责分析、GitHub 修改、版本推进。
- 多房间保留 per-room 边界。
- `enemy+0x7E` 必须实时重读；warning entry target 不能冻结成最终目标。

## 已锁死底层
- P1/P2/P3 `0xFFBE1C / 0xFFBEFC / 0xFFBFDC`
- enemy pool `0xFFC0BC`, stride `0xE0`, 20 slots
- enemy target `+0x7E=0/4/8 -> P1/P2/P3`
- selector / player table / dispatcher44 / descriptor consumer `0x247C` 已解决
- `enemy+0x70 U16 0->nonzero` = ACTIVE-start convention，不是 exact hitbox/damage onset

## WOF-043 — completed
Batch `b-e6844556-f8b`：
- 5 joined / 5 complete / 0 error / 0 interrupted
- `readOnly=true / ramWrites=0`
- 59894 polls / 182907 enemy samples / 889 ACTIVE edges
- 112 signals = 112 strict + 0 jitter + 0 late + 0 hard miss
- retargets=0
- player histogram `[0P18,1P458,2P1465,3P484]`
- 5/5 embedded WOF-043R identity validations passed

### T24 BODY7512/TM3 -> A5440
`T24_5440_CYCLE_BODY7512_TM3_80`
- 18 signals / 18 strict / 0 miss
- A5440=18/18
- target=18/18
- side=18/18
- lead49.4..58.7ms
- 3 rooms

=> **production-shadow** confirmed again.

### T24 BODY7520/TM4 -> A5424
`T24_5424_CYCLE_BODY7520_TM4_S24_LEVEL_90`
- level visibility rawMatch=36
- once-per-zero-cycle armed signals=21
- 21/21 strict
- A5424=21/21
- target=21/21
- side=21/21
- lead60.8..71.5ms
- 3 rooms

=> **production-shadow**.

This directly proves the WOF-042 `rawMatch17 / transitionEntry0 / signals0` problem was an entry-detector blind spot, not rule failure. The correct semantics are: state99 2/4 + BODY7520/TM4 held-state visibility, arm once per zero->ACTIVE cycle.

### T20 B0->B255 -> A5136
`T20_5136_B0_TO_B255_1250`
- 9/9 strict
- A5136/target/side=9/9
- lead458.6..800.2ms
- 3 rooms

=> remains **production-shadow-coarse**. 1250ms is audit window only, never countdown/causal threshold.

### D867BA / D8811E
- `D867BA_3232_TM6_220`: 35/35 strict，A3232/target=35/35，side=34/35；types T9/T33/T36；all5 rooms => production-shadow.
- `D8811E_3232_TM6_135`: 9/9 strict，A3232/target/side=9/9；types T34/T37/T11；3 rooms => production-shadow.

### T16 B4
`T16_B4_DANGER_40`：20/20 strict，all A6432 in this batch，target20/20，side19/20，0 retargets。

=> imminent-danger production-shadow remains strong. Historical A4832/A4840 counterexamples remain authoritative, so attack identity is still not exclusive A6432.

### T23
Old `T23_4792_BODY4920_B0_ENTRY_180` again had `rawMatch=0 / signals=0` despite6490 T23 samples and9 A4792 edges.

=> old rule is now explicitly **retired-no-forward-coverage**. Do not revive it.

The global `cyclePrecursorTop` can be dominated by high-frequency types, so WOF-044 adds dedicated per-room `cyclePrecursorFocus.T23` and `cyclePrecursorFocus.T18` arrays, each derived only from same-cycle attack-zero states that later resolve into 0->nonzero ACTIVE.

## Current next — WOF-044
```text
resume = wof-resume-dispatch-selector-v54
nextCopyId = WOF-044
nextScript = wof_future_danger_multiroom_coordinator_v44.js
nextMarker = === WOF FUTURE DANGER MULTIROOM COORDINATOR V44 JSON ===
embedded = WOF-044R / wof_future_danger_cycle_validator_v44r.js
```

### WOF-044 目的
- 两条 T24 规则都按 production-shadow 继续 prospective audit。
- T20 coarse、D867、D881、T16 继续审计。
- old T23 BODY4920/B0 标记 retired。
- 新增 focused same-cycle mining：
  - `cyclePrecursorFocus.T23`：专门寻找新的 T23 forward precursor。
  - `cyclePrecursorFocus.T18`：扩大 A5440/A5424 等相邻攻击族覆盖。
- 不再让低频 type 因 global top100 排名被挤掉。

### 操作
最多5个 live `gstyphoon.js` Worker 运行同一条 WOF-044，每房约120秒。全部结束后切 `top` 再运行同一条，生成唯一 `WOF-044_<batchId>.json`。

## 禁止误判
- broad T16 FAST/MID / broad T30_FAST ❌
- absDx/距离 = hitbox或timing threshold ❌
- warning entry target = 最终锁定目标 ❌
- T16 B4 = 100% exclusive A6432 ❌
- T20 1250ms / D867220 / D881135 = causal boundary ❌
- retired fixed-lag T24 BODY5424/5440 复活 ❌
- old T23 BODY4920/B0 prospective 复活 ❌

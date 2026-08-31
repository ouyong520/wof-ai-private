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

## WOF-042 — completed
Batch `b-14ce196a-f24`：
- 5 joined / 5 complete / 0 error / 0 interrupted
- `readOnly=true / ramWrites=0`
- 59816 polls / 190429 enemy samples / 1018 ACTIVE edges
- 93 signals = 92 strict + 1 jitter + 0 late + 0 hard miss
- player histogram `[0P0,1P105,2P1058,3P1264]`
- 5/5 embedded WOF-042R identity validations passed

### T24 BODY7512/TM3 -> A5440
`T24_5440_CYCLE_BODY7512_TM3_80`
- 11 signals / 11 strict / 0 miss
- A5440 = 11/11
- target = 11/11
- side = 11/11
- lead 49.0..58.2ms
- 2 rooms

=> **production-shadow**.

### T24 BODY7520/TM4 -> A5424
`T24_5424_CYCLE_BODY7520_TM4_90`
- rawMatch=17
- transitionEntry=0，故旧 arm-on-entry matcher 没有产生 forward watch
- 但 same-cycle miner 在本轮直接看到：
  - S2/A2/B4 BODY7520 FE8AF6C NX8A6E4 V180001 TM4：6 cycles，A5424 6/6，first lead61.6..71.6ms，target/side6/6
  - S4/A2/B4 同 descriptor：5 cycles，A5424 5/5，first lead61.5..71.2ms，target/side5/5

解释：这是 **entry detector blind spot**。状态在首次观察时可能已经 held，因此 `entry(base,s,p)` 不会 arm；不能把 0 signals 当成候选失败。

WOF-043 改成：
- state99 允许 2/4
- `match = base(s)` level trigger
- `arm()` 仍由 existing cycle id 去重，所以每个 zero->ACTIVE cycle 只 arm 一次
- horizon90 / tail250
- 直接检验“现在观察到该 held state 是否能 forward 预测 A5424”

### T20 B0->B255 -> A5136
WOF-042：6/6 strict，A5136/target/side=6/6，lead420.6..580.6ms，跨3房。

结合 WOF-037/WOF-039/WOF-041 same-cycle evidence，升为 **production-shadow-coarse**。1250ms 是审计窗口，不是 countdown 或因果阈值。

### D867BA / D8811E
- D867BA_3232_TM6_220：14/14 strict，A3232/target/side14/14，types T9/T33，跨4房 => production-shadow。
- D8811E_3232_TM6_135：6/6 strict，A3232/target/side6/6，types T11/T34，跨3房 => production-shadow。

### T16 B4
56/56 在40ms+jitter范围进入 ACTIVE danger；A6432=54，A4832=2。
但本轮出现2个 retarget：
- P1 -> P3 at17.1ms
- P1 -> P2 at20.3ms
两次都发生在 ACTIVE 边缘。

=> danger timing 规则仍强；但 warning entry 的目标不是100%锁定。生产层必须在决策时实时读 `enemy+0x7E`。

### T23
旧 `BODY4920/B0` prospective rule 再次 rawMatch=0，即使本轮有5116 T23 samples、15次 A4792。
=> 旧规则退役；继续从 same-cycle miner 找新前驱，不再围绕旧 fixed-lag signature 打转。

## Current next — WOF-043
```text
resume = wof-resume-dispatch-selector-v53
nextCopyId = WOF-043
nextScript = wof_future_danger_multiroom_coordinator_v43.js
nextMarker = === WOF FUTURE DANGER MULTIROOM COORDINATOR V43 JSON ===
embedded = WOF-043R / wof_future_danger_cycle_validator_v43r.js
```

### WOF-043 目的
- T24 BODY7512/TM3 S2 -> A5440 作为 production-shadow 继续复核。
- 直接 forward 验证 T24 BODY7520/TM4 state99 2/4 -> A5424 的 **cycle-level trigger**。
- T20 按 production-shadow-coarse 复核。
- D867/D881 production-shadow 复核。
- T16 继续记录 retarget，明确 danger 与 target-lock 是两个不同置信度。
- same-cycle miner 继续为 T23/其他攻击寻找新候选。

### 操作
最多5个 live `gstyphoon.js` Worker 运行同一条 WOF-043，每房约120秒。全部结束后切 `top` 再运行同一条，生成唯一 `WOF-043_<batchId>.json`。

## 禁止误判
- broad T16 FAST/MID / broad T30_FAST ❌
- absDx/距离 = hitbox或timing threshold ❌
- warning entry target = 最终锁定目标 ❌
- T16 B4 = 100% exclusive A6432 ❌
- T20 1250ms / D867220 / D881135 = causal boundary ❌
- retired fixed-lag T24 BODY5424/5440 复活 ❌
- 旧 T23 BODY4920/B0 继续作为 prospective candidate ❌

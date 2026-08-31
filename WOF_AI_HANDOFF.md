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

## WOF-044 — completed
Batch `b-62677eb2-642`：
- 5 joined / 5 complete / 0 error / 0 interrupted
- `readOnly=true / ramWrites=0`
- 59988 polls / 211029 enemy samples / 1057 ACTIVE edges
- 132 signals / 130 strict / 0 jitter / 1 real-late / 0 hard miss / 1 censored
- retargets=1
- player histogram `[0P49,1P0,2P1412,3P979]`
- 5/5 embedded WOF-044R identity validations passed

### Production rules
- `T20_5136_B0_TO_B255_1250`: **13/13 strict**, A5136/target/side=13/13, lead410.5..869.5ms，3 rooms。保持 `production-shadow-coarse`。
- `D867BA_3232_TM6_220`: **39/39 strict**, A3232/target/side=39/39，types T33/T9，all5 rooms。保持 production-shadow。
- `D8811E_3232_TM6_135`: 14/14 最终 A3232/target/side；13 strict + 1 clean real-late at209.5ms，0 miss。保持 production-shadow；135ms 只是 audit horizon。
- `T24_5440_CYCLE_BODY7512_TM3_80`: 10 signals，9 evaluable/9 strict；第10个在采集结束前约28ms发出后被 censored，不算 miss。9个解析结果全部 A5440/target/side，lead49.6..59.9ms。
- `T24_5424_CYCLE_BODY7520_TM4_S24_LEVEL_90`: **9/9 strict**, A5424/target/side=9/9，lead60.0..71.0ms。
- `T16_B4_DANGER_40`: **47/47 danger timing hit**；A6432=46、A4832=1；一次 P3->P1 retarget 与 ACTIVE 同时发生，继续证明 entry target 不是最终锁定目标。

## WOF-044 focused-mining bug
WOF-044 的 model 文本声称会输出 `cyclePrecursorFocus.T23/T18`，但实际 JSON 结果对象里 **没有 `cyclePrecursorFocus` 字段**。

因此：
- WOF-044 没有完成原定的 T23 focused capture。
- 不能把“没有 T23 focus 数组”解释成“没有 T23 前驱”；这是 exporter/包装器缺陷。
- old `T23_4792_BODY4920_B0_ENTRY_180` 仍然 rawMatch=0，在本轮3810 T23 samples / 15 A4792下继续没有 forward coverage，逻辑上保持 retired。

## T18 新候选
虽然 focused export 失效，global `cyclePrecursorTop` 在唯一 T18 房间仍保留了两条强 same-cycle 候选：

1. A5440:
   - `S2/A2/B4|BODY7512|FE8BBB2|NX8B290|V180001|TM4|P6C0`
   - 9/9 cycles -> A5440
   - first lead60.2..70.5ms
   - target/side9/9

2. A5424:
   - `S2/A2/B4|BODY7520|FE8BBDE|NX8B2A4|V180001|TM4|P6C0`
   - 9/9 cycles -> A5424
   - first lead60.7..71.1ms
   - target/side9/9

=> 目前仍是 discovery evidence；WOF-045 将直接 forward 验证。

## Current next — WOF-045
```text
resume = wof-resume-dispatch-selector-v55
nextCopyId = WOF-045
nextScript = wof_future_danger_multiroom_coordinator_v45.js
nextMarker = === WOF FUTURE DANGER MULTIROOM COORDINATOR V45 JSON ===
embedded = WOF-045R / wof_future_danger_cycle_validator_v45r.js
```

### WOF-045 目的
- 用独立并行 focus miner **真正输出** `cyclePrecursorFocus.T23` 与 `.T18`，每房最多120条。
- 不再依赖 WOF-044 那个只改 model 文本、却没有把字段接到 result 的脆弱 patch。
- 直接 prospective 验证两条 T18：
  - `T18_5440_CYCLE_BODY7512_TM4_LEVEL_90`
  - `T18_5424_CYCLE_BODY7520_TM4_LEVEL_90`
- 两条都用 once-per-zero-cycle level arm，horizon90/tail250。
- T16/T20/D867/D881/T24 继续 production audit。

### 操作
最多5个 live `gstyphoon.js` Worker 运行同一条 WOF-045，每房约120秒。全部结束后切 `top` 再运行同一条，生成唯一 `WOF-045_<batchId>.json`。

## 禁止误判
- broad T16 FAST/MID / broad T30_FAST ❌
- absDx/距离 = hitbox或timing threshold ❌
- warning entry target = 最终锁定目标 ❌
- T16 B4 = 100% exclusive A6432 ❌
- T20 1250ms / D867220 / D881135 = causal boundary ❌
- retired fixed-lag T24 BODY5424/5440 复活 ❌
- old T23 BODY4920/B0 prospective 复活 ❌
- WOF-044 缺 `cyclePrecursorFocus` = 没有 T23 前驱 ❌

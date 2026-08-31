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

## WinKawaks Collector v1 — 已交付 / AI 调用入口
本地采集平台与 Browser Future Danger 项目分离。需要本地 WinKawaks 高速 RAM 证据时先读 `COLLECTOR_ROUTING.md`。本地证据必须回到 Browser/Web 生产语境验证后才能升级正式规则。

## 当前并行研究拓扑 — 必须先读
本项目现在明确允许主线与多条 WinKawaks discovery 研究线并发推进。完整协议见 `PARALLEL_RESEARCH.md`。

```text
MAINLINE  = 当前 Browser/Web Future Danger 主线（以本文件 Current next 为准）
GEO-*     = WinKawaks 人物几何/坐标研究
EFIELD-*  = WinKawaks enemy 0xE0 字段地图研究
RAWMINE-* = WinKawaks raw diff/transition/offset-ranking 研究
```

四条线可同时推进，但必须隔离：GEO/EFIELD/RAWMINE 不得修改、推进或重写当前 WOF 主线 coordinator/validator，不得改变 production-shadow 规则，不得把 WinKawaks 本地 offset 直接升级成 Browser/WASM production 结论。

多个 AI 可以同时向 Collector 提交任务；Collector 只拥有一个 WinKawaks runtime，并严格串行执行采集，因此是“AI producer 并发、模拟器 capture 串行”。各并行线使用独立 taskId 前缀，按 `taskId + taskBlobSha` 接受自己的结果。

并行 AI 收到操作员只发 `继续` 时，应检查自己 lane 的 GitHub 任务/结果、继续分析并决定下一轮采集；除非确实需要 operatorGate 场景，不要让操作员搬运 JSON/log/hash/raw。主线生产结论仍以 Browser/Web prospective validation 为最终权威。

## WOF-045 — completed
Batch `b-c45e8d2d-d9d`：
- 5 joined / 5 complete / 0 error / 0 interrupted
- `readOnly=true / ramWrites=0`
- 59994 polls / 202612 enemy samples / 1025 ACTIVE edges
- 137 signals / 137 strict / 0 jitter / 0 real-late / 0 hard miss / 0 censored
- retargets=0
- player histogram `[0P119,1P42,2P1179,3P1088]`
- 5/5 embedded WOF-045R identity validations passed

### Production rules
- `T20_5136_B0_TO_B255_1250`: **10/10 strict**, A5136/target/side=10/10, lead460.0..1020.1ms，3 rooms。`production-shadow-coarse`。
- `D867BA_3232_TM6_220`: **41/41 strict**, A3232/target/side=41/41，types T9/T33，all5 rooms。production-shadow。
- `D8811E_3232_TM6_135`: **14/14 strict**, A3232/target/side=14/14，lead99.0..109.8ms。production-shadow。
- `T24_5440_CYCLE_BODY7512_TM3_80`: **14/14 strict**, A5440/target/side=14/14，lead49.1..59.4ms。production-shadow。
- `T24_5424_CYCLE_BODY7520_TM4_S24_LEVEL_90`: **15/15 strict**, A5424/target/side=15/15，lead59.9..71.0ms。production-shadow。
- `T16_B4_DANGER_40`: **23/23 strict danger timing**，本轮23次均A6432，target/side=23/23。历史 A4832/A4840 与 retarget 反例继续有效，所以禁止 exclusive attack / frozen-target 语义。

## WOF-045 focused mining — exporter bug 已修复
WOF-045 实际 JSON 已真正包含 `cyclePrecursorFocus`：
- room1：T23 populated，120 entries
- room2：T23 populated，120 entries
- room5：T18 populated，120 entries
- 没有 T23/T18 的房间为空数组，属于正常结果

因此 WOF-044 的 missing-field 问题已经解决。

## T18 — direct prospective 通过
WOF-044 discovery 后，WOF-045 直接 forward 验证：

1. `T18_5440_CYCLE_BODY7512_TM4_LEVEL_90`
   - signature `S2/A2/B4|BODY7512|FE8BBB2|NX8B290|V180001|TM4|P6C0`
   - 10/10 strict
   - A5440/target/side=10/10
   - lead60.5..70.4ms

2. `T18_5424_CYCLE_BODY7520_TM4_LEVEL_90`
   - signature `S2/A2/B4|BODY7520|FE8BBDE|NX8B2A4|V180001|TM4|P6C0`
   - 10/10 strict
   - A5424/target/side=10/10
   - lead61.5..70.3ms

结合 WOF-044 各9/9 same-cycle discovery，WOF-046 起两条都升 **production-shadow**。

## T23 — 新 focused candidate
旧 `T23_4792_BODY4920_B0_ENTRY_180` 继续 retired；WOF-045 仍 rawMatch=0。

新的短 lead 分支：
- `S0/A6/B4|BODY4976|FE84868|NX83F20|V0|TM5|P6C0`
- active attack A4792
- 4/4 same-cycle
- first lead79.3,79.5,81.1,89.4ms
- target/side=4/4

=> WOF-046 新 rule：`T23_4792_BODY4976_A6_B4_TM5_LEVEL_100`，once-per-zero-cycle level arm，horizon100 / tail300，直接 prospective 验证。

另一个 T23 房间存在不同的长 lead 分支，例如 `S2/A4/B0|BODY0|FE84A98|NX83D14|V100000|TM20|P6C0`，当前只有2 cycles，first lead约1.4–2.9s。仅继续 focused mining，不 promotion。

## Current next — WOF-046
```text
resume = wof-resume-dispatch-selector-v56
nextCopyId = WOF-046
nextScript = wof_future_danger_multiroom_coordinator_v46.js
nextMarker = === WOF FUTURE DANGER MULTIROOM COORDINATOR V46 JSON ===
embedded = WOF-046R / wof_future_danger_cycle_validator_v46r.js
```

### WOF-046 目的
- T18 两条规则按 production-shadow 继续 audit。
- 直接 prospective 验证新 T23 A4792 TM5 short-lead rule。
- 保留 WOF-045 已修好的 `cyclePrecursorFocus.T23/T18`，继续发现 alternate T23 branch。
- T16/T20/D867/D881/T24 继续 production audit。

### 操作
最多5个 live `gstyphoon.js` Worker 运行同一条 WOF-046，每房约120秒。全部结束后切 `top` 再运行同一条，生成唯一 `WOF-046_<batchId>.json`。

## 禁止误判
- broad T16 FAST/MID / broad T30_FAST ❌
- absDx/距离 = hitbox或timing threshold ❌
- warning entry target = 最终锁定目标 ❌
- T16 B4 = 100% exclusive A6432 ❌
- T20 1250ms / D867220 / D881135 = causal boundary ❌
- retired fixed-lag T24 BODY5424/5440 复活 ❌
- old T23 BODY4920/B0 prospective 复活 ❌
- alternate long-lead T23 branch 仅2 cycles就 promotion ❌

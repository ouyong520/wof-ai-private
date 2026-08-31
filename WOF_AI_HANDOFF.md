# WOF Future Danger AI — 最新交接 / START HERE

更新时间：2026-08-31
仓库：`ouyong520/wof-ai-private`
项目：Project A — Browser/MAME/gstyphoon.js Future Danger

> 与 `ouyong520/wof-winkawaks-bridge` 完全分开。

## 强制协议
- 每轮只使用一个唯一 copyId；回传先校验 `copyId/project/version/marker/readOnly/ramWrites`。
- RAM 默认只读，`ramWrites=0`。
- Assistant 负责分析、GitHub 修改、版本推进。
- 多房间 batch 仍然使用**同一条 WOF-039 命令**；由于各 `gstyphoon.js` 是彼此隔离的 Worker，同一命令需分别贴入各房间 Worker，不能从一个 Worker 直接 eval 其他既有 Worker。

## 已锁死底层
- P1/P2/P3 `0xFFBE1C / 0xFFBEFC / 0xFFBFDC`
- enemy pool `0xFFC0BC`, stride `0xE0`, 20 slots
- enemy authoritative target `+0x7E=0/4/8 -> P1/P2/P3`
- selector、player pointer table、dispatcher44 incoming edges、descriptor consumer `0x247C` 已解决
- `enemy+0x70 U16 0->nonzero` 仅 ACTIVE-start convention，不是 exact hitbox/damage onset

## 当前规则状态
- T16 exact B4 -> A6432 = `production-shadow`，已有 LEFT+RIGHT 强覆盖。
- T20 `B0->B255` -> A5136 = `production-shadow-candidate`：WOF-037 forward prospective 6/6 strict，attack/target/side 6/6，LEFT1 RIGHT5，lead 418.6..680.1ms；只称 coarse early warning。
- T33/T34 TM6 -> A3232 = type-specific `production-shadow-candidates`。
- `D867BA_3232_TM6_120` / `D8811E_3232_TM6_120` = descriptor-family prospective，等待 forward evidence。
- T24 四条 exact TM2 与 T23 B0 保留 prospective，等待 coverage。

## WOF-037 最新完成结果
身份正确，readOnly=true，ramWrites=0；120002.3ms / 10ms；40039 enemy samples；140 ACTIVE edges。

### T20 A5136
`T20_5136_B0_TO_B255_700`：6 signals / 6 evaluable / 6 strict / 0 late / 0 hard miss；expected A5136 6/6；target 6/6；side 6/6；lead 418.6,458.6,530.1,647.8,670.1,680.1ms。
Entry absDx 与 lead 无可信单调关系，不得制造 distance threshold。

### 3232 descriptor-family discovery
- T9 `BODY2872 FE867BA NX85ECE V100000 A4/B2 TM6 P6C2784`：3 个 retrospective ~100ms -> A3232。
- T11 `BODY2872 FE8811E NX879E2 V100000 A4/B2 TM6 P6C2784`：2 个 retrospective ~100ms -> A3232。
与历史 T33/T34 exact TM6 结构一致，但 T9/T11 仍需 forward prospective。

## WOF-039 多房间批量采集
当前 frontier：
```text
version = wof-resume-dispatch-selector-v49
nextCopyId = WOF-039
nextScript = wof_future_danger_multiroom_batch_v39.js
nextMarker = === WOF FUTURE DANGER MULTIROOM BATCH V39 JSON ===
```

### 工作方式
1. 第一个房间启动 WOF-039 后创建 shared batch。
2. 在 **45 秒 join window** 内，把**同一条 WOF-039 命令**贴入另外 3~4 个 live `gstyphoon.js` Worker；最多5房。
3. 每房独立运行 embedded WOF-038 约120秒，互不混数据。
4. 每房额外记录：`roomId`、玩家数量直方图、玩家 presence 变化、enemy type composition、`+0x7E` target distribution。
5. 当前没有已证明的 authoritative scene/stage RAM field，因此这些只叫 `contextTimeline/context fingerprint`，不能冒充正式 scene ID。
6. 每房结果写入 same-origin IndexedDB；某房关闭时其他房仍可继续，最终标记 interrupted。
7. join window 关闭且房间完成后，一个 elected Worker 自动输出**一份合并 WOF-039 JSON**。
8. 合并 JSON 同时保留 per-room 原始 WOF-038 result，并生成 aggregate diagnostics/ruleStats；分析时先看 per-room，再看 aggregate。

### Embedded WOF-038
- `D867BA_3232_TM6_120`
- `D8811E_3232_TM6_120`
- `T20_5136_B0_TO_B255_700`
- opportunistic T16/T23/四条 T24
- fallback mining 仍只算 discovery/correlation

## 禁止误判
- broad T16 FAST/MID ❌
- broad T30_FAST ❌
- absDx130 / T20 absDx = hitbox或timing threshold ❌
- T16 4840 divergence production ❌
- retrospective lag = fixed-time predictor ❌
- mined correlation = prospective proof ❌
- 把不同房间先混合再判断规则 ❌
- 未证明 RAM field 就声称精确 scene/stage ID ❌

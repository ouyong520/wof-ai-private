# WOF Future Danger AI — CURRENT FRONTIER

更新时间：2026-08-31
仓库：`ouyong520/wof-ai-private`
项目：Project A — Browser / MAME / gstyphoon.js Future Danger

## 当前阶段
selector / dispatcher / descriptor 已解决。当前重点是：扩大 Future Danger coverage、跨 enemy type 泛化、跨房间 forward prospective 验证。

## Ground truth
- enemy `+0x7E` authoritative target；P1/P2/P3 = 0/4/8
- `enemy+0x70 U16 0->nonzero` = ACTIVE-start convention，不是 exact hitbox/damage onset
- T16 exact B4 = production-shadow
- T20 B0->B255 -> A5136 = production-shadow-candidate，coarse early warning
- T33/T34 TM6 -> A3232 = type-specific production-shadow-candidates
- D867BA / D8811E TM6 -> A3232 = descriptor-family prospective
- T24 exact TM2 / T23 B0 = prospective pending coverage

## WOF-037 completed evidence
120002.3ms/10ms；40039 samples；140 ACTIVE edges。

`T20_5136_B0_TO_B255_700`：6/6 strict，expected A5136 6/6，target 6/6，side 6/6，LEFT1 RIGHT5，lead 418.6..680.1ms。
=> production-shadow-candidate；不把宽 lead 称精确 countdown；不从 absDx 推 timing boundary。

WOF-037 fallback 还在新 type 上看到旧 descriptor 结构复现：
- T9 `FE867BA/NX85ECE/BODY2872/V100000/A4/B2/TM6/P6C2784`：3 retrospective ~100ms -> A3232
- T11 `FE8811E/NX879E2/.../TM6`：2 retrospective ~100ms -> A3232
与历史 T33/T34 一致，但 T9/T11 仍需 forward prospective。

## Current next — WOF-039 multiroom batch
```text
resume = wof-resume-dispatch-selector-v49
nextCopyId = WOF-039
nextScript = wof_future_danger_multiroom_batch_v39.js
nextMarker = === WOF FUTURE DANGER MULTIROOM BATCH V39 JSON ===
```

### Why WOF-039
单房120秒经常因房间 enemy type 不同而 coverage=0。WOF-039 把 WOF-038 嵌入最多5个不同 live room Worker，同时保留每房边界，再自动合并。

### Batch protocol
- 同一条 WOF-039 命令分别贴到 4~5 个 `gstyphoon.js` Worker；不是4~5条不同脚本。
- 第一个 Worker 建 batch；其余 Worker 必须在45秒 join window内加入；最多5房。
- 每房独立跑 embedded WOF-038 120秒。
- Same-origin IndexedDB 保存 per-room result；最终一个 Worker自动输出一份 merged WOF-039 JSON。
- 输出包含每房 player-count histogram / presence changes / enemy-type composition / authoritative target distribution。
- 目前没有被证明的正式 scene/stage RAM address，所以 `contextTimeline` 只是场景上下文 fingerprint，不称 scene ID。
- aggregate ruleStats 附带 `roomsWithSignal / roomsWithRawMatch / perRoom / entryTypeCounts`；必须先看 per-room 再作跨房间结论。
- 房间中途关闭不会污染其他房；deadline 后在 merged result 中标为 interrupted。

### Embedded WOF-038 targets
- `D867BA_3232_TM6_120` type-agnostic forward entry
- `D8811E_3232_TM6_120` type-agnostic forward entry
- `T20_5136_B0_TO_B255_700` reconfirmation
- opportunistic T16/T23/four T24 exact candidates
- fallback terminal/fixed-lag mining remains discovery only

## Do not redo / revive
- P1/P2/P3 identity / +0x7E selector / player table / dispatcher44 / descriptor consumer
- broad T16 FAST/MID
- broad T30_FAST
- absDx130 or T20 absDx as hitbox/range/timing threshold
- T16 4840 divergence
- ambiguous T24 TM3/TM4
- persistent-state retrospective lag as fixed-time warning
- retrospective mining as prospective proof
- arbitrary scene ID without proven RAM field

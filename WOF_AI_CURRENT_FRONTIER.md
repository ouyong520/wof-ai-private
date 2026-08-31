# WOF Future Danger AI — CURRENT FRONTIER

更新时间：2026-08-31
仓库：`ouyong520/wof-ai-private`
项目：Project A — Browser / MAME / gstyphoon.js Future Danger

## 当前阶段
selector / dispatcher / descriptor 已解决。当前重点：固化 descriptor-family production shadows，并把 same-cycle attack-zero mining 转成真正的 forward prospective T24/T23 规则。

## WOF-041 completed
身份严格通过：`WOF-041 / WOF-AI-PRIVATE / wof-future-danger-multiroom-coordinator-v41 / marker`，`readOnly=true`，`ramWrites=0`。

Batch `b-281d582f-3a0`：5 joined / 5 complete / 0 error / 0 interrupted；59937 polls；191524 enemy samples；1166 ACTIVE edges；232 signals；229 strict；2 jitter；0 late；1 watcher hard-miss。

player-count samples `[1,0,865,1559]` = 0P/1P/2P/3P；本轮主要2P/3P，1P链路已由WOF-040证明。

### T16 B4 danger
172/172 <=40ms ACTIVE danger；target/side172/172；A6432=170，A4832=1，A4840=1。

=> **imminent-danger production-shadow**，不允许 exclusive A6432 语义。

### T20 B0->B255 -> A5136
28 signals；27 strict<=850ms；1 watcher hard-miss；27个已解析全部 A5136/target/side，lead409.4..799.9ms。

same-cycle miner 在 hard-miss 所在房对 B255->A5136 记录14 cycles，firstLead max=1190.4ms，target/side14/14。该房 watcher同样14 signals，因此更像1100ms tail过短。

=> 保持 strong coarse `production-shadow-candidate`；WOF-042 audit horizon=1250ms，tail=1500ms；仍不是 countdown/因果边界。

### D867BA -> A3232
WOF-041 `D867BA_3232_TM6_220` = 10/10 strict，A3232/target/side10/10，lead100.1..200ms。

结合 WOF-040 的跨 `T36/T9/T33` 33/33 expected attack/target/side evidence：

=> 升 **type-agnostic production-shadow**。

### D8811E -> A3232
22/22 A3232/target/side；20 strict<=120ms +2 jitter120.1/120.9ms；0 late/miss；types T11=6,T34=16。

=> 保持 **production-shadow**；下一轮 audit horizon=135ms，仅吸收边界 jitter。

## T24 breakthrough — same-cycle real precursors
旧四条 fixed-lag 来源 T24 rules 再次 rawMatch=0 / transitionEntry=0，即使本轮有 T24 samples9198、A5440=23、A5424=21；旧 BODY5424/5440 rules 继续退役。

same-cycle `+0x70==0` miner 在两个独立房间都找到：

### A5440 candidate
`S2/A2/B4|BODY7512|FE8AF46|NX8A6D0|V180001|TM3|P6C0`
- 8+8 = 16 cycles
- first lead49.0..59.6ms
- target/side16/16

### A5424 candidate
`S2/A2/B4|BODY7520|FE8AF6C|NX8A6E4|V180001|TM4|P6C0`
- 8+8 = 16 cycles
- first lead49.5..70.3ms
- target/side16/16

=> 这是与旧 fixed-lag signature 不同的 **current-cycle precursor**。WOF-042 将直接 arm-on-entry 做 prospective 验证。

## T23
A4792 same-cycle 目前只有单房4-cycle evidence；长持久状态，target/side约0.75。暂不 promotion。

## Current next — WOF-042
```text
resume = wof-resume-dispatch-selector-v52
nextCopyId = WOF-042
nextScript = wof_future_danger_multiroom_coordinator_v42.js
nextMarker = === WOF FUTURE DANGER MULTIROOM COORDINATOR V42 JSON ===
embedded = WOF-042R / wof_future_danger_cycle_validator_v42r.js
```

### WOF-042 protocol
- dual-mode multiroom 不变：Worker=ROOM-COLLECT；top=FINALIZE+下载唯一JSON。
- 无短 join window；最多5房；每房约120秒；fresh IndexedDB v4。
- embedded WOF-042R：
  - `T24_5440_CYCLE_BODY7512_TM3_80` prospective
  - `T24_5424_CYCLE_BODY7520_TM4_90` prospective
  - D867 production-shadow / 220ms
  - D881 production-shadow / 135ms audit
  - T16 imminent-danger
  - T20 1250ms horizon /1500ms tail coarse audit
  - 继续 same-cycle `cyclePrecursorTop`

## Ground truth / exclusions
- `enemy+0x7E` authoritative target；0/4/8=P1/P2/P3
- `enemy+0x70 U16 0->nonzero` 只是 ACTIVE-start convention
- 不恢复 broad T16 FAST/MID / broad T30_FAST
- 不把 absDx 当 hitbox/range/timing threshold
- 不声称 T16 B4 exclusive A6432
- 不把 T20 1250ms / D867220 / D881135 当 causal boundary
- retrospective fixed-lag 不能冒充 prospective proof
- 不复活旧 T24 BODY5424/5440 fixed-lag rules
- 未证明的 RAM field 不能叫 scene/stage ID

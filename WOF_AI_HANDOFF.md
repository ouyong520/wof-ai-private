# WOF Future Danger AI — 最新交接 / START HERE

更新时间：2026-08-31
仓库：`ouyong520/wof-ai-private`
项目：Project A — Browser/MAME/gstyphoon.js Future Danger

> 与 `ouyong520/wof-winkawaks-bridge` 完全分开。

## 强制协议
- 回传先校验 `copyId/project/version/marker/readOnly/ramWrites`。
- RAM 默认只读，`ramWrites=0`。
- Assistant 负责分析、GitHub 修改、版本推进。
- 多房间必须保留 per-room 边界，不能先混合再判断规则。

## 已锁死底层
- P1/P2/P3 `0xFFBE1C / 0xFFBEFC / 0xFFBFDC`
- enemy pool `0xFFC0BC`, stride `0xE0`, 20 slots
- enemy authoritative target `+0x7E=0/4/8 -> P1/P2/P3`
- selector / player table / dispatcher44 / descriptor consumer `0x247C` 已解决
- `enemy+0x70 U16 0->nonzero` = ACTIVE-start convention，不是 exact hitbox/damage onset

## WOF-041 — 已完成 5 房 batch
身份严格通过：`WOF-041 / WOF-AI-PRIVATE / wof-future-danger-multiroom-coordinator-v41 / marker`，`readOnly=true`，`ramWrites=0`。

Batch `b-281d582f-3a0`：
- joined 5 / complete 5 / error 0 / interrupted 0
- 59937 polls
- 191524 enemy samples
- 1166 ACTIVE edges
- 232 signals
- 229 strict + 2 jitter + 0 real-late + 1 watcher hard-miss
- player-count samples `[0P1,1P0,2P865,3P1559]`；本轮主要是2P/3P。1P workflow 已由 WOF-040 证明。

### T16 exact B4 danger
`T16_B4_DANGER_40`：172/172 在40ms内进入 ACTIVE danger；target/side=172/172；attack identity = A6432 170 + A4832 1 + A4840 1。

结论：继续是 **imminent-danger production-shadow**。A6432 只作 specificity audit，禁止 exclusive 语义。

### T20 B0->B255 -> A5136
`T20_5136_B0_TO_B255_850`：28 signals；27 strict，1 watcher hard-miss；被解析的27次全部 A5136/target/side=27/27，lead 409.4..799.9ms。

同一个 hard-miss 所在房的 same-cycle miner 对 B255 signature 记录了14个 A5136 cycle，其中 first-lead 最大 1190.4ms，且 target/side 14/14 稳定。结合该房 watcher=14 signals，这个 hard-miss 更像1100ms tail过短，而不是明确 false positive。

下一轮只把 audit horizon/tail 放宽到 **1250/1500ms**；仍称 coarse early warning，不称 countdown/因果边界。

### D867BA descriptor family -> A3232
`D867BA_3232_TM6_220`：10/10 strict<=220ms；A3232/target/side=10/10；lead100.1..200ms；本轮 type=T33。

结合 WOF-040 已有跨 `T36/T9/T33` 的33/33 expected attack/target/side 证据，现升为 **type-agnostic production-shadow**。

### D8811E descriptor family -> A3232
`D8811E_3232_TM6_120`：22/22 最终 A3232/target/side；20 strict<=120ms + 2 jitter 120.1/120.9ms；0 late / 0 miss；types `T11=6,T34=16`。

继续 **production-shadow**。下一轮 audit horizon 调到135ms，只为吸收边界 jitter，不代表因果阈值。

### T24 — WOF-041 发现真正 same-cycle 前驱
旧四条 fixed-lag 来源 T24 rule 再次 `rawMatch=0 / transitionEntry=0`，即使本轮 T24 samples=9198、A5440=23、A5424=21。因此旧 BODY5424/5440 fixed-lag 规则继续退役。

same-cycle attack-zero miner 找到两条新的、真实位于当前攻击周期中的状态：

1. A5440 prospective candidate
   - `S2/A2/B4|BODY7512|FE8AF46|NX8A6D0|V180001|TM3|P6C0`
   - 两房各8 cycle，共16
   - first lead 49.0..59.6ms
   - target/side=16/16

2. A5424 prospective candidate
   - `S2/A2/B4|BODY7520|FE8AF6C|NX8A6E4|V180001|TM4|P6C0`
   - 两房各8 cycle，共16
   - first lead 49.5..70.3ms
   - target/side=16/16

这两条与旧 fixed-lag BODY5424/5440 signature 不同，WOF-042 将直接做 forward prospective entry 验证。

### T23
same-cycle A4792 当前只得到单房4-cycle 证据，状态持续时间长，target/side rate约0.75；暂不升 prospective rule。

## Current next — WOF-042
```text
resume = wof-resume-dispatch-selector-v52
nextCopyId = WOF-042
nextScript = wof_future_danger_multiroom_coordinator_v42.js
nextMarker = === WOF FUTURE DANGER MULTIROOM COORDINATOR V42 JSON ===
embedded = WOF-042R / wof_future_danger_cycle_validator_v42r.js
```

### WOF-042 目的
- 直接 prospective 验证新 T24：
  - `T24_5440_CYCLE_BODY7512_TM3_80`
  - `T24_5424_CYCLE_BODY7520_TM4_90`
- D867 status=production-shadow，220ms复核。
- D881 production-shadow，audit horizon=135ms。
- T16 imminent-danger 继续复核。
- T20 audit horizon=1250ms、tail=1500ms；仍 coarse warning。
- 继续 `cyclePrecursorTop`，用于 T23/其他 type 的同周期前驱发现。

### 操作
- 最多5个 live `gstyphoon.js` Worker 运行同一条 WOF-042；每房约120秒。
- 所有房结束后切 `top`，再运行同一条；若仍有活房则拒绝 finalize，否则只下载一份 `WOF-042_<batchId>.json`。

## 禁止误判
- broad T16 FAST/MID / broad T30_FAST ❌
- absDx/距离 = hitbox或timing threshold ❌
- T16 B4 = 100% exclusive A6432 ❌
- T20 1250ms / D867 220ms / D881 135ms = causal boundary ❌
- retrospective fixed-lag fingerprint = forward predictor ❌
- 旧 T24 BODY5424/5440 fixed-lag rule 复活 ❌
- 未证明 RAM field 就声称精确 scene/stage ID ❌

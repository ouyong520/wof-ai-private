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
- selector、player table、dispatcher44 incoming edges、descriptor consumer `0x247C` 已解决
- `enemy+0x70 U16 0->nonzero` 仅 ACTIVE-start convention，不是 exact hitbox/damage onset

## WOF-040 — 已完成 5 房 batch
身份严格通过：`WOF-040 / WOF-AI-PRIVATE / wof-future-danger-multiroom-coordinator-v40 / marker`，`readOnly=true`，`ramWrites=0`。

Batch `b-f998189b-ff0`：
- joined 5 / complete 5 / error 0 / interrupted 0
- 59991 polls
- 198105 enemy samples
- 1002 ACTIVE edges
- 111 signals
- 109 strict + 1 jitter + 1 real-late + 0 hard miss
- multiroom workflow 已证明能收 3P、纯2P(P2+P3)、纯1P(P2)。aggregate player-count samples = `[0P49,1P808,2P538,3P1017]`。

### D8811E descriptor family -> A3232
`D8811E_3232_TM6_120`：24/24 strict<=120ms；A3232=24/24；target=24/24；side=24/24；lead 98.8..112.4ms。

跨 type：`T37=1,T11=10,T34=13`；P1/P2/P3、LEFT/RIGHT 都覆盖；跨3房。

结论：升为 **type-agnostic production-shadow**。

### D867BA descriptor family -> A3232
WOF-040：33/33 都最终 A3232，target/side 33/33；31 strict<=120ms，1 jitter=121ms，1 clean real-late=200ms，0 hard miss。

跨 type：`T36=3,T9=10,T33=20`；P1/P2/P3、LEFT/RIGHT 全覆盖；跨4房。

结论：规则本身强，但 120ms horizon 太窄。升为 **production-shadow-candidate**，下一轮用 220ms audit horizon。200ms 只是观测到的较慢样本，不得从 absDx/距离制造 timing law。

### T16 exact B4
WOF-040：54/54 都在40ms内进入 ACTIVE danger，target/side=54/54；但攻击 identity 为 A6432=53、A4832=1。WOF-039 另有1次 A4840。

结论：T16 exact B4 是 **imminent-danger production-shadow**，不是“100% exclusive A6432”。A6432 继续作为 specificity audit。

### T20 B0->B255 -> A5136
WOF-040 有 T20/A5136 activity，但 exact B0->B255 transition entry=0，所以没有新的 forward 样本，也没有负面证据。

历史 WOF-039 23/23 A5136/target/side，lead442.1..780.8ms；下一轮 audit horizon 调到850ms，仍称 coarse early warning，不称 countdown/因果边界。

### T24/T23 correction
WOF-040 有很强 T24 coverage：T24 samples=6024，A5440=19，A5424=16；但旧四条 T24 exact prospective rule 全部 `rawMatch=0 / transitionEntry=0`。

同时 retrospective `fingerprintTop` 又能在约100ms看到旧 TM2 signature（A5424候选6次，A5440候选5次）。这正说明固定 lag 可能抓到前一攻击周期/非当前 attack-zero 链，不能当 forward proof。

因此：旧 T24 fixed-lag TM2/TM3/TM4 全部降为 retrospective/correlation only。T23 同理继续等待真正 same-cycle evidence。

## Current next — WOF-041
```text
resume = wof-resume-dispatch-selector-v51
nextCopyId = WOF-041
nextScript = wof_future_danger_multiroom_coordinator_v41.js
nextMarker = === WOF FUTURE DANGER MULTIROOM COORDINATOR V41 JSON ===
```

### WOF-041 目的
继续使用已经验证成功的 dual-mode multiroom workflow，但 embedded validator 改成 `WOF-041R`：
- D8811E 按 production-shadow 继续独立复核。
- D867BA 用220ms horizon 复核。
- T16 改成 imminent-danger 语义；A6432 只作为 specificity audit。
- T20 horizon=850ms，仍 coarse early warning。
- 新增 `cyclePrecursorTop`：只统计 **enemy+0x70==0 且位于同一个之后真正 0->nonzero ACTIVE 的 cycle** 中出现过的状态。
- 这条 same-cycle attack-zero 约束专门用来淘汰 fixed-lag 污染，并为 T24/T23 找真正前驱状态。

### WOF-041 操作
- 在最多5个 live `gstyphoon.js` Worker 分别运行同一条 WOF-041；无短 join window；1P/2P/3P 都可。
- 每房约120秒。
- 所有想收的房间结束后切到 `top`，再运行同一条 WOF-041；若仍有活房会拒绝过早 finalize，否则只下载一份 `WOF-041_<batchId>.json`。

## 禁止误判
- broad T16 FAST/MID ❌
- broad T30_FAST ❌
- absDx130 / 距离 = hitbox或timing threshold ❌
- T16 B4 = 100% exclusive A6432 ❌
- T20 850ms / D867 220ms = causal boundary ❌
- retrospective fixed-lag fingerprint = forward predictor ❌
- 旧 T24 fixed-lag TM2/TM3/TM4 直接复活 ❌
- 未证明 RAM field 就声称精确 scene/stage ID ❌

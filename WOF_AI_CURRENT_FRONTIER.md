# WOF Future Danger AI — CURRENT FRONTIER

更新时间：2026-08-31
仓库：`ouyong520/wof-ai-private`
项目：Project A — Browser / MAME / gstyphoon.js Future Danger

## 当前阶段
selector / dispatcher / descriptor 已解决。当前重点：把已验证的 descriptor-family 规则固化成 production shadow，并用 same-cycle attack-zero mining 扩大 T24/T23 等 Future Danger coverage。

## WOF-040 completed
严格身份通过：`WOF-040 / WOF-AI-PRIVATE / wof-future-danger-multiroom-coordinator-v40 / marker`，`readOnly=true`，`ramWrites=0`。

Batch `b-f998189b-ff0`：5 joined / 5 complete / 0 error / 0 interrupted；59991 polls；198105 enemy samples；1002 ACTIVE edges；111 signals；109 strict；1 jitter；1 late；0 hard miss。

多房间 workflow 已验证：包含3P、纯2P(P2+P3)、纯1P(P2)。aggregate player-count samples `[49,808,538,1017]` 对应0P/1P/2P/3P采样。

### D8811E -> A3232
24/24 strict<=120ms；A3232/target/side=24/24；lead98.8..112.4ms；types `T37=1,T11=10,T34=13`；P1/P2/P3、LEFT/RIGHT 全覆盖；跨3房。

=> **production-shadow**。

### D867BA -> A3232
33/33 A3232/target/side；31 strict<=120ms +1 jitter121ms +1 clean late200ms；0 hard miss；types `T36=3,T9=10,T33=20`；P1/P2/P3、LEFT/RIGHT；跨4房。

=> **production-shadow-candidate**。下一轮 audit horizon=220ms；200ms 不是距离/因果 timing law。

### T16 exact B4
54/54 在40ms内进入 ACTIVE danger；target/side54/54；attack=A6432 53 + A4832 1。WOF-039 另有A4840 1。

=> **imminent-danger production-shadow**；禁止 exclusive A6432 语义。

### T20 A5136
WOF-040 exact B0->B255 entry=0；no new evidence，不是 failure。历史 WOF-039 23/23 expected attack/target/side，lead442.1..780.8ms。

=> coarse production-shadow-candidate；下一轮 audit horizon=850ms。

### T24/T23
WOF-040 T24 samples=6024，A5440=19，A5424=16，但旧四条 exact rule rawMatch/entry 全0；与此同时 retrospective fingerprintTop 在100ms又复现旧TM2 signatures（6、5次）。

=> 这些旧 fixed-lag T24 候选不能 forward promotion；最可能的问题是固定 lag 可落到前一攻击周期。必须改用 **same-cycle + attack==0** 的链路证据。

## Current next — WOF-041
```text
resume = wof-resume-dispatch-selector-v51
nextCopyId = WOF-041
nextScript = wof_future_danger_multiroom_coordinator_v41.js
nextMarker = === WOF FUTURE DANGER MULTIROOM COORDINATOR V41 JSON ===
```

### WOF-041 protocol
- 保留 WOF-040 已验证成功的 dual-mode multiroom：Worker=ROOM-COLLECT；top=FINALIZE+下载唯一JSON。
- 无短 join window；1P/2P/3P；最多5房；每房约120秒。
- embedded `WOF-041R`：
  - D8811E status=production-shadow，120ms复核。
  - D867BA status=production-shadow-candidate，horizon=220ms。
  - T16 改名/语义为 `T16_B4_DANGER_40`；A6432 expected rate只作 specificity audit。
  - T20 horizon=850ms，仍 coarse warning。
  - 并行 `cyclePrecursorTop`：只把同一 enemy slot 中 **+0x70==0 时真实观察到、且同一个 cycle 后来发生0->nonzero ACTIVE** 的状态归因给这次攻击。
- fixed-lag `fingerprintTop` 继续保留作 retrospective/correlation 对照，但不允许当 prospective proof。

## Ground truth / exclusions
- `enemy+0x7E` authoritative target；0/4/8=P1/P2/P3
- `enemy+0x70 U16 0->nonzero` 只是 ACTIVE-start convention
- 不恢复 broad T16 FAST/MID / broad T30_FAST
- 不把 absDx 当 hitbox/range/timing threshold
- 不再声称 T16 B4 exclusive A6432
- 不把 T20 850ms / D867 220ms 当 causal boundary
- 不把 retrospective fixed-lag 当 forward predictor
- 不复活旧 T24 fixed-lag TM2/TM3/TM4，除非 same-cycle attack-zero evidence 支持
- 未证明的 RAM field 不能叫 scene/stage ID

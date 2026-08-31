# WOF Future Danger AI — CURRENT FRONTIER

更新时间：2026-08-31  
仓库：`ouyong520/wof-ai-private`

## 阶段
底层 selector/dispatcher/descriptor 已解决。当前是 **production-shadow 扩展 + T23 same-cycle sequence discrimination**。

## WOF-046 两批证据
### Batch A `b-65a0db92-24c`
- 5 joined / 4 complete / 1 interrupted / 0 error
- readOnly=true / ramWrites=0
- 47998 polls / 181961 enemy samples / 989 ACTIVE edges
- 294 signals / 294 strict / 0 hard miss

### Batch B `b-b1f1a5a3-92c`
- 4 joined / 4 complete / 0 interrupted / 0 error
- readOnly=true / ramWrites=0
- 48000 polls / 168660 enemy samples / 958 ACTIVE edges
- 110 signals / 108 strict + 1 jitter + 1 real-late / 0 hard miss
- player histogram `[0,490,489,983]` = 0P/1P/2P/3P

## Combined production audit
- **T16 B4 imminent danger**: 225/225 tail hits = 224 strict +1 jitter; A6432=223, A4840=2; target/side225/225. danger production remains; attack not exclusive.
- **T20 B0->B255 -> A5136**: 14/14 strict A5136/target/side, lead460.8..700.4ms; production-shadow-coarse.
- **D867BA TM6 -> A3232**: 16/16 strict A3232/target/side, lead99.1..119.6ms; production-shadow.
- **D8811E TM6 -> A3232**: 21/21 eventual A3232/target/side;20 strict +1 clean209.5ms real-late,0 miss; production-shadow.
- **T24 BODY7512/TM3 -> A5440**: 28/28 strict, lead48.5..68.5ms.
- **T24 BODY7520/TM4 -> A5424**: 34/34 strict, lead59.9..71.8ms.
- **T18 BODY7512/TM4 -> A5440**: 33/33 strict, lead59.1..78.5ms.
- **T18 BODY7520/TM4 -> A5424**: 33/33 strict, lead58.2..71.3ms.

## T23
旧 BODY4920/B0 继续 retired。

WOF-045 short candidate：
`S0/A6/B4|BODY4976|FE84868|NX83F20|V0|TM5|P6C0 -> A4792`
在两个 WOF-046 batch 都 rawMatch0/signals0，因此是 **zero coverage，不是 failure**。

WOF-046 Batch B 有 7379 T23 samples、12 个 T23 A4792 ACTIVE，但 focused 数据显示常见 single-state fingerprint 会跨 attack：
- `S2/A4/B0 BODY0 FE84A98 NX83D14 TM20` 同时通往 A4792/A4920/A5848；A4792 long-lead branch targetSame 0/4。
- `S0/A4/B2 BODY4936 FE84060 NX83C60 TM1` 同时出现在 A4792 与 A4920。

=> 单一 T23 state 不足以区分 attack branch；下一步改做 ordered transition sequence。

## Current next — WOF-047
```text
resume = wof-resume-dispatch-selector-v57
nextCopyId = WOF-047
nextScript = wof_future_danger_multiroom_coordinator_v47.js
nextMarker = === WOF FUTURE DANGER MULTIROOM COORDINATOR V47 JSON ===
embedded = WOF-047R
```

### WOF-047 protocol
- Worker=collect / top=finalize+one JSON
- fresh IndexedDB v9
- production audits continue
- previous T23 short candidate audit continues
- new `t23CycleTraces` captures up to120 resolved T23 cycles/room
- each trace preserves up to48 ordered distinct states + first/last lead + target/side/retargets + tail1/tail2/tail3
- traces are discovery only; next prospective rule must be built from discriminating sequence evidence

## Exclusions
- +0x70 ≠ exact hitbox/damage onset
- absDx ≠ causal timing law
- warning entry target ≠ final lock
- T16 B4 ≠ exclusive A6432
- T20 1250ms / D867220 / D881135 ≠ causal boundary
- retired fixed-lag T24 BODY5424/5440 不复活
- old T23 BODY4920/B0 不复活
- WOF-046 short T23 rawMatch0 不算失败
- ambiguous T23 single-state 不直接 promotion

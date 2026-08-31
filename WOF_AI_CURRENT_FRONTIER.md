# WOF Future Danger AI — CURRENT FRONTIER

更新时间：2026-08-31
仓库：`ouyong520/wof-ai-private`
项目：Project A — Browser / MAME / gstyphoon.js Future Danger

## 当前阶段
底层 selector / dispatcher / descriptor 已解决。当前只做高可靠 Future Danger 规则扩展与 prospective validation。

## Ground truth / exclusions
- enemy `+0x7E` authoritative target；P1/P2/P3 = 0/4/8
- `enemy+0x70 U16 0->nonzero` 仅 ACTIVE-start convention，不是 exact hitbox/damage onset
- T16 exact B4 = production-shadow
- T33/T34 TM6 attack3232 = production-shadow-candidates
- broad T16 FAST/MID 已否定
- broad T30_FAST 已降级
- absDx130 不是 hitbox/range
- T16 4840 divergence 不是 production
- mined/fixed-lag correlation 不能直接升 production；persistent state 尤其不能把 retrospective 100ms bucket 当成 fixed 100ms predictor

## WOF-036 — latest completed
身份严格通过；readOnly=true；ramWrites=0。
120004.3ms / 10ms；33569 samples；156 ACTIVE edges。

### T16 exact B4
13/13 strict <=40ms；0 jitter / late / hard miss；attack6432 13/13；target 13/13；side 13/13；lead 10.2..20.1ms；entry sides LEFT11 RIGHT2。
=> T16 production-shadow 再次强化，并补到直接 RIGHT 强覆盖。

### T20 A5136 discovery
Exact persistent state：
`S2/A4/B255|BODY0|FE839C4|NX82B0A|V100000|TM20|P6C0`
terminal count22；20/50/100/150/250ms retrospective buckets 全22，500ms 19；target/side stable。

不能将其称 fixed-100ms warning，因为状态持续很久。真正的 live transition：
`S2/A4/B0 ... -> S2/A4/B255 ...`
WOF-036 倒推 mining：17 eventual A5136；lead 369.4..659.2ms；target/side 17/17。当前只是 discovery/correlation。

### T23 A4792 discovery
Exact state：
`S0/A0/B0|BODY4920|FE848E2|NX83C56|V140000|TM1|P6C7904`
100ms retrospective bucket 7/7 eventual A4792；lead sampled 99.9..102.6ms；target/side 7/7；含 opposite-side coverage。需 forward state-entry prospective。

### T20 A4792 discovery
Exact countdown family：
`S0/A6/B4|BODY4976|FE83824|NX82D38|V0|TMx|P6C0`
TM6->TM5 transition：小样本 lead ~69.8..79.9ms；TM3->TM2：~20.4..29.9ms；均 eventual A4792，且已有 LEFT/RIGHT discovery coverage。需 prospective。

### T24 / T33 / T34
WOF-036 coverage仍为0；不升不降。四条 T24 TM2 exact candidates 保留 prospective。

## Current next
```text
resume = wof-resume-dispatch-selector-v47
nextCopyId = WOF-037
nextScript = wof_future_danger_t20_t23_hybrid_prospective_validator_v37.js
nextMarker = === WOF FUTURE DANGER T20 T23 HYBRID PROSPECTIVE VALIDATOR V37 JSON ===
```

WOF-037 是 forward prospective validator：
- `T20_5136_B0_TO_B255_700` expected A5136, horizon700, tail1100
- `T23_4792_BODY4920_B0_ENTRY_180` expected A4792, horizon180, tail500
- `T20_4792_TM6_TO_TM5_110` expected A4792, horizon110, tail300
- `T20_4792_TM3_TO_TM2_60` expected A4792, horizon60, tail220
- opportunistic `T16_6432_B4_40`

信号只在 live forward entry/transition 时 arm；输出 strict/jitter/realLate/hardMiss/expectedAttack/targetSame/sideStable/lead/side coverage。

同时保留轻量 adaptive terminal + 50/100/150/250/500ms mining，避免房间 coverage=0 时完全无数据；这些 fallback mining 数据仍只算 discovery/correlation。

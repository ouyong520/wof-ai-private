# WOF Future Danger AI — 最新交接 / START HERE

更新时间：2026-09-01  
仓库：`ouyong520/wof-ai-private`  
项目：Project A — Browser/MAME/gstyphoon.js Future Danger

## 强制协议
- 回传先校验 `copyId/project/version/marker/readOnly/ramWrites`。
- RAM 默认只读，`ramWrites=0`。
- Assistant 负责分析、GitHub 修改、版本推进。
- 多房间保留 per-room 边界。
- `enemy+0x7E` 必须实时重读；warning entry target 不能冻结成最终目标。
- 每轮只给用户 ONE 条 Browser Console command。

## 已锁死底层
- P1/P2/P3 `0xFFBE1C / 0xFFBEFC / 0xFFBFDC`
- enemy pool `0xFFC0BC`, stride `0xE0`, 20 slots
- enemy target `+0x7E=0/4/8 -> P1/P2/P3`
- selector / player table / dispatcher44 / descriptor consumer `0x247C` 已解决
- `enemy+0x70 U16 0->nonzero` = ACTIVE-start convention，不是 exact hitbox/damage onset

## WinKawaks Collector / 并行线
本地采集与 Browser production 主线严格分离。需要本地 WinKawaks 证据时先读：
- `COLLECTOR_ROUTING.md`
- `PARALLEL_RESEARCH.md`
- `ouyong520/wof-winkawaks-bridge/docs/COLLECTOR_V1_CONTRACT.md`

并行 lane：
```text
MAINLINE  = Browser/Web Future Danger 主线
GEO-*     = WinKawaks 人物几何/坐标
EFIELD-*  = WinKawaks enemy 0xE0 字段地图
RAWMINE-* = WinKawaks raw diff/transition/offset ranking
```
GEO/EFIELD/RAWMINE 不得修改/推进 mainline coordinator/validator 或 production-shadow；WinKawaks 证据只能 discovery，正式升级必须回 Browser/Web prospective 验证。

## 方法论
权威路线：
```text
attack==0 current cycle
-> same-cycle state/sequence mining
-> prospective arm
-> same enemy 0->nonzero ACTIVE
-> verify attack / target / side / lead / miss
```
fixed-lag fingerprint 只能 discovery/correlation。held state 优先 once-per-zero-cycle level arm。

## 多房 coordinator
WOF-040 起已稳定：
```text
Worker = collect (~120s/room)
top    = finalize + download exactly one merged JSON
max 5 rooms
no short join window
1P/2P/3P allowed
```

## WOF-046 — 已完成
两批合并 production audit：
- T16 225/225 danger tail hits；A6432=223 + A4840=2；target/side225/225。
- T20 14/14 strict A5136/target/side。
- D867 16/16 strict A3232/target/side。
- D881 21/21 eventual A3232/target/side，20 strict +1 clean209.5ms late。
- T24 A5440 28/28 strict；T24 A5424 34/34 strict。
- T18 A5440 33/33 strict；T18 A5424 33/33 strict。
- old T23 BODY4920/B0 retired。
- WOF-045 short T23 BODY4976/A6/B4/TM5 在两批 WOF-046 都 rawMatch0/signals0：zero coverage，不是 failure。

## WOF-047 — completed
Batch `b-fbbbc59d-cea`：
- identity valid: WOF-047 / WOF-AI-PRIVATE / coordinator-v47
- readOnly=true / ramWrites=0
- 3 joined / 3 complete / 0 error / 0 interrupted
- 35996 polls / 113581 enemy samples / 644 ACTIVE edges
- 144 signals = 143 strict +1 jitter / 0 hard miss / 0 censored
- player histogram `[0P0,1P0,2P579,3P902]`
- all3 embedded WOF-047R identity validations passed

### Production audit WOF-047
- `T16_B4_DANGER_40`: 94/94 danger tail hits =93 strict+1 jitter；A6432=93,A4832=1；target/side94/94；lead9.0..40.5ms。继续 imminent danger，不是 attack-exclusive。
- `T20_5136_B0_TO_B255_1250`: 本轮0 coverage；不构成负证据。
- `D867BA_3232_TM6_220`: 23/23 strict A3232/target/side；lead98.8..119.5ms；T33=18,T9=5；3/3 rooms。
- `D8811E_3232_TM6_135`: 19/19 strict A3232/target/side；lead99.4..120.4ms；T34。
- T24 A5440 3/3 strict；T24 A5424 3/3 strict。
- T18 A5440 1/1 strict；T18 A5424 1/1 strict。
- WOF-045 short T23 candidate 再次 rawMatch0/signals0；仍是 zero coverage。

## T23 ordered trace breakthrough
WOF-047 的 `t23CycleTraces` 已真实工作。只有 room1 有 T23，得到 8 个 resolved zero->ACTIVE cycles：
```text
A4792 = 3
A4920 = 3
A5888 = 2
```
0 dropped。

### 当前序列结论
T23 的 immediate pre-ACTIVE tail 已经显示明显 branch structure，但样本还不够 promotion。

A4920 的 final branches 包括：
```text
S0/A4/B0 BODY4976 FE84868 NX83c56 V1
S0/A6/B4 BODY4976 FE84868 NX83f20 V0
S0/A4/B10 BODY4952 FE84102 NX83c7e V0
```

A5888 final branches：
```text
S2/A6/B4 BODY4936 FE84060 NX83c60 Vffff
S0/A6/B4 BODY4936 FE84060 NX83c60 Vffff
```
其中一个 A5888 tail3 是：
```text
S0/A8/B2 BODY4936
-> S0/A2/B0 BODY4936
-> S0/A6/B4 BODY4936
-> A5888
```
而 `S0/A8/B2 BODY4936...` 单独也出现在 A4792，进一步证明单 state 不够，order 才有判别力。

A4792 三个 cycle 自身也走不同尾部：
- `... A6/B0 -> A6/B4 -> A2/B0` on BODY4952/FE84140 branch。
- terminal `S0/A8/B2 BODY4936 FE84060...`。
- `S2/A4/B10 BODY4952 FE841b4 -> S2/A2/B0 -> S2/A8/B2 BODY4936`。

=> 当前还没有一个 universal A4792 short sequence；必须继续扩大 cycle 样本并 rank pair/triple。

## WOF-047 tracer instrumentation note
发现一个 trace-only 小问题：如果 target 恰好在与 ACTIVE 0->nonzero 同一 poll 改变，`targetStable=false` 会正确反映变化，但旧 `retargets[]` 不会记录该 active-edge retarget，因为 observer 只在 attack==0 时运行。

WOF-048R 已修：resolve 前若 `lastTarget7E != targetAtActive7E`，追加 `atActiveEdge:true` retarget。

## Current next — WOF-048
```text
resume = wof-resume-dispatch-selector-v58
nextCopyId = WOF-048
nextScript = wof_future_danger_multiroom_coordinator_v48.js
nextMarker = === WOF FUTURE DANGER MULTIROOM COORDINATOR V48 JSON ===
embedded = WOF-048R / wof_future_danger_cycle_validator_v48r.js
```

### WOF-048 目的
- 继续全部 production audit。
- 继续 T23 ordered cycle traces。
- 修 active-edge retarget logging。
- 新增 `t23SequenceSummary`：按 activeAttack 输出 timer-normalized `TM*` family 的 final/tail2/tail3、transition pair、transition triple 频率。
- sequence summary 仍是 discovery；找到重复、attack-specific discriminator 后，再建立下一版 prospective sequence validator。

详细分析：`reports/WOF-047_ANALYSIS.md`

## 禁止误判
- broad T16 FAST/MID / broad T30_FAST ❌
- absDx/距离 = hitbox或timing threshold ❌
- warning entry target = 最终锁定目标 ❌
- T16 B4 = 100% exclusive A6432 ❌
- T20 1250ms / D867220 / D881135 = causal boundary ❌
- retired fixed-lag T24 BODY5424/5440 复活 ❌
- old T23 BODY4920/B0 复活 ❌
- WOF-045 short T23 rawMatch0 = forward failure ❌
- 当前8个 T23 traces 就直接 promotion 新 sequence ❌

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
权威 discovery/validation 路线：
```text
attack==0 current cycle
-> same-cycle state mining
-> prospective arm
-> same enemy 0->nonzero ACTIVE
-> verify attack / target / side / lead / miss
```
fixed-lag fingerprint 只能 discovery/correlation。held state 优先 once-per-zero-cycle level arm，不能只依赖 entry edge。

## 多房 coordinator
WOF-040 起已稳定：
```text
Worker = collect (~120s/room)
top    = finalize + download exactly one merged JSON
max 5 rooms
no short join window
1P/2P/3P allowed
```
同一条 JS 在 Worker 与 top 两种 context 使用。

## WOF-046 — 两个批次已完成分析

### Batch A `b-65a0db92-24c`
- identity valid: WOF-046 / WOF-AI-PRIVATE / coordinator-v46
- readOnly=true / ramWrites=0
- 5 joined / 4 complete / 0 error / 1 interrupted
- 47998 polls / 181961 enemy samples / 989 ACTIVE edges
- 294 signals / 294 strict / 0 miss
- completed-room player histogram `[0P0,1P12,2P1949,3P161]`; interrupted room was 3P
- 4 completed embedded WOF-046R validations passed

### Batch B `b-b1f1a5a3-92c`
- identity valid
- 4 joined / 4 complete / 0 error / 0 interrupted
- 48000 polls / 168660 enemy samples / 958 ACTIVE edges
- 110 signals / 108 strict + 1 jitter + 1 real-late / 0 hard miss
- player histogram `[0P0,1P490,2P489,3P983]`
- all 4 embedded WOF-046R validations passed

### Combined WOF-046 production audit
Across the two returned batches:
- `T16_B4_DANGER_40`: 225/225 danger tail hits = 224 strict + 1 jitter; A6432=223, A4840=2; target/side 225/225. Remains imminent-danger only, not exclusive attack.
- `T20_5136_B0_TO_B255_1250`: 14/14 strict A5136/target/side, lead460.8..700.4ms. Remains production-shadow-coarse.
- `D867BA_3232_TM6_220`: 16/16 strict A3232/target/side, lead99.1..119.6ms. Remains production-shadow.
- `D8811E_3232_TM6_135`: 21/21 eventual A3232/target/side; 20 strict + 1 clean 209.5ms real-late, 0 miss. Remains production-shadow; 135ms is only audit horizon.
- `T24 BODY7512/TM3 -> A5440`: 28/28 strict A5440/target/side, lead48.5..68.5ms.
- `T24 BODY7520/TM4 -> A5424`: 34/34 strict A5424/target/side, lead59.9..71.8ms.
- `T18 BODY7512/TM4 -> A5440`: 33/33 strict A5440/target/side, lead59.1..78.5ms.
- `T18 BODY7520/TM4 -> A5424`: 33/33 strict A5424/target/side, lead58.2..71.3ms.

## T23 — WOF-046 结论
旧 `T23_4792_BODY4920_B0_ENTRY_180` 继续 retired。

WOF-045 discovery 的 short rule：
```text
T23_4792_BODY4976_A6_B4_TM5_LEVEL_100
S0/A6/B4|BODY4976|FE84868|NX83F20|V0|TM5|P6C0
```
在两个新 WOF-046 batch 都：
```text
rawMatch = 0
signals = 0
```
所以目前是 **zero coverage，不是 forward failure**。Batch B 仍有 7379 T23 samples 与 12 个 T23 A4792 ACTIVE，说明新场景里 T23 确实活跃，但走的是其它分支。

focused same-cycle 数据进一步证明：当前常见 T23 单一状态不能直接做 attack-specific production。例：
```text
S2/A4/B0|BODY0|FE84A98|NX83D14|V100000|TM20|P6C0
```
在当前数据里同一 signature 可通往 A4792 / A4920 / A5848；A4792 分支还出现 targetSame=0/4 的长 lead 样本。另一个 `S0/A4/B2|BODY4936|FE84060|NX83C60|VFFFF|TM1|P6C4944` 同样同时出现在 A4792 与 A4920。

=> 现在的问题已从“找单个 T23 fingerprint”转成“找能区分攻击分支的 ordered transition sequence”。

## Current next — WOF-047
```text
resume = wof-resume-dispatch-selector-v57
nextCopyId = WOF-047
nextScript = wof_future_danger_multiroom_coordinator_v47.js
nextMarker = === WOF FUTURE DANGER MULTIROOM COORDINATOR V47 JSON ===
embedded = WOF-047R / wof_future_danger_cycle_validator_v47r.js
```

### WOF-047 目的
- 保留 WOF-046 production audits。
- 保留 WOF-045 short T23 candidate audit；若出现仍直接 prospective 验证。
- 新增 `t23CycleTraces`：每房最多120个 resolved T23 zero->ACTIVE cycle。
- 每个 trace 保存最多48个 distinct states 的有序序列，含 first/last lead、target/side evolution、retargets、tail1/tail2/tail3。
- 用序列/transition pair/triple 区分 A4792、A4920、A5848 等共享单一状态的 T23 分支。
- sequence trace 仍是 discovery evidence；找到稳定 sequence 后再做下一版 prospective validator。

### 操作
最多5个 live `gstyphoon.js` Worker 运行同一条 WOF-047，每房约120秒。全部目标房结束后切 `top` 再运行同一条，生成唯一 `WOF-047_<batchId>.json`。

## 禁止误判
- broad T16 FAST/MID / broad T30_FAST ❌
- absDx/距离 = hitbox或timing threshold ❌
- warning entry target = 最终锁定目标 ❌
- T16 B4 = 100% exclusive A6432 ❌
- T20 1250ms / D867220 / D881135 = causal boundary ❌
- retired fixed-lag T24 BODY5424/5440 复活 ❌
- old T23 BODY4920/B0 复活 ❌
- WOF-046 short T23 rawMatch0 = 规则失败 ❌（只是没有覆盖）
- 把当前 ambiguous T23 single-state 直接 promotion ❌

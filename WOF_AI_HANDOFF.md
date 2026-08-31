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

## WOF-039 — 已完成的 3 房 batch
身份严格通过：`WOF-039 / WOF-AI-PRIVATE / wof-future-danger-multiroom-batch-v39 / marker`，`readOnly=true`，`ramWrites=0`。

Batch `b-cab8bed7-fd3`：
- joined 3 / complete 3 / error 0 / interrupted 0
- 105571 enemy samples
- 515 ACTIVE edges
- 58 signals
- 55 strict + 3 real-late + 0 hard miss
- 这 3 个实际被收进来的房间全是 3P；用户尝试的 2P 房因为 v39 的 45 秒 join window 被拒绝，所以 **WOF-039 没有 2P coverage**。

### T20 B0->B255 -> A5136
WOF-039：23 signals / 23 evaluable；20 strict<=700ms，3 real-late（729.9/740.9/780.8ms），0 hard miss；A5136=23/23，target=23/23，side=23/23；P1=11/P2=4/P3=8；LEFT21/RIGHT2；lead 442.1..780.8ms。

结论：规则本身继续强，700ms 只是过紧的验证 horizon，不是因果 timing boundary。仍定义 coarse early warning；不要从 absDx 造 threshold。

### D867BA descriptor family -> A3232
`D867BA_3232_TM6_120`：6/6 strict，A3232=6/6，target/side=6/6，lead 90.2..120ms；跨两房；entry types `T9=5, T36=1`；P1/P2 与 LEFT/RIGHT 都有覆盖。

这已经是直接 forward 证据，结合历史 T33 5/5 prospective，D867BA family 可升为 **type-agnostic production-shadow-candidate**。

### D8811E descriptor family -> A3232
`D8811E_3232_TM6_120`：3/3 strict，A3232/target/side=3/3，lead 99.6..119.3ms，当前 entry type `T11=3`。

结合历史 T34 3/3 prospective，D8811E family 可升为 **type-agnostic production-shadow-candidate**，但当前新 batch 的 forward 新 type 只有 T11。

### T16 B4 imminent danger
`T16_6432_B4_40`：26/26 <=40ms ACTIVE danger，target/side=26/26；但 attack identity 不是 100% exclusive：A6432=25，A4840=1。

结论：T16 B4 仍是强 **imminent-danger production shadow**，但禁止继续声称“exact B4 必然 A6432”。那 1 个 A4840 必须保留为真实反例。

### T23 / T24
WOF-039 中 T23 B0 与四条 T24 TM2 都是 0 exact entry；仍只是 no coverage，不是 falsification。

## WOF-039 workflow 缺陷
v39 的规则采集结果有效，但批量工作流不合格：
- 45 秒 join window 会阻止后来切入的 1P/2P/3P 房间。
- Worker 没有 `document`，不能直接负责浏览器下载。
- 不应让 Worker 自动猜“所有房间已经加入”。

因此 v39 不再作为下一轮入口。

## Current next — WOF-040
```text
resume = wof-resume-dispatch-selector-v50
nextCopyId = WOF-040
nextScript = wof_future_danger_multiroom_coordinator_v40.js
nextMarker = === WOF FUTURE DANGER MULTIROOM COORDINATOR V40 JSON ===
```

### WOF-040 正确工作方式
同一条 WOF-040 命令按当前 DevTools context 自动选择模式：

1. 在任意 live `gstyphoon.js` Worker 执行：**ROOM-COLLECT**
   - 加入当前 active batch；最多5房。
   - **没有 45 秒 join window**。
   - 1P / 2P / 3P 都允许加入。
   - 每房独立跑 embedded WOF-038 120 秒，并写入 same-origin IndexedDB v2。
   - 记录 player count/presence、enemy types、`+0x7E` target distribution。
   - 房间关闭后 heartbeat 停止。

2. 所有想收的房间都完成后，把 DevTools context 切到 **top**，再运行**同一条 WOF-040 命令**：**TOP-FINALIZE**
   - 如果还有活跃房间，拒绝过早 finalize。
   - 已关闭且 heartbeat 超时的房间标为 `interrupted`。
   - 汇总所有 complete rooms，保留 `rooms[]` per-room 明细。
   - **只生成并下载一份** `WOF-040_<batchId>.json`。
   - finalize 后下一次 Worker 运行会自动创建新 batch。

### Scene policy
尚无已证明的 authoritative stage/scene RAM field；只能把 player presence / enemy-type composition / target distribution 称为 context fingerprint，不能冒充正式 scene ID。

## 禁止误判
- broad T16 FAST/MID ❌
- broad T30_FAST ❌
- absDx130 / T20 absDx = hitbox或timing threshold ❌
- T16 B4 = 100% exclusive A6432 ❌（WOF-039 已有 1 个 A4840 反例）
- T20 700ms = causal boundary ❌
- retrospective lag = fixed-time predictor ❌
- mined correlation = prospective proof ❌
- 未证明 RAM field 就声称精确 scene/stage ID ❌

# WOF Future Danger AI — CURRENT FRONTIER

更新时间：2026-08-31
仓库：`ouyong520/wof-ai-private`
项目：Project A — Browser / MAME / gstyphoon.js Future Danger

## 当前阶段
selector / dispatcher / descriptor 已解决。当前重点：Future Danger 规则扩展、跨 enemy type 泛化、跨房间 forward prospective 验证，以及可靠的多房间采集工作流。

## WOF-039 completed
严格身份通过，readOnly=true，ramWrites=0。

Batch `b-cab8bed7-fd3`：3 joined / 3 complete / 0 error / 0 interrupted；105571 enemy samples；515 ACTIVE edges；58 signals；55 strict；3 late；0 hard miss。

这 3 个有效房间全部是 3P。尝试加入的 2P 房被 v39 的 45 秒 join window 拒绝，因此当前 batch **没有 2P coverage**。

### T20 A5136
`T20_5136_B0_TO_B255_700`：23/23 eventual A5136；target23/23；side23/23；20 strict<=700ms + 3 late（729.9,740.9,780.8ms）；0 hard miss；lead442.1..780.8ms；P1=11,P2=4,P3=8。

=> 继续是强 coarse early warning。700ms horizon 太紧，但不能把新的 800ms 当作因果 threshold。

### D867BA A3232 family
`D867BA_3232_TM6_120`：6/6 strict；A3232/target/side 6/6；lead90.2..120ms；types T9=5,T36=1；跨2房。

=> 直接证明 descriptor family 可跨新 enemy type forward 泛化；结合历史 T33 5/5，升为 type-agnostic `production-shadow-candidate`。

### D8811E A3232 family
`D8811E_3232_TM6_120`：3/3 strict；A3232/target/side 3/3；lead99.6..119.3ms；type T11=3。

=> 结合历史 T34 3/3，升为 type-agnostic `production-shadow-candidate`。

### T16 B4
26/26 在40ms内进入 ACTIVE danger，target/side26/26；但 attack counts = A6432 25 + A4840 1。

=> 保留 imminent-danger production shadow，但取消“B4 必然 A6432”的 exclusive 语义。

### T23/T24
本 batch exact entry=0；no coverage，不是 falsification。

## WOF-039 transport defect
规则证据有效，但 v39 workflow 不再使用：45秒 join window 会丢掉后来加入的房间；Worker 没有 `document`，不能可靠负责下载；自动猜 batch 完结也不合适。

## Current next — WOF-040
```text
resume = wof-resume-dispatch-selector-v50
nextCopyId = WOF-040
nextScript = wof_future_danger_multiroom_coordinator_v40.js
nextMarker = === WOF FUTURE DANGER MULTIROOM COORDINATOR V40 JSON ===
```

### WOF-040 protocol
- **同一条脚本，双模式**。
- 在 live `gstyphoon.js` Worker 运行：加入 active batch 并独立采120秒。
- 无45秒 join window；1P/2P/3P 均允许；最多5房。
- 每房保存到 same-origin IndexedDB v2，保留 roomId / player presence / enemy types / `+0x7E` target context。
- 房间关闭后 heartbeat 停止。
- 所有想收的房间完成后切到 **top**，再运行同一条 WOF-040：
  - 有活跃房间则拒绝提前 finalize。
  - stale room 标 interrupted。
  - 合并 complete rooms，保留 per-room 明细。
  - 只下载一份 `WOF-040_<batchId>.json`。
  - finalize 后下一批自动新建。

Embedded validator 暂时继续使用 WOF-038，以保持与 WOF-039 证据可直接比较；下一步再根据新 batch 决定是否重写 rule pack。

## Ground truth / exclusions
- `enemy+0x7E` authoritative target；0/4/8=P1/P2/P3
- `enemy+0x70 U16 0->nonzero` 只是 ACTIVE-start convention
- 不恢复 broad T16 FAST/MID / broad T30_FAST
- 不把 absDx 当 hitbox/range/timing threshold
- 不再声称 T16 B4 exclusive A6432
- 不把 T20 700ms/800ms 当 causal boundary
- retrospective lag 不能冒充 prospective proof
- 未证明的 RAM field 不能叫 scene/stage ID

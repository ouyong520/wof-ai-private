# WOF-052L 10-Room Endurance Simulation — Fresh Stage

stageId: `WOF052L_10ROOM_ENDURANCE_SIM_V1`
priority: `P1`

## 启动去重守卫
先读取：
- `parallel/PM/STAGE_DEDUP_GUARD.md`
- `parallel/PM/OWNER_INTERVENTION_GATE.md`
- `parallel/PM/PM_CORE_OPERATING_CHARTER.md`
- GitHub 最新状态

若 stop condition 已满足：输出 `ALREADY COMPLETE — SAFE TO CLOSE — 当前线程空闲` 并停止。
若 `parallel/PM/STAGE_CLAIMS/WOF052L_10ROOM_ENDURANCE_SIM_V1.json` 已存在：输出 `ALREADY CLAIMED — SAFE TO CLOSE — 当前线程空闲` 并停止。
否则原子 create-file claim；成功后才工作；完成/阻断更新 claim。

## 为什么现在可以并行
当前 Recorder hardening 正在修改 `parallel/WOF052L_RECORDER/**`。本 stage 不修改 Recorder，只在独立目录构造可重放/可加速的 10-room endurance simulation，提前发现 1h/2h/overnight 才会暴露的编排、finalization、analysis/handoff 问题，减少 Owner 白跑长采集的风险。

## 只允许写入
- `parallel/WOF052L_ENDURANCE_SIM/**`

禁止修改：
- `parallel/WOF052L_RECORDER/**`
- `parallel/BROWSER_FLEET/**`
- `parallel/WOF052L_LIVE_CAPTURE/**`
- `parallel/WOF052L_ANALYSIS/**`
- `parallel/WOF052L_PROSPECTIVE_HANDOFF/**`
- `product/alpha/**`

## 必须读取（只读）
- 当前 WOF052L Recorder / Fleet supervisor / live capture / analyzer / prospective handoff contracts
- 现有历史 capture JSON / fixture / schema

## 目标
构造 synthetic/replay endurance harness，模拟 10 个独立 endpoint/room，支持时间加速，不要求真实浏览器。

至少覆盖：
1. 10 rooms 同时正常运行 1h 等价时间；
2. 2h 等价时间；
3. overnight 等价时间；
4. 单房 disconnect，其他 9 房继续；
5. Worker reload/replacement，仅对应房间 epoch/reset；
6. page close/finalize；
7. browser endpoint stale/recover；
8. checkpoint 周期写入；
9. per-room final JSON；
10. merged run JSON；
11. Ctrl+C / graceful shutdown 等价路径；
12. abrupt child failure 后证据保留；
13. analyzer watch/final pass 的 fixture 兼容；
14. prospective handoff 输入冻结/hash compatibility；
15. 10-room room/session isolation，无串采；
16. readOnly=true / ramWrites=0 / inputInjection=false safety assertions。

如果当前 hardening 期间 schema/entrypoint 变化，本 harness 结束前必须重新读取最新 HEAD 并重新跑 compatibility；不得修改 Recorder 去迁就 harness。

## 输出
- machine-readable endurance matrix JSON；
- 中文结果摘要；
- 失败时精确指出属于 Recorder / orchestration / analyzer / handoff 哪一层；
- 可重复运行的一键离线入口。

## Stop condition
`WOF052L 10-ROOM ENDURANCE SIM READY`

必须证明长时编排/收尾/隔离的 repository-side 可模拟部分已经尽量覆盖；仍只能由真实长采集证明的事实单独列出。不得要求 Owner 真人运行。
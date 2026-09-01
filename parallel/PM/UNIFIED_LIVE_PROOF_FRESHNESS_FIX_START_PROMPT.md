# WOF Unified Live Proof Freshness / Child Health Fix — Fresh Stage

stageId: `UNIFIED_LIVE_PROOF_FRESHNESS_FIX_V1`
priority: `P1`

## 启动去重守卫
先读取 `parallel/PM/STAGE_DEDUP_GUARD.md`、`parallel/PM/OWNER_INTERVENTION_GATE.md`、`parallel/LIVE_PROOF_BUNDLE_QA_FAILCLOSED/RESULT.md` 与最新 GitHub。

若等价修复已完成：`ALREADY COMPLETE — SAFE TO CLOSE — 当前线程空闲`，停止。
若 claim `parallel/PM/STAGE_CLAIMS/UNIFIED_LIVE_PROOF_FRESHNESS_FIX_V1.json` 已存在：`ALREADY CLAIMED — SAFE TO CLOSE — 当前线程空闲`，停止。
否则原子 claim 后工作。

## 写入范围
只允许：
- `parallel/LIVE_PROOF_BUNDLE/**`
- mandatory stage claim

不要修改 PYLAUNCH / Recorder / Fleet / Prospective / Alpha。

## 精确 P1
Fresh QA 已证明两条 false-PASS 风险：
1. 空/部分 process-health mapping 会被错误解释为 known+healthy；
2. PYLAUNCH 旧 PASS JSON 即使 `lastUpdateUtc` 极度 stale、child 仍未退出，也可能继续作为当前 authority。

## 必须修复
1. process health 结构必须完整且 fail closed：PYLAUNCH/Recorder required/live facts 必须显式存在、可判定、当前。
2. 缺字段、null、不完整、malformed mapping 不得 healthy。
3. 对所有可授权 PASS 的 child success 引入 current freshness/generation 语义；优先消费 PYLAUNCH `lastUpdateUtc`，必要时增加 bundle-local heartbeat/generation interpretation，但不要修改 PYLAUNCH。
4. stale positive history 只能诊断，不得授权 readiness。
5. Owner prompt 前和 Owner answer 后都重新做 freshness/current-state gate。
6. live-but-hung child + stale success 必须 BLOCKED，即使进程没有 exit。
7. 保留 sticky blocker、Recorder fatal generation、evidence preservation、longCaptureAutoStarted=false。
8. 保持中文 owner UX 和 readOnly / ramWrites=0 / inputInjection=false / no Worker replacement。
9. 吸收 QA adversarial fixture并扩展 stale/malformed/current recovery vectors。
10. 不要求 Owner 真人 Browser。

## Stop condition
`UNIFIED LIVE PROOF FRESHNESS FIX READY — READY FOR FRESH INDEPENDENT QA`

任何 stale/unknown child success 仍能使 overallResult=PASS 或 tenRoomLongCaptureReady=true 时必须 BLOCKED。
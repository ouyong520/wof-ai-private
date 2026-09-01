# WOF Unified Windows Live Proof Fail-Closed — Fresh Independent QA

stageId: `UNIFIED_WINDOWS_LIVE_PROOF_FAILCLOSED_QA_V1`

## 启动去重守卫

先读取：
- `parallel/PM/STAGE_DEDUP_GUARD.md`
- `parallel/PM/OWNER_INTERVENTION_GATE.md`
- `parallel/LIVE_PROOF_BUNDLE/FAILCLOSED_FIX_RESULT.md`
- GitHub 默认分支最新状态

若本 QA stop condition 已有 durable 结果：输出 `ALREADY COMPLETE — SAFE TO CLOSE — 当前线程空闲` 并停止。
若 `parallel/PM/STAGE_CLAIMS/UNIFIED_WINDOWS_LIVE_PROOF_FAILCLOSED_QA_V1.json` 已存在：输出 `ALREADY CLAIMED — SAFE TO CLOSE — 当前线程空闲` 并停止。
否则原子 create-file claim，成功后才开始；完成/阻断更新 claim。

## 独立 QA 边界

只允许写：
- `parallel/LIVE_PROOF_BUNDLE_QA_FAILCLOSED/**`
- mandatory PM stage claim

严禁修改：
- `parallel/LIVE_PROOF_BUNDLE/**`
- PYLAUNCH / Fleet / Recorder / Prospective / Alpha

发现问题只报告，不修；任何修复必须 fresh fix thread。

## QA 目标

重新验证此前 Unified Proof P1：任何 fatal/blocker/stale child success 都不能产生 PASS，也不能进入不该出现的 Owner playability prompt。

至少独立验证：
1. Recorder admission 后 fatal => current admission authority 立即撤销；
2. blocker + simulated Owner Y => 仍 BLOCKED；
3. PYLAUNCH exit-after-PASS => BLOCKED；
4. Recorder exit-after-admission => BLOCKED；
5. child health unknown => 不可 PASS；
6. stale positive JSON/history => 不可恢复 current authority；
7. recovery 必须是新 generation/current evidence；
8. run 内已有 sticky blocker 后续 positive 不可把同一 run 变 PASS；
9. 任一 blocker/fatal 时 ownerPromptEligible=false；
10. Owner 回答期间 child/regression 变化必须 final re-check 并 fail closed；
11. blocked JSON 仍保留历史正证据和 blocker diagnostics；
12. clean current Fleet + authoritative PYLAUNCH + Recorder + child health + Owner CONFIRMED 才允许 PASS；
13. repository/CI PASS 不能替代 live PASS；
14. safety violation（ramWrites/input/Worker replacement）不可 ready；
15. `longCaptureAutoStarted=false` 始终保持；
16. owner-facing modified path 简体中文正常。

优先新增 adversarial/race-style fixture，而不是只重跑实现线程 21 tests。

## 输出

- `parallel/LIVE_PROOF_BUNDLE_QA_FAILCLOSED/RESULT.md`
- machine-readable QA JSON
- 独立 fixtures/tests

## Stop condition

二选一：

`PASS — UNIFIED WINDOWS LIVE PROOF FAIL-CLOSED INDEPENDENT QA`

或

`BLOCKED — UNIFIED LIVE PROOF FAIL-CLOSED QA — <精确 P0/P1>`

即使 PASS，也不要请求 Owner；由 PM 后续决定 preflight/package/live proof 时机。
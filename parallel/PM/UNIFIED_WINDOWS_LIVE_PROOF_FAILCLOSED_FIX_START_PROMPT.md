# WOF Unified Windows Live Proof Fail-Closed Fix — Fresh Stage

stageId: `UNIFIED_WINDOWS_LIVE_PROOF_FAILCLOSED_FIX_V1`

## 启动去重守卫（必须最先执行）

先读取：
- `parallel/PM/PM_CORE_OPERATING_CHARTER.md`
- `parallel/PM/STAGE_DEDUP_GUARD.md`
- `parallel/PM/OWNER_INTERVENTION_GATE.md`
- GitHub 默认分支最新状态
- `parallel/UNIFIED_WINDOWS_LIVE_PROOF_QA/RESULT.md`

规则：
- 若本 stop condition 已被等价后续结果满足：输出 `ALREADY COMPLETE — SAFE TO CLOSE — 当前线程空闲`，停止。
- 若 `parallel/PM/STAGE_CLAIMS/UNIFIED_WINDOWS_LIVE_PROOF_FAILCLOSED_FIX_V1.json` 已存在：输出 `ALREADY CLAIMED — SAFE TO CLOSE — 当前线程空闲`，停止。
- 否则用 GitHub create-file 原子创建该 claim；创建失败按已认领处理并停止。
- claim 成功后才允许工作；完成更新 COMPLETE；精确 blocker 更新 BLOCKED。
- 不得因任务重复/已完成自行扩 scope。

## 背景

Fresh independent QA 已证明当前 `parallel/LIVE_PROOF_BUNDLE/**` 有 P1：

`BLOCKED — P1 fail-closed aggregation can return PASS with a retained fatal/blocker`

具体风险：
- Recorder 曾 admitted 后再 fatal，旧 `admitted=True` 仍可能参与 PASS；
- `build_status()` 的 PASS 分支优先于 blockers；
- blockers/fatal 已出现后仍可能进入 Owner Y/N playability question；
- PYLAUNCH/Recorder child 在先前 PASS/admit 后异常退出，旧 positive state 仍可能被信任。

这会造成真人 Proof 假 PASS，因此在修复前不得让 Owner 运行。

## 写入范围

只允许：
- `parallel/LIVE_PROOF_BUNDLE/**`

不要修改：
- `parallel/PYLAUNCH/**`
- `parallel/BROWSER_FLEET/**`
- `parallel/WOF052L_RECORDER/**`
- `parallel/PROSPECTIVE_VALIDATOR/**`
- `product/alpha/**`

## 必须完成

1. 最终 PASS predicate 必须显式要求：
   - no blockers；
   - no fatal state；
   - all automatic lanes currently healthy；
   - required child processes still live/valid where applicable；
   - owner playability only after all automatic checks are currently PASS。
2. `RecorderEvidence.fatal == true` 后必须撤销/失效旧 admission authority；不得保留为 ready。
3. PYLAUNCH/Recorder child 如果在此前 PASS/admitted 后异常退出，必须立即 fail closed；旧 positive evidence只可保留为历史证据，不能继续满足 readiness。
4. blockers 一旦存在：
   - `overallResult` 不得 PASS；
   - `tenRoomLongCaptureReady` 必须 false；
   - 不得询问 Owner Y/N；
   - 必须保留 unaffected lane positive evidence + blocker detail。
5. stale/recovered states 必须有明确 generation/current-health 语义，不能因为过去成功就自动恢复权威。
6. long capture 仍绝不自动开始。
7. owner-facing正常路径/错误默认简体中文。
8. readOnly=true / ramWrites=0 / inputInjection=false / no Worker replacement。

## 回归至少覆盖

- fatal-after-admission => BLOCKED；
- blocker + owner Y 模拟 => 仍 BLOCKED；
- PYLAUNCH exit-after-PASS => BLOCKED；
- Recorder exit-after-admission => BLOCKED；
- blocker exists => playability prompt unreachable；
- recovery requires new current positive state；
- unaffected Fleet/PYLAUNCH/Recorder historical positive evidence retained in final JSON；
- full clean current state + owner CONFIRMED => PASS；
- repository/CI PASS never substitutes live PASS；
- no auto long capture；
- safety invariants。

只使用 mock/fixture/offline tests；不要要求 Owner 真人 Browser。

## Stop condition

`UNIFIED WINDOWS LIVE PROOF FAIL-CLOSED FIX READY — READY FOR FRESH INDEPENDENT QA`

结果必须写回新的 fix result/status 文件，列出修改文件、测试数量、PASS 和 fresh QA 应重新验证的精确向量。
# WOF Prospective Validator Discovery V2 Hardening — Fresh Independent QA

stageId: `PROSPECTIVE_VALIDATOR_DISCOVERY_V2_HARDENING_QA_V1`

## 启动去重守卫

先读取：
- `parallel/PM/STAGE_DEDUP_GUARD.md`
- `parallel/PM/OWNER_INTERVENTION_GATE.md`
- `parallel/PROSPECTIVE_VALIDATOR/RESULT.md`
- GitHub 默认分支最新状态

若本 QA stop condition 已有 durable 结果：输出 `ALREADY COMPLETE — SAFE TO CLOSE — 当前线程空闲` 并停止。
若 `parallel/PM/STAGE_CLAIMS/PROSPECTIVE_VALIDATOR_DISCOVERY_V2_HARDENING_QA_V1.json` 已存在：输出 `ALREADY CLAIMED — SAFE TO CLOSE — 当前线程空闲` 并停止。
否则原子 create-file claim，成功后才开始；完成/阻断更新 claim。

## 独立 QA 边界

只允许写：
- `parallel/PROSPECTIVE_VALIDATOR_QA_DISCOVERY_V2_HARDENING/**`
- mandatory PM stage claim

严禁修改：
- `parallel/PROSPECTIVE_VALIDATOR/**`
- Recorder / PYLAUNCH / Fleet / Alpha / LIVE_PROOF_BUNDLE

发现问题只报告，不修复；任何 fix 必须 fresh thread。

## QA 目标

独立验证此前 P0/P1 是否真正关闭，尤其防止“研究证据被错误归属或错误 PASS”。

必须至少覆盖：
1. one page / one exact Worker => 可准入；
2. two pages / two distinct exact Workers => 独立准入；
3. two pages / same shared Worker => 所有相关 evidence fail closed，绝不按扫描顺序归属；
4. misleading openerId 不能成为 parent authority；
5. parentId / 可唯一映射 parentFrameId 行为正确；
6. unique-WOF-page direct fallback 与 multi-page fail closed；
7. remote host / remote websocket / cross-port websocket fail closed；
8. loopback alias 合法；
9. wrong World identity fail closed；
10. blob/data/hashed/no-extension URL 只能作为 diagnostic hint，不能替代 identity；
11. live topology 从唯一关系变歧义时，现有 room 必须先 censor/finalize，不能继续 prospective evidence；
12. discovery-only rows 永远不能满足 prospective gates；
13. candidate freeze/hash mutation rejection 保持；
14. `minProspectiveSignals`、`minProspectiveRooms`、`requireZeroHardMiss`、`minDistinctTargets`、`minObservedTypes`、`requireLifecycleReset` 全部真实执行；
15. unknown conservative gate 必须 fail closed；
16. `PROSPECTIVE_PASS_RESEARCH_ONLY` 不允许 production promotion；
17. readOnly=true / ramWrites=0 / inputInjection=false；
18. no Worker replacement / no URL rewrite / no gameplay input。

优先设计独立 adversarial fixtures，不能只运行实现线程自己的测试然后宣布 PASS。

## 输出

- `parallel/PROSPECTIVE_VALIDATOR_QA_DISCOVERY_V2_HARDENING/RESULT.md`
- machine-readable QA JSON
- 独立 fixtures/tests

## Stop condition

二选一：

`PASS — PROSPECTIVE VALIDATOR DISCOVERY V2 HARDENING INDEPENDENT QA`

或

`BLOCKED — PROSPECTIVE VALIDATOR HARDENING QA — <精确 P0/P1>`

不请求 Owner 真人 Browser。
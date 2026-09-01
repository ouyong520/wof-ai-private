# WOF Regression Orchestrator Discovery V2 Integration Guard — Fresh Stage

stageId: `REGRESSION_ORCH_DISCOVERY_V2_GUARD_V1`

## 启动去重守卫

先读取 `parallel/PM/STAGE_DEDUP_GUARD.md`、`parallel/PM/OWNER_INTERVENTION_GATE.md`、GitHub 最新状态。

- stop condition 已满足：`ALREADY COMPLETE — SAFE TO CLOSE — 当前线程空闲`，停止。
- claim `parallel/PM/STAGE_CLAIMS/REGRESSION_ORCH_DISCOVERY_V2_GUARD_V1.json` 已存在：`ALREADY CLAIMED — SAFE TO CLOSE — 当前线程空闲`，停止。
- 否则原子 create-file claim；成功后才工作；完成/阻断更新 claim。

## 背景

读取：
- `parallel/DISCOVERY_V2_AUDIT/RESULT.md`
- `parallel/REGRESSION_ORCH/**`
- PYLAUNCH / Browser Fleet / Recorder / Prospective Validator 当前 Discovery V2 tests/entrypoints

Cross-component audit 已指出全仓 orchestrator 仍可能漏掉 Prospective `test_discovery_v2.py` 和 Recorder 官方 V2 owner integration surface。

## 写入范围

只允许：
- `parallel/REGRESSION_ORCH/**`

不要修改任何组件核心实现或 Alpha。

## 目标

让全仓 regression 对 Discovery V2 成为真正 safety-critical gate：

1. Prospective Discovery V2 tests 必须是 required suite，不可静默漏跑；
2. Recorder 官方 V2 owner entrypoint/import/install composition 必须纳入 required compile/self-test/integration surface；
3. PYLAUNCH / Fleet / Recorder / Prospective 的 Discovery V2 当前安全测试均纳入明确 allowlist；
4. 若组件在本 stage 执行期间新增 safety-critical discovery tests，runner 在最终 HEAD rescan 时必须能发现并 BLOCKED，而不是静默遗漏；
5. generated dependency dirs 继续排除；
6. 所有 suite 继续真实暴露 FAIL/BLOCKED，不为了 overall green 修改别的 lane；
7. 输出 JSON + 中文摘要，清楚区分 orchestrator contract READY 与 component health；
8. 不运行真人 proof，不要求 Owner。

建议在结束前重新读取最新 HEAD 一次，确保并行 hardening 刚落地的新 test 文件也被发现；如果发现尚未明确 allowlist 的新 safety-critical test，状态应 BLOCKED 并精确列出，而不是自行修改其他组件。

## Stop condition

`REGRESSION ORCHESTRATOR DISCOVERY V2 GUARD READY`

要求 orchestrator 自身 contract tests PASS，并能对当前 HEAD 正确暴露所有 component PASS/FAIL/BLOCKED。
# WOF Repository Regression Orchestrator

状态目标：**REGRESSION ORCHESTRATOR READY**

## Owner 一键入口

Windows 双击：

```text
parallel/REGRESSION_ORCH/RUN_ALL_REGRESSION.cmd
```

也可以从仓库根目录执行：

```text
python parallel/REGRESSION_ORCH/orchestrator.py --repo-root .
```

运行结束固定生成：

- `parallel/REGRESSION_ORCH/REGRESSION_SUMMARY.json`
- `parallel/REGRESSION_ORCH/回归结果.txt`
- `parallel/REGRESSION_ORCH/logs/<run-id>/*.log`

这些运行产物默认不提交 Git。

## 当前固定 allowlist

编排器只运行 `manifest.json` 明确批准的命令，不会使用任意 `parallel/**/tests/test_*.py` 通配执行陌生脚本。

当前覆盖：

- PYLAUNCH discovery / discovery_v2 / fleet registry / proof model tests
- Browser Fleet offline tests
- WOF-052L Recorder owner self-test / Fleet tests
- Prospective Validator tests
- Owner 简体中文 UX compile / CLI smoke tests
- Windows WOF-052L 中文 CMD self-test（仅 Windows）
- Owner One-Click package tests
- Operator Toolkit tests
- Evidence Ingestor tests
- Project Status Scanner tests
- Alpha RC5 `product/alpha/regression.mjs`
- Alpha RC5 independent QA bootstrap harness
- Regression Orchestrator 自检

如果目标 lane 新增测试文件但尚未显式加入 allowlist，`测试 Allowlist 安全门` 会返回 `BLOCKED`，防止漏跑后误报 PASS。

其他 `parallel/**` 中发现的测试候选只会列入结果，不会自动执行。

## 结果语义

每个 suite：

- `PASS`：该离线 suite 完整通过。
- `FAIL`：命令已运行但测试失败/超时。
- `BLOCKED`：缺少明确文件/命令，或 allowlist 发现新的未批准目标-lane 测试。
- `SKIPPED`：当前平台不适用且 manifest 明确允许跳过。
- `NOT_RUN`：真人 proof 按设计不由本编排器自动执行。

`offlineOverall` 是仓库侧自动回归结果。任何离线 suite `FAIL` 都会使其为 `FAIL`；任何必需 suite `BLOCKED` 会使其为 `BLOCKED`。

`overall` 还会计入真人证明状态。因此即使 `offlineOverall=PASS`，只要真人 Browser proof 按设计未运行，`overall` 仍会显示 `BLOCKED`。这不是仓库侧编排器失败，而是为了禁止把未做的真人 proof 伪报为 PASS。

仓库侧 READY 判定：

```text
offlineOverall == PASS
and 测试 Allowlist 安全门 == PASS
```

## 安全边界

本编排器：

- read-only 游戏访问边界；
- `ramWrites=0`；
- no gameplay input injection；
- no `window.Worker` replacement；
- 不自动启动/进入游戏；
- 不执行真人 Browser proof；
- 不修改 `product/alpha/**`；
- 不修改各 lane 核心实现。

本目录唯一运行时写入是本编排器自己的 summary / 中文结果 / logs。

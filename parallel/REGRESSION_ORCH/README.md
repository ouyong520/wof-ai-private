# WOF Repository Regression Orchestrator

状态：**REGRESSION ORCHESTRATOR READY**

## Owner 一键入口

Windows 双击：

```text
parallel/REGRESSION_ORCH/RUN_ALL_REGRESSION.cmd
```

或从仓库根目录执行：

```text
python parallel/REGRESSION_ORCH/runner.py --repo-root .
```

`runner.py` 是正式入口。它在核心编排器前增加安全 discovery 过滤，明确排除 `.venv`、`venv`、`site-packages`、`node_modules`、`__pycache__`、`.git` 等生成/依赖目录，避免第三方测试被误当成 WOF 仓库测试。

运行结束固定生成：

- `parallel/REGRESSION_ORCH/REGRESSION_SUMMARY.json`
- `parallel/REGRESSION_ORCH/回归结果.txt`
- `parallel/REGRESSION_ORCH/logs/<run-id>/*.log`

这些运行产物默认不提交 Git。

## 固定 allowlist

编排器只运行 `manifest.json` 明确批准的命令，不会用任意通配规则自动执行未来陌生脚本。

当前覆盖：

- Regression Orchestrator 自检
- PYLAUNCH discovery / discovery_v2 / fleet registry / Windows proof model tests
- Browser Fleet manager / discovery v2 tests
- WOF-052L Recorder owner self-test / Fleet / discovery v2 sync tests
- Prospective Validator tests
- Owner 简体中文 UX compile / smoke tests
- Windows WOF-052L 中文 CMD self-test
- Owner One-Click package tests
- Operator Toolkit tests
- Evidence Ingestor tests
- Project Status Scanner tests
- Alpha RC5 `product/alpha/regression.mjs`
- Alpha RC5 independent QA bootstrap harness

如果目标 lane 新增测试文件但尚未显式加入 allowlist，`测试 Allowlist 安全门` 返回 `BLOCKED`，防止漏跑后误报 PASS。其他非目标 `parallel/**` 测试候选只列入结果，不自动执行。

## 结果语义

每个 suite：

- `PASS`：该 suite 完整通过。
- `FAIL`：命令已运行，但测试失败或超时。
- `BLOCKED`：缺文件/命令，或目标 lane 出现尚未批准的新测试。
- `SKIPPED`：当前平台不适用，且 manifest 明确允许跳过。
- `NOT_RUN`：真人 proof 按设计不由本编排器自动执行。

`offlineOverall` 表示**当前仓库离线回归健康度**，不是编排器自身是否 READY。真实组件测试失败时必须保持 `FAIL`，编排器不会为了绿色结果隐藏失败。

`overall` 还会计入真人证明状态。PYLAUNCH 真人 Windows/Browser proof 与 Alpha 真人 Browser acceptance 不会自动执行，因此必须保留为 `NOT_RUN/BLOCKED`，绝不伪造 PASS。

**REGRESSION ORCHESTRATOR READY** 的判定是：

1. Owner 有一个双击/单命令入口；
2. Windows contract CI 能编译并通过编排器自身测试；
3. 完整 runner 能继续执行全部 allowlisted suite，即使中途有组件 FAIL；
4. 能稳定生成 JSON、中文摘要和逐 suite 日志；
5. allowlist 安全门能阻止陌生目标测试被静默漏跑，也不会把生成依赖目录当仓库测试；
6. 当前组件真实 FAIL 会被准确暴露，而不是修改外部 lane 或伪报 PASS。

因此，编排器可以处于 READY，同时某个具体仓库快照的 `offlineOverall` 仍为 `FAIL`。

## GitHub Actions

独立 workflow：`.github/workflows/regression-orchestrator.yml`。

它分成两层：

- `orchestrator-contract`：验证编排器自身、safe runner 与 allowlist/discovery contract；
- `windows-offline-regression`：在真实 Windows runner 上执行当前完整离线回归并上传 summary/logs。

这样可以区分“编排器坏了”和“编排器正确发现了某个组件回归失败”。

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

本目录运行时只写本编排器自己的 summary / 中文结果 / logs。

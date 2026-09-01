# WOF Discovery V2 Cross-Component Audit — Fresh Start Prompt

你负责一个独立的跨组件 Discovery V2 一致性审计线。

仓库：`ouyong520/wof-ai-private`

## 目的

当前 PYLAUNCH、Browser Fleet、WOF-052L Recorder、Prospective Validator 都需要发现真实 WOF Browser page / Worker topology。

这些组件职责不同：
- PYLAUNCH：权威 Worker/WASM/World 921031 proof；
- Browser Fleet：cheap indicator only；
- Recorder：采集 admission authority；
- Prospective Validator：prospective session admission authority。

本线不重写实现，而是防止四套 Discovery V2 在快速并行开发中出现语义漂移，导致“各自测试 PASS、拼起来不一致”。

## 读取

只读检查最新：
- `parallel/WORKER_SURFACE/**`
- `parallel/PYLAUNCH/**`
- `parallel/BROWSER_FLEET/**`
- `parallel/WOF052L_RECORDER/**`
- `parallel/PROSPECTIVE_VALIDATOR/**`
- `parallel/REGRESSION_ORCH/**`
- `parallel/PM/CHINESE_UI_UX_REQUIREMENT.md`

## 写入范围

仅：`parallel/DISCOVERY_V2_AUDIT/**`

禁止修改任何上述组件实现。

## 必查项目

建立一份明确 matrix，逐组件核对：

1. localhost endpoint 限制；
2. page 识别与多 page ambiguity；
3. direct Worker fallback；
4. Target.setAutoAttach / related target；
5. iframe -> Worker；
6. target lifecycle / recreated Worker；
7. URL mismatch tolerance；
8. Worker -> page / endpoint association；
9. 多房/多 tab/多 port 严格隔离；
10. stale/reload/disconnect 清理；
11. WASM/heap readiness；
12. exact World 921031 SHA-256 authority差异；
13. wrong identity fail-closed；
14. ambiguous Workers fail-closed；
15. read-only CDP allowlist；
16. `Input.*` / gameplay injection 禁止；
17. `ramWrites=0`；
18. no Worker replacement / Blob rewrite；
19. owner-facing Chinese status；
20. evidence authority：cheap indicator / capture / prospective / authoritative proof 不得混淆。

## 输出

至少：
- `parallel/DISCOVERY_V2_AUDIT/MATRIX.md`
- `parallel/DISCOVERY_V2_AUDIT/RESULT.md`
- machine-readable `result.json`

每个差异必须分类：
- EXPECTED_ROLE_DIFFERENCE
- SAFE_COMPATIBILITY_DIFFERENCE
- P1_DRIFT_RISK
- P0_INTEGRATION_BLOCKER

如果发现 P0/P1：
- 不在本线修代码；
- 精确指出哪个 fresh fix lane 应拥有哪个目录；
- 给 PM 一个最小修复任务定义。

## Stop condition

直到：

**DISCOVERY V2 CROSS-COMPONENT AUDIT COMPLETE**

并明确：
- 无阻塞 drift；或
- 一个/多个精确 P0/P1 blocker + 对应 fresh fix ownership。

不要要求 owner 做真人 Browser 操作；真实 Windows 行为统一留给 Unified Windows Live Proof Bundle。
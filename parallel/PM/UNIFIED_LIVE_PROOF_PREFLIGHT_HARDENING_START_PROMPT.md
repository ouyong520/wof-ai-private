# WOF Unified Live Proof Preflight Hardening — Fresh Stage

stageId: `UNIFIED_LIVE_PROOF_PREFLIGHT_HARDENING_V1`

## 启动去重守卫

先读取：
- `parallel/PM/STAGE_DEDUP_GUARD.md`
- `parallel/PM/OWNER_INTERVENTION_GATE.md`
- GitHub 默认分支最新状态

若 stop condition 已满足：`ALREADY COMPLETE — SAFE TO CLOSE — 当前线程空闲`。
若 claim `parallel/PM/STAGE_CLAIMS/UNIFIED_LIVE_PROOF_PREFLIGHT_HARDENING_V1.json` 已存在：`ALREADY CLAIMED — SAFE TO CLOSE — 当前线程空闲`。
否则原子 create-file claim，成功后才工作；完成/阻断更新 claim。不得重复扩 scope。

## 目标

只修改：
- `parallel/LIVE_PROOF_BUNDLE/**`

不要修改 PYLAUNCH / Fleet / Recorder / Prospective / Alpha / Owner OneClick。

把 Unified Live Proof 变成“**真人运行前自我证明尽可能完整**”的入口。Owner 不应该成为 preflight。

## 必须实现

在启动真实 Browser/WOF 之前先运行 repository-side preflight：

1. 检查所需组件文件/入口存在且来自同一最新 snapshot；
2. 检查已知 required RESULT/status 不是 BLOCKED/SUPERSEDED；
3. 检查 current component test entrypoints 可运行；
4. 运行/调用安全的相关离线 regression（或读取可信 fresh regression artifact 后验证 commit 对齐）；
5. 检查 Discovery V2 contract version/required capability 标志，不能把旧 direct-gstyphoon implementation 当新版本；
6. 检查 owner-facing Chinese entrypoints；
7. 检查 readOnly / ramWrites=0 / inputInjection=false / no Worker replacement declarations；
8. 检查 package/snapshot 不 stale，所有子组件来自同一 commit 或明确兼容的 pinned manifest；
9. 任一 repository-side P0/P1 blocker 存在时，**不得启动 Browser，也不得要求 Owner 进入 WOF**；输出中文 blocker JSON，然后退出；
10. preflight 全 PASS 后才允许进入真正 live proof 阶段；即使如此也不自动开始 10-room long capture。

## 失败路径

必须保证：
- preflight failure 不启动 Browser；
- 不要求 Owner 点击/确认；
- 输出一个中文摘要 + `UNIFIED_PREFLIGHT_STATUS.json`；
- 精确指出 component / test / commit / blocker；
- stale cache / mixed snapshot / missing file / wrong entrypoint / BLOCKED result 都能 fail closed。

## Mock/fixture 回归

至少模拟：
- 全部 repository checks PASS；
- 一个组件 BLOCKED；
- stale snapshot；
- mixed component commits；
- missing required test；
- old Discovery implementation；
- English-only owner entry regression；
- safety declaration mismatch；
- malformed result JSON；
- regression command failure；
- preflight PASS 后 live stage才可启动；
- preflight FAIL 时 live stage绝不启动。

不需要 Owner 真人 Browser。

## Stop condition

`UNIFIED LIVE PROOF PREFLIGHT HARDENING READY — OWNER NOT NEEDED FOR REPOSITORY CHECKS`

结果写回 `parallel/LIVE_PROOF_BUNDLE/**`，明确测试数量和仍然只能由真实 Windows/WOF 证明的事实。
# Discovery V2 Current-HEAD Long Soak Audit — Fresh Stage

stageId: `DISCOVERY_V2_CURRENT_HEAD_LONG_SOAK_AUDIT_V1`
priority: `P1 MAINLINE LONG-RUN`

## 启动守卫

先读取：
- `parallel/PM/STAGE_DEDUP_GUARD.md`
- `parallel/PM/PM_DELIVERY_REASSESSMENT_GATE.md`
- 最新默认分支与 `parallel/PM/STAGE_CLAIMS/**`

若 stop condition 已满足，返回：
`ALREADY COMPLETE — SAFE TO CLOSE — 当前线程空闲`

若 claim 已存在且 ACTIVE，返回：
`ALREADY CLAIMED — SAFE TO CLOSE — 当前线程空闲`

否则原子创建：
`parallel/PM/STAGE_CLAIMS/DISCOVERY_V2_CURRENT_HEAD_LONG_SOAK_AUDIT_V1.json`

## 为什么现在做

当前 PYLAUNCH / Recorder 等实现仍在收尾，但 Discovery V2 已有 conformance harness。需要一条只读长审计线持续跟随 current HEAD，及时发现跨组件接口漂移，避免等所有修复完成后才一次性发现新的组合问题。

## 写入范围

只允许写：
- `parallel/DISCOVERY_V2_CURRENT_HEAD_LONG_SOAK_AUDIT/**`
- 对应 stage claim

不得修改：
- `parallel/PYLAUNCH/**`
- `parallel/WOF052L_RECORDER/**`
- `parallel/PROSPECTIVE_VALIDATOR/**`
- `parallel/LIVE_PROOF_BUNDLE/**`
- `parallel/ALPHA_TRANSPORT_IMPL/**`
- Owner package / HUDANCHOR 实现

## 长任务目标

构建并持续执行 current-head 跨组件审计，至少覆盖：

1. Browser Fleet Discovery V2；
2. PYLAUNCH discovery / parentId / parentFrameId / generation identity；
3. WOF052L Recorder endpoint / topology / identity lifecycle；
4. Prospective Validator exact-pair / ambiguity / fail-closed；
5. Regression Orchestrator Discovery V2 guard；
6. Unified Live Proof 对 Discovery/Recorder/PYLAUNCH authority 的消费边界；
7. exact World 921031 identity；
8. loopback exact-port confinement；
9. shared Worker / cross-page ambiguity；
10. reconnect / reload / target-id reuse / generation transitions；
11. readOnly=true / ramWrites=0 / inputInjection=false / no Worker replacement；
12. owner-facing Chinese path 不退化。

## Current-HEAD 规则

- 记录每轮起始 HEAD。
- 若执行期间上游实现 HEAD 发生变化，不把旧结果当最终结论；重新读取受影响组件并重跑相应矩阵。
- 必须记录 `testedHead`、组件 blob SHA、发现的 drift。
- 允许已有实现线程继续提交；本 lane 只读跟随，不抢 ownership。
- 若发现 P0/P1，立即写精确 blocker 和最小复现，但不要修改实现。

## 长跑工作量

目标是多小时级工作量，不允许靠 sleep/空等凑时长。通过以下方式形成真实 workload：
- current-head 重复矩阵；
- adversarial topology/generation permutations；
- deterministic replay；
- cross-component contract diff；
- failure-injection；
- 当前 HEAD 漂移后的 selective rerun；
- 至少一次完整全矩阵重跑。

## 第一 downstream consumer

- Alpha Safe Transport formal integration
- Unified Live Proof release preflight
- WOF052L long-capture QA

## 停止条件

以下任一成立即可停止：

A. 发现一个精确 P0/P1 跨组件 blocker：
`BLOCKED — DISCOVERY V2 CURRENT-HEAD LONG SOAK — <precise blocker>`

B. 当前 HEAD 在最终完整矩阵中无 P0/P1 drift，并输出 machine-readable matrix + Chinese summary：
`PASS — DISCOVERY V2 CURRENT-HEAD LONG SOAK — READY FOR FORMAL INTEGRATION GATE`

不得因“跑够时间”单独 PASS。

## Kill / park

如果唯一剩余问题只能由真实 Owner Browser/WOF 证明，停止并报告，不要求 Owner 现在介入。

## 最大 breadth

只审 Discovery V2 / authority / generation / safety / consumer contract。不得扩成游戏逻辑逆向或无关性能研究。

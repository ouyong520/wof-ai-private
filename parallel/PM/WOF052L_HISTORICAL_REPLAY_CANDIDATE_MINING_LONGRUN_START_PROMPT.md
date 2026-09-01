# WOF052L Historical Replay + Candidate Mining Longrun — Fresh Stage

stageId: `WOF052L_HISTORICAL_REPLAY_CANDIDATE_MINING_LONGRUN_V1`
priority: `P2 STRATEGIC ACCELERATOR LONG-RUN`

## 启动守卫

先读取：
- `parallel/PM/STAGE_DEDUP_GUARD.md`
- `parallel/PM/PM_DELIVERY_REASSESSMENT_GATE.md`
- `parallel/PM/PRIORITY_POLICY.md`
- Prospective Validator fresh QA PASS 结果
- 现有 WOF-047 / WOF-051 / WOF-052 / WOF-052L 可用历史证据与 manifest

若 stop condition 已满足：
`ALREADY COMPLETE — SAFE TO CLOSE — 当前线程空闲`

若 claim ACTIVE：
`ALREADY CLAIMED — SAFE TO CLOSE — 当前线程空闲`

否则原子创建：
`parallel/PM/STAGE_CLAIMS/WOF052L_HISTORICAL_REPLAY_CANDIDATE_MINING_LONGRUN_V1.json`

## 为什么现在做

Prospective Validator 的 live ambiguity P0 fresh QA 已 PASS。当前 Recorder 仍在修复，不适合马上要求 Owner 长采集，因此利用已有历史 corpus 做高强度 replay / ordered-sequence mining，可以提前筛掉弱候选、发现需要补采的最小证据缺口，减少未来真人 1h/2h capture 的浪费。

## 写入范围

只允许写：
- `parallel/WOF052L_HISTORICAL_REPLAY_LONGRUN/**`
- 对应 stage claim

不得修改：
- `parallel/WOF052L_RECORDER/**`
- `parallel/PROSPECTIVE_VALIDATOR/**`
- Alpha / PYLAUNCH / Browser Fleet / Live Proof / HUD

## 核心规则

- Browser type notation 必须统一为 `T<decimal> (0xHH)`；不得把旧本地 T12/T17 与 Browser T12/T17 混用。
- 单状态歧义不能被包装成确定 predictor；优先 ordered context / lifecycle / target / side / timing。
- retrospective 不能冒充 prospective。
- 0 coverage 不能当 predictor failure。
- research-only 结果不得 promotion to production。
- 不扩大到无关游戏内部机制逆向。

## 长任务目标

对已有 corpus 做多小时级、可重复的离线工作量：

1. 统一字段/类型/时间轴规范；
2. 重放 WOF-047/051/052/已有 052L artifact；
3. 对已成熟规则做 replay sanity：T16、T20、D867BA、D8811E、T18 BODY7512/7520；
4. 对 T18 BODY4728 歧义做 ordered-sequence / previous-state / next-state / target / side / timing discriminator mining；
5. 对 T23 历史 8 个 positive cycles 做 ordered-tail / branch-pattern mining；
6. candidate dedup / support count / room count / target count / hard-miss estimate；
7. leave-one-room-out / leave-one-cycle-out robustness；
8. synthetic perturbation：timing jitter、missing sample、duplicate sample、room reorder；
9. 生成 prospective-validator 可消费的 research-only candidate manifests 或明确 NOT_READY reason；
10. 输出“下一次真实采集最值得补什么”的最小 coverage plan，而不是泛泛要求更多数据。

## 长跑工作量

禁止 sleep/空等凑时长。通过：
- 大量 deterministic replay permutations；
- sequence-window sweep；
- support/precision/ambiguity matrix；
- leave-one-out；
- perturbation；
- candidate cross-check；
形成真实多小时工作量。

## 第一 downstream consumer

- 下一轮 WOF052L long capture plan
- Prospective Validator candidate queue
- Beta common-danger coverage planning

## Stop condition

A. 找到一个或多个 durable research candidate，且明确证据层级/支持度/仍缺 prospective proof：
`WOF052L HISTORICAL REPLAY LONGRUN READY — CANDIDATE QUEUE UPDATED`

B. 证明现有 corpus 对关键歧义不足，且已经把下一次采集需求压缩成最小、可操作 coverage target：
`WOF052L HISTORICAL REPLAY LONGRUN READY — MINIMAL NEXT CAPTURE PLAN`

C. 若工作开始重复描述、不再改变决策，立即 PARK，不得为了时长继续扩 scope。

## Kill / park

若唯一能推进的问题已经变成“必须获得新的真实 WOF 样本”，停止并报告缺口；不要要求 Owner 现在采集，等待主线 live-proof / Recorder gate 允许后再统一安排。

## 最大 breadth

只做现有证据 replay、candidate mining、ordered discriminator、下一次采集最小化。不得扩成全游戏 attack atlas。

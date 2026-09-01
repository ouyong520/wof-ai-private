# WOF Alpha Safe Transport Reference Implementation — Fresh Stage

stageId: `ALPHA_TRANSPORT_REFERENCE_IMPL_V1`
priority: `P1`

## 启动去重守卫
先读取：
- `parallel/PM/STAGE_DEDUP_GUARD.md`
- `parallel/PM/OWNER_INTERVENTION_GATE.md`
- `parallel/PM/PM_CORE_OPERATING_CHARTER.md`
- GitHub 最新状态

若 stop condition 已满足：输出 `ALREADY COMPLETE — SAFE TO CLOSE — 当前线程空闲` 并停止。
若 `parallel/PM/STAGE_CLAIMS/ALPHA_TRANSPORT_REFERENCE_IMPL_V1.json` 已存在：输出 `ALREADY CLAIMED — SAFE TO CLOSE — 当前线程空闲` 并停止。
否则原子 create-file claim；成功后才工作；完成/阻断更新 claim。

## 为什么现在可以并行
当前 PYLAUNCH / Recorder / Prospective / Unified Proof 正在各自 hardening。本 stage 不修改这些目录，也不修改 `product/alpha/**`，只把已经冻结的 Safe Transport Contract + 67-vector mock harness 变成可执行的独立 reference implementation，减少未来正式 Integration 的代码量和试错。

## 只允许写入
- `parallel/ALPHA_TRANSPORT_IMPL/**`

禁止修改：
- `parallel/PYLAUNCH/**`
- `parallel/WOF052L_RECORDER/**`
- `parallel/PROSPECTIVE_VALIDATOR/**`
- `parallel/LIVE_PROOF_BUNDLE/**`
- `product/alpha/**`

## 必须读取
- `parallel/PM/ALPHA_SAFE_TRANSPORT_INTEGRATION_CONTRACT.md`
- `parallel/ALPHA_TRANSPORT_MOCK/**`
- 当前 RC5 Alpha transport-facing contract / message schema（只读）

## 目标
实现一个与真实浏览器解耦的 reference transport runtime，至少包括：
- session / pairGeneration / pairNonce / seq envelope；
- exact identity handshake 输入接口；
- runtime epoch / Worker replacement reset；
- state / diag authority；
- stale / disconnect / reconnect；
- backpressure / in-flight suppression；
- bounded heartbeat；
- warning authority fail-closed；
- target/session/tab isolation；
- fixed-HUD transport output contract；
- readOnly=true / ramWrites=0 / inputInjection=false 强制安全字段；
- no Worker replacement / no gameplay input / no RAM write。

必须直接运行现有 `parallel/ALPHA_TRANSPORT_MOCK/**` 67-vector acceptance，或提供兼容 adapter 让同一向量验证 reference implementation，不允许重新发明更宽松的测试标准。

为未来正式 integration 留清晰 adapter 接口：
- Discovery adapter（未来接 PYLAUNCH hardening 后结果）
- Native Worker runtime adapter
- Alpha detector adapter
- Page/HUD transport adapter

不得假设真实 Chrome topology 已经最终证明；所有真实运行依赖必须通过 adapter 注入。

## Stop condition
`ALPHA TRANSPORT REFERENCE IMPLEMENTATION READY FOR INTEGRATION`

要求：
- reference implementation 自测 PASS；
- 67-vector contract 不回退；
- machine-readable result + 中文摘要；
- 明确列出正式 Integration 还需从 hardening 后组件接入的最小接口；
- 不要求 Owner 真人测试。
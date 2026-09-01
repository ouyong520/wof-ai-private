# WOF-052L Recorder Discovery V2 Hardening — Fresh Stage

stageId: `WOF052L_RECORDER_DISCOVERY_V2_HARDENING_V1`

## 启动去重守卫（必须最先执行）

先读取：
- `parallel/PM/STAGE_DEDUP_GUARD.md`
- `parallel/PM/OWNER_INTERVENTION_GATE.md`
- GitHub 默认分支最新状态
- 本 stage 等价 result/commit

规则：
- stop condition 已满足：输出 `ALREADY COMPLETE — SAFE TO CLOSE — 当前线程空闲`，停止。
- `parallel/PM/STAGE_CLAIMS/WOF052L_RECORDER_DISCOVERY_V2_HARDENING_V1.json` 已存在：输出 `ALREADY CLAIMED — SAFE TO CLOSE — 当前线程空闲`，停止。
- 否则用 GitHub create-file 原子创建 claim；创建失败按已认领处理，重新读取后停止。
- claim 成功后才允许修改实现；完成更新 COMPLETE；精确 blocker 更新 BLOCKED。
- 不得因重复/已完成自行扩 scope。

## 背景

必须读取最新：
- `parallel/DISCOVERY_V2_AUDIT/RESULT.md`
- `parallel/WOF052L_LIVE_CAPTURE_QA/RESULT.md`
- `parallel/WOF052L_RECORDER/**`
- `parallel/WOF052L_LIVE_CAPTURE/**`
- `parallel/WORKER_SURFACE/**`
- `parallel/BROWSER_FLEET/**` 仅作为 endpoint-isolation 参考

当前 Recorder 同一写入域中有一组应该一次关闭的问题，不要拆成多轮 Owner 测试：

### P0
Cross-page shared Worker ambiguity：两个 page 关联同一个 exact supported Worker 时，不能按 scan order 选一个 page 归属证据。

### P1 Discovery V2 drift
- endpoint confinement / returned browser websocket 未严格同 endpoint host/port pin；
- existing blob/data Worker 在 runtime/exact identity 前被 URL scheme 硬拒绝；
- direct fallback 不应把 Worker openerId 当 parent authority。

### P1 Owner UX
10-room normal path 的 Fleet Recorder runtime status/error 仍有 English-only owner-visible 文本。

## 写入范围

只允许核心修改：
- `parallel/WOF052L_RECORDER/**`

仅当 live-capture wrapper 必须做极小适配时才允许：
- `parallel/WOF052L_LIVE_CAPTURE/**`

不要修改：
- PYLAUNCH
- Browser Fleet
- Prospective Validator
- WOF052L Analysis
- Alpha

## 必须完成

1. Endpoint-level Worker<->page relation graph：同一 Worker targetId 关联 >1 page 时，全部 fail closed，明确中文/diagnostic reason，例如 `cross-page-worker-association-ambiguous`。
2. 已开始的 live capture 若后续重新审计进入该 ambiguity，先 finalize/censor 受影响 room，再拒绝后续 evidence；其他 room 不受影响。
3. Generic/owner path 只允许 loopback CDP；`/json/version` 返回 websocket 必须归属请求 endpoint，同 host/port；cross-port fail closed；规范化 loopback alias 可接受。
4. 对**已经存在、可 attach**的 Worker，URL scheme 只作为 hint/diagnostic；blob/data/hashed/no-extension URL 必须让 runtime readiness + exact World 921031 identity 决定 admission。绝不创建/替换/rewrite Blob Worker/ObjectURL。
5. Direct fallback 不得使用 Worker `openerId` 作为 parent authority；优先 page-rooted auto-attach / actual parentId / parentFrameId；否则只有唯一 WOF page 才可兼容 direct Worker，否则 fail closed。
6. World 921031 + golden SHA gate 保持权威；WASM/heap readiness 保持。
7. 所有 normal 1/5/10-room owner runtime status/error 默认简体中文；错误先中文解释，再技术详情；endpoint/CDP/WOF-052L 等技术名可保留。
8. Windows UTF-8 / 中文路径 / spaces / retry / disconnect / finalize 不乱码、不破坏现有 schema。
9. room/session/endpoint isolation、readOnly=true、ramWrites=0、inputInjection=false、no Worker replacement。
10. 不要求 Owner 真人 WOF；用 synthetic CDP topology、mock runtime、fixtures、offline regression 关闭所有 repository-side uncertainty。

## 回归至少覆盖

- one page / one exact Worker => admit；
- two pages / two distinct exact Workers => independent admit；
- two pages / same shared exact Worker => admit none；
- ambiguity appears mid-capture => finalize affected only；
- remote host reject；
- returned websocket cross-port reject；
- loopback alias accept；
- existing blob/data exact supported Worker accept；
- wrong identity blob/data reject；
- misleading openerId no misassociation；
- unique-page direct fallback；
- multi-page direct fallback fail closed；
- endpoint waiting / CDP failure / Browser connected / child startup / disconnect / retry / finalize 全中文；
- simulated 10-room one-room failure isolation；
- existing discovery v2 / SHA / cadence / checkpoint / merged JSON regressions；
- safety invariants。

## Stop condition

`WOF052L RECORDER DISCOVERY V2 HARDENING READY — P0/P1 + CHINESE UX CLOSED IN REPOSITORY`

结果必须列出完整测试数量、PASS、剩余只能由真实 Windows/WOF 证明的最小事实。不得要求 Owner 立即运行。
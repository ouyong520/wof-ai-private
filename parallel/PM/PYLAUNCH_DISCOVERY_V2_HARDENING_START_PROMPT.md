# WOF PYLAUNCH Discovery V2 Hardening — Fresh Stage

stageId: `PYLAUNCH_DISCOVERY_V2_HARDENING_V1`

## 启动去重守卫（必须最先执行）

先读取 `parallel/PM/STAGE_DEDUP_GUARD.md`、GitHub 默认分支最新状态和本 stage 等价结果。

- 已满足本 stop condition：输出 `ALREADY COMPLETE — SAFE TO CLOSE — 当前线程空闲`，停止。
- `parallel/PM/STAGE_CLAIMS/PYLAUNCH_DISCOVERY_V2_HARDENING_V1.json` 已存在：输出 `ALREADY CLAIMED — SAFE TO CLOSE — 当前线程空闲`，停止。
- 否则用 GitHub create-file 原子创建该 claim。创建失败按已认领处理并停止。
- claim 成功后输出 `CLAIM ACQUIRED — WORK STARTED` 再工作。
- 完成后更新 claim 为 COMPLETE；精确 blocker 更新为 BLOCKED。
- 不得因重复/已完成而自行扩 scope。

## 背景

读取最新：
- `parallel/DISCOVERY_V2_AUDIT/RESULT.md`
- `parallel/PYLAUNCH/**`
- `parallel/WORKER_SURFACE/**`
- `parallel/BROWSER_FLEET/**` 仅作 endpoint isolation 参考

Cross-component audit 已确认 PYLAUNCH 的 Discovery V2 仍有 P1 drift：
1. endpoint confinement：generic host / returned browser websocket 未严格同 host/port pin；
2. URL scheme gate：对已经存在、可 attach 的 blob/data Worker 在 runtime/exact identity 前硬拒绝；
3. direct fallback association：不应把 Worker `openerId` 当 parent authority。

PYLAUNCH 对 cross-page exact supported pair 的全局唯一性目前比 Recorder/Prospective 更严格，必须保留，不要放宽。

## 写入范围

只允许：
- `parallel/PYLAUNCH/**`

不要修改 Browser Fleet、Recorder、Prospective Validator、Alpha。

## 目标

在不改变 read-only 安全边界的前提下关闭上述 PYLAUNCH P1 drift：

- 默认/owner proof 只允许 loopback CDP；
- `/json/version` 返回的 websocket 必须归属请求 endpoint，同 host/port；cross-port fail closed；
- 允许规范化 loopback alias；
- 对**已经存在**的 attachable Worker，URL scheme 只能作为 hint/diagnostic；blob/data/hashed/no-extension URL 不能在 runtime readiness + exact World identity 前被一刀切；
- 这绝不授权创建 Blob Worker/ObjectURL、替换 Worker、rewrite URL；
- direct fallback 不得用 Worker `openerId` 作为 parent authority；优先 page-rooted auto-attach / parentId / parentFrameId；否则必须只有一个唯一 WOF page 才能兼容 direct Worker，否则 fail closed；
- 保留全局 exact supported page/Worker pair 唯一性；多 pair 必须 fail closed；
- reload/Worker replacement 后 stale state 清除；
- exact World 921031 SHA 保持权威；
- readOnly=true / ramWrites=0 / inputInjection=false / no Worker replacement。

## 回归

至少覆盖：
- remote host reject；
- cross-port websocket reject；
- loopback alias accept；
- blob/data existing Worker + exact supported runtime accept；
- wrong identity blob/data reject；
- openerId misleading case 不误关联；
- unique WOF page direct fallback；
- two WOF pages direct fallback fail closed；
- cross-page exact pair ambiguity仍 fail closed；
- reload/recreated Worker；
- no write/no input/no replacement invariants。

不要要求 owner 真人 Browser。

## Stop condition

`PYLAUNCH DISCOVERY V2 HARDENING READY — REPOSITORY REGRESSION PASS`

把结果写回 `parallel/PYLAUNCH/**` 新的 result/status 文件，列出回归数量和仍需真人证明的最小项。
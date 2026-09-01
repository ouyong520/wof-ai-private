# WOF-052L Recorder Discovery V2 Hardening — Fresh Independent QA

stageId: `WOF052L_RECORDER_HARDENING_QA_V1`
priority: `P1`

## 启动去重守卫
先读取 `parallel/PM/STAGE_DEDUP_GUARD.md`、`parallel/PM/OWNER_INTERVENTION_GATE.md`、`parallel/WOF052L_RECORDER/DISCOVERY_V2_HARDENING_RESULT.md` 与最新 GitHub。

若等价 QA 已完成：`ALREADY COMPLETE — SAFE TO CLOSE — 当前线程空闲`，停止。
若 claim `parallel/PM/STAGE_CLAIMS/WOF052L_RECORDER_HARDENING_QA_V1.json` 已存在：`ALREADY CLAIMED — SAFE TO CLOSE — 当前线程空闲`，停止。
否则原子 claim 后工作。

## QA 边界
只允许新增/修改：
- `parallel/WOF052L_RECORDER_QA_HARDENING/**`
- mandatory stage claim

绝不修改 Recorder 实现；发现问题只记录 blocker，交 fresh fix。

## 必须独立验证
1. cross-page shared Worker ambiguity：新 admission 与 mid-capture transition 都必须在 evidence polling 前 fail closed/finalize。
2. two pages / two distinct Workers 独立。
3. endpoint loopback + exact port confinement，remote/cross-port fail closed。
4. blob/data/hashed/no-extension existing Worker URL 只作 hint，wrong identity 仍 reject。
5. openerId 非 parent authority；parentId / parentFrameId / unique-page fallback 的真实 reachability。
6. explicit `--cdp-port` 不 fallover。
7. reload/recreated Worker 不继承 stale authority。
8. 10 endpoint 单点失败隔离。
9. Chinese owner UX、UTF-8、中文路径与 merged JSON。
10. exact World 921031 SHA、readOnly=true、ramWrites=0、inputInjection=false、no Worker replacement。
11. cadence/checkpoint/finalize/merged schema 不回归。
12. 不能因为 CI 绿色就跳过 adversarial fixture；必须自己构造至少一个 shared-worker transition 和一个 endpoint drift fixture。

## Owner
不要求真人 Browser/Windows。

## Stop condition
- PASS：`PASS — WOF052L RECORDER HARDENING QA — READY FOR LONG-CAPTURE QA RETEST`
- 或精确 `BLOCKED — ... P0/P1 ...`

交卷不等于最终通过，PM 仍会二次审核。
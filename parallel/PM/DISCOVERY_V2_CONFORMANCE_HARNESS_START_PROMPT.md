# WOF Discovery V2 Cross-Component Conformance Harness — Fresh Stage

stageId: `DISCOVERY_V2_CONFORMANCE_HARNESS_V1`

## 启动去重守卫

先读取 `parallel/PM/STAGE_DEDUP_GUARD.md`、`parallel/PM/OWNER_INTERVENTION_GATE.md` 和 GitHub 最新状态。

若 stop condition 已满足：输出 `ALREADY COMPLETE — SAFE TO CLOSE — 当前线程空闲` 并停止。
若 `parallel/PM/STAGE_CLAIMS/DISCOVERY_V2_CONFORMANCE_HARNESS_V1.json` 已存在：输出 `ALREADY CLAIMED — SAFE TO CLOSE — 当前线程空闲` 并停止。
否则原子 create-file claim；成功后才工作。完成/阻断更新 claim。

## 写入范围

只允许新增/修改：
- `parallel/DISCOVERY_V2_CONFORMANCE/**`

不要修改 PYLAUNCH / Browser Fleet / Recorder / Prospective Validator / Alpha。

## 目标

把当前 `parallel/DISCOVERY_V2_AUDIT/RESULT.md` 的人工交叉审计结论变成可重复运行的 synthetic topology conformance harness。

Harness 要能对当前组件 adapter/公开 discovery entry 进行只读/fixture 驱动验证，至少覆盖：

- one page / one worker；
- two pages / two workers；
- two pages / same shared worker；
- iframe -> worker；
- direct worker fallback；
- misleading openerId；
- Worker URL = gstyphoon / hashed / blob / data / no extension；
- remote host；
- cross-port websocket；
- loopback alias；
- reload/recreated worker；
- stale target/session；
- exact supported identity / wrong identity；
- one room failure isolation；
- advisory Fleet vs authoritative PYLAUNCH/Recorder/Prospective role difference。

输出每组件的 matrix：PASS / FAIL / EXPECTED_ROLE_DIFFERENCE，不把 Fleet 的 cheap indicator 误判成 exact identity authority。

必须把这些安全不变量统一检查：
- readOnly=true；
- ramWrites=0；
- inputInjection=false；
- no Worker replacement/wrap；
- no Blob/Data/ObjectURL Worker creation/rewrite；
- no production auto-promotion。

Harness 不得要求 Owner 真人 Browser；使用 fixture/mock/synthetic CDP topology。

## Stop condition

`DISCOVERY V2 CONFORMANCE HARNESS READY`

必须能对当前 HEAD 生成 machine-readable + 中文 summary，并把现存 drift 精确暴露出来，而不是为了绿色结果隐藏 FAIL。
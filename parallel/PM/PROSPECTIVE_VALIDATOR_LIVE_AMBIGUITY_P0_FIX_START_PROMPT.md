# WOF Prospective Validator Live Topology Ambiguity P0 Fix — Fresh Stage

stageId: `PROSPECTIVE_VALIDATOR_LIVE_AMBIGUITY_P0_FIX_V1`
priority: `P0`

## 启动去重守卫

先读取：
- `parallel/PM/STAGE_DEDUP_GUARD.md`
- `parallel/PM/OWNER_INTERVENTION_GATE.md`
- `parallel/PROSPECTIVE_VALIDATOR_QA_DISCOVERY_V2_HARDENING/RESULT.md`
- GitHub 默认分支最新状态

若等价修复已完成，输出 `ALREADY COMPLETE — SAFE TO CLOSE — 当前线程空闲` 并停止。
若 claim `parallel/PM/STAGE_CLAIMS/PROSPECTIVE_VALIDATOR_LIVE_AMBIGUITY_P0_FIX_V1.json` 已存在，输出 `ALREADY CLAIMED — SAFE TO CLOSE — 当前线程空闲` 并停止。
否则原子 create-file claim，成功后才工作；完成/阻断更新 claim。

## 写入范围

只允许修改：
- `parallel/PROSPECTIVE_VALIDATOR/**`
- mandatory stage claim

不要修改 Recorder / PYLAUNCH / Browser Fleet / Alpha / LIVE_PROOF_BUNDLE。

## 精确 P0

Fresh independent QA 已证明：live room 从唯一 Worker↔page ownership 变成 shared/cross-page ambiguity 后，当前 10 秒 full-audit gap 内仍可能继续 `drain()/ingest()` prospective evidence，从而污染 conservative gates 并可能错误产生 research PASS。

## 必须修复

1. 在任何一次 prospective `drain()/ingest()` 前，必须用当前 topology 重新证明该 live room 的 Worker↔page ownership 仍唯一。
2. 一旦 ownership 已变 ambiguous，必须在本轮 evidence ingest 前 censor/finalize；不允许正长度 audit gap。
3. 可以优化扫描成本，但不能以接收 post-ambiguity prospective evidence 为代价。
4. 保持 two pages / two distinct Workers 可独立运行。
5. 保持 exact World 921031 identity、freeze hash、discovery-only exclusion、全部 conservative gates。
6. 保持 research-only / no production promotion。
7. 保持 readOnly=true / ramWrites=0 / inputInjection=false / no Worker replacement / no Blob rewrite。
8. 吸收 QA fixture `live_unique_to_shared_worker.json` 与控制流复现，并增加修复回归。
9. 不要求 Owner 真人 Browser。

## Stop condition

`PROSPECTIVE VALIDATOR LIVE AMBIGUITY P0 FIX READY — READY FOR FRESH QA RETEST`

如果仍存在任何 topology 变歧义后可 ingest prospective evidence 的路径，则必须 BLOCKED，不得宣称 READY。
# WOF Prospective Validator — Result

更新时间：2026-09-01

## Verdict

**PROSPECTIVE VALIDATOR LIVE AMBIGUITY P0 FIX READY — READY FOR FRESH QA RETEST**

Fresh independent QA 暴露的 live topology ambiguity P0 已在 repository-side 关闭；Owner 不需要真人 Browser 操作。

## P0 closure — no positive ingest audit gap

`live_validator_v2.py` 不再允许 live room 在 topology audit 间隔内独立 `drain()/ingest()`：

- `AUDIT_LIVE_TOPOLOGY_INTERVAL = 0.0`，不存在正长度 full-audit gap；
- prospective `drain()` 只存在于 fresh full topology scan 成功后的同一控制流中；
- full scan 固定 `skip_page_ids=set()`，live page 不再因为已连接而被跳过；
- scan 后不仅检查 ambiguity，还必须正向重证当前 `(pageTargetId, workerTargetId)` exact supported pair；
- 只有本次 full scan 重新产出的 exact pair 才允许进入该轮 `drain()/ingest()`；
- ownership 已变 shared/cross-page ambiguous 时，相关 room 先以 `worker-association-ambiguous` censor/finalize，再到 drain 阶段；
- topology 扫描异常或无法重新证明 pair 时，room 立即以 `worker-association-unverified` fail closed；不会把这段未验证期间积累的 Worker queue 延后到之后某次成功 audit 再摄入。

因此 QA fixture 中 `t=100` 唯一、`t=101` 变 shared、`t=105` 仍位于旧 10 秒 gap 的复现，当前实现会在 `t=105` full reproof 时先 finalize，post-ambiguity prospective drain/ingest 数量为 0。

## Finalization ingest guard

旧 `finalize_room(remote=True)` 会执行 Worker `stop()` 并把返回 queue 再 `ingest()`；如果退出恰好发生在未重新审计的 ambiguity window，这同样可能把未验证证据带入最终 counters。

现已改为：

- remote cleanup 仍可执行 `stop()` 清理 sampler；
- `stop()` 返回 payload 固定丢弃，不再进入 prospective ingest；
- 已经通过前序 full audit 摄入的 `room.pending` 仍按 censor 语义结束。

最终 verdict 不再能被未经 fresh topology proof 的 shutdown payload 推动。

## QA fixture + regression absorbed

已把 independent QA fixture 吸收到 Validator lane：

- `fixtures/live_unique_to_shared_worker.json`
- `test_live_ambiguity_p0_fix.py`
- `LIVE_AMBIGUITY_P0_FIX_RESULT.json`

新增 4 个 targeted regression：

1. unique -> shared Worker：必须先 finalize，drain=0 / ingest=0；
2. two pages / two distinct Workers：各自 exact pair 重新证明后可独立 drain；
3. topology reproof failure：立即 censor/finalize，不允许 deferred buffered ingest；
4. remote cleanup payload：没有 fresh audit 时不得进入 ingest。

本阶段对 production method 做 repository-equivalent extracted control-flow smoke，4/4 PASS；同时按原 independent QA 的静态判据复算：旧 conditional live-page skip pattern 已不存在、audit interval 为 0、unsafe-window predicate 为 false。

Repository test surface 由原 **40** cases 增至 **44** cases；原 hardening / validator / discovery tests 文件未被修改。

## Preserved hardening and conservative gates

此前 Discovery V2 hardening 保持不变：

- endpoint-level Worker↔page relation graph；
- shared Worker under two pages 全部 fail closed；
- two pages / two distinct exact Workers 独立；
- direct fallback 不使用 Worker `openerId` 作为 parent authority；
- `parentId` / `parentFrameId` authority 与唯一 WOF page compatibility 规则保持；
- assigned endpoint / returned websocket 仍必须 loopback + exact same port；
- blob/data/hashed/no-extension Worker URL shape 仍不是身份 gate；
- exact World 921031 SHA-256 identity 保持；
- candidate freeze/hash 与 mutation rejection 保持；
- discovery-only evidence 不进入 prospective counters；
- conservative gates 仍执行 `minProspectiveSignals` / `minProspectiveRooms` / `requireZeroHardMiss` / `minDistinctTargets` / `minObservedTypes` / `requireLifecycleReset`；
- unknown conservative gate fail closed；
- PASS 仍固定 `PROSPECTIVE_PASS_RESEARCH_ONLY`；
- `productionPromotionAllowed=false`。

## Safety invariants

保持：

- `readOnly=true`；
- `ramWrites=0`；
- `inputInjection=false`；
- no `window.Worker` replacement；
- no Blob/Data/ObjectURL Worker rewrite；
- 不修改游戏 RAM；
- 不注入游戏输入；
- research-only / no production promotion。

## Owner entrypoints

保持：

- `RUN_PROSPECTIVE_VALIDATOR.cmd` -> `live_validator_v2_hardened.py`；
- direct `python live_validator.py ...` -> hardened V2；
- hardened wrapper 继续安装 relation-graph、direct-fallback、endpoint confinement guards。

## Stage artifacts / commits

- core P0 fix: `2d732329d43362f0dc34c5e1a8391b90b5109725`
- absorbed fixture: `e45557d08e804e39ff6ae6c0c3d11fd62efa4597`
- targeted regression: `9103f8b1d992f45e25a8e914dac0e42c34297092`
- machine result: `634dca2fffe8419c06b6a9f6f39e4ef92c48c4ee`

## Owner action

**你现在需要操作：NO**

下一步应由新的 fresh QA stage 独立复测本 P0，不在本 fix 线程自证 QA。

## Stop condition

**PROSPECTIVE VALIDATOR LIVE AMBIGUITY P0 FIX READY — READY FOR FRESH QA RETEST**

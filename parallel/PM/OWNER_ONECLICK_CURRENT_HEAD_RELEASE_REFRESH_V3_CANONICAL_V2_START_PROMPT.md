# WOF Owner OneClick — Current-HEAD Release Refresh V3 — Canonical Dedup V2 Wrapper

stageId: `OWNER_ONECLICK_CURRENT_HEAD_RELEASE_REFRESH_V3_CANONICAL_V2`
dedupProtocol: `v2`
dedupKey: `owner.oneclick.current-head.release-refresh-v3`
dedupMode: `exclusive`

你这次负责 **Owner OneClick Current-HEAD Release Refresh V3**，但必须按当前 canonical dedup v2 执行。

本 prompt 只升级 ownership/dedup 入口；功能、QA、read/write boundary、success/failure stop 全部以：

`parallel/PM/OWNER_ONECLICK_CURRENT_HEAD_RELEASE_REFRESH_V3_START_PROMPT.md`

为准。

开始前必须重新读取当前 `main`、`parallel/PM/STAGE_DEDUP_GUARD.md`、原 V3 prompt、当前 Owner OneClick RESULT/manifest/refresh generator，以及所有 V3 hard upstream gates。

先检查等价工作：

- 若当前 manifest 已准确代表一个 immutable current release candidate，且原 V3 要求的 package/Windows/integrity/UTF-8 gate 已 durable PASS，则 `ALREADY COMPLETE — SAFE TO CLOSE`；
- 若等价 canonical/stage work 已 ACTIVE，则 `ALREADY CLAIMED — SAFE TO CLOSE`；
- 否则 create-only：
  `parallel/PM/DEDUP_CLAIMS/owner.oneclick.current-head.release-refresh-v3.json`
  使用 fresh unpredictable claimToken，重新读取验证 ownership 后再创建 stage claim：
  `parallel/PM/STAGE_CLAIMS/OWNER_ONECLICK_CURRENT_HEAD_RELEASE_REFRESH_V3_CANONICAL_V2.json`。

硬门槛仍完全遵从原 V3 prompt：Transport formal real-adapter fresh QA、Recorder authority generation QA、PYLAUNCH startup attestation/current blobs、以及 package-selected runtime file 无 active P0/P1 fix。任何一项不绿都必须 fail closed / WAITING_GATE，不得为了更新 hash 提前刷新。

如果当前 package selection policy 包含 Alpha owner/live-proof assets，必须确认 Recovery V2 COMPLETE 后当前 selected assets 与 immutable source candidate 一致；如果新 dual-overlay proof tooling 不属于 package selection，必须在 RESULT 明确记录“不属于 selected payload”的依据，不能静默遗漏。

不得修改上游 PYLAUNCH、Recorder、Transport、Alpha product/HUD、danger rules、target semantics、input/AI/RAM 行为来让 package 通过。

成功 stop：
`PASS — OWNER ONECLICK CURRENT-HEAD RELEASE REFRESH V3 — PACKAGE GATE CLOSED`

失败 stop：
`BLOCKED — OWNER ONECLICK CURRENT-HEAD RELEASE REFRESH V3 — <precise blocker>`

Owner action: **NO**。

严格持续到 PASS / BLOCKED / WAITING_GATE / duplicate stop。
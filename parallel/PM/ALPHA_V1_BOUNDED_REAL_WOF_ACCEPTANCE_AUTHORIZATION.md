# Alpha V1 — Bounded Real WOF Acceptance Authorization

Date: 2026-09-02
Status: **AUTHORIZED — START BOUNDED REAL WOF ACCEPTANCE**

## Repository gate closure

The final repository gate is closed by:

`PASS — ALPHA V1 PROOF-AUTHORITY FINAL FRESH QA RECOVERY V2 — PREFLIGHT COMPATIBILITY REPAIRED / 17/17 INDEPENDENT CASES PASS — READY FOR BOUNDED REAL WOF ACCEPTANCE`

Durable result:

`parallel/PM/RESULTS/ALPHA_V1_PROOF_AUTHORITY_FINAL_FRESH_QA_PREFLIGHT_RECOVERY_V2_RESULT.md`

Repository QA stops here. Do not open second-opinion, cross-check, V3/V4 QA, readiness audit, or closeout QA unless a concrete live acceptance defect later requires a focused repair/retest.

## Authorized OneClick candidate

Use the existing immutable Owner OneClick V4 candidate:

- source commit: `770d240d286aa69c95e002a1ea88bcc3edb36407`
- package version: `2026.09.02.770d240d286a`
- selection policy: `owner-oneclick-runtime-v2`
- manifest: `parallel/OWNER_ONECLICK/package_manifest.json`
- manifest publish commit: `fa8f48712d3da580ca2b9aec437c1665ed6a8de8`
- V4 PASS record: `7ad0c93973ff1ec52b8daf1954ffd140b4b06117`

Current manifest remains pinned to the same source commit and package version. Later PM, Collector and Training Farm commits do not alter this immutable acceptance candidate.

Safety remains:

- `readOnly=true`
- `ramWrites=0`
- `inputInjection=false`

## Owner procedure

Follow exactly:

`parallel/PM/ALPHA_V1_BOUNDED_LIVE_ACCEPTANCE_OWNER_FLOW_V2.md`

Bounded flow:

`启动最终 OneClick -> 进入别人正在玩的活跃房间 -> 约 5–10 分钟关键观察/简单操作`

No DevTools. No manual script. No full-game clear required.

Observe, when naturally available:

- enemy-head `1P / 2P / 3P` follows the correct enemy;
- player-head `[危险]` follows the correct player when a real warning occurs;
- left/right, lane-depth, normal jump, rear jump, rapid forward, whole-screen scroll;
- retarget;
- resize/fullscreen/DPR remap;
- death/respawn;
- stale/invalid authority hide/fixed fallback.

Do not guess unsupported Chinese enemy/move mappings. Current production authority remains only the exact repository-enabled rules.

## Owner report

If PASS, one short line is enough.

If a failure occurs, record the surface/scene/symptom and preferably one 5–15 second clip or 1–2 screenshots. Do not debug with DevTools.

Accepted one-line format:

`PASS/FAIL/NOT EXERCISED | surface=危险检测/玩家[危险]/怪物目标/stale回退 | scene=后跳/卷屏/retarget/resize/... | symptom=一句话描述`

## Release boundary

Real Browser/WOF evidence is now the only remaining V1 release-closing gate.

**START BOUNDED REAL WOF ACCEPTANCE**

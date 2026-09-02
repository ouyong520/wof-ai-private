# Alpha Transport Formal Real-Adapter Integration Current-HEAD Fresh QA V3 — Recovery V4

stageId: `ALPHA_TRANSPORT_FORMAL_REAL_ADAPTER_INTEGRATION_CURRENT_HEAD_FRESH_QA_V3_RECOVERY_V4`
dedupProtocol: `v2`
dedupKey: `alpha.transport.formal-real-adapter-integration.current-head-fresh-qa-v3-recovery-v4`
dedupMode: `exclusive`

Priority: **P0/P1 release gate recovery/finalization**

Repository: `ouyong520/wof-ai-private`

## PM authorization

The original V3 worker is no longer an active chat, but its canonical claim remains historical ACTIVE:

`parallel/PM/DEDUP_CLAIMS/alpha.transport.formal-real-adapter-integration.current-head-fresh-qa-v3.json`

Do not overwrite/delete/reuse that claim. This Recovery V4 is explicitly authorized with a new dedup key.

Current durable repository evidence already contains the V3 current-source execution matrix, including `EXECUTION_RESULT.json` with 85/85 PASS at staging time, but no durable final `RESULT.md` and no valid release-gate closure.

## Goal

Recover the interrupted QA, re-read current `main`, revalidate the exact tested release-runtime/SUT blobs and the completed execution evidence, rerun only what current drift requires, then produce a durable successor verdict that release selectors may consume.

## Required reads

- current `main` HEAD and recent related commits;
- original prompt `parallel/PM/ALPHA_TRANSPORT_FORMAL_REAL_ADAPTER_INTEGRATION_CURRENT_HEAD_FRESH_QA_V3_START_PROMPT.md`;
- `parallel/ALPHA_TRANSPORT_FORMAL_INTEGRATION_CURRENT_HEAD_FRESH_QA_V3/**`;
- original V3 canonical/stage claims;
- current `product/alpha/wof_alpha_real_worker.js`, HUD, bootstrap/loader;
- current formal adapter/SUT seam and PYLAUNCH discovery/probe sources;
- Owner OneClick V3 WAITING_GATE evidence.

## Recovery rules

1. Claim this recovery using canonical dedup v2; do not mutate the old V3 claim.
2. Verify current exact Git blobs against the execution matrix.
3. PM/result-only commits do not invalidate a tested runtime; runtime/SUT blob drift does.
4. If any tested runtime/SUT blob moved, rerun affected current-head cases or stop `BLOCKED — CURRENT-HEAD DRIFT`.
5. Historical Recovery V2 remains supportive only.
6. QA-only: do not modify production/formal/PYLAUNCH/Recorder/OneClick implementation.
7. No Browser/WOF.

## Minimum verdict evidence

Record exact tested HEAD/blobs and the independent current-head totals/raw paths, including the current equivalents of:

- exact worker/HUD/player-head transport adversarial coverage;
- formal adapter regression;
- integration regression;
- detector-local World 921031 identity regression;
- formal SUT current-equivalent replay;
- one-in-flight/no-catch-up;
- stale completion/rebind/reconnect/runtime replacement;
- 249/250 ms and 1500/1501 ms;
- exact safety `readOnly=true`, `ramWrites=0`, `inputInjection=false` and related no-control boundaries.

## Success

`PASS — ALPHA FORMAL REAL-ADAPTER INTEGRATION CURRENT-HEAD FRESH QA V3 RECOVERY V4 — CURRENT RELEASE RUNTIME VERIFIED / V3 INTERRUPTION SUPERSEDED`

Write a durable successor RESULT/STATUS and close only this Recovery V4 claim/stage. Explicitly mark the old V3 ACTIVE claim as historical interrupted evidence superseded by this recovery for release gating.

## Failure

`BLOCKED — ALPHA FORMAL REAL-ADAPTER INTEGRATION CURRENT-HEAD FRESH QA V3 RECOVERY V4 — <precise blocker>`

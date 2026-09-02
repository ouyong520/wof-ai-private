# Alpha Transport Formal Real-Adapter Integration Current-HEAD Fresh QA V3

stageId: `ALPHA_TRANSPORT_FORMAL_REAL_ADAPTER_INTEGRATION_CURRENT_HEAD_FRESH_QA_V3`
dedupProtocol: `v2`
dedupKey: `alpha.transport.formal-real-adapter-integration.current-head-fresh-qa-v3`
dedupMode: `exclusive`

Priority: **P0/P1 release gate — current release-runtime revalidation**

Repository: `ouyong520/wof-ai-private`

## PM reason

The PM-authorized Fresh QA Recovery V2 is durably PASS, but its tested release-runtime blobs are no longer current after the Alpha V1 player-head / dual-overlay integration work.

Owner OneClick Current-HEAD Release Refresh V3 correctly stopped `WAITING_GATE` because the prior fresh QA audited, among others:

- old `product/alpha/wof_alpha_real_worker.js` blob `9c63a2c6a185ead8406487edd10038c035d41623`;
- old `product/alpha/wof_alpha_hud.js` blob `f41838c760ee9f7c40f3c91c71687e72ba740803`.

Current release runtime has moved to the current HEAD pair (re-read exact blobs before claiming; at PM staging time OneClick observed `real_worker=b7f4506fc90b681ede059df5ad3316e665c6f15e` and `HUD=50d944c451ac94b114e4f86441aeae8ad6b25c78`).

This is a new current-HEAD fresh QA, not a rerun of the historical V1 claim and not an implementation fix.

## Before work

Strictly follow `parallel/PM/STAGE_DEDUP_GUARD.md` canonical dedup v2.

Re-read:

- current `main` HEAD and recent related commits;
- `parallel/ALPHA_TRANSPORT_FORMAL_INTEGRATION/RESULT.md`;
- `parallel/ALPHA_TRANSPORT_FORMAL_INTEGRATION_QA_RECOVERY_V2/RESULT.md`;
- `parallel/OWNER_ONECLICK/RESULT.md` current V3 WAITING_GATE evidence;
- current `product/alpha/wof_alpha_real_worker.js`;
- current `product/alpha/wof_alpha_hud.js`;
- current Alpha bootstrap/loader files consumed by formal integration;
- current `parallel/ALPHA_TRANSPORT_FORMAL_INTEGRATION/**` real adapter/SUT seam;
- current PYLAUNCH discovery/probe interfaces;
- relevant stage/canonical claims.

If a newer durable QA already certifies the exact current release-runtime blobs against all attacks below, stop `ALREADY COMPLETE — SAFE TO CLOSE`.

If this exact current-head QA is ACTIVE, stop `ALREADY CLAIMED — SAFE TO CLOSE`.

Otherwise atomically create the canonical claim, reread and verify exact token/key/mode/stageId/state, then create the stage claim.

## Goal

Independently decide whether the **current Alpha release-runtime generation** still satisfies the Formal Real-Adapter integration contract after the player-head / dual-overlay production changes, so Owner OneClick V3 and current-head acceptance can consume a non-stale fresh QA.

## Required checks

At minimum independently verify:

1. current `wof_alpha_real_worker.js` still performs detector-local exact World 921031 identity proof at observer install;
2. current runtime still requires exact 1 MiB CPU-logical SHA-256 `5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62`;
3. same-`targetId` runtime/execution-context replacement between Discovery and observer install fails closed;
4. the player-head spatial publication added in the current worker does not weaken session/pair-generation/pair-nonce/runtime-epoch authority or stale-completion revocation;
5. current HUD changes for player-head warning / enemy target labels do not widen warning authority, accept stale pair state, or bypass formal adapter binding;
6. disconnect/reconnect, Worker replacement/reinstall, rebind and runtime-epoch reset revoke old authority;
7. one tick in flight / no catch-up / queue depth 0 remains exact;
8. heartbeat/stale boundaries remain 249/250 ms and 1500/1501 ms as contracted;
9. RC5/bootstrap/transport failure still leaves gameplay unaffected;
10. current SUT seam consumes the exact current production worker/HUD/bootstrap/real-adapter files it claims and is not detached from current source;
11. current PYLAUNCH discovery/probe generation semantics remain compatible and do not reintroduce targetId-only trust;
12. safety remains exact: `readOnly=true`, `ramWrites=0`, `inputInjection=false`, `workerReplacement=false`, `blobRewrite=false`, `gamePostMessageControl=false`, `heapWrites=false`, `assistMode=false`.

## Required execution

Use an independent oracle/fixture against the current real seam. Historical Recovery V2 selftests and the prior Fresh QA Recovery V2 PASS are supportive evidence only, not the current verdict.

Run current equivalents of:

- `node parallel/ALPHA_TRANSPORT_FORMAL_INTEGRATION_QA_PREP/formal_integration_qa.mjs --sut parallel/ALPHA_TRANSPORT_FORMAL_INTEGRATION/formal_integration_qa_sut.mjs`
- `node parallel/ALPHA_TRANSPORT_FORMAL_INTEGRATION/detector_local_identity_test.mjs`
- `node parallel/ALPHA_TRANSPORT_FORMAL_INTEGRATION/integration_test.mjs`
- formal adapter regressions/selftests;
- stale-generation regression;
- frozen Safe Transport consumer gate.

Add independent adversarial cases specifically around the **current** worker/HUD changes where needed. Verify the seam is source-pinned to the current blobs before accepting any PASS.

If the prepared QA seam itself is stale and cannot test current production without implementation changes, stop with `BLOCKED — SUT DRIFT` and record the exact stale pin; do not silently patch production in the QA lane.

## Write boundary

QA only. Write only:

- `parallel/ALPHA_TRANSPORT_FORMAL_INTEGRATION_CURRENT_HEAD_FRESH_QA_V3/**`;
- this stage's RESULT/STATUS evidence;
- this stage's canonical/stage claims.

Do not modify:

- `product/alpha/**`;
- `parallel/ALPHA_TRANSPORT_FORMAL_INTEGRATION/**` implementation;
- PYLAUNCH / Recorder / Live Proof / Owner OneClick / HUDANCHOR implementation;
- historical QA/claim evidence.

If QA finds a defect, stop BLOCKED with the first deterministic repro; do not fix it here.

## Drift rule

Immediately before finalizing, reread current `main` and exact tested production/SUT blobs. If any tested release-runtime blob moved, rerun against the new current blob or stop `BLOCKED — CURRENT-HEAD DRIFT`.

PM/result-only commits that do not alter tested runtime payloads do not invalidate the decision; record that distinction.

## Success stop

`PASS — ALPHA FORMAL REAL-ADAPTER INTEGRATION CURRENT-HEAD FRESH QA V3 — CURRENT RELEASE RUNTIME VERIFIED`

Close this stage with exact tested HEAD, current production/SUT blob SHAs, independent pass counts/raw result paths, ownerAction=`NO`, and explicit statement that the prior Fresh QA Recovery V2 remains valid historical evidence but is superseded for release gating by this current-head result.

## Failure stop

`BLOCKED — ALPHA FORMAL REAL-ADAPTER INTEGRATION CURRENT-HEAD FRESH QA V3 — <precise blocker>`

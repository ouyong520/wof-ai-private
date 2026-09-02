# Alpha Formal Real-Adapter — Current Alpha Blob Fresh Revalidation

stageId: `ALPHA_FORMAL_REAL_ADAPTER_CURRENT_BLOB_REVALIDATION_V1`

Priority: **P1 Alpha release freshness gate / independent QA**

Purpose: revalidate the Formal Real-Adapter integration after the mandatory Alpha V1 enemy target-head-label implementation changed release-consumed Alpha blobs, especially `product/alpha/wof_alpha_real_worker.js` and `product/alpha/wof_alpha_hud.js`. The historical Recovery V2 Formal fresh QA PASS pinned older blobs and must not be mechanically reused for the current candidate.

## Start / dedup

Before work, re-read latest `main`, recent Alpha/Formal commits, `parallel/PM/STAGE_DEDUP_GUARD.md`, current `parallel/PM/STAGE_CLAIMS/**`, and at minimum:

- `parallel/ALPHA_TRANSPORT_FORMAL_INTEGRATION_QA_RECOVERY_V2/RESULT.md`
- `parallel/ALPHA_ENEMY_TARGET_HEAD_LABELS/RESULT.md`
- current `product/alpha/wof_alpha_real_worker.js`
- current `product/alpha/wof_alpha_hud.js`
- current bootstrap/loader/core files consumed by Formal integration
- `parallel/ALPHA_TRANSPORT_FORMAL_INTEGRATION/real_adapter.py`
- current formal integration QA SUT / detector-local identity / integration tests
- current target-label independent QA claim/result if it exists by the time this stage starts.

If an equivalent current-blob Formal independent QA is already COMPLETE/PASS on the exact current Alpha/Formal blobs, stop `ALREADY COMPLETE — SAFE TO CLOSE`.
If equivalent work is CLAIMED/EXECUTING, stop `ALREADY CLAIMED — SAFE TO CLOSE`.
Otherwise atomically create `parallel/PM/STAGE_CLAIMS/ALPHA_FORMAL_REAL_ADAPTER_CURRENT_BLOB_REVALIDATION_V1.json` with exact current HEAD and exact production blob pins.

## Scope

Independent repository QA only. Do not modify Alpha/Formal implementation. Allowed writes only under `parallel/ALPHA_FORMAL_REAL_ADAPTER_CURRENT_BLOB_REVALIDATION/**` plus this claim.
No Browser/WOF launch is required. Do not start broad capture or gameplay input injection.

## Required revalidation

Independently verify the changed current Alpha blobs preserve the already-accepted Formal invariants:

1. detector-local exact World 921031 identity remains fail-closed and freshly measured in the current Worker;
2. same-targetId runtime/execution-context replacement cannot inherit stale authority;
3. pair/session/generation/nonce/runtime-epoch authority remains exact across rebind/replacement;
4. old/late in-flight completion cannot publish into a new generation;
5. disconnect/stale status revokes warning authority safely;
6. one-in-flight/no-catch-up/queue-depth-zero behavior remains intact;
7. warning heartbeat/freshness semantics remain compatible after marker-channel additions;
8. enemy-target marker publication remains decorative and cannot authorize/refresh danger warning authority;
9. new marker fields/payloads do not weaken adapter validation or transport authority;
10. current HUD changes preserve exact transport-pair checks and warning revocation behavior;
11. read-only, `ramWrites=0`, input injection false, no Worker replacement, no Blob rewrite, no game memory writes remain exact;
12. current Formal regression/seam still actually reads/tests the current production Alpha blobs rather than a copied stale implementation.

Re-run current Formal integration deterministic tests/fixtures where possible. Add an independent current-blob inspection/fixture if needed. Do not treat the historical Recovery V2 PASS alone as sufficient because it pinned `wof_alpha_real_worker.js` blob `9c63a2c6...` while the target-head-label implementation reports current worker blob `924d02eb...` and current HUD blob `b6f9cbf2...`.

The target-head projection profile may still be intentionally `UNPROVEN`/silent. That is not itself a Formal defect if the marker path fails closed and normal warning authority is unaffected.

## Success / failure

Success:
`PASS — ALPHA FORMAL REAL-ADAPTER CURRENT-BLOB REVALIDATION — FRESHNESS GATE CURRENT`

Failure:
`BLOCKED — ALPHA FORMAL REAL-ADAPTER CURRENT-BLOB REVALIDATION — <precise blocker>`

Owner action: **NO**.

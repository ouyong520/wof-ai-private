# WOF Alpha Safe Transport — Formal Real-Adapter Integration Recovery V2

stageId: `ALPHA_TRANSPORT_FORMAL_REAL_ADAPTER_INTEGRATION_RECOVERY_V2`

Priority: **P0/P1 — Alpha mainline recovery**

PM has audited the prior V1 claim as stale/superseded after the execution chat stopped without a durable COMPLETE/BLOCKED result. Re-read current HEAD before work. Follow `parallel/PM/STAGE_DEDUP_GUARD.md`; the superseded V1 claim does not block this recovery stage.

If an equivalent durable integration result already exists, return `ALREADY COMPLETE — SAFE TO CLOSE — 当前线程空闲`. Otherwise atomically claim `parallel/PM/STAGE_CLAIMS/ALPHA_TRANSPORT_FORMAL_REAL_ADAPTER_INTEGRATION_RECOVERY_V2.json`.

Read the V1 prompt, current `product/alpha/**`, `parallel/ALPHA_TRANSPORT_FORMAL_INTEGRATION/**`, current PYLAUNCH interfaces, all V1 implementation commits, and the prepared formal integration QA harness. Continue from current committed state; do not redo completed work.

Allowed writes: `product/alpha/**`, `parallel/ALPHA_TRANSPORT_FORMAL_INTEGRATION/**`, own claim. Do not modify PYLAUNCH, Recorder, Unified Live Proof, HUD, Owner OneClick, Prospective.

Required before closing: finish the production-facing real-adapter wiring; prove current pair/session/generation/nonce and detector-local identity authority; stale/rebind/runtime/Worker replacement fail closed; no Worker wrap/Blob rewrite/input injection/RAM writes; no-transport and unsupported identity leave gameplay unaffected; run deterministic integration tests, frozen 67-vector consumer gate, and current relevant RC4/RC5 bootstrap regressions; re-read current PYLAUNCH blobs before finalization.

Produce durable RESULT.md + machine-readable result. Success: `ALPHA FORMAL REAL-ADAPTER INTEGRATION READY — READY FOR FRESH INTEGRATION QA`. Failure: one precise P0/P1 blocker. Owner action: **NO**.

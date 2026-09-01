# PYLAUNCH Startup Attestation Fresh QA Start Prompt

stageId: `PYLAUNCH_STARTUP_ATTESTATION_QA_V1`

Priority: **P0/P1 Alpha release gate**

Follow `parallel/PM/STAGE_DEDUP_GUARD.md`. Re-read current HEAD before work. If equivalent PASS already exists, return `ALREADY COMPLETE — SAFE TO CLOSE — 当前线程空闲`. If claimed, return `ALREADY CLAIMED — SAFE TO CLOSE — 当前线程空闲`.

Otherwise claim `parallel/PM/STAGE_CLAIMS/PYLAUNCH_STARTUP_ATTESTATION_QA_V1.json`.

Read the completed startup-attestation fix result and current `parallel/PYLAUNCH/**` implementation. This is independent QA; do not modify PYLAUNCH product code.

Attack at minimum: missing/empty Browser metadata; malformed product/version shapes; websocket endpoint host/port mismatch; stale endpoint metadata after reconnect; same targetId across runtime generations; malformed DevTools version response; rejected attestation must invalidate stale authority; valid Chrome/Edge localhost endpoint remains accepted; all existing identity-generation regressions remain green.

Allowed writes only under `parallel/PYLAUNCH_QA_STARTUP_ATTESTATION/**` plus own claim. Produce RESULT.md + machine-readable result + deterministic runner/fixtures. Re-run relevant current PYLAUNCH regression suites.

Success: `PASS — PYLAUNCH STARTUP ATTESTATION FRESH QA — RELEASE GATE CLOSED`.

Failure: one precise P0/P1 blocker with reproducible fixture. Owner action: **NO**.
# PYLAUNCH Startup Browser Metadata Attestation Fix — Start Prompt

stageId: `PYLAUNCH_STARTUP_ATTESTATION_FIX_V1`

Priority: **P0/P1 — Alpha mainline startup authority**

## Dedup / claim

Before work, follow `parallel/PM/STAGE_DEDUP_GUARD.md`.

If equivalent durable result already exists, return exactly:
`ALREADY COMPLETE — SAFE TO CLOSE — 当前线程空闲`

If already claimed/executing, return exactly:
`ALREADY CLAIMED — SAFE TO CLOSE — 当前线程空闲`

Otherwise claim under:
`parallel/PM/STAGE_CLAIMS/PYLAUNCH_STARTUP_ATTESTATION_FIX_V1.json`

## Read first

Re-read current HEAD, especially:
- `parallel/PYLAUNCH/wof_launcher/browser.py`
- `parallel/PYLAUNCH/wof_launcher/cdp.py`
- `parallel/PYLAUNCH/wof_launcher/monitor.py`
- `parallel/PYLAUNCH/tests/**`
- `parallel/PYLAUNCH_QA_IDENTITY_GENERATION/QA_RESULT.md`
- `parallel/PYLAUNCH_QA_IDENTITY_GENERATION/test_startup_attestation_regression.py`
- `parallel/PM/STAGE_CLAIMS/PYLAUNCH_IDENTITY_CACHE_GENERATION_QA_V1.json`

## Current blocker

Fresh QA blocked on startup Browser attestation:
- missing `/json/version` Browser metadata can currently be accepted;
- a non-browser / malformed websocket endpoint shape can currently be accepted;
- startup authority therefore is not fully fail-closed before discovery/identity logic begins.

The identity-cache generation fix itself is not the blocker here. Do not reopen that solved scope.

## Goal

Make PYLAUNCH startup prove that the connected loopback CDP endpoint is a valid Browser-level Chrome/Edge endpoint before it can become authoritative.

Required semantics:
1. `/json/version` metadata required and structurally valid.
2. Browser identity must be recognized as supported Chrome/Chromium/Edge family according to existing product policy; unsupported/missing metadata fails closed.
3. Browser-level `webSocketDebuggerUrl` must have the expected browser endpoint shape; page/worker/non-browser websocket URLs must not be accepted as browser authority.
4. loopback + exact configured port confinement remains mandatory.
5. reconnect/new browser generation must repeat startup attestation; no stale accepted startup metadata reuse.
6. Chinese-first owner diagnostics for rejection.
7. preserve Page.getFrameTree/parentFrame, identity-generation fix, read-only allowlist, no input, no RAM writes.

## Regression

At minimum cover:
- valid Chrome Browser metadata -> PASS;
- valid Edge/Chromium metadata if currently supported -> PASS;
- missing Browser metadata -> fail closed;
- malformed `/json/version` -> fail closed;
- page websocket endpoint masquerading as browser endpoint -> fail closed;
- worker/non-browser websocket shape -> fail closed;
- wrong host/port -> fail closed;
- reconnect forces fresh attestation;
- all existing PYLAUNCH discovery/parentFrame/identity-generation/endpoint tests remain green.

Use the fresh QA reproducer as an adversarial input; do not weaken it.

## Write boundary

Write only:
- `parallel/PYLAUNCH/**`
- mandatory claim under `parallel/PM/STAGE_CLAIMS/**`

Do not modify Owner One-Click, Recorder, Live Proof, Transport, HUD, or `product/alpha/**`.

## Delivery reassessment

Before stopping, state:
- whether the startup attestation blocker is truly closed;
- exact regression counts;
- whether fresh PYLAUNCH QA is now unblocked;
- Owner action required or not.

## Stop

Success:
`PYLAUNCH STARTUP ATTESTATION FIX READY — READY FOR FRESH QA`

Or one precise blocker.

Owner action: **NO**.

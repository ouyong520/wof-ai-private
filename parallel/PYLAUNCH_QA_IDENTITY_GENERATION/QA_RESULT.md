# PYLAUNCH Identity Cache Generation QA — BLOCKED

Date: 2026-09-01
Stage: `PYLAUNCH_IDENTITY_CACHE_GENERATION_QA_V1`

## Verdict

**BLOCKED — current HEAD fails a mandatory retained startup-safety invariant.**

This is a fresh QA/disproof result. The identity-generation hardening itself is present in current production code, but this stage cannot PASS because the start prompt explicitly requires the checked launch/endpoint safety lane, including startup `/json/version` metadata attestation, to remain green.

## QA snapshot

Fresh-QA base HEAD inspected before evidence-only commits:

- commit: `3cf948005329568c09fded1ff31bcec2a297317b`
- `parallel/PYLAUNCH/wof_launcher/discovery_v2.py`: `ec9d27bfe26557a11187a23853893b898a3366d1`
- `parallel/PYLAUNCH/wof_launcher/monitor.py`: `4430f7e927265cd3366fd70ce560c375aa878993`
- `parallel/PYLAUNCH/wof_launcher/browser.py`: `e883030fe8a90333b8ed58aae5699118b2c876fe`
- `parallel/PYLAUNCH/wof_launcher/probe.py`: `789a6849b826b35542b22d56a4d2ca3628d285a1`

The production `browser.py` blob was re-fetched after the fresh repro was committed and remained `e883030fe8a90333b8ed58aae5699118b2c876fe`.

## Blocking reproduction

Violated required rule from the QA start prompt:

> startup `/json/version` metadata attestation must remain green.

Current `probe_endpoint()` accepts a `/json/version` response that has no `Browser` metadata at all:

```python
ws = payload.get("webSocketDebuggerUrl")
if not isinstance(ws, str) or not websocket_matches_endpoint(ws, host, port):
    return None
return BrowserEndpoint(
    host=host,
    port=port,
    browser=str(payload.get("Browser") or "Chromium"),
    websocket_url=ws,
)
```

Therefore this payload is accepted instead of failing closed:

```json
{
  "webSocketDebuggerUrl": "ws://127.0.0.1:9223/devtools/browser/repro"
}
```

Fresh source-equivalent execution of the exact current logic produced:

```text
accepted_missing_Browser= True
synthesized_browser= Chromium
```

This is not merely a missing test: production code synthesizes the absent attested field.

A second deterministic selector violation is present in the same function: `websocket_matches_endpoint()` checks scheme, loopback host, and exact port, but `probe_endpoint()` does not require the browser-level `/devtools/browser/` path. A `/devtools/page/...` websocket on the same loopback port is therefore accepted as a browser endpoint.

Fresh executable regression evidence was added at:

- `parallel/PYLAUNCH_QA_IDENTITY_GENERATION/test_startup_attestation_regression.py`

The two assertions intentionally state the required fail-closed behavior and reproduce the current production violation.

## Identity-generation findings before the blocker

The identity-generation fix itself is present in the current blobs:

- `discover(..., identity_cache=...)` clears the supplied cache before target discovery, preventing cross-discovery-generation exact-identity reuse;
- `LauncherMonitor._connect()` clears `_last_worker_id`, `_last_identity`, and `_identity_cache` before installing a replacement browser-level CDP client;
- explicit `reconnect()` and connection-error reset paths also clear the same authority state;
- `parentId` is checked before `parentFrameId`; `parentFrameId` is only accepted when it maps uniquely to a page/frame identity;
- exact World authority remains `World 921031` SHA-256 `5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62`.

These observations do **not** override the blocking startup-safety failure.

## Regression policy

Historical implementation-thread PASS counts were not reused as fresh QA evidence. Once the mandatory retained startup-attestation invariant produced an actionable current-blob reproduction, the QA stop condition moved to the failure path; no overall PYLAUNCH regression PASS is claimed.

## Scope / handoff

Actual violating production module:

- `parallel/PYLAUNCH/wof_launcher/browser.py`

Required repair is narrow: make startup `/json/version` attestation fail closed rather than synthesizing missing browser metadata, and require a valid browser-level websocket endpoint shape. Re-run the full current PYLAUNCH offline regression matrix after that repair.

The Alpha/PyLauncher readiness blocker therefore remains **OPEN**. The downstream PyLauncher readiness stage is **NOT UNLOCKED** by this QA.

## Stop condition

> **BLOCKED — actionable current-blob reproduction produced; stage claim must be updated to BLOCKED.**

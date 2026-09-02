# Universal Collector Agent V1 Implementation

Work only on branch `universal-collector-agent-v1`. Do not merge to `main`.

Goal: build a generic Windows CMD collector shell whose job is Git <-> local collection communication. The first installed adapter is Browser WOF multi-room collection. Tampermonkey room auto-open/auto-close is out of scope.

Required owner UX:

```text
START_WOF_UNIVERSAL_COLLECTOR.cmd
-> fetch `collector/control/current.json`
-> show concise Chinese request
-> Owner presses Enter once
-> agent stays running
-> sources may appear/disappear/restart dynamically
-> collect through installed adapter
-> chunk and upload to request-selected destination
-> publish exact manifest
```

The Git request is declarative JSON, not arbitrary executable remote code. Unknown adapter/field/capability must fail closed.

Implement at minimum:

- UTF-8 Windows CMD launcher with Python/py fallback;
- generic request fetch/validation using GitHub CLI patterns already proven by `wof-winkawaks-bridge`;
- requestId + request blob/hash pinning;
- adapter registry and a first `browser_wof_rooms_v1` adapter;
- Browser Fleet manifest discovery plus independent localhost endpoint re-probe;
- 0..10 dynamic room hotplug after the single Enter;
- one room close/reload/failure does not stop other rooms;
- lifecycle-safe `sourceId/sourceGeneration`;
- read-only Browser/WOF data reads only; no game RAM writes, gameplay input injection, Worker replacement or Blob rewrite;
- request-selectable supported read profile/ranges, Hz, chunk duration, upload interval and destination;
- local small chunks, periodic upload, immediate partial flush on room/source end, flush on clean agent stop;
- exact sha256 and upload/session manifests;
- idempotent upload retry and no silent cross-room/cross-request mixing;
- current status file and fixed owner handoff text:
  - `AI联通：读取 collector/status/current.json`
  - `AI分析：读取 <exact manifest path>`
- deterministic tests using fake Git/fake Fleet/fake adapter data; do not start real Browser/WOF during implementation.

Reuse patterns, not unsafe coupling, from:

- `ouyong520/wof-winkawaks-bridge/bridge/collector_service.py`
- `ouyong520/wof-winkawaks-bridge/bridge/collector_queue_runner.py`
- `parallel/BROWSER_FLEET/**`
- `parallel/PYLAUNCH/wof_launcher/browser.py`
- `parallel/PYLAUNCH/wof_launcher/cdp.py`
- `parallel/PYLAUNCH/wof_launcher/probe.py`

Keep the local shell generic. Browser-specific behavior belongs in the adapter. Future WinKawaks/FBNeo adapters should be able to plug into the same shell without changing its owner workflow.

Stop only at:

`COMPLETE — UNIVERSAL COLLECTOR AGENT V1 — GENERIC GIT/LOCAL SHELL + BROWSER MULTI-ROOM ADAPTER READY FOR BOUNDED LOCAL QA`

or a precise BLOCKED result.
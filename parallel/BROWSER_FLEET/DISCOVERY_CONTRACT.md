# Browser Fleet Discovery Contract v1

Producer: `parallel/BROWSER_FLEET/fleet_manager.py`

Consumer helper: `parallel/PYLAUNCH/wof_launcher/fleet.py`

Default manifest:

`%LOCALAPPDATA%\WOF Future Danger\Fleet\instances.json`

Version remains:

`wof-browser-fleet-v1`

The manifest is advisory discovery data. A consumer must independently re-probe the listed localhost CDP endpoint before attaching. Stale/down entries are never authority for live browser, Worker, WASM or identity state.

## Per-instance contract

```json
{
  "id": 1,
  "host": "127.0.0.1",
  "port": 9323,
  "endpoint": "http://127.0.0.1:9323",
  "profileDir": "...\\Fleet_01",
  "pid": 12345,
  "managerRunId": "abc123",
  "status": {
    "browser": "OK",
    "page": "OK",
    "pageCount": 1,
    "worker": "OK",
    "workerCount": 1,
    "workerDiscovery": "page-autoattach-module",
    "relatedTopologyCount": 1,
    "workerIndicatorOnly": true,
    "world921031Identity": "NOT_CHECKED"
  }
}
```

The extra discovery-v2 keys are advisory. Consumers that only understand the original `browser/page/worker` keys remain compatible.

## Fleet discovery-v2 producer behavior

Fleet status is recomputed independently for every instance from that instance's own `127.0.0.1:<port>` CDP endpoint.

Worker/page indication no longer depends on only `type=worker + TargetInfo.url contains gstyphoon`:
- WOF page candidates are probed independently;
- page-related targets are observed with flattened `Target.setAutoAttach`;
- related iframe -> worker topology is followed recursively within a small bounded depth;
- worker-like related/direct targets may be accepted by a read-only Emscripten module/heap-shape probe even when the target URL changes;
- the historical direct `gstyphoon*.js` Worker shape remains a backward-compatible hint;
- reload/recreated Workers are rediscovered from fresh state; old Worker state is not retained as success.

A Fleet Worker `OK` is deliberately only a **cheap discovery indicator**. Fleet does not run the authoritative World 921031 full CPU-logical SHA-256 identity proof. PYLAUNCH remains the authority for Worker/WASM/heap/World 921031 acceptance.

## Isolation and stale-state rules

1. Each instance is pinned to its own localhost port/profile.
2. The browser-level CDP websocket advertised by `/json/version` must resolve to the same assigned Fleet port; a websocket pointing at another Fleet port is rejected.
3. No instance may silently fall across to another port when its own endpoint is missing or broken.
4. A missing/stale endpoint clears that instance's page/Worker indicator and does not affect other instances.
5. A discovery error in one instance is contained to that instance; status refresh continues for the remaining rooms.
6. Reload/recreated Worker state is rediscovered on later refreshes.
7. Consumers must still independently re-probe `host:port` and must not trust Fleet's advisory status alone.

## Safety declaration

```json
{
  "readOnly": true,
  "ramWrites": 0,
  "inputInjection": false,
  "windowWorkerReplacement": false,
  "workerStatusAuthority": "cheap-indicator-only",
  "world921031IdentityAuthoritative": false
}
```

Discovery is limited to CDP target/session attachment, auto-attach, Runtime enable/evaluate of read-only expressions, and target enumeration. It does not replace `window.Worker`, write game RAM, inject gameplay input, or change Alpha behavior.

## Consumer rules

1. never trust status alone; re-probe `host:port`;
2. do not attach one room's Worker/session state to another instance id;
3. a missing/down endpoint invalidates only that instance;
4. reload/recreated Worker state must be re-discovered by the consumer;
5. no consumer may add RAM writes or gameplay input through this contract;
6. a consumer pinned to one Fleet endpoint must not silently fall across to a different Fleet port when that endpoint is unavailable.

PYLAUNCH:
- `launcher.py --fleet-auto` selects a live, independently re-probed instance;
- `launcher.py --fleet-instance N` selects one numbered live instance;
- both modes are attach-only and do not start/replace the Fleet browser;
- normal PYLAUNCH page/Worker/WASM/heap/exact World 921031 validation remains authoritative.

WOF-052L:
- the supervisor reads the manifest and creates independent recorder handling per listed localhost endpoint;
- each child is pinned to its assigned endpoint;
- one endpoint disconnect/restart affects only that child/session;
- absent/empty Fleet manifest may fall back to the original supported recorder path.

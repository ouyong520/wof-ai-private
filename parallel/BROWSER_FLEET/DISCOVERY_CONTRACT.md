# Browser Fleet Discovery Contract v1

Producer: `parallel/BROWSER_FLEET/fleet_manager.py`

Consumer helper: `parallel/PYLAUNCH/wof_launcher/fleet.py`

Default manifest:

`%LOCALAPPDATA%\WOF Future Danger\Fleet\instances.json`

Version:

`wof-browser-fleet-v1`

A consumer must treat the manifest as advisory discovery data. Before attaching, it must independently probe the listed localhost CDP endpoint. Stale entries are ignored.

Required per-instance keys:

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
    "worker": "OK"
  }
}
```

Top-level safety declaration:

```json
{
  "readOnly": true,
  "ramWrites": 0,
  "inputInjection": false,
  "windowWorkerReplacement": false
}
```

Consumer rules:
1. never trust status alone; re-probe `host:port`;
2. do not attach one room's Worker/session state to another instance id;
3. a missing/down endpoint invalidates only that instance;
4. reload/recreated Worker state must be re-discovered by the consumer;
5. no consumer may add RAM writes or gameplay input through this contract.

PYLAUNCH:
- `launcher.py --fleet-auto` selects the first live instance;
- `launcher.py --fleet-instance N` selects one numbered live instance;
- both modes are attach-only and do not start/replace the fleet browser.

WOF-052L:
- import `discover_fleet_instances(..., live_only=True)`;
- iterate every returned endpoint independently;
- keep per-room/Worker capture lifecycle isolated.

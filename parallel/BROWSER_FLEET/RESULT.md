# WOF Browser Fleet Manager — Discovery V2 Result

Updated: 2026-09-01

Verdict: **BROWSER FLEET DISCOVERY V2 READY — repository regression PASS; one bounded real Windows proof remains.**

This lane modifies only `parallel/BROWSER_FLEET/**`. It does not modify PYLAUNCH, WOF-052L Recorder, `product/alpha/**`, game logic, RAM or gameplay input.

## What changed

The old Fleet status path used `/json/list` and counted a Worker only when the target was `worker/shared_worker` and its URL contained `gstyphoon`. That correlated with the same surface assumption that failed in the real Windows PYLAUNCH proof.

Fleet now has `fleet_discovery_v2.py` and `fleet_manager.py` uses it independently for every instance.

### Page / Worker discovery

Per assigned Fleet endpoint:
- `Target.getTargets` gives a fresh snapshot;
- page candidates are probed independently;
- the page is attached read-only and `Target.setAutoAttach(... flatten=true)` observes related targets;
- related `iframe -> worker` topology is followed recursively within a small bounded depth;
- worker-like related/direct targets receive a light read-only Emscripten module/heap-shape probe;
- a changed/non-gstyphoon Worker URL may therefore still produce the Fleet Worker indicator when the related runtime surface is valid;
- historical direct `gstyphoon*.js` Workers remain backward compatible;
- reload/recreated Worker state is rediscovered on the next refresh instead of inheriting stale success.

Fleet deliberately does **not** run the full World 921031 SHA-256 identity proof. Manifest/UI explicitly mark the Worker row as `cheap-indicator-only`; PYLAUNCH remains authoritative for Worker/WASM/heap/exact World 921031 acceptance.

### Multi-instance isolation

Every numbered instance retains its own:
- Chrome/Edge profile directory;
- localhost CDP port;
- browser process;
- window rectangle;
- manifest row.

Status refresh probes only `127.0.0.1:<that instance port>`.

A browser websocket returned by `/json/version` must resolve back to the same assigned port. A websocket pointing at a different Fleet port is rejected rather than associated with the wrong room.

A stale/missing endpoint clears only that instance's current page/Worker indicator. A discovery exception in one room is caught per instance and does not stop refresh of other rooms.

## Owner UX

Primary Windows path remains:

`parallel/BROWSER_FLEET/RUN_WOF_FLEET.cmd`

Owner-visible status remains Simplified Chinese. New error/status wording explains:
- endpoint unavailable;
- cross-room port mismatch safely rejected;
- Worker discovery temporarily unavailable;
- Fleet Worker state is only a quick indicator and PYLAUNCH World 921031 proof remains authoritative.

No DevTools or Worker Console selection is required.

## Manifest / compatibility

Manifest version stays:

`wof-browser-fleet-v1`

Existing consumers remain compatible with the original keys. Additional advisory fields include:
- `workerDiscovery`;
- `relatedTopologyCount`;
- `workerIndicatorOnly: true`;
- `world921031Identity: "NOT_CHECKED"`;
- top-level `workerStatusAuthority: "cheap-indicator-only"`;
- top-level `world921031IdentityAuthoritative: false`.

Consumers still must independently re-probe their selected endpoint and must never trust Fleet status as authority.

## Repository regression

Browser Fleet discovery-v2 offline regression: **15/15 PASS**.

Required cases covered:
1. direct worker backward compatibility — PASS;
2. related-target-only — PASS;
3. URL mismatch but related runtime — PASS;
4. iframe -> worker — PASS;
5. reload/recreated worker — PASS;
6. 10 instance isolation — PASS;
7. stale/missing endpoint — PASS;
8. no cross-port association — PASS.

Additional regression coverage:
- one instance discovery failure does not block another — PASS;
- manifest explicitly marks Worker state non-authoritative — PASS;
- 10-window layout bounded/unique — PASS;
- fleet count guard — PASS;
- settings round-trip — PASS;
- isolated profile/port construction — PASS;
- read-only/no-write/no-input/no-Worker-replacement manifest invariants — PASS.

The tested implementation uses the same `fleet_manager.py` and `fleet_discovery_v2.py` blobs now merged to `main`.

## Safety review

Preserved:
- `readOnly=true`;
- `ramWrites=0`;
- `inputInjection=false`;
- `windowWorkerReplacement=false`;
- no `product/alpha/**` changes;
- no PYLAUNCH changes in this lane;
- no WOF-052L changes in this lane;
- no Worker replacement/wrap;
- no game RAM write;
- no keyboard/mouse/controller gameplay injection;
- no game-speed control;
- no attack automation.

Discovery uses only CDP enumeration/attachment/auto-attach and read-only Runtime evaluation.

## Remaining real Windows proof — minimal and bounded

Only live Windows Chrome/Edge behavior cannot be proved by repository regression.

1. Double-click `parallel/BROWSER_FLEET/RUN_WOF_FLEET.cmd`.
2. Enter `10`.
3. Enter WOF normally in at least two rooms.
4. Press `S`; confirm those rooms can reach `浏览器：已连接 / WOF 页面：已找到 / Worker：已找到` without DevTools/manual JS.
5. Use `R` on one room and confirm the other room remains unaffected.
6. Press `A` to close the managed Fleet.

That is the only remaining bounded human proof. A failure there should produce a concrete per-room defect; it does not reopen the old broad `worker + gstyphoon URL` assumption.

## Stop condition

**BROWSER FLEET DISCOVERY V2 READY.**

Repository-side implementation, isolation guards, Chinese owner UX, contract, and required regression vectors are complete. Do not expand this lane before the bounded Windows proof unless that proof exposes a concrete defect.

# WOF Alpha Acceptance V2 — Integration Driver / Page Collector Contract

Status: **PREPARED — IMPLEMENT AFTER SAFE TRANSPORT OFFLINE PASS**

This file freezes the acceptance handoff so the future Safe Transport Integration stage does not need to redesign Browser acceptance.

## 1. Ownership

`parallel/ALPHAACCEPT/**` owns:

- the support-only page collector;
- acceptance fixtures;
- final result schema/validation;
- owner workflow.

The future integration stage owns the concrete CDP/PYLAUNCH control operations that already belong to its transport contract.

Acceptance must not duplicate Worker/WASM/identity discovery or RAM offsets in this lane.

## 2. Page collector surface

When `wof_alpha_acceptance.user.js` is present, it exposes:

```text
window.__WOF_ALPHA_ACCEPTANCE_V2_COLLECTOR
```

Required methods:

```text
status()
begin({ ownerConfirmedPlayable: true })
mark(name, detail?)
snapshot()
postNegative(kind)
finalize(driverEvidence)
reset()
```

The integrated driver may call only these fixed methods through its existing narrow CDP evaluation path. No arbitrary user-entered JavaScript is allowed.

### `status()`

Returns readiness without changing product state:

- helper version;
- page config;
- transport status if exposed;
- current pair;
- HUD status;
- observed current-pair state/diag counts;
- gameplay liveness counters.

### `begin(...)`

Starts one bounded collection epoch.

It does not bind transport, attach Worker, write RAM, inject input, or navigate.

`ownerConfirmedPlayable` must be true only because the owner clicked the Chinese start control after already entering a normally playable room.

### `mark(name, detail?)`

Driver records phase boundaries such as:

```text
preflight
pair-ready
stale-probe-start
stale-probe-end
diag-stop
rebind-start
rebind-ready
negative-probes
final
```

### `postNegative(kind)`

Posts a support-only synthetic `state` or `diag` to the product BroadcastChannel using a deliberately old generation or wrong nonce.

Allowed `kind`:

```text
old-generation-state
old-generation-diag
wrong-nonce-state
wrong-nonce-diag
```

It must never include gameplay input, Worker construction, heap writes or new attack rules.

### `finalize(driverEvidence)`

Combines collector observations with driver evidence and emits one compact JSON matching `RESULT_SCHEMA.md`.

The collector must refuse PASS when mandatory driver evidence is missing.

## 3. Driver evidence shape

The future integration driver supplies one object:

```json
{
  "integrationGate": {
    "status": "PASS",
    "productRegression": "PASS",
    "transportIntegrationTests": "PASS",
    "pylaunchTests": "PASS",
    "rc5NoWorkerReplacementRegression": "PASS",
    "rc4DiagSessionStaleRegression": "PASS",
    "exactStaleBoundary1500_1501": "PASS"
  },
  "launcher": {
    "browser": true,
    "wofPage": true,
    "worker": true,
    "wasmHeap": true,
    "world921031": true,
    "launcherIdentityGate": true,
    "roomRemainedPlayable": true
  },
  "safety": {
    "readOnly": true,
    "ramWrites": 0,
    "inputInjection": false,
    "windowWorkerReplacement": false
  },
  "actions": {
    "staleProbe": "PASS|OFFLINE_GATE_ONLY|FAIL|INCOMPLETE",
    "currentDiagStop": "PASS|FAIL|INCOMPLETE",
    "rebind": "PASS|FAIL|INCOMPLETE"
  },
  "firstCurrentPairState": {
    "hudAuthorityOnlyAfterState": true
  },
  "stale1500": {
    "browserObservedSilentAfter1500": true
  },
  "rebind": {
    "freshStateObserved": true,
    "oldAuthorityInherited": false
  }
}
```

`stale1500.browserObservedSilentAfter1500` may be `null` only when `actions.staleProbe` is `OFFLINE_GATE_ONLY`; the exact 1500/1501 offline gate must still be `PASS`.

No driver field may claim a game RAM write or injected input was used to create evidence.

## 4. Production surfaces observed by collector

The collector expects the integration to preserve the contract-defined page config:

```text
window.__WOF_ALPHA_CONFIG
```

and to expose the recommended page transport status surface:

```text
window.__WOF_ALPHA_TRANSPORT_V1.status()
```

The minimum transport status consumed by acceptance is:

```json
{
  "transportVersion": "wof-alpha-safe-transport-v1",
  "session": "<page session>",
  "pairGeneration": 1,
  "pairNonce": "<32 lowercase hex>"
}
```

Additional fields are allowed, especially detector-local identity status.

If the integration chooses an equivalent fixed status method name, it must add a compatibility alias for this acceptance surface rather than require owner workflow redesign.

## 5. Current-pair classification

A product message is current-pair only when all are exact:

- `schema === "wof-alpha-v2"`;
- `transportVersion === "wof-alpha-safe-transport-v1"`;
- `session === pageSession`;
- `pairGeneration === currentPairGeneration`;
- `pairNonce === currentPairNonce`.

A `state` also requires a valid increasing `seq` for that generation.

Foreign/old/wrong-nonce messages are logged as rejected evidence and must not be counted as current-pair state or diag.

## 6. First-state authority evidence

The integration driver must independently prove that the page/HUD does not gain current warning authority before the first valid current-pair `state` and pass:

```json
{"firstCurrentPairState":{"hudAuthorityOnlyAfterState":true}}
```

The collector supplies the observed first accepted state and sequence; the driver supplies the before/after authority observation because the integration harness controls the bind/install boundary.

## 7. Stale probe contract

Exact timing semantics are verified offline. Real Browser probing must not invent a new threshold.

Preferred integrated driver operation:

1. mark `stale-probe-start`;
2. suppress ordinary detector publication without emitting a current `diag`;
3. keep game Worker/gameplay running;
4. allow receiver-local stale timeout to expire;
5. mark `stale-probe-end`;
6. restore current-pair publication.

If the transport cannot expose this support-only operation without weakening production safety, use `OFFLINE_GATE_ONLY` in the real Browser result and retain exact offline PASS as mandatory.

## 8. Diagnostic stop / rebind contract

The driver uses only the approved Alpha agent control plane:

- stop/disable the **Alpha detector agent only**;
- never terminate/recreate the native game Worker;
- never navigate the page;
- never inject gameplay input.

The current diagnostic must carry current pair metadata.

Rebind must create:

- strictly greater `pairGeneration`;
- fresh `pairNonce`;
- a fresh accepted current-pair state;
- no stale sequence/warning authority inheritance.

The driver records the last two facts explicitly as:

```json
{"rebind":{"freshStateObserved":true,"oldAuthorityInherited":false}}
```

## 9. Owner interaction

The final owner interaction must remain:

1. open the integrated Chinese acceptance entry;
2. enter WOF room normally;
3. click once to confirm “当前房间可以正常操作，开始验收”;
4. tool performs the bounded sequence automatically;
5. return one JSON.

No DevTools / Worker Console / pasted JS.

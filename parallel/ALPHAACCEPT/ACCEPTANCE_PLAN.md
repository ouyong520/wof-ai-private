# WOF Alpha — Transport-Aware Bounded Real-Browser Acceptance V2 Plan

## 1. Authorization gate

Do not run the final Browser acceptance until **both** are true:

1. fresh real Windows PYLAUNCH proof has simultaneously proven Browser / WOF page / native Worker / WASM heap / exact World 921031 / READ ONLY while the room remains playable;
2. Safe Transport Integration reports:
   `INTEGRATION IMPLEMENTED — READY FOR BOUNDED REAL BROWSER ACCEPTANCE`
   with product regression, transport integration tests and PYLAUNCH tests all PASS.

Browser acceptance never waives an offline integration failure.

## 2. Fixed constants

```text
application schema:  wof-alpha-v2
release:             wof-alpha-rc3
transportVersion:    wof-alpha-safe-transport-v1
supported build:     wof / Warriors of Fate (World 921031)
golden SHA-256:      5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62
identity signature:  wof-world-921031-maincpu-sha256-v1:5c369ce2de4f53d8
ordinary stale:      1500 ms
```

Only these production `ruleId` values are allowed:

```text
T18_5440_CYCLE_BODY7512_TM4_LEVEL_90
T18_5424_CYCLE_BODY7520_TM4_LEVEL_90
```

## 3. Single bounded acceptance run

The integrated acceptance driver and the page collector use the fixed handoff in `ACCEPTANCE_DRIVER_CONTRACT.md`.

### A1 — launcher/runtime preflight

Required PASS evidence:

- Browser connected;
- exact WOF page resolved;
- exact native `gstyphoon*.js` Worker resolved;
- WASM/module/shared heap resolved;
- exact World 921031 Gate A accepted;
- `readOnly=true`;
- `ramWrites=0`;
- `inputInjection=false`;
- no Worker replacement/wrap/Blob/URL rewrite;
- room is already entered and owner confirms it is normally playable when starting the run.

Failure of an exact association or identity gate is FAIL/CANNOT_START, never a manual Worker Console fallback.

### A2 — exact current pair binding

The page collector reads the authoritative page config and transport status.

Required current-pair tuple:

```json
{
  "transportVersion": "wof-alpha-safe-transport-v1",
  "session": "<32 lowercase hex>",
  "pairGeneration": 1,
  "pairNonce": "<32 lowercase hex>"
}
```

PASS requires:

- page config session/channel are well formed;
- transport status session equals page session;
- generation is a positive integer;
- nonce is 32 lowercase hex;
- only current-pair messages can become acceptance-authoritative.

### A3 — detector-local identity and first current-pair state

PASS requires:

- detector-local Gate B identity accepted for the current Worker/runtime epoch;
- identity signature equals the World 921031 expected signature;
- the first authoritative `state` matches schema/session/transportVersion/generation/nonce;
- sequence is valid/current;
- HUD does not gain warning authority before this first valid state;
- after the first valid state the HUD is paired to that same current pair.

A launcher Gate A PASS never substitutes for Gate B.

### A4 — fresh no-warning state

PASS requires at least one valid current-pair `state` with `warnings: []`.

This proves the normal no-warning path is fresh and harmless.

### A5 — ordinary stale behavior

The exact boundary is an offline integration gate and must already be PASS:

- fresh through exactly 1500 ms;
- silent at 1501 ms without newer accepted state.

The bounded Browser run additionally pauses ordinary publication without forging a current `diag` when the integrated acceptance driver supports the contract-defined stale probe, then records:

- last accepted current-pair state time;
- receiver/HUD remains governed by receiver-local freshness;
- no warning authority survives after the >1500 ms boundary;
- gameplay render/liveness continues.

The Browser measurement is tolerant to scheduler jitter; it cannot redefine the exact 1500/1501 contract. If the live stale probe cannot be exposed safely, Browser result records `OFFLINE_GATE_ONLY` and requires the offline exact boundary gate PASS.

### A6 — current-pair diagnostic immediate clear

The driver triggers the fixed support-only transport diagnostic/stop path defined by the integration harness, never a game-RAM or input failure.

PASS requires:

- diagnostic is current session/generation/nonce;
- collector observes it as current-pair;
- prior warning authority becomes zero/invalid in the same task boundary or immediately observable next task;
- it does **not** wait for the 1500 ms stale timeout;
- room/game render remains alive.

If no warning was active immediately before the diagnostic, the run still requires the product HUD to remain cleared and records the warning-clear subcheck as `NO_ACTIVE_WARNING`; exact warning->diag clearing remains backed by offline integration regression.

### A7 — reconnect/rebind fresh pair

After the forced stop/diagnostic the driver reconnects/rebinds.

PASS requires:

- same page session is retained unless the page itself reloaded;
- `pairGeneration` strictly increases;
- `pairNonce` changes;
- a fresh detector-local identity acceptance occurs for a new Worker/runtime epoch when required;
- first new authoritative state belongs only to the fresh pair;
- no old warning state or sequence authority transfers.

### A8 — old generation / wrong nonce rejection

The page collector may post support-only synthetic messages into the existing Alpha BroadcastChannel. These messages never touch game RAM or input.

Negative vectors:

1. old generation + old nonce `state`;
2. old generation + old nonce `diag`;
3. current generation + wrong nonce `state`;
4. current generation + wrong nonce `diag`.

PASS requires none can create or clear current warning authority or replace the current pair. The collector also records that these messages are rejected by its own current-pair classifier.

If a visible warning is not active at the time of a clear-negative vector, the browser subcheck may be `NO_ACTIVE_WARNING`; exact receiver rejection remains mandatory in offline integration tests.

### A9 — warning sanity

Every naturally observed warning must:

- use one of the two allowed T18 rule IDs;
- be `publication="hold-only-current-level"`;
- be `evidence="fresh-current-sample"`;
- use current valid P1/P2/P3 target/target7E values;
- use current LEFT/CENTER/RIGHT source/threat side;
- contain no age/watch/history carry-over fields.

If no approved T18 condition occurs naturally, result is `NOT_EXERCISED`. Do not create new attack research merely to manufacture one.

### A10 — gameplay fail-open / room remains playable

The owner starts acceptance only after entering the room and confirming the room is normally controllable.

During stop/stale/rebind, the tool automatically records non-invasive liveness evidence such as page `requestAnimationFrame` and game draw counters when available.

PASS requires:

- no navigation/room-entry control issued by acceptance;
- no gameplay input injected;
- render/liveness continues through transport disruption;
- owner start confirmation states the room was playable;
- no Alpha/Launcher failure stops the game page.

### A11 — final safety invariants

Final JSON must contain:

```json
{
  "readOnly": true,
  "ramWrites": 0,
  "inputInjection": false
}
```

Any other value is FAIL.

## 4. Final result

Allowed top-level results:

- `PASS — REAL BROWSER ACCEPTANCE V2`
- `FAIL — REAL BROWSER ACCEPTANCE V2`
- `INCOMPLETE — REAL BROWSER ACCEPTANCE V2`
- `BLOCKED — TRANSPORT INTEGRATION NOT READY`

PASS requires every mandatory infrastructure/safety/current-pair/rebind gate to pass. Optional natural T18 exercise may be `NOT_EXERCISED`.

A Browser PASS is evidence for PM. It is **not** an Alpha release declaration.

## 5. Deliberate exclusions

Do not ask the owner to:

- open DevTools;
- select a Worker Console;
- paste JavaScript;
- inspect RAM;
- provoke quarantined F1-F4 or unrelated T23/T24/WOF-052/Beta behavior;
- compare WinKawaks timing numerically;
- retry a real FAIL until it happens to pass.

Do not modify `product/alpha/**` in this prep lane.

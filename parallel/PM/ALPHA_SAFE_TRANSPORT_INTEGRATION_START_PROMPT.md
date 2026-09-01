# WOF Alpha Safe Transport Integration — Fresh Start Prompt

You own the fresh implementation stage that follows the Python Launcher Windows/Browser proof.

Repository:
- `ouyong520/wof-ai-private`

## Prerequisite gate — check before changing code

First re-read the latest Python Launcher proof result and PM state.

You may begin implementation only if the real Windows/Browser proof has explicitly passed all of these simultaneously:

```text
Browser: OK
WOF page: OK
Worker: OK
WASM / heap: OK
World 921031: OK
READ ONLY / RAM writes: 0
room remains normally playable
```

If that proof is still pending or failed, **do not implement transport yet**. Stop with the precise remaining proof blocker.

## Read first

Mandatory:

- `parallel/PM/ALPHA_SAFE_TRANSPORT_INTEGRATION_CONTRACT.md`
- `parallel/PM/ACTIVE_PRIORITIES.md`
- `parallel/PM/RELEASE_READINESS.md`
- `parallel/PM/PYTHON_LAUNCHER_WINDOWS_PROOF_START_PROMPT.md`
- latest `parallel/PYLAUNCH/**` proof/result/architecture and implementation
- `parallel/ALPHAQA_RC5/result.json`
- `product/alpha/ALPHA_RC5_REPORT.md`
- `product/alpha/wof_alpha_bootstrap.user.js`
- `product/alpha/wof_alpha_core.js`
- `product/alpha/wof_alpha_loader.js`
- `product/alpha/wof_alpha_hud.js`
- `product/alpha/wof_alpha_hud_model.js`
- `product/alpha/rules_manifest.json`
- `product/alpha/regression.mjs`
- `product/alpha/regression_result.json`
- prior RC4 independent QA evidence as needed

## Current authoritative product state

Do not reopen these without new evidence:

- fresh RC5 independent QA: `PASS — RC5 ROOM-ENTRY REPAIR QA`;
- native game Worker startup path must remain untouched;
- no `window.Worker` replacement/wrapping;
- no Blob/Data/ObjectURL Worker;
- no game Worker URL/options rewrite;
- gameplay must remain fail-open if Alpha cannot attach;
- warning authority must remain fail-closed without a valid detector transport;
- exact World 921031 full 1 MiB CPU-logical SHA-256 remains authoritative;
- exactly two T18 current-level production rules remain active;
- F1-F4 remain quarantined;
- same-type slot reuse carries no history;
- target/side are current-sample values and UNKNOWN remains silent;
- current accepted diag immediately invalidates prior warning authority;
- ordinary no-diag stale boundary remains exactly 1500 ms;
- multi-warning HUD, legacy HUD cleanup and WebGL restoration remain gates;
- read-only, `ramWrites=0`, no gameplay input injection remain absolute requirements.

## Architecture is already decided

Do **not** research a new transport architecture unless real proof contradicts the contract.

Required v1 path:

```text
Python Launcher / localhost CDP
  -> discover + uniquely associate the already-native gstyphoon Worker
  -> exact Worker/WASM/heap + World 921031 pre-injection proof
  -> bind the exact RC5 page session with pairGeneration + pairNonce
  -> evaluate one fixed source-pinned read-only Alpha detector agent in that existing Worker
  -> detector samples WASM heap and runs canonical Alpha core inside the native Worker
  -> session/generation/nonce-bound BroadcastChannel state/diag
  -> RC5 bootstrap
  -> Alpha HUD
```

Python is the **control plane**. The native Worker -> page BroadcastChannel is the **high-frequency data plane**.

Do not build a normal 50-100 Hz Worker -> CDP -> Python -> page snapshot relay.

## Implementation goals

Implement only the minimum required by `ALPHA_SAFE_TRANSPORT_INTEGRATION_CONTRACT.md`.

### Product side

Under `product/alpha/**`, implement the minimum necessary to:

1. expose a page-side safe transport bind/status/reset surface;
2. make the page own a monotonic pair generation;
3. bind a fresh launcher-provided 128-bit pair nonce;
4. immediately revoke old warning authority on rebind;
5. preserve RC5 behavior: bind alone does not fetch/load HUD;
6. package/refactor a fixed Worker detector agent around the canonical Alpha core;
7. preserve detector-local exact World 921031 identity verification;
8. emit current state/diag messages with session + generation + nonce + sequence metadata;
9. preserve current warning/HUD semantics and all RC4/RC5 regressions.

Do not add any new warning rule.

### Python Launcher side

Under `parallel/PYLAUNCH/**`, implement only the minimum control-plane support to:

1. read/validate the exact associated RC5 page session/channel;
2. create a fresh cryptographic pair nonce;
3. request the page-owned next pair generation;
4. independently verify exact World 921031 before detector installation;
5. evaluate only the fixed approved Worker agent source in the already-native Worker;
6. query only fixed WOF Alpha agent status/stop surfaces;
7. detect page reload, Worker replacement, runtime/heap generation change and reconnect;
8. ensure at most one current detector agent per resolved page/Worker pair;
9. expose compact transport status/diagnostics;
10. keep the CDP allowlist narrow and retain read-only/no-input enforcement.

Do not duplicate RAM offsets or warning predicates in Python.

## Worker snapshot contract

Use exactly the contract-defined current-sample schema:

```text
wof-alpha-snapshot-v1
```

Envelope fields:

- `snapshotSchema`
- `sampleSeq`
- `sampledAtMonoMs`
- `pairGeneration`
- `enemies`

Enemy rows contain only current values:

- `slot`
- `type`
- `target7E`
- `state99`
- `action2A`
- `b2B`
- `body`
- `attack`
- `frameEnd`
- `next`
- `value30`
- `timer34`
- `payload6C`
- `enemyX`
- `targetX`

Do not add inferred room identity, lifecycle identity, history, age, watch ID or previous/current transition state.

The snapshot is internal Worker detector input in v1; do not normally move it through Python/CDP.

## Identity handshake

Keep the dual gate:

### Gate A — Launcher

Before detector installation, the selected Worker must independently pass exact World 921031 identity including the full golden SHA-256.

### Gate B — detector-local

The installed detector must independently run the canonical Alpha identity validation once for that Worker/runtime epoch before any state can become warning-authoritative.

Launcher success never bypasses detector-local identity failure.

Hash once per Worker/runtime epoch, never per detector poll.

## Session / Worker / reload lifecycle

Use the contract exactly:

- RC5 page session remains authoritative and unique per page load;
- fresh page reload => fresh session; old messages become foreign forever;
- each successful transport bind => page-owned next `pairGeneration` + fresh 128-bit `pairNonce`;
- old generation/nonce messages cannot create or clear current warnings;
- Worker target/context/module/heap/RAM-base generation discontinuity => new runtime epoch, full identity proof and fresh pair;
- never transfer identity cache, warning state or sequence numbers across runtime epochs;
- do not invent a semantic room ID from unproven RAM data.

## Warning / diagnostic contract

State must remain compatible with `wof-alpha-v2` and add the transport metadata defined in the contract.

Only these user-facing rules may appear:

```text
T18_5440_CYCLE_BODY7512_TM4_LEVEL_90
T18_5424_CYCLE_BODY7520_TM4_LEVEL_90
```

Current warning rows remain `hold-only-current-level` / `fresh-current-sample`.

Current valid `diag` clears old warning authority immediately.

Foreign session/schema, old pair generation or wrong pair nonce messages must be ignored and must not clear current warnings.

## HUD contract

The page/HUD must reject messages unless all required session + generation + nonce + schema + transport + identity checks pass.

Preserve:

- no HUD load before first valid current-pair state;
- first valid state may pair/load HUD;
- receiver-local freshness;
- fresh through exactly 1500 ms;
- silent at 1501 ms without a newer accepted state;
- immediate clear on current valid diag;
- immediate clear on rebind;
- multi-warning aggregation;
- HUD failure affects Alpha only, never the game Worker.

## Timing / backpressure

Detector target cadence remains approximately 10 ms inside the native Worker.

Required safety:

- maximum one detector tick in flight;
- no catch-up queue;
- delayed ticks skip missed history and sample current state;
- publish warning/target/side changes immediately;
- publish warning clear as immediate empty state;
- unchanged-state heartbeat at least every 250 ms;
- no application-managed unbounded message queue;
- Launcher control-plane lifecycle poll may remain around 1 second;
- do not repeat the full 1 MiB hash each poll.

## Disconnect / reconnect

A temporary Python/CDP disconnect may leave an already-healthy detector agent running. Gameplay remains independent.

If state publication stops, HUD authority expires naturally at 1500 ms.

On Launcher reconnect/restart:

- rediscover exact page/Worker pair;
- create a fresh pair binding;
- revoke old generation immediately;
- stop only the old WOF Alpha agent, never the game Worker;
- re-run required identity for the current runtime epoch;
- install exactly one current agent;
- never resume old authority from Python memory.

## Hard exclusions

Do not:

- modify WOF-052 or WOF-052L;
- do one-key moves;
- implement Assist Mode;
- implement gameplay input injection;
- write game RAM;
- add speed control;
- add Beta features;
- add new attack research/rules;
- reintroduce Worker wrapping/replacement/Blob URL rewriting;
- use native Chrome process memory as the primary transport;
- expand the CDP allowlist without a documented necessity + regression;
- accept arbitrary JavaScript from tray/UI/user input.

## Required tests

Implement and pass **all mock integration/regression vectors enumerated in `ALPHA_SAFE_TRANSPORT_INTEGRATION_CONTRACT.md`**. Do not reduce that matrix to a smaller happy-path suite.

At minimum the final result must explicitly report:

```text
product regression: PASS
transport integration tests: PASS
PYLAUNCH tests: PASS
RC5 no-Worker-replacement regression: PASS
RC4 diag/session/stale regression: PASS
World 921031 launcher gate: PASS
World 921031 detector-local gate: PASS
readOnly: true
ramWrites: 0
inputInjection: false
```

## Real Browser boundary after offline PASS

Prepare one bounded real Browser acceptance that verifies the integrated path without reopening attack research:

- launcher Browser/page/Worker/WASM/World status all OK;
- room remains playable;
- exact page session is paired to the native Worker;
- detector-local identity accepted;
- HUD receives fresh current-pair state;
- forced transport stop/diag clears warnings without affecting gameplay;
- reconnect/rebind returns to a fresh pair with no stale-warning inheritance;
- exercise an already-approved T18 warning only if the existing bounded fixture makes it practical; do not create new attack-research work merely to manufacture one.

Do not announce Alpha release from this integration stage. A PM release decision still follows bounded Browser acceptance.

## Stop condition

Stop with one of:

1. **INTEGRATION IMPLEMENTED — READY FOR BOUNDED REAL BROWSER ACCEPTANCE**, with all offline/mock gates passing and a concise real-Browser handoff; or
2. one precise P0/P1 integration blocker with exact evidence and the smallest next action.

Do not stop to redesign transport if the contract is implementable as written.

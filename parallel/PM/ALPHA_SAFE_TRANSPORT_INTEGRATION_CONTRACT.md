# WOF Alpha Safe Transport Integration Contract

Updated: 2026-09-01  
Status: **IMPLEMENTATION-READY DESIGN / WAITING FOR PYLAUNCH REAL WINDOWS PROOF**  
Scope: future safe transport integration only. This document does not itself authorize Alpha release.

## 1. Authority and current state

This contract is the implementation authority for the next fresh integration stage once the Python Launcher Windows/Browser proof passes.

Current facts that must not be reopened without new evidence:

- RC5 fresh independent QA verdict is `PASS — RC5 ROOM-ENTRY REPAIR QA`.
- The native game Worker must remain untouched during page startup; RC5 must never replace/wrap `window.Worker`, create a Blob Worker, or rewrite the game Worker URL/options.
- Python Launcher foundation already discovers an existing `gstyphoon*.js` target through localhost CDP, finds the Emscripten/WASM module + heap, and verifies exact `WOF / World 921031` identity read-only.
- Alpha detector/HUD behavior is intentionally warning-silent until a safe external live-Worker transport pairs with the RC5 page session.
- Exact authoritative program identity remains the 1 MiB CPU-logical SHA-256:
  `5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62`.
- Exactly two current-level T18 rules remain production-active:
  - `T18_5440_CYCLE_BODY7512_TM4_LEVEL_90`
  - `T18_5424_CYCLE_BODY7520_TM4_LEVEL_90`
- F1-F4 remain quarantined.
- RC4 warning invalidation, 1500 ms ordinary staleness, same-type slot replacement safety, target/side/UNKNOWN safety, multi-warning HUD, legacy HUD teardown, read-only/no-input and WebGL restoration remain release gates.

## 2. Selected architecture

### 2.1 Required path

```text
Python Launcher
  -> localhost Chrome/Edge CDP
  -> already-native gstyphoon Worker target
  -> exact Worker/WASM/heap identity verification
  -> one fixed, source-pinned, read-only Alpha detector agent evaluated in that existing Worker
  -> detector reads native WASM heap in-place
  -> detector creates fresh current snapshots and runs canonical Alpha core in the same Worker context
  -> session-bound BroadcastChannel state/diag
  -> RC5 page bootstrap
  -> page Alpha HUD
```

### 2.2 Explicitly rejected path

Do **not** stream 10 ms snapshots from Worker -> CDP -> Python -> page as the normal transport. CDP is a lifecycle/control-plane transport, not the high-frequency data plane.

Reason:

- it creates avoidable 50-100 Hz CDP round trips;
- it introduces Python/JSON scheduling jitter into the detector timing path;
- it creates unnecessary backpressure/queue risk;
- the existing Alpha runtime already proves that heap sampling + detector execution can live safely inside the real Worker context;
- direct CDP evaluation into the already-existing Worker preserves the RC5 no-replacement invariant.

The high-frequency path therefore remains entirely inside the native Worker. Python only discovers, verifies, binds, installs, audits and repairs the observer runtime.

## 3. Non-negotiable safety invariants

The implementation MUST preserve all of the following:

1. `window.Worker` constructor identity is never assigned, wrapped, proxied or replaced.
2. No Blob/Data/ObjectURL Worker is created for the game.
3. No game Worker URL, options, credentials, name or module/classic semantics are rewritten.
4. The existing native `gstyphoon*.js` Worker is never terminated/recreated by Alpha/Launcher.
5. No game RAM write. `ramWrites` remains exactly `0`.
6. No `Input.*`, keyboard, mouse, controller, gameplay callback invocation, one-key move, autoplay or input injection.
7. No game-speed control.
8. No page navigation or room-entry control.
9. Failure to discover, attach, verify, bind, inject, poll, reconnect or render may disable Alpha only; it must not block or stop gameplay.
10. Warning authority is fail-closed: no exact supported identity + no current authoritative state = no warning.
11. Only source-controlled fixed CDP expressions may execute. No user-entered/arbitrary JavaScript bridge.
12. Observer-owned JS state is allowed only under dedicated `__WOF_ALPHA_*` namespaces plus observer timers/BroadcastChannel/WebGL HUD resources. “READ ONLY” means no game RAM/control mutation, not literally zero JavaScript allocations.

## 4. Protocol/version constants

Until a deliberate product version bump is approved, integration should preserve:

```text
application schema:  wof-alpha-v2
Alpha release:        wof-alpha-rc3
core version:         wof-alpha-core-rc3
HUD version lineage:  wof-alpha-hud-rc4
transport version:    wof-alpha-safe-transport-v1
snapshot schema:      wof-alpha-snapshot-v1
supported game:       wof
supported build:      Warriors of Fate (World 921031)
logical program bytes:1048576
expected SHA-256:     5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62
ordinary stale limit: 1500 ms
```

Transport metadata may be added to `wof-alpha-v2` messages, but existing required `schema/session/kind/warnings` semantics must remain compatible unless the fresh implementation stage intentionally bumps the application schema and updates every consumer/test together.

## 5. Control plane vs data plane

### Control plane — Python/CDP

Python owns only:

- browser endpoint discovery;
- page/Worker target association;
- fixed read-only page config probes;
- fixed Worker module/heap probes;
- exact World 921031 pre-injection identity proof;
- pair generation / nonce setup;
- fixed observer-agent install/status/stop calls;
- lifecycle polling and repair;
- tray/diagnostic status.

### Data plane — native Worker -> page

The injected detector agent owns:

- current heap reads;
- snapshot construction;
- Alpha core evaluation;
- warning state creation;
- heartbeat/state publication;
- runtime diagnostic publication.

Data plane uses the existing per-page session-bound `BroadcastChannel` and does not require Python to relay every frame.

## 6. Page session and pair binding

### 6.1 Page session

RC5 already creates a fresh cryptographically random 128-bit page session and channel:

```text
session = 32 lowercase hex chars
channel = WOF_ALPHA_<session>
```

The integration stage MUST treat that page session as authoritative. It must read it from the exact associated page target with a fixed page probe. It must never guess a session/channel or share one between tabs.

Required page config acceptance:

```json
{
  "release": "wof-alpha-rc3",
  "schema": "wof-alpha-v2",
  "session": "<32 lowercase hex>",
  "channel": "WOF_ALPHA_<same session>"
}
```

Malformed/missing config => no Worker injection and no HUD pairing.

### 6.2 Pair generation and pair nonce

To prevent stale same-session messages from an older agent after reconnect/reinjection, v1 adds a page-owned monotonic `pairGeneration` plus a fresh launcher-generated 128-bit `pairNonce`.

Recommended page-side bind API for the implementation stage:

```text
window.__WOF_ALPHA_TRANSPORT_V1.bind({
  transportVersion: "wof-alpha-safe-transport-v1",
  pairNonce: "<32 lowercase hex>"
})
```

The page owns `pairGeneration` so launcher process restart cannot reuse an old generation accidentally. A successful bind:

- increments generation;
- stores the active nonce in Alpha-owned state/closure;
- immediately revokes all previous warning authority;
- sets bootstrap transport state to a pairing/waiting state;
- does **not** fetch/load the HUD by itself;
- returns the page session/channel + new generation to the fixed CDP caller.

The Worker agent receives exactly that session/channel/generation/nonce tuple.

Messages from an older generation, wrong nonce, wrong session or wrong schema are ignored and must never clear or create current warning authority.

## 7. Page <-> Worker association rules

Never select “the first Worker”. A pair is eligible only when all required relations are unambiguous.

Worker requirements:

1. target type is exactly `worker`;
2. URL matches `gstyphoon*.js` using the current foundation predicate;
3. module probe finds a shared Emscripten `HEAPU8`/`HEAPU32` buffer;
4. exact World 921031 identity passes;
5. Worker is uniquely associated with the page session being bound.

Association preference:

1. exact Chromium `openerId` / target relation when present;
2. otherwise current safe page-surface probe only when it leaves one unique page/Worker pair;
3. if two supported WOF tabs/workers exist and exact per-tab association cannot be established, fail closed rather than cross-pairing.

Multi-tab support is allowed only when each page/Worker pair is independently and exactly resolved. Ambiguous multi-tab state => warnings silent for the ambiguous pair(s), gameplay unaffected.

## 8. World 921031 identity handshake

Identity is a **dual gate**.

### Gate A — Launcher pre-injection proof

Before binding/installing the detector agent, the launcher must independently verify on the selected native Worker:

- Emscripten module + heap present;
- valid RAM window;
- exactly one plausible 1 MiB program locator candidate;
- CPU-logical SHA-256 equals exactly the golden digest;
- `readOnly=true`, `ramWrites=0`, `inputInjection=false`.

A failed/pending/missing/malformed/ambiguous hash gate means no detector injection.

### Gate B — Detector-local proof

The detector agent itself must perform the canonical Alpha identity validation once for that Worker/runtime epoch before warning evaluation begins. The launcher result is not a substitute for the detector-side gate.

No `state` message is authoritative before detector-local identity acceptance.

The accepted runtime status should expose at least:

```json
{
  "identity": {
    "ok": true,
    "game": "wof",
    "description": "Warriors of Fate (World 921031)",
    "logicalBytes": 1048576,
    "sha256": "5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62",
    "signature": "wof-world-921031-maincpu-sha256-v1:5c369ce2de4f53d8"
  },
  "readOnly": true,
  "ramWrites": 0,
  "inputInjection": false
}
```

Identity scanning/hashing happens once per Worker/runtime epoch, never per detector sample.

## 9. Worker/runtime epoch

A Worker target ID alone is not sufficient forever. The detector agent must treat any of these as a runtime discontinuity requiring stop + fresh identity handshake:

- Worker target replacement;
- Worker execution context destroyed/recreated;
- canonical module object replaced;
- `HEAPU8/HEAPU32` no longer share the originally accepted buffer;
- heap backing buffer/view generation changes unexpectedly;
- RAM base changes;
- accepted identity status is lost;
- detector namespace reports terminal runtime error.

No identity cache or warning state may transfer from one runtime epoch to another.

## 10. Room lifecycle

v1 MUST NOT invent a semantic room ID from an unproven RAM field.

There is therefore no authoritative gameplay `roomId` in this contract.

Room-transition safety is achieved by stronger existing properties:

- active production rules are stateless current-level predicates;
- every detector tick rebuilds the current slot map from fresh RAM reads;
- first current nonmatch clears the warning immediately;
- an empty current snapshot publishes `warnings: []`;
- same-type same-slot replacement inherits no history;
- Worker/runtime discontinuity causes a new pair/runtime epoch;
- transport silence clears at the 1500 ms receiver stale boundary.

If a future proven room marker is introduced, that is a separate schema/version change. Transport v1 safety must not depend on guessing one.

## 11. Worker snapshot contract

Snapshots are **internal detector input** in v1; they do not normally cross CDP or BroadcastChannel.

Envelope:

```json
{
  "snapshotSchema": "wof-alpha-snapshot-v1",
  "sampleSeq": 1234,
  "sampledAtMonoMs": 123456.7,
  "pairGeneration": 3,
  "enemies": []
}
```

Each enemy row is the current canonical Alpha input:

```json
{
  "slot": 0,
  "type": 18,
  "target7E": 0,
  "state99": 2,
  "action2A": 2,
  "b2B": 4,
  "body": 7512,
  "attack": 0,
  "frameEnd": 572338,
  "next": 569984,
  "value30": 1572865,
  "timer34": 4,
  "payload6C": 0,
  "enemyX": 100,
  "targetX": 140
}
```

Field rules:

- `slot`: integer `0..19`;
- numeric RAM fields are unsigned integer values read from the current sample only;
- `enemyX`: finite integer;
- `targetX`: finite integer for target indices `0/4/8`, otherwise `null`;
- inactive/invalid enemy slots are omitted;
- no previous-state, age, watch id, room id, inferred lifecycle id or attack history is inserted by transport;
- at most 20 enemy rows.

The adapter passes `snapshot.enemies` and `snapshot.sampledAtMonoMs` directly to canonical `WOFAlphaCore.createEngine().step(...)`. Transport must not duplicate rule predicates.

## 12. Detector input contract

The detector consumes only the current snapshot above.

Required behavior:

- clear/rebuild current slot state every sample;
- exactly two current-level T18 production predicates remain active;
- F1-F4 never enter warning output;
- unsupported/UNKNOWN target is silent;
- target is reread every sample;
- source/threat side is recomputed from current positions;
- same-type slot reuse carries no prior warning state;
- detector reset immediately empties warning state.

Any fatal heap read/runtime exception stops detector publication and emits an authoritative diagnostic if the session channel is still available.

## 13. Warning/state output contract

A valid state message retains existing Alpha semantics and adds transport binding metadata:

```json
{
  "schema": "wof-alpha-v2",
  "kind": "state",
  "release": "wof-alpha-rc3",
  "coreVersion": "wof-alpha-core-rc3",
  "transportVersion": "wof-alpha-safe-transport-v1",
  "session": "<page session>",
  "pairGeneration": 3,
  "pairNonce": "<current pair nonce>",
  "seq": 42,
  "sentAt": 1788290000000,
  "identitySignature": "wof-world-921031-maincpu-sha256-v1:5c369ce2de4f53d8",
  "readOnly": true,
  "ramWrites": 0,
  "inputInjection": false,
  "warnings": []
}
```

`seq` is strictly increasing within one pair generation. Receivers drop duplicate/out-of-order `seq` values.

Every warning row must be freshly regenerated from the current sample and retain the current core output fields:

```text
ruleId
freezeStatus
releaseStatus
warningClass
attackSpecific
attack
target
target7E
sourceSide
threatSide
timingClass
validatedLeadLabel
publication = hold-only-current-level
evidence = fresh-current-sample
slot
type
```

Forbidden warning carry-over fields include `ageMs`, `watchId`, `atMs`, previous/current transition history, prior target provenance or room history.

The only allowed `ruleId` values are the two active T18 rules. Any unknown rule in a supposedly production state is a regression failure.

## 14. Diagnostic output contract

Authoritative runtime failure message:

```json
{
  "schema": "wof-alpha-v2",
  "kind": "diag",
  "release": "wof-alpha-rc3",
  "transportVersion": "wof-alpha-safe-transport-v1",
  "session": "<page session>",
  "pairGeneration": 3,
  "pairNonce": "<current pair nonce>",
  "sentAt": 1788290000000,
  "status": "DISABLED",
  "code": "runtime-exception",
  "reason": "short user-safe reason",
  "readOnly": true,
  "ramWrites": 0,
  "inputInjection": false
}
```

Current-generation accepted `diag` MUST revoke old warning authority immediately; do not wait for 1500 ms.

A diagnostic from:

- another session;
- another schema;
- older pair generation;
- wrong pair nonce;

must be ignored and must not clear current warnings.

A later valid current-generation `state` may become authoritative again, preserving the RC4 recovery contract. Terminal detector failures naturally stop the agent, so recovery normally occurs through a fresh pair generation.

## 15. HUD transport contract

The page/HUD consumer must validate, in order:

1. application schema;
2. page session;
3. transport version;
4. current pair generation;
5. current pair nonce;
6. message kind;
7. monotonic `seq` for state messages;
8. expected identity signature for accepted state.

### Pairing / loading

- RC5 bootstrap starts in `WAITING_EXTERNAL_TRANSPORT`.
- Pair bind alone must not load HUD.
- First valid current-pair authoritative `state` moves the page to paired state and may request HUD load.
- No valid state => HUD remains unloaded/silent, preserving RC5 gameplay-first behavior.

### Freshness

- Receiver freshness uses local receive time, not sender clock.
- ordinary state is fresh through exactly 1500 ms;
- at 1501 ms with no newer accepted message, warnings are silent;
- current accepted diag clears immediately regardless of age;
- rebinding to a new pair generation clears immediately before new state arrives.

### Multi-warning

HUD must retain all current warning rows and continue current grouping behavior. Transport must not collapse to one “most important” warning.

### HUD failure

HUD load/render/WebGL failure is an Alpha-only failure. It may update diagnostics/status but must not stop or restart the game Worker.

## 16. Sampling, heartbeat and backpressure

### Detector sampling

Target detector sampling cadence remains approximately 10 ms, matching the current Alpha Worker runtime intent.

Implementation should use a self-scheduling loop or explicit in-flight guard:

- maximum one detector tick in flight;
- no catch-up queue;
- if a tick is delayed, skip missed intervals rather than enqueue historical snapshots;
- current sample always wins.

### State publication

To reduce BroadcastChannel pressure without delaying warning changes:

- publish immediately whenever the canonical warning set/target/side changes;
- publish immediate empty state when a warning clears;
- while canonical state is unchanged, publish a heartbeat state at least every 250 ms;
- never buffer an unbounded sequence of states.

This preserves the 1500 ms HUD freshness contract while keeping high-frequency sampling local to the Worker.

### Launcher lifecycle poll

Launcher discovery/liveness control plane should remain around the current 1 second poll cadence. It must not re-run the 1 MiB hash on every poll.

## 17. Disconnect / reconnect semantics

### CDP disconnect while agent is healthy

A temporary Launcher/CDP disconnect does not automatically invalidate a healthy already-installed detector agent. If the agent continues producing valid current-pair state, warning authority may continue.

This is safe because warning authority comes from the detector-local identity gate + current state, not from an open Python socket.

If the agent also disappears/stops, the page clears naturally at 1500 ms.

### Launcher reconnect/restart

On reconnect:

1. rediscover exact page/Worker pair;
2. read current page session;
3. inspect only the dedicated WOF Alpha agent namespace;
4. create a fresh pair nonce and page-owned next generation;
5. immediately revoke old generation authority on the page;
6. stop only the previous WOF Alpha detector agent, never the game Worker;
7. re-run required identity handshake for the current runtime epoch;
8. install one agent;
9. accept new state only from the new binding.

Do not attempt to continue an old pair generation from Python process memory.

## 18. Reload / Worker replacement

### Page reload

A page reload creates a fresh RC5 session. Old session messages are permanently foreign and ignored. No old session/channel may be reused.

### Worker replacement

A new Worker target/runtime epoch requires:

- immediate old warning revocation when the launcher observes replacement and the page is still reachable;
- otherwise ordinary 1500 ms stale fallback;
- new exact identity proof;
- new page pair generation/nonce;
- fresh agent install;
- no identity cache, sample, warning or sequence reuse.

### Same Worker / WASM reinitialization

If the same target changes module/heap/RAM-base generation, treat it exactly like Worker replacement from an Alpha authority perspective.

## 19. Fail-open gameplay / fail-closed warning matrix

| Failure | Gameplay | Warning/HUD authority |
|---|---|---|
| no CDP endpoint | continue | silent / existing healthy agent only |
| no page | continue | no new pair |
| no Worker | continue | silent |
| multiple ambiguous Workers | continue | silent |
| malformed page session | continue | silent |
| module/heap not ready | continue | silent; retry discovery |
| World hash pending/error/mismatch | continue | silent; no detector start |
| page bind failure | continue | silent |
| agent injection failure | continue | current pair disabled/silent |
| detector runtime exception | continue | current diag clears immediately |
| BroadcastChannel unavailable | continue | silent |
| HUD load/render failure | continue | no usable HUD; game unaffected |
| launcher exits after healthy pair | continue | healthy agent may continue |
| Worker dies | continue/recover per game | stale/diag clears; re-pair only after proof |

No failure may fall back to Worker replacement, RAM writing or input injection.

## 20. CDP allowlist for the integration stage

The existing foundation methods remain sufficient for the preferred v1 path:

```text
Target.getTargets
Target.attachToTarget
Target.detachFromTarget
Runtime.enable
Runtime.evaluate
```

Do not broaden the allowlist merely for convenience.

If the implementation proves one additional CDP method is strictly necessary, it requires an explicit contract update + regression proving it cannot navigate, input-inject, mutate game memory or replace the Worker.

`Runtime.evaluate` changes from “probe-only” to two narrowly defined fixed observer actions:

1. fixed page Alpha transport bind/status/reset calls;
2. fixed Worker Alpha detector agent install/status/stop calls.

No arbitrary expression parameter may be accepted from tray/UI/user input.

## 21. Source provenance / pinning

Do not make the integrated runtime depend on “whatever is currently on GitHub main” at the instant of injection.

The integration implementation must consume a release-pinned canonical Alpha bundle/descriptor containing at least:

```text
release
application schema
transport version
expected core version
expected World SHA-256
canonical core source digest
canonical Worker agent source digest
canonical page bootstrap/HUD compatibility version
allowed active rule IDs
```

The launcher may carry or load these canonical product bytes, but must not independently reimplement warning predicates or RAM offsets in Python.

For development, local repository sources are acceptable when their digests are checked against the descriptor. Packaged Alpha should carry/pin the exact approved artifacts.

## 22. Recommended implementation boundaries for the next stage

Exact filenames may vary, but responsibilities should remain separated:

### `product/alpha/**`

May add/refactor only the minimum integration pieces required to:

- expose the page transport bind/status API;
- validate session + pair generation + pair nonce;
- package a Worker detector agent around the canonical core;
- preserve current warning/HUD semantics;
- add product regression for new transport metadata/lifecycle.

Do not add new rules/Beta features.

### `parallel/PYLAUNCH/**`

May add only the minimum lifecycle/control-plane code required to:

- bind page session;
- inject/status/stop the fixed Worker agent;
- perform reconnect/replacement repair;
- expose compact transport status/diagnostics;
- retain read-only/no-input enforcement.

Do not move detector predicates into Python.

### WOF-052 / WOF-052L

No modification and no dependency.

## 23. Required mock integration tests / regression vectors

The next implementation stage is not complete until automated tests cover at least all vectors below.

### A. Startup / Worker safety

1. RC5 bootstrap preserves exact original `window.Worker` identity.
2. zero Blob/ObjectURL Worker wrappers.
3. zero game Worker URL/options rewrite.
4. no HUD fetch before first valid current-pair state.
5. no transport => gameplay fail-open / warnings silent.

### B. Target selection

6. exact one `gstyphoon*.js` supported Worker succeeds.
7. zero candidate fails closed.
8. two supported ambiguous workers fail closed.
9. wrong target type/URL never injects.
10. two tabs with exact association remain session-isolated.
11. two tabs without exact association do not cross-pair.

### C. Identity

12. exact golden 1 MiB SHA accepts.
13. pending hash rejects.
14. missing hash rejects.
15. malformed hash rejects.
16. one-digit hash mutation rejects.
17. ambiguous ROM locator rejects.
18. launcher identity success + detector-local identity failure still produces zero state authority.
19. hash is not repeated per detector tick.

### D. Pair/session isolation

20. correct session/generation/nonce state accepts.
21. foreign session state ignored.
22. wrong schema state ignored.
23. older generation state ignored.
24. wrong nonce state ignored.
25. duplicate/out-of-order `seq` ignored.
26. page reload session invalidates all old messages.
27. launcher restart creates a fresh generation instead of resuming old authority.

### E. Warning safety

28. exactly two production T18 rule IDs.
29. all F1-F4 candidates remain silent.
30. first current nonmatch clears immediately.
31. neutral same-type slot replacement cannot inherit warning.
32. matching replacement is accepted only as fresh current evidence.
33. invalid target index is silent.
34. target and side change are reflected from the current sample.
35. two simultaneous warning slots remain two warnings.
36. BODY4728/A4704-specific excluded candidate remains silent.

### F. Diagnostics / stale behavior

37. current-pair diag immediately clears prior warning authority.
38. old-generation diag cannot clear new-generation warning.
39. foreign-session diag cannot clear current warning.
40. later valid current-pair state can recover after a nonterminal diag.
41. ordinary state is fresh at exactly 1500 ms.
42. ordinary state is silent at 1501 ms.
43. pair rebind clears immediately before new state.
44. Worker replacement clears old authority and requires new full identity proof.

### G. Timing / backpressure

45. one detector tick maximum in flight.
46. missed intervals are skipped; no catch-up queue.
47. warning change publishes immediately.
48. warning clear publishes immediate empty state.
49. unchanged state heartbeat is <=250 ms.
50. simulated slow page consumer does not create an application-managed unbounded queue.

### H. Failure injection

51. CDP disconnect leaves game playable.
52. page bind exception leaves game playable and warning-silent.
53. Worker agent eval exception leaves game playable and warning-silent.
54. BroadcastChannel constructor/post failure leaves game playable and warning-silent.
55. heap/module generation change stops old detector authority.
56. HUD initialization/render exception leaves game playable.
57. reconnect creates at most one current detector agent.

### I. Read-only / no-input

58. CDP allowlist rejects `Input.dispatchKeyEvent` and all `Input.*`.
59. no game `postMessage` command/control path is introduced.
60. no writes through HEAP typed arrays/DataView/game RAM helpers.
61. `ramWrites` remains exactly `0` in launcher, agent and state/diag status.
62. `inputInjection` remains exactly `false`.
63. no one-key move/autoplay/assist implementation.

### J. Existing RC4/RC5 regressions

64. legacy HUD teardown remains required.
65. WebGL snapshot/restore regression remains PASS.
66. RC5 independent no-Worker-replacement regression remains PASS.
67. existing RC4 adversarial diag/session/stale regression remains PASS.

## 24. Integration-stage acceptance gates

Offline/mock gate:

```text
product regression: PASS
transport integration tests: PASS
PYLAUNCH tests: PASS
window.Worker identity preserved: PASS
World 921031 dual identity gate: PASS
readOnly=true
ramWrites=0
inputInjection=false
```

Then one bounded real Browser acceptance must prove:

1. launcher reaches Browser/page/Worker/WASM/World 921031 OK;
2. game can still enter/play the room normally;
3. page session binds to the real native Worker;
4. detector-local identity becomes accepted;
5. HUD receives fresh state from the current pair;
6. no-warning state is fresh and harmless;
7. at least one already-approved T18 warning can be exercised if the existing bounded acceptance fixture permits it, without expanding attack research;
8. forced transport stop/diag clears warnings and does not affect gameplay;
9. reconnect/rebind returns to a fresh current pair without stale-warning inheritance.

Passing this integration stage does **not** by itself announce Alpha release. It only unblocks the final bounded Browser acceptance / PM release decision.

## 25. Definition of done for this prep contract

This design is complete when the Python Launcher Windows proof can hand the next fresh integration thread a verified live Worker/CDP capability and that thread can implement directly from this document without researching a new transport architecture.

The next thread should not reopen Blob Worker, `window.Worker` interception, Python high-frequency snapshot relaying, game RAM writes, input injection, WOF-052L or Beta features.

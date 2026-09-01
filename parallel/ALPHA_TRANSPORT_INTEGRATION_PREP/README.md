# WOF Alpha Safe Transport — Real Adapter Integration Prep V1

Status: **ALPHA TRANSPORT REAL ADAPTER PREP READY**

This directory is the repository-side preparation layer for wiring the frozen Alpha Safe Transport reference implementation into the real WOF stack. It deliberately does **not** modify or replace PYLAUNCH, WOF-052L Recorder, Live Proof, the Alpha product, or the reference implementation.

## What this package freezes

The prep layer translates current real-stack authority into the already-frozen Safe Transport interfaces rather than reimplementing discovery, identity, detector predicates, or warning semantics.

Consumed frozen semantics:

- application schema: `wof-alpha-v2`
- release: `wof-alpha-rc3`
- core: `wof-alpha-core-rc3`
- transport: `wof-alpha-safe-transport-v1`
- World 921031 SHA-256: `5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62`
- stale warning boundary: 1500 ms
- unchanged-state heartbeat maximum: 250 ms
- canonical production warning rules: the same two current-level T18 rules already pinned by Alpha core/reference acceptance
- safety: `readOnly=true`, `ramWrites=0`, `inputInjection=false`, no Worker replacement, no Blob rewrite

The upstream reference implementation remains the semantic authority and already reports **8/8 selftest + 67/67 acceptance PASS**. This prep package does not create a weaker acceptance catalog.

## Stable Discovery adapter boundary

Formal integration must consume the **final authoritative Discovery V2 result**, not private topology helpers.

Required input shape is equivalent to the current PYLAUNCH `TargetChoice` public result:

```text
choice.page.targetId                 non-empty page target id
choice.page.type                     "page"
choice.worker.targetId               non-empty target id
choice.worker.type                   worker | shared_worker | service_worker
choice.worker.url                    diagnostic hint only
choice.worker_probe.moduleOk         true
choice.worker_probe.heapOk           true
choice.identity.ok                   true
choice.identity.moduleOk             true
choice.identity.heapOk               true
choice.identity.candidateCount       1
choice.identity.sha256               exact World 921031 golden SHA-256
choice.identity.readOnly             true
choice.identity.ramWrites            0
choice.identity.inputInjection       false
choice.reason                        null
choice.diagnostics.path              diagnostic only
```

The page config must be the current Alpha page-owned config:

```json
{
  "release": "wof-alpha-rc3",
  "schema": "wof-alpha-v2",
  "session": "<32 lowercase hex>",
  "channel": "WOF_ALPHA_<same session>"
}
```

`contracts.mjs` intentionally overrides the older narrow reference resolver. Current Discovery V2 is authoritative about topology and may legitimately surface `worker`, `shared_worker`, or `service_worker`, including `blob:`, `data:`, hashed, or extensionless URLs. URL/type hints must not become a second admission rule. Ambiguity or non-authoritative `choice.reason` always fails closed for warnings.

## Lifecycle / runtime epoch contract

The stable lifecycle input is:

```text
connectionId   browser/CDP connection generation identity
pageTargetId   exact page target id
pageEpoch      non-negative page lifecycle generation
workerTargetId exact Worker target id
workerEpoch    non-negative Worker runtime generation
```

`runtimeEpoch = connectionId | pageTargetId | pageEpoch | workerTargetId | workerEpoch`.

Any change means the previous warning authority is dead. Required sequence:

1. reset page/HUD authority;
2. stop the old observer where possible;
3. reset canonical detector state;
4. discard cached identity/observer authority for the old runtime epoch;
5. rediscover and re-prove the exact pair;
6. perform a new page bind with a fresh 128-bit `pairNonce` and strictly larger page-owned `pairGeneration`.

Old session/generation/nonce/seq traffic stays rejected. Gameplay remains fail-open while warning authority fails closed.

## Native Worker runtime adapter contract

Prepared interface:

```text
launcherIdentityProbe(workerRef)
detectorLocalIdentityProbe(workerRef)
installObserver(workerRef, binding, detectorAdapter)
statusObserver(workerRef)
stopObserver(workerRef)
```

Rules:

- the exact Discovery identity is an admission prerequisite, and the native adapter then performs a fresh read-only launcher identity probe bound to that same `runtimeEpoch`;
- WASM module and heap must both be ready;
- candidate count must be exactly one and SHA-256 must match World 921031;
- detector-local identity proof is required after page bind and before observer authority;
- observer status must echo the same runtime epoch;
- observer install/status/stop must preserve `readOnly=true / ramWrites=0 / inputInjection=false`;
- no Worker construction/replacement, Blob rewrite, heap write, gameplay `postMessage` control, `Input.*`, keyboard/mouse/gamepad injection, or automatic gameplay action is authorized.

## Alpha detector adapter contract

The detector remains `parallel/ALPHA_TRANSPORT_IMPL/detector_adapter.mjs` over the release-pinned `product/alpha/wof_alpha_core.js` API:

```text
WOFAlphaCore.VERSION === wof-alpha-core-rc3
WOFAlphaCore.SCHEMA  === wof-alpha-v2
WOFAlphaCore.createEngine().step(...)
```

Transport adapters may validate envelopes and safety, but must not duplicate Alpha predicates. State/warning authority comes only from valid current canonical-core output. Current-generation `diag`, runtime disable/error, stale timeout, rebind, disconnect, or epoch change removes warning authority immediately according to the frozen reference semantics.

## Page / HUD adapter contract

Prepared interface:

```text
bind(pageRef, pairNonce) -> { session, pairGeneration, pairNonce }
status(pageRef)
reset(pageRef)
```

The page owns the monotonically increasing `pairGeneration`. A bind/reset immediately invalidates the old generation.

First-release HUD transport output stays exactly the frozen authority shape:

```text
schema
release
transportVersion
session
pairGeneration
attachState
hudLoadAllowed
stale
warnings
diagnostic
```

A future player-head HUD anchor is a **presentation placement input only**. It may add something like `{anchorMode, x, y, confidence}` to the renderer path later, but it must not alter warning rows, identity, stale timing, pair authority, or detector semantics.

## Files

- `contracts.mjs` — concrete executable prep adapters and validators.
- `fixtures.json` — deterministic valid/invalid Discovery and lifecycle fixtures.
- `selftest.mjs` — isolated adapter/reference integration tests.
- `DRIFT_BASELINE.json` — exact Git blob baseline for every consumed current interface.
- `drift_check.mjs` — Git-blob-compatible current-tree drift verifier.
- `INTEGRATION_WIRING_PLAN.md` — bounded later wiring set and prerequisite gates.
- `RUN_PREP_SELFTEST.cmd` — Windows repository-side test entry.
- `RESULT.md` — durable stage result.

## Run

From this directory:

```text
node selftest.mjs
node drift_check.mjs
```

On Windows, double-click/run:

```text
RUN_PREP_SELFTEST.cmd
```

No Browser, WOF room, DevTools, Worker Console, pasted JavaScript, or Owner action is required.

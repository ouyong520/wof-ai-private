# Alpha Safe Transport — Formal Integration Wiring Plan

Stage source: `ALPHA_TRANSPORT_REAL_ADAPTER_PREP_V1`

This plan bounds a later formal integration stage. It is not permission to modify the listed files in the current prep stage.

## 1. Wiring principle

Do not redesign Safe Transport. The later stage should wire the existing real-stack authorities to the frozen reference interfaces:

```text
PYLAUNCH Discovery V2 final TargetChoice
        + lifecycle generation
        + exact World 921031 identity
                    |
                    v
Prepared Discovery / Native Worker adapters
                    |
                    v
canonical WOFAlphaCore detector
                    |
                    v
page-owned pairGeneration / pairNonce authority
                    |
                    v
fixed warning/HUD output
```

Warning authority fails closed. Gameplay always remains fail-open.

## 2. Exact later touch set

### PYLAUNCH side

Expected bounded touch set for formal integration:

1. `parallel/PYLAUNCH/wof_launcher/discovery_v2.py`
   - consume the existing public `discover(...) -> TargetChoice` result as authority;
   - do **not** fork/rewrite `_related_rows`, `_direct_page`, frame topology, URL compatibility, or ambiguity logic for Alpha;
   - expose only the normalized final pair fields required by `contracts.mjs`.

2. `parallel/PYLAUNCH/wof_launcher/probe.py`
   - reuse the existing exact World 921031 identity result and module/heap readiness;
   - do not add a second ROM predicate/hash implementation;
   - map accepted current identity into the frozen reference identity shape.

3. `parallel/PYLAUNCH/wof_launcher/monitor.py`
   - supply explicit connection/page/Worker lifecycle generations;
   - on disconnect/reconnect/reload/Worker replacement, invalidate the prior runtime epoch before any new warning authority can be established.

4. A new integration-owned bridge module, expected path:
   - `parallel/PYLAUNCH/wof_launcher/alpha_transport_adapter.py`
   - responsibility: stable JSON/operation bridge for Discovery authority, read-only Worker evaluation/observer lifecycle, status/stop, and page bind/reset orchestration;
   - it must not contain Alpha warning predicates.

`parallel/PYLAUNCH/wof_launcher/cdp.py` should remain the existing transport primitive unless a narrowly proven adapter hook is required. No formal integration change may authorize `Input.*`, arbitrary gameplay control, Worker creation/replacement, or heap writes.

### Alpha product side

Expected bounded touch set:

1. `product/alpha/wof_alpha_bootstrap.user.js`
   - extend the current RC5 session/channel bootstrap with page-owned monotonic `pairGeneration` and current `pairNonce` bind/reset authority;
   - reject old generation/nonce traffic before it can make the HUD authoritative;
   - preserve native game Worker construction untouched.

2. `product/alpha/wof_alpha_core.js`
   - **consume/pin only**; no rule or predicate rewrite is required for transport integration.

3. `product/alpha/wof_alpha_hud.js` and `product/alpha/wof_alpha_hud_model.js`
   - consume only the fixed current-pair HUD warning output;
   - presentation placement may later consume player-head anchor data independently;
   - transport integration must not change warning meaning, target/side calculation, or the two production rule semantics.

### Reference implementation

`parallel/ALPHA_TRANSPORT_IMPL/**` is the frozen semantic reference. Formal real integration should not turn it into a second mutable production implementation. Use it as the contract/acceptance oracle and keep the same 67-vector baseline.

## 3. Language boundary

PYLAUNCH is Python while the current reference implementation and Alpha core are JavaScript. The durable boundary is therefore the normalized contract data and operations in `contracts.mjs`, not Python private classes or JavaScript private helpers.

The later implementation may execute equivalent concrete adapter operations in Python/CDP plus page/Worker JavaScript, but every crossing must preserve the exact normalized fields, lifecycle epoch, pair envelope, identity authority, canonical detector ownership, and safety invariants in this prep package. Choosing a process/IPC packaging mechanism is implementation detail; changing semantics is not.

## 4. Required later control flow

Formal integration should be mechanically bounded to:

1. read current Alpha page config;
2. obtain exactly one authoritative final Discovery V2 `TargetChoice`;
3. normalize and validate exact page/Worker/lifecycle authority;
4. prove current World 921031 + WASM/heap + safety;
5. bind page with fresh nonce and larger page-owned generation;
6. run detector-local identity proof on the same Worker runtime epoch;
7. install at most one read-only observer for that epoch;
8. feed snapshots only to release-pinned canonical Alpha core;
9. publish frozen state/diag envelopes;
10. page/HUD accepts only current session/generation/nonce/seq;
11. any runtime epoch/reload/replacement/disconnect/error resets authority and requires a full rebind.

No speculative transport redesign is needed.

## 5. Gates that must close before formal wiring is treated as integration-ready

### Direct formal-wiring gates

1. **PYLAUNCH parentFrame authority — fresh independent QA still required.**
   - development completion is recorded by commits `57e77b65986bcc5f99f192159455e1dcbf2188fd` / `e9becb4797db7a816481fd436f4e547f5922566a`;
   - current core `discovery_v2.py` interface is compatible with this prep package;
   - formal integration must consume only the QA-approved final TargetChoice authority.

2. **Unified Live Proof freshness fix — fresh independent QA still required.**
   - current fix result is `UNIFIED LIVE PROOF FRESHNESS FIX READY — READY FOR FRESH INDEPENDENT QA`;
   - current implementation blobs are pinned in `DRIFT_BASELINE.json`;
   - do not use a repository fix-stage PASS as a substitute for independent QA or live PASS.

### Release / Owner-proof gate

3. **WOF-052L Recorder hardening fresh QA is currently BLOCKED.**
   - P0: a live/live shared-Worker topology transition can be missed until the delayed live audit, allowing evidence polling first;
   - P1: a recreated Worker with a reused target id can inherit stale cached World identity authority;
   - current Recorder implementation blobs remain unchanged at this prep drift check;
   - these do not prevent isolated adapter preparation, but they must be fixed/retested before unified Owner proof / long-capture readiness and must not be bypassed by Alpha integration.

### Non-blocking for first-release warning semantics

4. **Future player-head HUD anchor work is not a first-release transport blocker.**
   - fixed HUD warning output remains stable;
   - anchor geometry plugs into presentation later without changing detector/warning authority.

5. **Owner One-Click packaging refresh is downstream packaging work, not adapter architecture.**
   - refresh after core integration/QA blobs stabilize.

## 6. Formal integration acceptance checklist

A later integration stage is not complete until it proves, with the same semantic baseline:

- one exact current pair only;
- wrong World reject;
- missing WASM/heap reject;
- runtime replacement/reload reset;
- reconnect/rebind with new generation/nonce;
- cross-tab/session isolation;
- stale/diag/disable/error immediate warning invalidation;
- 1500/1501 ms stale boundary unchanged;
- <=250 ms heartbeat/backpressure semantics unchanged;
- canonical core only, no duplicated predicates;
- fixed HUD warning semantics unchanged;
- `readOnly=true`;
- `ramWrites=0`;
- `inputInjection=false`;
- no Worker replacement/Blob rewrite/game control;
- gameplay still works when transport is absent or fails;
- upstream 67/67 acceptance remains PASS;
- fresh independent integration QA passes before any bounded Owner Browser run.

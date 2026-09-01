# WOF Alpha Safe Transport Mock Harness

Status: **MOCK HARNESS READY — WAITING FOR REAL PYLAUNCH PROOF / TRANSPORT IMPLEMENTATION**

This directory is a preparation-only contract harness for the future Alpha safe-transport integration stage. It does **not** implement the product transport, inject a Worker agent, modify the game, or claim that live Browser integration exists.

## Scope and safety boundary

Allowed here:
- machine-readable protocol fixtures;
- machine-readable expected results;
- a reference contract state machine;
- regression vectors and result schema;
- offline failure/lifecycle/backpressure simulations.

Explicitly not done here:
- no `product/alpha/**` changes;
- no `parallel/PYLAUNCH/**` implementation changes;
- no game RAM writes;
- no input injection;
- no `window.Worker` replacement/wrapping;
- no Blob/Data/ObjectURL Worker rewrite;
- no new attack rule or warning predicate.

The warning fixtures contain only expected current warning rows. The harness does not copy or reimplement production warning predicates.

## Files

- `fixtures.json` — reusable sessions, pair nonces/generations, World 921031 identity probes, target topologies, warning rows, detector-frame outputs, RC5/RC4 baseline gates, and safety invariants.
- `vectors.json` — all 67 contract vectors, preserving contract numbering and sections A-J.
- `expected_results.json` — machine-readable expected PASS catalog for the same 67 vectors.
- `harness.mjs` — dependency-free Node.js reference contract model and runner.
- `result.schema.json` — machine-readable schema for `result.json`.
- `result.json` — latest offline reference-model execution result.
- `RUN_MOCK_HARNESS.cmd` — Windows one-click local runner.
- `RESULT.md` — repository-side handoff status.

## Run

From this directory:

```text
node harness.mjs
```

or on Windows, double-click:

```text
RUN_MOCK_HARNESS.cmd
```

A successful run must report:

```text
PASS
67 / 67
MOCK HARNESS READY — WAITING FOR REAL PYLAUNCH PROOF / TRANSPORT IMPLEMENTATION
```

## Reuse by the future integration stage

The integration stage should keep `fixtures.json`, `vectors.json`, `expected_results.json`, and `result.schema.json` stable as the acceptance oracle. Its production-side tests may either consume these directly or adapt the same scenarios to the real page bind surface, real fixed Worker agent, and PYLAUNCH control plane.

The future implementation must replace only the mocked behavior under test, not weaken expected outcomes. In particular it must preserve:
- current page session + monotonic pair generation + fresh nonce authority;
- foreign session / old generation / wrong nonce rejection;
- immediate current diag invalidation;
- 1500 ms fresh / 1501 ms silent receiver boundary;
- rebind and runtime-epoch revocation;
- exact World 921031 launcher gate plus detector-local gate;
- no HUD load before first valid current-pair state;
- multi-warning behavior and current-sample safety;
- one detector tick maximum in flight with no catch-up queue;
- reconnect to a fresh pair with at most one current Alpha agent;
- `readOnly=true`, `ramWrites=0`, `inputInjection=false`;
- no Worker replacement or Blob URL rewrite.

This harness is intentionally a specification/reference model. Passing it does not mean the live transport exists; it means the test framework and expected outcomes are ready for that implementation.

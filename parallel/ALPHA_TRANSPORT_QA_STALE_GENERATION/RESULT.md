# Alpha Safe Transport — Stale In-Flight Generation Fresh QA

## Verdict

**PASS — ALPHA TRANSPORT STALE IN-FLIGHT GENERATION FRESH QA — READY FOR FORMAL REAL-ADAPTER INTEGRATION**

The former P1 stale in-flight completion race is closed in the reference Safe Transport path tested here.

## Independent evidence

- QA claim start commit: `1be09d7f14e18d5aaa3721dff74df5df02a94063`
- Main tip observed immediately before final QA artifact write: `419e4d0839b09ca69e6ab305f8b829da3d122d7b`
- Targeted independently constructed adversarial suite: **12/12 PASS**
- Frozen Safe Transport catalog: **67/67 PASS**
- Frozen catalog and adapter were executed from byte-identical Git blobs; the QA runner checks the expected Git blob SHA before execution.
- Frozen adapter execution is performed in a temporary mirror so its own `result.json` write cannot modify `parallel/ALPHA_TRANSPORT_IMPL/**`.

## Required stale-generation findings

1. Generation-1 detector work can remain unresolved while generation 2 is installed and starts a new tick.
2. When the old completion arrives after rebind, `finishTick` returns no state publication.
3. The old completion does not clear or consume generation-2 `inFlightAuthority`.
4. Generation-2 completion then publishes normally under its own immutable session/generation/nonce authority.
5. Runtime-epoch reset revokes old authority.
6. Worker replacement revokes old authority.
7. Reinstall with a session change revokes old authority.
8. A legacy/untagged completion after unresolved revoke fails closed.
9. Current untagged compatibility remains valid when no unresolved revoke occurred.
10. One-tick-in-flight, skipped-tick, no-catch-up, and `queueDepth=0` invariants remain intact.
11. Stale boundary, warning clear/change immediacy, 250 ms heartbeat, and pair/session isolation remain intact.
12. Safety remains exact: `readOnly=true`, `ramWrites=0`, `inputInjection=false`, `workerReplacement=false`, `blobRewrite=false`.

## Delivery reassessment

- Former P1: **CLOSED**
- Reference-contract blocker remaining: **NONE**
- Formal real-adapter integration: **UNBLOCKED BY THE REFERENCE CONTRACT**
- Downstream real-adapter/integration work still requires its own integration QA; that is not a remaining blocker in this reference QA lane.

## Rerun

From repository root:

```bash
node parallel/ALPHA_TRANSPORT_QA_STALE_GENERATION/run_fresh_qa.mjs
```

Expected terminal summary:

```text
{"status":"PASS","targeted":"12/12","frozenCatalog":"67/67",...}
```

Machine-readable result: `parallel/ALPHA_TRANSPORT_QA_STALE_GENERATION/summary.json`

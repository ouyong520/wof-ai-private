# PYLAUNCH Startup Attestation Fresh QA Result

- Stage: `PYLAUNCH_STARTUP_ATTESTATION_QA_V1`
- Decision: **PASS**
- Release gate: **CLOSED**
- Owner action: **NO**
- Product-code writes by this QA lane: **NONE**

## Decision

`PASS — PYLAUNCH STARTUP ATTESTATION FRESH QA — RELEASE GATE CLOSED`

The startup Browser-level attestation fix is independently accepted for the tested current PYLAUNCH product blobs. Missing, empty, malformed, unsupported, stale, cross-host/cross-port, and non-browser authority inputs fail closed; valid Chrome/Chromium/Edge loopback Browser endpoints remain accepted.

## Current product authority validated

The final drift check reconfirmed the same current implementation blobs used by the QA harness:

- `parallel/PYLAUNCH/wof_launcher/browser.py` — `d6f7fa93aaf8d15da6ce77cfa35c4f72c4c3b332`
- `parallel/PYLAUNCH/wof_launcher/monitor.py` — `8e3c5c527fdd5a845bbfc135f55014de22078cf4`
- `parallel/PYLAUNCH/wof_launcher/discovery_v2.py` — `ec9d27bfe26557a11187a23853893b898a3366d1`
- `parallel/PYLAUNCH/tests/test_startup_attestation.py` — `c71070f6356b3c03bb89e4b7ad681efd3edc14af`
- `parallel/PYLAUNCH/tests/test_endpoint_hardening.py` — `242a76e8c9cddf28ba60bc3e5aee93060bd6d1ae`
- `parallel/PYLAUNCH/tests/test_identity_cache_generation.py` — `ed7a7af17060ae234687b6ef546ac50a0c0dcfef`
- prior adversarial startup reproducer — `04db971b44e72cf45e441913c49afaf077068415`

Main moved concurrently during QA, but the relevant PYLAUNCH blobs did not move, so unrelated repository drift did not invalidate the test decision.

## Fresh adversarial coverage

Independent QA added attacks beyond the fix-stage self-tests:

1. Missing `Browser`, `null`, empty, and whitespace-only Browser metadata -> rejected.
2. Malformed/unsupported product and version forms (`Firefox`, non-string, empty version, extra slash, embedded whitespace/control-style shapes) -> rejected.
3. Malformed `/json/version` JSON and non-object responses -> rejected with Chinese-first diagnostics.
4. Returned websocket on remote host or wrong configured port -> rejected.
5. Page/Worker masquerades, empty browser id, extra path, userinfo, query, and fragment -> rejected.
6. Valid Chrome, Chromium, and Edge Browser-level loopback endpoints -> accepted.
7. `reconnect()` discards old endpoint metadata, client authority, identity cache, worker id, and accepted identity before fresh attestation.
8. A stable websocket URL does not preserve stale Browser metadata: the monitor retains only metadata from the current fresh `/json/version` attestation.
9. A rejected fresh attestation immediately closes and clears previously accepted client/endpoint/identity authority and resets runtime status fail-closed.
10. Reuse of the same Worker `targetId` across runtime/CDP generations cannot reuse prior accepted identity authority.

## Regression execution

**35 / 35 passed, 0 failed.**

- Fresh independent startup-attestation QA: **11 / 11**.
- Current `test_startup_attestation.py` semantics: **15 / 15**.
- Current `test_endpoint_hardening.py` semantics: **5 / 5**.
- Current `test_identity_cache_generation.py` semantics: **2 / 2**.
- Prior independent startup-attestation adversarial reproducer: **2 / 2**.

The executable checks were run in an isolated harness reconstructed from the connector-fetched current source blobs because the execution container could not clone GitHub directly. The lane also commits a deterministic checkout runner that loads the real current repository modules/test files without copied product code:

```text
python parallel/PYLAUNCH_QA_STARTUP_ATTESTATION/runner.py
```

Runner: `parallel/PYLAUNCH_QA_STARTUP_ATTESTATION/runner.py`

Fixtures: `parallel/PYLAUNCH_QA_STARTUP_ATTESTATION/fixtures.json`

Machine result: `parallel/PYLAUNCH_QA_STARTUP_ATTESTATION/RESULT.json`

## Generation / stale-authority conclusion

The two independent generation protections are both present and green:

- `discover(..., identity_cache=...)` clears external identity authority at the start of each discovery generation, so a stable `targetId` is re-probed.
- `LauncherMonitor` invalidates client/endpoint/worker/identity caches on reconnect, replacement, connection error, and fresh startup-attestation rejection.

Therefore neither stale `/json/version` metadata nor a repeated target id can carry accepted authority into a later runtime generation.

## Safety boundary

QA wrote only under `parallel/PYLAUNCH_QA_STARTUP_ATTESTATION/**` plus its own stage claim. No `parallel/PYLAUNCH/**` product file was modified. Read-only discovery/identity protections were not relaxed.

## Final

**PASS — PYLAUNCH STARTUP ATTESTATION FRESH QA — RELEASE GATE CLOSED**

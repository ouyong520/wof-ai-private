# WOF Alpha RC3 — Independent QA

Updated: 2026-09-01
Role: fresh independent QA for `product/alpha/**`
Product mutation: **none**
Verdict: **BLOCKED — one concrete P1 release blocker found; do not enter owner Browser acceptance yet**

## Scope

This QA uses `parallel/PM/ALPHA_RC3_QA_START_PROMPT.md` as the acceptance contract. It does **not** reuse the obsolete RC2 expectation that all six frozen candidates must become user-visible warnings.

RC3 is expected to expose only the two stateless/current-sample T18 rules while quarantining F1–F4.

## Independent result

The following RC3 corrections survive independent source/adversarial review:

- World 921031 identity is gated by exact full 1 MiB CPU-logical SHA-256 equality to `5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62`; sparse locator/layout evidence is not an alternate acceptance path.
- same-slot + same-type continuity is no longer used by the production alert engine; there are no production watches/history states.
- only `T18_5440_CYCLE_BODY7512_TM4_LEVEL_90` and `T18_5424_CYCLE_BODY7520_TM4_LEVEL_90` are production rules.
- F1–F4 are quarantined and cannot be traversed by the production engine.
- multi-warning HUD modeling retains every simultaneous warning and groups by target/side.
- page/Worker transport is session-bound with a per-page random 128-bit session and unique channel.
- the normal-user userscript installs at `document-start`, patches the target Worker constructor before normal page load, and pairs page/Worker with the same session.
- the legacy canvas HUD has a real `dispose()` that removes its key listener, closes its BroadcastChannel, deletes its own GL resources, and deliberately leaves the persistent GL bridge available for safe takeover; RC3 refuses takeover when a legacy `WOFHUD` lacks `dispose()`.
- target is reread from `enemy+0x7E`; side is recomputed from current enemy/target X; invalid target/geometry is silent.
- detector access is read-only and no automatic gameplay input path was found; the HUD snapshots/restores the GL state it mutates.

## Release blocker

`ALPHAQA-RC3-001` (P1): after a previously valid warning state, a Worker runtime exception resets/stops the detector and posts a `diag`, but the page HUD does not invalidate `lastMsg` / `lastRx`. `drawHud()` gives a still-fresh prior warning priority over the diagnostic until `STALE_MS=1500` expires.

Deterministic sequence:

1. page receives a valid RC3 `state` containing a T18 warning;
2. Worker tick throws;
3. Worker sets `running=false`, resets the engine, and posts only `diag`;
4. HUD stores `lastDiag` but keeps the previous warning state timestamp;
5. for up to 1500 ms, HUD continues to render the obsolete warning instead of immediately entering disabled/silent state.

This violates the RC3 contract that runtime error/exception paths fail closed and that stale/error paths clear user warnings.

## Stop condition

Stop condition **B** from the RC3 QA prompt is reached: a concrete P1 blocker is proven and documented.

Do **not** ask the project owner for Browser acceptance yet. Product engineering should first make `diag` immediately invalidate warning state (or otherwise make disabled diagnostics take precedence over every prior warning) and add a regression for `warning state -> runtime diag -> immediate zero user warnings`.

See:

- `AUDIT_STATUS.md`
- `FINDINGS.md`
- `ACCEPTANCE_CHECKLIST.md`
- `independent_qa.mjs`
- `qa_result.json`

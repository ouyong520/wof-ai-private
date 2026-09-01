# WOF Future Danger — Alpha RC4 Report

Updated: 2026-09-01  
Status: **RC4 CANDIDATE — product regression PASS; ready for fresh independent RC4 QA**

## Scope

RC4 closes exactly one RC3 independent-QA blocker:

- `ALPHAQA-RC3-001` — a paired/current runtime `diag` could leave the previous warning authoritative for up to `STALE_MS = 1500` ms.

No attack research, WOF-052 work, Beta feature, rule promotion, identity relaxation, input behavior, or game-memory write behavior is part of RC4.

## Minimal product fix

Changed file: `product/alpha/wof_alpha_hud.js`.

The HUD still rejects messages unless both schema and per-page session match. After that pairing gate, an accepted `diag` now performs the fail-closed transition in the same handler turn:

```js
lastMsg=null;
lastRx=0;
lastDiag={at:Date.now(),reason:m.reason||m.status||'diagnostic'};
```

Consequences:

- prior warning authority is invalidated immediately;
- `WOFALPHAHUD.status().warningCount` becomes zero immediately after the accepted diagnostic path;
- `drawHud()` cannot enter its warning-freshness branch from the pre-diagnostic state;
- the diagnostic/disabled rendering path wins immediately instead of waiting for the 1500 ms ordinary stale timeout;
- foreign-session diagnostics remain ignored because the existing schema/session gate is still before the state mutation;
- a later fresh paired `state` follows the existing contract and becomes authoritative normally;
- ordinary no-message staleness remains exactly `STALE_MS = 1500` when no explicit diagnostic occurs.

HUD patch identity is now `wof-alpha-hud-rc4`. The detector/core/bootstrap/rule manifest remain on the already-QA-audited RC3 transport/rule contract intentionally; RC4 does not perform unrelated protocol or rule-version churn.

## Required RC4 regressions added

`product/alpha/regression.mjs` now deterministically covers:

1. valid warning -> accepted runtime disable/error `diag` -> warning count is zero immediately;
2. valid warning -> accepted `diag` -> diagnostic rendering wins immediately;
3. foreign-session `diag` is ignored and cannot clear the paired session;
4. later fresh paired `state` after a diagnostic behaves normally and does not resurrect stale authority;
5. ordinary state staleness still remains warning-fresh through 1500 ms and expires after that boundary when no explicit `diag` occurred.

Static guards also require the production HUD source to clear both `lastMsg` and `lastRx` in the accepted `diag` branch and require `STALE_MS=1500` to remain unchanged.

## Preserved RC3 contract

The full RC3 product regression remains in place and passed together with the new RC4 assertions. Preserved invariants include:

- exact `wof / World 921031` full 1 MiB CPU-logical SHA-256 gate;
- golden SHA-256 `5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62`;
- no sparse vector/dispatch fallback;
- exactly two active current-level T18 production rules;
- F1-F4 remain quarantined and cannot user-alert;
- BODY4728/A4704-specific remains excluded;
- no same-type slot/history inheritance;
- first current nonmatch clears T18 immediately;
- per-session/cross-tab isolation;
- simultaneous multi-warning HUD aggregation;
- legacy `WOFHUD.dispose()` cleanup;
- document-start normal-user bootstrap;
- live target reread / side recompute;
- UNKNOWN invalid target silence;
- read-only game RAM with `ramWrites=0`;
- no gameplay input injection/autoplay;
- no T23/T24/WOF-052/Beta promotion.

## Product regression result

Executed:

```text
cd product/alpha
node regression.mjs
```

Result: **PASS**

Recorded output: `product/alpha/regression_result.json` with artifact `wof-alpha-rc4`.

The execution snapshot was reconstructed byte-for-byte from current GitHub files and verified against Git blob SHA before running:

- `wof_alpha_core.js` — `267a44190744b6848b0685712c3d5572627d3a8a`
- `wof_alpha_hud_model.js` — `16641129ff651c2733aebc6fae09a280e4bac49b`
- `wof_alpha_loader.js` — `ef6c74fc6cba3c101654a851c411b2b2b005d447`
- `wof_alpha_bootstrap.user.js` — `80dfa948473b49c8e1f0695d131da40084d4f01a`
- `README.md` — `09d6913d7375cf9d45347020f269fe77ff636c11`
- `rules_manifest.json` — `7dc8f66e5e39c04b258c8f1a24751eaee6107818`
- `wof_alpha_hud.js` RC4 — `f93f90cc3cc898083d9613841927349159a0d4ae`
- `regression.mjs` RC4 — `5f6a56d9e3b07cec7b19f926a83c8d768cbddf75`

Regression output confirms:

- `tests = PASS`;
- `runtimeDiagImmediateWarningInvalidation = true`;
- `ordinaryStalenessUnchanged = true`;
- exact full-SHA identity protection remains true;
- history rules remain quarantined;
- current-level hold-only behavior remains true;
- same-type replacement inheritance remains blocked;
- session-bound transport remains preserved;
- `readOnly = true`;
- `inputInjection = false`.

## Handoff / stop condition

Stop condition A is satisfied for this product-fix stage:

- RC4 candidate exists;
- ALPHAQA-RC3-001 is concretely closed in product code;
- product regression passes with deterministic coverage for the blocker and preserved RC3 safeguards;
- candidate is ready for a **fresh independent RC4 QA** stage.

This thread does **not** declare Alpha released and does **not** run final Browser acceptance.

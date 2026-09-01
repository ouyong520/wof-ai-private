# WOF Future Danger — Alpha RC5 Real Browser Bootstrap Report

Updated: 2026-09-01  
Status: **RC5 CANDIDATE — full product regression PASS; only one minimal real-Browser room-entry retest remains**  
Rule/runtime core: `wof-alpha-rc3` + RC4 HUD safety patch  
Bootstrap: `wof-alpha-bootstrap-rc5`

## RC5 decision

Real Browser acceptance established a P0 product blocker:

- Browser Acceptance Helper disabled;
- normal Alpha userscript enabled;
- game could not enter a room;
- with both WOF userscripts disabled, the game could enter normally.

The failure therefore implicated the normal Alpha Browser bootstrap rather than the game alone or the Acceptance Helper alone.

RC5 fixes only that bootstrap boundary. It does not resume WOF-052, does not add Beta work, does not expand attack research, and does not promote additional warning rules.

## Root cause / compatibility diagnosis

The RC3/RC4 normal userscript replaced the target game Worker URL with a generated Blob Worker. The wrapper then attempted to run the original game script and inject Alpha inside the replacement Worker.

That design is unsafe for the base game because replacing the Worker target can change browser-visible Worker semantics before Alpha itself even runs successfully, including:

- `WorkerGlobalScope.location` / base URL;
- relative resource lookup;
- `importScripts()` behavior;
- classic-versus-module loading behavior;
- CSP handling for `blob:` URLs and injected source;
- module import base/origin behavior;
- exact propagation of Worker URL/options/credentials/name/type.

The existing `parallel/ALPHABOOT` audit had already identified Worker proxy/replacement/Blob wrapping as a production risk and recommended attaching to the actual live Worker instead of replacing it. The real room-entry A/B result is consistent with that previously identified failure class.

A synchronous `try/catch` fallback around `new Worker(blob, options)` would not close this P0: the replacement Worker can be constructed successfully and then fail asynchronously while loading the original game or its dependent assets. By then the page has already lost the native construction path. RC5 therefore removes replacement rather than attempting a narrower Blob-wrapper patch.

## RC5 bootstrap behavior

`product/alpha/wof_alpha_bootstrap.user.js` now:

1. still installs at `document-start`;
2. creates the existing secure 128-bit per-page session/channel config;
3. **never assigns to or wraps `window.Worker`**;
4. creates no Blob Worker / ObjectURL and does not rewrite any game Worker URL;
5. passively waits for a valid same-session detector `state` from a future/available non-replacing live-Worker transport;
6. does not fetch/evaluate the page HUD before such a detector state is observed;
7. treats secure-session or BroadcastChannel failure as Alpha-disabled while leaving the game Worker untouched;
8. treats later page-HUD attach failure as an Alpha error only, not a game-start exception.

The bootstrap exposes `gameWorkerUntouched=true`, `workerIntercepted=false`, and starts in `WAITING_EXTERNAL_TRANSPORT` when its passive listener is available.

### Intentional RC5 tradeoff

The repository currently does not contain a proven normal-userscript mechanism that can enter the already-native WorkerGlobalScope without replacing/proxying the Worker. Therefore RC5 does **not** pretend to preserve automatic detector attachment by recreating the unsafe wrapper under a different form.

If no compatible non-replacing live-Worker transport is present:

- base game: **must continue normally**;
- Alpha detector: not attached;
- warnings: **fail-closed / silent**;
- HUD: not loaded.

This is the required gameplay-first failure mode for RC5.

## Focused bootstrap/failure-injection regression

`product/alpha/regression.mjs` now includes executable VM tests for the RC5 userscript. They verify:

- evaluating the userscript preserves the exact original `window.Worker` constructor identity;
- bootstrap itself creates zero game Workers;
- no Blob/ObjectURL wrapper is created;
- no loader/HUD fetch occurs before paired detector state;
- original Worker URL is unchanged;
- original Worker `options` object (including module/name/credentials test values) is passed to the native constructor unchanged;
- BroadcastChannel construction failure does not throw out of bootstrap and leaves Worker untouched;
- secure random/session failure does not throw out of bootstrap and leaves Worker untouched.

## Full product regression

Executed after the final bootstrap surface-check fix:

```text
artifact: wof-alpha-rc5
tests: PASS
supportedIdentity: wof / World 921031
goldenSha256: 5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62
productionRules:
  - T18_5440_CYCLE_BODY7512_TM4_LEVEL_90
  - T18_5424_CYCLE_BODY7520_TM4_LEVEL_90
quarantinedRules:
  - T16_B4_DANGER_40
  - T20_5136_B0_TO_B255_1250
  - D867BA_3232_TM6_220
  - D8811E_3232_TM6_135
```

Recorded output: `product/alpha/regression_result.json`.

## RC4 safety contract preserved

The RC5 bootstrap change does not modify `wof_alpha_core.js`, `wof_alpha_loader.js`, `wof_alpha_hud.js`, or `wof_alpha_hud_model.js`. Full regression confirms the preserved gates:

- exact WOF / World 921031 full 1 MiB CPU-logical SHA-256 identity protection;
- golden digest `5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62`;
- only the two T18 hold-only current-level production rules;
- F1-F4 remain quarantined;
- same-type slot replacement cannot inherit warning history;
- session/cross-tab nonce contract remains enforced for paired transport;
- simultaneous warning aggregation remains multi-warning;
- legacy research HUD safe disposal remains required before Alpha HUD takeover;
- accepted runtime disable/error/diag immediately clears prior warning authority;
- foreign-session diag cannot clear the current session warning;
- a later valid state may become authoritative again;
- ordinary no-diag stale behavior remains exactly 1500 ms;
- target and threat side remain live;
- invalid/UNKNOWN target remains silent;
- game RAM remains read-only with `ramWrites=0`;
- no gameplay input injection;
- WebGL state snapshot/restore remains present.

## Files changed for RC5

Only `product/alpha/**` is intentionally changed:

- `wof_alpha_bootstrap.user.js` — removes Worker replacement and defers HUD until real detector pairing;
- `regression.mjs` — replaces obsolete “must intercept Worker” assertion with gameplay-first RC5 failure tests while retaining the complete prior product suite;
- `rules_manifest.json` — records the RC5 bootstrap/fail-open gameplay policy; rule inventory remains unchanged;
- `README.md` — documents the safe bootstrap contract and the one-question retest;
- `regression_result.json` — records the RC5 PASS result;
- `ALPHA_RC5_REPORT.md` — this report.

No attack/core/HUD implementation file is changed by RC5.

## Single remaining human Browser blocker check

Keep **Browser Acceptance Helper disabled**.

Enable only the current normal Alpha userscript, refresh the game page, and answer exactly one question:

> **Can the game enter a room normally?**

No Worker-console work, warning triggering, attack testing, ROM re-identification, multi-tab test, or Console JSON collection is required for this RC5 blocker retest.

### Stop condition

- If **YES**: the P0 “Alpha prevents room entry” blocker is closed; RC5 has satisfied its bootstrap repair objective. Alpha may remain warning-silent when no safe live-Worker transport is present, by design.
- If **NO**: the remaining blocker is a real-host effect not reproduced by the repository regression despite RC5 making no Worker/HUD modification before detector pairing. At that point the next evidence needed is only the exact real-Browser failure under this Worker-untouched userscript, not broader attack/research work.

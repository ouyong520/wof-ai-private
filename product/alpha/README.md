# WOF Future Danger — Alpha RC2

Status: **RC2 candidate — offline P0/P1 regression complete; fresh real-Browser QA still required.**

RC2 ships only the six frozen PM rules. It does not ship T18 BODY4728/A4/B2/TM1 as A4704-specific, any T23/T24 discovery rule, Safe Path, miners, or WinKawaks-local logic.

## Normal user install

Use the single userscript entry:

`product/alpha/wof_alpha_bootstrap.user.js`

Install it in a userscript manager, enable it for the Browser game page, then refresh the game page once. The script runs at `document-start`, creates a fresh per-page random session, intercepts the target `gstyphoon*.js` Worker as it is created, injects the read-only detector there, and loads the WebGL HUD in the page. No DevTools context switching is part of the supported Alpha path.

Expected page diagnostic:

`WOFALPHAHUD.status()`

Expected detector contract (available inside the instrumented Worker for engineering diagnostics): release `wof-alpha-rc2`, `readOnly=true`, `ramWrites=0`, `inputInjection=false`.

If the userscript was enabled only after the emulator Worker had already been created, refresh the page so the bootstrap can run before Worker creation.

## Fail-closed supported-runtime guard

Warnings are enabled only after both classes of evidence pass:

1. Browser/WASM runtime layout: shared `HEAPU8`/`HEAPU32`, valid CPS RAM window, and P1/P2/P3 `+0x7C` self indexes `0/4/8`.
2. Positive Browser ROM executable fingerprint, derived from the retained Browser ROM probe: reset vectors `SP=0x00FF62EE`, `PC=0x0000754A`, dispatch table offset `0x25DC`, and the five-entry type-dispatch sequence based on `0x06F4E4, 0x07494C, 0x071ADA, 0x077B8E, 0x07C6D2` (allowing only the small uniform live-ROM delta already handled by the Browser probe).

A layout-compatible runtime without the ROM fingerprint is unsupported and emits no warnings.

## RC2 safety changes

- Same-slot/same-type watch inheritance is conservative: an armed watch survives only while its exact frozen zero-attack precursor remains observable. Any descriptor drift invalidates the episode before a later ACTIVE edge can resolve it.
- Every active warning is preserved in HUD state. The HUD aggregates all current warnings by target and threat side rather than selecting only one warning.
- Warning transport is session-bound. Each page has a fresh random nonce and a unique BroadcastChannel; HUD messages must also carry the same nonce.
- Before Alpha takes the WebGL HUD bridge, an existing research `WOFHUD` must expose `dispose()` and is disposed. Alpha refuses takeover if a legacy HUD cannot be safely released.
- Game RAM remains read-only; there is no input injection.

## Frozen rules

1. `T16_B4_DANGER_40` — imminent danger only, not A6432-specific.
2. `T20_5136_B0_TO_B255_1250` — A5136.
3. `D867BA_3232_TM6_220` — A3232.
4. `D8811E_3232_TM6_135` — A3232.
5. `T18_5440_CYCLE_BODY7512_TM4_LEVEL_90` — A5440.
6. `T18_5424_CYCLE_BODY7520_TM4_LEVEL_90` — A5424.

Target is reread live from `enemy+0x7E`; threat side is recomputed from current enemy/target X. Invalid target selector, stale state, unsupported runtime, identity uncertainty, and runtime exceptions are silent with respect to danger warnings.

## Offline regression

Run:

```bash
cd product/alpha
node regression.mjs
```

RC2 regression covers the six frozen rules, the 143-signal WOF-051 canonical reconstruction, layout-lookalike identity rejection, ROM fingerprint mismatch rejection, same-type replacement invalidation, simultaneous warning aggregation, foreign-session transport rejection, research HUD teardown, read-only/no-input static checks, and the document-start user bootstrap contract.

## Fresh Browser QA still required

The remaining work is real Browser acceptance rather than more offline rule research:

- userscript/Worker interception on the actual host, including CSP and the real Worker constructor/options;
- positive ROM fingerprint passes on the declared World 921002 / `wofr1` Browser build;
- a deliberately unsupported/lookalike environment fails closed if one is available;
- two same-origin game tabs stay isolated;
- reload/restart creates clean pairing;
- legacy research HUD listeners/channel/resources are gone after takeover;
- real WebGL rendering, simultaneous-danger layout, retarget, stale cleanup, and frame-time overhead.

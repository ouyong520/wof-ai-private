# WOF Future Danger — Alpha RC1

Status: **Release Candidate; real Browser acceptance pending**  
Release: `wof-alpha-rc1`  
Rule manifest: `wof-alpha-rules-v1`

This directory is the bounded user Alpha implementation. It is intentionally separate from WOF-0xx research coordinators and all `parallel/**` discovery lanes.

## Included rules

Only the six PM freeze candidates are compiled into the release core:

- `T16_B4_DANGER_40` — danger-only, never labeled A6432-exclusive.
- `T20_5136_B0_TO_B255_1250` — A5136.
- `D867BA_3232_TM6_220` — A3232.
- `D8811E_3232_TM6_135` — A3232.
- `T18_5440_CYCLE_BODY7512_TM4_LEVEL_90` — A5440.
- `T18_5424_CYCLE_BODY7520_TM4_LEVEL_90` — A5424.

`T18 BODY4728/A4/B2/TM1`, T23 ordered candidates, T24 non-freeze variants and all discovery/local candidates are absent.

## Runtime boundaries

1. `wof_alpha_loader.js` — the single supported load path; same URL in top Window and live `gstyphoon.js` Worker.
2. `wof_alpha_core.js` — frozen rule engine + identity guard logic. No research mining.
3. `wof_alpha_hud.js` — direct WebGL HUD consumer. SAFE/UNKNOWN/stale are visually silent after short load confirmation.
4. `rules_manifest.json` — machine-readable freeze and release policy.
5. `regression.mjs` — release-artifact fixture/static regression.

## Supported identity / fail closed

Warnings are enabled only when all checks pass:

- a Browser WASM module exposes compatible `HEAPU8`/`HEAPU32` over the same buffer;
- CPS RAM pointer `HEAPU32[0x2e39e4>>2]` is nonzero and its 64 KiB window is in bounds;
- Browser player objects report self-index `0/4/8` at P1/P2/P3 `+0x7C`.

This is the supported Browser layout signature `wofr1-world-921002-browser-layout-v1`. It is a positive layout guard, not a ROM cryptographic hash. Any mismatch disables warnings and emits a diagnostic; offsets are never guessed.

## Target / retarget / side

The Worker rereads `enemy+0x7E` every 10 ms and resolves only `0/4/8` to P1/P2/P3. The rule engine does not freeze entry target. While a warning exists, the published target and left/right threat side are recomputed from the current target every poll. Unknown target values are silent.

## Read-only contract

The Alpha runtime only reads the WASM heap. It contains no game RAM assignment and no keyboard/gameplay input injection. Worker exceptions stop the Alpha timer, clear warnings and publish a disabled diagnostic; gameplay is not modified.

## Supported load path

Use the same loader expression in both contexts:

```js
fetch('https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/product/alpha/wof_alpha_loader.js?x='+Date.now()).then(r=>r.text()).then(eval)
```

For RC acceptance, load it once in the live `gstyphoon.js` Worker console and once in the top page console. The top copy installs only the HUD; the Worker copy installs only the read-only detector/publisher.

## Regression

Run locally from this directory with:

```text
node regression.mjs
```

The fixture suite checks all six release predicates, 143 WOF-051 production-subset signal/resolution fixtures, attack distributions, zero hard-miss equivalent in claimed fixtures, level-arm deduplication, BODY4728 exclusion, live retarget, UNKNOWN silence, stale cleanup, static no-HEAP-write/no-input-injection, and presence of WebGL state snapshot/restore.

Historical WOF-051 raw per-poll snapshots are not retained as a release replay corpus here; the 143-count regression is a canonical fixture reconstruction from the audited WOF-051 aggregate. The final real-Browser RC acceptance is therefore still required.

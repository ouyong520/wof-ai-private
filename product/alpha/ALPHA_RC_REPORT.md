# WOF Future Danger — Alpha RC1 Report

Updated: 2026-09-01
Status: **ALPHA RELEASE CANDIDATE — only real Browser owner acceptance remains**
Artifact: `product/alpha/**`
Release: `wof-alpha-rc1`
Manifest: `wof-alpha-rules-v1`

## Release scope

Alpha RC1 contains only the six PM freeze candidates:

1. `T16_B4_DANGER_40` — danger-only; never A6432-exclusive.
2. `T20_5136_B0_TO_B255_1250` — attack-specific A5136.
3. `D867BA_3232_TM6_220` — attack-specific A3232.
4. `D8811E_3232_TM6_135` — attack-specific A3232.
5. `T18_5440_CYCLE_BODY7512_TM4_LEVEL_90` — attack-specific A5440.
6. `T18_5424_CYCLE_BODY7520_TM4_LEVEL_90` — attack-specific A5424.

Explicitly absent: T18 BODY4728/A4/B2/TM1 -> A4704, all T23 ordered/discovery candidates, T24 non-freeze variants, provisional/one-off/retrospective/local candidates, research miners and Safe Path logic.

## A1 → A10 status

| Task | Status | Result |
|---|---|---|
| A1 reusable asset inventory | PASS | `A1_REUSE_MATRIX.md`; adapt proven WebGL HUD mechanism, reject research V4/HUD producer from release path. |
| A2 frozen manifest | PASS | `rules_manifest.json`; six exact freeze candidates, explicit exclusions and UNKNOWN policy. |
| A3 release/runtime separation | PASS | `wof_alpha_core.js`, `wof_alpha_loader.js`, `wof_alpha_hud.js`; no WOF-0xx coordinator/miner is executed. |
| A4 fail-closed identity guard | PASS in artifact regression; Browser acceptance pending | Module/heap/RAM/self-index positive checks; mismatch emits disabled diagnostic and no warning. |
| A5 live target/retarget | PASS in artifact regression; Browser acceptance pending | `enemy+0x7E` and target X reread every poll; retarget fixture P1 -> P3 changes warning target/side immediately; unknown selector is silent. |
| A6 HUD integration | PASS implementation; Browser visual acceptance pending | Direct WebGL HUD, stale/SAFE/UNKNOWN silent, concise danger/attack + target + threat side + validated lead class. |
| A7 release regression | PASS | Release core fixture regression: 143/143 production-subset signals resolved; zero hard-miss equivalent in claimed fixtures. |
| A8 read-only/interference audit | PASS static; Browser interference acceptance pending | No HEAP assignment, no keyboard/click injection, GL state snapshot/restore present, exceptions fail closed. |
| A9 minimal packaging | PASS | One dual-context loader URL; same expression is used in live Worker and top Window. |
| A10 RC report | PASS | This report. |

## Regression result

`regression_result.json` records `PASS` for the exact RC1 release core.

Canonical WOF-051 production-subset reconstruction:

| Rule | Signals | Resolved | Active attack distribution |
|---|---:|---:|---|
| T16 B4 danger | 98 | 98 | A6432=97, A4840=1 |
| T20 B0->B255 | 5 | 5 | A5136=5 |
| D867BA | 10 | 10 | A3232=10 |
| D8811E | 22 | 22 | A3232=22 |
| T18 BODY7512/TM4 | 4 | 4 | A5440=4 |
| T18 BODY7520/TM4 | 4 | 4 | A5424=4 |
| **Total** | **143** | **143** | — |

Additional release-artifact assertions passed:
- BODY4728 experimental candidate stays silent;
- T16 A4840 remains a valid danger-only resolution rather than false A6432 labeling;
- cycle-level T18 arming deduplicates held state within one zero->ACTIVE cycle;
- retarget uses the current target and recomputes side;
- invalid/unknown target selector emits no warning;
- stale warnings expire;
- no game HEAP write statement was found in release JS;
- no automatic keyboard/click input injection was found;
- HUD retains explicit GL state snapshot/restore and persistent reload-safe hook structure.

Important limitation: the repository does not retain the WOF-051 raw per-poll Browser stream as a release replay corpus. Therefore 143/143 is a canonical fixture reconstruction from the audited WOF-051 aggregate and exact predicates, not a claim that RC1 was replayed against raw WOF-051 frames. This is why real Browser acceptance remains mandatory.

## Supported runtime/build

Declared supported game/build: WOF / Warriors of Fate / 三国志II, World 921002 / `wofr1` Browser layout already proven by the project.

RC1 positive runtime guard signature: `wofr1-world-921002-browser-layout-v1`.

Required checks:
- compatible WASM `HEAPU8` and `HEAPU32` share one backing buffer;
- CPS RAM pointer `HEAPU32[0x2e39e4>>2]` is positive and its 64 KiB window is in heap bounds;
- P1/P2/P3 Browser object `+0x7C` self-index values are exactly `0/4/8`.

This is a conservative positive layout guard, not a cryptographic ROM hash. An unsupported/mismatched runtime fails closed.

## Runtime safety contract

- read-only game memory access;
- `ramWrites=0` by design;
- no automatic gameplay input;
- warnings disabled on identity failure or runtime exception;
- current target reread continuously while warning is alive;
- current threat side recomputed from live geometry;
- SAFE/UNKNOWN/stale are silent after short load confirmation;
- release HUD callback errors are isolated from the game draw call;
- reload disposes only Alpha-owned HUD resources while preserving the persistent safe WebGL bridge.

## Known Alpha limitations

- Coverage is intentionally narrow: only six frozen rules.
- No T23, BODY4728 A4704-specific prediction, T24 non-freeze rules, generic danger-map expansion or Safe Path.
- HUD currently displays the highest-priority warning only; multi-danger composition is a Beta concern.
- Lead text is the validated evidence band/class, not a causal countdown.
- Browser identity guard is layout-based rather than ROM-hash-based.
- Final runtime overhead, real retarget visual behavior, stale cleanup and reload safety still require one owner acceptance run in the actual Browser game.

## Single supported load path

Run this exact expression in the live `gstyphoon.js` Worker console and in the top page console:

```js
fetch('https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/product/alpha/wof_alpha_loader.js?x='+Date.now()).then(r=>r.text()).then(eval)
```

Worker expected state: `self.__WOF_ALPHA_RUNTIME.status()` shows `release=wof-alpha-rc1`, `running=true`, `readOnly=true`, `ramWrites=0`, `inputInjection=false`.

Top expected state: `WOFALPHAHUD.status()` shows `connected=true`, `drawHooked=true`, no persistent `lastError`.

## Release judgment

Engineering stop condition is reached. RC1 exists, production/experimental boundaries are enforced, offline release-artifact regression passes, and the remaining release-blocking work cannot be completed without the actual Browser game: a short real-Browser owner acceptance run.

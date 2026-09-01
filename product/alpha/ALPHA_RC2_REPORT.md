# WOF Future Danger — Alpha RC2 Report

Updated: 2026-09-01  
Status: **RC2 CANDIDATE — all offline Alpha QA P0/P1 blockers closed; only fresh real-Browser QA remains**  
Release: `wof-alpha-rc2`  
Manifest: `wof-alpha-rules-v2`

## RC2 judgment

RC1 was blocked by six Alpha QA findings. RC2 fixes all six without adding attack rules, widening predicates, weakening UNKNOWN silence, or introducing RAM writes/input injection.

Offline verification now passes both:

- `product/alpha/regression.mjs`: `PASS`, canonical WOF-051 frozen subset `143/143` signals resolved.
- `parallel/ALPHAQA/independent_qa.mjs` (`wof-alpha-independent-qa-v2`): `PASS`, zero P0/P1 blockers.

The remaining release gate is real Browser acceptance because CSP, actual Worker construction, actual ROM mapping, WebGL rendering, and two-tab runtime behavior cannot be proven by Node fixtures.

## P0/P1 closure

| Finding | Severity | RC2 fix | Offline result |
|---|---|---|---|
| ALPHAQA-001 layout-only identity | P0 | Requires positive Browser/WASM ROM executable fingerprint in addition to layout. Uses reset vectors plus the retained five-entry type-dispatch fingerprint from `wof_rom_focus_probe.js`; mismatches fail closed. | PASS |
| ALPHAQA-002 same-type same-slot replacement inheritance | P1 | Conservative episode policy: while a watch is armed, any zero-attack drift away from that rule's exact frozen base clears the watch and arm state before a later ACTIVE edge. | PASS |
| ALPHAQA-003 HUD drops warnings 1+ | P1 | New pure HUD model aggregates every warning by target/threat side; renderer prints every group. No first-warning special case. | PASS |
| ALPHAQA-004 manual Worker-console bootstrap | P1 | New `wof_alpha_bootstrap.user.js` runs at document-start, generates the session, intercepts `gstyphoon*.js` Worker creation, injects the detector, and loads the page HUD. Supported user path no longer requires DevTools context switching. | PASS |
| ALPHAQA-005 cross-tab BroadcastChannel contamination | P0 | Each page gets a random 128-bit session and unique channel; every message also carries the session nonce and HUD checks it. | PASS |
| ALPHAQA-006 legacy research HUD not disposed | P1 | Alpha HUD calls legacy `WOFHUD.dispose()` before taking the persistent GL bridge. If a legacy HUD exists without safe disposal, Alpha refuses takeover. | PASS |

## Runtime/build identity

RC2 no longer claims a build from RAM layout alone.

Positive identity requires:

1. compatible Browser/WASM heap and RAM window;
2. self-index values `0/4/8`;
3. Browser ROM reset vector `SP=0x00FF62EE`, `PC=0x0000754A`;
4. type-dispatch table at ROM offset `0x25DC` matching the five retained Browser entries:
   `0x06F4E4, 0x07494C, 0x071ADA, 0x077B8E, 0x07C6D2`,
   permitting only the bounded uniform live-ROM delta already present in the retained Browser ROM probe.

This evidence comes from the Browser/WASM ROM locator path, not WinKawaks addresses. A layout-compatible fixture without this ROM evidence now fails closed.

Real Browser QA must still confirm that the declared World 921002 / `wofr1` host produces this fingerprint in the actual current runtime.

## Lifecycle safety

There is no proven Browser spawn-id/episode-id field. RC2 therefore does not infer continuity merely from `slot + type`.

A watch is allowed to survive only while its exact frozen zero-attack precursor remains observable. If the descriptor changes while still at attack zero, RC2 invalidates the watch. This is intentionally conservative: it can reduce warning coverage, but it prevents a stale watch from being inherited by a same-type replacement.

## Multi-threat HUD

`wof_alpha_hud_model.js` is a deterministic pure model. It groups simultaneous warnings by `P1/P2/P3` and threat side (`左侧/右侧/近身`) and keeps attack labels/counts inside each group. The WebGL HUD renders all groups rather than selecting one array element.

## User bootstrap and session isolation

Supported Alpha path:

1. install `product/alpha/wof_alpha_bootstrap.user.js` in a userscript manager;
2. enable it for the Browser game page;
3. refresh the page once.

At document-start it creates a fresh random session. The page HUD and intercepted target Worker receive the same config. Cross-tab messages use different channels and different nonces.

The loader now refuses an unpaired/manual invocation with no RC2 session config.

## Preserved freeze boundary

Exactly six frozen rules remain:

1. `T16_B4_DANGER_40` — danger-only.
2. `T20_5136_B0_TO_B255_1250` — A5136.
3. `D867BA_3232_TM6_220` — A3232.
4. `D8811E_3232_TM6_135` — A3232.
5. `T18_5440_CYCLE_BODY7512_TM4_LEVEL_90` — A5440.
6. `T18_5424_CYCLE_BODY7520_TM4_LEVEL_90` — A5424.

Still excluded: T18 BODY4728/A4/B2/TM1 as A4704-specific, T23, T24, discovery/provisional/local rules, research miners, and Safe Path.

Target is reread live from `enemy+0x7E`; threat side is recomputed from current geometry. Invalid target, unsupported identity, stale data, and runtime errors produce no danger warning.

## Browser-only acceptance remaining

Fresh QA should now do only the runtime checks that Node cannot establish:

- install userscript and refresh; confirm it intercepts the real target Worker under the site's CSP and actual Worker options;
- confirm supported World 921002 / `wofr1` produces identity signature `wofr1-world-921002-browser-rom-v2`;
- confirm an unsupported/lookalike build fails closed if such an environment is available;
- open two same-origin game tabs and verify warnings do not cross;
- restart/reload and verify a clean new pairing;
- start with the legacy research HUD loaded and verify its key listener/channel/resources are gone after Alpha takeover;
- provoke simultaneous valid warnings and visually confirm every target/side group is readable;
- confirm live retarget, stale cleanup, GL rendering, and acceptable frame-time overhead.

No additional broad data collection or attack research is required for RC2.

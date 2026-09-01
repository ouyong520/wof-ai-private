# WOF Alpha RC4 — Fresh Independent QA Findings

Updated: 2026-09-01  
Overall: **PASS**  
Final verdict: **PASS — READY FOR ONE REAL BROWSER ACCEPTANCE**

QA product changes: **0**. This lane did not modify `product/alpha/**`.

## Primary RC4 gate — ALPHAQA-RC3-001 — PASS

The RC3 blocker was independently rechecked against the current RC4 HUD source and with a separate adversarial state-machine harness (`parallel/ALPHAQA_RC4/independent_adversarial.mjs`). The harness is intentionally independent from `product/alpha/regression.mjs`.

Current HUD precedence is:

1. reject unless `schema === wof-alpha-v2` and `session === current page session`;
2. accepted `state` sets `lastMsg`, `lastRx`, and clears `lastDiag`;
3. accepted `diag` performs `lastMsg=null; lastRx=0` in the same message-handler turn, then records diagnostic state;
4. rendering/status derives warning authority only from a fresh `lastRx` within `STALE_MS=1500`.

This closes the exact RC3 failure. A current paired disable/error diagnostic cannot leave the old warning authoritative until the ordinary stale timeout.

### Independent adversarial checks — PASS

The independently executed reproduction passed all of these:

- valid paired warning -> accepted current-session `diag` -> `lastMsg === null` immediately;
- valid paired warning -> accepted current-session `diag` -> `lastRx === 0` immediately;
- same timestamp/next render decision -> diagnostic mode, warning count `0`;
- foreign-session `diag` is rejected before mutation and the current warning remains valid;
- foreign-schema `diag` is rejected before mutation;
- later paired legal warning `state` after `diag` becomes authoritative normally;
- later paired empty `state` after `diag` becomes fresh/silent normally;
- ordinary no-diag warning remains fresh at exactly `1500 ms` and is stale at `1501 ms`;
- unrelated paired message kinds do not clear warning authority.

Therefore `ALPHAQA-RC3-001` is closed.

## World 921031 identity — PASS

Canonical Browser evidence remains:

- MAME set `wof`;
- `Warriors of Fate (World 921031)`;
- full CPU-logical program length `0x100000` / 1 MiB;
- golden SHA-256 `5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62`;
- repeated full digest stable;
- old World 921002 identity explicitly does not match.

The current core still requires exact lowercase equality to that 64-hex digest. Pending, missing, malformed, mismatched, ambiguous-locator, Web Crypto error/timeout and hash exceptions fail closed. Reset-vector/dispatch/layout evidence remains locator/sanity evidence only and cannot enable warnings by itself.

## Production rule scope / F1–F4 quarantine — PASS

Current production evaluation contains exactly two rules:

1. `T18_5440_CYCLE_BODY7512_TM4_LEVEL_90`
2. `T18_5424_CYCLE_BODY7520_TM4_LEVEL_90`

The four history-dependent frozen candidates remain `production:false` and outside the production evaluation loop:

- `T16_B4_DANGER_40`
- `T20_5136_B0_TO_B255_1250`
- `D867BA_3232_TM6_220`
- `D8811E_3232_TM6_135`

The BODY4728/A4704-specific candidate remains excluded. T23, T24, WOF-052, local/discovery candidates and Beta features remain excluded. The obsolete RC2 six-visible-rule requirement was not used.

## Same-type slot reuse / current nonmatch — PASS

The current engine clears its entire `current` map on every `step()` and rebuilds warnings solely from the current snapshots. There is no production watch/history state.

Consequences remain correct:

- same-type same-slot replacement cannot inherit warning age/history/target provenance;
- neutral replacement clears immediately;
- first F5/F6 current nonmatch clears immediately;
- a replacement that independently matches may warn only as fresh current evidence.

## Session / cross-tab isolation — PASS

The bootstrap creates 16 cryptographically random bytes per page and derives a unique channel from that session. Loader and HUD both require exact schema/session pairing. The RC4 diagnostic mutation remains behind that pairing gate, so a foreign-session diagnostic cannot clear a current-session warning.

## Multi-warning HUD — PASS

The HUD model processes the complete warning array, groups by target/side, preserves total warning count and multiplicity, and does not truncate to warning `[0]`.

## Legacy HUD cleanup — PASS

The product HUD still requires legacy `WOFHUD.dispose()` before takeover and refuses takeover when a legacy HUD exists without a disposal function. RC4 did not change this path.

## Normal-user loading contract — PASS (offline/source boundary)

The supported entry remains the document-start userscript. It creates the session before Worker creation, wraps the target `gstyphoon*.js` Worker, injects the detector into the Worker and automatically loads the page HUD. No supported Alpha path requires the old manual Worker-console procedure.

Actual host/CSP/Worker behavior remains deliberately reserved for the single real Browser acceptance after this QA PASS.

## Target / side / UNKNOWN — PASS

The loader rereads `enemy+0x7E` and current enemy/target X every poll. The core accepts only target selectors `0/4/8`, recomputes side from live geometry, and suppresses warnings when target or required geometry is invalid/UNKNOWN.

## Read-only / no-input — PASS

The detector still exposes `readOnly:true`, `ramWrites:0`, `inputInjection:false`. Its game accessors are reads from WASM memory; no game-RAM write or gameplay keyboard/mouse/autoplay path was introduced by RC4.

## WebGL state restoration — PASS (offline/source)

The current HUD continues to snapshot touched GL state and restore it in `finally` blocks around texture upload and HUD drawing. RC4 changed only diagnostic invalidation plus visible RC4 labels in the HUD; the GL preservation path is unchanged from the already-passed RC3 implementation.

## Current RC4 candidate identity

The current critical blobs match the RC4 report snapshot:

- `wof_alpha_core.js` — `267a44190744b6848b0685712c3d5572627d3a8a`
- `wof_alpha_hud_model.js` — `16641129ff651c2733aebc6fae09a280e4bac49b`
- `wof_alpha_loader.js` — `ef6c74fc6cba3c101654a851c411b2b2b005d447`
- `wof_alpha_bootstrap.user.js` — `80dfa948473b49c8e1f0695d131da40084d4f01a`
- `README.md` — `09d6913d7375cf9d45347020f269fe77ff636c11`
- `rules_manifest.json` — `7dc8f66e5e39c04b258c8f1a24751eaee6107818`
- `wof_alpha_hud.js` — `f93f90cc3cc898083d9613841927349159a0d4ae`

The product-recorded RC4 regression also reports PASS for immediate runtime-diag invalidation and preserved ordinary staleness.

## Browser boundary / stop condition

No deterministic P0 or P1 was found in fresh RC4 QA.

The final human Browser acceptance was **not** performed from this QA lane. That is the next bounded stage and should validate the prepared real-host items such as Worker/CSP interception, live golden-hash acceptance, cross-tab/reload behavior, legacy teardown, live WebGL rendering/state restoration and runtime behavior.

**PASS — READY FOR ONE REAL BROWSER ACCEPTANCE**

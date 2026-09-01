# WOF Future Danger — Alpha RC3

Status: **RC3 candidate — product offline regression PASS; ready for fresh independent QA and real-Browser acceptance.**

Supported Browser lineage for this candidate is **WOF / Warriors of Fate (World 921031)**. The authoritative program identity is the exact full 1 MiB CPU-logical SHA-256:

`5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62`

RC3 deliberately ships fewer user-facing warning rules than RC2. The Browser snapshot contract has no proven enemy instance/generation token, so history-derived rules are quarantined rather than allowed to infer continuity from slot/type.

## Normal user install

Use the single userscript entry:

`product/alpha/wof_alpha_bootstrap.user.js`

Install it in a userscript manager, enable it for the Browser game page, then refresh once. It runs at `document-start`, creates a fresh random per-page session, intercepts the target `gstyphoon*.js` Worker, injects the read-only detector there, and loads the WebGL HUD in the page. No manual Worker-console selection is part of the supported Alpha path.

Expected page diagnostic:

`WOFALPHAHUD.status()`

Engineering detector contract: release `wof-alpha-rc3`, `readOnly=true`, `ramWrites=0`, `inputInjection=false`.

If the userscript was enabled after the emulator Worker already existed, refresh so the bootstrap can run before Worker creation.

## Authoritative runtime identity gate

Warnings cannot initialize until all of the following are true:

1. Browser/WASM layout sanity passes: shared HEAP buffer, valid CPS RAM window, self indexes `0/4/8`.
2. The retained reset-vector/dispatch checks locate exactly one plausible 1 MiB program candidate. These checks are **locator/sanity helpers only**, not proof of build identity.
3. The candidate is normalized to CPU-logical byte order and SHA-256 hashed once for that Worker/runtime startup.
4. The resulting lowercase digest equals exactly `5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62`.

Hash pending, missing, malformed, mismatched, ambiguous-locator, Web Crypto failure, timeout, or exception all fail closed. No sparse-vector/dispatch/layout fallback can enable warnings.

Canonical provenance for the confirmed 921031 lineage:

- `tk2e_23c.8f` SHA-1 `10b8cb53a4600e3e76f471a3eee8a600e93096fc`
- `tk2e_22c.7f` SHA-1 `52c2d05279623d93b27856e6b76830796a089eae`
- historical live dispatch delta `+0x34`

## Active production rules

Only two rules are user-facing in RC3, both as stateless hold-only current-level warnings:

1. `T18_5440_CYCLE_BODY7512_TM4_LEVEL_90` — A5440.
2. `T18_5424_CYCLE_BODY7520_TM4_LEVEL_90` — A5424.

For both rules, publication is based only on the exact **current** sample. The warning disappears on the first current nonmatch. A matching same-type replacement is valid only because that replacement independently supplies fresh current evidence; it inherits no `atMs`, age, watch/cycle state, prior target provenance, or previous/current transition state.

Target is reread live from `enemy+0x7E`; threat side is recomputed from current enemy/target X. Invalid/UNKNOWN target is silent.

## Quarantined frozen candidates

The following remain frozen research candidates but are not user-facing production rules in RC3:

- `T16_B4_DANGER_40`
- `T20_5136_B0_TO_B255_1250`
- `D867BA_3232_TM6_220`
- `D8811E_3232_TM6_135`

Reason: each depends on previous/current or watch history, while `same slot + same type` is not proven enemy continuity in the Browser contract.

## Preserved RC2 safety work

RC3 preserves the RC2 mechanisms for random per-session transport binding/cross-tab isolation, simultaneous warning aggregation, safe legacy `WOFHUD.dispose()` takeover, one-step userscript bootstrap, live target/side recomputation, UNKNOWN silence, no RAM writes, and no gameplay input injection.

Still excluded: BODY4728/A4704-specific production logic, T23, T24, discovery/local promotion, WOF-052, and Beta features.

## Offline regression

Run:

```bash
cd product/alpha
node regression.mjs
```

The RC3 product regression covers the exact 921031 SHA-256 positive gate; wrong/mutated/malformed/pending/error digest rejection; sparse-fingerprint-without-full-digest rejection; ambiguous locator rejection; F1–F4 quarantine; F5/F6 hold-only behavior; neutral and matching same-type replacements; UNKNOWN target silence; multi-slot current warnings; session transport; and static read-only/no-input guards.

The existing `parallel/ALPHAQA/independent_qa.mjs` was written for the older six-production-rule RC2 contract and must be refreshed independently rather than edited by this product-fix stage.

## Fresh QA / Browser acceptance remaining

RC3 is not declared QA PASS. Fresh independent QA should verify the new two-rule production inventory and lifecycle contract, then real Browser acceptance should confirm:

- the actual 921031 runtime hashes to the bound golden digest and starts the detector;
- loader/Worker interception works under the real host CSP and Worker options;
- two same-origin game tabs stay isolated;
- reload/restart creates a clean new pairing and one startup hash;
- legacy research HUD resources are released before Alpha takeover;
- simultaneous current-level warnings render correctly;
- retarget/UNKNOWN/stale cleanup and WebGL restoration remain correct;
- no gameplay input injection or RAM writes occur.

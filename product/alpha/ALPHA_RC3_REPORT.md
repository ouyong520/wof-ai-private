# WOF Future Danger — Alpha RC3 Report

Updated: 2026-09-01  
Status: **RC3 CANDIDATE — product offline regression PASS; ready for fresh independent QA**  
Release: `wof-alpha-rc3`  
Manifest: `wof-alpha-rules-v3`

## RC3 decision

RC3 preserves the useful RC2 packaging/isolation/HUD fixes while correcting the two PM release blockers that rejected RC2.

This stage does not expand attack research, does not do WOF-052, and does not add Beta features.

## C1 closed — actual Browser program identity

Supported lineage is now:

- MAME set: `wof`
- description: `Warriors of Fate (World 921031)`
- canonical half SHA-1: `10b8cb53a4600e3e76f471a3eee8a600e93096fc`
- canonical half SHA-1: `52c2d05279623d93b27856e6b76830796a089eae`
- full CPU-logical SHA-256: `5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62`
- historical live dispatch delta: `+0x34`

The loader locates a plausible 1 MiB program region using the retained Browser vector/dispatch checks, normalizes adjacent-pair storage to CPU-logical byte order, and hashes the complete 1 MiB region with Web Crypto exactly once per Worker/runtime startup.

Positive acceptance requires exact lowercase digest equality. Layout/vector/dispatch evidence cannot enable warnings by itself. Pending, missing, malformed, mismatched, ambiguous-locator, timeout, Web Crypto failure, and hash exceptions all leave warnings disabled.

Emitted accepted signature:

`wof-world-921031-maincpu-sha256-v1:5c369ce2de4f53d8`

## C2 closed — same-type slot reuse cannot inherit history warnings

The Browser contract still has no positive enemy instance/generation token. RC3 therefore removes all history/watch state from the user-facing production engine.

### Active production rules

1. `T18_5440_CYCLE_BODY7512_TM4_LEVEL_90` — A5440 — stateless/hold-only current-level.
2. `T18_5424_CYCLE_BODY7520_TM4_LEVEL_90` — A5424 — stateless/hold-only current-level.

For both: show iff the exact current predicate matches; clear on the first current nonmatch. A same-type replacement that independently matches creates fresh current evidence only. Warning rows contain no inherited `atMs`, `ageMs`, watch ID, cycle state, or historical target provenance.

### Quarantined frozen candidates

1. `T16_B4_DANGER_40`
2. `T20_5136_B0_TO_B255_1250`
3. `D867BA_3232_TM6_220`
4. `D8811E_3232_TM6_135`

They remain frozen candidates in metadata but cannot publish user-facing warnings because they require unproven cross-sample continuity/history.

## Preserved RC2 fixes

Preserved unless fresh QA disproves them:

- random 128-bit per-page session and unique BroadcastChannel/message nonce;
- simultaneous warning groups are retained by core/HUD model;
- safe legacy `WOFHUD.dispose()` takeover;
- document-start normal-user userscript bootstrap;
- live target reread and threat-side recompute;
- UNKNOWN/invalid target silent;
- read-only game RAM, `ramWrites=0` contract;
- no keyboard/mouse/gameplay input injection;
- BODY4728/A4704-specific rule remains excluded;
- no T23/T24/discovery/local promotion.

## Offline verification

`product/alpha/regression.mjs` was executed against the RC3 core/loader and returned `PASS`.

Covered blocker cases include:

- exact supported digest accepts;
- wrong/other digest rejects;
- one-digit digest mutation rejects;
- layout + vector + dispatch with no full digest rejects;
- pending hash rejects/silences;
- hash error rejects;
- malformed digest rejects;
- ambiguous/no locator rejects;
- hidden same-type T20 edge cannot warn because F2 is quarantined;
- F1/F3/F4 cannot publish;
- F5/F6 current match shows and first nonmatch clears;
- matching replacement is fresh current evidence only;
- neutral same-type replacement cannot retain the old warning;
- simultaneous same-type current matches remain per-slot;
- UNKNOWN target remains silent;
- session nonce enforcement, no game-heap writes, and no input injection remain asserted.

Recorded output: `product/alpha/regression_result.json`.

## Independent QA note

The existing `parallel/ALPHAQA/independent_qa.mjs` is an RC2-era harness that asserts all six frozen rules remain production-visible and directly exercises history warnings. Those expectations are intentionally invalid under the PM-mandated RC3 quarantine policy. This product-fix stage did **not** modify ALPHAQA findings/harnesses; RC3 requires a fresh independent QA stage against the new contract.

## Remaining human Browser acceptance

No further product-code blocker is known from offline testing. Fresh QA still needs real Browser checks for actual Worker/CSP interception, live 921031 hash acceptance, cross-tab isolation, reload pairing, legacy HUD teardown, WebGL rendering/state restoration, and runtime overhead.

The candidate remains fail-closed if any live identity step does not match the exact golden SHA-256.

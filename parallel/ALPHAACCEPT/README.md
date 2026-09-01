# WOF Alpha RC3 — Browser Acceptance Preparation

Status: **PREPARED / DO NOT RUN FINAL ACCEPTANCE UNTIL FRESH RC3 QA PASSES**

This lane contains support-only tooling for the bounded owner Browser acceptance of `wof-alpha-rc3`.

It does **not** modify `product/alpha/**`, does **not** certify RC3, and does **not** declare Alpha released.

## Current gate

At the time this preparation was written, fresh independent RC3 QA is **BLOCKED / P1** by `ALPHAQA-RC3-001`: a runtime diagnostic can leave a prior warning visible for up to 1500 ms. Final owner Browser acceptance must wait for the product fix and a fresh QA verdict exactly equal to:

`PASS — READY FOR ONE REAL BROWSER ACCEPTANCE`

## Goal of this lane

Reduce the final real-Browser work to one short run with no manual inspection of many Console values.

Install the normal Alpha userscript plus the support-only acceptance userscript in this directory. After the QA gate is open, refresh the game page and click the acceptance helper's single **Run RC3 Browser Acceptance** button.

The helper then:

- confirms document-start bootstrap intercepted the real `gstyphoon*.js` Worker;
- confirms the page HUD is paired to the same random RC3 session;
- listens to the live session-bound detector stream;
- requires the accepted World 921031 identity signature that is emitted only after exact full-program SHA-256 validation;
- records any runtime diagnostic and fails the run if one occurs;
- validates every naturally observed warning is one of the two current-level T18 rules and has sane target/side/current-evidence fields;
- checks the real HUD draw hook is active and captures WebGL state immediately before/after real HUD callback execution;
- measures real HUD callback cost during those samples;
- opens one auxiliary same-origin game tab from the operator click, proves its RC3 session/channel differs from the primary tab, reloads it automatically, proves a fresh session is created, then closes it;
- records legacy-HUD takeover evidence when legacy `WOFHUD` was present;
- emits one final machine-readable JSON object in the page UI and `window.__WOF_ALPHA_ACCEPTANCE_RESULT`.

No rare attack reproduction is required. If neither active T18 condition occurs naturally, attack-warning coverage is reported as `NOT_EXERCISED` rather than treated as an infrastructure failure.

## Files

- `ACCEPTANCE_PLAN.md` — exact scope, automatic checks, pass rules and exclusions.
- `OPERATOR_STEPS.md` — the smallest owner procedure.
- `RESULT_SCHEMA.md` — unambiguous JSON contract.
- `wof_alpha_acceptance.user.js` — support-only one-click acceptance helper.

## Identity authority

Supported Browser build:

- MAME set: `wof`
- `Warriors of Fate (World 921031)`
- exact full 1 MiB CPU-logical SHA-256: `5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62`
- accepted runtime signature: `wof-world-921031-maincpu-sha256-v1:5c369ce2de4f53d8`

The helper does not implement a second ROM locator/hash algorithm. Instead it verifies that the real Worker produced the RC3 accepted signature. In current RC3 source, that state stream is unreachable until the full 1 MiB digest has been computed once and accepted by exact equality; sparse vector/dispatch/layout evidence cannot produce the signature.

## Safety boundary

This support lane does not:

- write game RAM;
- inject keyboard/mouse/gameplay input;
- replace the Alpha detector/core/HUD;
- promote quarantined F1–F4 rules;
- add WOF-052/T23/T24/Beta behavior;
- certify attack coverage;
- declare release readiness.

Read-only/no-input product guarantees remain part of fresh independent QA. The Browser helper adds real-runtime evidence for bootstrap, pairing, identity acceptance, WebGL behavior, isolation/reload and catastrophic-overhead absence.

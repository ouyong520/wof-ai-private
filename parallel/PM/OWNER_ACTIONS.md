# WOF Future Danger AI — Owner Actions

Updated: 2026-09-01 — RC4 QA PASS / Browser acceptance authorized

## Current owner action required: YES — one real Browser acceptance

Fresh independent RC4 QA has completed with:

`PASS — READY FOR ONE REAL BROWSER ACCEPTANCE`

No P0/P1 remains from offline/source QA.
Do not reopen RC4 implementation or QA threads.

## Action O1 — use the prepared Browser acceptance package

Preparation is already complete under:
- `parallel/ALPHAACCEPT/**`

Use both userscripts on the real WOF Browser page:
1. `product/alpha/wof_alpha_bootstrap.user.js`
2. `parallel/ALPHAACCEPT/wof_alpha_acceptance.user.js`

Then:
1. refresh/open the real WOF game normally;
2. let the game reach its ordinary running screen;
3. in the acceptance panel click the single Browser acceptance button once;
4. allow the one auxiliary same-origin tab/window if the browser asks;
5. do not play, use DevTools, or provoke a rare attack during the short run;
6. return only the final JSON shown in the panel.

Valid results:
- `PASS — REAL BROWSER ACCEPTANCE`
- `FAIL — REAL BROWSER ACCEPTANCE`
- `INCOMPLETE — REAL BROWSER ACCEPTANCE`

If FAIL, do not keep retrying. Return the JSON.
If INCOMPLETE, return the JSON first; PM will decide whether it is only environmental.

## Why the helper is still valid for RC4

RC4 changed the HUD fail-closed behavior/version but preserved the product transport contract used by the helper (`release='wof-alpha-rc3'`, schema/session/channel contract). Fresh RC4 QA is the authority for the diag-invalidation fix; the Browser helper verifies the live host/bootstrap/identity/transport/HUD/WebGL/performance environment.

## Non-blocking work — not required before acceptance

- Runtime Speed paired measurement.
- Local WinKawaks ROM hash.
- HUD Anchor Browser projection proof.
- WOF-052 remains after the Alpha release gate.

## Next PM trigger

Paste the final Browser acceptance JSON here.
PM will either:
- record Alpha Browser acceptance PASS and make the release decision; or
- route a concrete Browser failure into one fresh fix/debug stage.

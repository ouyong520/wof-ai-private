# WOF Alpha RC3 — Owner Browser Acceptance Steps

## Do not start yet unless QA gate is open

Run this only after fresh independent RC3 QA says exactly:

`PASS — READY FOR ONE REAL BROWSER ACCEPTANCE`

At the time this support package was prepared, QA was still blocked by P1 `ALPHAQA-RC3-001`; therefore there is currently **no owner Browser action to perform**.

## One-time setup

Have both userscripts enabled for the real Browser WOF page:

1. normal product userscript: `product/alpha/wof_alpha_bootstrap.user.js`;
2. support-only helper: `parallel/ALPHAACCEPT/wof_alpha_acceptance.user.js`.

No Worker Console script paste is part of this flow.

## Final acceptance operation after QA PASS

1. Open/refresh the real WOF game page normally and let the game reach its ordinary running screen.
2. In the small **WOF Alpha RC3 Acceptance** panel, click **Run RC3 Browser Acceptance** once.
3. Allow the one auxiliary same-origin game tab/window if the browser asks about a popup. Do not play or manipulate DevTools during the short run.
4. The helper automatically checks the primary page, opens the auxiliary page, verifies independent pairing, reloads the auxiliary page once, verifies the new pairing, closes it, and writes one final JSON result into the primary-page panel.

You do **not** need to inspect Console values or provoke a specific enemy attack.

## What to return to PM

Return only the final JSON shown by the helper (or its `result` plus JSON if copying the whole object is inconvenient).

Valid top-level results are:

- `PASS — REAL BROWSER ACCEPTANCE`
- `FAIL — REAL BROWSER ACCEPTANCE`
- `INCOMPLETE — REAL BROWSER ACCEPTANCE`

A PASS means the bounded real-Browser acceptance passed. It does not itself declare Alpha released.

## If the helper says INCOMPLETE

The JSON will contain a short `failures` array. Typical environmental causes are:

- popup blocked;
- helper/product userscript not enabled at document-start;
- auxiliary page could not load the real game Worker;
- run started on a page that is not the actual game page.

Resolve only the named environmental cause and repeat once. Do not switch to the old manual two-console workflow.

## If the helper says FAIL

Do not keep retrying until it passes. Preserve the JSON and return it to PM/QA as the Browser evidence for a new product/debug decision.

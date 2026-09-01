# WOF Future Danger AI — Owner Actions

Updated: 2026-09-01 — RC5 candidate ready / owner room-entry retest next

## Current owner action required: YES — one minimal RC5 Browser retest

RC5 engineering is complete for this stage.

Authoritative result:
- `product/alpha/ALPHA_RC5_REPORT.md`
- full product regression: PASS
- current bootstrap: `WOF Future Danger Alpha RC5 Safe Bootstrap`
- RC5 no longer replaces/wraps `window.Worker`, creates no Blob Worker, and leaves native game Worker construction untouched.

## Action O1 — update the installed Alpha userscript to RC5

Use the current repository file:
- `product/alpha/wof_alpha_bootstrap.user.js`

Keep Browser Acceptance Helper disabled for this retest.

## Action O2 — one question only

1. close all current WOF game tabs;
2. enable only the RC5 Alpha userscript;
3. reopen/refresh the normal WOF game page;
4. try to enter one normal room;
5. report only: `RC5 能进房` or `RC5 还是不能进房`.

No Console, Worker selection, attack triggering, warning test, multi-tab test, ROM identity recheck, or JSON collection is required.

## Decision after result

- If `RC5 能进房`: close the P0 room-entry blocker, close RC5 engineering stage, then open a fresh independent RC5 QA/retest stage before resuming full Browser acceptance.
- If `RC5 还是不能进房`: preserve the observation and open a fresh targeted real-host bootstrap diagnostic/fix stage; do not revive the completed RC5 thread.

## Other lanes

WOF-052 evening capture and Python Launcher foundation may continue independently. They are not substitutes for this Alpha release gate.

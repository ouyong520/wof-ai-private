# WOF Future Danger AI — Owner Actions

Updated: 2026-09-01 — real Browser room-entry blocker found

## Current owner action required: YES — open fresh RC5 fix thread

Real Browser A/B evidence is now sufficient to stop acceptance:
- Acceptance helper OFF + normal Alpha userscript ON -> cannot enter room.
- Both WOF userscripts OFF -> can enter normally.

This is a P0 Alpha bootstrap/real-host compatibility blocker.

## Action O1 — keep WOF userscripts disabled

For normal play, keep both disabled:
- `WOF Future Danger Alpha RC3`
- `WOF Alpha Browser Acceptance Loader`

Do not repeat the failing room-entry test on the current candidate.

## Action O2 — open fresh Alpha RC5 Browser Bootstrap Fix thread

Use:

`parallel/PM/ALPHA_RC5_BROWSER_BOOTSTRAP_FIX_START_PROMPT.md`

The RC5 stage owns the product fix. It may modify `product/alpha/**` only as needed to restore normal room/game entry while preserving the passed RC4 safety gates.

## Do not do yet

- Do not rerun Browser acceptance.
- Do not release Alpha.
- Do not revive RC4 implementation or QA threads.
- Do not restart WOF-052 or Beta work as an Alpha blocker substitute.

## Next PM trigger

After RC5 publishes a candidate and exact minimal Browser retest, PM will open a fresh independent QA/retest stage.

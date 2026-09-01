# WOF Future Danger AI — Owner Actions

Updated: 2026-09-01 — RC3 QA is the only Alpha-path owner action

## Current owner action required: YES — ensure fresh RC3 QA is running

RC3 implementation is complete and closed.
The next Alpha stage is a fresh independent QA thread using:

`parallel/PM/ALPHA_RC3_QA_START_PROMPT.md`

Current GitHub status: no RC3-QA verdict commit is present yet.

If that QA thread is already open, no duplicate thread is needed; let it continue until it commits either:
- `PASS — READY FOR ONE REAL BROWSER ACCEPTANCE`, or
- a concrete P0/P1 blocker.

Do not run final Alpha Browser acceptance before that verdict exists.

## Non-blocking support actions — do not delay Alpha QA

### Local ROM identity

Support lane reached STOP B.
One read-only command can cryptographically decide whether local WinKawaks is really World 921002 or matches Browser World 921031:

`powershell -NoProfile -ExecutionPolicy Bypass -File .\parallel\LOCALROM\local_rom_identity_probe.ps1`

Run only from an up-to-date local `wof-ai-private` checkout while WinKawaks has WOF loaded. Game may remain paused. Return the single JSON output.

This is useful but does not block Alpha.

### Runtime speed

Support lane reached STOP B.
Exactly one paired 15-second no-input measurement per runtime remains. It is not required for Alpha because Browser production lead labels were measured in the Browser runtime and remain valid.

Do not spend owner time on this until the QA stage is running or completed.

### Player-anchored HUD

Beta support reached STOP B.
One minimal Browser projection proof remains before implementation. Do not run it as an Alpha release prerequisite.

## Completed threads to close

- Alpha RC3 implementation — complete candidate.
- Runtime Speed audit — STOP B, handoff written.
- Player-Anchored HUD audit — STOP B, handoff written.
- Local ROM identity audit — STOP B, one owner command remains.

## Do not do yet

- Do not run final Alpha Browser acceptance before RC3 QA PASS.
- Do not modify RC3 from its completed implementation thread.
- Do not restart WOF-052 as an Alpha blocker.
- Do not perform broad Browser/WinKawaks recollection.

## Next PM trigger

After RC3 QA commits its verdict, PM will either:
- create a fresh next fix stage for any P0/P1 blocker; or
- issue one exact bounded Browser acceptance procedure and decide Alpha release.

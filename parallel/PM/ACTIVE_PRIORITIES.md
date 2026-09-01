# WOF Future Danger AI — Active Priorities

Updated: 2026-09-01 — real Browser acceptance exposed P0 room-entry blocker

## P0 — Alpha RC5 real-Browser bootstrap fix

Fresh RC4 independent QA had passed offline/source gates, but the first real Browser acceptance setup exposed a launch blocker before the acceptance run could begin.

Owner A/B evidence:
- Acceptance helper OFF + normal Alpha userscript ON -> game cannot enter the room.
- Both WOF userscripts OFF -> game enters normally.

Therefore the normal Alpha bootstrap/product entry path is implicated. This is a **P0 release blocker** because enabling Alpha can prevent the base game from entering a room.

Authoritative PM blocker record:
- `parallel/PM/ALPHA_BROWSER_ACCEPTANCE_BLOCKER.md`

Fresh fix bootstrap:
- `parallel/PM/ALPHA_RC5_BROWSER_BOOTSTRAP_FIX_START_PROMPT.md`

Only the fresh RC5 engineering stage may modify `product/alpha/**`.

## Preserve passed RC4 gates

Do not reopen without new evidence:
- exact World 921031 full-program SHA-256 authority;
- exactly two current-level T18 production rules;
- F1-F4 quarantine;
- same-type slot replacement safety;
- session isolation;
- multi-warning HUD;
- runtime diag immediate warning invalidation;
- target/side/UNKNOWN safety;
- read-only/no-input;
- GL restoration.

The new blocker is specifically real-host normal-user bootstrap / Worker interception / injection compatibility.

## Browser acceptance

PAUSED. Do not rerun the acceptance helper until RC5 produces a candidate and a fresh retest stage authorizes it.

## SUPPORT — READY / NON-BLOCKING

- Runtime Speed Probe Tooling: complete; one paired ~15 s local/Browser measurement remains when convenient.
- Local WinKawaks ROM identity: one read-only local hash remains.
- HUD Anchor Proof Tooling: complete; one Browser projection proof remains for Beta.

## Explicit stops

- Keep both WOF userscripts disabled for normal play until RC5 retest.
- STOP repeated room-entry retries on the broken candidate.
- STOP Alpha release.
- STOP broad collection / WOF-052 / Beta work as a substitute for the launch blocker.

## Current fastest path

**RC5 real-host bootstrap fix -> fresh independent QA/retest -> one real Browser acceptance -> Alpha release decision**

# WOF Alpha — Real Browser Acceptance Blocker

Updated: 2026-09-01
Severity: **P0 / release blocker**
Status: **REAL BROWSER ACCEPTANCE FAILED BEFORE RUN**

## Owner-observed A/B result

During the authorized post-RC4 real Browser acceptance setup:

1. `WOF Alpha Browser Acceptance Loader` disabled, `WOF Future Danger Alpha RC3` enabled -> owner reports the game still cannot enter the room.
2. Both WOF userscripts disabled -> owner reports the game can enter the game/room normally.

Therefore the acceptance helper is not the sole cause. The normal Alpha bootstrap/product path is implicated by the minimal A/B isolation.

## Product impact

This is a P0 launch/usability defect for Alpha: enabling the supported normal-user Alpha entry path prevents normal game entry on the real host.

No Alpha release is allowed while this remains unresolved.

## What is NOT reopened

The following RC4 independent-QA results remain valid unless new evidence contradicts them:
- World 921031 exact SHA-256 gate;
- two current-level T18 production rules only;
- F1-F4 quarantine;
- same-type slot replacement safety;
- session isolation;
- multi-warning HUD;
- runtime diag immediate warning invalidation;
- target/side/UNKNOWN safety;
- read-only/no-input semantics.

The new blocker is specifically the real-host normal-user bootstrap/Worker interception/injection path and its compatibility with entering a room.

## Required next stage

Open a fresh product engineering stage using:

`parallel/PM/ALPHA_RC5_BROWSER_BOOTSTRAP_FIX_START_PROMPT.md`

Only that stage may modify `product/alpha/**`.

## Owner action now

Keep both WOF userscripts disabled for normal play. Do not repeat the failing room-entry test until RC5 provides a new candidate and exact retest instruction.

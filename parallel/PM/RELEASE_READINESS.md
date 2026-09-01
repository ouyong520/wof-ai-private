# WOF Future Danger AI — Release Readiness

Updated: 2026-09-01 — real Browser acceptance exposed P0 bootstrap blocker

## Alpha — **BLOCKED / RC5 REQUIRED**

Fresh RC4 independent QA passed offline/source validation, but the first real Browser acceptance setup exposed a launch blocker before acceptance could run.

Owner A/B result:
- normal Alpha userscript enabled, acceptance helper disabled -> game cannot enter room;
- both WOF userscripts disabled -> game enters normally.

This is a P0 release blocker because the supported normal-user Alpha entry path can prevent the base game from entering a room.

## Previously passed gates remain retained evidence

- exact `wof / Warriors of Fate (World 921031)` full-program SHA-256 identity;
- identity pending/mismatch/error fail-closed;
- exactly two stateless current-level T18 production rules;
- F1-F4 quarantine;
- same-type replacement safety;
- session/cross-tab isolation;
- simultaneous warning aggregation;
- legacy HUD cleanup;
- runtime diagnostic immediate warning invalidation;
- target/side/UNKNOWN safety;
- read-only/no-input;
- WebGL state restoration.

The new blocker is real-host bootstrap/Worker interception/injection compatibility, not a reopening of rule semantics.

## Gate status

| Gate | Status |
|---|---|
| RC4 product regression | PASS |
| Fresh RC4 independent QA | PASS |
| Real host can enter room with Alpha enabled | **FAIL / P0** |
| Browser acceptance | BLOCKED / PAUSED |
| RC5 bootstrap fix | NEXT |
| Alpha release | BLOCKED |

## Required sequence

1. fresh RC5 real-Browser bootstrap fix;
2. preserve all RC4 safety gates;
3. one minimal owner room-entry retest on the RC5 candidate;
4. fresh independent QA/retest;
5. only then rerun the bounded Browser acceptance;
6. Alpha release decision only after Browser PASS.

## Current release judgment

**Alpha is not releasable. Real Browser testing found a P0 startup compatibility defect: enabling the supported Alpha userscript can prevent normal room entry.**

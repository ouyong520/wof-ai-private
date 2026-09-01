# WOF Future Danger AI — Release Readiness

Updated: 2026-09-01 — RC3 independent QA complete / one P1 requires RC4

## Alpha — **RC3 QA BLOCKED / RC4 REQUIRED**

Fresh independent RC3 QA is complete. It found exactly one release blocker:

- `ALPHAQA-RC3-001` — a runtime disable/error diagnostic does not immediately invalidate the last warning in the page HUD. A prior warning can remain visible for up to 1500 ms after the detector has already failed closed.

This is a P1 user-visible fail-closed defect and blocks human Browser acceptance.

## RC3 areas already independently passed

Do not treat the entire candidate as failed. Independent QA passed:
- exact `wof / Warriors of Fate (World 921031)` full-program SHA-256 gate;
- wrong/missing/pending/error/malformed identity remains disabled;
- no sparse identity fallback;
- no same-type hidden replacement inheritance;
- exactly two stateless current-level T18 production rules;
- F1-F4 quarantined / cannot user-alert;
- session/cross-tab isolation;
- simultaneous warning aggregation;
- legacy HUD cleanup;
- normal-user document-start bootstrap;
- live target / side recomputation;
- UNKNOWN target silence;
- read-only / no gameplay input injection;
- GL state restoration.

## Alpha gate status

| Gate | Status |
|---|---|
| Browser World 921031 exact identity | PASS independent QA |
| same-type replacement safety | PASS independent QA |
| production rule inventory | PASS — only two T18 current-level rules |
| F1-F4 quarantine | PASS |
| session isolation | PASS offline/source |
| multi-threat HUD | PASS offline/source |
| legacy HUD teardown | PASS offline/source |
| normal-user bootstrap | PASS offline/source / live acceptance later |
| target/side/UNKNOWN | PASS offline/source |
| read-only/no-input | PASS offline/source |
| runtime explicit-error warning clearing | **FAIL P1 — RC4 required** |
| RC3 independent QA | COMPLETE / BLOCKED |
| RC4 implementation | NEXT |
| fresh RC4 independent QA | WAIT |
| Browser acceptance | PREP COMPLETE / NOT AUTHORIZED |
| Alpha release | WAIT |

## Browser acceptance preparation

`parallel/ALPHAACCEPT/**` is complete. Once a future independent QA returns `PASS — READY FOR ONE REAL BROWSER ACCEPTANCE`, the owner operation is already reduced to a normal refresh + one acceptance button, with automated auxiliary-tab checks and one result JSON.

Do not run it before RC4 + fresh QA.

## Release sequence

1. close completed RC3 QA thread;
2. open fresh RC4 fix using `parallel/PM/ALPHA_RC4_FIX_START_PROMPT.md`;
3. RC4 changes only the immediate diagnostic warning-clearing behavior and adds regression;
4. close RC4 implementation when candidate is produced;
5. open fresh independent RC4 QA;
6. if QA passes, run prepared one-click Browser acceptance;
7. if Browser acceptance passes, PM may release Alpha.

## Parallel non-blocking support

- Local WinKawaks ROM identity: one local read-only hash command remains; expected local World 921002 vs Browser World 921031.
- Runtime Speed: simulation-speed question remains separate; support tooling may continue.
- Player-Anchored HUD: Beta projection proof tooling/handoff is separate from Alpha.

## Current release judgment

**Alpha is blocked by one narrow P1, not by the core identity/lifecycle/rule-scope work. Fastest path: RC4 tiny fix -> fresh QA -> prepared one-click Browser acceptance.**

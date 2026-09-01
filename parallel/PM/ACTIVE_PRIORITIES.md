# WOF Future Danger AI — Active Priorities

Updated: 2026-09-01 — RC5 real-Browser room-entry repair passed; usable Alpha now waits on safe live-Worker transport

## P0 — Safe non-replacing live-Worker transport for usable Browser Alpha

Owner real-Browser RC5 retest result:
- current `WOF Future Danger Alpha RC5 Safe Bootstrap` enabled;
- Browser Acceptance Helper disabled;
- game **can enter a room normally**;
- no Alpha HUD / warnings appear.

Decision:
- the former P0 `Alpha prevents room entry` is CLOSED by owner Browser evidence, pending fresh independent RC5 QA confirmation;
- the lack of HUD/warnings is expected under RC5 when no safe external live-Worker transport pairs;
- Alpha is still not usable/releasable until a non-replacing transport connects the detector to the already-native WOF Worker.

Do not restore the old `window.Worker` replacement / Blob Worker path.

The active Python Launcher foundation is the primary non-duplicative transport path:
- Chrome/Edge CDP post-start attachment;
- discover already-running WOF page / `gstyphoon*.js` Worker;
- discover module/heap;
- keep base gameplay independent of attach failure;
- read-only foundation first.

Start prompt:
- `parallel/PM/PYTHON_LAUNCHER_FOUNDATION_START_PROMPT.md`
- `parallel/PM/PYTHON_LAUNCHER_TRAY_UI_REQUIREMENTS.md`

## P1 — Fresh independent RC5 QA / retest

Open a fresh QA stage using:
- `parallel/PM/ALPHA_RC5_QA_RETEST_START_PROMPT.md`

Purpose:
- independently confirm the no-Worker-replacement gameplay-first RC5 repair;
- preserve all RC4 safety gates;
- explicitly distinguish `room-entry repair PASS` from `Alpha release-ready`.

QA must not modify `product/alpha/**` and must not duplicate Python Launcher implementation.

## WOF-052 — evening batch COMPLETE / STOP until natural T18 coverage

Latest bounded batch:
- 5 joined / 5 complete / 0 error / 0 interrupted;
- readOnly=true / ramWrites=0;
- 59,997 polls / 241,485 enemy samples / 1,411 ACTIVE edges;
- real multiplayer occupancy was present;
- but all five rooms had `T18 samples = 0` and candidate cycles = 0.

Result:
- no A4704-vs-A4712 ordered discriminator can be inferred;
- no collector/tooling defect found;
- do not manually hunt attacks or reopen broad collection;
- resume WOF-052 only opportunistically when natural rooms actually expose T18.

Authoritative report:
- `reports/WOF-052_ANALYSIS.md`

## Preserve passed Alpha safety gates

Do not reopen without new evidence:
- World 921031 exact full-program SHA-256 authority;
- exactly two current-level T18 production rules;
- F1-F4 quarantine;
- same-type slot replacement safety;
- session isolation;
- multi-warning HUD;
- runtime diag immediate warning invalidation;
- target/side/UNKNOWN safety;
- read-only/no-input;
- GL restoration.

## Browser acceptance

Full Browser acceptance remains PAUSED.

It resumes only after:
1. fresh independent RC5 QA accepts the room-entry repair; and
2. a safe non-replacing live-Worker transport actually pairs the detector so Browser acceptance can test real HUD/warning behavior.

## Current fastest path

**Python Launcher safe live-Worker attachment proof + fresh RC5 independent QA -> Alpha transport integration -> bounded real Browser acceptance -> Alpha release decision**

WOF-052 stays parked until natural T18 coverage appears.

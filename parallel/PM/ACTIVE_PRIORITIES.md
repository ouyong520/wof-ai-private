# WOF Future Danger AI — Active Priorities

Updated: 2026-09-01 — RC5 candidate ready; one owner room-entry retest is the Alpha gate

## P0 — RC5 owner Browser room-entry retest

RC5 product engineering has completed its stage with:
- `product/alpha/ALPHA_RC5_REPORT.md`
- full product regression PASS
- current userscript `WOF Future Danger Alpha RC5 Safe Bootstrap`
- native game `window.Worker` construction left untouched
- no Blob Worker / Worker URL replacement
- gameplay-first fail-open behavior: if Alpha cannot attach safely, base game continues and Alpha remains silent.

The only remaining P0 check is one real Browser question with Browser Acceptance Helper disabled:

**Can the game enter a room normally with only the current RC5 Alpha userscript enabled?**

If YES: close the room-entry blocker and open a fresh independent RC5 QA/retest stage.
If NO: route the exact real-host failure to a fresh targeted diagnostic/fix stage.

## P1-opportunistic — WOF-052 evening multiplayer capture

The evening multiplayer window may be used for the bounded read-only WOF-052 lane:
- up to 5 rooms;
- focus on T18 BODY4728/A4/B2/TM1 ordered context;
- seek A4704 vs A4712 sequence discrimination;
- discovery only;
- no `product/alpha/**` changes;
- read-only / `ramWrites=0` / no input injection.

Start prompt:
- `parallel/PM/WOF_052_EVENING_CAPTURE_START_PROMPT.md`

## P1-productization — Python Launcher foundation

Python/EXE launcher work may continue independently:
- Chrome/Edge CDP post-start attachment;
- automatic WOF page/Worker/module/heap discovery;
- Windows tray icon + settings UI;
- read-only foundation only;
- no one-key moves, command injection, or RAM writes yet.

Start prompt:
- `parallel/PM/PYTHON_LAUNCHER_FOUNDATION_START_PROMPT.md`
- `parallel/PM/PYTHON_LAUNCHER_TRAY_UI_REQUIREMENTS.md`

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

Full Browser acceptance remains PAUSED until the RC5 room-entry retest passes and fresh independent RC5 QA/retest is completed.

## Current fastest path

**owner RC5 room-entry retest -> fresh independent RC5 QA/retest -> full Browser acceptance -> Alpha release decision**

Parallel:
- WOF-052 evening capture
- Python Launcher foundation

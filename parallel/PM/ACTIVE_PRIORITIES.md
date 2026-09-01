# WOF Future Danger AI — Active Priorities

Updated: 2026-09-01 — Alpha RC5 P0 remains primary; WOF-052 evening capture and Python launcher foundation may run independently

## P0 — Alpha RC5 real-Browser bootstrap fix

Fresh RC4 independent QA had passed offline/source gates, but the first real Browser acceptance setup exposed a launch blocker before the acceptance run could begin.

Owner A/B evidence:
- Acceptance helper OFF + normal Alpha userscript ON -> game cannot enter the room.
- Acceptance helper ON + normal Alpha userscript OFF -> game can enter the room.
- Both WOF userscripts OFF -> game enters normally.

Therefore the normal Alpha bootstrap/product entry path is implicated. This is a **P0 release blocker** because enabling Alpha can prevent the base game from entering a room.

Authoritative PM blocker record:
- `parallel/PM/ALPHA_BROWSER_ACCEPTANCE_BLOCKER.md`

Fresh fix bootstrap:
- `parallel/PM/ALPHA_RC5_BROWSER_BOOTSTRAP_FIX_START_PROMPT.md`

Only the fresh RC5 engineering stage may modify `product/alpha/**`.

## P1-opportunistic — WOF-052 evening multiplayer capture

The owner reports that evening multiplayer rooms are now available. Because WOF-052 needs natural Browser room coverage, especially T18, PM temporarily resumes this independent read-only research lane while RC5 proceeds.

Start prompt:
- `parallel/PM/WOF_052_EVENING_CAPTURE_START_PROMPT.md`

Purpose:
- collect candidate-containing T18 zero->ACTIVE ordered cycles;
- seek an ordered-state discriminator between A4704 and A4712 after the ambiguous BODY4728/A4/B2/TM1 state;
- use up to 5 available rooms, prioritizing T18;
- keep sequence evidence discovery-only until a later prospective validator.

Hard boundary:
- no `product/alpha/**` changes;
- do not use the broken Alpha bootstrap;
- read-only / `ramWrites=0` / no input injection;
- WOF-052 remains non-blocking for Alpha release.

## P1-productization — Python launcher foundation

A separate read-only launcher lane may begin now because it does not need to modify Alpha product code or WOF-052 collectors.

Start prompt:
- `parallel/PM/PYTHON_LAUNCHER_FOUNDATION_START_PROMPT.md`

UX requirements:
- `parallel/PM/PYTHON_LAUNCHER_TRAY_UI_REQUIREMENTS.md`

Goal:
- Python/EXE -> Chrome/Edge CDP -> discover already-running WOF page/Worker -> attach after normal game startup;
- avoid replacing `window.Worker`;
- automatically discover Worker/module/heap;
- show status through a Windows bottom-right tray icon and on-demand settings window;
- preserve read-only / no-input behavior in this foundation stage;
- base game must continue even when launcher attachment fails.

This lane is not an Alpha release blocker and must not implement one-key moves, command injection, or RAM writes yet.

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

The new Alpha blocker is specifically real-host normal-user bootstrap / Worker interception / injection compatibility.

## Browser acceptance

PAUSED. Do not rerun the acceptance helper until RC5 produces a candidate and a fresh retest stage authorizes it.

## SUPPORT — READY / NON-BLOCKING

- Runtime Speed Probe Tooling: complete; one paired ~15 s local/Browser measurement remains when convenient.
- Local WinKawaks ROM identity: one read-only local hash remains.
- HUD Anchor Proof Tooling: complete; one Browser projection proof remains for Beta.

## Explicit stops

- Keep the Alpha product userscript disabled for normal play until RC5 retest.
- STOP repeated room-entry retries on the broken Alpha candidate.
- STOP Alpha release.
- WOF-052 may run only as the bounded evening capture lane above; do not let it substitute for or modify the RC5 launch blocker.
- Python launcher foundation stays read-only; no one-key moves / command injection / RAM writes yet.
- STOP Beta work and broad collection.

## Current fastest path

Primary release path:
**RC5 real-host bootstrap fix -> fresh independent QA/retest -> one real Browser acceptance -> Alpha release decision**

Parallel time-window opportunity:
**WOF-052 evening rooms -> one merged read-only JSON -> ordered T18 discrimination analysis**

Parallel productization opportunity:
**Python launcher foundation -> post-start CDP attachment proof -> tray UX -> later EXE packaging**

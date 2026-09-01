# WOF Future Danger AI — Active Priorities

Updated: 2026-09-01 — RC5 room-entry repair passed; Python launcher foundation implemented; safe live-Worker proof is now P0

## P0 — Python Launcher Windows/Browser live proof

Authoritative state:
- owner proved RC5 can enter a real Browser room normally;
- RC5 intentionally shows no HUD/warnings without a safe external transport;
- `parallel/PYLAUNCH/**` foundation is now implemented;
- foundation uses post-start localhost CDP, does not replace `window.Worker`, and remains read-only;
- one real Windows/Browser proof remains.

Fresh proof stage:
- `parallel/PM/PYTHON_LAUNCHER_WINDOWS_PROOF_START_PROMPT.md`

Required proof:
- Browser OK;
- WOF page OK;
- `gstyphoon*.js` Worker OK;
- WASM/heap OK;
- exact World 921031 OK;
- READ ONLY / RAM writes 0;
- room remains playable.

If PASS, the next fresh stage is Alpha transport integration. Do not modify Alpha from the proof stage itself.

## P1 — Fresh independent RC5 room-entry repair QA

Fresh QA stage:
- `parallel/PM/ALPHA_RC5_QA_RETEST_START_PROMPT.md`

Goal:
- independently confirm the no-Worker-replacement RC5 repair and retained RC4 safety gates;
- close only the specific room-entry P0;
- do not call Alpha release-ready while safe transport is still missing.

## P1-opportunistic — WOF-052L long event capture tooling

The valid five-room WOF-052 batch had zero T18 coverage. PM has approved replacing repeated blind 120-second windows with one bounded long event-capture design.

Decision:
- `parallel/PM/WOF_052_LONG_CAPTURE_DECISION.md`

Fresh tooling stage:
- `parallel/PM/WOF_052L_LONG_CAPTURE_START_PROMPT.md`

Target:
- about 60 minutes natural play;
- event-selective T18 retention only;
- compact checkpointing and bounded JSON;
- no full-frame raw dump;
- no manual attack hunting;
- read-only / no input injection;
- no `product/alpha/**` changes.

WOF-052L remains non-blocking for Alpha release.

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

Full Browser acceptance remains PAUSED until:
1. RC5 fresh independent QA accepts the room-entry repair; and
2. safe live-Worker transport is proven and integrated so real HUD/warning behavior can run.

## Current fastest path

**PYLAUNCH Windows live proof + RC5 independent QA -> fresh Alpha transport integration -> bounded Browser acceptance -> Alpha release decision**

Parallel research only:
**WOF-052L tooling -> one long natural capture -> ordered T18 analysis**

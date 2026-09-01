# WOF Future Danger AI — Owner Actions

Updated: 2026-09-01 — RC5 room-entry test passed; next work is safe transport proof + fresh QA

## Current owner action required: YES — open fresh stages, but do not perform more Alpha Browser tests yet

The RC5 room-entry retest is complete:
- RC5 enabled;
- Acceptance Helper disabled;
- game can enter normally;
- no HUD/warnings because no safe live-Worker transport is paired.

Do not repeat the RC5 room-entry test and do not run full Browser acceptance yet.

## Fresh stage A — Python Launcher Windows proof

Use:
- `parallel/PM/PYTHON_LAUNCHER_WINDOWS_PROOF_START_PROMPT.md`

The foundation implementation already exists under `parallel/PYLAUNCH/**`. This stage should first reduce the live Windows proof to the simplest safe owner operation, then ask for exactly one proof.

## Fresh stage B — RC5 independent QA

Use:
- `parallel/PM/ALPHA_RC5_QA_RETEST_START_PROMPT.md`

This is read-only QA. It must not modify `product/alpha/**`.

## Fresh stage C — WOF-052L tooling (optional parallel research)

PM approved a long event-filtered capture instead of repeating blind 120-second rooms.

Use:
- `parallel/PM/WOF_052L_LONG_CAPTURE_START_PROMPT.md`

Do not start the one-hour human capture until that tooling stage explicitly says READY.

## Current game-script state

- RC5 Safe Bootstrap may remain installed.
- Browser Acceptance Loader should remain disabled until Browser acceptance is re-authorized.
- No more Worker-console/manual JavaScript work is required for the Alpha product path.

## Next PM trigger

Return when any fresh stage reports a stop condition or asks for one precise owner action. PM will reassess the whole project before authorizing the next human test.

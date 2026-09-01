# WOF Future Danger AI — Owner Actions

Updated: 2026-09-01 — RC5 QA PASS; only one minimal PYLAUNCH Windows proof is required now

## Current owner action required: YES — one double-click proof

RC5 independent QA is complete and passed. Do not repeat RC5 room-entry testing and do not run Browser Acceptance yet.

The only immediate owner action is the real Windows proof for the Python Launcher.

## Exact operation

1. update the local `wof-ai-private` repository to latest;
2. open:
   `parallel\PYLAUNCH\`
3. double-click exactly:
   `RUN_WINDOWS_PROOF.cmd`
4. use the Chrome/Edge window opened by the launcher;
5. enter one normal WOF room exactly as usual;
6. do not open DevTools and do not paste JavaScript;
7. confirm the room remains normally playable.

The proof tooling continuously writes:
- `parallel\PYLAUNCH\WINDOWS_PROOF_STATUS.json`

## Pass condition

All must be true simultaneously:
- Browser: OK
- WOF page: OK
- Worker: OK
- WASM / heap: OK
- World 921031: OK
- READ ONLY / RAM writes: 0
- room remains normally playable

If PASS, report only:

`PASS — PYLAUNCH WINDOWS PROOF`

If it does not PASS, provide only:

`parallel\PYLAUNCH\WINDOWS_PROOF_STATUS.json`

No Console/Worker selection, gameplay capture, RAM collection, frame counting, or extra diagnostics are required.

## Other active lanes

WOF-052L automatic multi-room recorder, Browser Fleet Manager, and Safe Transport Integration Prep may continue independently. Do not perform extra human tests for them unless their own fresh stage reaches an explicit owner gate.

## After PYLAUNCH PASS

PM will authorize a fresh Alpha transport-integration implementation stage. Do not reopen an old Alpha engineering thread.

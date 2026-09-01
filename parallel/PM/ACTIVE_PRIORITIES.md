# WOF Future Danger AI — Active Priorities

Updated: 2026-09-01 — RC5 independent QA PASS; PYLAUNCH real Windows proof is now the sole immediate Alpha gate

## P0 — Python Launcher real Windows/Browser live proof

Repository-side proof automation is READY.

Current stage result:
- Foundation remains implemented under `parallel/PYLAUNCH/**`;
- proof UX has been reduced to one double-click entry: `parallel/PYLAUNCH/RUN_WINDOWS_PROOF.cmd`;
- it continuously writes `parallel/PYLAUNCH/WINDOWS_PROOF_STATUS.json`;
- automated PASS requires Browser / WOF page / gstyphoon Worker / WASM-heap / exact World 921031 / READ ONLY-RAM writes 0 simultaneously;
- owner must additionally confirm the room remains normally playable;
- no DevTools, Worker-console selection, pasted JavaScript, frame counting, gameplay capture or memory collection is required.

If this real Windows proof PASSes, authorize a fresh Alpha transport-integration implementation stage using the proven non-replacing CDP/live-Worker path.

## CLOSED — RC5 independent room-entry repair QA

Fresh independent QA verdict:

**PASS — RC5 ROOM-ENTRY REPAIR QA**

The former P0 `Alpha prevents room entry` is CLOSED.

Retained evidence includes:
- owner real-Browser room-entry PASS with RC5 enabled;
- no `window.Worker` replacement/wrap;
- no Blob/ObjectURL Worker rewrite;
- gameplay fail-open;
- warning/HUD fail-closed while no authoritative transport is paired;
- RC4 safety gates preserved;
- exact World 921031 identity gate preserved;
- exactly two current-level T18 production rules;
- F1-F4 quarantine;
- read-only / `ramWrites=0` / no input injection.

No more RC5 QA work is needed unless new contrary evidence appears.

## P1 research tooling — WOF-052L automatic multi-room recorder

Use the revised specification:
- `parallel/PM/WOF_052L_LONG_CAPTURE_START_PROMPT.md`

Current target is no longer a fixed one-hour single-room run.

Build an always-on Windows/CMD/Python recorder that:
- remembers one output directory;
- discovers 1 / 5 / 10+ supported WOF rooms automatically;
- starts each room capture automatically;
- isolates each room/session/Worker lifecycle;
- finalizes one room independently on close/reload/disconnect;
- lets other rooms continue;
- accepts newly opened rooms at any time;
- saves compact per-room JSON/checkpoints plus merged run JSON;
- keeps ordinary frames as counters only, not long raw dumps.

Mandatory research target remains T18 `BODY4728/A4/B2/TM1 -> A4704 vs A4712` ordered discrimination. Secondary compact coverage may retain T23, enemy/attack frequency, player occupancy, target/retarget and rare descriptor+attack summaries.

This remains non-blocking for Alpha release.

## P1 acceleration — Browser Fleet Manager

A separate project-acceleration lane may build the safe multi-browser/fleet utility:
- one-click 1 / 5 / 10 rooms;
- independent profiles/CDP targets;
- automatic numbering/window layout;
- independent restart/close;
- discoverable by PYLAUNCH and WOF-052L;
- no `window.Worker` replacement;
- no RAM writes/input injection.

This is tooling acceleration, not an Alpha release gate.

## P1 preparation — Alpha Safe Transport Integration Prep

Architecture/interface preparation may proceed in parallel without modifying `product/alpha/**` or `parallel/PYLAUNCH/**`.

It should freeze the future contract for:
- Worker snapshot/state format;
- World 921031 identity handshake;
- session/room/Worker lifecycle;
- disconnect/reconnect/stale-state cleanup;
- detector input and warning output contracts;
- HUD transport;
- polling/backpressure;
- fail-open gameplay / fail-closed warning;
- multi-tab/session isolation;
- mock integration tests/regression vectors.

Actual Alpha transport implementation remains blocked until the real PYLAUNCH Windows proof PASSes.

## Browser acceptance

Full Browser acceptance remains PAUSED.

It resumes only after:
1. PYLAUNCH real Windows proof PASS;
2. fresh Alpha transport integration using that proven path;
3. integrated regression PASS.

Then run bounded real Browser acceptance for actual detector/HUD/warning behavior before any Alpha release decision.

## Current fastest path

**owner PYLAUNCH one-CMD proof -> fresh Alpha transport integration -> bounded Browser acceptance -> Alpha release decision**

Parallel/nonblocking:
- WOF-052L automatic recorder;
- Browser Fleet Manager;
- Safe Transport Integration Prep.

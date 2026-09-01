# WOF Python Launcher — Fresh Windows/Browser Live Proof Result

Date: 2026-09-01
Status: **AUTOMATION READY; ONE MINIMAL OWNER WINDOWS RUN REMAINS**

## Foundation is not being redone

The existing Python Launcher Foundation remains the transport under test. This proof stage only adds owner-proof UX under `parallel/PYLAUNCH/**`.

Still unchanged:

- no `product/alpha/**` modification;
- no WOF-052/WOF-052L modification;
- no Tampermonkey dependency;
- no `window.Worker` replacement/wrapping;
- no gameplay input injection;
- no game/WASM RAM writes;
- no one-key moves / Assist Mode;
- localhost Chrome/Edge CDP only;
- exact World 921031 full 1 MiB CPU-logical SHA-256 gate remains `5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62`.

## Proof UX added

New double-click entry:

```text
parallel\PYLAUNCH\RUN_WINDOWS_PROOF.cmd
```

It:

1. reuses `.venv` if present;
2. creates it only when missing;
3. installs the three launcher dependencies only when their imports are missing;
4. starts the tray launcher with `pythonw.exe` so no permanent console window is required;
5. lets the launcher attach to or start its dedicated localhost-CDP Chrome/Edge profile;
6. continuously writes one compact diagnostics file:

```text
parallel\PYLAUNCH\WINDOWS_PROOF_STATUS.json
```

The JSON is generated from launcher status only. Failure to export diagnostics is deliberately ignored by the monitor path so diagnostics can never become a game/browser blocker.

## Automated proof JSON contract

`WINDOWS_PROOF_STATUS.json` reaches `"automatedResult": "PASS"` only when all six checks are simultaneously true:

```text
Browser: OK
WOF page: OK
Worker: OK
WASM / heap: OK
World 921031: OK
READ ONLY / RAM writes: 0
```

It also records page/Worker URLs, module key, heap size, exact SHA-256/reason, launcher error, `readOnly`, `ramWrites`, and `inputInjection`.

Even after automated PASS it reports:

```text
"ownerPlayabilityConfirmation": "REQUIRED"
```

because repository/offline tooling must not pretend to prove that the real room stayed playable.

## Offline validation completed in this stage

- `wof_launcher/proof.py` compiles under Python.
- PASS aggregation was exercised with all six checks true.
- changing `ramWrites` away from zero forces the proof result back to WAITING.
- proof JSON is written by atomic replace (`*.tmp` -> final file).
- no new CDP method, Worker hook, input path, or RAM-write path was introduced.

## The only remaining owner operation

1. Update the local repository.
2. Double-click exactly:

```text
parallel\PYLAUNCH\RUN_WINDOWS_PROOF.cmd
```

3. In the Chrome/Edge window opened by the launcher, enter the normal WOF room exactly as usual. Do not open DevTools and do not paste JavaScript.
4. Confirm the tray reaches all six `OK` lines above and that the room remains normally playable.

### If it passes

Return only:

```text
PASS — PYLAUNCH WINDOWS PROOF
```

Then this file can be updated with the live PASS and a separate Alpha transport-integration handoff can be prepared. Do not modify Alpha in this stage.

### If it does not pass

Return only this one file:

```text
parallel\PYLAUNCH\WINDOWS_PROOF_STATUS.json
```

No DevTools output, Worker-console selection, pasted JavaScript, frame counting, gameplay capture, or memory collection is required.

## Stop condition reached

All repository-side work practical before a real Windows/Browser target is complete. The remaining uncertainty is specifically live Chromium target/session behavior plus owner confirmation that room playability is unaffected while attached.

# WOF-052L Automatic Multi-Room Event Recorder

Windows/Python research recorder for the PM-approved WOF-052L long-capture stage.

## Owner workflow

1. Double-click `RUN_WOF052L_RECORDER.cmd`.
2. On the first run only, choose the folder where capture JSON should be stored.
3. Use the Chrome/Edge window attached/launched by Recorder and open/close WOF rooms normally.
4. Do nothing per room. Supported `gstyphoon*.js` Workers are discovered and attached automatically after their WASM heap is live.
5. Leave Recorder running for minutes, hours, or overnight.
6. Press `Ctrl+C` when finished. Recorder finalizes every live room and writes the merged run JSON automatically.

The remembered output folder is stored in `%LOCALAPPDATA%\WOF052LRecorder\settings.json`.

To change it later:

```bat
RUN_WOF052L_RECORDER.cmd --reset-output
```

or:

```bat
RUN_WOF052L_RECORDER.cmd --output-dir D:\WOF_CAPTURE
```

## Browser/CDP behavior

Recorder first scans local Chrome/Edge CDP ports, preferring `9223` and `9222`.

- If a compatible debug browser is already running (for example a browser started by the existing Python Launcher), Recorder attaches to it.
- Otherwise Recorder launches a separate Chrome/Edge process with a persistent profile under `%LOCALAPPDATA%\WOF052LRecorder\BrowserProfile` and remote debugging enabled.
- Open WOF rooms in that browser window.
- Recorder never replaces `window.Worker`, never creates Blob Workers, and never rewrites Worker URLs.
- It attaches only after a real `gstyphoon*.js` Worker exists and its WASM/CPS RAM is ready.
- Failure to connect/attach is fail-open: the game/browser is not modified and Recorder keeps waiting/retrying.

Optional controls:

```bat
RUN_WOF052L_RECORDER.cmd --cdp-port 9223
RUN_WOF052L_RECORDER.cmd --browser edge
RUN_WOF052L_RECORDER.cmd --browser chrome
RUN_WOF052L_RECORDER.cmd --no-launch-browser
RUN_WOF052L_RECORDER.cmd --game-url https://example.invalid/your-wof-page
```

## Room lifecycle

Every supported Worker target owns an independent recorder state.

- New Worker: exact World 921031 identity is verified, then capture starts automatically.
- Room closed / refreshed / Worker recreated: only that Worker is finalized.
- Other rooms continue.
- A replacement Worker is a fresh room session and joins automatically.
- New rooms may join at any time.
- There is no one-hour or 120-second stop timer.
- Design is not capped at five rooms; practical limits are browser/PC resources.

Each room is accepted only after exact CPU-logical ROM SHA-256 matches:

`5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62`

which is the established `Warriors of Fate (World 921031)` identity.

## Stored data

Recorder does **not** save full per-frame RAM histories.

The Worker probe polls compact fields at 10 ms and stores counters plus event-level traces.

Mandatory WOF-052 target:

`T18 BODY4728/A4/B2/TM1 -> eventual A4704 vs A4712`

For candidate-containing T18 `attack=0 -> ACTIVE` cycles it preserves:

- ordered distinct pre-ACTIVE states;
- the exact candidate state indexes;
- eventual ACTIVE attack;
- target/side and retarget history, including target change at the ACTIVE edge;
- lead times;
- exact final / tail2 / tail3;
- timer-normalized `TM*` final / tail2 / tail3;
- transition-pair / transition-triple summaries grouped by eventual attack.

Secondary compact evidence:

- enemy type sample counts;
- `type|ACTIVE attack` frequency;
- other T18 zero->ACTIVE traces;
- T23 ordered zero->ACTIVE traces, including natural A5888 cycles;
- 0P/1P/2P/3P occupancy samples;
- target samples / retarget counts;
- bounded descriptor+attack edge examples;
- bounded enemy-type-set coverage as a scene/encounter coverage proxy.

All ordered discoveries are research evidence only. This tool does not promote Alpha/product rules.

## Files written

Under the configured output folder:

```text
rooms/
  <timestamp>_<room-id>.json

checkpoints/
  <run-id>_<room-id>.checkpoint.json

runs/
  <run-id>_merged.json
```

Room checkpoints are rewritten atomically while a room is live and removed after that room has a successful final JSON. If the Recorder or PC crashes, the last checkpoint remains on disk.

`runs/<run-id>_merged.json` is a rolling merged summary while Recorder is running and becomes the final merged summary on normal shutdown. It includes retained T18 candidate evidence across rooms, aggregate sequence summaries, room rollups, coverage and safety fields.

## CMD status

The console continuously reports:

```text
Browser OK | Live rooms 7 | Completed 12 | T18 samples 3456 | Candidate 8 | A4704 3 | A4712 5 | T23 4 | READ ONLY / RAM writes 0
```

## Safety contract

Hard invariants:

- `readOnly=true`
- `ramWrites=0`
- `inputInjection=false`
- no keyboard/controller injection
- no game speed changes
- no Worker replacement/interception
- no Alpha bootstrap dependency
- no `product/alpha/**` dependency
- no full-frame long-duration raw dump

The Python CDP client has an explicit method allowlist limited to target discovery/attach/detach and `Runtime.enable` / `Runtime.evaluate`.

## Self-test

Without opening a browser:

```bat
RUN_WOF052L_RECORDER.cmd --self-test
```

Expected:

```text
SELF-TEST PASS — WOF-052L recorder invariants and sequence aggregation
```

This validates sequence aggregation, atomic JSON writes, no fixed duration in the Worker probe, and the read-only CDP method boundary.

## Current proof boundary

Repository/local self-test can prove the implementation and safety invariants, but it cannot manufacture a live Windows WOF Worker.

The remaining live proof is minimal:

1. double-click `RUN_WOF052L_RECORDER.cmd`;
2. choose the output folder once (first run only);
3. open one or more WOF rooms in the attached/launched browser;
4. observe `Live rooms` rise automatically and JSON/checkpoints appear;
5. close/refresh one room and verify only that room moves to `Completed`;
6. press `Ctrl+C` and verify `runs/<run-id>_merged.json`.

No Worker-console selection, pasted JavaScript, per-room Start action, fixed one-hour run, or repeated 120-second collection is part of WOF-052L anymore.

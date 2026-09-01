# Runtime Speed Probe — Minimal Operator Steps

## Before starting

Have both runtimes at ordinary active gameplay, unpaused. P1 may simply stand still. Do not change emulator speed, VSync, audio, frameskip or Browser settings for this measurement.

Keep `wof-ai-private` and `wof-winkawaks-bridge` as sibling folders if possible. The probe can also take an explicit bridge path with `--bridge-root`.

## 1. Run one local command

From the `wof-ai-private` root:

```bat
python parallel\RUNTIMESPEED_PROBE\run_probe.py
```

The command automatically performs the WinKawaks read-only full-RAM capture for about 15 seconds.

Do not press movement/attack/jump during the measured interval. There is no need to count frames or watch a timer precisely.

## 2. Paste the prepared Browser line once

When the command says the Browser loader is ready:

1. Bring the Browser WOF game to active, unpaused gameplay.
2. Open DevTools Console.
3. Change the Console execution context to the existing **`gstyphoon` Worker**.
4. Press **Ctrl+V**, then **Enter** once.
5. Stop input. The Browser probe waits 3 seconds and then records about 15 seconds automatically.

The local command normally copied the exact one-line loader to the clipboard. If clipboard access failed, it prints the path of `parallel/RUNTIMESPEED_PROBE/out/browser_worker_loader.txt`; copy that single line instead.

The Browser script is read-only. It neither replaces the Worker nor injects game input. When the timed capture ends, it automatically sends the capture to the waiting process on `127.0.0.1` only.

## 3. Use the final JSON

No third command is required. The waiting local process automatically:

- finds common U8/U16 game heartbeat/frame-counter candidates;
- calculates WinKawaks game progression rate;
- calculates Browser game progression rate;
- calculates `WinKawaks / Browser` speed ratio;
- applies confidence/quality checks and decision thresholds.

Its final stdout is one result JSON, also saved at:

```text
parallel/RUNTIMESPEED_PROBE/out/runtime_speed_result.json
```

Raw paired captures are retained at approximately:

```text
parallel/RUNTIMESPEED_PROBE/out/local_speed_capture.wofsp.gz
parallel/RUNTIMESPEED_PROBE/out/browser_speed_capture.wofsp.gz
```

If Browser gzip compression is unavailable, the Browser capture may instead end in `.wofsp`.

## What not to do

Do not:

- count video frames;
- equate sample count with game frames;
- move around to create a special event;
- attack an enemy to trigger a known rule;
- change WinKawaks speed settings;
- change Browser rendering/audio settings;
- write game RAM or inject input.

The result JSON is the only artifact that needs interpretation after the paired measurement.
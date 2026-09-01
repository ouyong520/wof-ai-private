# WOF Runtime Speed Probe

Status: **support-only one-shot tooling ready for one paired owner measurement**  
Scope: `parallel/RUNTIMESPEED_PROBE/**` only

## Purpose

This closes the narrow measurement gap left by `parallel/RUNTIMESPEED/**`:

> compare actual autonomous WOF game-state progression per host second in WinKawaks and Browser.

It deliberately does **not** use Collector sample count as game frames. Each runtime records a monotonic host timestamp plus the complete normalized CPS work-RAM window `0xFF0000..0xFFFFFF`, and the offline analyzer finds a common in-game U8/U16 heartbeat/counter automatically.

## Safety boundary

The tooling is support-only and read-only:

- no game RAM writes;
- no input injection;
- no emulator speed/VSync/audio/frameskip changes;
- no `product/alpha/**` changes;
- no attack choreography and no video/manual frame counting.

Standing still in active, unpaused gameplay is enough.

## Recommended one-shot path

From the `wof-ai-private` repository root, with `wof-winkawaks-bridge` available beside it or passed through `--bridge-root`:

```bat
python parallel\RUNTIMESPEED_PROBE\run_probe.py
```

The command performs the WinKawaks capture first, then starts a loopback-only Browser handoff. It places the Browser one-line loader on the clipboard when possible.

For Browser, use the **existing `gstyphoon` Worker execution context** in DevTools Console, paste once, and press Enter. The Browser side waits three seconds, records about 15 seconds, sends the capture only to `127.0.0.1`, and the local command immediately performs the comparison.

Human work is therefore limited to:

1. start one local command;
2. paste one already-prepared line into the existing game Worker context.

No separate analyzer invocation or manual interpretation is required.

`run_probe.py` writes progress to stderr. Its stdout is reserved for the final result JSON.

## Measurement implementation

### WinKawaks

`local_capture.py` reuses the bridge's fresh immutable session discovery to obtain the current RAM base and host byte-lane mapping. During the timed window it performs one native 64 KiB `ReadProcessMemory` read per sample at a default target of 120 Hz and timestamps with `time.perf_counter()`.

To reduce measurement self-interference, byte-lane normalization and gzip compression happen **after** the timed capture, not inside every sample loop.

### Browser

`browser_capture.js` runs inside the already-existing WOF `gstyphoon` Worker. It reuses the proven Emscripten/WASM RAM access shape:

- find a Module exposing `HEAPU8` and `HEAPU32` on the same buffer;
- obtain the CPS RAM base through `HEAPU32[0x2e39e4 >>> 2]`;
- validate the live P1/P2/P3 WOF RAM structure;
- copy the raw 64 KiB host view at an 8 ms target interval;
- timestamp samples with `performance.now()`.

The timed loop only copies bytes and timestamps. Browser `xor-1` normalization, packaging and gzip happen after the timed interval.

The script does not wrap or replace the game Worker.

## Capture format

Both runtimes produce the same logical format, normally gzip-compressed as `.wofsp.gz`:

```text
8 bytes   magic: WOFSPC1\n
4 bytes   little-endian JSON header length
N bytes   UTF-8 JSON header
repeat:
  8 bytes     float64 little-endian elapsed milliseconds
  65536 bytes normalized logical CPS RAM 0xFF0000..0xFFFFFF
```

The header asserts the read-only/no-input contract and identifies runtime, clock, requested duration, sampling cadence, normalization and session metadata.

## Automatic analysis

`analyze.py` works from the paired captures only. It:

1. scans all logical CPS addresses as U8 and U16 candidates;
2. uses wrap-aware `+` and `-` progression;
3. ranks stable monotonic counters by coverage, regularity and step quality;
4. intersects the two runtimes by the **same logical CPS address, width and direction**;
5. requires agreement between multiple candidates when available;
6. computes each rate from accepted game-counter steps divided by elapsed monotonic wall-clock time;
7. computes `speedRatio = WinKawaks_rate / Browser_rate`;
8. if literal monotonic counters are absent, tries a conservative same-address periodic autonomous-heartbeat fallback from the **same captures**, so an empty first scan does not force another gameplay run.

The analyzer does not assume the two rates are equal while selecting the common candidate. Candidate ratios are clustered and a consensus ratio is reported.

## Decision bands

The primary decision follows the completed measurement plan:

- `abs(speedRatio - 1) <= 0.015` -> `SAME_SIMULATION_SPEED_DIFFERENT_FEEL`;
- 1.5% to 3% disagreement -> `INCONCLUSIVE_1_5_TO_3_PERCENT`;
- `speedRatio >= 1.03` with Browser near proven nominal cadence -> `WINKAWAKS_FASTER`;
- nominal CPS1 reference is approximately `59.6374 Hz`, and is used only when the selected heartbeat behaves like a once-per-frame counter.

The retained plan text also says `speedRatio <= 0.97` with WinKawaks nominal means `BROWSER_SLOWER`, but that prose conflicts with the plan's own definition `speedRatio = WinKawaks_rate / Browser_rate`: a ratio below one means Browser progression is faster than local progression. The analyzer preserves the numeric threshold but refuses to emit a directionally false label; it reports the measured direction and sets `planDirectionConflict: true` in that branch.

## Files

- `run_probe.py` — recommended paired one-shot orchestrator.
- `local_capture.py` — standalone WinKawaks 64 KiB capture.
- `browser_capture.js` — Browser Worker capture payload.
- `analyze.py` — standalone paired analyzer.
- `OPERATOR_STEPS.md` — minimal owner actions.
- `RESULT_SCHEMA.md` — final JSON contract.

Generated data is placed under `parallel/RUNTIMESPEED_PROBE/out/` by default.

## Tooling validation

Before publication, the analyzer/orchestrator support code was syntax-checked and exercised against synthetic full-RAM captures:

- synthetic 60 Hz local vs 60 Hz Browser -> `SAME_SIMULATION_SPEED_DIFFERENT_FEEL`;
- synthetic 63 Hz local vs 60 Hz Browser -> `WINKAWAKS_FASTER`.

Those are tooling tests only. They are **not** evidence about the owner's actual WinKawaks or Browser runtime. The real speed verdict must come from the one paired owner measurement.
# Runtime Speed / Timing Consistency Audit

Updated: 2026-09-01  
Evidence scope: retained GitHub data first; no new gameplay capture  
Write scope: `parallel/RUNTIMESPEED/**`

## 1. Separate the clocks

There are four different quantities that must not be conflated:

1. **Emulated-game / simulation cadence** — how fast WOF logic and CPS1 frame work advances relative to real time.
2. **WinKawaks Collector cadence** — how often the external Python process reads RAM.
3. **Browser validator cadence** — how often the Worker-side validator observes RAM and timestamps observations.
4. **Presentation / response latency** — input queue, emulation scheduling, audio buffering, VSync/compositor/display latency and frame pacing.

A game can have the same simulation cadence in two runtimes and still feel different because item 4 differs.

## 2. What WinKawaks Collector `hz` actually means

`bridge/collector_platform.py` implements burst timing with Python `time.perf_counter()`:

```text
interval_target = 1.0 / hz
start = time.perf_counter()
elapsedSeconds = time.perf_counter() - start
deadline = start + sequence * interval_target
time.sleep(deadline - time.perf_counter())
```

`achievedHz` is computed from the resulting host sample timestamps. PASS only verifies sample-count/timing health and that achieved sampling rate is at least 75% of target.

There is no binding to:

- emulator VBlank;
- emulated 68000 cycles;
- game frame interrupt;
- audio callback;
- display VSync;
- a WinKawaks internal speed percentage.

Therefore:

> `targetHz=60` / `achievedHz≈60` means approximately 60 **RAM reads per host second**, not “the game is running at 60 fps”.

The BASECAP catalog confirms many healthy captures around 59.94–60.00 samples/s, but this only validates acquisition pacing.

## 3. Can retained local raw recover simulation speed anyway?

Not defensibly from the current retained object-only corpus.

The canonical stream is only the contiguous P1/P2/P3 + 20 enemy objects (`23 * 0xE0 = 5152` bytes/sample), not the full 64 KiB CPS RAM. No field in that retained block has been proven to be a global once-per-VBlank monotonic frame counter.

The strongest tempting field, local enemy `+0x34`, is explicitly an executor dwell/countdown field rather than a global frame clock. Retained EFIELD evidence shows while a script cursor is stable it commonly decrements, but observed deltas include `-1`, `-2`, `-3`, holds and reloads. `+0x35` is a separate mode byte. Therefore neither `+0x34` nor Collector sequence can serve as an invariant simulation-frame counter.

`distinctRawFrameCount` is also insufficient: a changed 5152-byte RAM block proves some state changed between two samples, not that exactly one emulated frame elapsed.

Conclusion: retained WinKawaks data proves sampling quality, but **does not bind local wall-clock seconds to game frames**.

## 4. Browser lead-time methodology

The Browser prospective validators use `performance.now()` and interval polling. Representative production/shadow validators run approximately:

```text
start = performance.now()
setInterval(..., 10)
t = performance.now() - start
signal.at = t
leadMs = activeObservationTime - signal.at
```

So Browser `leadMs` means:

> elapsed Browser Worker monotonic wall-clock time between the poll that first observed the warning state/transition and the poll that first observed the ACTIVE edge.

It is not derived from emulated frame number or CPU cycle count.

The sampling-jitter validator explicitly treats observations up to +15 ms beyond a horizon as a separate 10 ms polling-jitter band instead of automatically widening the game horizon. Short lead values therefore have meaningful quantization uncertainty.

### Consequences

- A `~10–20 ms` lead is near the resolution floor of a 10 ms observer and should not be interpreted with sub-frame precision.
- `~60–120 ms` leads are substantially more informative, but still carry polling phase/jitter.
- `~380–640 ms` leads are not materially explained by 10 ms sampling quantization.

## 5. Browser speed sanity check from retained production observations

The strongest current production examples include:

- T18 `BODY7512 / timer34=4 -> A5440`: `62.3..70.9 ms`.
- T18 `BODY7520 / timer34=4 -> A5424`: `69.1..70.0 ms`.
- D867BA `timer34=6 -> A3232`: `99.1..109.4 ms`.
- D8811E `timer34=6 -> A3232`: `98.6..119.2 ms`.
- T16 `timer34=1` imminent-danger state: `8.9..21.0 ms`.

These timer values are object-executor state, not a universal frame counter, so this is a **sanity check only**. Nevertheless, the observed scales are strongly consistent with roughly 16.7 ms game ticks: four ticks are about 66.7 ms and six ticks about 100 ms, with the expected additional 10 ms polling phase/jitter.

The CPS1 hardware cadence is also independently near 60 Hz. Current MAME CPS1 video raw parameters use an 8 MHz pixel clock, 512 clocks/scanline and 262 scanlines/frame, giving approximately `8,000,000 / (512*262) = 59.6374 Hz` (source: `mamedev/mame`, `src/mame/capcom/cps1.h`).

This does **not** prove the Browser implementation is exactly 59.6374 Hz under every host condition, but retained Browser production data contains no sign of a large global slowdown that would explain a clearly faster-feeling WinKawaks session.

## 6. Why subjective WinKawaks speed can still differ

Current GitHub telemetry does not timestamp the complete path from physical input to rendered photon/audio output, so the audit cannot uniquely assign the subjective difference to one of VSync, compositor buffering, audio synchronization, or keyboard/input queueing.

All remain plausible presentation-path contributors. For example, two emulators can advance game RAM at the same average cadence while one:

- queues an extra rendered frame;
- waits differently for VSync;
- has a deeper audio buffer and schedules emulation around it;
- samples host input at a different point in the emulation frame;
- presents uneven frame pacing despite the same average simulation rate.

Those mechanisms alter responsiveness/feel without necessarily changing RAM-state-to-RAM-state game timing.

No retained timestamped input-to-RAM or RAM-to-present dataset exists, so choosing one of these mechanisms now would be speculation.

## 7. Can WinKawaks timing be directly compared to Browser milliseconds?

**No, not currently.**

Both use monotonic host clocks, but they timestamp different observation systems:

- WinKawaks: external Python RAM reads paced by `perf_counter()`.
- Browser: Worker RAM observations paced by `setInterval`, timestamped by `performance.now()`.

A numerical comparison becomes valid only after both conditions are satisfied:

1. local and Browser simulation cadence are calibrated against the same in-game monotonic progression; and
2. the compared start/end events have the same game semantic meaning.

Until then, statements such as “local state X lasted 70 ms, therefore Browser warning lead should be 70 ms” are not valid.

Frame/sample counts are even less portable: one Collector sample is not proven to equal one game frame.

## 8. Alpha release timing labels

No Alpha timing-label change is warranted.

The RC3 manifest/core labels are summaries of prospective measurements made in the Browser production runtime lineage, now positively bound to `wof / World 921031` with full CPU-logical SHA-256 `5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62`.

The two currently active RC3 rules are current-level predicates; they do not use WinKawaks elapsed time to arm or age production watches. Their displayed `validatedLeadLabel` values are Browser evidence labels, not cross-emulator constants.

Therefore a possible WinKawaks speed difference does not invalidate those Browser-specific labels.

## 9. ROM revision

Browser revision is positively identified as World 921031. The retained WinKawaks Collector metadata is not a cryptographic ROM-identity measurement, so local revision must not be inferred from Collector captures.

However, **no current evidence implicates ROM revision as the cause of the global subjective speed difference**. CPS1 video timing is hardware/platform timing shared by these revisions; a revision can alter game logic details, but it should not be used as the default explanation for a whole-runtime faster/slower feel without measurement.

## 10. Audit boundary

The only material missing fact is:

> How many units of the same autonomous in-game progression occur per host second in WinKawaks versus Browser?

That is reduced to the one read-only test in `MEASUREMENT_PLAN.md`. No broad recapture, product modification, WOF-052 work or Collector behavior change is justified before that result.

# Runtime Speed / Timing Verdict

Updated: 2026-09-01

## Required verdict

# **INSUFFICIENT — ONE MINIMAL TEST REQUIRED**

This is a narrow insufficiency, not an open-ended research state.

The missing datum is only the WinKawaks **emulated-game progression per host second**. Existing Collector timing cannot supply it because Collector `hz` is external RAM-read cadence.

## What the retained evidence already says

### Browser is not currently shown to be globally slow

Browser lead measurements are Worker wall-clock observations using `performance.now()` with approximately 10 ms polling. Existing T18 `timer34=4` leads around 62–71 ms and `timer34=6` A3232 leads around 99–119 ms are consistent with roughly nominal CPS1-scale game timing once polling phase/jitter is considered.

This is strong evidence against a large Browser slowdown, although it is not a formal frame-rate measurement.

### WinKawaks `~60 Hz` does not prove normal game speed

BASECAP/EFIELD captures around 60 samples/s prove that the Python Collector can read RAM on that schedule. The Collector is not synchronized to VBlank, game frames, emulated CPU cycles, audio callbacks or WinKawaks speed control.

Therefore the subjective report “WinKawaks feels faster” has two live explanations after this audit:

1. WinKawaks really is advancing simulation faster than Browser/nominal; or
2. both simulations are effectively the same speed, while WinKawaks has lower/different input/render/audio/VSync latency or frame pacing and therefore feels faster.

Current retained data favors explanation 2 over a large Browser slowdown, but cannot exclude explanation 1 without measuring local game progression.

## Direct numeric comparability

**Can WinKawaks discovery timing be directly compared to Browser lead milliseconds? — NO.**

Do not equate:

- Collector sample count with game frames;
- Collector `elapsedSeconds` intervals with Browser attack-warning lead;
- a local object's dwell time with a Browser production horizon unless the same semantic event and simulation-speed calibration are both established.

After a common in-game counter/heartbeat calibration, cross-runtime wall-clock intervals may be normalized and compared. Until then, keep local timing as local discovery evidence and Browser milliseconds as Browser production evidence.

## Alpha timing labels

**Do Alpha release timing labels need change? — NO.**

The RC3 active labels (`~62–71 ms`, `~69–70 ms`) are summaries of prospective Browser evidence on the positively identified `wof / World 921031` runtime. RC3 production rules are current-level predicates and do not consume WinKawaks elapsed time.

A faster or slower WinKawaks instance therefore does not invalidate those Browser-specific labels.

No file under `product/alpha/**` was modified by this audit.

## ROM revision

**Is ROM revision implicated? — NO CURRENT EVIDENCE.**

Browser is positively bound to:

```text
wof / Warriors of Fate (World 921031)
SHA-256 5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62
```

The local Collector does not itself prove local ROM identity. That is an identity metadata gap, but it is not evidence that revision explains a global faster/slower feel. CPS1 platform video cadence is common hardware timing; revision should not be blamed without a measured logic-timing difference.

## Remaining action

Exactly one operator measurement remains, specified in `MEASUREMENT_PLAN.md`:

> 15 seconds of stable no-input, read-only full CPS RAM timing in WinKawaks and 15 seconds in Browser, followed by automatic discovery/comparison of a common monotonic in-game counter/heartbeat against host wall clock.

No combat choreography, no broad recapture, no video frame counting.

### Automatic final classification after that one test

- equal calibrated progression -> **SAME SIMULATION SPEED / DIFFERENT FEEL**;
- local materially faster with Browser nominal -> **WINKAWAKS FASTER**;
- Browser materially slower with local nominal -> **BROWSER SLOWER**;
- both materially off a proven nominal frame heartbeat -> **BOTH DEVIATE**.

Until that single measurement exists, emulator/VSync/audio/input tuning would be premature.

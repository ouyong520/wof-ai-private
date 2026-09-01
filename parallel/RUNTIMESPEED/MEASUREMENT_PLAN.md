# Runtime Speed Minimal Measurement Plan

Updated: 2026-09-01  
Status: **ONE TEST ONLY — no broad collection**

## Purpose

Resolve the only remaining timing ambiguity:

> Does WinKawaks advance WOF game simulation materially faster per wall-clock second than the Browser runtime?

This is not an attack study and does not require combat choreography.

## One operator test

Perform one paired, read-only **15-second stable no-input capture per runtime**:

- WinKawaks: 15 s.
- Browser/WASM: 15 s.
- Same practical game condition if possible: active gameplay, unpaused, P1 standing still, no directional/attack/jump input, no need for enemies to attack.

Human work is only starting the measurement in each runtime. Do not manually count video frames.

## What to record

For each runtime, record:

1. monotonic host timestamp for every sample;
2. the full normalized CPS RAM 64 KiB window (`0xFF0000..0xFFFFFF`) read-only;
3. sampling target above nominal frame rate, preferably 120 Hz locally and a 5–8 ms Browser poll where practical.

Why full 64 KiB: the retained BASECAP stream only has the 5152-byte actor block and may omit a global software frame/heartbeat counter.

Do not change game RAM and do not inject game input.

## Automatic analysis

The analysis must discover a counter/heartbeat from the same capture; no second run should be required.

For every U8/U16 candidate address, use wrap-aware deltas and rank fields that show:

- repeated monotonic `+1` or `-1` progression;
- regular steps through most of the 15-second run;
- no dependence on player movement/combat;
- stable address and width;
- preferably the same CPS address and same progression signature in both runtimes.

A once-per-frame counter near CPS1 cadence should produce about 895 steps in 15 seconds at 59.6374 Hz. A divided heartbeat is still usable if its divisor/progression is stable and identical across runtimes.

If more than one candidate qualifies, compare several and require agreement. If no literal monotonic counter qualifies, the already-retained full-RAM samples from this same test may be analyzed offline for a periodic autonomous heartbeat; do not ask for another capture merely because the first candidate scan is empty.

## Calculation

For a selected common counter:

```text
rate = wrap_aware_counter_steps / measured_wall_clock_seconds
speed_ratio = WinKawaks_rate / Browser_rate
```

Use elapsed monotonic time between the first and last accepted step, not requested duration and not sample count.

Nominal CPS1 reference, only when the counter is shown to advance once per video/game frame:

```text
8 MHz / (512 * 262) ~= 59.6374 Hz
```

## Decision rules

Primary decision is the cross-runtime ratio; nominal CPS1 rate is a secondary sanity check.

- `abs(speed_ratio - 1) <= 0.015` with stable counters: **SAME SIMULATION SPEED / DIFFERENT FEEL**.
- `speed_ratio >= 1.03`, with Browser near nominal/stable: **WINKAWAKS FASTER**.
- `speed_ratio <= 0.97`, with WinKawaks near nominal/stable: **BROWSER SLOWER**.
- both clearly depart from a proven nominal once-per-frame counter: **BOTH DEVIATE**.
- 1.5–3% disagreement or unstable counter: preserve exact measured rates and do not guess; inspect measurement quality before any emulator tuning.

The gap between 1.5% and 3% is intentionally conservative so scheduler noise or a misclassified divided counter is not promoted into a speed defect.

## What this test does and does not settle

It directly settles **simulation speed**. If the result is SAME SIMULATION SPEED while the subjective feel still differs, then the remaining cause is in presentation/input responsiveness rather than game-state progression.

This one test does not need to distinguish VSync from compositor buffering from audio buffering from input queueing, because those mechanisms do not change the Browser RAM-state lead evidence used by Alpha. A separate latency optimization study would only be justified if product responsiveness becomes a release problem; that is outside this audit.

## No-extra-work rule

Do not:

- recapture BASECAP gameplay;
- reproduce WOF-038..052 attacks;
- modify `product/alpha/**`;
- alter Collector timing before a measured defect exists;
- tune WinKawaks/Browser VSync, audio or frameskip merely by feel.

One paired 15-second read-only capture is the entire unresolved operator requirement.

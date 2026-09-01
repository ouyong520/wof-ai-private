# WOF Runtime Speed / Timing Audit

Updated: 2026-09-01  
Lane: `parallel/RUNTIMESPEED/**` only  
Status: **AUDIT COMPLETE TO ONE MINIMAL MEASUREMENT**

## Official current verdict

**INSUFFICIENT — ONE MINIMAL TEST REQUIRED**

The retained evidence is enough to settle the measurement semantics, but not enough to prove the WinKawaks emulated-game speed itself.

What is already established:

- WinKawaks Collector `hz` is **host wall-clock RAM sampling frequency**, not emulated frame rate.
- Browser WOF lead values are **Browser Worker monotonic wall-clock milliseconds** between observed RAM states, normally sampled every 10 ms; they are not game-frame counts.
- Existing Browser production timings are consistent with nominal CPS1 cadence and do not show evidence that the Browser runtime is globally running conspicuously slow.
- Retained WinKawaks object raws do not contain a proven global monotonic frame/VBlank counter, so `sequence` or `elapsedSeconds` cannot prove WinKawaks is at 100% emulation speed.
- WinKawaks wall-clock discovery timings therefore must **not** be numerically substituted for Browser lead milliseconds without a simulation-speed calibration and same-semantic-event binding.
- Browser Alpha timing labels remain Browser-specific validated labels and require **no change** from this audit.
- Browser identity remains `wof / Warriors of Fate (World 921031)`, full CPU-logical SHA-256 `5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62`.
- No retained evidence implicates ROM revision as the cause of the subjective speed difference.

## Files

- `AUDIT.md` — evidence and timing-model audit.
- `MEASUREMENT_PLAN.md` — exactly one bounded read-only operator test, if a categorical simulation-speed verdict is required.
- `VERDICT.md` — release-facing conclusion and comparability decision.

## Scope guard

This lane does not modify `product/alpha/**`, does not restart WOF-052, does not change Collector behavior, and does not request broad gameplay collection.

# WOF RUNTIME SPEED PROBE TOOLING — START PROMPT

You own a bounded tooling stage that consumes the completed `parallel/RUNTIMESPEED/**` audit.

Repositories:
- `ouyong520/wof-ai-private`
- `ouyong520/wof-winkawaks-bridge`

## Goal

Turn the existing timing measurement plan into the smallest practical one-shot tooling so the owner does not need to manually count frames or assemble data.

Read first:
- `parallel/RUNTIMESPEED/VERDICT.md`
- `parallel/RUNTIMESPEED/MEASUREMENT_PLAN.md`
- `parallel/RUNTIMESPEED/AUDIT.md`
- current bridge Collector/runtime-discovery implementation
- Browser Worker RAM access patterns already proven in the project

## Write boundary

Write only under:
- `parallel/RUNTIMESPEED_PROBE/**`

Do NOT modify:
- `product/alpha/**`
- Collector production behavior unless absolutely necessary; prefer support-only scripts
- existing RUNTIMESPEED verdict files

## Required tooling

Prepare support-only tools for one paired measurement:

1. WinKawaks: one command that records ~15 seconds of full normalized CPS RAM plus monotonic host timestamps read-only.
2. Browser: one-line loader/JS that records ~15 seconds of the same normalized CPS RAM window plus `performance.now()` timestamps read-only.
3. Offline analyzer that automatically searches both captures for common monotonic U8/U16 heartbeat/frame-counter candidates and calculates:
   - local rate;
   - Browser rate;
   - local/Browser speed ratio;
   - confidence/quality diagnostics;
   - verdict using the thresholds in `MEASUREMENT_PLAN.md`.
4. One compact result JSON the owner can paste back.

No gameplay choreography: standing still is enough.
No RAM writes. No input injection. No video/manual frame counting.

If the bridge already exposes a safe way to obtain the full 64 KiB CPS window, reuse it. Otherwise create a support-only local script rather than changing production Collector semantics.

## Required outputs

Create:
- `parallel/RUNTIMESPEED_PROBE/README.md`
- local capture script
- Browser capture JS
- analyzer script
- `OPERATOR_STEPS.md`
- `RESULT_SCHEMA.md`

Prefer one command for local + one one-line Browser loader + one analyzer command, or fewer if automation can safely combine them.

## Stop condition

Stop when the remaining simulation-speed question can be answered from one paired owner measurement with no manual interpretation.

Do not tune WinKawaks, VSync, audio, frameskip or Browser settings in this tooling stage.
# WOF RUNTIME SPEED / TIMING CONSISTENCY AUDIT — START PROMPT

You own a bounded support audit for the WOF / Warriors of Fate / 三国志II project.

Repositories:
- `ouyong520/wof-ai-private`
- `ouyong520/wof-winkawaks-bridge`

## Question

The owner reports that local WinKawaks gameplay feels noticeably faster than the online Browser/WASM game.

Your job is to determine whether this comes from:
- WinKawaks running above nominal emulation speed;
- Browser/WASM running below nominal speed;
- frame pacing / VSync / audio synchronization differences;
- input/render latency that only feels slower;
- or a real game/revision timing difference.

Do not assume ROM revision is the cause.

## Read first

Read current GitHub state relevant to timing and runtime:
- `WINKAWAKS_SINGLE_OPERATOR_SWEEP_GUIDE.md`
- `parallel/BASECAP/BASE_CAPTURE_CATALOG.md`
- `parallel/COVERAGE/**` summaries if relevant
- `parallel/PM/RUNTIME_IDENTITY_CORRECTION.md`
- `parallel/PM/WORLD_921031_BROWSER_IDENTITY_RESULT.md` if present
- Browser WOF-038..WOF-052 timing/production-shadow summaries
- bridge Collector timing implementation and result metadata under `results/by_task/**`

The Browser lineage is now positively bound to:
- `wof / Warriors of Fate (World 921031)`
- full 1 MiB CPU-logical SHA-256 `5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62`

Do not revert to the old `wofr1 / World 921002` label.

## Scope

This is a timing audit, not product development.

Do NOT modify `product/alpha/**`.
Do NOT restart WOF-052.
Do NOT perform broad gameplay collection.
Do NOT change Collector behavior unless the audit proves a concrete measurement defect and documents it first.

Write only under:
- `parallel/RUNTIMESPEED/**`

## Required analysis

1. Determine what the current WinKawaks Collector `hz` means:
   - wall-clock sampling frequency only, or
   - actual emulated-game frame rate.

2. Search retained data for any reliable wall-clock vs in-game-frame/counter signal that can estimate emulation speed without new capture.

3. Inspect Browser timing methodology used for lead-time claims and determine whether those milliseconds are Browser wall-clock based, game-frame based, or mixed.

4. Decide whether existing Browser Alpha lead-time labels remain valid even if WinKawaks runs faster/slower.

5. If retained evidence is insufficient, reduce the problem to ONE minimal operator test, preferably:
   - 10–20 seconds per runtime;
   - no combat choreography;
   - read-only;
   - compare the same monotonic in-game counter/frame progression against wall-clock time;
   - no manual counting from video if a direct counter exists.

6. Separately distinguish:
   - actual game simulation speed difference;
   - frame presentation pacing;
   - input latency / responsiveness.

## Required outputs

Create:
- `parallel/RUNTIMESPEED/README.md`
- `parallel/RUNTIMESPEED/AUDIT.md`
- `parallel/RUNTIMESPEED/MEASUREMENT_PLAN.md`
- `parallel/RUNTIMESPEED/VERDICT.md`

The verdict must say clearly one of:
- SAME SIMULATION SPEED / DIFFERENT FEEL
- WINKAWAKS FASTER
- BROWSER SLOWER
- BOTH DEVIATE
- INSUFFICIENT — ONE MINIMAL TEST REQUIRED

Also state:
- whether local WinKawaks discovery timing can be compared numerically to Browser milliseconds;
- whether Alpha release timing labels need any change;
- whether ROM revision is implicated or not.

## Stop condition

Stop when either:
A. retained evidence is enough for a defensible verdict; or
B. exactly one minimal human timing test is specified.

Do not ask the owner to choose technical methods. Do not broaden into performance optimization or emulator configuration tuning unless a measured speed defect is proven.

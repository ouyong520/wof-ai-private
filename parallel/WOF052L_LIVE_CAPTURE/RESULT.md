# WOF-052L Multi-Room Live Capture — Result

Updated: 2026-09-01

Verdict: **READY FOR 10-ROOM LONG CAPTURE**

This verdict means the repository-side launch/capture/analysis path is ready for the real Windows long capture. It does **not** claim that the future 10-room long capture dataset has already been collected.

## Final owner entry

Double-click:

`parallel/WOF052L_LIVE_CAPTURE/RUN_10_ROOM_LONG_CAPTURE.cmd`

Normal owner flow:

```text
double-click CMD
-> first run only: choose JSON save folder
-> enter 1 / 5 / 10 (default 10)
-> isolated Browser Fleet launches
-> WOF-052L Recorder workers start automatically
-> WOF-052L Analysis watch starts automatically
-> owner enters WOF normally in the browser windows
-> capture begins automatically when each room passes Recorder admission
```

There is no per-room Start button and no required DevTools, Worker Console, pasted JavaScript, manual RAM inspection, or injected gameplay input.

## Worker discovery blocker status

The old blocker was real: browser-level `Target.getTargets` plus a strict `type=worker + gstyphoon*.js` prefilter could miss the native WOF Worker even when the page/game was healthy.

That repository-side blocker is now closed for WOF-052L:

- `parallel/WOF052L_RECORDER/discovery_v2_sync.py` implements page-session `Target.setAutoAttach`;
- related `iframe / worker / shared_worker / service_worker` topology is traversed;
- direct Worker discovery remains a compatibility fallback;
- WASM/heap readiness is checked before capture;
- exact World 921031 SHA-256 is required;
- wrong identity is rejected;
- multiple supported Workers for one page are rejected as ambiguous;
- reload/replacement/CDP failure cannot inherit an old room state;
- discovery is read-only and does not use gameplay input methods.

The default Recorder Windows CMD now routes through `owner_v2_zh_cn.py`, and the long-capture entry independently calls `discovery_v2_sync.install(recorder)` before constructing Fleet Recorder children. This prevents the long-capture route from accidentally falling back to the old Worker discovery behavior.

## Multi-room orchestration

The long-capture entry composes the existing components rather than replacing them:

- Browser Fleet creates independent profile + localhost CDP endpoint per numbered instance;
- Fleet manifest remains the shared endpoint registry;
- `FleetSupervisor` creates one independent `RecorderManager` child per Fleet endpoint;
- a failed/disconnected endpoint does not stop other children;
- Worker close/reload/CDP failure finalizes only its room;
- new eligible Workers can be discovered while the supervisor continues;
- per-room JSON, checkpoints, child merged JSON and fleet merged JSON remain automatic.

## No-waste preflight

Before launching a long capture, `live_capture.py` verifies the Recorder runtime has:

- the exact current World 921031 SHA-256 gate;
- `Target.setAutoAttach` enabled in the read-only allowlist;
- Discovery V2 installed;
- no `Input.*` CDP method;
- no `Runtime.callFunctionOn`;
- no `Page.addScriptToEvaluateOnNewDocument`.

If any condition fails, the entry exits before starting the long capture and reports a Chinese blocker instead of allowing a one-hour run with zero usable Worker evidence.

## Owner-visible live status

The combined CMD continuously aggregates:

- online browser instances;
- currently capturing rooms;
- completed rooms;
- T18 samples;
- candidate cycles;
- A4704 count;
- A4712 count;
- T23 cycles;
- READ ONLY state;
- RAM writes 0.

Browser Fleet Worker status remains a cheap indicator only. Actual capture admission is authoritative only after Recorder Discovery V2 reaches Worker + WASM/heap + exact World 921031.

## Automatic analysis

The entry self-checks `parallel/WOF052L_ANALYSIS/analyzer.py` and, when healthy, starts:

`analyzer.py <capture-folder> --watch --interval 5`

It automatically refreshes:

- `analysis/analysis.json`
- `analysis/分析结果.txt`

On Ctrl+C the recorder children finalize, the fleet merged index is written, the watch process stops, and one final analysis pass runs.

## Regression / audit evidence

Repository-side Recorder Discovery V2 regression covers:

- direct Worker compatibility;
- page-attached Worker;
- iframe -> Worker;
- Worker URL-shape variation;
- wrong World identity;
- WASM not ready;
- ambiguous multiple Workers;
- Worker replacement/reload;
- ten endpoint isolation;
- read-only installation without input/write methods.

The long-capture integration adds checks for:

- default/allowed room counts;
- aggregate status parsing;
- old discovery path rejected by preflight;
- forbidden input CDP method rejected;
- safe auto-attach Discovery V2 accepted.

## Safety boundary

Preserved end-to-end:

- `readOnly=true`;
- `ramWrites=0`;
- `inputInjection=false`;
- no `window.Worker` replacement/wrapping;
- no Blob/Data/ObjectURL Worker rewrite;
- no game-speed control;
- no attack automation;
- no `product/alpha/**` modification in this lane.

## Remaining human action

There is no known repository-side blocker remaining before the requested long capture.

The next step is the capture itself:

1. double-click `parallel/WOF052L_LIVE_CAPTURE/RUN_10_ROOM_LONG_CAPTURE.cmd`;
2. accept the default `10` unless a smaller proof is intentionally desired;
3. enter WOF normally in the browser windows;
4. leave the combined CMD running for the desired long-capture period;
5. press `Ctrl+C` once when finished so final merged JSON and final analysis are written.

**Stop condition reached: READY FOR 10-ROOM LONG CAPTURE.**

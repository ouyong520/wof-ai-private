# WOF-052L Automatic Multi-Room Recorder — Implementation Result

## Verdict

**READY FOR FRESH WINDOWS/BROWSER LIVE PROOF**

The PM-revised WOF-052L workflow is implemented as a standalone Windows CMD/Python recorder. No `product/alpha/**` or `parallel/PYLAUNCH/**` file is modified.

## Implemented

- one-time remembered output directory;
- one double-click CMD entry point;
- automatic Chrome/Edge CDP discovery;
- optional safe dedicated debug-browser launch when no CDP endpoint exists;
- automatic discovery of any number of `gstyphoon*.js` Worker targets;
- post-start module readiness check;
- exact World 921031 SHA-256 gate before capture;
- independent persistent CDP session / capture state per Worker;
- room close/reload/disconnect finalizes only that Worker;
- new Workers can join at any time;
- no fixed duration;
- 10 ms event-state sampling inside each supported Worker;
- 1 s event drain to Python;
- atomic 10 s per-room checkpoint;
- automatic per-room final JSON;
- rolling merged run JSON;
- final merged JSON on `Ctrl+C`;
- live CMD counters for rooms, T18, candidate, A4704, A4712, T23 and safety.

## WOF-052 mandatory evidence

The recorder specifically preserves candidate-containing:

`T18 S0/A4/B2 | BODY4728 | FE8b660 | NX8b204 | Vffff | TM1 | P6C4736`

zero->ACTIVE cycles and groups them by eventual ACTIVE attack.

Per-room and merged outputs compute:

- exact final/tail2/tail3;
- timer-normalized `TM*` final/tail2/tail3;
- ordered transition pairs;
- ordered transition triples;
- candidate first/last lead;
- target/side stability;
- retargets including active-edge retarget.

The implementation does not infer/promote a discriminator. WOF-051 remains authoritative that the single candidate state is ambiguous until enough ordered A4704 and A4712 evidence is collected.

## Secondary evidence

Bounded compact collection also retains:

- type sample frequency;
- type/ACTIVE-attack frequency;
- other T18 cycles;
- T23 cycles and natural A5888 cycles;
- player occupancy;
- target samples and retarget counts;
- descriptor/attack edge examples;
- enemy-type-set encounter/scene proxy coverage.

No long-duration full raw frames are stored.

## Safety

Static/runtime self-test passes with:

- read-only CDP allowlist only;
- `ramWrites=0`;
- no input CDP methods;
- no Worker replacement/Blob URL rewrite;
- no fixed-duration loop;
- no Alpha dependency.

Local self-test command:

`python recorder.py --self-test`

Result:

`SELF-TEST PASS — WOF-052L recorder invariants and sequence aggregation`

## Remaining live gate

A real Windows browser/WOF Worker is required only to prove the external environment:

- Browser endpoint is reachable;
- multiple real room Workers surface in CDP;
- exact SHA gate passes;
- files appear in the selected Windows directory;
- closing/reloading one room leaves other room captures running.

Owner operation is now reduced to:

**choose save folder once -> double-click one CMD -> open/close WOF rooms -> JSON appears automatically.**

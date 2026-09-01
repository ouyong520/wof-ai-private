# WOF-052L — Automatic Multi-Room Event Recorder Tooling Stage

You own a fresh independent research-tooling stage.

Repository:
- `ouyong520/wof-ai-private`

Read first:
- `parallel/PM/WOF_052_LONG_CAPTURE_PM_REVIEW.md`
- `parallel/PM/WOF_052_LONG_CAPTURE_DECISION.md`
- `reports/WOF-052_ANALYSIS.md`
- current WOF-052 coordinator/tracer code and relevant WOF-051 evidence
- read-only reference to `parallel/PYLAUNCH/**` for the safe post-start CDP discovery approach

## Revised PM decision

Do **not** implement WOF-052L as one fixed one-hour capture.

Build it as a small always-on **automatic multi-room recorder**. A simple Windows CMD/console UI is acceptable and preferred for the first working version; do not spend time on polished UI before collection is proven.

## Owner UX target

The owner should configure one output directory once, then start the recorder once.

After that:

1. owner may open 1, 5, 10 or more normal WOF Browser rooms/tabs, subject only to machine/browser resource limits;
2. every newly detected supported WOF room / `gstyphoon*.js` Worker starts its own read-only capture automatically;
3. no per-room Start button;
4. no Worker-console selection;
5. no pasted JavaScript per room;
6. closing/reloading/disconnecting one room finalizes/checkpoints only that room and must not interrupt any other room;
7. newly opened rooms may join at any time and begin capture automatically;
8. there is no fixed one-hour deadline — collection continues until that room closes or the recorder itself is stopped;
9. all output is written automatically to the configured directory;
10. when the recorder exits, finalize all still-live room summaries and write one merged run summary.

The first version may simply run in a CMD window and display live status such as:

```text
WOF Capture Recorder
Save folder: D:\WOF_CAPTURE
Browser: OK
Live rooms: 7
Completed rooms: 12
T18 samples: 3456
T18 candidate cycles: 8
A4704 candidate cycles: 3
A4712 candidate cycles: 5
READ ONLY / RAM writes: 0
```

## Output-directory behavior

Provide one easy mechanism such as:

- first-run prompt for an output folder and remember it in a local settings JSON; and/or
- `--output-dir <folder>` command-line option.

Once configured, the owner should not need to choose a save location again on each run.

Prefer direct filesystem writes from the Python recorder over browser download prompts.

Suggested outputs:

- `rooms/<timestamp>_<room-id>.json` when an individual room finalizes;
- `checkpoints/...` for compact crash/reload recovery state;
- `runs/<run-id>_merged.json` rolling/merged session summary;
- final merged JSON on recorder shutdown.

Use safe/portable filenames and create directories automatically.

## Primary unresolved research target

The mandatory WOF-052 target remains the T18 ordered-sequence ambiguity:

`BODY4728/A4/B2/TM1 -> eventual A4704 vs A4712`.

The previous valid five-room batch had zero T18 coverage. The new recorder must maximize natural room/time coverage without manual attack hunting.

For T18 retain compact event-level evidence for:
- zero->ACTIVE cycle boundaries;
- exact BODY4728/A4/B2/TM1 candidate occurrences;
- ordered distinct states after the candidate;
- eventual ACTIVE attack, especially A4704 vs A4712;
- exact/TM* final, tail2, tail3, transition pair/triple summaries;
- target/side/retarget metadata;
- room/session/build identity sufficient to compare evidence across rooms.

## Other useful data to retain opportunistically

T18 is the only current **mandatory missing discriminator evidence** for WOF-052, but a long multi-room recorder should cheaply preserve other high-value event summaries when available rather than throw them away.

Without becoming a full RAM dump, retain bounded compact coverage for:
- all observed enemy type / ACTIVE attack frequency;
- other T18 outcomes and descriptors;
- prior T23 ordered-sequence opportunities, including the known A5888 branch/tail target when naturally observed;
- player occupancy (1P/2P/3P), target distribution, retarget counts and room duration;
- rare/unusual descriptor + attack combinations useful for later triage;
- scene/type coverage indicators needed to explain what was or was not observed.

These secondary records are research/coverage evidence only and must not automatically promote product rules.

## Preferred implementation form

Prefer a small Windows/Python recorder using supported Chrome/Edge CDP post-start attachment.

Reason:
- it can discover many already-running WOF page/Worker targets automatically;
- it avoids replacing/wrapping `window.Worker`;
- it can write JSON directly to the chosen disk folder;
- room close/reload can be handled independently;
- later it can be packaged into a one-click EXE or folded into the main WOF Launcher.

A Tampermonkey helper may be used only for harmless optional UX if truly useful. Do **not** restore the old Worker replacement / Blob Worker interception pattern that previously blocked room entry.

## Multi-room isolation requirements

Each live room/Worker must have independent:
- room/session ID;
- CDP target / Worker identity;
- capture state machine;
- counters;
- T18 cycle state;
- bounded traces;
- checkpoint;
- lifecycle/finalization state.

One room crash/close/reload must never clear, corrupt or stop another room's recorder state.

If a Worker is recreated on reload/room transition, finalize/invalidate the stale Worker state and attach a fresh capture session safely.

Design for at least 10 simultaneous rooms if the Browser/PC can sustain them, but fail gracefully if host resources are exhausted.

## Storage / size policy

Do not save every frame or full RAM snapshots for hours.

Ordinary polls contribute counters/context only. Persist detailed ordered traces only for selected event cycles.

Use:
- bounded trace counts;
- bounded states per trace;
- top-N / capped summary maps;
- compact periodic checkpoints;
- per-room finalization;
- merged aggregates.

The output must remain practical to upload/analyze even after many rooms and many hours.

## Safety boundaries

Must remain:
- `readOnly=true`;
- `ramWrites=0`;
- no keyboard/controller/gameplay input injection;
- no game speed changes;
- no startup/Worker interception that can break room entry;
- no dependence on Alpha bootstrap;
- no `product/alpha/**` changes;
- no full-frame long-duration raw dump;
- no Beta features;
- ordered discoveries remain research-only until later prospective validation.

## Stop condition

Stop when either:

A. the automatic multi-room CMD recorder is READY and owner operation is reduced to: configure/save folder once -> run one command/tool -> open/close WOF rooms normally -> JSON files appear automatically; or

B. one precise Browser/CDP limitation blocks automatic multi-room discovery/capture; or

C. after owner collection, merged evidence is analyzed and the T18 A4704-vs-A4712 discriminator verdict is recorded.

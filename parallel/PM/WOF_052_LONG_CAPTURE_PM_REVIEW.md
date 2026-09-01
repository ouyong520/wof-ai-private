# WOF-052 Long Capture — PM Review Request

Updated: 2026-09-01

## Why this review is requested

The bounded WOF-052 evening batch has completed and was analyzed in `reports/WOF-052_ANALYSIS.md`.

Batch `b-9d72f930-cd5` was valid:
- 5 joined / 5 complete / 0 error / 0 interrupted
- `readOnly=true`
- `ramWrites=0`
- 59,997 aggregate polls
- 241,485 enemy samples
- 1,411 ACTIVE edges
- real multiplayer occupancy was present (1P/2P/3P states across the batch)

However all five rooms had:

```text
t18Samples=0
attackZeroStarts=0
activeEdges=0
resolvedCycles=0
candidateSamples=0
candidateCycles=0
```

Therefore the WOF-052 objective was not solved. The failure was target scene/enemy coverage, not collector/runtime correctness.

The batch did see `T24|A4712=19` and `T24|A4704=8`, including a superficially similar T24 BODY4728/A4/B2/TM1 state, but that T24 descriptor was `FE8aaa0/NX8a644`, while the actual T18 target is `FE8b660/NX8b204`. This cannot substitute for T18 evidence.

## Owner question

The owner asks whether instead of repeated 120-second room sampling, WOF-052 should run as a **single long-duration monitor, approximately one hour, then emit one compact JSON**.

The owner also notes that a huge raw one-hour dump would be inconvenient to upload. The desired design is therefore not full-frame archival; it is long observation with event-selective retention.

## Why a long monitor may help

The current T18 tracer duration is only:

```js
DURATION=120000
INTERVAL=10
MAX_TRACES=160
MAX_STATES=64
```

Five 120-second rooms gave about ten room-minutes of bounded observation and happened to contain zero T18. If T18 occurrence is sparse and scene-dependent, a longer natural-play session has a materially better chance of crossing relevant stages/enemy populations than repeated short random windows.

The useful evidence is not all one-hour RAM frames. For the A4704/A4712 question, useful evidence is event-level:
- T18 zero->ACTIVE cycle boundaries;
- exact candidate occurrence:
  `S0/A4/B2|BODY4728|FE8b660|NX8b204|Vffff|TM1|P6C4736`;
- ordered distinct states from candidate to ACTIVE;
- final ACTIVE attack, especially A4704 vs A4712;
- exact and TM*-normalized tail2/tail3;
- pair/triple transitions;
- target/side stability and retargets.

A one-hour monitor can therefore stay compact if ordinary frames are counted but not retained.

## Proposed WOF-052L design if PM approves

Create a research-only long-capture variant, tentatively `WOF-052L`, without touching `product/alpha/**`.

### Duration / operator UX
- one live `gstyphoon.js` Worker
- default duration about 60 minutes
- one short loader command to start
- owner plays normally / follows the natural multiplayer room
- no manual attack hunting
- at completion, one compact JSON download

### Retention policy
Do **not** save every poll/frame.

Retain:
1. aggregate counters for all samples;
2. compact T18 cycle summaries;
3. ordered distinct-state traces only for candidate-containing T18 cycles, plus a bounded diagnostic sample of non-candidate T18 cycles if useful;
4. per-attack summaries for A4704/A4712 and any other observed T18 ACTIVE outcomes;
5. exact/TM* tail2, tail3, transition pair/triple counts;
6. target/side stability and retarget metadata.

Ordinary non-T18 frames should contribute only to counters/context, not raw output.

### Output-size controls
Use hard caps so a one-hour run cannot create an unbounded JSON:
- bounded candidate trace count;
- bounded states per trace;
- bounded top-N summary keys;
- no giant raw frame arrays;
- optionally discard or heavily summarize non-candidate T18 cycles after counts are accumulated.

Goal: output should remain practical for direct ChatGPT upload even after a one-hour session.

### Resilience / checkpointing
A one-hour in-memory-only trace is riskier than a 120-second run. If implemented, periodically checkpoint compact progress to IndexedDB so a late room/Worker loss does not discard the entire hour.

Checkpointing must remain browser-local result storage only; no game RAM writes and no gameplay input injection.

### Safety boundaries
Must preserve:
- `readOnly=true`
- `ramWrites=0`
- no keyboard/controller/gameplay input injection
- no startup/Worker interception that can break room entry
- no dependence on Alpha bootstrap
- no `product/alpha/**` changes
- ordered-sequence result remains discovery-only until later prospective validation

## Existing coordinator consideration

The inherited coordinator has `batchMaxAgeMs=30*60*1000`, although the current top-finalize logic does not itself expire a still-heartbeating running room. A one-hour design should still review/cleanly separate this batch-age assumption rather than silently relying on behavior designed for 120-second rooms.

The inherited coordinator/context model also has limits tuned for short captures (`maxContextEntries=180`, etc.), so long capture should intentionally summarize context rather than simply multiplying the old capture window by 30.

## Decision requested from PM

Please choose one:

### Option A — keep WOF-052 stopped
Keep the existing result as `INSUFFICIENT TARGET COVERAGE` and resume only when a naturally known T18-containing scene/room is available.

### Option B — approve WOF-052L long event capture
Authorize a minimal research-tooling change for a ~60-minute event-filtered, compact-output, checkpointed T18 monitor, then run one natural-play room and analyze the resulting JSON.

## Engineering recommendation

If WOF-052 is worth continuing at all, **Option B is more informative than repeating more blind 120-second rooms**.

Reason: the previous tooling worked correctly; the failure mode was zero target coverage. Increasing observation time while keeping output event-selective directly addresses that failure without broad RAM dumping or additional owner burden.

This should remain non-blocking research. Alpha RC5/Browser acceptance stays the primary product path.

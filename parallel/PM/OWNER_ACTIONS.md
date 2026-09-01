# WOF Future Danger AI — Owner Actions

Updated: 2026-09-01 — parallel acceleration

## Current owner action required: YES — two remaining actions

Product Alpha thread has been opened by the owner and is considered STARTED.

### Action O1 — MAINLINE WOF-052 Browser run

When continuing the Browser MAINLINE thread, run the already-defined `WOF-052` multi-room protocol.

Operator goal:
- up to 5 rooms;
- prefer rooms where T18 appears;
- allow normal gameplay so the coordinator can collect candidate-containing attack-zero cycles;
- return the one final coordinator JSON according to the MAINLINE protocol.

Purpose:
- discover ordered context that separates the prospectively ambiguous T18 BODY4728 anchor outcomes A4704 vs A4712.

Do **not**:
- perform a new broad WinKawaks sweep;
- create BASECAP collector batches;
- repeatedly hunt T23-only rooms at high operator cost;
- interpret or choose offsets/rules manually.

### Action O2 — PRODUCT / ALPHA implementation thread — STARTED

Status: owner reports the dedicated Product Alpha thread has been opened.

It should continue from:
- `parallel/PM/PRODUCT_ALPHA_START_PROMPT.md`

No duplicate Product Alpha implementation thread should be opened.

### Action O3 — Open one COVERAGE refresh thread

Open one new ChatGPT thread and send:

```text
你负责 WOF 的 COVERAGE 数据整理。请连接 GitHub，读取 ouyong520/wof-ai-private/parallel/PM/COVERAGE_REFRESH_START_PROMPT.md，然后按里面要求继续做。主要使用现有数据，不要让我重新采集，做到覆盖情况整理清楚或者确认真的需要最小补采为止。
```

Purpose:
- refresh stale COVERAGE snapshot against current SWEEPATLAS/SEQMINER;
- normalize enemy type IDs;
- separate real physical data gaps from analysis/label gaps;
- avoid unnecessary human replay.

## Current authorized parallel streams

1. Product Alpha implementation — active.
2. MAINLINE WOF-052 — active / human-gated.
3. Existing SEQMINER — active existing lane.
4. COVERAGE refresh — start O3.
5. PM coordination — active.

Do not open more research lanes now.

A separate Alpha QA thread should wait until Product Alpha produces a concrete release candidate or stable integrated implementation; opening it earlier would duplicate work and create conflict risk.

## Further owner action gates

After O1 and O3 are started, do not request more owner work until one of these occurs:

1. a prospective Browser validator needs a precise operator run;
2. Alpha release candidate needs a short real-Browser acceptance test;
3. refreshed COVERAGE proves a minimal targeted WinKawaks recap is necessary;
4. a true product-scope/release choice is required.

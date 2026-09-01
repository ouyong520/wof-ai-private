# WOF Future Danger AI — Owner Actions

Updated: 2026-09-01

## Current owner action required: YES — two lightweight actions

Only one action involves gameplay.

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

### Action O2 — Start one PRODUCT / ALPHA implementation thread

Open one new ChatGPT thread and send only this bootstrap instruction:

```text
你负责 WOF PRODUCT / ALPHA 实现。请连接 GitHub，读取 ouyong520/wof-ai-private/parallel/PM/PRODUCT_ALPHA_START_PROMPT.md，然后严格按里面的职责、写入范围和 stop condition 持续执行，直到 Alpha RC 或只剩真人 Browser acceptance。
```

Purpose:
- let Alpha engineering proceed in parallel with MAINLINE research;
- keep release runtime/ruleset/HUD separate from WOF-0xx research coordinators;
- reuse existing HUD/production-shadow assets rather than rebuild them.

This is the only new workstream currently authorized. Do not open another research lane.

## No other owner work now

After O1 and O2 are started, PM/research/product lanes can continue from GitHub without the owner manually moving technical results between chats.

A further owner action should not be requested until one of these gates occurs:

1. a prospective Browser validator needs a precise operator run;
2. Alpha release candidate needs a short real-Browser acceptance test;
3. COVERAGE proves a minimal targeted WinKawaks recap is necessary;
4. a true product-scope/release choice is required.

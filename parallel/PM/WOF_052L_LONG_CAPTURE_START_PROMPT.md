# WOF-052L — Fresh Long Event Capture Tooling Stage

You own a fresh independent research-tooling stage.

Repository:
- `ouyong520/wof-ai-private`

Read first:
- `parallel/PM/WOF_052_LONG_CAPTURE_PM_REVIEW.md`
- `parallel/PM/WOF_052_LONG_CAPTURE_DECISION.md`
- `reports/WOF-052_ANALYSIS.md`
- current WOF-052 coordinator/tracer code and relevant WOF-051 evidence

PM has approved **Option B**.

## Objective

Build the smallest read-only WOF-052L tool that can observe one natural Browser WOF session for about 60 minutes and emit one compact JSON focused on the unresolved T18 ordered-sequence split:

`BODY4728/A4/B2/TM1 -> eventual A4704 vs A4712`.

The previous five-room batch was valid but had zero T18 coverage. Do not repeat the same blind 120-second pattern.

## Required capture behavior

- one live native `gstyphoon.js` Worker after normal room entry;
- default duration approximately 60 minutes;
- read-only / `ramWrites=0` / no input injection;
- ordinary non-T18 frames contribute only compact counters/context;
- retain T18 zero->ACTIVE cycle summaries;
- retain ordered distinct states for candidate-containing cycles;
- record final ACTIVE attack;
- summarize exact/TM* final, tail2, tail3, transition pairs/triples;
- retain target/side/retarget metadata;
- bounded diagnostic sample of non-candidate T18 cycles only if useful;
- hard output-size caps;
- periodic compact checkpointing to IndexedDB or equivalent browser-local storage;
- one compact final JSON practical for direct upload and analysis.

## Operator UX

Do not ask the owner to hunt attacks or move through special choreography.

Before human operation, reduce start to one short loader command or similarly simple action. After start, owner should only play/watch normally. At completion, automatically produce one compact JSON.

If the game/Worker closes early, preserve the latest compact checkpoint and provide a simple recovery/finalize path.

## Hard boundaries

- do not modify `product/alpha/**`;
- do not modify PYLAUNCH;
- do not depend on RC5 Alpha bootstrap;
- do not replace/wrap the game Worker in a way that can break room entry;
- no RAM writes;
- no keyboard/controller/gameplay input injection;
- no full-frame one-hour raw dump;
- no Beta features;
- ordered discovery remains research-only until later prospective validation.

## Stop condition

Stop when either:
- WOF-052L tooling is READY and only one minimal owner start action remains; or
- one precise Browser limitation blocks the long capture; or
- after owner capture, the compact JSON is analyzed and the A4704/A4712 discriminator verdict is recorded.

# WOF-052 Long Capture — PM Decision

Updated: 2026-09-01

## Decision

**APPROVE Option B — create WOF-052L as a bounded long event capture.**

Reason:
- the valid five-room WOF-052 evening batch had zero T18 coverage;
- collector correctness was not the problem;
- repeating more blind 120-second windows is low-value;
- a longer natural-play observation directly addresses sparse scene/enemy coverage;
- event-selective retention keeps the final JSON compact and avoids a giant raw dump.

## Product priority

WOF-052L remains non-blocking research. It must not delay the primary Browser Alpha path:

`Python Launcher live-Worker proof -> Alpha transport integration -> Browser acceptance`.

## Approved scope

Create one fresh research-tooling stage that prepares approximately 60 minutes of natural-play monitoring with:
- T18-focused event capture;
- exact BODY4728/A4/B2/TM1 candidate detection;
- ordered distinct states through ACTIVE;
- final attack outcome, especially A4704 vs A4712;
- exact/TM* tail2/tail3 and transition pair/triple summaries;
- target/side/retarget metadata;
- aggregate counters for ordinary samples;
- bounded output caps;
- periodic compact checkpointing so a late room loss does not discard the full run;
- one final compact JSON practical to upload/analyze.

## Prohibited

- no full-frame one-hour raw dump;
- no manual attack hunting requirement;
- no `product/alpha/**` changes;
- no Alpha bootstrap dependency;
- no Worker replacement that can block gameplay;
- no RAM writes;
- no gameplay input injection;
- no promotion of discovery result directly to production.

## Operator goal

After tooling is ready, owner operation should be one short start action, then normal play/observation for about one hour, then one compact JSON.

Do not ask the owner to begin the hour until the tooling stage explicitly reports READY.

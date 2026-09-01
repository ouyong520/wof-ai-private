# WOF-052L Automatic Analysis — Implementation Result

Status: **READY**

Scope respected:

- writes only under `parallel/WOF052L_ANALYSIS/**`;
- no changes to `parallel/WOF052L_RECORDER/**`;
- no changes to `product/alpha/**`;
- offline/read-only analysis only;
- no RAM writes;
- no input injection;
- no production-rule auto-promotion.

## Implemented

`analyzer.py` accepts one or more WOF-052L per-room, ordinary merged, or Browser Fleet merged JSON inputs, or recursively scans a Recorder save directory.

It automatically produces:

- `analysis.json` — machine-readable analysis;
- `分析结果.txt` — Simplified Chinese owner summary.

It computes:

- exact T18 BODY4728/A4/B2/TM1 candidate-containing cycle support;
- final A4704 / A4712 distribution;
- exact final / tail2 / tail3;
- timer-normalized `TM*` final / tail2 / tail3;
- exact and `TM*` ordered pairs/triples;
- candidate first/last lead min/median/max;
- target / side / retarget stability;
- strongest outcome-exclusive ordered discriminator candidates;
- conservative `已解决 / 仍不足` verdict;
- whether evidence is worth a new prospective validator;
- T18/T23 coverage;
- enemy type / active attack frequency;
- player occupancy;
- rare descriptor+attack coverage when room detail is available.

## WOF-051 ambiguity guardrail

The analyzer permanently treats the exact single state

```text
S0/A4/B2|BODY4728|FE8b660|NX8b204|Vffff|TM1|P6C4736
```

as insufficient for an A4704-specific rule by itself. WOF-051 prospectively observed it before both A4704 and A4712, so only post-candidate ordered context can move the analysis forward.

Default conservative resolution gate:

1. A4704 candidate cycles >= 2;
2. A4712 candidate cycles >= 2;
3. at least one ordered tail/pair/triple has support >= 2 for one outcome and 0 for the other;
4. target stable rate = 1.0 for both outcomes;
5. side stable rate = 1.0 for both outcomes;
6. retarget-free rate = 1.0 for both outcomes;
7. observed room identity is exactly the World 921031 golden SHA-256;
8. no input safety violation.

Even when this returns `已解决`, the only recommendation is to build a new prospective validator. No Alpha/product rule is changed or promoted.

## Continuous mode

`RUN_WOF052L_ANALYSIS.cmd` is the owner entry point. With no arguments it reads the Recorder's remembered output directory and starts continuous monitoring. New/updated Recorder JSON automatically refreshes the two result files.

Generated `analysis.json` is ignored by the watch input signature, preventing self-trigger loops.

Recorder checkpoint JSON is intentionally excluded from primary scanning, avoiding repeated rolling-checkpoint double counting.

## Input de-duplication

- ordinary merged JSON is preferred over same-run room JSON for aggregate counts;
- same-run room JSON may supplement T23 traces and rare descriptor+attack detail omitted from merged output;
- Fleet index is skipped when all referenced child merged runs are available;
- when a Fleet index must fill missing child runs, its aggregate replaces overlapping child aggregate input instead of being added on top;
- per-room traces are explicitly namespaced by real `roomId` and run identity before fingerprint de-duplication;
- candidate/t23 traces are fingerprint-deduplicated across copied room/merged/fleet representations;
- ordered pair/triple support counts cycles containing a pattern, not repeated occurrences inside one cycle;
- rare descriptor counts prefer diagnostics totals and use individual edge events only as fallback, preventing double counting.

## Validation

Passed locally:

```text
python -m py_compile common.py ingest.py engine.py report.py analyzer.py test_analyzer.py
python -m unittest -v
python analyzer.py --self-test
```

Regression cases: 9/9 PASS.

Covered cases:

- single-state-only evidence remains `仍不足`;
- repeated exclusive ordered tails can become `已解决`;
- target/side/retarget instability blocks resolution;
- wrong ROM identity blocks resolution;
- merged-first aggregation plus room T23/rare-detail supplementation;
- identical traces from distinct per-room JSON stay room-isolated instead of being falsely deduplicated;
- partial Fleet + available child merged input does not double Fleet totals/evidence;
- missing safety metadata blocks a resolved verdict;
- zero T18 target coverage reproduces the historical WOF-052 conclusion `仍不足`.

A smoke test using a WOF-052-shaped zero-target merged payload produced:

```text
T18 判别：仍不足
支撑样本数：0
A4704/A4712：0/0
是否值得进入新的前瞻验证器：否
```

## Stop condition

Repository-side implementation is READY. No human analysis thread is required after future long WOF-052L captures: the analyzer can continuously update its own conclusion. A future human/browser action is only needed to generate additional natural T18 candidate coverage when the analyzer itself reports `仍不足`.

# WOF-051 Analysis

Batch: `b-2f39eb3f-4a7`

## Identity / integrity
- copyId: `WOF-051`
- project: `WOF-AI-PRIVATE`
- version: `wof-future-danger-multiroom-coordinator-v51`
- expected marker: `=== WOF FUTURE DANGER MULTIROOM COORDINATOR V51 JSON ===`
- readOnly: `true`
- ramWrites: `0`
- 3 joined / 3 complete / 0 error / 0 interrupted
- all embedded WOF-051R validations passed
- player histogram: `[0,488,488,492]`; rooms were effectively pure 3P, pure 1P, pure 2P

## Aggregate
- polls: 35,999
- enemy samples: 108,463
- ACTIVE edges: 558
- signals: 145
- strict: 144
- jitter: 0
- realLate: 1
- hardMiss: 0
- censored: 0

The one realLate belongs to the new experimental T18 A4704 candidate, not an existing production rule.

## Production audit
### T16_B4_DANGER_40
- 98/98 strict danger hits
- lead 8.9..21.0ms
- active attacks: A6432=97, A4840=1
- target 98/98 stable
- side 98/98 stable

This again confirms T16 B4 is an imminent-danger rule, not an A6432-exclusive predictor.

### T20_5136_B0_TO_B255_1250
- 5/5 strict
- A5136 5/5
- target/side 5/5
- lead 380.9..639.7ms

### D867BA_3232_TM6_220
- 10/10 strict A3232
- target/side 10/10
- lead 99.1..109.4ms
- type coverage T33=8, T9=2
- P1/P2/P3 target coverage present

### D8811E_3232_TM6_135
- 22/22 strict A3232
- target/side 22/22
- lead 98.6..119.2ms
- type coverage T34=15, T11=7

### T24
Both production rules had zero coverage in this batch; no negative evidence.

### Existing T18 production rules
- BODY7512/TM4 -> A5440: 4/4 strict, lead 62.3..70.9ms, target/side 4/4
- BODY7520/TM4 -> A5424: 4/4 strict, lead 69.1..70.0ms, target/side 4/4

## T23
All three rooms again had:
```text
t23Samples=0
attackZeroStarts=0
activeEdges=0
resolvedCycles=0
```
Aggregate type census contains no T23. WOF-047 remains the latest positive T23 ordered-sequence evidence.

## Critical WOF-051 result: T18 BODY4728 single state is attack-ambiguous
WOF-050 discovery proposed:
```text
S0/A4/B2|BODY4728|FE8b660|NX8b204|Vffff|TM1|P6C4736
```
as a possible precursor for T18 A4704.

WOF-051 directly prospectively armed that exact state once per zero-attack cycle. It produced two evaluable signals:
```text
A4704 @ 19.9ms
A4712 @ 100.4ms
```
with target 2/2 stable and side 2/2 stable.

Therefore:
- the exact single state is real and forward-relevant;
- but it is NOT attack-specific;
- expected A4704 rate is only 1/2 in direct prospective evidence;
- do not promote it as an A4704 production rule;
- this is analogous to the earlier T23 lesson: ordered sequence/context is required.

The broad same-cycle focus data in the same T18 room also shows A4704 and A4712 live in materially different longer state histories, but unordered membership is not enough to build a production discriminator.

## Decision / WOF-052
Retire the single-state A4704 candidate as a predictor. WOF-052 keeps all production audits and T23 tracing, but adds an ordered T18 candidate-context tracer:
- record all T18 zero->ACTIVE cycles;
- mark every occurrence of the exact BODY4728/A4/B2/TM1 state;
- preserve ordered distinct states before/after it;
- group candidate-containing cycles by eventual ACTIVE attack;
- summarize exact and timer-normalized TM* final/tail2/tail3, transition pairs and triples;
- specifically seek a post-candidate discriminator for A4704 vs A4712;
- discovery only until a later prospective ordered-sequence validator is built.

Next:
- copyId: `WOF-052`
- coordinator: `wof_future_danger_multiroom_coordinator_v52.js`
- embedded: `WOF-052R`
- IndexedDB: `wof-future-danger-multiroom-v14`

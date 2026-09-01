# WOF-049 ANALYSIS

Batch: `b-106c5a3c-819`

## Identity / integrity
- `copyId=WOF-049`
- `project=WOF-AI-PRIVATE`
- `version=wof-future-danger-multiroom-coordinator-v49`
- marker `=== WOF FUTURE DANGER MULTIROOM COORDINATOR V49 JSON ===`
- `readOnly=true`
- `ramWrites=0`
- 5 joined / 5 complete / 0 error / 0 interrupted
- embedded validator identity passed as `WOF-049R / wof-future-danger-cycle-validator-v49r`

## Aggregate
- polls: 60000
- enemySamples: 194328
- ACTIVE edges: 1166
- signals: 106
- strictHits: 106
- jitterBandHits: 0
- realLateHits: 0
- hardMisses: 0
- censored: 0
- retargets recorded by rule diagnostics: 0
- player histogram: `[27,1087,196,1134]`
- room peak player counts: `3,1,3,1,3`

This was a useful mixed 1P/2P/3P audit batch, but it did not include enemy type T23 in any room.

## Production-shadow audit

### T16_B4_DANGER_40
- 31/31 strict
- attack A6432: 31/31 in this batch
- targetSame 31/31
- sideSame 31/31
- lead 10.0..21.6ms
- remains `production-shadow-imminent-danger`; historical non-A6432 cases still forbid attack-exclusive semantics.

### T20_5136_B0_TO_B255_1250
- 4/4 strict A5136
- targetSame 4/4
- sideSame 4/4
- lead 430.2..629.1ms
- remains `production-shadow-coarse`; 1250ms remains audit horizon, not causal threshold.

### D867BA_3232_TM6_220
- 13/13 strict A3232
- type distribution T9=11 / T33=2
- targets P1=7 / P2=3 / P3=3
- targetSame 13/13
- sideSame 13/13
- lead 29.9..120.1ms
- remains production-shadow.

### D8811E_3232_TM6_135
- 4/4 strict A3232
- all T11 in this batch
- targetSame 4/4
- sideSame 4/4
- lead 100.0..108.8ms
- remains production-shadow; 135ms still audit-only.

### T24
- BODY7512/TM3 -> A5440: 19/19 strict, targetSame 19/19, sideSame 19/19, lead 49.2..59.3ms.
- BODY7520/TM4 -> A5424: 21/21 strict, targetSame 21/21, sideSame 20/21, lead 60.6..70.4ms.
- the single side mismatch is a CENTER-at-entry -> RIGHT-at-ACTIVE crossing, not an attack/target failure and not a hard miss.

### T18
- BODY7512/TM4 -> A5440: 7/7 strict, target/side 7/7, lead 60.0..70.6ms.
- BODY7520/TM4 -> A5424: 7/7 strict, target/side 7/7, lead 68.9..70.5ms.

## T23 result
All five rooms had dedicated T23 trace diagnostics with:
```text
t23Samples = 0
attackZeroStarts = 0
activeEdges = 0
resolvedCycles = 0
t23CycleTraces = []
t23SequenceSummary.totalCycles = 0
```
The aggregate type census also contains no T23. Both prior T23 forward candidates remained rawMatch0/signals0 because there was no T23 coverage.

Therefore WOF-049 adds **no new T23 sequence evidence**. This is stronger evidence that the current bottleneck is room/scene coverage probability, not tracer correctness. It is still not a forward failure of any T23 candidate.

## Decision / next
- No production rule is demoted.
- No T23 rule is promoted.
- Preserve active-edge retarget fix and exact-TM + TM* ordered sequence summaries.
- WOF-050 is a semantic coverage-repeat with fresh IndexedDB namespace `wof-future-danger-multiroom-v12`.
- Prefer up to 5 simultaneous rooms again; target is simply to obtain at least one T23 room with repeated A4792/A4920/A5888 cycles.

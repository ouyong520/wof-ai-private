# WOF-046 — two-batch analysis

Date: 2026-08-31  
Project: `WOF-AI-PRIVATE`

## Returned batches

### Batch A — `b-65a0db92-24c`
Identity:
```text
copyId = WOF-046
project = WOF-AI-PRIVATE
version = wof-future-danger-multiroom-coordinator-v46
expectedMarker = === WOF FUTURE DANGER MULTIROOM COORDINATOR V46 JSON ===
readOnly = true
ramWrites = 0
```

Batch status:
```text
joined = 5
complete = 4
error = 0
interrupted = 1
polls = 47998
enemySamples = 181961
activeEdges = 989
signals = 294
strictHits = 294
hardMisses = 0
```

Player histogram:
```text
[0P0,1P12,2P1949,3P161]
```
The interrupted room was the 3P room. The four completed embedded WOF-046R identities passed.

### Batch B — `b-b1f1a5a3-92c`
Identity valid with the same WOF-046 contract.

Batch status:
```text
joined = 4
complete = 4
error = 0
interrupted = 0
polls = 48000
enemySamples = 168660
activeEdges = 958
signals = 110
strictHits = 108
jitterBandHits = 1
realLateHits = 1
hardMisses = 0
```

Player histogram:
```text
[0P0,1P490,2P489,3P983]
```
All four embedded WOF-046R identities passed.

## Combined production audit

Across the two batches:

| rule | resolved | timing | attack specificity | target/side |
|---|---:|---|---|---|
| T16_B4_DANGER_40 | 225 | 224 strict + 1 jitter, 0 miss | A6432=223, A4840=2 | 225/225 |
| T20_5136_B0_TO_B255_1250 | 14 | 14 strict, 460.8..700.4ms | A5136 14/14 | 14/14 |
| D867BA_3232_TM6_220 | 16 | 16 strict, 99.1..119.6ms | A3232 16/16 | 16/16 |
| D8811E_3232_TM6_135 | 21 | 20 strict + 1 real-late209.5ms, 0 miss | A3232 21/21 | 21/21 |
| T24_5440_CYCLE_BODY7512_TM3_80 | 28 | 28 strict, 48.5..68.5ms | A5440 28/28 | 28/28 |
| T24_5424_CYCLE_BODY7520_TM4_S24_LEVEL_90 | 34 | 34 strict, 59.9..71.8ms | A5424 34/34 | 34/34 |
| T18_5440_CYCLE_BODY7512_TM4_LEVEL_90 | 33 | 33 strict, 59.1..78.5ms | A5440 33/33 | 33/33 |
| T18_5424_CYCLE_BODY7520_TM4_LEVEL_90 | 33 | 33 strict, 58.2..71.3ms | A5424 33/33 | 33/33 |

Interpretation:
- Existing production set remains healthy.
- T16 continues to be an imminent-danger rule, not an exclusive A6432 classifier.
- D881 135ms remains only an audit horizon; the repeat 209.5ms clean tail hit is positive attack evidence, not a miss.

## T23 direct candidate

WOF-045 discovery candidate:
```text
T23_4792_BODY4976_A6_B4_TM5_LEVEL_100
S0/A6/B4|BODY4976|FE84868|NX83F20|V0|TM5|P6C0
```

Both WOF-046 batches:
```text
rawMatchSamples = 0
transitionEntries = 0
signals = 0
```

This is zero coverage, not negative forward evidence.

Batch B still had:
```text
T23 samples = 7379
T23 A4792 ACTIVE = 12
```
so T23 was active but the WOF-045 exact branch did not occur.

## Why the next T23 step changes from single-state to sequence

Focused same-cycle data showed common T23 states are attack-ambiguous.

Example:
```text
S2/A4/B0|BODY0|FE84A98|NX83D14|V100000|TM20|P6C0
```
appeared before:
```text
A4792 = 4 cycles
A4920 = 2 cycles
A5848 = 1 cycle
```
The A4792 branch had targetSame=0/4 in that long-lead room, so this state is not suitable as a target-specific warning.

Another state:
```text
S0/A4/B2|BODY4936|FE84060|NX83C60|VFFFF|TM1|P6C4944
```
also appeared before both A4792 and A4920.

Therefore the next discriminating feature should be an ordered transition path / state sequence, not a single fingerprint.

## WOF-047 design

`WOF-047R` keeps the full WOF-046 production audit and previous short T23 candidate audit, and adds:
```text
t23CycleTraces
```

Per room:
- up to 120 resolved T23 zero->ACTIVE cycles
- up to 48 distinct states per cycle in chronological order
- first/last lead to ACTIVE for every state
- target/side at cycle start and ACTIVE
- retarget list
- tail1 / tail2 / tail3 state sequence

This is discovery evidence only. After WOF-047, rank transition pairs/triples by attack specificity and then build a later prospective validator.

Current next:
```text
resume = wof-resume-dispatch-selector-v57
nextCopyId = WOF-047
nextScript = wof_future_danger_multiroom_coordinator_v47.js
embedded = WOF-047R
```

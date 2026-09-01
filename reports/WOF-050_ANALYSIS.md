# WOF-050 Analysis

Date: 2026-09-01  
Batch: `b-f8bbda7c-fae`

## Identity / integrity

PASS:

- `copyId = WOF-050`
- `project = WOF-AI-PRIVATE`
- `version = wof-future-danger-multiroom-coordinator-v50`
- marker = `=== WOF FUTURE DANGER MULTIROOM COORDINATOR V50 JSON ===`
- `readOnly = true`
- `ramWrites = 0`
- 3 joined / 3 complete / 0 error / 0 interrupted
- every embedded validator passed WOF-050R identity/integrity

## Aggregate

- polls: 36,000
- enemy samples: 104,337
- ACTIVE edges: 495
- signals: 98
- strict: 96
- jitter: 0
- realLate: 2
- hard miss: 0
- censored: 0
- retargets: 0
- player histogram `[112,0,868,488]` => only 2P/3P gameplay coverage in this batch

## Production audit

### T16 B4 danger

- 72/72 strict
- target 72/72
- side 72/72
- lead 9.7..21.2 ms
- ACTIVE attacks: A6432=71, A4832=1

Interpretation: the danger rule remains excellent, and this batch again confirms that T16 B4 is **not attack-exclusive**. A4832 is a valid non-A6432 terminal outcome while the danger timing remains correct.

### T20 B0 -> B255 -> A5136

- 4/4 strict
- A5136 4/4
- target/side 4/4
- lead 599.4, 831.1, 989.7, 989.7 ms

Interpretation: production-shadow-coarse remains valid. 1250ms is an audit horizon, not a countdown law.

### D867BA -> A3232

- 18/18 strict
- A3232 18/18
- target/side 18/18
- lead 79.7..110.1 ms
- types: T9=12, T36=1, T33=5
- targets include P1/P2

### D8811E -> A3232

- 2/2 strict
- A3232 2/2
- target/side 2/2
- lead 109.7, 110.8 ms
- type T11

### T24

No raw coverage for either production rule in this batch. No negative evidence.

### T18 A5440 / A5424

Both existing production-shadows fired once:

- BODY7512/TM4 -> A5440: lead 138.6ms
- BODY7520/TM4 -> A5424: lead 128.5ms

Both were:
- correct expected attack
- target stable
- side stable
- within the existing 250ms tail
- classified `realLate` only because the legacy audit horizon is 90ms

Interpretation: no demotion. The 90ms value is not a causal boundary. This batch extends the observed correct warning lead beyond 90ms.

## T23

All 3 rooms had:

```text
t23Samples = 0
attackZeroStarts = 0
activeEdges = 0
resolvedCycles = 0
```

Aggregate type census also contained no T23.

Therefore WOF-050 adds no T23 discriminator evidence. This remains pure room/scene coverage absence, not a tracer or candidate failure.

## New same-cycle discovery from WOF-050

The broad `cyclePrecursorTop` miner produced a strong new T18 / A4704 candidate:

```text
T18
ACTIVE attack = A4704
signature =
S0/A4/B2|BODY4728|FE8b660|NX8b204|Vffff|TM1|P6C4736
```

Same-cycle evidence:

- 18 resolved cycles
- attack-zero only
- targetSame = 18/18
- sideSame = 18/18
- first-seen lead 50.5..188.6ms, median 80.3ms
- last-seen lead 29.6..51.1ms, median 40.5ms

This is substantially stronger than a retrospective lag fingerprint and is suitable for a fresh prospective level-arm test.

## Decision for WOF-051

Keep all existing production audits and T23 ordered-sequence tracer unchanged.

Add one new prospective candidate:

`T18_4704_BODY4728_A4_B2_TM1_LEVEL_80`

Exact pre-ACTIVE state:

```text
type=18
attack=0
state99=0
action2A=4
b2B=2
body=4728
frameEnd=0x8B660
next=0x8B204
value30=0xFFFF
timer34=1
payload6C=4736
```

Expected ACTIVE attack: `4704`

Audit:
- horizon 80ms
- tail 250ms
- once-per-zero-cycle level arm
- live target `enemy+0x7E`
- target/side checked at ACTIVE

Status remains `prospective-cycle-level-candidate` until direct forward confirmation.

WOF-051 uses fresh IndexedDB `wof-future-danger-multiroom-v13`.

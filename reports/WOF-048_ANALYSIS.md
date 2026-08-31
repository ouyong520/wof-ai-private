# WOF-048 analysis

Batch: `b-bdb16c09-b10`

## Identity / transport
- copyId `WOF-048`
- project `WOF-AI-PRIVATE`
- version `wof-future-danger-multiroom-coordinator-v48`
- marker `=== WOF FUTURE DANGER MULTIROOM COORDINATOR V48 JSON ===`
- readOnly `true`
- ramWrites `0`
- 1 joined / 1 complete / 0 error / 0 interrupted
- embedded WOF-048R identity passed
- player histogram `[0,0,0,495]`: pure 3P room

## Aggregate
- 11997 polls
- 39546 enemy samples
- 164 ACTIVE edges
- 19 signals
- 19 strict
- 0 jitter / late / hard miss / censored / retarget

## Production audit
### T20 `T20_5136_B0_TO_B255_1250`
- 6/6 strict
- 6/6 expected A5136
- target 6/6
- side 6/6
- lead 481.0..799.5ms
- remains `production-shadow-coarse`

### D867BA `D867BA_3232_TM6_220`
- 11/11 strict A3232 / target / side
- lead 99.2..111.3ms
- types T33=1, T9=10
- remains `production-shadow`

### D8811E `D8811E_3232_TM6_135`
- 2/2 strict A3232 / target / side
- lead 99.9,109.3ms
- remains `production-shadow`

T16, T24 and T18 production rules had no raw coverage in this room; this is not negative evidence.

## T23
This room had **zero T23 samples** in the dedicated trace probe:
- t23Samples 0
- attackZeroStarts 0
- activeEdges 0
- resolvedCycles 0
- t23CycleTraces []
- t23SequenceSummary totalCycles 0

Therefore WOF-048 provides **no new T23 discriminator evidence**. It does not weaken the WOF-047 ordered-trace result; this room simply never exposed T23 during the 120s trace window.

The WOF-048 active-edge retarget fix and timer-normalized sequence summary remain installed, but neither was exercised for T23 in this batch.

## Decision
Do not invent or promote a T23 sequence rule from this batch. The limiting factor is coverage, not model failure.

Next: WOF-049 repeats the same sequence instrumentation with a fresh multiroom DB. Prefer several rooms in parallel because T23 is scene-dependent/low-frequency; 5 concurrent rooms gives far better chance of collecting repeated A4792/A4920/A5888 sequence families without increasing wall-clock time much beyond one 120s collection window.

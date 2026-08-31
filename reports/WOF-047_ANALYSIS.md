# WOF-047 Analysis

Batch: `b-fbbbc59d-cea`

## Identity / transport
- copyId `WOF-047`
- project `WOF-AI-PRIVATE`
- version `wof-future-danger-multiroom-coordinator-v47`
- marker `=== WOF FUTURE DANGER MULTIROOM COORDINATOR V47 JSON ===`
- readOnly=true / ramWrites=0
- 3 joined / 3 complete / 0 error / 0 interrupted
- 35996 polls / 113581 enemy samples / 644 ACTIVE edges
- 144 signals = 143 strict + 1 jitter / 0 hard miss / 0 censored
- player histogram `[0,0,579,902]` = 0P/1P/2P/3P
- all three embedded WOF-047R validations passed

## Production audit
- T16 B4: 94/94 danger tail hits = 93 strict +1 jitter; A6432=93, A4832=1; target/side94/94; lead9.0..40.5ms. Keep imminent-danger semantics only.
- T20: no coverage this batch; rawMatch0/signals0. No negative evidence.
- D867BA: 23/23 strict A3232/target/side; lead98.8..119.5ms; T33=18,T9=5; all3 rooms.
- D8811E: 19/19 strict A3232/target/side; lead99.4..120.4ms; T34.
- T24 A5440: 3/3 strict; lead50.0..52.1ms.
- T24 A5424: 3/3 strict; lead63.3..70.6ms.
- T18 A5440: 1/1 strict at60.0ms.
- T18 A5424: 1/1 strict at69.8ms.
- old T23 BODY4920/B0 remains retired.
- WOF-045 short T23 BODY4976/A6/B4/TM5 candidate again rawMatch0/signals0: still zero coverage, not forward failure.

## T23 ordered traces — main result
Only room1 contained T23 in the parallel trace probe. It produced exactly 8 resolved zero->ACTIVE cycles:
- A4792 = 3
- A4920 = 3
- A5888 = 2
- dropped=0

The tracer therefore worked and delivered attack-labelled ordered pre-ACTIVE state sequences.

### A4920 examples
Observed final/tail branches include:
- `S0/A4/B0|BODY4976|FE84868|NX83c56|V1|TM8|P6C0`
- `S0/A6/B4|BODY4976|FE84868|NX83f20|V0|TM11|P6C0`
- `S0/A4/B10|BODY4952|FE84102|NX83c7e|V0|TM1|P6C4960`

### A5888 examples
Observed final/tail branches include:
- `S2/A6/B4|BODY4936|FE84060|NX83c60|Vffff|TM1|P6C4944`
- `S0/A6/B4|BODY4936|FE84060|NX83c60|Vffff|TM1|P6C4944`

One A5888 tail3 is structurally:
`S0/A8/B2 BODY4936 -> S0/A2/B0 BODY4936 -> S0/A6/B4 BODY4936`
which is important because the first state by itself also appears on an A4792 cycle. This proves again that single-state membership is insufficient; order matters.

### A4792 examples
Three A4792 cycles used different immediate tails:
1. final `S0/A2/B0|BODY4952|FE84140|NX83c88|V0|TM2|P6C4960`; immediately preceded by A6/B4 and A6/B0 in the same descriptor family.
2. final `S0/A8/B2|BODY4936|FE84060|NX83c60|Vffff|TM1|P6C4944`.
3. final `S2/A8/B2|BODY4936|FE84060|NX83c60|Vffff|TM1|P6C4944`; preceded by `S2/A2/B0 BODY4952 FE841b4` and `S2/A4/B10 BODY4952 FE841b4`.

So A4792 itself is multi-branch. There is not yet one universal short sequence that covers all A4792 cycles.

## Target evolution / tracer correction
Two A4792 traces ended with a different target than their start. One trace correctly logged the retarget. Another had `targetStable=false` but an empty `retargets` array. Inspection of WOF-047R shows why: target changes that occur on the exact poll where attack changes 0->nonzero are checked by `targetStable` but were not appended to `retargets`, because the trace observer runs only while attack==0.

WOF-048R patches this instrumentation bug: an active-edge target change is appended with `atActiveEdge:true` before the cycle is resolved.

## Interpretation
WOF-047 confirms the T23 research direction should stay sequence-based. The useful discriminator is likely a late ordered tail/pair/triple or branch family, not a single persistent fingerprint. Current sample size is only 8 resolved cycles from one T23 room, so no new T23 production rule is promoted yet.

## Next — WOF-048
WOF-048 keeps all WOF-047 audits and ordered T23 traces, fixes active-edge retarget logging, and adds `t23SequenceSummary` per room:
- timer-normalized family signatures (`TM*`)
- final-family counts by active attack
- tail2 / tail3 family counts
- transition pair frequencies
- transition triple frequencies

Goal: accumulate more T23 cycles across rooms and automatically rank attack-specific sequence discriminators before building the next prospective sequence validator.

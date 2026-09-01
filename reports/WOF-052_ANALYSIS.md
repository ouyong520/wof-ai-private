# WOF-052 Evening Multiplayer Capture Analysis

Batch: `b-9d72f930-cd5`

## Identity / integrity

- copyId: `WOF-052`
- project: `WOF-AI-PRIVATE`
- version: `wof-future-danger-multiroom-coordinator-v52`
- expected marker: `=== WOF FUTURE DANGER MULTIROOM COORDINATOR V52 JSON ===`
- readOnly: `true`
- ramWrites: `0`
- 5 joined / 5 complete / 0 error / 0 interrupted
- all five embedded results validated as `WOF-052R`
- aggregate: 59,997 polls / 241,485 enemy samples / 1,411 ACTIVE edges

This is a valid merged WOF-052 capture batch and satisfies the bounded evening collection protocol itself.

## Room coverage

| ordinal | room | peak players | T18 samples | T18 resolved cycles | candidate samples | candidate cycles |
|---:|---|---:|---:|---:|---:|---:|
| 1 | `r-f42d3e53-89d` | 2 | 0 | 0 | 0 | 0 |
| 2 | `r-9ca097f8-300` | 3 | 0 | 0 | 0 | 0 |
| 3 | `r-914777fe-3f6` | 2 | 0 | 0 | 0 | 0 |
| 4 | `r-c87d563b-e1b` | 2 | 0 | 0 | 0 | 0 |
| 5 | `r-2938cfb1-e89` | 3 | 0 | 0 | 0 | 0 |

Aggregate player histogram was `[0,41,1426,976]`, so the batch did exercise real 1P/2P/3P multiplayer occupancy. The target failure is not a multiplayer-presence failure; it is specifically a T18 scene/enemy coverage absence.

## Critical target result

Target candidate:

```text
S0/A4/B2|BODY4728|FE8b660|NX8b204|Vffff|TM1|P6C4736
```

All five rooms report:

```text
t18Samples=0
attackZeroStarts=0
activeEdges=0
resolvedCycles=0
candidateSamples=0
candidateCycles=0
t18CycleTraces=[]
t18CandidateSequenceSummary.byAttack={}
```

Therefore WOF-052 produced **zero candidate-containing T18 ordered cycles**. There is no exact/TM* final, tail2, tail3, transition-pair or transition-triple evidence to compare for eventual A4704 versus A4712.

## Important non-target observation

The aggregate batch did observe:

```text
T24|A4712 = 19
T24|A4704 = 8
```

All of those A4704/A4712 observations came from room 5 T24 coverage. Room 5 also contains a superficially similar T24 terminal state:

```text
S0/A4/B2|BODY4728|FE8aaa0|NX8a644|Vffff|TM1|P6C4736
```

which appeared before both A4712 and A4704.

This **must not be substituted** for the WOF-052 target. It is `type=24`, and its descriptor `FE8aaa0/NX8a644` differs from the T18 target descriptor `FE8b660/NX8b204`. It only confirms that A4704/A4712 were active elsewhere in the batch; it is not T18 ordered-sequence evidence.

## Discriminator verdict

**INSUFFICIENT TARGET COVERAGE — no discriminator can be inferred from this batch.**

WOF-051 remains authoritative for the current T18 BODY4728 conclusion:

- the exact single state is forward-relevant;
- it is attack-ambiguous because direct prospective evidence produced both A4704 and A4712;
- it stays retired as an A4704-specific predictor;
- no production rule is promoted from WOF-052.

WOF-052 neither confirms nor rejects any particular post-candidate ordered sequence because the target candidate was never observed.

## Exact missing coverage

To resume ordered discrimination, the next useful evidence must contain **candidate-containing T18 zero->ACTIVE cycles** for both eventual outcomes:

1. at least one T18 cycle containing the exact BODY4728/A4/B2/TM1 candidate and resolving to `A4704`;
2. at least one T18 cycle containing the same exact candidate and resolving to `A4712`;
3. preserve the ordered distinct states after the candidate so exact/TM* tail2, tail3, transition pair and triple can be compared.

That is the minimum needed to perform the requested A4704-vs-A4712 sequence comparison. More than one cycle per outcome, preferably across more than one room, is required before any discovered discriminator should be considered stable enough to build a later prospective validator.

Do **not** reopen broad collection or manually hunt attacks. Only resume opportunistically when natural rooms provide T18 coverage. Existing WOF-052 collection remains read-only / `ramWrites=0` / no input injection and must stay separate from `product/alpha/**`.

## Stop condition

Evening collection stop condition reached:

- valid merged WOF-052 JSON: **yes**;
- five-room bounded capture completed: **yes**;
- target discriminator solved: **no — zero T18 coverage**;
- exact missing evidence documented: **yes**.

No tooling/runtime defect was found in the merged result. The blocker is natural T18 room coverage, not collector correctness.

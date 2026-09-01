# WOF-052L Historical Replay Candidate Mining Longrun — Result

stageId: `WOF052L_HISTORICAL_REPLAY_CANDIDATE_MINING_LONGRUN_V1`

## Verdict

**WOF052L HISTORICAL REPLAY LONGRUN READY — MINIMAL NEXT CAPTURE PLAN**

No new durable ordered Browser attack predictor can be honestly frozen from the currently committed historical corpus. The useful stop condition is therefore the bounded next-capture plan, not more offline repetition.

Existing mature research candidates remain intact. Historical replay does **not** satisfy prospective gates and does **not** authorize production promotion.

## Startup / safety gates

- Prospective Validator fresh live-ambiguity QA: **PASS**.
- Stage claim: acquired before work.
- `parallel/PM/PM_DELIVERY_REASSESSMENT_GATE.md`: **missing on current `main` (404)**; recorded as a repository-state limitation rather than silently ignored.
- `readOnly=true`; `ramWrites=0`; `inputInjection=false`.
- No Recorder / Prospective Validator / Alpha / PYLAUNCH / Browser Fleet / Live Proof / HUD code was modified.
- Writes are confined to this lane plus the stage claim.

## Browser type normalization

The replay uses decimal Browser type notation plus hex:

- `T16 (0x10)`
- `T18 (0x12)` — the BODY4728 A4704/A4712 ambiguity
- `T20 (0x14)`
- `T23 (0x17)`
- `T24 (0x18)` — BODY7512/BODY7520

The start prompt's phrase “T18 BODY7512 / 7520” is normalized to **T24 (0x18)** because the authoritative Beta manifests identify those candidates as Browser type 24. This avoids decimal/hex type conflation.

## Evidence replayed

### Mature-pattern sanity set

The current research manifests were replayed at count/contract level:

| candidate | Browser type / family | historical positive support | single-missing support | decision |
|---|---|---:|---:|---|
| T16_B4_DANGER_40 | T16 (0x10) | 520 danger outcomes | 519 | keep imminent-danger semantics; not attack-exclusive |
| T20_5136_B0_TO_B255_1250 | T20 (0x14) | 27/27 | 26 | keep ordered/history candidate; lifecycle reset remains mandatory |
| D867BA_3232_TM6_220 | cross-type descriptor | 80/80 | 79 | keep research candidate |
| D8811E_3232_TM6_135 | cross-type descriptor | 68/68 | 67 | keep research candidate; 135 ms is an audit horizon, not a causal boundary |
| T24_5424_CYCLE_BODY7520_TM4_S24_LEVEL_90 | T24 (0x18) | 58/58 | 57 | keep research candidate |
| T24_5440_CYCLE_BODY7512_TM3_80 | T24 (0x18) | 50/50 | 49 | keep research candidate |

These checks demonstrate count-level resilience to one omitted positive unit and duplicate de-duplication. They do **not** claim leave-one-room-out robustness where the compiled historical sources do not enumerate each support unit's room, and they do **not** convert historical support into prospective PASS.

### T18 (0x12) BODY4728

Authoritative historical state:

`S0/A4/B2|BODY4728|FE8b660|NX8b204|Vffff|TM1|P6C4736`

WOF-051 prospectively observed:

- A4704: 1 cycle, lead 19.9 ms
- A4712: 1 cycle, lead 100.4 ms
- target stable: 2/2
- side stable: 2/2

WOF-052 then completed five valid rooms but produced:

- T18 samples: 0
- T18 resolved cycles: 0
- candidate cycles: 0

Therefore WOF-052 is **zero coverage, not predictor failure**.

Replay findings:

- all 2 order permutations preserve the 1/1 outcome split;
- duplicating either cycle and de-duplicating by cycle identity leaves support at 1/1;
- leaving either cycle out removes one outcome completely;
- 49 deterministic ±40 ms timing-jitter combinations preserve the observed lead ordering, but timing is **not** promoted because support is only one cycle per outcome;
- no committed repeated first-post-anchor / pair / triple / exact-tail / TM-tail discriminator exists.

Verdict: **NOT READY**. The single BODY4728 state remains permanently invalid as an A4704-specific predictor.

### T23 (0x17)

WOF-047 delivered exactly eight resolved T23 zero->ACTIVE cycles:

- A4792 = 3
- A4920 = 3
- A5888 = 2
- all eight came from one T23 room.

Known A5888 ordered tail3:

`S0/A8/B2 BODY4936 -> S0/A2/B0 BODY4936 -> S0/A6/B4 BODY4936 -> A5888`

Discovery support for that complete tail is **1**. Its first state also occurs on A4792, proving constituent single-state membership is insufficient.

Replay findings:

- all `8! = 40,320` cycle-order permutations preserve aggregate A4792/A4920/A5888 counts and tail3 support=1;
- duplicate perturbations never increase de-duplicated support;
- leaving out the one supporting A5888-tail cycle collapses tail3 support from 1 to 0;
- leave-one-room-out collapses all T23 evidence because the historical T23 sample came from one room;
- A4792 and A4920 remain multi-branch/multi-family without a repeated branch-specific predicate at support >=2.

Verdict: keep `T23_A5888_BODY4936_TAIL3` in the **research-only** queue, but label its discovery support fragile. Do not upgrade it to a durable predictor from this replay.

## Deterministic replay workload

The committed harness performs **40,399 deterministic checks**:

- T18 order permutations: 2
- T18 timing-jitter combinations: 49
- T23 order permutations: 40,320
- T23 one-cycle-missing runs: 8
- T23 duplicate-sample runs: 8
- mature-candidate single-missing checks: 6
- mature-candidate duplicate checks: 6

This is deliberately bounded. More permutations would repeat the same decision and violate the accelerator stop discipline.

## Local WinKawaks structural corpus

Retained local evidence is large (7 captures, 23,400 frames, 468,000 enemy-slot samples, all 31 local types, local T18/T23 present), but it still lacks a separately proven exact local move/attack value and authoritative stage/scene/wave labels.

Accordingly, local cursor/timer/mode/branch structure remains discovery context only. Numeric local offsets are not translated into Browser attack rules.

## Minimal next capture plan

Do **not** request a generic one-hour/two-hour/overnight collection. The evidence target is bounded counters.

Primary target: **T18 (0x12) BODY4728 ordered discriminator**.

Freeze-minimum discovery condition:

1. candidate-containing resolved cycles reach at least `A4704 >= 2` and `A4712 >= 2`;
2. since the current baseline is 1/1, the theoretical minimum additional successful coverage is one new A4704 candidate cycle plus one new A4712 candidate cycle, if natural outcomes split ideally;
3. one shortest exact or `TM*` tail2/tail3/pair/triple reaches support >=2 for one outcome and `oppositeSupport == 0`;
4. target stable, side stable, and retarget-free rates remain 1.0 for both outcomes;
5. exact World 921031 golden SHA and read-only safety invariants remain true.

Durability preference, without inflating the minimum: obtain the repeated winning branch across >=2 rooms and >=2 targets when natural coverage permits. If that cannot be obtained, label it room/target-conditioned rather than universal.

Secondary opportunistic T23 target: one additional unique A5888 cycle repeating the exact or timer-normalized BODY4936 tail3 would raise discovery support from 1 to 2; preferably this comes from a different room. A4792/A4920 branches should not be frozen until the same branch-specific ordered predicate repeats in >=2 unique cycles.

No manual attack hunting is requested. Capture should resume only when the Recorder/live-proof path is ready and natural rooms can provide the missing target coverage, and should stop when the counters above are met.

## Candidate queue decision

- Mature T16/T20/D867BA/D8811E/T24 research candidates: **keep**; prospective proof still required.
- T23 A5888 BODY4936 tail3: **keep queued, fragile discovery support**; fresh prospective proof still required.
- T18 BODY4728 post-anchor split: **NOT READY**; no ordered manifest should be frozen yet.

## Why the stage stops here

Additional offline permutation/mining over the same retained evidence no longer changes the decision:

- T18 needs new real candidate-containing cycles.
- T23 needs a repeated ordered branch and cross-room evidence for durability.
- local reverse-engineering cannot supply exact Browser attack labels.

Continuing would become repetitive research rather than reducing Owner work.

## Artifacts

- `evidence_snapshot.json`
- `replay_longrun.py`
- `REPLAY_MATRIX.json`
- `CANDIDATE_QUEUE.json`
- `MINIMAL_NEXT_CAPTURE_PLAN.json`
- `RESULT.md`

**Stop condition reached: WOF052L HISTORICAL REPLAY LONGRUN READY — MINIMAL NEXT CAPTURE PLAN**

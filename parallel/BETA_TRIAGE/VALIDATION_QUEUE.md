# WOF Beta — Top 10 Validation Queue

Updated: 2026-09-01
Status: **BETA VALIDATION QUEUE READY**
Promotion: **research-only; no automatic production promotion**

Scoring: `user value × coverage frequency × predictive strength × validation convenience`, each 1..5. Convenience 5=cheap/direct, 1=expensive/blocked. Score is a triage heuristic, not a probability.

| Rank | Candidate | Score | Evidence / state | WOF-052L |
|---:|---|---:|---|---|
| 1 | T24 (0x18) BODY7520/TM4 -> A5424 | 400=4×4×5×5 | 58/58 expected attack across WOF-046/047/049; current-level prospective-ready | YES |
| 2 | T24 (0x18) BODY7512/TM3 -> A5440 | 400=4×4×5×5 | 50/50 across WOF-046/047/049; current-level prospective-ready | YES |
| 3 | D867BA -> A3232 | 300=5×4×5×3 | 80/80 across WOF-046/047/049/050/051; research-ready, lifecycle gate remains | YES |
| 4 | D8811E -> A3232 | 300=5×4×5×3 | 68/68 expected attack; one clean real-late tail; lifecycle gate remains | YES |
| 5 | T20 (0x14) B0->B255 -> A5136 | 150=5×3×5×2 | 27/27 expected attack; long lead; ordered/history lifecycle gate | YES |
| 6 | T16 (0x10) B4 imminent danger | 150=3×5×5×2 | 520 positive danger outcomes; not A6432-exclusive; lifecycle gate | YES |
| 7 | T18 (0x12) BODY4728 post-anchor A4704/A4712 split | 90=5×3×2×3 | shared anchor prospectively ambiguous; ordered discriminator not yet known | **YES — priority piggyback** |
| 8 | T23 (0x17) A5888 BODY4936 tail3 | 32=4×1×2×4 | complete ordered tail is manifest-expressible; rare coverage | YES, per-room JSON |
| 9 | T23 (0x17) A4920 branch family | 16=4×1×2×2 | 3 WOF-047 cycles, multi-family; needs repeated ordered branch | YES, per-room JSON |
| 10 | T23 (0x17) A4792 branch set | 8=4×1×2×1 | 3 WOF-047 cycles, explicitly multi-branch + retarget complexity | YES, per-room JSON |

Tie-breaks: #1 has more retained positive cycles than #2; #3 has broader type/target evidence than #4; #5 beats #6 on user lead/attack-specific value; #10 is costlier than #9 because A4792 already shows multi-branch and active-edge retarget complexity.

## Minimum prospective designs

### 1. T24 (0x18) BODY7520/TM4 -> A5424
Freeze the **full audited current-level predicate**, not only BODY/TM shorthand. `expectedAttacks=[5424]`; once per zero-attack cycle; live target reread and side recompute at ACTIVE. Minimum decision sample: 10 fresh evaluable signals across >=2 rooms, zero wrong attacks/hard misses. WOF-049's one CENTER->RIGHT side crossing is not an attack failure and reinforces live side recomputation. WOF-050/051 zero coverage is not negative evidence.

### 2. T24 (0x18) BODY7512/TM3 -> A5440
Same design as #1 using the exact audited T24 predicate and `expectedAttacks=[5440]`. Minimum: 10 fresh evaluable signals across >=2 rooms, zero wrong attacks/hard misses. Do not hunt rooms specifically for T24.

### 3. D867BA -> A3232
Test the safest **current-level/once-per-zero-cycle** form first so the research result does not rely on inherited entry history. `expectedAttacks=[3232]`. Minimum: 12 evaluable signals, >=2 physical targets, and >=2 Browser types when natural coverage permits. If only the historical/entry formulation remains predictive, keep quarantined until a Browser-safe same-instance continuity discriminator exists.

### 4. D8811E -> A3232
Same current-level-first strategy as #3; `expectedAttacks=[3232]`. Minimum: 12 evaluable signals and >=2 targets when available. Preserve late tails instead of treating the old 135 ms audit horizon as causal. Lifecycle-safe promotion remains separately gated.

### 5. T20 (0x14) B0->B255 -> A5136
Freeze the exact ordered/history path, never unordered membership. `expectedAttacks=[5136]`. Reset history on every detectable lifecycle/session/Worker boundary. Minimum: 8 fresh evaluable signals across >=2 rooms. Even a perfect research result cannot waive the hidden same-type replacement problem; promotion needs same-instance continuity or a history-free equivalent.

### 6. T16 (0x10) B4 imminent danger
Keep semantic label **IMMINENT DANGER**; never call it A6432-exclusive. Test current-level/once-per-zero-cycle before history-dependent entry semantics. The research manifest must explicitly enumerate the observed ACTIVE outcome set while preserving every alternate ACTIVE for review. Minimum: 30 evaluable signals across >=2 rooms/targets because this candidate is common. Lifecycle-safe promotion remains separate.

### 7. T18 (0x12) BODY4728 ordered post-anchor split
Hard constraint: the shared anchor alone produced A4704 @19.9 ms and A4712 @100.4 ms in WOF-051, so **never arm on the anchor alone**.

Discovery order: first distinct post-anchor state -> post-anchor pair -> post-anchor triple -> descriptor/body/frameEnd/next progression -> timer progression/terminal hold -> pre-anchor tail only if still needed. Require >=2 unique resolved discovery cycles for a discriminator before freezing; loop visits in one cycle do not increase confidence. Then prospectively validate the shortest frozen branch with >=5 evaluable signals and record all alternate outcomes/misses/retargets.

WOF-052L is the preferred opportunistic source. A 10-room batch with no T18 is coverage absence, not failure.

### 8. T23 (0x17) A5888 BODY4936 tail3
Freeze only the complete ordered path:

`S0/A8/B2 BODY4936 -> S0/A2/B0 BODY4936 -> S0/A6/B4 BODY4936`

with `expectedAttacks=[5888]`. A constituent state is invalid because the first state also occurs before A4792. Minimum: 3 fresh evaluable prospective signals, preferably across >=2 rooms/targets, without random room hunting. Use WOF-052L **per-room JSON** for complete T23 traces.

### 9. T23 (0x17) A4920 branch family
WOF-047's 3 A4920 cycles span BODY4976/BODY4952 families; no universal final state exists. Rank exact and TM*-normalized tail2/tail3 by unique resolved-cycle support. Require >=2 discovery cycles for the same branch before freeze, then >=3 prospective signals. Prefer the shortest attack-pure branch after target conditioning; do not merge distinct families to manufacture universality.

### 10. T23 (0x17) A4792 branch set
Treat A4792 as separate branches, not one fingerprint. Preserve target changes including ACTIVE edge. Require >=2 unique discovery cycles **per branch** before freezing that branch, then >=3 prospective signals per frozen branch. Target-conditioned branches are allowed if explicitly labelled. Use WOF-052L per-room JSON only when T23 occurs naturally.

## Permanent rejects / not attack-specific queue candidates

- T18 (0x12) BODY4728/A4/B2/TM1 -> A4704 single-state rule: prospectively falsified as attack-specific.
- Any T23 (0x17) single state already observed before multiple attacks.
- WinKawaks `+0x73 != 0` or `+0x24 != 0` as Browser attack predictors.
- Local branch hotspots without an independently proven exact local attack label.
- Any pair/triple supported by only one resolved cycle as a production claim.
- Retired fixed-lag fingerprints that are not current prospective/current-level candidates.

## Parked / low priority

- WOF-045 T23 BODY4976/A6/B4/TM5 single-state candidate: ordered evidence supersedes it; do not spend room cost hunting it.
- WinKawaks `02008BE0`, cursor-flag, terminal-TM1 hold, delayed-reload, mode35 and loop/reset families: structural discovery only until exact local attack semantics exist.
- Stage/scene/wave-conditioned expansion: authoritative labels are absent; this is not a generic raw-volume problem.

## Execution policy

No new capture is requested. WOF-052L is opportunistic reuse, not a prerequisite. Absence of T18/T23/T24 from a batch is coverage absence, not automatic candidate failure. Every manifest remains `research-only`, frozen before prospective evidence, and no result here modifies `product/alpha/**` or becomes production automatically.

**BETA VALIDATION QUEUE READY**

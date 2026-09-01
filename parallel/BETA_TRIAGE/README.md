# WOF Beta Rule Candidate Triage

Updated: 2026-09-01
Status: **BETA VALIDATION QUEUE READY**
Scope: `parallel/BETA_TRIAGE/**` only

## Purpose

This lane consumes existing evidence only and ranks the next Beta Future Danger rule validations. It does not collect new data, does not modify `product/alpha/**`, and does not promote any production rule.

Primary outputs:

- `VALIDATION_QUEUE.md` — evidence-ranked Top 10 with minimum prospective test design.
- `validation_queue.json` — machine-readable queue/status.

## Hard boundaries

- All candidates remain `research-only` until a separate promotion decision.
- Browser prospective evidence outranks WinKawaks-local discovery correlation.
- WinKawaks numeric offsets/cursors are never copied into Browser/WASM production logic.
- No RAM writes; no gameplay input injection.
- No new Collector task is requested by this triage.
- Existing/forthcoming WOF-052L long-room evidence may be consumed opportunistically, but this lane does not require rooms to be hunted merely to force rare coverage.
- Canonical type notation is always `T<decimal> (0xHH)`, e.g. T18 (0x12), T23 (0x17), T24 (0x18).

## Non-negotiable T18 rule

The Browser state

`T18 (0x12) S0/A4/B2|BODY4728|FE8b660|NX8b204|Vffff|TM1|P6C4736`

is a forward-relevant **shared anchor**, not an A4704-specific rule. WOF-051 prospectively produced both A4704 and A4712 from that same state. Any future candidate using this anchor must include ordered context and must never arm on the anchor alone.

## Scoring contract

Queue score uses four 1..5 factors:

`user value × coverage frequency × predictive strength × validation convenience`

where validation convenience is 5 for cheap/direct validation and 1 for expensive/blocked validation. The score is a triage heuristic, not a probability or production confidence.

Tie-breakers, in order:

1. more independent Browser-positive cycles/batches;
2. broader target/type coverage;
3. simpler research-only prospective manifest;
4. lower risk of hidden cross-sample/lifecycle inheritance.

## Read-only evidence basis

The queue was derived from existing repository evidence, principally:

- `reports/WOF-046_ANALYSIS.md`
- `reports/WOF-047_ANALYSIS.md`
- `reports/WOF-049_ANALYSIS.md`
- `reports/WOF-050_ANALYSIS.md`
- `reports/WOF-051_ANALYSIS.md`
- `reports/WOF-052_ANALYSIS.md`
- `parallel/SEQMINER/**`
- `parallel/COVERAGE/**`
- `parallel/SWEEPATLAS/**`
- `parallel/RAWMINE/**`
- `parallel/EFIELD/**`
- `parallel/PROSPECTIVE_VALIDATOR/README.md`
- `product/alpha/rules_manifest.json` (read-only)
- `parallel/PM/ALPHA_FREEZE_SPEC.md` (read-only)

## What is prospective-ready now

Prospective infrastructure already supports current-level predicates and ordered tail2/tail3 rules, candidate freezing, per-room/session isolation, live target/side evidence, and research-only verdicts.

- T24 (0x18) BODY7520/TM4 -> A5424: direct current-level revalidation candidate.
- T24 (0x18) BODY7512/TM3 -> A5440: direct current-level revalidation candidate.
- D867BA -> A3232: research-only prospective candidate; promotion remains blocked unless history/lifecycle dependence is eliminated or made safe.
- D8811E -> A3232: same lifecycle caveat.
- T20 (0x14) B0->B255 -> A5136: ordered/history candidate; research validation is possible, but promotion remains lifecycle-gated.
- T16 (0x10) B4 imminent danger: research-only danger validator; do not claim A6432 exclusivity.
- T23 (0x17) A5888 BODY4936 tail3: ordered manifest is expressible now; run only when T23 appears naturally/cheaply.

## What still needs ordered discovery before a real prospective discriminator can be frozen

- T18 (0x12) BODY4728 A4704-vs-A4712 split: first post-anchor distinct state, then pair, then triple; only add pre-anchor context if post-anchor context still fails.
- T23 (0x17) A4920 branch family: current evidence is multi-family and too small for one universal tail.
- T23 (0x17) A4792 branch set: current evidence is explicitly multi-branch and includes retarget-sensitive cycles.

## Permanently rejected / not queued as attack-specific Beta rules

- T18 (0x12) BODY4728/A4/B2/TM1 by itself -> A4704. Prospectively falsified as attack-specific.
- Any T23 (0x17) single state already known to occur before multiple eventual attacks.
- WinKawaks `+0x73 != 0` as a universal attack-active predictor.
- WinKawaks `+0x24 != 0` as a Browser attack predictor.
- Any local branch hotspot without an independently proven exact local attack label.
- Any pair/triple supported by only one resolved cycle as a production claim.
- Retired fixed-lag fingerprints that are not current prospective/current-level candidates.

## Low priority / parked

- WOF-045 short T23 BODY4976/A6/B4/TM5 single-state candidate: displaced by stronger ordered-sequence evidence and repeated zero-match/coverage limitations; do not spend rooms hunting it.
- WinKawaks `02008BE0`, cursor-flag splits, terminal-TM1 hold families, delayed timer reload, mode35 and loop/reset nodes: valuable structural discovery, but not Browser Beta rule candidates until exact local attack semantics exist.
- Stage/scene/wave-conditioned rules: authoritative labels are absent; do not infer them from filenames, rarity or type frequency.

## WOF-052L reuse rule

The Top 10 may consume a planned WOF-052L 10-room long capture without requesting extra gameplay. For T23 ordered work, use **per-room JSON**, because merged WOF-052L output does not preserve complete T23 traces. No candidate is failed merely because its type does not appear in a room batch.

## Stop condition

**BETA VALIDATION QUEUE READY**

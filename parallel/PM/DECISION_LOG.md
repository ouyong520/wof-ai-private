# WOF Future Danger AI — PM Decision Log

## 2026-09-01 — D001: Project enters Alpha transition

Decision: classify the project as **Late research / Alpha transition**, not pure research.

Reason: core feasibility and multiple prospective production-shadow rules are already proven. The marginal product value of continued generic reverse engineering is now below the value of packaging the validated subset.

## 2026-09-01 — D002: Start productization before full coverage

Decision: start Alpha runtime/loader/HUD/ruleset work immediately.

Reason: UNKNOWN can safely remain silent. Full-game coverage is a Beta/v1 concern, not a prerequisite to let real users test a conservative subset.

## 2026-09-01 — D003: Stop broad BASECAP

Decision: BASECAP v1 is complete; no broad baseline collection.

Reopen condition: a downstream lane names a specific missing discriminator that cannot be answered from retained raw.

## 2026-09-01 — D004: Stop generic EFIELD and RAWMINE

Decision: bounded high-value EFIELD mapping and current RAWMINE owner-question screening are complete.

Reason: residual unknown bytes do not currently constrain Future Danger product value.

## 2026-09-01 — D005: Park SWEEPATLAS rather than repeat the game sweep

Decision: do not ask the owner to replay the full game now.

Reason: current dominant gap is authoritative labeling/provenance, not a proven absence of physical samples. Existing GitHub corpus must be reused first.

## 2026-09-01 — D006: Ordered sequence becomes mandatory for ambiguous branches

Decision: single-state ambiguity must escalate to ordered context rather than more single-state rule fitting.

Trigger: T18 BODY4728/A4/B2/TM1 prospectively produced both A4704 and A4712.

## 2026-09-01 — D007: Browser highest priority is T18 ordered split

Decision: rank T18 post-anchor sequence discrimination above T23 room hunting.

Reason: T18 has a directly falsified single-state hypothesis and recent coverage; T23 has valuable ordered evidence but repeated recent rooms had zero T23 exposure.

## 2026-09-01 — D008: T23 stays queued, not abandoned

Decision: retain T23 A5888 tail / branch-set validation as P1/P2, preferably when coverage appears naturally or an authoritative scene is known.

## 2026-09-01 — D009: Normalize type identifiers project-wide at PM boundary

Decision: PM canonical notation is `T<decimal> (0xHH)`.

Reason: current lane artifacts mix Browser decimal T numbers and local hex-style T labels. Example: Browser T23 is local byte 0x17 and corresponds to COVERAGE row `T17`, not the COVERAGE exemplar `T23=0`.

No coverage or recap decision may compare raw T labels across lanes without numeric normalization.

## 2026-09-01 — D010: No additional research lane

Decision at initial audit: do not add another research lane.

Reason: acquisition, geometry, fields, generic mining, atlas, sequence and coverage already have owners. Current bottleneck is integration into Browser validation and product release, not missing research ownership.

This remains in force for research lanes.

## 2026-09-01 — D011: Alpha coverage philosophy

Decision: Alpha uses a small high-evidence frozen production subset; unsupported attacks remain silent.

Release emphasis: low false positive, target/retarget correctness, read-only safety, runtime identity, isolation and usable HUD.

## 2026-09-01 — D012: v1 is not 100% attack completion

Decision: v1 coverage target will be defined against an authoritative common dangerous-event denominator after COVERAGE is refreshed. Rare unsupported branches may remain silent if explicitly outside claimed support.

## 2026-09-01 — D013: Start one bounded PRODUCT / ALPHA implementation workstream

Decision: add one **product implementation workstream**, while continuing to forbid new research lanes.

Why this is justified:
1. Alpha productization is already an approved project track, not new research scope.
2. MAINLINE still owns WOF-052 prospective research and should not become the release-code owner.
3. Existing WebGL HUD and production-shadow assets make implementation immediately actionable.
4. Production/experimental isolation is an Alpha release blocker; separate implementation ownership reduces leakage risk.
5. Inputs are explicit: PM freeze spec + audited Browser sources.
6. Outputs are explicit: release runtime, frozen manifest, HUD integration, regression, Alpha RC.
7. Stop condition is explicit: stop when an Alpha RC exists and only real-Browser acceptance remains.

Reference:
- `parallel/PM/ALPHA_FREEZE_SPEC.md`
- `parallel/PM/ALPHA_ENGINEERING_TASKS.md`
- `parallel/PM/PRODUCT_ALPHA_START_PROMPT.md`

This decision supersedes any reading of D010 that would block product implementation; D010 continues to block extra research lanes.

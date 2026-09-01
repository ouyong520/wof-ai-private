# WOF Future Danger AI — Project Dashboard

Snapshot: 2026-09-01 — Alpha RC audit

## Executive status

**Stage: Alpha RC / independent QA gate, with late research continuing separately.**

A concrete Alpha RC1 now exists under `product/alpha/**`. The product implementation lane reports that its engineering stop condition is reached: six frozen rules only, isolated release runtime, fail-closed layout guard, live target/retarget, WebGL HUD, packaging and release-artifact regression are present. The release regression reconstructs the audited WOF-051 production subset at 143/143 resolved signals with zero hard-miss equivalent in the fixtures.

This is not yet an Alpha release. Two release gates remain: independent Alpha QA and one real Browser owner acceptance run. The RC report explicitly notes that the repository does not retain the raw WOF-051 per-poll stream, so its 143/143 regression is a canonical fixture reconstruction rather than a raw Browser replay.

Research state also improved: COVERAGE normalized the type notation and corrected the old T23 accounting error; current retained EFIELD material contains canonical T1 (0x01) through T31 (0x1F), including T23 (0x17). COVERAGE concludes human recap is not required. SEQMINER continues to refine ordered features but requests no recapture. WOF-052 still has no Browser run/result.

## Project metrics

| Dimension | Status | Meaning |
|---|---|---|
| Reverse engineering foundation | READY | sufficient for narrow product release work |
| Collector / retained raw | READY / STOP BROAD COLLECTION | reusable baseline exists; no generic recap justified |
| BASECAP | READY | complete for current baseline |
| GEO | CORE READY / ON DEMAND | no current Alpha blocker |
| EFIELD | READY / STOP GENERIC | bounded high-value mapping complete |
| RAWMINE | READY / PARKED | reopen only for a concrete question |
| normalized enemy type census | STRONG LOCAL ACCOUNTING | retained corpus observes canonical T1..T31; scene semantics remain incomplete |
| attack coverage | NARROW | six conservative Alpha freeze rules; breadth is a Beta/v1 issue |
| ordered-sequence research | MID-DISCOVERY | ordered context is mandatory for T18/T23 ambiguity; no new production promotion yet |
| target/retarget | STRONG IMPLEMENTATION / HUMAN CHECK PENDING | RC regression covers live retarget/side; real Browser visual check remains |
| production rules | 6 FROZEN IN RC1 | exact Alpha subset only |
| Alpha readiness | **RC1 / QA + HUMAN ACCEPTANCE PENDING** | implementation work is no longer the main blocker |
| Beta readiness | MID | requires broader validated common-event coverage and product polish |
| v1 readiness | EARLY-MID | requires stable Beta and defensible breadth denominator |

## Current lane state

### PRODUCT / ALPHA — RC1 REACHED / WAIT FOR QA

`product/alpha/ALPHA_RC_REPORT.md` declares `wof-alpha-rc1` and says only real Browser owner acceptance remains from the implementation owner's perspective.

PM adds one independent gate before spending owner Browser time: `parallel/ALPHAQA/**` must independently audit the RC. The QA bootstrap already exists at `parallel/PM/ALPHA_QA_START_PROMPT.md`.

### ALPHA QA — START NOW / P0

Read-only audit of `product/alpha/**`. QA writes only under `parallel/ALPHAQA/**`. It must either PASS with no open P0/P1 or return an exact blocking defect list to the Alpha developer.

No `parallel/ALPHAQA/**` result exists yet at this snapshot.

### MAINLINE WOF-052 — HUMAN-GATED / P1 FOR ALPHA, P0 RESEARCH

The coordinator exists, but no WOF-052 result has landed. T18 BODY4728 remains attack-ambiguous and excluded from RC1. WOF-052 is useful research but no longer blocks Alpha RC1.

### COVERAGE — REFRESH COMPLETE / PARK

Canonical notation is now `T<decimal> (0xHH)`. The retained corpus observes T1..T31. The previous `T23=0` conclusion was a notation artifact: canonical T23 (0x17) has 2,140 retained samples. Current stop decision: **human recap required: NO**.

### SEQMINER — CURRENT CORPUS NEAR SAFE STOP / NO RECAP

Latest work strengthens ordered feature contracts and cross-state timer progression. It requests no Collector recapture. Browser validation remains the correct next evidence step for attack-specific promotion.

### BASECAP / GEO / EFIELD / RAWMINE / SWEEPATLAS — STOP OR ON DEMAND

No broad collection or generic field research is justified.

## Current biggest bottlenecks

1. **Independent Alpha QA** — falsify RC1 before human acceptance.
2. **Real Browser Alpha acceptance** — only after QA has no open P0/P1.
3. **WOF-052 ordered T18 Browser evidence** — important for post-Alpha rule expansion, not required for RC1.

## Current biggest risks

1. RC1 regression is fixture reconstruction, not replay of retained raw WOF-051 polls.
2. Browser identity guard is conservative layout-based, not a cryptographic ROM hash.
3. Independent QA has not yet produced a result; developer self-tests alone are not enough for release approval.

## Current product judgment

**Do not open more discovery lanes. Move Alpha through QA, then one short real Browser acceptance.**

COVERAGE should stop rather than request recap. SEQMINER should stop when its current contract/materialization work is exhausted. Correct narrow release is now more valuable than adding speculative rules before Alpha.
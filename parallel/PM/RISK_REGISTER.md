# WOF Future Danger AI — Risk Register

Updated: 2026-09-01

## P0 / release-blocking risks

### R1 — False warning from evidence over-promotion

Risk: a retrospective, same-cycle, or local WinKawaks candidate is treated as a production predictor.

Concrete evidence: the exact T18 BODY4728/A4/B2/TM1 state prospectively led to both A4704 and A4712.

Mitigation:
- strict evidence ladder;
- production rules frozen separately from experiments;
- ordered context required for ambiguous states;
- UNKNOWN stays silent.

Release effect: Alpha blocker if experimental rules can leak into production.

### R2 — Stale target / retarget / wrong side

Risk: attack prediction is correct but warning points at the wrong player or side after target changes.

Mitigation:
- live target reread;
- preserve active-edge retarget fix;
- target/side included in every production regression;
- target-conditioned rules explicitly labelled when cross-target invariance is unproven.

Release effect: Alpha blocker for frozen rules.

### R3 — Runtime namespace or game/browser revision mismatch

Risk: a field/offset/rule is applied to a runtime representation or game revision where identity differs.

Concrete evidence: Browser and WinKawaks target-layout offsets are known not to be numerically interchangeable.

Mitigation:
- runtime/version identity guard;
- never copy local offsets into Browser/WASM;
- fail closed on unsupported identity;
- declare supported build(s).

Release effect: Alpha blocker.

## P1 risks

### R4 — Scene bias / insufficient breadth

Risk: strong rules work in researched rooms but give little value across ordinary play.

Mitigation:
- refreshed COVERAGE with authoritative type notation/scene joins;
- prioritize common enemies/common attacks;
- multi-room prospective validation;
- do not claim unsupported breadth.

Release effect: Beta/v1 blocker, not Alpha blocker.

### R5 — Low-density / rare branches

Risk: rare branches remain untested and cause misses.

Mitigation:
- keep UNKNOWN silent;
- target recaps only after scene incidence is known;
- prioritize by frequency/user value.

Release effect: acceptable in Alpha/Beta if clearly outside claimed coverage; v1 denominator must account for them honestly.

### R6 — Coverage accounting notation drift

Risk: decimal Browser `T23` is confused with hex-style local `T23`, producing false missing/coverage conclusions.

Mitigation:
- PM canonical `T<decimal> (0xHH)` notation;
- normalize COVERAGE before any recap or release breadth decision.

Release effect: blocks coverage-driven Beta/v1 claims, not narrow Alpha.

### R7 — Research scripts leaking into user runtime

Risk: discovery instrumentation changes warning behavior, creates performance issues, or enables unvalidated rules.

Mitigation:
- production/experimental module boundary;
- debug mode off by default;
- frozen rule manifest/version;
- regression on release artifact rather than research coordinator script.

Release effect: Alpha blocker.

### R8 — Runtime/HUD performance and failure behavior

Risk: polling or HUD affects gameplay or errors leave stale warnings on screen.

Mitigation:
- bounded polling/processing budget;
- stale warning TTL/clear path;
- exception isolation;
- fail closed;
- acceptance test on real Browser game.

Release effect: Alpha/Beta quality gate.

## P2 risks

### R9 — Missing stage/scene/wave/boss labels

Impact: prevents efficient targeted recap and authoritative coverage claims.

Mitigation: wait for authoritative labels or materialize joins from existing evidence before collecting.

### R10 — Browser operator cost

Impact: repeated room hunting can consume high human effort for zero target-type coverage, as happened with T23 across recent rooms.

Mitigation: rank candidates; favor T18 current P0; T23 opportunistic unless a known scene becomes available.

## Risk policy

No release date or feature may override R1-R3/R7. Missing breadth is safer than speculative warnings.

# WOF Future Danger AI — Release Readiness

Updated: 2026-09-01 — RC1 QA blocked

## Alpha — **RC1 BLOCKED / RC2 REQUIRED**

Independent QA has completed its first pass and RC1 is not releasable yet.

### QA result

Passed:
- frozen six-rule fidelity;
- T16 remains danger-only;
- T18 BODY4728/A4/B2/TM1 remains excluded as an A4704-specific production predictor;
- no T23/T24/local/discovery leakage;
- static read-only/no-input audit;
- live target reread, P1/P2/P3 mapping, side recomputation and UNKNOWN silence in core;
- stale horizon, slot-gone and type-change cleanup.

Blocked:
- **P0 ALPHAQA-001:** supported build signature is derived from layout-only evidence and can fail open on a lookalike revision;
- **P1 ALPHAQA-002:** same-type same-slot replacement can inherit a prior enemy watch;
- **P1 ALPHAQA-003:** HUD silently drops simultaneous warnings after the first row;
- **P1 ALPHAQA-004:** supported load path still requires researcher-level manual live Worker-console selection.

### Alpha gate status

| Gate | Status |
|---|---|
| frozen production rules | PASS QA |
| release/runtime separation | PASS QA |
| positive runtime/build identity | **FAIL P0** |
| same-type replacement safety | **FAIL P1** |
| simultaneous warning presentation | **FAIL P1** |
| ordinary-user bootstrap | **FAIL P1** |
| live target/retarget/side core | PASS QA, lifecycle fix required |
| UNKNOWN/stale silence | PASS QA |
| static no RAM writes / no input | PASS QA |
| independent RC1 QA | COMPLETE / BLOCKED |
| RC2 implementation | OPEN |
| fresh RC2 QA retest | OPEN |
| real Browser acceptance | WAIT |

### Release sequence

1. RC2 fixes all four P0/P1 blockers;
2. parallel runtime identity audit supplies positive guard evidence or one minimal human probe;
3. fresh independent QA retests RC2;
4. only after QA clears, run one short real Browser acceptance;
5. if acceptance passes, mark Alpha released.

Do not use owner Browser time on RC1 acceptance while blockers remain.

## Beta — MID

Beta requirements remain broader validated common-event coverage, ordered ambiguity resolution, multi-danger polish, easier install/update, extended stability and defensible breadth accounting. Those are not reasons to delay the bounded RC2 safety fixes.

## v1 — EARLY-MID

Unchanged: stable Beta, trustworthy breadth denominator, intentional silence for unsupported events, no P0 release risk, normal-user packaging and support matrix.

## Current release judgment

**RC1 is a useful engineering milestone but failed independent release QA. The fastest safe route is RC2 fixes + identity audit in parallel -> fresh QA -> one Browser acceptance.**
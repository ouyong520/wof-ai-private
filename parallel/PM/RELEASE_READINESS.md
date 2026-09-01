# WOF Future Danger AI — Release Readiness

Updated: 2026-09-01 — RC1 audit

Statuses are management bands, not fake precision.

## Alpha — **RC1 / QA + HUMAN BROWSER ACCEPTANCE PENDING**

A bounded release candidate now exists at `product/alpha/**` as `wof-alpha-rc1`.

The implementation owner has completed the Alpha engineering checklist: six frozen rules, release/runtime isolation, fail-closed Browser layout guard, live target/retarget, WebGL HUD, UNKNOWN silence policy, minimal loader path, static no-write/no-input audit and release regression.

The release regression reconstructs the audited WOF-051 production subset at 143/143 resolved fixture signals with zero hard-miss equivalent. It also checks that the ambiguous T18 BODY4728 candidate remains silent and that T16 B4 is danger-only rather than A6432-exclusive.

Important limitation: the repository does not retain the raw WOF-051 per-poll Browser stream, so this is a canonical fixture reconstruction rather than a raw production-stream replay. Therefore real Browser acceptance remains mandatory.

### Alpha gate status

| Gate | Status | PM judgment |
|---|---|---|
| frozen production manifest | PASS RC1 | six PM freeze rules only; explicit exclusions retained |
| release/runtime separation | PASS RC1 | no WOF-0xx research coordinator in release path |
| loader/bootstrap | PASS IMPLEMENTATION | one dual-context loader path documented; real Browser acceptance pending |
| runtime identity / fail-closed | PASS OFFLINE / HUMAN CHECK PENDING | positive layout guard exists; unsupported mismatch must remain silent |
| live target + retarget + side | PASS OFFLINE / HUMAN CHECK PENDING | regression covers P1->P3 and UNKNOWN silence |
| non-console WebGL HUD | PASS IMPLEMENTATION / VISUAL CHECK PENDING | real game visual/interference check required |
| UNKNOWN / stale silence | PASS OFFLINE | must be observed once in Browser acceptance |
| release-artifact regression | PASS | 143/143 canonical production-subset fixture resolution |
| no RAM writes / no input injection | PASS STATIC / HUMAN INTERFERENCE CHECK PENDING | static audit clean; runtime status reports must confirm readOnly/ramWrites=0/inputInjection=false |
| independent Alpha QA | **OPEN** | `parallel/ALPHAQA/**` has not produced a result yet |
| real Browser RC acceptance | **OPEN** | perform only after QA has no open P0/P1 |

### Alpha release decision

**Do not call Alpha released yet.**

Release sequence is now:

1. independent Alpha QA;
2. Alpha developer fixes any P0/P1 findings;
3. QA rechecks current artifact;
4. one short real Browser owner acceptance;
5. if acceptance passes, mark Alpha released.

No extra attack research is required before Alpha.

## Beta — MID

Beyond Alpha, Beta should add:

- broader validated common-event coverage;
- validated ordered rules for important ambiguous branches;
- broader multi-room/scene evidence;
- polished multi-danger prioritization;
- easier install/config/update flow;
- extended runtime overhead/stability checks;
- automated release regression against retained real Browser traces when such traces become available;
- defensible common-event coverage denominator.

COVERAGE now has normalized type accounting and explicitly says broad human recap is not currently required. Stage/scene/wave/boss semantics remain the main breadth-label gap.

## v1 — EARLY-MID

V1 still requires stable Beta, trustworthy breadth accounting, high coverage of the common dangerous-event set, intentional silence for unsupported ambiguity, no unresolved P0 release risks and normal-user packaging/support documentation.

`100% all attacks` is not the criterion.

## Current release judgment

**RC1 is real and narrow. The fastest safe route is independent QA -> one real Browser acceptance -> Alpha release.**
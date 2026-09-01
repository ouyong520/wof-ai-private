# WOF Future Danger AI — Project Dashboard

Snapshot: 2026-09-01 — RC1 QA-blocked audit

## Executive status

**Stage: Alpha RC1 blocked by independent QA; RC2 repair stage now required.**

Alpha RC1 is a real narrow candidate, but independent QA found one P0 and three P1 release blockers. Therefore RC1 must not advance to human Browser acceptance yet.

The blockers are concrete and bounded:
- runtime/build identity is only a layout check and can fail open on an unsupported lookalike revision;
- same-type same-slot replacement can inherit a prior enemy watch;
- HUD silently renders only the first simultaneous warning;
- the supported load path still assumes researcher-level manual Worker-console selection.

Frozen-rule fidelity itself passed QA, including T16 danger-only semantics and exclusion of the ambiguous T18 BODY4728 A4704-specific candidate.

Research/accounting lanes are no longer the bottleneck. COVERAGE is complete and says human recap NO. SEQMINER has exhausted the current retained corpus to its safe boundary and requests no recapture.

## Project metrics

| Dimension | Status | Meaning |
|---|---|---|
| reverse-engineering foundation | READY | sufficient for narrow product work |
| collector / retained raw | READY / STOP BROAD COLLECTION | no generic recap justified |
| frozen Alpha rules | 6 / FIDELITY QA PASS | release set itself is not the current blocker |
| runtime identity | **P0 BLOCKED** | needs positive supported-build recognition, not layout-only signature |
| enemy episode lifecycle | **P1 BLOCKED** | same-type slot replacement can inherit a warning |
| simultaneous warning HUD | **P1 BLOCKED** | current HUD silently drops warnings after first row |
| user bootstrap | **P1 BLOCKED** | current path still assumes manual live Worker console selection |
| read-only / no input | STATIC QA PASS | real Browser interference check remains later |
| target / retarget / side | CORE QA PASS / LIFECYCLE BLOCKED | live target logic good; episode transfer risk must be fixed |
| Alpha readiness | **RC1 BLOCKED -> RC2 REQUIRED** | no human acceptance yet |
| Beta readiness | MID | unchanged; broader work waits for Alpha closure |
| v1 readiness | EARLY-MID | unchanged |

## Current lane state

### ALPHA QA RC1 — COMPLETE AT BLOCKED

QA produced `parallel/ALPHAQA/AUDIT_STATUS.md`, `FINDINGS.md` and an independent adversarial harness. This stage is complete; do not keep extending the same RC1 QA thread.

### PRODUCT / ALPHA RC2 — START NOW / P0

New implementation stage bootstrap:
- `parallel/PM/ALPHA_RC2_FIX_START_PROMPT.md`

It owns `product/alpha/**` repairs and must close all four QA blockers without widening the production rule set.

### ALPHA RUNTIME IDENTITY AUDIT — START NOW / PARALLEL P0

Read-only supporting lane bootstrap:
- `parallel/PM/ALPHA_RUNTIME_IDENTITY_AUDIT_START_PROMPT.md`

It searches retained Browser evidence for a real positive supported-build identifier and writes only under `parallel/ALPHAID/**`.

### COVERAGE — COMPLETE / PARK

Normalized refresh complete; T23 notation error corrected; human recap required NO.

### SEQMINER — CURRENT CORPUS EXHAUSTED / PARK

v3 contract is ready. No generic offline step or recapture is justified until a reopen trigger appears.

### MAINLINE WOF-052 — DEFER HUMAN TIME UNTIL ALPHA RELEASE GATE

Still useful for post-Alpha rule expansion, but not an Alpha blocker.

## Current biggest bottlenecks

1. close ALPHAQA-001 positive runtime/build identity;
2. close ALPHAQA-002/003/004 in RC2;
3. fresh independent QA retest of RC2;
4. only then one real Browser Alpha acceptance.

## Current product judgment

**Do not spend owner gameplay time yet. Run RC2 fixes and the identity audit in parallel, then retest.**

The project should close completed work threads rather than keep them alive: COVERAGE, SEQMINER and RC1 QA can stop now.
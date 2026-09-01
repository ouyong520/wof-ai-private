# WOF Future Danger AI — Parallel Acceleration Plan

Updated: 2026-09-01 — RC2 repair allocation

## Goal

Use parallelism only where outputs are disjoint and directly shorten the Alpha critical path.

## Current concurrent work allocation

### Stream 1 — PRODUCT / ALPHA RC2 FIX — P0
Owner: new RC2 implementation thread.
Bootstrap: `parallel/PM/ALPHA_RC2_FIX_START_PROMPT.md`.

Owns `product/alpha/**` repairs for the four RC1 QA blockers. Must not widen the frozen rule set.

### Stream 2 — ALPHA RUNTIME IDENTITY AUDIT — PARALLEL P0
Owner: new read-only identity thread.
Bootstrap: `parallel/PM/ALPHA_RUNTIME_IDENTITY_AUDIT_START_PROMPT.md`.

Treats `product/alpha/**` as read-only and writes only `parallel/ALPHAID/**`. Its purpose is to unblock the hardest P0 identity question while RC2 fixes the other blockers.

### Stream 3 — PM / RELEASE COORDINATION — CONTINUOUS
Owner: PM thread.

Reads GitHub, routes findings, prevents conflicting writes and opens a fresh QA-retest stage only when RC2 is ready.

## Completed / stop now

### ALPHA QA RC1 — COMPLETE AT BLOCKED
The first independent QA stage is finished. Preserve its artifacts as test requirements for RC2; do not keep extending the same stage.

### COVERAGE — COMPLETE / PARK
Human recap = NO. Reopen only for a future concrete Beta/v1 coverage question.

### SEQMINER — CURRENT CORPUS EXHAUSTED / PARK
v3 is ready; no recapture or generic offline mining remains justified.

### Original PRODUCT / ALPHA RC1 implementation — COMPLETE
Do not revive the old stage; RC2 is a new work thread.

## Human-time sequencing

1. no Alpha Browser acceptance while RC2 blockers remain;
2. if identity audit proves retained evidence insufficient, run only its single minimal Browser probe;
3. after RC2 fresh QA PASS, run one short Alpha Browser acceptance;
4. WOF-052 comes after/alongside post-Alpha research, not before release safety closure.

## Do not open now

No new generic RAM/EFIELD/GEO/full-sweep/duplicate-sequence/attack-discovery lanes. Do not split RC2 into multiple implementation threads that edit the same `product/alpha/**` files.

## Throughput judgment

The highest-value parallelism is now **one implementation owner + one read-only identity investigator + PM coordination**. More implementation threads would create merge conflicts; keeping finished COVERAGE/SEQMINER/RC1-QA threads alive would create noise rather than speed.
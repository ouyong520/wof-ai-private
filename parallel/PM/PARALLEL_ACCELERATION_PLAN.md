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
Owner: read-only identity thread.
Bootstrap: `parallel/PM/ALPHA_RUNTIME_IDENTITY_AUDIT_START_PROMPT.md`.

Writes only `parallel/ALPHAID/**` and finds a safe positive supported-build identity mechanism or one minimal Browser probe.

### Stream 3 — ALPHA ENEMY LIFECYCLE AUDIT — PARALLEL P1
Owner: read-only lifecycle thread.
Bootstrap: `parallel/PM/ALPHA_LIFECYCLE_AUDIT_START_PROMPT.md`.

Writes only `parallel/ALPHALIFE/**` and defines a Browser-proven or conservative invalidation policy preventing same-type slot-reuse watch inheritance.

### Stream 4 — ALPHA USER BOOTSTRAP AUDIT — PARALLEL P1
Owner: read-only bootstrap thread.
Bootstrap: `parallel/PM/ALPHA_BOOTSTRAP_AUDIT_START_PROMPT.md`.

Writes only `parallel/ALPHABOOT/**` and selects the smallest reliable normal-user path that avoids manual live Worker-console selection.

### Stream 5 — PM / RELEASE COORDINATION — CONTINUOUS
Owner: PM thread.

Reads GitHub, merges support-lane conclusions into the RC2 critical path, prevents conflicting writes, and opens fresh QA only when RC2 is ready.

## Completed / stop now

### ALPHA QA RC1 — COMPLETE AT BLOCKED
Preserve its artifacts as RC2 test requirements; do not keep extending that same QA stage.

### COVERAGE — COMPLETE / PARK
Human recap = NO.

### SEQMINER — CURRENT CORPUS EXHAUSTED / PARK
v3 ready; no generic offline mining or recapture justified.

### Original PRODUCT / ALPHA RC1 implementation — COMPLETE
RC2 is a new stage/thread.

## Conflict rule

Only Stream 1 may edit `product/alpha/**`. Streams 2/3/4 are read-only support lanes with separate result directories. This allows four execution threads without merge races.

## Human-time sequencing

1. no Alpha Browser acceptance while RC2 blockers remain;
2. if a support audit proves retained evidence insufficient, run only its exact minimal Browser probe;
3. after RC2 fresh QA PASS, run one short Alpha Browser acceptance;
4. WOF-052 follows the Alpha safety gate for post-Alpha rule expansion.

## Do not open now

No generic RAM/EFIELD/GEO/full-sweep/duplicate-sequence/attack-discovery lanes. Do not create a second implementation owner touching `product/alpha/**`.

## Throughput judgment

This restores four useful execution threads while keeping write ownership clean: **RC2 implementation + identity audit + lifecycle audit + bootstrap audit**. Finished COVERAGE/SEQMINER/RC1-QA threads should be closed rather than kept alive for thread count.
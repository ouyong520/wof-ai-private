# WOF Future Danger AI — Parallel Acceleration Plan

Updated: 2026-09-01 — RC1 reallocation

## Goal

Keep useful work parallel without duplicating implementation, wasting owner gameplay, or reopening closed collection lanes.

## Current concurrent work allocation

### Stream 1 — PRODUCT / ALPHA implementation — RC1 REACHED / MAINTENANCE ONLY
Owner: dedicated Product Alpha thread.

Engineering stop condition has been reached at `wof-alpha-rc1`. The implementation thread should not keep adding features. It should only respond to concrete Alpha QA P0/P1 findings until release.

### Stream 2 — ALPHA QA — START NOW / P0
Owner: one independent QA thread.
Bootstrap: `parallel/PM/ALPHA_QA_START_PROMPT.md`.

Read-only audit of `product/alpha/**`; findings under `parallel/ALPHAQA/**` only.

Stop: QA PASS with no open P0/P1, or exact defect list handed to Product Alpha.

### Stream 3 — MAINLINE WOF-052 — HUMAN-GATED RESEARCH
Owner: existing MAINLINE Browser thread + owner gameplay.

Still the highest-value ordered T18 research task, but not an Alpha blocker. Resume when owner Browser time is available. Do not replace Alpha acceptance with WOF-052 work.

### Stream 4 — SEQMINER — FINISH CURRENT MATERIALIZATION / THEN PARK
Owner: existing SEQMINER thread.

Latest work may finish its v3 feature/contract outputs from retained data. No new Collector request is allowed. Park once current retained material is exhausted.

### Stream 5 — COVERAGE — REFRESH COMPLETE / PARK
Owner: COVERAGE thread.

Normalized refresh is complete. Current physical recap decision is NO. Stop this thread unless later Beta/v1 evidence creates a concrete bounded coverage question.

### Stream 6 — PM / release coordination — CONTINUOUS
Owner: PM thread.

Audit GitHub, route QA findings, keep closed lanes closed, and move RC1 to human Browser acceptance once QA clears.

## Human-time sequencing

Owner gameplay is the scarce resource. Use it in this order:

1. Alpha RC1 Browser acceptance after QA clears P0/P1;
2. WOF-052 T18 Browser run;
3. any later precise prospective validator;
4. targeted WinKawaks recap only if COVERAGE later proves it necessary.

## Do not open now

No new generic:
- RAM mining;
- EFIELD mapping;
- GEO research;
- full-game sweep;
- duplicate sequence mining;
- extra Alpha implementation thread;
- speculative rule-discovery thread.

## Throughput judgment

The project no longer needs more thread count for its own sake. The fastest safe throughput is to let QA attack the existing RC1 while SEQMINER finishes retained-data work and COVERAGE parks. Adding overlapping threads before QA returns would increase conflict rather than speed.
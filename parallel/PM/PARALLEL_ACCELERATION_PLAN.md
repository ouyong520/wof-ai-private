# WOF Future Danger AI — Parallel Acceleration Plan

Updated: 2026-09-01

## Goal

Increase throughput without opening duplicate research or causing concurrent-write conflicts.

## Authorized concurrent work

### Stream 1 — PRODUCT / ALPHA implementation — P0
Owner: dedicated Product Alpha thread.
Scope: release runtime, frozen rules, loader/bootstrap, identity guard, fail-closed behavior, live target/retarget, HUD integration, release regression.
Bootstrap: `parallel/PM/PRODUCT_ALPHA_START_PROMPT.md`.
Stop: Alpha RC exists or only real Browser acceptance remains.

### Stream 2 — MAINLINE WOF-052 — P0 / human gated
Owner: existing MAINLINE Browser thread + owner gameplay.
Scope: ordered T18 context discovery separating A4704 vs A4712 while preserving production audits.
Stop: shortest stable ordered discriminator is identified, then hand off to a later prospective validator.

### Stream 3 — SEQMINER — ACTIVE EXISTING LANE
Owner: existing SEQMINER thread.
Scope: consume retained corpus, ordered-cycle/retarget/reference timeline mining, feed Browser validation queue.
Do not request broad collection.
Stop: current retained corpus is exhausted for product-relevant ordered candidates.

### Stream 4 — COVERAGE refresh — P1
Owner: one dedicated COVERAGE refresh thread.
Scope: normalize T identifiers, ingest current SWEEPATLAS/SEQMINER, materialize cross-tabs, distinguish physical vs analysis vs label gaps, recompute minimal recap decision.
Bootstrap: `parallel/PM/COVERAGE_REFRESH_START_PROMPT.md`.
Stop: refreshed matrix says either human recap NO or identifies exactly one bounded residual recap need.

### Stream 5 — PM / release coordination — continuous
Owner: PM thread.
Scope: audit GitHub, prevent duplication, update priorities, decide promotion/release gates, request owner action only when truly required.

## Not authorized now

Do not open more research lanes for:
- generic RAM mining;
- new EFIELD mapping;
- broad GEO work;
- another full-game sweep;
- duplicate sequence mining;
- speculative attack-rule discovery without an owner question.

## Why not add Alpha QA as a separate thread yet

A separate Alpha QA/release-audit thread becomes valuable only after Product Alpha produces a concrete release artifact or stable implementation commit. Starting it earlier would duplicate implementation work and increase merge/conflict risk.

Trigger to open Alpha QA:
- Product Alpha publishes a candidate frozen manifest + runtime/HUD integration or labels an Alpha RC candidate.

At that point PM should create a read-mostly release audit task focused on regression, identity guard, fail-closed behavior, target/retarget, no writes, UNKNOWN silence, and acceptance checklist.

## Throughput rule

Prefer 4 high-value parallel streams with disjoint outputs over 8 overlapping threads.

If two streams begin editing the same product file family, PM will serialize them rather than allow race/conflict.

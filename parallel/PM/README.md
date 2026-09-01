# WOF Future Danger AI — PM Control Plane

Updated: 2026-09-01

This directory is the project-level coordination layer for WOF / Warriors of Fate / 三国志II Future Danger AI.

## Authority

GitHub is the project source of truth. PM reads MAINLINE and all parallel lanes, but PM writes only `parallel/PM/**` by default.

PM does not replace lane-owned technical analysis. It decides:

- what matters to the product now;
- which lanes continue or stop;
- which discovery candidates deserve Browser cost;
- which evidence can enter a release ruleset;
- Alpha / Beta / v1 release gates;
- what, if anything, requires the human owner.

## Current project phase

**Late research / Alpha transition.**

The project is no longer proving whether Future Danger is possible. Core Browser selector/target/geometry and multiple prospective production-shadow rules exist. The primary management problem is now:

1. convert the mature validated subset into a frozen user-facing Alpha;
2. use ordered sequence/context to resolve known single-state ambiguity;
3. expand coverage without allowing local discovery evidence to leak into Browser production.

Research and productization now run in parallel. Full enemy/attack completion is not an Alpha prerequisite.

## Evidence ladder

Never collapse these levels:

1. retrospective correlation
2. same-cycle discovery
3. ordered-sequence discovery
4. prospective validation
5. multi-room prospective validation
6. production-shadow
7. production

WinKawaks discovery is never Browser/WASM production proof. Numeric local offsets are never promoted directly across namespaces. Zero coverage is never predictor failure.

## Canonical type notation

Cross-lane type notation is currently inconsistent. PM canonical notation is:

`T<decimal> (0xHH)`

Examples:

- Browser/Mainline `T18` = local type byte `0x12` = COVERAGE hex-style row `T12`.
- Browser/Mainline `T23` = local type byte `0x17` = COVERAGE hex-style row `T17`.
- Browser/Mainline `T16` = local type byte `0x10` = COVERAGE hex-style row `T10`.
- Browser/Mainline `T20` = local type byte `0x14` = COVERAGE hex-style row `T14`.

No PM decision may compare `Txx` labels from different lanes without normalizing the numeric value first.

## Current lane policy

- MAINLINE: ACTIVE — Browser validation and production rule promotion.
- BASECAP: STOP broad baseline acquisition; reopen only for a named missing discriminator.
- GEO: CORE CLOSED; on-demand only for a concrete product/research geometry question.
- EFIELD: STOP generic mapping.
- RAWMINE: STOP generic mining; reusable analyzer only.
- SWEEPATLAS: PARK at current safe labeling boundary; resume when authoritative labels/new auditable input appear.
- SEQMINER: v1 infrastructure/current-corpus mining COMPLETE; its ranked queue feeds MAINLINE, and offline work resumes only on new discriminative input.
- COVERAGE: ACTIVE as accounting/recompute lane, but must refresh stale snapshots when SWEEPATLAS/SEQMINER change; no generic recap.
- PRODUCT TRACK: ACTIVE NOW — Alpha freeze, runtime/HUD/loader hardening, compatibility and regression.

## No broad collection rule

No new large WinKawaks Collector sweep is authorized. Reuse retained raw first. A future physical recap must be a minimal, specifically justified scene/wave set selected from an audited coverage gap.

## Files

- `PROJECT_DASHBOARD.md` — project state and metrics
- `ROADMAP.md` — Alpha/Beta/v1 path
- `ACTIVE_PRIORITIES.md` — current 3–5 priorities and stops
- `DEPENDENCY_MAP.md` — lane/evidence dependencies
- `RISK_REGISTER.md` — product/program risks
- `RELEASE_READINESS.md` — release gates
- `DECISION_LOG.md` — durable PM decisions
- `VALIDATION_QUEUE.md` — Browser cost priority
- `OWNER_ACTIONS.md` — only work requiring the human owner

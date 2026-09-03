# WOF Unified Collector V12 — Reuse / Legacy Readiness Preflight

Status: PM-AUTHORIZED READ-ONLY PREFLIGHT

This is **not V12 implementation** and does not authorize V12 production changes before V11 terminal COMPLETE.

## Dedup

- dedupProtocol: `v2`
- dedupKey: `wof.unified-collector.v12.preflight.reuse-legacy-readiness`
- dedupMode: `exclusive`
- stageId: `WOF_UNIFIED_COLLECTOR_V12_REUSE_LEGACY_READINESS_PREFLIGHT_V1`

Before work, perform canonical dedup v2 preflight against current main, RESULTs, claims, recent equivalent commits and this START_PROMPT. If equivalent ACTIVE/COMPLETE/superseded, return NO EXECUTION.

## Purpose

Shorten the V12 critical path while V11 W1/W2 finish. Produce a durable, read-only implementation recommendation for the final OneClick Unified Collector / legacy retirement stage.

## Hard boundary

- Do not modify `ouyong520/wof-winkawaks-bridge` production code.
- Do not modify `training/farm/**`, `product/alpha/**`, launcher/runtime code, schemas, CI, task/result implementation or data-stack implementation.
- Do not acquire the future V12 umbrella implementation claim.
- Do not declare V12 COMPLETE.
- Do not start Browser/WOF/WinKawaks/Training Farm runtimes.
- Do not rerun V11 tests.

## Required work

1. Read latest `AGENTS.md`, `GLOBAL_GITHUB_REUSE_FIRST_POLICY.md`, V9→V12 roadmap and current V10/V11 artifacts.
2. Inventory all current collection-related Windows entrypoints, launchers, services, status/health surfaces and overlapping legacy collector paths in both repos. Classify each candidate for future V12 as one of:
   - `MIGRATED_TO_UNIFIED_AGENT`
   - `COMPATIBILITY_ONLY`
   - `TEST_FIXTURE_ONLY`
   - `DEPRECATED_DO_NOT_USE`
   - `REMOVED_CANDIDATE`
3. Perform GitHub/official-ecosystem reuse-first research for the V12 owner-runtime/launcher/status packaging problem. At minimum evaluate maintained candidates relevant to:
   - Windows one-click/service/process supervision;
   - process/resource discovery/health;
   - optional lightweight local status UI or tray UX only if it reduces total lifecycle cost;
   - packaging/deployment simplicity.
4. For meaningful external candidates, record:
   - current maintenance/activity;
   - deployment/integration complexity;
   - exact reusable functions/modules;
   - license and material supply-chain risk;
   - secondary-development suitability.
5. Make explicit decisions: `DIRECT_USE`, `ADAPT`, `FORK`, `REFERENCE_ONLY`, `SELF_BUILD`, or `DEFER`.
6. Recommend the **simplest V12 MVP** minimizing new code, dependencies, Owner steps and maintenance burden. Prefer existing V10/V11 launcher/Agent surfaces when they are already sufficient; do not add infrastructure just because it exists.
7. Identify any legacy path whose retirement would be unsafe before V12 acceptance, and any path that can be cleanly deprecated without implementation risk.

## Required durable output

Write:

`parallel/PM/WOF_UNIFIED_COLLECTOR_V12_REUSE_LEGACY_READINESS_PREFLIGHT_RESULT.md`

The RESULT must include:

- exact repo HEADs inspected;
- dedup verdict;
- legacy inventory/classification;
- GitHub candidate comparison table;
- maintenance/deployment/reuse/license assessment;
- explicit reuse decisions;
- simplest MVP recommendation;
- implementation-ready V12 checklist;
- explicit statement: `V12 implementation authority not claimed`.

Then mark only this preflight claim COMPLETE. Do not touch V11 or future V12 umbrella claims.

## Stop condition

`COMPLETE — V12 REUSE / LEGACY READINESS PREFLIGHT — IMPLEMENTATION-READY RECOMMENDATION DURABLE`

or precise `BLOCKED` if a genuinely external fact prevents the research.

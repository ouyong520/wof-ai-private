# WOF Unified Collector V12 — Reuse / Legacy Readiness Preflight Recovery V2

stageId: `WOF_UNIFIED_COLLECTOR_V12_REUSE_LEGACY_READINESS_PREFLIGHT_RECOVERY_V2`
dedupProtocol: `v2`
dedupKey: `wof.unified-collector.v12.preflight.reuse-legacy-readiness-recovery-v2`
dedupMode: `exclusive`

Priority: **P1 — prepare V12 final consolidation without touching V11 implementation**

## PM recovery authority

Owner has explicitly confirmed that all previously assigned Collector workers are now idle. The original V12 reuse/legacy readiness preflight claim remains `ACTIVE`, but no durable preflight RESULT or completion claim exists. This is therefore a PM-authorized stale-claim recovery under `STAGE_DEDUP_GUARD.md` section 8.

This recovery supersedes execution ownership of, but does **not** overwrite/delete/reuse, the historical occupied claim:

- `wof.unified-collector.v12.preflight.reuse-legacy-readiness`
- stage `WOF_UNIFIED_COLLECTOR_V12_REUSE_LEGACY_READINESS_PREFLIGHT_V1`

Acquire a fresh canonical/stage claim for this recovery key before research work.

## Parent authority

Original read-only preflight:

`parallel/PM/WOF_UNIFIED_COLLECTOR_V12_REUSE_LEGACY_READINESS_PREFLIGHT_START_PROMPT.md`

Final roadmap:

`parallel/PM/COLLECTOR_V9_TO_V12_FINAL_UNIFIED_COLLECTOR_ROADMAP.md`

Global reuse policy:

`parallel/PM/GLOBAL_GITHUB_REUSE_FIRST_POLICY.md`

The sibling acceptance/fixture readiness preflight is already COMPLETE and must not be duplicated:

`parallel/PM/WOF_UNIFIED_COLLECTOR_V12_ACCEPTANCE_FIXTURE_READINESS_PREFLIGHT_RESULT.md`

## Dedup preflight

Re-read current main, the original preflight claim/stage, any newer successor/recovery and any newly created reuse/legacy RESULT.

If equivalent successor work is ACTIVE, return:

`ALREADY ACTIVE / CLAIMED — NO EXECUTION`

If a durable successor RESULT is already COMPLETE, return:

`ALREADY COMPLETE — NO EXECUTION`

Otherwise acquire and verify this recovery claim/stage before substantive research.

## Hard boundary

This remains **read-only V12 readiness work**, not V12 implementation.

Do not:

- modify `ouyong520/wof-winkawaks-bridge` production code;
- modify Training Farm, Alpha, schemas, Agent, adapters, workflow or launcher production code;
- acquire V12 umbrella implementation authority;
- start Browser/WOF/WinKawaks/Training Farm runtimes;
- rerun V10/V11 tests;
- duplicate the completed acceptance/fixture preflight.

## Required work

Finish the original preflight end-to-end from current Git truth:

1. Inventory every current collection-related Windows entrypoint, launcher, service, status/health surface and overlapping historical collector path in both repos.
2. Classify each as exactly one future V12 disposition where applicable:
   - `MIGRATED_TO_UNIFIED_AGENT`
   - `COMPATIBILITY_ONLY`
   - `TEST_FIXTURE_ONLY`
   - `DEPRECATED_DO_NOT_USE`
   - `REMOVED_CANDIDATE`
3. Perform bounded GitHub/official-ecosystem reuse-first research for final Windows one-click start/stop/status/process-health packaging only where a recent durable decision is not already sufficient.
4. For meaningful candidates record current maintenance, deployment/integration complexity, exact reusable modules, license/supply-chain considerations and secondary-development suitability.
5. Make explicit `DIRECT_USE` / `ADAPT` / `FORK` / `REFERENCE_ONLY` / `SELF_BUILD` / `DEFER` decisions.
6. Prefer the smallest V12 MVP. Reuse V10/V11 Agent/launchers/status surfaces where adequate; do not add Docker, Redis, broker, service framework, tray framework or other infrastructure unless it demonstrably lowers total lifecycle cost.
7. Consume the completed acceptance/fixture preflight so the final V12 recommendation identifies which legacy/launcher changes require only deterministic CI and which acceptance remains real-Windows-only.
8. Produce an implementation-ready V12 legacy-retirement checklist, including any path unsafe to retire before final acceptance.

## Required durable output

Write:

`parallel/PM/WOF_UNIFIED_COLLECTOR_V12_REUSE_LEGACY_READINESS_PREFLIGHT_RECOVERY_V2_RESULT.md`

The RESULT must include:

- exact repo HEADs inspected;
- stale predecessor authority and recovery dedup verdict;
- complete legacy inventory/classification;
- external candidate comparison table;
- maintenance/deployment/reuse/license assessment;
- explicit reuse decisions;
- simplest V12 MVP recommendation;
- implementation-ready legacy retirement/status/launcher checklist;
- acceptance implications consumed from the sibling completed preflight;
- explicit `V12 implementation authority not claimed` statement.

Then mark only this recovery canonical/stage claim COMPLETE. Leave the predecessor ACTIVE claim intact as stale historical evidence superseded by this recovery.

Terminal success token:

`COMPLETE — V12 REUSE / LEGACY READINESS PREFLIGHT RECOVERY V2 — IMPLEMENTATION-READY RECOMMENDATION DURABLE`

If problems occur, continue automatic diagnosis within this read-only scope until COMPLETE or a genuinely external precise BLOCKED. Do not create extra QA or rerun already-passing tests. Report sparingly.
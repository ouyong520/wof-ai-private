# WOF Unified Collector V12 — Post-Freeze Crossline Revalidation V1 — START PROMPT

Status: **PM-AUTHORIZED POST-FREEZE REVALIDATION**

## Why this exists

Owner reported that another product/thread crossed scope boundaries. V12 was previously terminal COMPLETE, but its bridge candidate changed after the earlier terminal result from `9b7c6897149cc7de615dd372e072d7b21e9de8f7` to current `65831cb0cf3ec3fcfdfe0f20bade5ee24deafc95`, and `wof-ai-private` subsequently reconciled V12 evidence/claims while unrelated Alpha work was also active.

This is **not V13**, not a feature reopen, and not permission to create another Collector. It is an independent post-freeze contamination / authority revalidation of the current V12 final candidate.

## Repositories

- `ouyong520/wof-winkawaks-bridge`
- `ouyong520/wof-ai-private`

## Current candidate to verify, not assume

- bridge candidate: `65831cb0cf3ec3fcfdfe0f20bade5ee24deafc95`
- bridge tree recorded by current V12 authority: `6102471dde9c4f8b6b6f85fed3d1c7cc54d41d55`
- current V12 RESULT: `parallel/PM/WOF_UNIFIED_COLLECTOR_V12_FINAL_CONSOLIDATION_ONECLICK_LEGACY_RETIREMENT_RESULT.md`
- current terminal acceptance bundle: `parallel/PM/WOF_UNIFIED_COLLECTOR_V12_FINAL_CONSOLIDATION_ONECLICK_LEGACY_RETIREMENT_ACCEPTANCE_BUNDLE.json`

## Dedup

- protocol: canonical dedup v2
- dedup key: `wof.unified-collector.v12.post-freeze-crossline-revalidation-v1`
- mode: exclusive parent audit authority
- stageId: `WOF_UNIFIED_COLLECTOR_V12_POST_FREEZE_CROSSLINE_REVALIDATION_V1`

Do duplicate preflight first. If equivalent ACTIVE/COMPLETE/superseded authority exists, NO EXECUTION.

## Hard invariant

There is exactly one maintained Collector product:

`one Unified Collector Agent -> browser-wasm + winkawaks + stable-retro-fbneo adapters`

Adapters are modules, not separate Collectors. Maintain one public lifecycle entrypoint, one Agent, one Git task/status/result plane, one dataset/provenance stack, one retention/storage stack, one DuckDB warehouse/query plane, and one analysis/reuse planner.

## Revalidation scope

Independently verify current Git truth, with special attention to cross-product/thread contamination:

1. compare exact V12 terminal baseline and current bridge main; classify every post-terminal change and changed file;
2. prove no Alpha production, Training Farm control code, unrelated product runtime, second Collector service/daemon, second queue/data plane, or foreign authority was introduced into V12;
3. verify `65831cb...` only changes intended V12 lifecycle/acceptance surfaces and that no later bridge commit silently supersedes it;
4. verify lifecycle identity, stale-stop behavior, health/readiness instance binding, canonical entrypoint identity, single named mutex, and three adapter health visibility;
5. verify one Git task/status/result plane and existing V11 data-plane ancestry remain intact;
6. verify final focused V12 CI is bound to exact current candidate and machine acceptance remains valid;
7. verify V12 W1, umbrella canonical, stage, terminal recovery, RESULT and acceptance bundle all point to one coherent final candidate and no stale ACTIVE V12 claim remains;
8. scan recent `wof-ai-private` cross-product commits around V12 reconciliation and prove Alpha/Training Farm/other product authority did not overwrite V12 evidence, and V12 authority did not overwrite their product files;
9. preserve real-runtime facts as BLOCKED/DEFERRED where evidence is unavailable; do not manufacture Windows/WOF or live 10-worker proof.

## Change boundary

Initial work is audit/verification only.

- Do **not** modify bridge production, BATs, adapters, data stack, Training Farm, Alpha, or existing terminal RESULT/claims during subworkstream auditing.
- Tests may be executed only within the directly affected V12 boundary; do not rerun historical V10/V11 merely for confidence unless audit finds material shared-SUT drift after their green run.
- If a real defect or authority inconsistency is found, document the exact file/commit/evidence and return it to the coordinator. The coordinator may perform only the minimum V12-scoped correction explicitly required by the evidence; no scope expansion.

## Durable terminal revalidation result

Write:

`parallel/PM/WOF_UNIFIED_COLLECTOR_V12_POST_FREEZE_CROSSLINE_REVALIDATION_V1_RESULT.md`

Result must state one of:

- `PASS — V12 POST-FREEZE CROSSLINE REVALIDATION — CURRENT FINAL CANDIDATE CLEAN / FEATURE FROZEN`
- `BLOCKED — V12 POST-FREEZE CROSSLINE REVALIDATION — <precise defect/contamination>`

Record exact bridge HEAD/tree, changed-file classification, CI/evidence IDs, authority consistency, cross-product contamination verdict, and whether any repair was required.

No V13/V14. Feature remains frozen on PASS.

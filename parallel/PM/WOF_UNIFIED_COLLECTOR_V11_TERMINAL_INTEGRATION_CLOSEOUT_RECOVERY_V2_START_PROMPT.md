# WOF Unified Collector V11 — Terminal Integration + Closeout Recovery V2

stageId: `WOF_UNIFIED_COLLECTOR_V11_TERMINAL_INTEGRATION_CLOSEOUT_RECOVERY_V2`
dedupProtocol: `v2`
dedupKey: `wof.unified-collector.v11.terminal-integration-closeout-recovery-v2`
dedupMode: `exclusive`

Priority: **P0 — unblock V12 final consolidation**

## PM recovery authority

Owner has explicitly confirmed that all previously assigned Collector workers are now idle. Current Git still shows the original V11 umbrella claim and W1 exporter/coordinator subclaim as `ACTIVE`, but no V11 terminal RESULT, no terminal integration commit, and no maintained V3–V11 terminal CI authority exists. Therefore those ACTIVE records are stale execution ownership, not evidence of a live worker.

This is a PM-authorized recovery under `STAGE_DEDUP_GUARD.md` section 8. It supersedes execution ownership of, but does **not** overwrite/delete/reuse, these historical occupied claims:

- canonical: `wof.unified-collector.v11.training-farm-adapter-unified-task-data-stack`
- W1 subclaim: `wof.unified-collector.v11.workstream.training-farm-exporter-coordinator`
- stage: `WOF_UNIFIED_COLLECTOR_V11_TRAINING_FARM_ADAPTER_UNIFIED_TASK_DATA_STACK_V1`

Historical claims remain intact as stale predecessor evidence. This recovery must acquire its own fresh canonical/stage claims using the recovery dedup key above.

## Exact current durable starting point

Re-read current main before work. At PM authorization time:

- `ouyong520/wof-winkawaks-bridge` main = `8905732d93032a814e79d6fb3dd8077df0828ac0`
- W2 durable sub-result = `parallel/PM/WOF_UNIFIED_COLLECTOR_V11_W2_ADAPTER_SCHEMA_AGENT_RESULT.md`
- W2 subclaim = `SUBCOMPLETE`
- W3 durable sub-result = `parallel/PM/WOF_UNIFIED_COLLECTOR_V11_W3_UNIFIED_DATA_STACK_SUBRESULT.md`
- W3 subclaim = `SUBCOMPLETE`
- W1 Training Farm exporter implementation already exists in `training/farm/**`, including ROM-free one/ten-worker fixture evidence.
- V12 acceptance/fixture readiness preflight is already COMPLETE at `parallel/PM/WOF_UNIFIED_COLLECTOR_V12_ACCEPTANCE_FIXTURE_READINESS_PREFLIGHT_RESULT.md` and should be consumed as a gap map, not rerun.

Parent V11 authority remains:

`parallel/PM/WOF_UNIFIED_COLLECTOR_V11_TRAINING_FARM_ADAPTER_UNIFIED_TASK_DATA_STACK_START_PROMPT.md`

Parallel split authority:

`parallel/PM/WOF_UNIFIED_COLLECTOR_V11_PARALLEL_3_WORKER_DISPATCH.md`

## Dedup preflight

Before meaningful execution, re-read current main, predecessor claims/results, this recovery prompt, any newer V11 successor/recovery, and any V11 terminal RESULT/CI created after this prompt.

If a newer equivalent V11 terminal recovery is ACTIVE, return:

`ALREADY ACTIVE / CLAIMED — NO EXECUTION`

If V11 already has a newer durable terminal COMPLETE successor, return:

`ALREADY COMPLETE — NO EXECUTION`

Otherwise acquire and verify this recovery canonical claim and matching stage claim before task work.

## Scope — finish V11, do not rebuild it

Do **not** reimplement W1/W2/W3. Reuse the current durable component work.

Your job is to finish only the missing terminal integration/authority:

1. Re-read exact W1 exporter contract, W2 `stable-retro-fbneo` adapter/v2 Agent contract, and W3 source-aware V4–V9 facade.
2. Determine whether any real cross-component integration defect remains. Fix only concrete V11 integration defects required for terminal correctness.
3. Ensure the source-owned Training Farm exporter output is consumable by the actual W2 adapter without synthetic contract assumptions. If not already proven by equivalent current evidence, add the minimum ROM-free W1 -> W2 integration fixture/join.
4. Ensure an actual unified v2 Training Farm result/envelope can flow into the W3 source-aware catalog/query/reuse stack without losing `sourceNamespace`, worker/runtime/result/artifact provenance. If not already proven by equivalent current evidence, add the minimum W2 -> W3 integration fixture/join.
5. Preserve V10 Browser/WASM + WinKawaks compatibility and one Git queue/status/result plane.
6. Preserve source separation: `browser-wasm`, `winkawaks`, `stable-retro-fbneo`. Never infer one source's RAM/semantic authority from another.
7. Preserve Collector safety: `readOnly=true`, `writesGameMemory=false`, `inputInjection=false`. Collector must not call Training Farm reset/step/load_state, choose actions, launch workers, or bypass R0.5/real-WOF gates.
8. Do not start real 2–10 Training Farm workers for validation. Use existing deterministic ROM-free fixtures.
9. Do not modify Alpha/product code.

## Testing cadence

Treat terminal V11 as one coherent integration candidate.

- Do not rerun historical PASS suites merely for confidence.
- Reuse W2/W3 focused PASS evidence unless terminal integration materially changes their SUT.
- After all missing integration wiring/fixtures are complete, run **one maintained V3–V11 terminal regression/CI on the exact final candidate**.
- That terminal gate must cover the required current integration boundary, V10 compatibility, three-source task/result/data-stack authority, source isolation and safety.
- Fix concrete failures as one related defect cluster, then retest only the affected/final terminal gate.

## Required durable completion

Write:

`parallel/PM/WOF_UNIFIED_COLLECTOR_V11_TERMINAL_INTEGRATION_CLOSEOUT_RECOVERY_V2_RESULT.md`

The RESULT must record:

- exact final repo HEAD/tree identities;
- predecessor W1/W2/W3 authorities consumed;
- any integration defects fixed;
- exact terminal workflow/run/job and test counts;
- W1 -> W2 exporter/adapter evidence;
- W2 -> W3 result/data-stack evidence;
- Browser/WASM + WinKawaks compatibility;
- three-source provenance/source-isolation guarantees;
- Training Farm no-control safety guarantees;
- statement that the predecessor ACTIVE V11/W1 claims are stale historical authority superseded by this recovery and were not overwritten;
- explicit V11 terminal verdict.

Then mark **only this recovery canonical/stage claim** COMPLETE with RESULT authority. Do not overwrite predecessor claim files.

Terminal success token:

`COMPLETE — WOF UNIFIED COLLECTOR V11 TERMINAL INTEGRATION RECOVERY V2 — THREE SOURCE NAMESPACES ON ONE COLLECTOR DATA PLANE COMPLETE`

After this success V12 may begin. Do not implement V12 in this stage.

If problems occur, do not stop at one error. Continue automatic diagnosis and repair of all safe in-scope issues until COMPLETE or a genuinely Owner-required precise BLOCKED. Complete the coherent integration module before the final focused regression; do not test step-by-step. Report sparingly.
# WOF Unified Collector V11 — Owner-authorized 3-worker parallel dispatch

Owner authorization: 2026-09-03

This file supplements, but does not replace:

`parallel/PM/WOF_UNIFIED_COLLECTOR_V11_TRAINING_FARM_ADAPTER_UNIFIED_TASK_DATA_STACK_START_PROMPT.md`

The Owner explicitly authorizes three implementation workers to work concurrently on V11. This overrides the normal single-worker execution preference only for the non-overlapping workstream split below. Canonical dedup v2, source authority, testing cadence, no-force-push, and terminal RESULT rules remain mandatory.

## One V11 terminal authority

There is still exactly one terminal V11 module authority:

- umbrella dedup key: `wof.unified-collector.v11.training-farm-adapter-unified-task-data-stack`
- terminal RESULT: `parallel/PM/WOF_UNIFIED_COLLECTOR_V11_TRAINING_FARM_ADAPTER_UNIFIED_TASK_DATA_STACK_RESULT.md`

Worker W1 is the coordinator and is the only worker authorized to acquire/close the umbrella V11 canonical/stage claim and to write the terminal V11 RESULT. W2/W3 must not create a second umbrella claim or terminal V11 RESULT.

Each subworker also uses a distinct non-equivalent subworkstream dedup key so parallel execution does not violate canonical dedup:

- W1 exporter/coordinator: `wof.unified-collector.v11.workstream.training-farm-exporter-coordinator`
- W2 adapter/schema: `wof.unified-collector.v11.workstream.adapter-schema-agent`
- W3 data stack: `wof.unified-collector.v11.workstream.unified-data-stack`

Subworkstream claims are coordination authority only. `SUBCOMPLETE` does not mean V11 COMPLETE.

## Current baselines at dispatch

Re-read current main before work; do not blindly reuse these if main has advanced.

- `ouyong520/wof-winkawaks-bridge` V10 final baseline: `31ec55650ccce29fad60dcab2ca099425a1ecc0b`
- `ouyong520/wof-ai-private` observed main at dispatch preparation: `1771ec889170b386d87123fc0a1b458d9da78ae8`
- V10 maintained regression: 187/187 PASS at run `33710701482`

## Shared hard boundaries

All workers must preserve:

- one Unified Collector product and one Git queue/status/result plane;
- sources: `browser-wasm`, `winkawaks`, `stable-retro-fbneo`;
- source-specific provenance and no cross-source offset guessing;
- Collector `readOnly=true`, `writesGameMemory=false`, `inputInjection=false`;
- no Alpha production modification;
- no Collector ownership of Training Farm reset/step/action/PPO/savestate search/worker scheduling;
- current Training Farm stage guard: do not start 2/4/8/10 real workers for V11 verification;
- deterministic fixtures may prove protocol/isolation for up to 10 already-active workers.

No worker may force-push, overwrite another workstream, or edit another workstream's owned files merely to make integration easier. Re-read main before each push and rebase/merge safely when main advances.

# W1 — Training Farm exporter + coordinator

Primary repository: `ouyong520/wof-ai-private`.

W1 owns:

1. V11 umbrella canonical/stage claim and W1 subworkstream claim;
2. narrow Training Farm read-only exporter/observer contract under `training/farm/**`;
3. worker registry/evidence atomicity, generation/sequence/stale detection, runtime/ROM/Farm/memory-layout/episode/root/branch provenance where actually available;
4. ROM-free deterministic exporter fixtures/self-checks;
5. no second Git consumer/daemon/catalog/warehouse/planner under Training Farm;
6. after W2/W3 subworkstream commits are visible on current main, final integration review, V3–V11 coherent regression/CI, durable terminal V11 RESULT, and umbrella canonical/stage COMPLETE.

W1 must not implement a training controller. Exporter may observe existing action/result metadata but must not call `reset`, `step`, `step_frame`, `load_state`, choose actions, alter workers, or authorize R0.5.

During the parallel phase W1 should avoid editing bridge files owned by W2/W3. Final integration patches are allowed only after rereading their landed commits and should be minimal.

W1 stop condition: do not declare V11 COMPLETE until W2/W3 subworkstreams are integrated, full V3–V11 regression/CI is green, terminal RESULT is durable, and umbrella canonical/stage claims are COMPLETE. If W2/W3 are not yet landed when W1 finishes exporter work, keep umbrella ACTIVE and report exact integration dependency; do not fake terminal completion.

# W2 — stable-retro-fbneo adapter + task v2 + Agent routing

Primary repository: `ouyong520/wof-winkawaks-bridge`.

W2 owns only the adapter/control-contract slice:

- `bridge/adapters/stable_retro_fbneo.py` (new or equivalent);
- necessary strict extensions in `bridge/adapters/base.py`;
- necessary strict dispatch/health integration in `bridge/unified_collector_agent.py`;
- V11 unified task/status/result schema versioning (prefer explicit v2 if V10 v1 meaning would otherwise change);
- Training Farm task examples;
- focused adapter/Agent/schema tests and fixtures.

Required selectors: strict `ONE`, `WORKER_IDS`, `ALL_ACTIVE`, bounded to 1..10 and fail-closed on ambiguity/excess/conflicting generation.

Required actions must map only to exporter evidence that actually exists. Do not invent unsupported data types.

W2 must preserve strict V10 v1 Browser/WinKawaks compatibility and must not modify Training Farm source files or generic dataset/storage/analysis/warehouse/planner modules owned by W1/W3.

W2 produces a durable subworkstream RESULT recording exact commits/tests and marks only its own subworkstream claim `SUBCOMPLETE`/`COMPLETE-SUBWORKSTREAM` according to the existing claim schema. It must explicitly state `V11 terminal authority not claimed`.

# W3 — source-aware unified data stack

Primary repository: `ouyong520/wof-winkawaks-bridge`.

W3 owns the generic data/research slice and should avoid W2 adapter/Agent/schema files.

Generalize V4–V9 concepts into one source-aware stack for all three namespaces:

- immutable dataset/provenance registration;
- V5-derived retention/archive/pressure policy integration;
- V6-derived research-only analysis envelopes/readers;
- V7-derived bounded scheduling/batch integration where source-appropriate;
- V8 DuckDB 1.5.5 multi-source warehouse/query with source/provenance columns preserved;
- V9 reuse-first planning generalized without fuzzy cross-source semantic matching;
- explicit historical registration/migration provenance rather than rewriting old evidence.

Prefer additive generic modules/wrappers where that minimizes merge conflict and preserves stable V3–V10 code. Do not duplicate a second catalog, cleanup daemon, warehouse truth, queue, or planner authority.

W3 must not edit Training Farm runtime/exporter files and should not edit `bridge/adapters/base.py`, `bridge/adapters/stable_retro_fbneo.py`, or `bridge/unified_collector_agent.py` unless a concrete unavoidable interface defect is first documented; leave integration adapters/hooks for W1/W2 when possible.

W3 produces a durable subworkstream RESULT with exact commits/tests and marks only its distinct subworkstream claim complete. It must explicitly state `V11 terminal authority not claimed`.

## Integration / conflict rules

1. All three workers re-read both mains and this dispatch before substantive work.
2. W1 acquires umbrella authority; W2/W3 never acquire the umbrella key.
3. Each worker acquires only its distinct subworkstream claim before substantive work.
4. Land small coherent commits; no force push.
5. If another worker advances main, rebase/merge safely and preserve their changes.
6. File-ownership boundaries above are mandatory during parallel implementation.
7. W1 performs final cross-workstream integration only after W2/W3 durable sub-results/commits are visible.
8. Full V3–V11 regression and final CI belong to W1 terminal closeout; W2/W3 run focused implementation-owned checks only.
9. Only W1 writes terminal V11 RESULT and closes umbrella canonical/stage claims.
10. Only after V11 terminal COMPLETE may PM stage V12.

## Final V11 success condition

Exactly one Unified Collector Agent consumes one Git task plane and can route strict tasks to Browser/WASM, WinKawaks, or Training Farm exporter evidence; all three sources feed one source-aware dataset/storage/analysis/warehouse/reuse stack while retaining independent runtime provenance and safety authority.

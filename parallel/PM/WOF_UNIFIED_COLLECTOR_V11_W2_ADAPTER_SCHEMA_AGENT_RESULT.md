# WOF Unified Collector V11 — W2 Adapter / Schema / Agent Subworkstream — RESULT

Date: 2026-09-03

## Disposition

**SUBCOMPLETE — W2 adapter/control-contract slice complete; V11 terminal authority not claimed.**

This is a W2 subworkstream handoff only. It does not declare WOF Unified Collector V11 COMPLETE, does not close the V11 umbrella canonical/stage claims, and does not authorize V12.

## Authority

- parent stageId: `WOF_UNIFIED_COLLECTOR_V11_TRAINING_FARM_ADAPTER_UNIFIED_TASK_DATA_STACK_V1`
- W2 dedup key: `wof.unified-collector.v11.workstream.adapter-schema-agent`
- W2 claim token: `v11-w2-c5d403b032c4f4901aa98627126b5e31`
- dispatch authority: `parallel/PM/WOF_UNIFIED_COLLECTOR_V11_PARALLEL_3_WORKER_DISPATCH.md`
- implementation repository: `ouyong520/wof-winkawaks-bridge`
- V10 completed baseline: `31ec55650ccce29fad60dcab2ca099425a1ecc0b`
- reviewed W2 handoff HEAD: `8905732d93032a814e79d6fb3dd8077df0828ac0`
- reviewed W2 handoff tree: `c57b389370e4526cb2459d64aff562f3c2f001a4`

## Current-state / dedup preflight

Before closeout, current repository authority was re-read rather than relying on the forwarded task text.

- bridge `main` is exactly `8905732d93032a814e79d6fb3dd8077df0828ac0`.
- W2 claim remained `ACTIVE` with the exact claim token above.
- no durable W2 subworkstream RESULT already existed at this path.
- the V11 umbrella canonical claim remains owned by W1 and remains outside W2 closeout authority.
- the exact-head W2 focused GitHub Actions run is green.
- no material W2 SUT change occurred after that exact-head run, so already-passing tests were not rerun merely for closeout.
- no current W2 implementation defect was found during handoff review.

## W2 delivered contract

### Unified task / status / result v2

W2 added an explicit V11 v2 contract without changing the closed V10 v1 meaning:

- `wof_unified_collector_task_v2`
- `wof_unified_collector_status_v2`
- `wof_unified_collector_result_v2`

The v2 source allowlist is exactly:

- `browser-wasm`
- `winkawaks`
- `stable-retro-fbneo`

V10 v1 remains closed to its existing Browser/WinKawaks namespaces. Browser and WinKawaks v1 compatibility is therefore preserved rather than silently reinterpreted as v2.

All v2 tasks still route through the existing single Unified Collector Git control plane and Agent result authority. W2 did not introduce a Training Farm-specific Git queue/status/result plane.

### Training Farm read-only adapter

`bridge/adapters/stable_retro_fbneo.py` consumes only source-owned exporter evidence already produced by Training Farm. It does not import or instantiate Training Farm control runtime objects and does not call or own:

- `reset`
- `step`
- `step_frame`
- `load_state`
- training action choice/injection
- worker launch
- worker scheduling/orchestration
- PPO/RL policy execution

Maintained safety remains:

- `readOnly=true`
- `writesGameMemory=false`
- `inputInjection=false`

The adapter is bound to `stable-retro-fbneo` exporter record/artifact authority and does not guess Browser or WinKawaks offsets.

### Worker selectors

Training Farm v2 selectors are strict and bounded:

- `ONE`: requires exactly one eligible active worker and fails closed otherwise.
- `WORKER_IDS`: requires 1..10 unique canonical worker IDs and resolves only requested eligible workers.
- `ALL_ACTIVE`: requires explicit native-integer `maxWorkers` in 1..10 and fails closed if the eligible active set exceeds that bound.

The hard selected-worker ceiling remains 10. The focused fixture proves the 10-worker protocol/isolation path without launching 10 real emulator workers.

### Artifact / worker-generation isolation

The adapter verifies source-owned `current.json` and immutable artifacts before returning PASS evidence. The reviewed implementation binds or verifies, as available:

- worker ID and worker generation;
- generation start;
- monotonic sequence / publication time;
- record identity SHA-256;
- capture binding SHA-256;
- immutable artifact bytes and SHA-256;
- runtime identity and ROM/Farm source identity;
- memory-layout identity;
- episode ID/generation;
- fork-set/root/branch identity;
- logical-frame/step metadata;
- exporter source identity and evidence-kind availability.

Pre/post continuity mismatch withholds PASS. Artifact replacement/tampering fails closed. Each selected worker is validated in an isolated result path, so a corrupt worker cannot be silently spliced into or attributed to another worker, and one worker failure cannot hide a valid sibling result.

## Exact-head focused CI

Workflow: `Collector V11 W2 Adapter Agent Regression`

- workflow run: `33714170008`
- job: `100519730722` (`v11-w2-focused`)
- exact checkout: `8905732d93032a814e79d6fb3dd8077df0828ac0`
- conclusion: **success**

Maintained gates on that exact HEAD:

- compile W2-owned Python surface: PASS
- closed V10 Unified Agent compatibility regression: **36/36 PASS**
- W2 Training Farm adapter / Agent / worker-isolation focused regression: **19/19 PASS**
- v2 task/status/result schema checks: PASS
- ONE / WORKER_IDS / ALL_ACTIVE example coverage: PASS
- Training Farm no-control-authority static safety gate: PASS

The focused regression includes the required fail-closed and isolation cases, including 10 active workers, 11/over-bound rejection, unknown/ineligible worker selection, stale records, artifact SHA replacement, generation/episode continuity changes, missing evidence kinds, exact WORKER_IDS selection, and per-worker artifact-failure isolation.

Because the reviewed bridge `main` still equals the exact CI head above, no duplicate closeout rerun was performed.

## Material W2 implementation commits

- `9f30b4004f26bca5c7995089efc3a24bd2e2a223` — strict unified v2 contract
- `699a6d89d3705cf67010d382a8cdf2393f0ace98` — unified task v2 schema
- `707c7f67071cec678b2c54f1d762b08956d3b434` — unified status v2 schema
- `39f9abc8c6e12221d2b349c11f831ededa19cc5b` — unified result v2 schema
- `4c6e6a3eea1e20e0e8f97a6209feae4826cc2c2e` — `stable-retro-fbneo` read-only adapter
- `9303d611067ab228ce2cfca5e33b3920c5298333` — bind adapter to source exporter v1
- `d6fbe1f181e34c031600dbb9c5e35971843b15d2` — align v2 task schema to exporter IDs
- `08febc966834416a86399294b9a8dea5dac420ad` — expose Training Farm source adapter
- `f9715f8b577e076bc254fb84f3b16b0ba1fc7730` — route unified v2 Training Farm tasks through the Agent
- `6821e22891bf3e0d01fc56555fde74e75f234447` — harden exporter-backed v2 validation
- `485c1cd97fb6c89268e12f54b22ba3a12e2219f1` — ONE example
- `15a5a2e2a349af3a2ba0a9e0206eba3074b5641a` — WORKER_IDS example
- `1e8cc821e9baa1399c53a303f467dbc546a98fc2` — ALL_ACTIVE example
- `bfb791ec4b967bb317e27805bd4a20b4054dc74f` — exporter adapter / v2 Agent regression
- `7e3f3220dad9b94852e146036a36dd867479a094` — preserve closed V10 compatibility gate
- `ef18049508ff16ef883e8d2f85bd94d3fc94daa4` — focused adapter/Agent regression
- `8db4e88d97b25db091cfd6cac69f89ff6a19b4ab` — verify artifact authority before envelope and isolate worker failures
- `bee854999c62e75f6d35bf7af747ef0cd66f19b6` — per-worker artifact failure isolation coverage
- `8905732d93032a814e79d6fb3dd8077df0828ac0` — focused worker-isolation regression coverage

## Primary W2 files

- `bridge/adapters/base.py`
- `bridge/adapters/stable_retro_fbneo.py`
- `bridge/adapters/__init__.py`
- `bridge/unified_collector_agent.py`
- `schemas/unified_collector_task_v2.schema.json`
- `schemas/unified_collector_status_v2.schema.json`
- `schemas/unified_collector_result_v2.schema.json`
- `examples/unified_collector_training_farm_one_v2.example.json`
- `examples/unified_collector_training_farm_worker_ids_v2.example.json`
- `examples/unified_collector_training_farm_all_active_v2.example.json`
- `tests/test_unified_collector_v11_adapter.py`
- `tests/test_unified_collector_v11_worker_isolation.py`
- `.github/workflows/collector-v11-w2-regression.yml`

## Handoff boundary

W2 is ready for W1 terminal integration. The following are explicitly **not** claimed by this RESULT:

- W1 Training Farm exporter completion/authority;
- W3 source-aware generic data-stack completion/authority;
- full V3–V11 terminal regression/CI;
- V11 terminal durable RESULT;
- V11 umbrella canonical/stage COMPLETE;
- V12 authorization or implementation.

**V11 terminal authority not claimed.**

## Verdict

**SUBCOMPLETE — W2 stable-retro-fbneo adapter + task/status/result v2 + Unified Agent routing + bounded worker/artifact/generation isolation + V10 compatibility are complete at reviewed HEAD `8905732d93032a814e79d6fb3dd8077df0828ac0`; handoff to W1 integration authority.**

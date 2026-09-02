# WinKawaks Collector V9 — Reuse-first Experiment Planner / Gap-to-Batch Compiler — RESULT

## Verdict

**COMPLETE — WINKAWAKS COLLECTOR V9 REUSE-FIRST EXPERIMENT PLANNER / GAP-TO-BATCH COMPILER — REUSE-BEFORE-RECAPTURE PLANNING COMPLETE**

## Authority

- stage: `WINKAWAKS_COLLECTOR_V9_REUSE_FIRST_EXPERIMENT_PLANNER_GAP_TO_BATCH_COMPILER_V1`
- canonical dedup key: `winkawaks.collector.v9.reuse-first-experiment-planner-gap-to-batch`
- claim token: `v9-e484d836e86743108de6dc871adb532f-03b51ff514cf`
- implementation repository: `ouyong520/wof-winkawaks-bridge`
- continuation anchor supplied by Owner: `744faaccc1d984d291a35e2d01d8c64028c832a9`
- final bridge HEAD: `9f4e9b4ff918e0abc75d4ffd5f727d39ea991249`
- final bridge tree: `a3c92ead3bb818b887617bd5e9533fa4e3d55900`
- V9 remained the same canonical/stage authority; no Recovery generation was opened and V10 was not entered.

## Exact V9 contracts and final blobs

- request schema/version: `wof_collector_experiment_request_v1`
- planner result schema/version: `wof_collector_experiment_plan_v1`
- planner tool: `wof-winkawaks-collector-v9-experiment-planner-v1`
- request identity: `wof_collector_v9_experiment_request_identity_v1`
- allocation formula/version: `wof_collector_v9_reuse_allocation_v1`

| Path | Final blob | Purpose |
|---|---|---|
| `bridge/experiment_planner.py` | `33103336f19205b291e930b926c246d29d9bd6b5` | exact reuse planner, CURRENT gate, gap compiler, freshness and CLI |
| `tests/test_experiment_planner.py` | `6306327003cad724438e523d681aa5bf3848053e` | deterministic V9 implementation self-check |
| `schemas/collector_experiment_request_v1.schema.json` | `60f1a3570b185e62334e4c56269832213bab5602` | strict request contract |
| `schemas/collector_experiment_plan_v1.schema.json` | `6fae586860767e60da59b2eb44c942725afd6818` | strict derived plan contract |
| `examples/collector_experiment_request_v1.example.json` | `e39c67d91112019c97c26c3d2e498bb6686e0c1a` | versioned request example |
| `docs/COLLECTOR_V9_REUSE_FIRST_EXPERIMENT_PLANNER.md` | `5e01335037e40009545a2c8a5d61b9e41e388aaa` | V9 authority/CLI/operating documentation |
| `.github/workflows/collector-python-smoke.yml` | `94498a7b4dac2f941526134610f03395ffc2bfa0` | maintained V3–V9 current-head smoke/regression |
| `.gitignore` | `882f34484edc27b91742a7cb4a76d927523f0e03` | ignores disposable `derived/planning/` artifacts |

## Reuse eligibility and deterministic allocation

Default reuse is fail-closed:

- source namespace must be exactly `winkawaks`;
- current V4 lifecycle must be `VALID`;
- current V4 integrity must be `VERIFIED`;
- dataset must be active reusable under current V4/V8 authority;
- authoritative artifact availability must be explicit;
- every material field named by the condition match must be present and canonically exact;
- missing material metadata is not a match;
- no fuzzy text similarity, embeddings, inferred scene/action, filename inference or semantic promotion is used.

Cross-experiment reuse preserves the source dataset's original experiment/repeat/trial grouping. V9 only records that existing dataset as reused evidence for the new request; it does not rewrite acquisition provenance.

A dataset can satisfy at most one repeat slot across the whole request. Allocation is independent of warehouse/query row order. When `preferLocalArtifacts=true`, deterministic preference is local authoritative artifact, then verified archive, then explicit remote reference, with `datasetId` ascending as the deterministic tie-break. When local preference is disabled, authoritative exact candidates use `datasetId` ordering. V9 never counts multiple execution records as multiple copies of one canonical dataset.

## V8 CURRENT/source-set binding

Planning requires the current V8 warehouse schema/tool and exact `sourceNamespace=winkawaks` with state `CURRENT`, non-empty `buildId`, and non-empty `sourceSetDigest`. `STALE`, `CONFLICT`, `INVALID`, namespace mismatch or incompatible V8 schema/tool fails closed with an instruction to use the existing V8 refresh/rebuild authority; V9 does not implement a second indexing engine.

Every plan binds the exact V8 build/source-set identity. Planning reads the identity before and after allocation and rejects an identity change during planning. `verify-plan` marks a saved result `STALE` if the V8 state is no longer CURRENT, if build/source-set identity changed, or if re-planning against the same current source authority produces a different allocation fingerprint.

## V4/V5 authority preservation

V4 remains the dataset identity/lifecycle/integrity/grouping authority. V9 validates authoritative V4 records and does not promote invalid, unreviewed, partial, stale or conflicting evidence.

V5 remains storage/archive authority. A verified archived dataset is represented as reusable evidence with an explicit retrieval notice and is not converted into needless new capture. V9 does not restore, archive, prune or delete artifacts. Local/verified-archive/remote availability facts are query inputs only and do not create storage mutation authority.

## Gap computation and V7 compiler reuse

The gap set is exactly the requested repeat slots left unsatisfied after deterministic exact reuse allocation. Each gap retains `experimentId`, `conditionId`, repeat slot, exact match facts, a precise no-candidate reason and deterministic V7 step identity.

For non-zero gaps V9 compiles only those missing slots into the existing V7 `wof_collector_batch_plan_v1` contract. Ordering is request condition order plus repeat-slot ordinal. Every generated step has repeat count 1; `maxConcurrentCaptures=1`; current V7 safety, storage and catalog policy fields are reused; and the generated plan must pass `bridge.batch_acquisition.validate_plan` and its canonical `planSha256` path before V9 returns it.

V9 does not publish `tasks/queue/**`, does not call `run_queued_task()`, and does not execute collection. Execution remains a later explicit V7 action.

If zero gaps remain, disposition is `REUSE_COMPLETE_NO_CAPTURE_REQUIRED`; no empty/fake V7 batch and no `v7PlanSha256` are manufactured.

## CLI and derived output

The final CLI exposes exactly:

- `validate-request`
- `plan`
- `verify-plan`
- `show`
- `emit-v7-plan`

There is no execution command. `emit-v7-plan` writes only a locally validated derived plan. Output is constrained under `derived/planning/**`; absolute paths and parent traversal are rejected. Derived planning artifacts are ignored by Git by default.

## External reuse decisions

- DuckDB `1.5.5`: existing V8 dependency, `DIRECT_USE`; no fork and no V9 replacement engine.
- V7 batch plan/validator/execution authority: `REUSE`.
- V8 warehouse/current source-set authority: `REUSE`.
- OR-Tools: `DEFER`.
- Polars: `DEFER`.
- Prefect: `DEFER`.

V9 adds no new runtime dependency beyond current V7/V8 requirements.

## Deterministic implementation self-check and maintained CI

Maintained GitHub Actions workflow: `Collector Python smoke check`

- workflow run ID: `33660656297`
- job ID: `100350093277`
- run number: `18`
- exact tested HEAD: `9f4e9b4ff918e0abc75d4ffd5f727d39ea991249`
- exact tested tree: `a3c92ead3bb818b887617bd5e9533fa4e3d55900`
- result: `success`
- runner Python: CPython `3.12.14`
- observed direct dependencies: APScheduler `3.11.3`, DuckDB `1.5.5`
- workflow permission remains `contents: read` (with metadata read supplied by Actions); no CI writeback or mutable PASS receipt exists.

Exact test commands are the maintained workflow's V3–V9 module boundary, including:

- `python -m unittest discover -s tests -p 'test_collector_segmented*.py' -v`
- `python -m unittest -v tests/test_dataset_catalog.py`
- `python -m unittest discover -s tests -p 'test_storage_retention*.py' -v`
- `python -m unittest -v tests/test_analysis_reader.py`
- `python -m unittest -v tests/test_batch_acquisition.py`
- `python -m unittest -v tests/test_research_warehouse.py`
- `python -m unittest -v tests/test_experiment_planner.py`

Exact regression counts from the successful run:

- V3 segmented: **15/15 PASS**
- V4 dataset catalog: **20/20 PASS**
- V5 storage retention + recovery: **28/28 PASS**
- V6 segment-aware analysis reader: **31/31 PASS**
- V7 batch acquisition: **20/20 PASS**
- V8 research warehouse: **16/16 PASS**
- V9 experiment planner: **21/21 PASS**
- combined V3–V9 regression cases: **151/151 PASS**

The V9 21-case self-check covers strict unknown-key/numeric validation, deterministic request identity, duplicate condition rejection, capture-template alignment, V3 segmented template reuse, exact material matching, global no-double-counting, deterministic candidate order, local/archive preference, archive retrieval reuse, exact gaps, zero-gap behavior, V7 validation, source-set stale detection, plan fingerprint mutation detection, output path traversal, no queue/execution path, a bounded hundreds-of-datasets/dozens-of-conditions fixture, and a synthetic V8 DuckDB reader-to-planner integration.

## Current-repository V8 → V9 smoke

The same successful workflow rebuilt current V4 authority, checked V5 health, rebuilt/verified/queried V8, then planned the V9 example against that exact V8 database.

- current V4 records: `33`
- current V4 default active/reusable: `8`
- V8 build ID: `wkv8-122aac682638c79182d75ea4c70416d1197f818e84a5373c4de5d19ec437169f`
- V8 source-set digest: `122aac682638c79182d75ea4c70416d1197f818e84a5373c4de5d19ec437169f`
- V8 verification: `CURRENT`
- V9 example request SHA-256: `10cbbde9ea9a50510b9477219afb4685e9894dcf9212550f23a1f988e325a0e6`
- V9 planning disposition: `GAPS_COMPILED_CAPTURE_NOT_EXECUTED`
- requested repeats: `2`
- reused datasets for that exact example/current source set: `0`
- missing capture slots: `2`
- generated V7 steps: exactly `2`, one per gap
- queue published: `false`
- collection executed: `false`

The example intentionally does not claim that unrelated retained datasets are semantically reusable; exact material mismatch correctly produces gaps.

## Safety/source isolation

Final V9 invariant:

```text
sourceNamespace=winkawaks
readOnly=true
writesGameMemory=false
inputInjection=false
researchOnly=true
semanticAuthority=false
```

V9 does not start/control WinKawaks, read or write game memory directly, inject input, navigate scenes, use Lua/macros, step savestates, call Training Farm, publish Collector queue tasks, or execute V7 batches. It does not modify or block Alpha, Transport, Recorder, PYLAUNCH, OneClick or Training Farm lanes.

## Concrete defect disposition

No new implementation defect surfaced after the landed exact planner/self-check boundary. The remaining interrupted-state work was completed by adding the derived planning ignore rule and extending the maintained Collector workflow into one current-head V3–V9 regression/current-repository V8→V9 smoke. That integration passed without requiring a V9 source/schema/test defect patch, so no artificial churn was introduced.

## Intentional limitations / future extensions

- MVP matching remains exact structured metadata only; semantic/fuzzy/embedding planning is intentionally absent.
- shared evidence semantics across conditions are intentionally not enabled; one dataset is globally single-use per request.
- V9 only plans and verifies. It does not retrieve archives/remotes or execute capture.
- OR-Tools optimization, Polars dataframes and Prefect orchestration remain deferred.
- broader experiment optimization belongs to a future separately authorized stage; this V9 result does not enter V10.

## Closeout

After this RESULT commit is durable, the V9 canonical and matching stage claim are to transition from `ACTIVE` to `COMPLETE` using the same claim token and the same RESULT/bridge/workflow terminal authority.
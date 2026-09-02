# WinKawaks Collector V9 — Reuse-First Experiment Planner / Gap-to-Batch Compiler

stageId: `WINKAWAKS_COLLECTOR_V9_REUSE_FIRST_EXPERIMENT_PLANNER_GAP_TO_BATCH_COMPILER_V1`
dedupProtocol: `v2`
dedupKey: `winkawaks.collector.v9.reuse-first-experiment-planner-gap-to-batch`
dedupMode: `exclusive`

Priority: **P1 reusable datasets / acquisition-efficiency automation**

## Duplicate-forward preflight — mandatory

Before any substantive work, re-read current `main` in both repositories and verify:

- this exact START_PROMPT;
- canonical/stage claims for this V9 dedup key;
- any same/equivalent V9 RESULT;
- any newer V9 recovery/successor authority;
- current V7/V8 completed authority used by this module.

If the same/materially equivalent V9 is already legitimately ACTIVE, COMPLETE, or superseded, stop immediately:

`DUPLICATE / ALREADY COMPLETE / SUPERSEDED — NO EXECUTION — <current authority>`

Do not create a second equivalent claim, do not invent a Recovery generation to bypass dedup, and do not edit code merely to create activity.

If not duplicate, acquire and verify the canonical dedup-v2 claim and matching stage claim before substantive implementation.

## Read and obey

- `parallel/PM/COLLECTOR_WORKER_EXECUTION_POLICY.md`
- `parallel/PM/PROJECT_EXTERNAL_GITHUB_REUSE_POLICY.md`
- `parallel/PM/COLLECTOR_EXTERNAL_GITHUB_REUSE_POLICY.md`
- `parallel/PM/TESTING_CADENCE_POLICY.md`
- `parallel/PM/STAGE_DEDUP_GUARD.md`
- `COLLECTOR_ROUTING.md`
- `RUNTIME_DATA_SOURCE_BOUNDARIES.md`

## Current completed Collector authority — preserve

At V9 staging, the Collector stack is complete through V8:

- V3 segmented long-session capture: COMPLETE;
- V4 dataset catalog / immutable capture identity: COMPLETE;
- V5 storage / retention / archive / pressure guard: COMPLETE;
- V6 segment-aware analysis reader: COMPLETE;
- V7 reuse-first local serial batch acquisition automation: COMPLETE through Recovery V2;
- V8 rebuildable DuckDB research warehouse / query accelerator: COMPLETE through Recovery V2.

Exact current V8 implementation authority:

- bridge HEAD: `5359fe8209ba1dd540733ea0cad09acef8005eb3`;
- bridge tree: `cc2eb2c294ecf8a5461662237efaec840c91352e`;
- V8 workflow run: `33657091103`, SUCCESS;
- coherent V3–V8 implementation regression: `130/130 PASS`;
- current retained V4 catalog in clean CI: `33` records / `8` active reusable;
- V8 warehouse is a disposable derived index and never source authority.

Do not rewrite V3–V8 merely because V9 consumes them.

## Why V9 now

The Collector can already:

`capture -> segment -> identify -> retain -> analyze -> batch -> warehouse/query`

The remaining acquisition-efficiency gap is the manual step between a new research requirement and a V7 batch plan.

Today a researcher still has to manually answer:

1. Which requested experimental conditions are already covered by authoritative reusable datasets?
2. Which exact existing datasets should be reused?
3. Which repeat slots remain missing?
4. Which missing slots require local retrieval versus genuinely new capture?
5. How should only those real gaps be compiled into the existing V7 batch-plan contract?

V9 closes that gap without adding gameplay automation.

Target operating flow:

`explicit experiment request -> CURRENT V8 warehouse -> exact reuse allocation -> gap set -> validated V7 batch plan for gaps only`

This module must actively enforce the project rule:

**reuse before recapture**.

## Mandatory external GitHub reuse decision

### DIRECT_USE / REUSE EXISTING — DuckDB through V8

V8 already pins and validates:

- `duckdb==1.5.5`
- upstream: `duckdb/duckdb`
- license: MIT
- classification: `DIRECT_USE`

V9 must reuse the current V8 query/warehouse API and current DuckDB dependency rather than building another catalog/query subsystem.

Do not add a second database.

### REUSE EXISTING — V7 plan validator and plan identity

V9 must compile gaps into the current `wof_collector_batch_plan_v1` contract and validate the generated plan through the existing V7 validator/identity implementation.

Do not duplicate V7 task identity, batch identity, queue authority, retry or execution semantics.

### DEFER — Google OR-Tools

PM preflight inspected `google/or-tools` on 2026-09-03:

- actively maintained;
- Apache-2.0;
- strong general optimization capability;
- very large dependency/project surface.

V9 MVP needs deterministic exact matching and bounded slot allocation, not mixed-integer programming or generic operations-research machinery.

Classification: `DEFER`.

Do not add OR-Tools unless current implementation proves a concrete optimization requirement that cannot be handled by deterministic bounded matching. If such a requirement unexpectedly appears, record it as a future extension rather than broadening V9 by default.

### DEFER — Polars

PM preflight inspected `pola-rs/polars`:

- Python stable release inspected: `1.44.1` / `py-1.44.1`;
- MIT;
- actively maintained.

V6 already supplies raw-data statistics/ranking, while V9 is a planning/matching module. Adding Polars would create a second analytical dependency without solving the current gap.

Classification: `DEFER`.

### DEFER — Prefect

V7 already provides local serial durable batch orchestration. V9 only compiles a plan; it does not need another workflow engine.

Classification: `DEFER`.

## Core authority rule

V9 is a **derived research planner**, not evidence authority and not execution authority.

Canonical truth remains:

- V3 session/segment facts;
- V4 dataset ID/lifecycle/integrity/provenance;
- V5 artifact/storage/archive facts;
- V6 research-only analysis;
- V7 batch/task/result execution authority;
- V8 CURRENT warehouse build/source-set identity.

V9 must not upgrade an INVALID/UNREVIEWED/PARTIAL/stale/conflicting source into reusable evidence.

V9 must not rewrite an old dataset's experiment/trial grouping merely because the dataset is reused for a new research request.

V9 must not publish queue tasks or execute captures as part of planning.

## Required V9 contracts

Define strict versioned Collector-owned contracts, suggested names:

- request schema: `wof_collector_experiment_request_v1`;
- planner result: `wof_collector_experiment_plan_v1`;
- planner tool: `wof-winkawaks-collector-v9-experiment-planner-v1`;
- request identity: `wof_collector_v9_experiment_request_identity_v1`;
- allocation formula/version: `wof_collector_v9_reuse_allocation_v1`.

Exact names may differ only if versioned consistently across code/schema/docs/tests.

## Experiment request

The request must be explicit, strict and non-semantic-inference based.

At minimum include:

- `schemaVersion`;
- `experimentId`;
- `researchQuestion`;
- ordered `conditions`;
- safety/source invariants;
- requested output policy.

Each condition must have a stable explicit `conditionId` and enough structured facts to determine safe reuse, including as applicable:

- desired repeat count;
- scene label(s);
- player configuration;
- operator action;
- changed variable;
- held-stable variables;
- required capture mode/action family;
- duration / Hz / bytes/layout constraints when material;
- raw-stream retention requirement when material;
- explicit notes/confounder requirements only when they are part of matching;
- a V7-compatible capture-task template for missing slots.

Do not infer any of these from filenames, numeric RAM values, or human-readable prose alone.

Strict validation requirements:

- unknown keys fail closed unless the schema version explicitly allows them;
- integers must be native strict integers, not booleans/coercible strings;
- floats must be finite native numbers;
- repeat counts and collection bounds must be conservative;
- duplicate `conditionId` fails closed;
- source namespace must be exactly `winkawaks`;
- `readOnly=true`, `writesGameMemory=false`, `inputInjection=false` are mandatory.

## Deterministic request identity

Compute the request identity from canonical versioned request content, not:

- file path;
- filename;
- mtime;
- local machine path;
- display labels outside the actual request contract.

A byte-equivalent canonical request must produce the same request hash/ID regardless of input traversal order.

## V8 CURRENT gate

Planning requires a valid V8 warehouse.

Default V9 planning must require:

- V8 schema/tool compatible;
- `sourceNamespace=winkawaks`;
- warehouse state `CURRENT`;
- current V8 build/source-set identity available;
- no source conflict.

Do not silently plan from a stale warehouse.

If warehouse is `STALE`, `CONFLICT`, or `INVALID`, fail closed with a precise instruction to refresh/rebuild V8 using its existing authority.

V9 must not implement a second refresh/index engine.

## Reuse eligibility — fail closed

Default reusable dataset eligibility must be conservative:

- V4 lifecycle `VALID`;
- V4 integrity `VERIFIED`;
- active reusable according to current V4/V8 authority;
- exact `sourceNamespace=winkawaks`;
- current artifact availability facts are explicit;
- all condition fields declared as material to reuse must match exactly/canonically.

Do not use fuzzy text similarity, embeddings, AI semantic matching, approximate scene-name matching, or inferred operator action in V9 MVP.

Missing material metadata means **not a match**, not "probably reusable".

## Cross-experiment reuse is allowed without rewriting provenance

A dataset captured under an earlier experiment may satisfy a new condition if its authoritative acquisition metadata exactly satisfies the new condition.

When this happens:

- keep the original dataset's experiment/trial metadata unchanged;
- record it as a reused source dataset in the new V9 plan;
- bind exact `datasetId` plus current V8/V4 authority facts;
- do not pretend the old dataset was originally captured for the new experiment.

This is central to "capture once, reuse many times".

## Distinct repeat-slot allocation

For a condition requesting N repeats:

- one authoritative dataset may satisfy at most one repeat slot for that condition;
- do not count the same dataset twice;
- distinct retry attempts that resolved to one canonical dataset must not be double-counted merely because multiple execution records exist;
- deterministic allocation must be stable across input row order.

If two requested conditions are materially identical, default to global no-double-counting within the same experiment request unless the request contract explicitly and safely defines shared evidence semantics.

MVP may simply prohibit shared allocation across condition IDs to remain fail-closed.

## Deterministic candidate preference

Where multiple exact eligible datasets can satisfy one slot, choose deterministically using authority facts only.

Recommended priority:

1. current local authoritative artifact available;
2. verified V5 archive available;
3. deterministic dataset identity tie-break (`datasetId` ascending).

Do not use filesystem mtime, nondeterministic SQL row order, Git traversal order, or hidden scoring.

If the actual V5/V8 schema cannot authoritatively distinguish local versus verified archive availability, use deterministic `datasetId` ordering only and report the limitation.

## Planner dispositions

For every requested repeat slot, produce an explicit disposition such as:

- `REUSE_LOCAL`;
- `REUSE_ARCHIVED`;
- `MISSING_CAPTURE_REQUIRED`;
- `CONFLICT`.

Exact enums may differ, but the difference between "existing reusable evidence" and "must recollect" must be machine-readable.

An archived reusable dataset must not be turned into a new capture requirement merely because it is not currently in the primary local path. Mark the retrieval requirement explicitly and preserve V5 authority.

V9 must not itself restore/archive/prune/delete artifacts.

## Gap computation

The gap set is exactly the requested repeat slots not satisfied by authoritative reuse allocation.

Gap count must be deterministic and auditable.

For each missing slot, retain:

- experimentId;
- conditionId;
- desired slot/trial ordinal;
- reason no reuse candidate qualified;
- exact request facts;
- generated future trial identity / labels needed by the V7 task template.

Do not suppress a gap by using a lower-integrity dataset.

## V7 gap-to-batch compilation

If at least one real capture gap exists, compile only those missing slots into the existing V7 batch-plan contract.

Hard requirements:

1. use the current V7 `wof_collector_batch_plan_v1` schema and validator;
2. do not invent a V9 execution plan format that bypasses V7;
3. compile deterministic step/trial ordering from request condition order + slot ordinal;
4. preserve explicit experiment/repeat/trial metadata in the ordinary V7 fields already provided by V7;
5. keep `maxConcurrentCaptures=1` unless the current V7 contract itself changes in a future authority;
6. use current V7 safety invariants;
7. generated plan must pass the current V7 `validate_plan` / canonical plan identity path before V9 reports it usable;
8. V9 must not publish the plan into `tasks/queue/**`;
9. V9 must not call `run_queued_task()`;
10. execution remains an explicit later V7 action.

If zero gaps remain, do not manufacture an empty invalid V7 batch merely to produce a file. Return a clear terminal planning disposition such as `REUSE_COMPLETE / NO_CAPTURE_REQUIRED` with no execution plan.

## Plan freshness and source binding

Every V9 planner result must bind:

- experiment request ID/hash;
- exact V8 warehouse build ID;
- exact V8 source-set digest;
- selected reused dataset IDs;
- current lifecycle/integrity/availability facts used for allocation;
- generated V7 plan hash when gaps exist;
- planner schema/tool/formula versions.

Provide a verification path that can tell whether a saved plan is still current.

If the V8 source-set identity changes, a previously generated V9 plan must become `STALE` until re-evaluated, because a dataset may have become newly available, superseded, invalidated, archived or otherwise changed.

Do not silently execute an old gap plan after source authority changed.

## Output / derived artifact

V9 planner outputs are derived planning artifacts only.

Default namespace may be:

`derived/planning/**`

They must be ignored from Git by default unless a task explicitly requires durable fixture/example content.

A planner result should contain:

- request identity;
- V8 build/source-set identity;
- per-condition requested counts;
- reuse allocations;
- missing gaps;
- archived retrieval notices;
- generated V7 plan and planSha if applicable;
- deterministic counts/summary;
- provenance;
- `researchOnly=true`;
- `semanticAuthority=false`;
- safety flags.

## CLI

Provide a small Windows/local-first CLI, conceptually:

- `validate-request`
- `plan`
- `verify-plan`
- `show`
- `emit-v7-plan`

Exact names may vary if the resulting UX is simpler, but there must be no implicit execution command.

`emit-v7-plan` must only write a local validated plan artifact; it must not publish tasks or start Collector runtime.

Structured JSON output is required; human summaries should remain concise.

## No gameplay / runtime automation

V9 must not:

- start or control WinKawaks;
- read game memory directly;
- write game memory;
- inject keyboard/gamepad input;
- automate scene navigation;
- use Lua/macros;
- perform savestate stepping;
- invoke Training Farm actions;
- publish queue tasks;
- execute V7 batch captures automatically.

Safety remains:

```text
sourceNamespace=winkawaks
readOnly=true
writesGameMemory=false
inputInjection=false
researchOnly=true
semanticAuthority=false
```

## Side-lane isolation

Do not modify or block:

- `product/alpha/**`;
- Alpha live acceptance / danger / target / projection authority;
- Transport / Recorder / PYLAUNCH / OneClick;
- Training Farm / Stable-Retro / FBNeo / PPO/RL / 10-worker scheduling.

Collector V9 status is not an Alpha or Training Farm blocker.

## Implementation shape

Prefer a narrow Collector-owned module, e.g.:

- `bridge/experiment_planner.py`;
- strict schema under `schemas/**`;
- deterministic tests under `tests/**`;
- concise docs under `docs/**`;
- optional example request under `examples/**`;
- maintained smoke integration.

Do not perform an unrelated packaging/refactor migration.

No new dependency should be needed beyond current V7/V8 requirements for the MVP.

## Required implementation self-check

Complete the coherent V9 module first, then run one implementation-owned self-check boundary.

Cover at minimum:

- strict request schema / unknown-key fail-close;
- canonical deterministic request identity;
- duplicate condition rejection;
- strict numeric/no-coercion behavior;
- V8 CURRENT required;
- stale/conflict/invalid V8 rejected;
- source namespace isolation;
- V4 VALID+VERIFIED preservation;
- missing material metadata not matched;
- exact metadata match works;
- cross-experiment reuse preserves original dataset grouping;
- one dataset cannot fill multiple repeat slots incorrectly;
- deterministic allocation independent of query row order;
- local/archive preference only when current authority supports it;
- archived reuse avoids needless new capture;
- missing slots generate exact gap count;
- zero gaps returns no-capture-required without fake batch;
- generated gap batch passes current V7 validator;
- generated V7 plan includes only missing slots;
- no queue publication / no execution call;
- plan freshness bound to V8 build/source-set identity;
- changed source-set marks old plan stale;
- derived path traversal rejected;
- research-only / nonsemantic safety invariants;
- bounded synthetic fixture with at least hundreds of datasets / dozens of conditions and repeat slots;
- necessary current V7/V8 compatibility checks.

Do not start real WinKawaks, Browser/WOF, Training Farm or gameplay automation.

Do not open Fresh QA, second opinion, cross-check or a separate audit from this worker.

## Maintained smoke integration

Extend the current Collector Python smoke workflow conservatively so V9-owned files trigger it and the exact current module is compiled/tested.

The maintained smoke must retain:

```text
permissions:
  contents: read
```

Do not introduce CI writeback or mutable PASS receipts.

Prefer one coherent current-head V3–V9 compatibility boundary rather than many micro-runs.

If a concrete V9 defect is exposed, fix the actual defect cluster and rerun the affected/current-head checks once.

## Durable RESULT

On successful completion write:

`parallel/PM/WINKAWAKS_COLLECTOR_V9_REUSE_FIRST_EXPERIMENT_PLANNER_GAP_TO_BATCH_COMPILER_RESULT.md`

Record at minimum:

- exact final bridge HEAD/tree;
- relevant exact blob SHAs;
- request/result schema/tool/allocation versions;
- reuse eligibility rules;
- deterministic allocation/tie-break rules;
- V8 CURRENT/source-set binding;
- V4/V5 authority preservation;
- exact gap computation;
- V7 plan-validator/compiler reuse;
- zero-gap behavior;
- plan freshness/stale behavior;
- CLI/derived output behavior;
- external reuse decisions: DuckDB existing DIRECT_USE, V7/V8 REUSE, OR-Tools DEFER, Polars DEFER, Prefect DEFER;
- implementation self-check commands/counts/results;
- exact successful maintained workflow run ID/head SHA;
- safety/source isolation;
- intentional limitations / future extensions.

Allowed final success verdict:

`COMPLETE — WINKAWAKS COLLECTOR V9 REUSE-FIRST EXPERIMENT PLANNER / GAP-TO-BATCH COMPILER — REUSE-BEFORE-RECAPTURE PLANNING COMPLETE`

Otherwise only a precise unavoidable:

`BLOCKED — WINKAWAKS COLLECTOR V9 REUSE-FIRST EXPERIMENT PLANNER / GAP-TO-BATCH COMPILER — <exact blocker>`

A normal implementation defect is not automatically an external blocker; fix repository defects within scope first.

## Claim/stage closeout

After and only after the durable RESULT exists:

1. re-read the V9 canonical claim and verify the exact claim token;
2. update canonical claim to `COMPLETE` with RESULT path/commit, final bridge commit/tree and workflow run ID;
3. update matching stage claim to `COMPLETE` with the same terminal authority;
4. do not rewrite older V3–V8 historical claims/results.

## Stop rule

Do not stop at claim acquisition, schema creation, one code file, one test, smoke workflow edit, CI launch or CI PASS.

Continue through the complete V9 module, integration, implementation-owned self-check, durable RESULT and canonical/stage closeout.

Only stop at:

- COMPLETE with durable RESULT + claim/stage COMPLETE;
- precise unavoidable BLOCKED;
- duplicate/already-complete/superseded NO EXECUTION from the mandatory preflight.

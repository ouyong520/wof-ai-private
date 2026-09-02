# WinKawaks Collector V8 — Reuse-First Research Warehouse / Query Accelerator

stageId: `WINKAWAKS_COLLECTOR_V8_REUSE_FIRST_RESEARCH_WAREHOUSE_QUERY_ACCELERATOR_V1`
dedupProtocol: `v2`
dedupKey: `winkawaks.collector.v8.reuse-first-research-warehouse-query-accelerator`
dedupMode: `exclusive`

Priority: **P1 reusable datasets / large-scale research query acceleration**

## Duplicate-forward preflight — mandatory

Read and obey:

- `parallel/PM/COLLECTOR_WORKER_EXECUTION_POLICY.md`
- `parallel/PM/PROJECT_EXTERNAL_GITHUB_REUSE_POLICY.md`
- `parallel/PM/COLLECTOR_EXTERNAL_GITHUB_REUSE_POLICY.md`
- `parallel/PM/TESTING_CADENCE_POLICY.md`
- `parallel/PM/STAGE_DEDUP_GUARD.md`
- `COLLECTOR_ROUTING.md`
- `RUNTIME_DATA_SOURCE_BOUNDARIES.md`

Treat this post as potentially duplicated until current authority is checked. Before substantive implementation verify both current mains, this exact START_PROMPT, canonical/stage claims, any same/equivalent V8 RESULT, and any newer recovery/successor authority.

If the same/materially equivalent V8 is already legitimately ACTIVE under another current generation, already COMPLETE, or superseded by a newer active/completed successor, do not execute duplicate implementation. Stop:

`DUPLICATE / ALREADY COMPLETE / SUPERSEDED — NO EXECUTION — <current authority>`

Do not create a second equivalent claim, do not invent a recovery to bypass dedup, and do not rerun completed work merely to create activity.

If not duplicate, acquire canonical dedup-v2 canonical/stage ownership before substantive implementation.

## Current completed Collector authority

At task creation:

- V3 segmented long-session capture: COMPLETE;
- V4 dataset catalog / immutable capture identity: COMPLETE;
- V5 long-run storage / retention / archive / pressure guard: COMPLETE;
- V6 segment-aware analysis reader / raw research toolkit: COMPLETE through Recovery V2;
- V7 reuse-first local serial batch acquisition: COMPLETE through Recovery V2;
- exact V7 final bridge candidate: `4eb4b33bd09cfaeeb6644110a59b3452c489ea9e`;
- exact V7 final tree: `19f96fa973fc608e367e66325731e1ec869a44bc`;
- V7 Recovery V2 workflow run: `33650865968`, SUCCESS, `114/114` unittest PASS;
- V7 Recovery V2 durable RESULT and successor canonical/stage COMPLETE authority exist.

Do not rerun or rewrite V3/V4/V5/V6/V7 merely because V8 consumes their metadata.

## Why V8 now

V7 solved local single-machine batch orchestration, retry/resume, V5 preflight, V4 catalog refresh and optional V6 post-analysis. The next large-scale bottleneck is not more scheduler machinery; it is efficient reuse of an expanding body of captures, segments, experiments, trials, batch results and research-only analysis outputs.

V8 must make questions such as the following cheap and deterministic without rescanning every raw JSON/JSONL file each time:

- which reusable VALID WinKawaks datasets cover a scene / player config / operator action / experiment;
- which captures belong to an explicit repeat group and what trial/attempt lineage they have;
- which V7 batches produced which exact task/result/dataset IDs;
- which V3 sessions/segments are COMPLETE/PARTIAL and where their verified artifacts live;
- which V6 analysis outputs were derived from which exact datasets and parameters;
- which evidence is archived by V5 versus local primary storage;
- which captures have integrity/lifecycle/provenance conflicts or missing source authority;
- which existing datasets should be reused instead of asking Owner to recollect.

The warehouse is a **derived research index/query accelerator**, never evidence authority.

## Mandatory external GitHub reuse decision

### DIRECT_USE — DuckDB

Preferred upstream:

- repository: `duckdb/duckdb`
- stable release inspected by PM: `v1.5.5`
- release date: `2026-07-22`
- license: MIT
- upstream remains actively maintained on `2026-09-02`

Use the Python DuckDB package as a normal pinned dependency. Prefer `duckdb==1.5.5` if compatible with the bridge's current Python 3.12 / Windows-local environment. Verify exact installed version before implementation self-check and record the tested upstream version/license in docs/RESULT.

**Do not fork or vendor DuckDB.**

DuckDB is commodity embedded analytical infrastructure only. It must not redefine Collector identity, provenance, integrity or lifecycle authority.

### DEFER — Polars

`pola-rs/polars` remains a strong future/direct-use candidate for columnar transforms, but V8 MVP should not add two overlapping analytical dependencies unless current implementation facts prove DuckDB alone cannot meet the required bounded query/index workload.

Prefer the smaller dependency surface:

`DuckDB direct use + Collector-owned authority adapters`

If Polars becomes genuinely necessary for one narrow transform, record the exact version/license/reason. Do not add it merely because it exists.

### DEFER — Prefect

Prefect remains outside V8. V8 is not an orchestration expansion and must not introduce a server/dashboard/work-pool architecture.

## Core authority rule

The `.duckdb` warehouse file is disposable and rebuildable.

Canonical truth remains in existing Collector authority, including:

- V3 task/session/segment manifests and exact terminal authority;
- V4 immutable dataset IDs, lifecycle, integrity and provenance;
- V5 archive receipts / verified artifact location and storage safety;
- V6 analysis result identity, parameters, `researchOnly=true`, `semanticAuthority=false`;
- V7 batch plan/task/trial/attempt/result lineage and exact `taskId + taskBlobSha` authority.

A warehouse row must never turn missing, stale, conflicting or invalid source evidence into valid evidence.

If warehouse state disagrees with current source authority, source authority wins and V8 must mark/rebuild/fail closed as appropriate.

## MVP architecture

Target:

`V3/V4/V5/V6/V7 authority files -> strict adapters -> DuckDB derived warehouse -> bounded query/export CLI`

The warehouse should index compact metadata and provenance edges. It should **not ingest full raw frame streams by default**.

Raw frames remain in existing capture artifacts and are read through V6 when actual frame-level analysis is needed.

## Required capabilities

### 1. Versioned warehouse contract

Define one strict Collector-owned warehouse schema/version, e.g.:

- `wof_collector_research_warehouse_v1`
- `wof-winkawaks-collector-v8-research-warehouse-v1`

Record at minimum:

- schema/tool version;
- exact DuckDB dependency version;
- source namespace;
- build/rebuild timestamp;
- deterministic source-set digest / build identity;
- source authority counts;
- stale/conflict/error counts;
- safety flags;
- warehouse database path.

Warehouse build identity must derive from exact current source authority identities/hashes plus schema/tool version, not file mtime, path display labels or row order.

### 2. Source namespace isolation

V8 MVP imports only `sourceNamespace=winkawaks` authority.

Do not silently merge Browser or Training Farm evidence into WinKawaks tables.

If future cross-source comparison is needed it must be explicit and source-qualified; V8 MVP should fail closed on ambiguous/unqualified source records.

### 3. V4 dataset catalog is primary dataset selection authority

Use V4 catalog records as the canonical entry point for dataset-level indexing.

Index useful exact fields such as:

- datasetId;
- sourceNamespace;
- sourceTaskId/taskBlobSha where present;
- capture/session identity;
- lifecycle;
- integrity state;
- active/superseded relation;
- artifact hashes/paths/retention state;
- structured scene metadata;
- experiment/repeat/trial metadata only where explicitly authoritative;
- provenance links.

Do not synthesize lifecycle, validity or semantic labels from filenames/raw values.

`VALID`, `INVALID`, `SUPERSEDED`, `UNREVIEWED` semantics remain V4-owned.

### 4. V3 session / segment metadata index

Index compact V3 session/segment metadata without copying raw frame payloads.

At minimum where current authority exposes it:

- taskId + taskBlobSha;
- captureId/sessionId/source identity;
- segment ordinal;
- frame start/end/count;
- timestamps/Hz/bytes;
- raw/gzip SHA256;
- local/archive artifact references;
- COMPLETE/PARTIAL/FAILED status;
- integrity disposition.

Missing/duplicate/reordered/hash-invalid segment authority must not be normalized into a clean COMPLETE warehouse row.

### 5. V5 storage / archive state

Index V5-owned storage facts only from current verified V5 authority:

- primary local artifact location where authoritative;
- verified archive receipt/location;
- owned byte count where available;
- pressure/protection/pin/BASECAP protection facts where relevant;
- prune/archive lifecycle references.

Do not let warehouse existence authorize prune/delete/archive actions.

V8 is read/query only with respect to storage policy.

### 6. V6 derived-analysis provenance

Index compact V6 result metadata:

- analysisId / result identity;
- operation;
- exact input dataset/capture identities;
- canonical parameters / parameter hash;
- result SHA/path;
- formula/tool versions where present;
- repeat-group declarations where explicit;
- `researchOnly=true`;
- `semanticAuthority=false`.

V8 must preserve these two flags exactly and never present V6 candidates/ranks/transitions as gameplay truth.

### 7. V7 batch / experiment / trial / attempt lineage

Index V7 batch metadata so acquisition history becomes queryable:

- batchId / planSha256;
- experimentId;
- repeatGroupId;
- stepId;
- trialId / trialOrdinal;
- taskId / taskBlobSha;
- attemptOrdinal / predecessor lineage;
- terminal result state;
- datasetId after V4 refresh where available;
- V5 preflight disposition;
- required/optional post-analysis state;
- exact result/checkpoint references.

A later retry PASS must not erase or rewrite an earlier failed predecessor.

### 8. Provenance edge model

Provide an explicit machine-readable provenance relation rather than forcing callers to infer joins from names.

Conceptually support edges such as:

- batch -> trial;
- trial -> attempt/task;
- task -> capture/session;
- capture/session -> segments;
- capture -> dataset;
- dataset -> archive artifact;
- datasets -> analysis result;
- predecessor -> retry successor;
- dataset -> superseding dataset.

Exact table names are implementation-owned, but all edges must retain source-qualified exact IDs.

### 9. Rebuild and incremental refresh

Provide deterministic commands conceptually:

- `rebuild`
- `refresh`
- `verify`
- `status`
- `query`
- `show`
- `export`

`rebuild` must create the warehouse from current source authority with an atomic replace strategy; a failed rebuild must not corrupt the last valid warehouse.

`refresh` may be incremental, but it must use content/authority identity, not mtime alone. If incremental state cannot safely reconcile a source mutation/conflict, fail closed and require rebuild.

The same unchanged source authority set must produce the same logical rows/order-independent source-set digest.

### 10. Stale warehouse detection

On read/query, detect whether the warehouse was built from the current relevant source authority set.

Expose clear states such as:

- `CURRENT`
- `STALE`
- `CONFLICT`
- `INVALID`

Exact names may differ.

A stale warehouse may be queryable only when the CLI explicitly labels it stale; default high-confidence query mode should require CURRENT or automatically perform a safe refresh/rebuild according to command semantics.

Never silently report stale cached rows as current repository truth.

### 11. Bounded query API / CLI

Provide practical deterministic query surfaces for common research workflows without requiring users to write SQL.

At minimum support filters for:

- datasetId / taskId / batchId / experimentId / repeatGroupId;
- lifecycle / integrity / terminal status;
- sceneLabel;
- player config/operator action/changed variable where explicitly stored;
- active reusable only;
- archived/local availability;
- time/session ranges where meaningful;
- analysis operation/result;
- limit/order.

Provide provenance lookup: given a dataset/task/batch/analysis ID, show its connected authority chain.

Default output must be bounded and deterministic JSON, with concise human-readable summary.

### 12. Safe SQL boundary

Do not expose unrestricted DuckDB SQL as the default user path.

If an advanced `sql` command is implemented, it must be explicitly read-only and constrained to warehouse-owned tables/views. Fail closed on mutating or external-access statements such as `ATTACH`, `COPY`, `INSTALL`, `LOAD`, file readers, network/external extension access, DDL/DML or multiple statements.

Prefer opening query connections read-only and disabling external access where DuckDB supports it.

A query feature must not become a generic filesystem/network execution surface.

### 13. Derived exports

Allow bounded research exports only under a clear derived-output namespace, e.g. `derived/warehouse/**` or a user-specified safe local path.

Exports may include JSON/CSV and optionally Parquet if DuckDB supports the safe local operation cleanly.

Exports are `researchOnly` derivatives and never V3/V4/V5 authority.

Record the warehouse build/source-set identity and query/filter parameters alongside exported content so results are reproducible.

### 14. Performance / scale target

V8 exists to avoid repeated full-source scans for ordinary metadata questions.

Implementation self-check should include deterministic synthetic scale fixtures sufficient to prove that indexing/query logic remains bounded and correct across at least thousands of dataset/trial/segment metadata rows without loading raw capture frames into memory.

Do not overfit to the current small 33-record catalog.

No arbitrary benchmark claim is required, but the RESULT should report a simple reproducible synthetic rebuild/query measurement if practical.

### 15. BASECAP reuse-first integration

Make it easy to answer whether existing BASECAP/current VALID datasets already satisfy a requested scene/research need.

Do not mutate `parallel/BASECAP/BASE_CAPTURE_CATALOG.md` from V8.

Do not infer missing operator semantics.

The warehouse may surface BASECAP annotations only when they already exist in V4/explicit current authority.

### 16. DuckDB dependency / license record

Add the smallest clear V8 dependency surface, e.g. `requirements-collector-v8.txt`, with exact tested `duckdb` version.

Document:

- upstream repo;
- release/tag/version;
- license MIT;
- DIRECT_USE classification;
- no fork/vendor.

Do not migrate unrelated project packaging just to introduce DuckDB.

### 17. Safety / read-only Collector boundary

V8 must retain:

```text
sourceNamespace=winkawaks
readOnly=true
writesGameMemory=false
inputInjection=false
researchOnly=true
```

V8 must not:

- start/control WinKawaks;
- read/write game process memory directly;
- inject keyboard/gamepad input;
- add Lua/macros;
- alter gameplay;
- perform archive/prune/delete actions;
- change V3/V4/V5/V6/V7 authority semantics.

### 18. Side-lane isolation

Do not modify or block:

- `product/alpha/**`;
- Alpha release/proof/live acceptance/danger/target semantics;
- Transport / Recorder / PYLAUNCH / OneClick;
- Training Farm / Stable-Retro / FBNeo / PPO/RL / savestate/action injection / 10-worker scheduling.

Collector V8 incomplete/blocked is not an Alpha V1 or Training Farm blocker.

## Implementation-owned self-checks

Complete the coherent V8 module first, then run one implementation-owned self-check boundary. Do not open Fresh QA/cross-check/second opinion.

Cover at minimum:

- exact DuckDB dependency/version/import;
- schema/tool/source-set build identity determinism;
- atomic rebuild and failure preservation;
- incremental refresh same-content idempotence;
- stale source detection;
- changed source authority refresh/rebuild behavior;
- conflicting source authority fail-close;
- sourceNamespace isolation;
- V4 lifecycle/integrity preservation;
- V3 bad/missing/reordered segment state not upgraded;
- V5 archive facts indexed without prune authority;
- V6 `researchOnly=true / semanticAuthority=false` preservation;
- V7 retry/predecessor lineage preservation;
- provenance chain lookup;
- common bounded query filters/order/limit;
- query CURRENT/STALE labeling;
- safe path handling;
- no unrestricted external SQL/filesystem/network execution;
- derived export provenance;
- deterministic synthetic thousands-row fixture;
- necessary V3–V7 compatibility regression;
- no memory-write/input-injection/gameplay boundary drift.

Use synthetic/local repository fixtures. Do **not** start real WinKawaks, Browser/WOF, Training Farm, or gameplay automation.

If a concrete defect is found, fix that defect cluster and rerun affected checks. Do not manufacture additional QA stages.

## Maintained smoke integration

Extend the existing Collector Python smoke workflow conservatively to include V8 dependency install/import, module compile, V8 deterministic tests/CLI/schema checks, and V3–V8 safety/authority wiring.

Keep:

```text
permissions:
  contents: read
```

Do not add repository-writing PASS receipts or mutable CI authority.

## Documentation

Document at minimum:

- why DuckDB was selected;
- exact version/license/direct-use decision;
- why Polars and Prefect are deferred for this MVP;
- warehouse-is-derived-not-authority rule;
- table/entity/provenance model;
- rebuild/refresh/stale behavior;
- query examples for dataset reuse / experiment / trial / archive / analysis provenance;
- safe SQL boundary;
- Windows-local install/run path;
- intentional omission of raw-frame ingestion by default.

## Durable RESULT

On successful completion write:

`parallel/PM/WINKAWAKS_COLLECTOR_V8_REUSE_FIRST_RESEARCH_WAREHOUSE_QUERY_ACCELERATOR_RESULT.md`

Record at minimum:

- final exact bridge HEAD/tree;
- exact relevant blob SHAs;
- DuckDB version/tag/license/classification;
- warehouse schema/tool/build identity versions;
- authority sources consumed;
- source-set digest behavior;
- rebuild/refresh/stale/conflict behavior;
- indexed V3/V4/V5/V6/V7 facts;
- provenance model;
- query/export behavior;
- SQL/external-access safety;
- synthetic scale self-check;
- exact test counts/results;
- exact successful GitHub Actions workflow run ID/head SHA;
- safety/source isolation;
- remaining intentional limitations.

Final allowed success verdict:

`COMPLETE — WINKAWAKS COLLECTOR V8 REUSE-FIRST RESEARCH WAREHOUSE / QUERY ACCELERATOR — REBUILDABLE LARGE-SCALE RESEARCH INDEX COMPLETE`

Otherwise only precise unavoidable:

`BLOCKED — WINKAWAKS COLLECTOR V8 REUSE-FIRST RESEARCH WAREHOUSE / QUERY ACCELERATOR — <exact external/unresolvable blocker>`

A failing implementation test is not automatically an external blocker: fix concrete repository defects first.

## Claim/stage closeout

After and only after durable RESULT is committed:

1. update V8 canonical claim to `COMPLETE` with exact RESULT path/commit, bridge commit/tree, workflow run ID;
2. update matching V8 stage claim to `COMPLETE` with the same terminal authority;
3. do not rewrite historical V3–V7 claims/results;
4. preserve DuckDB as derived infrastructure, not canonical evidence authority.

## Stop condition

Do not stop at open-source review, claim acquisition, dependency install, schema creation, one patch, local self-check, workflow launch or CI PASS.

Continue through coherent implementation, integration, regression, concrete defect fixes, durable RESULT and canonical/stage closeout.

Only stop at:

- `COMPLETE` with durable RESULT + canonical/stage closeout;
- precise unavoidable `BLOCKED`;
- duplicate/already-complete/superseded `NO EXECUTION` from mandatory preflight.

# WinKawaks Collector V8 — Reuse-First Research Warehouse / Query Accelerator Recovery V2

stageId: `WINKAWAKS_COLLECTOR_V8_REUSE_FIRST_RESEARCH_WAREHOUSE_QUERY_ACCELERATOR_RECOVERY_V2`
dedupProtocol: `v2`
dedupKey: `winkawaks.collector.v8.reuse-first-research-warehouse-query-accelerator.recovery-v2`
dedupMode: `exclusive`

Priority: **P1 implementation recovery / finish V8 module end-to-end**

## PM recovery authorization

This is a PM-authorized implementation recovery for the existing V8 module. It is **not Fresh QA**, not a redesign, and not permission to restart V8 from scratch.

The original V8 worker was confirmed by Owner-forwarded terminal report to have stopped because its execution window reached the tool-call limit. The worker explicitly reported that this was an execution-environment interruption, not a code, dependency, authority, or external repository blocker.

Repository verification at Recovery V2 staging confirms:

- original V8 canonical claim remains historical `ACTIVE` under owner `gpt-5.6-sol-v8-worker`;
- original V8 durable RESULT does not exist;
- current `ouyong520/wof-winkawaks-bridge/main` remains `bb10c79be52d1a7e278e7a78fd85d87f930f73d8`;
- exact tree at that candidate is `577ba712d4495ac97034102d296ebf23858e42de`;
- current V8 core blob `bridge/research_warehouse.py` is `17665f9d79b40b0de61eea701c1535f5df205927`;
- no later V8 implementation commit was found at recovery staging;
- no V8 Recovery V2/V3 or newer successor authority was found at recovery staging;
- current maintained Collector smoke workflow still covers V3–V7 only and has not yet integrated V8;
- `requirements-collector-v8.txt`, V8 schema/docs/tests and durable RESULT are still absent at this candidate.

The Owner-forwarded stopped-worker report additionally records one known integration caution: a workflow draft contained three source-string assertions that do not exactly match the final compact `research_warehouse.py` implementation. **Do not copy that draft blindly.** Derive V8 smoke assertions from the current final source/API/contract and fix those checks before committing the workflow.

Recovery V2 therefore exists only to continue from `bb10c79...`, complete the already-scoped V8 module, run one coherent implementation-owned V3–V8 regression boundary, fix actual defects, write durable RESULT, and close Recovery V2 canonical/stage authority.

Do **not** modify, delete, rewrite, or falsely close the historical original V8 ACTIVE claim. Recovery V2 will supersede that stopped generation as successor authority if COMPLETE.

## Mandatory duplicate-forward preflight

Treat this Recovery V2 post itself as potentially duplicated.

Before substantive work, re-read:

- current `ouyong520/wof-ai-private/main`;
- current `ouyong520/wof-winkawaks-bridge/main`;
- `parallel/PM/WINKAWAKS_COLLECTOR_V8_REUSE_FIRST_RESEARCH_WAREHOUSE_QUERY_ACCELERATOR_START_PROMPT.md`;
- original V8 canonical/stage claims;
- this exact Recovery V2 START_PROMPT;
- any Recovery V2 canonical/stage claim;
- any original or Recovery V2 durable V8 RESULT;
- any newer V8 recovery/successor authority.

If this same/materially equivalent Recovery V2 is already legitimately ACTIVE under another current owner, already COMPLETE, or superseded, stop immediately:

`DUPLICATE / ALREADY COMPLETE / SUPERSEDED — NO EXECUTION — <current authority>`

Do not create a second equivalent claim. Do not invent Recovery V3 merely to bypass dedup. Do not rerun completed work just to create activity.

If no current Recovery V2 authority exists, acquire the Recovery V2 canonical dedup-v2 claim and matching stage claim before substantive implementation.

## Read and obey

- `parallel/PM/COLLECTOR_WORKER_EXECUTION_POLICY.md`
- `parallel/PM/PROJECT_EXTERNAL_GITHUB_REUSE_POLICY.md`
- `parallel/PM/COLLECTOR_EXTERNAL_GITHUB_REUSE_POLICY.md`
- `parallel/PM/TESTING_CADENCE_POLICY.md`
- `parallel/PM/STAGE_DEDUP_GUARD.md`
- `COLLECTOR_ROUTING.md`
- `RUNTIME_DATA_SOURCE_BOUNDARIES.md`
- original V8 START_PROMPT above

All original V8 functional requirements remain in force except where this Recovery V2 explicitly narrows the remaining work to current-head completion.

## Exact current V8 implementation lineage — preserve, inspect, do not redo

Current V8 bridge lineage already landed:

- parent V7 final candidate: `4eb4b33bd09cfaeeb6644110a59b3452c489ea9e`;
- V8 core: `bb10c79be52d1a7e278e7a78fd85d87f930f73d8` — `Collector V8: implement rebuildable DuckDB research warehouse`.

Current V8 core already intentionally includes, and Recovery must preserve unless a concrete defect is proven:

- DuckDB direct dependency contract in code: version `1.5.5`, upstream `duckdb/duckdb`, license `MIT`, classification `DIRECT_USE`;
- Polars classification `DEFER`;
- Prefect classification `DEFER`;
- versioned warehouse/tool/build/export identities;
- `sourceNamespace=winkawaks` isolation;
- `readOnly=true`;
- `writesGameMemory=false`;
- `inputInjection=false`;
- `researchOnly=true`;
- `semanticAuthority=false`;
- V4 dataset-catalog adapter;
- compact V3 session/segment metadata adaptation without default raw-frame ingestion;
- V5 storage/archive metadata adaptation without prune/delete authority;
- V6 research-only analysis provenance preservation;
- V7 batch/trial/attempt/retry lineage preservation;
- deterministic content/source-set identity;
- rebuild/refresh/status/query/provenance/export CLI surface;
- atomic rebuild strategy;
- `CURRENT / STALE / CONFLICT / INVALID` style warehouse state semantics;
- bounded query limit;
- explicit provenance graph lookup;
- JSON/CSV derived exports;
- no unrestricted SQL path;
- external DuckDB access disabled/constrained where current implementation supports it.

Do not rewrite the 387-line core merely to make the recovery look active. Inspect it and patch only real defects found by completion work/self-checks.

## Recovery V2 primary work

### 1. Finish exact DuckDB dependency surface

Add the smallest V8 dependency file, normally:

`requirements-collector-v8.txt`

Pin exactly:

`duckdb==1.5.5`

Record:

- upstream: `duckdb/duckdb`;
- stable release/tag: `v1.5.5`;
- license: MIT;
- classification: `DIRECT_USE`;
- no fork/vendor.

Do not add Polars or Prefect in this recovery unless exact current facts prove DuckDB alone cannot satisfy the already-defined V8 contract. A desire for broader future functionality is not such proof.

Do not perform unrelated packaging migration.

### 2. Add V8 versioned schema/contract artifact

Complete the V8 schema/contract surface required by the original prompt. Use strict finite/native types and fail-closed unknown-key behavior where applicable.

At minimum the maintained schema/contract must bind the relevant current V8 public output/state invariants, including:

- warehouse schema/tool version;
- source-set/build identity;
- source namespace;
- dependency identity where represented;
- source counts/conflict/stale state where represented;
- safety flags;
- `researchOnly=true`;
- `semanticAuthority=false`;
- bounded export/query envelope where represented.

Do not make the schema a second authority over V3–V7 source truth. It describes V8 derived state only.

### 3. Add V8 documentation

Document the actual current implementation rather than an aspirational redesign.

At minimum cover:

- why DuckDB was selected and Polars/Prefect remain deferred;
- exact version/upstream/license/classification;
- install command / Windows-local prerequisites;
- rebuildable/disposable warehouse principle;
- canonical authority remains V3–V7;
- indexed metadata categories;
- no raw-frame ingestion by default;
- build/source-set identity;
- rebuild / refresh / stale detection;
- bounded query filters/order/limit;
- provenance lookup;
- JSON/CSV export semantics;
- V7 retry/predecessor lineage preservation;
- CURRENT/STALE/CONFLICT/INVALID behavior;
- safe query boundary and lack of unrestricted SQL/external access;
- safety/source namespace contract;
- intentional limitations.

Do not document unimplemented commands/features as complete.

### 4. Add deterministic V8 implementation-owned tests

Add `tests/test_research_warehouse.py` or equivalent following repository conventions.

Cover the coherent original V8 contract, especially:

- exact DuckDB dependency/import/version;
- deterministic build/source-set identity independent of row/path traversal order where authority content is unchanged;
- atomic rebuild preserves last valid warehouse on failed replacement;
- same-content refresh is idempotent;
- changed authoritative content becomes STALE/refreshable;
- conflicting source authority fails closed;
- source namespace isolation;
- V4 lifecycle/integrity preservation;
- V3 missing/duplicate/reordered/incomplete segment facts never become clean COMPLETE;
- V5 archive facts are queryable without prune/delete authority;
- V6 `researchOnly=true / semanticAuthority=false` preservation;
- V7 repeat/trial/attempt/predecessor/retry lineage preservation;
- later retry success does not erase failed predecessor;
- bounded parameterized filters/order/limit;
- provenance traversal bounded by depth/edge limits;
- stale query labeling/default currentness behavior;
- safe local path/export handling;
- no unrestricted SQL execution;
- no ATTACH/INSTALL/LOAD/COPY/file-reader/network/external-extension mutation surface through the normal CLI/API;
- JSON/CSV export includes reproducibility/source-set/query metadata;
- synthetic scale fixture with thousands of metadata rows without ingesting raw frame streams;
- safety invariants remain exact.

Use synthetic/repository-local fixtures. Do not start WinKawaks, Browser/WOF, Training Farm, or gameplay automation.

### 5. Validate the current core against the tests and fix only real defects

The stopped worker had not yet run the completed V8 module boundary. Run the directly owned V8 tests after schema/docs/dependency are complete.

If tests expose concrete defects in `bridge/research_warehouse.py`, fix the actual defect cluster. Do not change V3–V7 authority semantics to make V8 tests pass.

Important authority rules to verify carefully:

- warehouse content is derived/rebuildable;
- current source authority always outranks warehouse rows;
- V4 lifecycle/integrity is copied/preserved, never synthesized from raw values or filenames;
- V3 segment integrity/status cannot be upgraded by indexing;
- V5 archive/location facts cannot authorize deletion/prune/archive operations;
- V6 analysis remains research-only/non-semantic;
- V7 retries preserve every attempt and predecessor lineage;
- source-set digest uses content/authority identity rather than mtime only;
- a stale local warehouse cannot silently claim current repository truth;
- a failed rebuild cannot corrupt the last valid DB;
- query/export remains bounded and deterministic;
- no cross-source Browser/Training Farm mixing.

### 6. Finish maintained Collector smoke integration

Update `.github/workflows/collector-python-smoke.yml` conservatively so the maintained implementation boundary covers V3–V8.

At minimum add/watch, as applicable:

- `bridge/research_warehouse.py`;
- V8 test file;
- V8 schema/contract file;
- `requirements-collector-v8.txt`;
- V8 docs;
- `.github/workflows/collector-python-smoke.yml` itself.

The workflow must:

- keep `permissions: contents: read`;
- install exact `duckdb==1.5.5` from the V8 dependency file;
- compile `bridge/research_warehouse.py` with existing Collector modules;
- run V8 deterministic tests;
- run V8 CLI/help/schema/dependency/direct-use/safety checks;
- retain existing V3–V7 regression coverage;
- extend current authority/source/safety wiring assertions to V8;
- not commit or push mutable PASS receipts.

**Known stopped-worker caution:** the uncommitted workflow draft had three string-level source assertions that did not match the compact final source. Do not preserve those incorrect literals just because they existed in a draft. Re-read `bridge/research_warehouse.py` and assert stable exported constants/behaviors or exact current source facts. Prefer behavioral/API assertions over brittle source substring assertions when practical.

The workflow is self-check evidence only; it cannot become authority over V3–V8 data semantics.

### 7. Run one coherent V3–V8 regression boundary

After V8 completion and smoke wiring are coherent, run one maintained implementation boundary.

Required coverage:

- Python compile including V8;
- V3 segmented regressions;
- V4 dataset catalog/self-check/current retained evidence;
- V5 storage retention/hardening/status wiring;
- V6 analysis reader/research-only invariants;
- V7 batch acquisition tests/dependency/safety/serial orchestration invariants;
- V8 warehouse tests/dependency/schema/query/provenance/safety invariants;
- existing source namespace/discovery/segmented/storage/batch wiring checks extended to V8.

Do not create Fresh QA, second opinion, cross-check, QA V2/V3, readiness audit, or separate closeout validation. This is implementation recovery and one module self-check boundary, consistent with `TESTING_CADENCE_POLICY.md`.

If the coherent run finds an actual V8 or compatibility defect, fix that defect cluster and rerun affected/current-head checks. Do not create a test loop merely to increase confidence.

### 8. Preserve V3–V7 authority

Do not redesign or rewrite:

- V3 segmented acquisition/terminal authority;
- V4 immutable dataset identity/lifecycle/integrity;
- V5 retention/archive/prune safety;
- V6 research-only analysis authority;
- V7 batch/task/result/retry/resume authority.

Narrow compatibility fixes are allowed only when current V8 integration proves a concrete issue. Record every such change in the RESULT.

## Safety / lane isolation

Still mandatory:

```text
sourceNamespace=winkawaks
readOnly=true
writesGameMemory=false
inputInjection=false
researchOnly=true
semanticAuthority=false
```

V8 must not:

- start/control WinKawaks;
- read/write game process memory directly;
- inject keyboard/gamepad input;
- add Lua/macros;
- perform savestate stepping;
- automate gameplay/scene navigation;
- prune/delete/archive evidence;
- change Alpha production/release authority;
- change Training Farm action/runtime authority;
- merge Browser/WinKawaks/Training Farm provenance.

Do not modify or block:

- `product/alpha/**`;
- Alpha release/proof/live acceptance/danger/target semantics;
- Transport / Recorder / PYLAUNCH / OneClick;
- Training Farm / Stable-Retro / FBNeo / PPO/RL / 10-worker scheduling.

Collector V8 incomplete/blocked is not an Alpha V1 or Training Farm blocker.

## Recovery-owned interruption discipline

Do not treat claim acquisition, one schema, one test file, one workflow patch, one local PASS, or one CI PASS as a stopping point.

If the execution environment is forcibly interrupted again, do not falsely write COMPLETE. Preserve landed commits and leave Recovery V2 claim ACTIVE unless a durable terminal RESULT has actually been committed and ownership-safe closeout is possible.

A tool-call/window limit is an execution interruption, **not** a repository code blocker. If it recurs, report exact progress and resume commit; do not label the module code BLOCKED unless a precise unresolved external/permission/dependency condition actually prevents completion.

## Durable RESULT

On successful completion, write:

`parallel/PM/WINKAWAKS_COLLECTOR_V8_REUSE_FIRST_RESEARCH_WAREHOUSE_QUERY_ACCELERATOR_RECOVERY_V2_RESULT.md`

The RESULT must record at minimum:

- final exact bridge HEAD/tree;
- exact V8 core/test/schema/docs/dependency/workflow blob SHAs;
- DuckDB version/upstream/tag/release/license/classification;
- Polars/Prefect deferred status;
- warehouse/tool/build/export schema/version identities;
- deterministic source-set/build identity semantics;
- indexed V3/V4/V5/V6/V7 authority categories;
- stale/conflict/invalid behavior;
- atomic rebuild/failure preservation;
- refresh idempotence/currentness reconciliation;
- bounded query API/filter/order/limit behavior;
- provenance edge/traversal behavior;
- V7 retry lineage preservation;
- export formats and reproducibility metadata;
- safe SQL/external access boundary;
- synthetic scale fixture scope/result;
- exact current repository data counts where useful;
- exact implementation self-check commands/counts/results;
- exact successful GitHub Actions run ID/head SHA/tree;
- safety/source isolation;
- intentional limitations/non-blocking future work.

Final allowed success verdict:

`COMPLETE — WINKAWAKS COLLECTOR V8 REUSE-FIRST RESEARCH WAREHOUSE / QUERY ACCELERATOR — REBUILDABLE DERIVED RESEARCH INDEX COMPLETE`

Otherwise only a precise unavoidable terminal blocker:

`BLOCKED — WINKAWAKS COLLECTOR V8 REUSE-FIRST RESEARCH WAREHOUSE / QUERY ACCELERATOR RECOVERY V2 — <exact external/unresolvable blocker>`

A failing implementation test, schema mismatch, brittle workflow assertion, or code defect is not automatically an external blocker: fix concrete repository defects first.

## Claim/stage closeout

After and only after the durable Recovery V2 RESULT is committed:

1. re-read the Recovery V2 canonical claim and verify exact claim token;
2. update Recovery V2 canonical claim to `COMPLETE` with RESULT path/commit, final bridge commit/tree and successful workflow run ID;
3. update matching Recovery V2 stage claim to `COMPLETE` with the same terminal authority;
4. preserve the original stopped V8 canonical/stage claims unchanged as historical ACTIVE residue;
5. record `supersedesDedupKey: winkawaks.collector.v8.reuse-first-research-warehouse-query-accelerator` or equivalent successor metadata.

Do not rewrite historical claims merely to make history look clean.

## Stop condition

Continue through the complete remaining V8 implementation scope: dependency, schema/contract, docs, deterministic tests, real defect fixes, smoke integration, one coherent V3–V8 regression/CI boundary, durable RESULT, and Recovery V2 canonical/stage closeout.

Do not stop at claim, dependency install, schema, docs, test creation, workflow edit, local PASS, CI launch, or CI PASS observation.

Only stop at:

- `COMPLETE` with durable RESULT + Recovery V2 canonical/stage closeout;
- precise unavoidable `BLOCKED`;
- duplicate/already-complete/superseded `NO EXECUTION` from the mandatory preflight.

# WinKawaks Collector V8 — Reuse-first Research Warehouse / Query Accelerator Recovery V2 — RESULT

## Verdict

**COMPLETE — WINKAWAKS COLLECTOR V8 REUSE-FIRST RESEARCH WAREHOUSE / QUERY ACCELERATOR — REBUILDABLE DERIVED RESEARCH INDEX COMPLETE**

## Recovery authority

- stage: `WINKAWAKS_COLLECTOR_V8_REUSE_FIRST_RESEARCH_WAREHOUSE_QUERY_ACCELERATOR_RECOVERY_V2`
- canonical dedup key: `winkawaks.collector.v8.reuse-first-research-warehouse-query-accelerator.recovery-v2`
- recovery claim token: `c8a0d6b89f7e4aa793be05bfc8a7d238e2db7976b7a84d73`
- historical original V8 ACTIVE claim was left unchanged; this Recovery V2 is the PM-authorized successor authority.
- implementation repository: `ouyong520/wof-winkawaks-bridge`
- implementation base: `bb10c79be52d1a7e278e7a78fd85d87f930f73d8`
- implementation final HEAD: `5359fe8209ba1dd540733ea0cad09acef8005eb3`
- implementation final tree: `cc2eb2c294ecf8a5461662237efaec840c91352e`
- base→final compare: exactly 1 fast-forward commit; 6 completion files changed/added; `bridge/research_warehouse.py` remained byte-identical to the landed V8 core.

## Exact retained V8 core

The 387-line warehouse core from the interrupted worker was deliberately not rewritten.

- `bridge/research_warehouse.py`
- blob: `17665f9d79b40b0de61eea701c1535f5df205927`
- warehouse schema version: `wof_collector_research_warehouse_v1`
- tool version: `wof-winkawaks-collector-v8-research-warehouse-v1`
- build/source-set identity version: `wof_collector_v8_source_set_v1`
- export schema version: `wof_collector_v8_query_export_v1`

The retained core provides atomic rebuild, content-identity refresh, `CURRENT/STALE/CONFLICT/INVALID`, V3/V4/V5/V6/V7 adapters, bounded parameterized dataset queries, bounded provenance traversal, safe JSON/CSV export, exact DuckDB runtime version enforcement, external-access/unsigned-extension disablement, and a CLI with only `rebuild`, `refresh`, `status`, `verify`, `query`, `show`, and `export` (no unrestricted SQL command).

## Completion commit

Commit `5359fe8209ba1dd540733ea0cad09acef8005eb3` completed the interrupted V8 module without changing the core:

| Path | Final blob | Purpose |
|---|---|---|
| `requirements-collector-v8.txt` | `bcd528daffb8c83ff3344b21e5f1eeeb7945afab` | exact DuckDB pin |
| `schemas/collector_research_warehouse_v1.schema.json` | `a469b551f4046fb9ae95eac299fa8b4ad7e85780` | maintained strict V8 public contract |
| `docs/COLLECTOR_V8_RESEARCH_WAREHOUSE.md` | `14fda9f35b2ed755a168b0b9c9ba873711ab769b` | authority, lifecycle, CLI, reuse and safety documentation |
| `tests/test_research_warehouse.py` | `8664c223871bea80f8cfab0a1813dccf40b42b36` | deterministic V8 implementation self-check |
| `.github/workflows/collector-python-smoke.yml` | `f1a67342b73ebc780e3e56961d84a87cb6da0b15` | coherent V3–V8 regression/current-repository smoke |
| `.gitignore` | `14868d6ca16804d6cf16942de112fcddb05ce9c6` | keeps disposable `derived/warehouse/` out of Git |

## Reuse decision and dependencies

DuckDB remains the only new V8 dependency:

- upstream repository: `duckdb/duckdb`
- exact version/release: `1.5.5` / `v1.5.5`
- license: MIT
- classification: `DIRECT_USE`
- forked: no
- vendored: no
- pin: `duckdb==1.5.5`

Polars and Prefect remain `DEFER`. No fork, reimplementation, vendoring, Polars, or Prefect was introduced.

## Authority model preserved

V8 is a disposable derived index. Source authority remains:

- V3: segmented session/segment identity, order, frame ranges, hashes, counters, terminal/integrity and safety facts. Bad/missing/reordered/duplicate/incomplete segment evidence is never upgraded to clean completion.
- V4: primary dataset selection authority; dataset identity, lifecycle, integrity, scene/grouping metadata and artifact references are preserved rather than synthesized.
- V5: local/archive/protection/storage status is query-only input; warehouse state never grants prune/delete/archive authority.
- V6: analysis input provenance and result identity remain `researchOnly=true`, `semanticAuthority=false`; wrong source namespace fails closed.
- V7: batch/experiment/repeat/trial/attempt/task metadata and retry predecessor lineage are preserved; a successful retry does not erase the failed predecessor.

Raw frame streams are not ingested by default. Frame-level research remains a V6/source-artifact operation.

## Build identity, stale/conflict and query semantics

- source-set digest is based on sorted source-qualified authority identity + content digest plus the versioned build identity and `winkawaks` namespace; traversal order and mtimes do not define identity.
- duplicate source identity with conflicting content digest fails closed.
- `refresh` returns `NOOP` for unchanged current authority.
- changed source identity/content yields `STALE`; default query refuses stale state.
- stale research query requires explicit `allow_stale` and remains visibly labeled `STALE`.
- failed rebuild cannot replace the last valid database; temp output is removed and destination preservation is tested.
- query limit is `1..500`, order is allowlisted, filters are parameterized, and unsupported filters fail closed.
- provenance bounds are depth `0..8` and edges `1..500`.
- safe export rejects absolute/parent traversal and writes reproducibility metadata binding build ID, source-set digest, exact filters/order/limit and output SHA-256.
- no CLI/API surface accepts arbitrary SQL, ATTACH/INSTALL/LOAD/COPY, file-reader, network, DDL, or DML commands.

## Brittle draft assertion recovery

The three fragile V8 source-string assertions from the interrupted, uncommitted workflow draft were not copied. The committed V8 workflow checks behavior/API instead:

1. imports the live `bridge.research_warehouse` constants and exact installed DuckDB version;
2. parses the maintained schema and checks the bounded contract against live constants;
3. inspects the parser command set and executes a real current-repository rebuild → verify → query path.

V8 source/safety wiring in the final regression also uses imported constants and parser behavior rather than compact-source whitespace/string formatting. Existing historical V3–V7 wiring checks remain unchanged where they pre-existed.

## Deterministic implementation self-check

GitHub Actions workflow: `Collector Python smoke check`

- run ID: `33657091103`
- job ID: `100338224624`
- run number: `17`
- exact tested HEAD: `5359fe8209ba1dd540733ea0cad09acef8005eb3`
- result: `success`
- runner Python: CPython `3.12.14`
- installed dependencies observed in log: APScheduler `3.11.3`, DuckDB `1.5.5`

Exact regression counts from the durable Actions log:

- V3 segmented regressions: **15/15 PASS**
- V4 dataset catalog Golden self-check: **20/20 PASS**
- V5 storage retention + recovery: **28/28 PASS**
- V6 segment-aware analysis reader: **31/31 PASS**
- V7 reuse-first batch acquisition: **20/20 PASS**
- V8 research warehouse deterministic tests: **16/16 PASS**
- combined V3–V8 implementation regression cases: **130/130 PASS**

V8's 16 tests include exact dependency/safety, strict versioned schema, no unrestricted SQL command, V3 integrity rejection, V4 lifecycle/integrity preservation, source namespace rejection, V5 archive fact preservation, V6 research-only/nonsemantic preservation, V7 failed-predecessor + successful-retry lineage, order-independent source-set identity, source conflict fail-closed, atomic rebuild preservation, idempotent refresh, stale rejection/explicit stale opt-in, parameterized injection resistance/limits, bounded provenance, safe JSON/CSV export, and a **2,000-row synthetic metadata fixture**.

## Current-repository integration smoke

The same run rebuilt V4 catalog authority from current retained repository evidence and then exercised V5 + V8 on that exact generated catalog.

Current retained catalog:

- V4 records: `33`
- V4 default active/reusable records: `8`

Current V8 rebuild:

- build ID: `wkv8-122aac682638c79182d75ea4c70416d1197f818e84a5373c4de5d19ec437169f`
- source-set digest: `122aac682638c79182d75ea4c70416d1197f818e84a5373c4de5d19ec437169f`
- verify: `CURRENT`, valid
- bounded active-reusable query limit: `5`
- bounded query returned: `5`
- counts:
  - datasets: `33`
  - storage_facts: `33`
  - provenance_edges: `33`
  - source_files: `3`
  - sessions: `0`
  - segments: `0`
  - analyses: `0`
  - analysis_inputs: `0`
  - batches: `0`
  - trials: `0`
  - attempts: `0`

The zero V3/V6/V7 derived-row categories reflect the exact retained source files present in the clean current-repository Actions checkout; they are not synthesized. The adapters themselves are covered by deterministic V8 fixtures and the full V3–V7 regressions above.

## Safety boundary

Final V8 invariant, checked by unit tests and current-repository smoke:

```text
sourceNamespace=winkawaks
readOnly=true
writesGameMemory=false
inputInjection=false
researchOnly=true
semanticAuthority=false
```

No Browser/runtime WOF control, WinKawaks process control, game-memory write, input injection, savestate stepping, AI/search/reward logic, or retention deletion authority was added.

## Concrete defect disposition

No defect in the landed `bb10c79...` warehouse core surfaced under the completed deterministic V8 tests or the current-repository build/verify/query smoke. Therefore Recovery V2 did not churn that core. The actual interrupted-state defects closed here were the missing direct dependency pin, missing maintained schema/contract, missing documentation, missing deterministic V8 tests, missing V8 smoke/regression integration, untracked derived warehouse output, and the uncommitted workflow draft's brittle V8 source-string assertions.

## Closeout

Recovery V2 canonical/stage claims must be transitioned from `ACTIVE` to `COMPLETE` using the same token above and must reference this durable RESULT and its commit. The historical original V8 ACTIVE claim remains untouched and is superseded by this PM-authorized Recovery V2 result authority.

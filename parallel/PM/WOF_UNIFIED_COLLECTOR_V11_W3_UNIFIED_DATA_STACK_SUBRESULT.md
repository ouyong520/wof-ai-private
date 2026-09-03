# WOF Unified Collector V11 — W3 Unified Data Stack Sub-result

## Verdict

`SUBCOMPLETE — W3 source-aware V4–V9 data-stack generalization implemented and focused-regression clean; ready for V11 main-worker integration and terminal validation.`

This is a **W3 sub-result only**. It does not claim umbrella V11 completion, W1 Training Farm exporter authority, W2 adapter/control-plane authority, or terminal V11 regression/closeout authority.

## Authority

- Dispatch: `parallel/PM/WOF_UNIFIED_COLLECTOR_V11_PARALLEL_3_WORKER_DISPATCH.md`
- Parent START_PROMPT: `parallel/PM/WOF_UNIFIED_COLLECTOR_V11_TRAINING_FARM_ADAPTER_UNIFIED_TASK_DATA_STACK_START_PROMPT.md`
- W3 dedup key: `wof.unified-collector.v11.workstream.unified-data-stack`
- W3 claim: `parallel/PM/DEDUP_CLAIMS/wof.unified-collector.v11.workstream.unified-data-stack.json`
- W3 claim token: `v11-w3-9dda02ab40864fedb9b90e2059c62b97`
- Parent umbrella claim token: `v11-8ae06246ff6533ce7ba6df8d37fc5f93` — retained by the main worker and not modified by W3.

## Bridge implementation authority

Repository: `ouyong520/wof-winkawaks-bridge`

W3 began from bridge parent `1e8cc821e9baa1399c53a303f467dbc546a98fc2`, after the concurrently owned W2 adapter/control-plane commits already present on `main`.

W3 additive implementation commits, in order:

1. `bd3108a9c42f6448022c9512df42c464c5260ac4` — source-aware common contract and explicit source-local semantic boundary.
2. `ca251a8d29262920fe466dab0e832ca650f57ac7` — unified V4 registration/provenance and V5 source-aware retention view.
3. `943e916679e39d37842c1d55adda30e0675aa398` — explicit per-source analysis readers and bounded batch integration envelope.
4. `4f9a14fa3151bbf0e5e9479d6fe32e187953fb3d` — unified projections inside the existing V8 DuckDB authority.
5. `04d62201d6266a78d53e8f698b47b0e36afc2383` — source-aware reuse-first planner and immutable cross-source mapping contract gate.
6. `b5095ef8ad738a4577abfa46b129194dbbedd40c` — public W3 facade.
7. `2e2a41a921a37179da1249722a4b1e3faf1f68d7` — focused three-source regression.
8. `69d0a17068f5e234c004b2ff8b838312e4d4d59c` — W3 authority/boundary documentation.
9. `079ec6ff43beea744408cc870ee78b1c818cffb1` — focused W3 workflow.
10. `8468c2fed5efeef068bd980c437384885d4f07d4` — focused workflow extended with legacy V4–V9 compatibility regression.

W3 handoff bridge commit: `8468c2fed5efeef068bd980c437384885d4f07d4`.

## Files added by W3

- `bridge/unified_data_common.py`
- `bridge/unified_dataset.py`
- `bridge/unified_analysis_batch.py`
- `bridge/unified_warehouse.py`
- `bridge/unified_reuse.py`
- `bridge/unified_data_stack.py`
- `tests/test_unified_data_stack_v11.py`
- `docs/COLLECTOR_V11_UNIFIED_DATA_STACK.md`
- `.github/workflows/collector-v11-w3-unified-data-stack.yml`

W3 intentionally did **not** modify existing V4–V9 implementation files. Existing WinKawaks behavior remains the compatibility authority, while V11 source-aware behavior is additive through the unified facade.

## V4 — one source-aware dataset/provenance catalog

The existing V4 `catalog/dataset_catalog_v1.json` remains the only dataset catalog. New Browser/WASM, WinKawaks, and Stable-Retro/FBNeo registrations become ordinary V4 records through `dataset_catalog.upsert_record`.

The registration facade requires and preserves:

- exact `sourceNamespace`;
- immutable task identity;
- immutable result identity/SHA-256;
- source-specific `runtimeProvenance.runtimeIdentity`;
- producer component/version;
- artifact SHA-256 and byte-availability facts;
- source schema version;
- original repository/path/source commit-or-blob registration provenance;
- lifecycle/integrity/completeness facts without semantic promotion.

Existing V4 task authority remains keyed by `(sourceNamespace, sourceTaskId)`, and artifact/hash authority remains source-namespaced. The same task ID may therefore exist independently in the three source namespaces without identity collision.

The legacy repository importer remains intentionally WinKawaks-only; W3 does not reinterpret old WinKawaks repository evidence as Browser/WASM or Stable-Retro/FBNeo evidence.

Historical metadata-only records use the same V4 catalog and retain original artifact hash/provenance. They must explicitly declare limitations; artifacts marked `bytesAvailable=false` are excluded only from the derived V5 local-storage view so retained historical metadata is not falsely reported as a missing local file. The authoritative V4 record is unchanged.

## V5 — retention and pressure reuse

W3 delegates storage accounting, pressure policy, archive receipts, protection rules, and pruning safety to the existing V5 manager. No second retention implementation or destructive path was created.

`source_aware_storage_status` adds exact source/runtime/registration provenance to V5 status rows while retaining the existing V5 policy and archive authority.

## V6 — analysis

`SourceReaderRegistry` requires an explicit reader for the exact source namespace. There is no source alias, fallback, or mixed-source reader call.

The common analysis envelope preserves dataset/sourceTask/result/runtime provenance and is always:

- `researchOnly=true`
- `semanticAuthority=false`
- `readOnly=true`
- `writesGameMemory=false`
- `inputInjection=false`

Source-specific readers alone may interpret their own source bytes.

## V7 — batch integration

`compile_batch_integration` provides a bounded source-specific integration envelope with `maxConcurrentReads` in `[1,10]` and references only existing task/result/runtime selectors.

It explicitly records:

- `existingQueueOnly=true`
- `queueCreated=false`
- `schedulerCreated=false`
- `adapterExecutionOwnedHere=false`
- `collectionOrExportReadsOnly=true`

W3 creates no second queue, does not execute adapter work, does not choose Training Farm actions, does not inject game input, and does not orchestrate workers.

## V8 — one DuckDB warehouse

W3 reuses exactly DuckDB `1.5.5` and `bridge.research_warehouse.DEFAULT_DB_PATH`, the existing V8 database authority. It adds only derived source-aware tables inside that database:

- `unified_dataset_projection_v11`
- `unified_artifact_projection_v11`
- `unified_projection_meta_v11`

No second warehouse was created. Existing V8 tables are not dropped or rewritten. The V4 catalog remains source of truth.

Projection rows retain source namespace, task/result identity, source schema, runtime provenance, registration provenance, complete source provenance, reuse material, artifact metadata, and canonical V4 record JSON. The query facade is bounded and parameterized and exposes no arbitrary SQL surface.

## V9 — reuse-first generalization

Reuse remains exact same-source by default. Legacy WinKawaks reuse material continues to use the existing V9 material authority. Browser/WASM and Stable-Retro/FBNeo require explicit producer-authored `reuseMaterial`; W3 never derives their semantic material from WinKawaks fields.

Cross-source RAM offsets, names, or numerically equal fields never establish equivalence. Cross-source candidates require an explicit immutable mapping contract with repository/path/source-commit provenance and contract SHA-256.

A cross-source mapped dataset is only research-related by default. It can fill a strict reuse slot only when both conditions hold:

1. the request explicitly authorizes cross-source slot reuse; and
2. the immutable mapping contract explicitly sets `strictSlotReuseAuthorized=true`.

Mapped allocations preserve mapping ID, mapping contract SHA-256, mapping provenance, source namespace, and runtime provenance.

## Source-local RAM / semantic authority

The W3 common contract explicitly records `ramSemanticEquivalence=false` and `semanticAuthority=false`.

No generic W3 layer assumes any equivalence among:

- Browser/WASM offsets;
- WinKawaks offsets;
- Stable-Retro/FBNeo offsets.

Cross-source relationships are valid only through an explicit immutable mapping contract. Same numeric offset, field name, or similar result content is insufficient.

## Focused regression evidence

Workflow: `.github/workflows/collector-v11-w3-unified-data-stack.yml`

GitHub Actions run: `33714040635`

Job/check: `100519361741` (`w3-focused-regression`)

Validated commit: `8468c2fed5efeef068bd980c437384885d4f07d4`

Results:

- W3 additive module/test compilation: PASS.
- New three-source focused regression: `8/8` PASS.
- Existing V4–V9 compatibility regression: `136/136` PASS.
- Total focused + compatibility tests in this run: `144/144` PASS.
- DuckDB authority guard: PASS — exact `1.5.5`, W3 DB path equals existing V8 DB path.
- Source namespace guard: PASS — exactly `browser-wasm`, `winkawaks`, `stable-retro-fbneo`.
- W3 ownership/control-plane scan: PASS.
- Source-local RAM/semantic-authority guard: PASS.

The only workflow messages outside the test results were GitHub Actions Node.js deprecation warnings from upstream `actions/checkout@v4` / `actions/setup-python@v5`; no W3 implementation defect was reported.

## Ownership boundary verification

W3 added no changes under `training/farm/**` and did not modify:

- `bridge/adapters/**`;
- Unified Collector Agent implementation;
- unified task/status/result v2 schemas;
- queue routing implementation;
- gameplay/input authority.

W3 did not create a second queue, second catalog, or second DuckDB warehouse.

## Handoff

W3 is ready for the main worker to consume at bridge commit `8468c2fed5efeef068bd980c437384885d4f07d4` (or a later descendant containing the same W3 commits), wire against the W1/W2 outputs if needed, and execute the parent V11 terminal regression/CI/RESULT/claim closeout under umbrella authority.

W3 itself intentionally stops at `SUBCOMPLETE`.

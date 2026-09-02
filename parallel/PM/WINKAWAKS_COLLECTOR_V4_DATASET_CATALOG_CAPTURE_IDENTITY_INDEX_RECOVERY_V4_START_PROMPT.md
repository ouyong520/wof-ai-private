# WinKawaks Collector V4 — Dataset Catalog / Capture Identity Index Recovery V4

stageId: `WINKAWAKS_COLLECTOR_V4_DATASET_CATALOG_CAPTURE_IDENTITY_INDEX_RECOVERY_V4`
dedupProtocol: `v2`
dedupKey: `winkawaks.collector.v4.dataset-catalog-capture-identity-index.recovery-v4`
dedupMode: `exclusive`

Priority: **P1 reusable datasets / acquisition infrastructure recovery**

## Read first

- `parallel/PM/WINKAWAKS_COLLECTOR_V4_DATASET_CATALOG_CAPTURE_IDENTITY_INDEX_START_PROMPT.md`
- `parallel/PM/WINKAWAKS_COLLECTOR_V4_DATASET_CATALOG_CAPTURE_IDENTITY_INDEX_RECOVERY_V2_START_PROMPT.md`
- `parallel/PM/WINKAWAKS_COLLECTOR_V4_DATASET_CATALOG_CAPTURE_IDENTITY_INDEX_RECOVERY_V3_START_PROMPT.md`
- `parallel/PM/COLLECTOR_WORKER_EXECUTION_POLICY.md`
- `parallel/PM/TESTING_CADENCE_POLICY.md`
- `parallel/PM/STAGE_DEDUP_GUARD.md`
- `COLLECTOR_ROUTING.md`
- `RUNTIME_DATA_SOURCE_BOUNDARIES.md`
- `parallel/BASECAP/BASE_CAPTURE_CATALOG.md`
- current original V4 claim/stage and Recovery V2/V3 claims/stages
- current `ouyong520/wof-ai-private/main`
- current `ouyong520/wof-winkawaks-bridge/main`

This is PM-authorized implementation recovery. Recovery V2 and Recovery V3 both stopped after claim acquisition without advancing `wof-winkawaks-bridge`. Do not repeat that failure mode.

**Claim acquisition is only ownership setup, not implementation progress and not a valid stopping point. After the canonical/stage claim is acquired and token re-read successfully, immediately continue the module work in the same run.**

Do not overwrite or falsely complete the historical original/V2/V3 claims. Recovery V4 must use its own canonical dedup v2 authority and supersede the stopped generations only after actual completion.

## Current implementation baseline

At prompt creation, `ouyong520/wof-winkawaks-bridge/main` is still:

`114862591aa94a359e60e383f076a70ee80da4fd`

Already landed V4 work that must be preserved rather than rewritten:

- `82699b8a0912325a7ce60d47ad7f80c73b072262` — deterministic dataset catalog core;
- `2abf0b773f57aba793934102105077bde0d26098` — BASECAP authority seed;
- `0e08179e0f464ef75b1b5abf73d0dfbf4dc97578` — retained task identity alignment;
- `c7da63fa316dcb52b15e77f9cba64792b5f26839` — catalog Golden self-check;
- `9785454dfcdb80325a655a2c644f5bacf238eac6` — versioned catalog schema;
- `212515168ac9e78d5bb471aef740c52ef4200cc2` — contract/CLI documentation;
- `114862591aa94a359e60e383f076a70ee80da4fd` — Golden integration in Collector smoke workflow.

Expected current surfaces include:

- `bridge/dataset_catalog.py`
- `tests/test_dataset_catalog.py`
- `schemas/collector_dataset_catalog_v1.schema.json`
- `catalog/basecap_authority_v1.json`
- `catalog/dataset_catalog_v1.json`
- `docs/COLLECTOR_V4_DATASET_CATALOG.md`
- `.github/workflows/collector-python-smoke.yml`

Re-read current HEAD first in case another worker has changed it.

## Objective

Finish the complete original V4 Dataset Catalog / Capture Identity Index module from current HEAD. Do not start V5 and do not open QA.

The completed module must provide one coherent reusable/searchable catalog surface for legacy Collector v1/v2 captures and V3 segmented sessions while preserving strict evidence provenance and fail-closed identity behavior.

### Required functional closure

Verify and, where necessary, complete/fix all of the following:

1. **Versioned schema**
   - machine-readable catalog/index schema is current and matches produced catalog records;
   - strict validation rejects malformed/coercible/conflicting records.

2. **Deterministic immutable dataset identity**
   - identity binds authoritative source/task/artifact authority, not filenames or labels;
   - same input always yields same identity;
   - same `taskId` with different `taskBlobSha`, capture/session, manifest or artifact authority fails closed.

3. **Legacy Collector v1/v2 support**
   - snapshot/burst records remain indexable;
   - historical unknown fields remain unknown instead of being fabricated.

4. **V3 segmented support**
   - index identity binds authoritative manifest plus ordered segment identities/hashes and source/runtime/session authority;
   - invalid/missing/reordered/hash-mismatched segmented evidence cannot be indexed as authoritative COMPLETE/reusable evidence.

5. **BASECAP reuse**
   - existing BASECAP authority seeds/imports deterministically;
   - operator labels, status, scene description, confounders and provenance are preserved exactly as repository authority;
   - no raw-byte semantic guessing and no Owner recapture requirement for already retained scenes.

6. **Integrity vs semantic lifecycle**
   - mechanical integrity and research lifecycle remain separate;
   - hash success must not automatically promote a record to `VALID`;
   - `INVALID`, `SUPERSEDED`, `UNREVIEWED` and current reusable records remain distinguishable.

7. **Build / rebuild / verify / query / show**
   - deterministic CLI/module surface works from repository conventions;
   - unchanged rebuild is idempotent;
   - ordering is deterministic;
   - duplicate/conflict diagnostics fail closed;
   - no silent destructive overwrite.

8. **Atomic catalog update**
   - lock/write/replace behavior cannot leave a partial or silently corrupted catalog;
   - interruption/failure before replacement leaves last valid catalog intact where repository design permits.

9. **Query defaults**
   - normal/default reuse query does not silently return `INVALID` or `SUPERSEDED` records as current canonical data;
   - explicit historical query can still discover them.

10. **Source isolation**
    - `browser-wasm`, `winkawaks`, `stable-retro-fbneo` provenance remain distinct;
    - this module must not transfer offsets/runtime semantics between them.

11. **Schema/docs/generated catalog consistency**
    - code, schema, seed, generated catalog, CLI docs and workflow checks must describe the same current contract.

12. **Experiment/repeated-trial metadata**
    - preserve optional explicit experiment/trial/repeat grouping fields supported by the schema;
    - they remain descriptive research metadata, not gameplay authority.

## Implementation self-check

This is implementation recovery, not independent QA.

Complete/fix the whole module first, then run one coherent implementation-owned self-check boundary. Use only checks needed to establish the candidate, including as applicable:

- Python compile/parse;
- `tests/test_dataset_catalog.py`;
- deterministic identity generation;
- schema validation;
- idempotent rebuild;
- duplicate/conflict fail-closed;
- same taskId/different authority conflict;
- BASECAP seed preservation;
- V3 segmented manifest/ordered-segment authority checks;
- lifecycle/integrity separation;
- query behavior;
- atomic update behavior;
- current Collector regression/smoke checks needed to prove no V3/legacy regression.

Fix concrete defects found by these checks inside this V4 scope, then rerun affected checks. Do not create Fresh QA, second opinion, cross-check, QA V2/V3/V4, readiness audit, Browser/WOF run, WinKawaks recapture or Training Farm validation.

## Side-lane boundary

Collector remains independent from Alpha V1 and Training Farm/10-worker training.

Do not modify or block:

- `product/alpha/**`;
- Alpha release/acceptance/proof;
- Transport;
- Recorder;
- PYLAUNCH;
- OneClick;
- Training Farm runtime/policy;
- current 10-worker training.

Collector invariants remain:

- `readOnly=true`;
- `writesGameMemory=false`;
- `inputInjection=false`.

## Durable completion

Before stopping COMPLETE, produce a durable Recovery V4 RESULT under `parallel/PM/**` containing at minimum:

- exact final `wof-winkawaks-bridge` HEAD/tree;
- exact relevant V4 blobs;
- final catalog/schema version;
- deterministic dataset identity derivation contract;
- legacy v1/v2 handling;
- V3 segmented authority handling;
- BASECAP seed/reuse behavior;
- integrity vs lifecycle behavior;
- duplicate/conflict/supersession rules;
- build/verify/query/show CLI surface;
- atomic/idempotent update behavior;
- implementation-owned self-check commands/results;
- remaining local-only limitations if any.

Then close Recovery V4 canonical claim and stage under canonical dedup v2 and record that it supersedes the stopped original/V2/V3 generations without rewriting their historical state.

## Stop rule — mandatory

Do not stop after claim acquisition. Do not stop after repository inspection. Do not stop after one patch. Do not stop after one test. Do not stop after documentation. Do not stop before RESULT/claim closeout.

Keep reporting sparse and continue through the entire assigned V4 module closure in the same worker run.

Stop only at:

`COMPLETE — WINKAWAKS COLLECTOR V4 DATASET CATALOG / CAPTURE IDENTITY INDEX — REUSABLE SEARCHABLE DATASET MODULE COMPLETE`

or:

`BLOCKED — WINKAWAKS COLLECTOR V4 DATASET CATALOG / CAPTURE IDENTITY INDEX — <precise unavoidable blocker>`

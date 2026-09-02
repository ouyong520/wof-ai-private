# WinKawaks Collector V4 — Dataset Catalog / Capture Identity Index Recovery V3

stageId: `WINKAWAKS_COLLECTOR_V4_DATASET_CATALOG_CAPTURE_IDENTITY_INDEX_RECOVERY_V3`
dedupProtocol: `v2`
dedupKey: `winkawaks.collector.v4.dataset-catalog-capture-identity-index.recovery-v3`
dedupMode: `exclusive`

Priority: **P1 reusable datasets / acquisition infrastructure recovery**

## Read first

- `parallel/PM/WINKAWAKS_COLLECTOR_V4_DATASET_CATALOG_CAPTURE_IDENTITY_INDEX_START_PROMPT.md`
- `parallel/PM/WINKAWAKS_COLLECTOR_V4_DATASET_CATALOG_CAPTURE_IDENTITY_INDEX_RECOVERY_V2_START_PROMPT.md`
- `parallel/PM/COLLECTOR_WORKER_EXECUTION_POLICY.md`
- `parallel/PM/TESTING_CADENCE_POLICY.md`
- `parallel/PM/STAGE_DEDUP_GUARD.md`
- `COLLECTOR_ROUTING.md`
- `RUNTIME_DATA_SOURCE_BOUNDARIES.md`
- `parallel/BASECAP/BASE_CAPTURE_CATALOG.md`
- current original V4 claim/stage
- current Recovery V2 claim/stage
- current `ouyong520/wof-ai-private/main`
- current `ouyong520/wof-winkawaks-bridge/main`

This is PM-authorized **implementation recovery V3**. Recovery V2 stopped after creating its recovery claim/stage and did not advance the bridge implementation or produce a durable RESULT. Do not reuse or overwrite the Recovery V2 claim. Acquire a new canonical dedup v2 Recovery V3 claim/stage and continue from current HEAD.

## Current repository facts

At Recovery V3 start, the latest known V4 bridge candidate remains:

`114862591aa94a359e60e383f076a70ee80da4fd`

Substantial V4 implementation is already landed and must be preserved rather than rewritten:

- `82699b8a0912325a7ce60d47ad7f80c73b072262` — deterministic dataset catalog core;
- `2abf0b773f57aba793934102105077bde0d26098` — BASECAP dataset authority seed;
- `0e08179e0f464ef75b1b5abf73d0dfbf4dc97578` — BASECAP seed aligned to retained task identities;
- `c7da63fa316dcb52b15e77f9cba64792b5f26839` — catalog Golden self-check;
- `9785454dfcdb80325a655a2c644f5bacf238eac6` — versioned dataset catalog schema;
- `212515168ac9e78d5bb471aef740c52ef4200cc2` — dataset catalog contract and CLI documentation;
- `114862591aa94a359e60e383f076a70ee80da4fd` — Golden self-check extended to current-repository catalog integration.

Known V4 surfaces include:

- `bridge/dataset_catalog.py`;
- `tests/test_dataset_catalog.py`;
- `schemas/collector_dataset_catalog_v1.schema.json`;
- `catalog/basecap_authority_v1.json`;
- `catalog/dataset_catalog_v1.json`;
- `docs/COLLECTOR_V4_DATASET_CATALOG.md`;
- `.github/workflows/collector-python-smoke.yml`.

Re-read current HEAD before changing anything in case concurrent commits have landed.

## Recovery V3 objective

Finish the existing V4 module end-to-end. Do not restart the module from zero and do not move to V5.

The final V4 candidate must satisfy the original V4 START_PROMPT, including:

- stable versioned dataset catalog/index schema;
- deterministic immutable dataset identity derived only from authoritative provenance/integrity fields;
- strict WinKawaks / Browser / Stable-Retro-FBNeo namespace separation;
- honest legacy v1/v2 snapshot/burst indexing without fabricated historical fields;
- V3 segmented-session indexing bound to authoritative manifest, ordered segments/hashes, capture/session/source/runtime identity;
- fail-closed same-task conflicts when taskBlobSha/capture/session/artifact authority differs;
- separate mechanical integrity state from semantic/catalog lifecycle state;
- no automatic `VALID` promotion from hash success;
- BASECAP ingestion/seed preserving operator/repository labels, confounders and provenance without Owner recapture;
- deterministic CLI/index operations for build/rebuild/index, verify, query and show as implemented by repository conventions;
- deterministic ordering, idempotent unchanged rebuild, strict schema validation and atomic write/replace;
- duplicate/conflict detection with no silent destructive overwrite;
- useful query/filter support across dataset/task/source/action/scene/status/time/group/hash/retention fields;
- explicit experiment/repeated-trial grouping where the schema supports it;
- explicit `INVALID` vs `SUPERSEDED` lifecycle/history;
- no semantic guessing from raw RAM;
- Collector read-only and side-lane isolation invariants preserved.

## Priority recovery tail

Because core/schema/docs/Golden integration are already landed, spend effort on **completion and authority coherence**, not code churn. Verify and fix only concrete gaps in this order:

1. current schema, generated catalog, BASECAP seed, CLI and docs agree;
2. deterministic dataset identity binds all fields promised by the contract;
3. V3 COMPLETE datasets cannot be cataloged as authoritative if manifest/ordered segment/hash authority fails;
4. legacy records preserve unknown historical fields as unknown rather than guessed;
5. same taskId with different taskBlobSha/capture/session/artifact identity fails closed;
6. duplicate dataset identities and artifact/hash conflicts fail closed;
7. `VERIFIED/PARTIAL/FAILED/UNKNOWN` remains independent from `VALID/INVALID/SUPERSEDED/UNREVIEWED`;
8. BASECAP labels are imported from repository authority only;
9. default query does not treat INVALID/SUPERSEDED as current reusable canonical data unless explicitly requested;
10. rebuild/index is deterministic, idempotent and atomic;
11. source namespace separation is enforced;
12. current workflow/self-check actually covers the final candidate and no stale assertions remain.

If these are already correct, prove them with implementation-owned self-checks instead of rewriting working code.

## Testing cadence

This is implementation recovery, not independent QA.

Do not create Fresh QA, second opinion, cross-check, QA V2/V3/V4, readiness audit, real WinKawaks recapture, Browser/WOF validation or Training Farm validation.

Complete the coherent V4 module first, then run one consolidated implementation self-check boundary, using only what is necessary, such as:

- compile/parse;
- `tests/test_dataset_catalog.py`;
- schema validation;
- deterministic identity/rebuild;
- conflict/fail-closed cases;
- BASECAP seed preservation;
- V3 manifest/segment authority indexing;
- query/filter behavior;
- atomic update behavior;
- relevant V3/legacy Collector regressions;
- current `Collector Python smoke check` if applicable.

Fix concrete failures found inside V4 and rerun only the affected/self-check boundary. Do not spend time multiplying test generations.

## Durable completion

Before COMPLETE, write a durable Recovery V3 RESULT under `parallel/PM/**` recording at minimum:

- exact final `wof-winkawaks-bridge` HEAD/tree;
- exact relevant V4 blobs;
- final schema/version;
- deterministic identity derivation contract;
- legacy v1/v2 handling;
- V3 segmented authority handling;
- BASECAP seed/import behavior;
- integrity vs lifecycle semantics;
- duplicate/conflict/supersession behavior;
- CLI/query surface;
- atomic/idempotent rebuild behavior;
- implementation-owned self-check commands/results;
- remaining real/local limitations if any.

Then close the Recovery V3 canonical claim/stage under canonical dedup v2. Preserve historical truth:

- original V4 ACTIVE claim remains historical stopped-worker residue;
- Recovery V2 ACTIVE claim remains historical stopped-recovery residue;
- Recovery V3 becomes the superseding completed generation if this recovery succeeds.

## Side-lane boundary

Do not modify or block Alpha V1, `product/alpha/**`, Transport, Recorder, PYLAUNCH, OneClick, Browser/WOF release proof, Training Farm runtime/policy, or the current 10-worker training lane.

Collector remains:

- `readOnly=true`;
- `writesGameMemory=false`;
- `inputInjection=false`.

## Stop

Do not stop at claim creation, file inspection, one code patch, one test run, documentation, or any other intermediate milestone. Keep reporting sparse and continue through the complete V4 functional/module objective, all necessary integration/fixes, one consolidated implementation self-check boundary, durable RESULT, and Recovery V3 claim/stage closeout.

Stop only at:

`COMPLETE — WINKAWAKS COLLECTOR V4 DATASET CATALOG / CAPTURE IDENTITY INDEX — REUSABLE SEARCHABLE DATASET MODULE COMPLETE`

or:

`BLOCKED — WINKAWAKS COLLECTOR V4 DATASET CATALOG / CAPTURE IDENTITY INDEX — <precise unavoidable blocker>`
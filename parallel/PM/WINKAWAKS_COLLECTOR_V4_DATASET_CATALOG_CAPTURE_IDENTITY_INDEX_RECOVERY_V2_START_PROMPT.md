# WinKawaks Collector V4 — Dataset Catalog / Capture Identity Index Recovery V2

stageId: `WINKAWAKS_COLLECTOR_V4_DATASET_CATALOG_CAPTURE_IDENTITY_INDEX_RECOVERY_V2`
dedupProtocol: `v2`
dedupKey: `winkawaks.collector.v4.dataset-catalog-capture-identity-index.recovery-v2`
dedupMode: `exclusive`

Priority: **P1 reusable datasets / acquisition infrastructure recovery**

## Read first

- `parallel/PM/WINKAWAKS_COLLECTOR_V4_DATASET_CATALOG_CAPTURE_IDENTITY_INDEX_START_PROMPT.md`
- `parallel/PM/COLLECTOR_WORKER_EXECUTION_POLICY.md`
- `parallel/PM/TESTING_CADENCE_POLICY.md`
- `parallel/PM/STAGE_DEDUP_GUARD.md`
- `COLLECTOR_ROUTING.md`
- `RUNTIME_DATA_SOURCE_BOUNDARIES.md`
- `parallel/BASECAP/BASE_CAPTURE_CATALOG.md`
- `parallel/PM/WINKAWAKS_COLLECTOR_V3_LONG_SESSION_SEGMENTED_CAPTURE_RECOVERY_V2_RESULT.md`
- current original V4 canonical/stage claims
- current `ouyong520/wof-ai-private/main`
- current `ouyong520/wof-winkawaks-bridge/main`

This is PM-authorized **implementation recovery** for a stopped V4 worker. It is not Fresh QA and it is not a request to restart V4 from zero.

The original V4 canonical claim is still historical `ACTIVE`. Preserve that history. Recovery V2 must acquire its own canonical dedup v2 recovery claim/stage and, when complete, supersede the stopped original generation without fabricating that the original worker completed normally.

## Current repository facts to preserve and verify

At the time this recovery prompt was staged, `ouyong520/wof-winkawaks-bridge/main` had already advanced from the V3 candidate `c180e303cb1caf10effde49edceec4ea70a26cc2` through substantial V4 implementation, including:

- `82699b8a0912325a7ce60d47ad7f80c73b072262` — deterministic dataset catalog core;
- `2abf0b773f57aba793934102105077bde0d26098` — BASECAP dataset authority seed;
- `0e08179e0f464ef75b1b5abf73d0dfbf4dc97578` — BASECAP seed aligned to retained task identities;
- `c7da63fa316dcb52b15e77f9cba64792b5f26839` — catalog Golden self-check;
- `9785454dfcdb80325a655a2c644f5bacf238eac6` — versioned dataset catalog schema;
- `212515168ac9e78d5bb471aef740c52ef4200cc2` — dataset catalog contract and CLI documentation;
- `114862591aa94a359e60e383f076a70ee80da4fd` — Golden self-check extended to repository catalog integration.

The current candidate already appears to include at least these V4 surfaces:

- `bridge/dataset_catalog.py`;
- `tests/test_dataset_catalog.py`;
- `schemas/collector_dataset_catalog_v1.schema.json`;
- `catalog/basecap_authority_v1.json`;
- `catalog/dataset_catalog_v1.json`;
- `docs/COLLECTOR_V4_DATASET_CATALOG.md`;
- `.github/workflows/collector-python-smoke.yml` integration.

Re-read current HEAD because newer commits may exist. Treat the list above as recovery context, not as proof that the module is complete.

## Recovery objective

Finish the original V4 module end-to-end from current HEAD, preserving completed implementation and fixing only concrete remaining defects or integration gaps.

The final module must satisfy the full original V4 START_PROMPT, including:

- one versioned machine-readable dataset catalog/index schema;
- deterministic immutable dataset/capture identity derived from authoritative provenance/integrity fields;
- strict source namespaces, with WinKawaks primary and Browser / Training Farm never silently reinterpreted as WinKawaks;
- legacy Collector v1/v2 snapshot/burst support without fabricating unavailable historical fields;
- V3 segmented-session support bound to manifest + ordered segment identities/hashes + source/runtime identity;
- strict same-task conflict detection: same taskId with different taskBlobSha/capture/session/artifact authority must fail closed rather than merge;
- integrity state kept separate from catalog/semantic lifecycle state;
- no automatic `VALID` promotion from hash/mechanical health alone;
- deterministic BASECAP seed/import/reference preserving operator/repository labels, confounders, limitations and provenance;
- no Owner recapture required for already retained BASECAP scenes;
- deterministic build/rebuild/index/verify/query/show surface following repository conventions;
- strict schema validation, deterministic ordering, idempotent unchanged rebuild, atomic catalog replacement, duplicate/conflict diagnostics and no silent destructive overwrite;
- practical query support for dataset identity, taskId, source, action/type, scene metadata, lifecycle/integrity state, capture time, experiment/trial grouping and artifact/hash/retention fields;
- optional explicit experimentId/trialId/repeatGroupId/trialOrdinal/expected discriminator metadata when supported by the final schema;
- explicit `INVALID` vs `SUPERSEDED` history, with old records retained rather than silently disappearing;
- no semantic guessing from raw bytes;
- Collector side-lane isolation and read-only invariants preserved.

## Recovery-tail checks

The stopped worker had reached workflow/Golden integration, so prioritize finishing the **module boundary**, not rewriting the core.

Verify current HEAD for any remaining gaps in these areas:

1. catalog schema and generated/indexed catalog agree exactly;
2. dataset identity derivation is deterministic and actually binds the authoritative fields promised by docs;
3. V3 segmented records cannot be indexed as authoritative COMPLETE when manifest/segment authority fails;
4. legacy records remain honest about unknown/unavailable historical fields;
5. BASECAP labels/lifecycle are seeded from repository authority rather than inferred from bytes;
6. same-task/different-authority conflicts fail closed;
7. duplicate dataset identity and artifact/hash conflicts fail closed;
8. rerun on unchanged inputs is deterministic/idempotent;
9. atomic write/lock behavior cannot silently corrupt/partially replace the catalog;
10. query defaults do not accidentally surface INVALID/SUPERSEDED records as current reusable canonical data unless explicitly requested;
11. source namespace separation remains explicit;
12. docs/CLI/schema/tests/current generated catalog are not mutually stale.

If a current implementation-owned self-check or workflow exposes a concrete defect, fix the related defect cluster inside this V4 recovery scope and rerun only the affected checks.

## Testing cadence

This is implementation recovery, **not independent QA**.

Do not create:

- Fresh QA;
- second opinion;
- cross-check;
- QA V2/V3/V4;
- readiness audit;
- real WinKawaks recapture;
- Browser/WOF validation;
- Training Farm validation.

Use only implementation-owned checks needed to finish a coherent V4 candidate, such as:

- compile/parse;
- `tests/test_dataset_catalog.py`;
- schema validation;
- deterministic identity/rebuild tests;
- conflict/fail-closed tests;
- BASECAP seed preservation;
- V3 manifest/segment authority indexing checks;
- query/filter behavior;
- atomic update behavior;
- existing Collector regressions needed to prove V4 did not break V3/legacy behavior;
- current `Collector Python smoke check` if applicable.

Do not spend time multiplying test generations. Complete the module, run the necessary implementation self-check once at the coherent boundary, fix real failures if any, then close it.

## Side-lane boundary

Collector remains an independent R&D/data-acquisition side lane.

This task must not modify or block:

- `product/alpha/**`;
- Alpha V1 release/acceptance/proof;
- Transport / Recorder / PYLAUNCH / OneClick;
- Training Farm runtime/policy;
- current 10-worker training lane.

Collector remains:

- `readOnly=true`;
- `writesGameMemory=false`;
- `inputInjection=false`.

Browser, WinKawaks and Stable-Retro/FBNeo provenance remain distinct.

## Durable completion

Before declaring COMPLETE, write a durable Recovery V2 RESULT under `parallel/PM/**` recording at minimum:

- exact final `wof-winkawaks-bridge` HEAD/tree;
- exact relevant current V4 blobs;
- final catalog schema/version;
- dataset identity derivation contract;
- legacy v1/v2 handling;
- V3 segmented handling and authority validation;
- BASECAP ingestion/seed behavior;
- integrity vs lifecycle semantics;
- conflict/duplicate/supersession behavior;
- query/CLI surface;
- atomic/idempotent rebuild behavior;
- implementation-owned self-check commands/results;
- any real limitation that remains local-only or requires future acquisition/runtime evidence.

Then close the Recovery V2 canonical claim and stage correctly under canonical dedup v2. Leave the stopped original V4 claim as historical truth and mark the Recovery generation as the superseding completed authority.

## Stop

Do not stop at an intermediate milestone. Keep implementation reporting sparse. Continue through the complete assigned V4 functional/module scope, remaining integration/fixes, implementation-owned self-checks, documentation consistency, durable RESULT and required recovery claim/stage closeout.

Do not move on to V5 from this worker.

Stop only at:

`COMPLETE — WINKAWAKS COLLECTOR V4 DATASET CATALOG / CAPTURE IDENTITY INDEX — REUSABLE SEARCHABLE DATASET MODULE COMPLETE`

or:

`BLOCKED — WINKAWAKS COLLECTOR V4 DATASET CATALOG / CAPTURE IDENTITY INDEX — <precise unavoidable blocker>`
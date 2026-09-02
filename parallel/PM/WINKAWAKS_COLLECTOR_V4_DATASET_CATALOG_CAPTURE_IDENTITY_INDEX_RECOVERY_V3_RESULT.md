# WinKawaks Collector V4 — Dataset Catalog / Capture Identity Index Recovery V3 RESULT

Status: **COMPLETE**

Date: 2026-09-02

Stage ID: `WINKAWAKS_COLLECTOR_V4_DATASET_CATALOG_CAPTURE_IDENTITY_INDEX_RECOVERY_V3`

Dedup key: `winkawaks.collector.v4.dataset-catalog-capture-identity-index.recovery-v3`

Claim token: `2d7f0e7b0b7e4df8922b0e24c1b9f18d`

Recovery V3 is the durable successor authority for the historical original V4 and Recovery V2 claims that remained `ACTIVE` after their workers stopped. Those historical claims are preserved as historical residue and are not rewritten or reused.

## Completion statement

**WINKAWAKS COLLECTOR V4 DATASET CATALOG / CAPTURE IDENTITY INDEX — REUSABLE SEARCHABLE DATASET MODULE COMPLETE**

Recovery V3 resumed from the already-landed V4 core and completed only the remaining catalog completeness, authority, consistency, implementation self-check, and closeout work. It did not reimplement the existing catalog core, BASECAP seed, schema foundation, CLI/documentation foundation, or Golden integration.

## Exact implementation authority

Repository: `ouyong520/wof-winkawaks-bridge`

Final implementation commit: `c48cdd03b0136247d794078d879a868d10e1f49c`

Final implementation tree: `6fac3df12311f92a2ca2aa8e51522e62faa0ed06`

Recovery V3 changed only the V4 catalog-owned implementation surface:

| Path | Exact blob SHA |
| --- | --- |
| `bridge/dataset_catalog.py` | `a6f26e0624840f4b040ff4bb48af6b74a8020bfd` |
| `tests/test_dataset_catalog.py` | `3e66b905400ef9944df9609ef47fb0978cdda22f` |
| `schemas/collector_dataset_catalog_v1.schema.json` | `1363d80fb6c3f042217ebd1f80ea0311e40121e2` |
| `docs/COLLECTOR_V4_DATASET_CATALOG.md` | `565abad270e48de8e7dbe36d9ae0c602c403fdf3` |

Relevant preserved authority/integration blobs at the exact final bridge commit:

| Path | Exact blob SHA | Role |
| --- | --- | --- |
| `catalog/basecap_authority_v1.json` | `17116d02589a4124e743814a780d0c0bab08e238` | BASECAP semantic/lifecycle authority seed |
| `.github/workflows/collector-python-smoke.yml` | `be3a0a5ba168e5a4aa66279625d2e65a494b6f07` | existing Golden integration |
| `bridge/collector_segmented_authority.py` | `4814b6471ec1d597b304a3b68680518c375cc558` | preserved V3 terminal-result authority |
| `bridge/collector_segmented_session.py` | `2370791a686de75d3b7e5eca00555266a90635fc` | preserved V3 local manifest/file validator |

Pinned BASECAP semantic source in `ouyong520/wof-ai-private`:

- `parallel/BASECAP/BASE_CAPTURE_CATALOG.md`
- exact blob SHA: `c9fb2a729798a684b1c3b740769f99977a45d5af`
- status in source: `BASECAP v1 COMPLETE`

## Completed capture identity contract

Catalog version remains `wof_collector_dataset_catalog_v1` and capture identity version remains `wof_collector_capture_identity_v1`.

The deterministic dataset identity is still:

```text
wkds-v1-<sha256(canonical-json(identity))>
```

Recovery V3 completed the authority tuple so identity explicitly binds:

- `sourceNamespace`;
- `captureMode`;
- `sourceTaskId`;
- immutable task identity via `taskBlobSha`, or canonical task-content SHA-256 only for older evidence without a blob binding;
- `captureId` / `sessionId` / `sourceIdentitySha256` when provided by the capture format;
- one or more immutable content SHA-256 bindings;
- V3 stable manifest binding plus ordered segment content hashes.

Paths, filenames, timestamps, labels, and task IDs alone are not sufficient capture identity. A path-only snapshot/result continues to fail closed.

## Source namespace authority

The catalog schema recognizes the project source namespaces:

```text
browser-wasm
winkawaks
stable-retro-fbneo
```

The WinKawaks Collector importer accepts only `winkawaks` evidence. An input that explicitly claims another namespace or an unknown namespace fails closed instead of being reinterpreted. No Browser/WASM or Training Farm evidence is promoted into WinKawaks authority, and no offset/runtime authority is transferred across sources.

## Duplicate and conflict authority

Recovery V3 completed fail-closed consistency rules:

- same exact immutable identity + byte-equivalent record -> `NOOP`;
- same `datasetId` with different record facts -> `CatalogConflict`;
- one `(sourceNamespace, sourceTaskId)` may resolve to only one immutable dataset identity;
- reusing the same task ID with a different task blob, capture/session authority, manifest authority, or content binding -> `CatalogConflict`;
- the same explicit source/artifact path cannot silently acquire two different hashes;
- another writer holding `<catalog>.lock` -> `CatalogConflict`;
- conflicts are never resolved by last-writer-wins.

Whole-catalog validation enforces the same invariants, so malformed pre-existing catalogs cannot bypass insertion-time checks.

## Mechanical integrity is separate from semantic lifecycle

Mechanical integrity states are:

```text
VERIFIED
PARTIAL
FAILED
UNKNOWN
```

Semantic/reuse lifecycle states are:

```text
VALID
INVALID
SUPERSEDED
UNREVIEWED
```

A mechanically healthy Collector `PASS` or `COMPLETE` no longer automatically becomes semantic `VALID`. Without explicit repository/upstream semantic authority, the capture remains `UNREVIEWED`.

For retained legacy/burst/snapshot evidence:

- mechanical `PASS` / `COMPLETE` -> integrity `VERIFIED`;
- partial/incomplete execution -> integrity `PARTIAL`;
- explicit failure -> integrity `FAILED`;
- unknown historical terminal form -> integrity `UNKNOWN`;
- semantic lifecycle remains `UNREVIEWED` unless an explicit authority classifies it.

BASECAP may classify a mechanically healthy capture as `VALID`, `INVALID`, or `SUPERSEDED`, while leaving the mechanical integrity result unchanged. `SUPERSEDED` records retain a reason and an optional successor task link. Historical invalid/superseded evidence is retained and remains queryable.

Default query returns only `VALID` datasets. `UNREVIEWED`, `INVALID`, and `SUPERSEDED` require an explicit lifecycle query or `--include-inactive`.

## BASECAP authority preservation

`catalog/basecap_authority_v1.json` remains an annotation/semantic authority seed, not a source of invented raw identity.

A BASECAP entry is applied only after matching retained task/result/manifest evidence supplies immutable capture identity. Scene labels, operator actions, action windows, changed variables, held-stable variables, research context, and confounders remain repository/operator authority and are never guessed from raw bytes.

The existing B10/B11 RAWMINE reuse therefore remains one immutable dataset identity with multiple authoritative labels; V4 does not fabricate two captures or invent a precise frame boundary.

## V3 segmented COMPLETE authority

Recovery V3 added a strict structural gate before a V3 `terminalState=COMPLETE` manifest can be cataloged as complete evidence. COMPLETE now fails closed on any of the following:

- V3 manifest schema mismatch;
- missing task/taskBlob/capture/session/source-runtime identity;
- expected segment-count mismatch;
- non-integer, duplicated, reordered, or non-contiguous segment indexes;
- segment task/taskBlob/capture/session/source-runtime binding mismatch;
- any non-COMPLETE segment;
- missing/invalid immutable segment SHA-256 or positive byte count;
- broken global frame-range continuity or aggregate frame count;
- incomplete gzip path/hash/size metadata when `github-gzip` retention is requested;
- duplicate remote paths under requested remote retention;
- runtime identity discontinuity;
- malformed or nonzero read/frame-size errors for COMPLETE;
- manifest/segment read-only, no-memory-write, no-input-injection, no-AI/no-future-danger safety invariant failure;
- invalid COMPLETE terminal shape.

V3 deterministic identity binds a stable manifest projection plus ordered per-segment hashes. Volatile bookkeeping such as `updatedAtUtc` does not change the dataset ID, while the full canonical manifest SHA-256 remains recorded in integrity metadata.

When the retained local manifest/raw files are available, V4 delegates exact local file/hash validation to the preserved V3 `validate_session_manifest()` authority. A COMPLETE manifest that fails exact local validation is rejected. A structurally valid repository COMPLETE manifest whose local retained raw is not available on the indexing machine remains mechanical integrity `UNKNOWN`, rather than being falsely upgraded to `VERIFIED`.

A V3 remote result also has to agree with the embedded manifest on task/taskBlob/capture/session/source-runtime identity before catalog import.

## Experiment / trial grouping and retained metadata

When explicitly present in task/result/manifest metadata, V4 preserves:

```text
experimentId
trialId
repeatGroupId
trialOrdinal
expectedDiscriminator
```

Grouping is never synthesized from filenames or raw values. Timing/sampling, action/schema version, artifact references/hashes, retention mode, operator scene metadata, and provenance remain queryable without changing capture identity.

## CLI / query / rebuild contract

The completed V4 CLI provides:

```text
index
rebuild
query
show
verify
```

`index` remains idempotent incremental discovery/upsert. `rebuild` deterministically reconstructs a catalog from currently discoverable authority. `show` resolves one exact immutable dataset ID, including inactive history. `verify` validates the catalog and the runtime/schema contract.

Query filters now cover:

- dataset ID;
- source namespace;
- source task ID;
- capture mode;
- action;
- scene label;
- lifecycle;
- integrity state;
- experiment/trial/repeat group;
- artifact/content SHA-256;
- retention mode;
- captured-after / captured-before ISO-8601 time;
- tag and text search.

Catalog writes remain serialized by a lock, validated as a whole, fsynced, and atomically replaced. Rebuild output is byte-stable for the same evidence/provenance inputs.

## Implementation self-check authority

Local final-candidate implementation self-check completed before publication:

- `python -m py_compile bridge/dataset_catalog.py` -> PASS;
- `python -m unittest -v tests/test_dataset_catalog.py` -> **20/20 PASS**;
- schema JSON parse -> PASS;
- CLI root/query help parse -> PASS.

The exact published bridge commit then passed the existing GitHub Actions Golden workflow:

- workflow: `Collector Python smoke check`;
- workflow run ID: `33626256840`;
- exact workflow head SHA: `c48cdd03b0136247d794078d879a868d10e1f49c`;
- conclusion: **success**.

Exact workflow evidence:

- preserved Collector V3 segmented implementation regressions: **15/15 PASS**;
- V4 dataset catalog implementation regressions: **20/20 PASS**;
- real current-repository retained evidence: `recordsDiscovered=33`, `inserted=33`, `noop=0`, `skipped=[]`;
- catalog verify: `valid=true`, `recordCount=33`, `schemaContractChecked=true`;
- default reusable dataset query: `active=8`;
- canonical retained BASECAP B00 and B13 resolve as lifecycle `VALID`;
- preserved V3 source-authority wiring check: PASS.

No Fresh QA or second-opinion QA was created; this is the implementation-owned self-check required by the stage.

## Runtime / project isolation

Recovery V3 did not modify:

- `product/alpha/**`;
- Alpha V1 runtime, danger, target, projection, Transport, Recorder, PYLAUNCH, or OneClick authority;
- `training/farm/**`;
- Stable-Retro / FBNeo adapters;
- training policy or action injection;
- 10-worker scheduling/execution;
- WinKawaks capture execution semantics;
- V3 segmented runtime/session completion authority.

Collector boundaries remain read-only and non-playing:

```text
readOnly=true
writesGameMemory=false
inputInjection=false
containsAiDecisionLogic=false
```

V4 indexes retained evidence; it does not execute game actions and it does not promote local evidence into Browser production authority.

## Intentional limitations

- The durable authority is the implementation/schema/docs/tests/seed plus deterministic rebuild/index behavior; the generated `catalog/dataset_catalog_v1.json` is not required to be checked in.
- Non-BASECAP captures remain `UNREVIEWED` until an explicit semantic authority classifies them.
- A structurally valid V3 COMPLETE manifest without locally available retained raw is not falsely called mechanically verified; its integrity remains `UNKNOWN` until exact local evidence can be validated.
- The schema reserves all project source namespaces, but this Collector importer intentionally accepts only WinKawaks evidence.

## Closeout

Recovery V3 has completed the remaining V4 completeness, authority, consistency, query/rebuild, schema-contract, and Golden implementation self-check requirements against exact current bridge HEAD. No unresolved implementation blocker remains inside the authorized scope.

Final verdict: **COMPLETE**.

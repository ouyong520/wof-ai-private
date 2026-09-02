# WinKawaks Collector V4 — Dataset Catalog / Capture Identity Index

stageId: `WINKAWAKS_COLLECTOR_V4_DATASET_CATALOG_CAPTURE_IDENTITY_INDEX_V1`
dedupProtocol: `v2`
dedupKey: `winkawaks.collector.v4.dataset-catalog-capture-identity-index`
dedupMode: `exclusive`

Priority: **P1 reusable datasets / acquisition infrastructure**

## Read first

- `parallel/PM/COLLECTOR_WORKER_EXECUTION_POLICY.md`
- `parallel/PM/TESTING_CADENCE_POLICY.md`
- `parallel/PM/STAGE_DEDUP_GUARD.md`
- `COLLECTOR_ROUTING.md`
- `RUNTIME_DATA_SOURCE_BOUNDARIES.md`
- `parallel/BASECAP/BASE_CAPTURE_CATALOG.md`
- `parallel/PM/WINKAWAKS_COLLECTOR_V3_LONG_SESSION_SEGMENTED_CAPTURE_RECOVERY_V2_RESULT.md`
- current `ouyong520/wof-ai-private/main`
- current `ouyong520/wof-winkawaks-bridge/main`

V3 segmented capture is COMPLETE at bridge candidate `c180e303cb1caf10effde49edceec4ea70a26cc2`. This V4 task is the next independent Collector side-lane development module. It must not modify or block Alpha V1 or Training Farm / current 10-worker training.

This is implementation, not QA. Acquire canonical dedup v2 ownership before substantive work. If an equivalent current module is already complete, stop duplicate/already-complete rather than reimplementing it.

## Purpose

Turn retained Collector captures into a reusable, searchable, integrity-bound dataset inventory so research threads can answer:

`Do we already have the right capture?`

before asking the Owner to collect again.

The module must support both:

- legacy Collector v1/v2 snapshot/burst datasets;
- V3 long-session segmented datasets/manifests.

The catalog is an indexing/provenance layer. It must not invent gameplay semantics from raw RAM.

## Primary implementation target

Prefer reusable Collector tooling in:

`ouyong520/wof-winkawaks-bridge`

PM authority/docs/results may be written under:

`ouyong520/wof-ai-private/parallel/PM/**`

Do not modify Alpha V1 runtime or Training Farm runtime.

## Required module capabilities

### 1. Versioned dataset catalog schema

Define a stable machine-readable schema for one reusable capture/dataset record.

At minimum retain:

- immutable dataset/capture identity;
- source namespace;
- taskId;
- taskBlobSha;
- action/schema version;
- captureId/sessionId when present;
- source/runtime identity and identity hash when present;
- capture timestamp/range;
- duration, requested/achieved Hz;
- bytes per frame / frame count / total bytes;
- raw artifact path(s);
- raw SHA-256 and gzip SHA-256 where available;
- V3 manifest identity and ordered segment identities/hashes where applicable;
- raw retention mode;
- integrity status;
- catalog lifecycle status;
- scene metadata / operator-provided metadata;
- provenance/evidence references;
- experiment/repeated-trial grouping fields;
- created/indexed timestamps and schema version.

### 2. Immutable capture identity

Create a deterministic capture/dataset identity derived only from authoritative provenance/integrity fields.

It must distinguish at least:

- `browser-wasm`;
- `winkawaks`;
- `stable-retro-fbneo`.

For this module, WinKawaks Collector records are the primary supported source. Never silently reinterpret another source as WinKawaks.

Same taskId with a different taskBlobSha, capture/session binding or artifact identity is a conflict and must fail closed, not merge.

A V3 segmented dataset identity must bind the authoritative session manifest and ordered segment identities/hashes. It must not be derived only from a mutable display label or filename.

### 3. Integrity state vs semantic/catalog state

Keep mechanical integrity separate from human/research classification.

Recommended separation:

- integrity: `VERIFIED / PARTIAL / FAILED / UNKNOWN`;
- catalog lifecycle: `VALID / INVALID / SUPERSEDED / UNREVIEWED`.

Do not automatically promote a mechanically healthy capture to semantically VALID merely because hashes pass.

`VALID`, descriptive scene labels and controlled-variable claims must come from authoritative metadata/operator/repository evidence, not inference from raw bytes.

### 4. BASECAP ingestion / reuse

Consume `parallel/BASECAP/BASE_CAPTURE_CATALOG.md` as existing repository authority for known reusable labeled WinKawaks captures.

Do not rewrite its labels from raw guesses.

Provide a deterministic way to seed/import or reference those existing records into the new machine-readable catalog/index while preserving:

- original task identity;
- retained raw path;
- status;
- scene/operator description;
- confounders/limitations;
- source evidence/provenance.

Do not require Owner recapture of existing BASECAP scenes merely to populate the index.

### 5. Legacy + V3 discovery

Support indexing of authoritative Collector artifacts already present in repository/local artifact layouts where repository facts permit it.

Legacy single-capture records and V3 segmented session records must share one searchable catalog surface without pretending they have identical artifact shapes.

For V3:

- verify manifest schema;
- retain ordered segment list;
- retain segment hashes;
- retain capture/session/source identity;
- do not index COMPLETE when local/repository evidence fails the V3 authority contract.

For legacy:

- retain exact task/result/raw identities available under the frozen contract;
- do not fabricate fields that did not exist historically.

### 6. Deterministic index build/update

Implement a deterministic catalog build/update path, preferably a small CLI/module, for example conceptual operations:

- `build` / `rebuild`;
- `verify`;
- `query`;
- `show`.

Exact command names may follow repository conventions.

Requirements:

- deterministic ordering/output;
- strict schema validation;
- atomic write/replace;
- duplicate identity detection;
- conflict detection;
- no silent destructive overwrite;
- clear diagnostics for invalid/incomplete records;
- rerunning on unchanged inputs is idempotent.

### 7. Search/query surface

Provide practical machine-readable and human-readable query support for fields such as:

- dataset/capture identity;
- taskId;
- source namespace;
- action/capture type;
- sceneLabel;
- player occupancy/configuration;
- operator action;
- changed variable;
- held-stable variables;
- research question;
- status;
- capture time/range;
- experiment group;
- repeated-trial group;
- raw/manifest/segment SHA;
- retention/local/remote availability.

The purpose is to let future PM/research workers search before requesting new capture.

### 8. Experiment / repeated-trial grouping

Support optional explicit grouping fields for future controlled acquisition, such as:

- `experimentId`;
- `trialId`;
- `repeatGroupId`;
- `trialOrdinal`;
- expected discriminator if explicitly supplied.

These are descriptive/research metadata only and must not become production gameplay authority.

### 9. Supersession/history

A dataset record must not silently disappear when replaced.

Support explicit lifecycle tracking such that an old record can remain discoverable as `SUPERSEDED` with a link/reason to the newer canonical record.

`INVALID` and `SUPERSEDED` are different states.

Do not reuse a historical dataset identity for new bytes.

### 10. No semantic guessing

Hard rule:

- raw bytes may support integrity and exploratory analysis;
- the catalog must never infer missing sceneLabel/operator action/changed variable/player configuration and store the guess as authoritative metadata;
- unknown fields remain unknown/unreviewed.

This module indexes evidence; it does not promote offset guesses, enemy semantics or gameplay rules.

### 11. Side-lane and source isolation

Hard boundaries:

- no `product/alpha/**` changes;
- no Alpha release/proof changes;
- no Transport/Recorder/PYLAUNCH/OneClick changes;
- no Training Farm policy/runtime changes;
- no gameplay input injection;
- no game-memory writes;
- no ROM/BIOS/game asset commits;
- `readOnly=true`, `writesGameMemory=false`, `inputInjection=false` remain Collector invariants;
- Browser / WinKawaks / Training Farm provenance remain distinct.

Collector V4 incomplete or blocked is not an Alpha V1 or Training Farm/10-worker blocker.

## Implementation-owned self-checks

Finish the whole module first. Use only implementation-owned checks needed to keep the candidate coherent, including as appropriate:

- compile/parse;
- catalog schema validation;
- deterministic identity generation;
- idempotent rebuild;
- duplicate/conflict fail-closed;
- same taskId + different taskBlobSha conflict;
- V3 ordered-segment/hash identity binding;
- legacy record compatibility;
- BASECAP import/reference preserving manual labels;
- VALID not auto-derived from mechanical integrity;
- INVALID vs SUPERSEDED behavior;
- source namespace isolation;
- query/filter behavior;
- atomic output/update behavior.

Do not open Fresh QA, cross-check, second opinion, QA V2/V3/V4, readiness audit or real WinKawaks capture from this task.

If concrete defects are found during self-check, fix them within this module and rerun only affected/self-check coverage.

## Durable completion

Before COMPLETE, write a concise durable RESULT under `parallel/PM/**` recording:

- exact final implementation candidate HEAD;
- exact changed files/blobs;
- catalog/index schema;
- identity derivation contract;
- V1/V2 vs V3 handling;
- BASECAP ingestion/reuse behavior;
- integrity vs semantic lifecycle states;
- query surface;
- experiment/repeat grouping;
- conflict/supersession rules;
- self-check commands/results;
- any remaining local-only limitation.

Close claim/stage under canonical dedup v2.

## Stop

Do not stop at an intermediate milestone. Keep implementation reporting sparse. Continue through the complete assigned functional/module scope, integration, implementation-owned self-checks, documentation, durable RESULT and required claim/stage closeout.

Stop only at:

`COMPLETE — WINKAWAKS COLLECTOR V4 DATASET CATALOG / CAPTURE IDENTITY INDEX — REUSABLE SEARCHABLE DATASET MODULE COMPLETE`

or:

`BLOCKED — WINKAWAKS COLLECTOR V4 DATASET CATALOG / CAPTURE IDENTITY INDEX — <precise unavoidable blocker>`

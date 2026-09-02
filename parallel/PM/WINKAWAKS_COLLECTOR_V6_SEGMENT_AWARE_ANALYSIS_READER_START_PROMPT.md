# WinKawaks Collector V6 — Segment-Aware Analysis Reader / Raw Research Toolkit

stageId: `WINKAWAKS_COLLECTOR_V6_SEGMENT_AWARE_ANALYSIS_READER_V1`
dedupProtocol: `v2`
dedupKey: `winkawaks.collector.v6.segment-aware-analysis-reader`
dedupMode: `exclusive`

Priority: **P2 segment-aware analysis tooling / reusable raw research**

## Duplicate-forward preflight — mandatory before implementation

Read and obey `parallel/PM/COLLECTOR_WORKER_EXECUTION_POLICY.md`, especially the duplicate forwarded-post guard.

Treat this post as potentially duplicated until current authority is checked. Before substantive implementation verify:

- current `ouyong520/wof-ai-private/main`;
- current `ouyong520/wof-winkawaks-bridge/main`;
- this exact START_PROMPT;
- canonical/stage claims for this exact V6 generation;
- any RESULT for the same/equivalent objective;
- any newer recovery/successor authority.

If this same/equivalent V6 task is already legitimately ACTIVE under another current generation, already COMPLETE, or superseded by a newer active/completed successor, **do not execute duplicate work**. Do not create another claim, do not edit code, and do not rerun old self-checks merely for activity. Stop with:

`DUPLICATE / ALREADY COMPLETE / SUPERSEDED — NO EXECUTION — <current authority>`

If it is not duplicate, acquire canonical dedup v2 claim/stage ownership before substantive implementation.

## Read first

- `parallel/PM/COLLECTOR_WORKER_EXECUTION_POLICY.md`
- `parallel/PM/TESTING_CADENCE_POLICY.md`
- `parallel/PM/STAGE_DEDUP_GUARD.md`
- `COLLECTOR_ROUTING.md`
- `RUNTIME_DATA_SOURCE_BOUNDARIES.md`
- `parallel/BASECAP/BASE_CAPTURE_CATALOG.md`
- `parallel/PM/WINKAWAKS_COLLECTOR_V3_LONG_SESSION_SEGMENTED_CAPTURE_RECOVERY_V2_RESULT.md`
- `parallel/PM/WINKAWAKS_COLLECTOR_V4_DATASET_CATALOG_CAPTURE_IDENTITY_INDEX_RECOVERY_V3_RESULT.md`
- `parallel/PM/WINKAWAKS_COLLECTOR_V5_LONG_RUN_STORAGE_RETENTION_MANAGER_RECOVERY_V2_RESULT.md`
- current V3/V4/V5 contracts and implementation in `ouyong520/wof-winkawaks-bridge`

Current Collector authority at task creation:

- V3 segmented long-session capture: COMPLETE;
- V4 dataset catalog / immutable capture identity: COMPLETE;
- V5 long-run storage / retention / archive / pressure guard: COMPLETE;
- exact V5 Recovery V2 tested bridge authority: `bfe8b95591f5f803d298f7cbe87a417b65e74326`.

This is a new **analysis/read tooling** module, not capture implementation and not independent QA.

## Purpose

Make retained Collector data directly reusable for research without manually concatenating raw files or writing one-off scripts for every experiment.

The V6 tool must provide a strict, segment-aware, source-bound reader plus deterministic research-only analysis operations over existing Collector evidence.

Operating principle:

`select authoritative dataset(s) -> verify/read immutable evidence -> expose one logical frame stream -> compute deterministic research summaries/candidates -> retain exact provenance -> never promote guesses into gameplay authority`

V6 must consume and respect V3/V4/V5 authority; it must not replace them.

## Primary implementation target

Prefer reusable tooling under:

`ouyong520/wof-winkawaks-bridge`

PM claim/result authority may be written only under:

`ouyong520/wof-ai-private/parallel/PM/**`

Do not modify Alpha V1 runtime or Training Farm runtime/policy.

## Required module capabilities

### 1. Versioned analysis/read contract

Define one versioned machine-readable analysis/read contract and result schema.

At minimum results must bind:

- analysis schema/tool version;
- operation kind;
- exact input datasetId(s) when V4 identity exists;
- source namespace;
- taskId/taskBlobSha where available;
- captureId/sessionId where available;
- source/runtime identity hash where available;
- V3 manifest identity and ordered segment hashes where applicable;
- exact input artifact hashes used;
- frame/time range actually analyzed;
- analysis parameters;
- deterministic analysis/result identity/hash;
- completeness/integrity disposition of each input;
- `researchOnly=true`;
- timestamp/build/tool provenance.

Analysis output identity must depend on immutable source identity + canonical analysis parameters, not display labels or filenames.

### 2. Strict source namespace isolation

Primary supported source is WinKawaks Collector evidence.

Never silently reinterpret:

- `browser-wasm`;
- `stable-retro-fbneo`;
- unknown source material

as WinKawaks.

Cross-source comparison may only exist if the future contract explicitly labels each source independently; do not implement cross-runtime offset inheritance or semantic equivalence in this V6 module.

### 3. V4 dataset selection / resolution

Support selecting evidence by immutable V4 dataset ID and practical catalog query where current repository conventions permit.

Requirements:

- resolve exact dataset identity, not filename heuristics;
- preserve V4 lifecycle/integrity separation;
- default analysis should prefer/currently permit reusable `VALID` datasets;
- `UNREVIEWED`, `INVALID`, `SUPERSEDED`, `PARTIAL`, or `FAILED` evidence must require explicit opt-in when analysis is permitted at all;
- never upgrade V4 lifecycle or V3 terminal authority;
- if V5 says source was pruned after verified archive, allow read resolution from the verified archive copy when current V5 authority can prove it, without changing dataset identity;
- conflicting/missing archive receipts or hashes fail closed.

V6 is read-only: it must not rewrite catalog, lifecycle, storage receipts or retention policy.

### 4. Segment-aware logical frame stream

Expose one ordered logical frame stream for a V3 segmented dataset without requiring destructive/identity-changing concatenation.

For V3 COMPLETE evidence:

- validate V3 manifest authority before claiming a complete logical stream;
- preserve exact ordered segment sequence;
- validate segment/task/blob/capture/session/source binding;
- validate local/archived artifact size/hash where available and required by existing authority;
- verify frame sequence continuity across segment boundaries;
- preserve segment index and original local/global frame identity;
- expose timestamps and sampling metadata honestly;
- fail closed on missing/duplicate/reordered/corrupt segment evidence.

For V3 PARTIAL/FAILED evidence:

- never masquerade as COMPLETE;
- analysis requires an explicit partial-evidence option;
- analyze only finalized authoritative segments/ranges;
- output must carry the exact partial/failed disposition and missing-range limitations.

Do not manufacture frames or interpolate gaps.

### 5. Legacy snapshot/burst reader compatibility

Support legacy Collector snapshot/burst raw evidence where repository facts permit.

Requirements:

- preserve exact historical task/result/raw authority available;
- do not fabricate V3-only fields;
- respect bytes-per-frame/layout metadata from authoritative evidence rather than assuming future layouts are identical;
- gzip/raw handling must verify retained hash/size facts when available;
- malformed/truncated frame records fail closed or are explicitly reported as incomplete evidence, never silently skipped as healthy.

### 6. Streaming / bounded-memory operation

Long V3 sessions may be very large. V6 must be usable on hour-scale retained captures without requiring the entire raw stream in RAM.

Provide streaming/iterator/chunked processing where appropriate.

Requirements:

- bounded memory by configurable safe chunk/window size;
- deterministic results independent of chunk boundaries;
- cross-segment/window state must be explicit and tested;
- cancellation/error must not produce a result marked complete;
- no temporary derived file should become authoritative merely because a process crashed after writing it.

### 7. Field/byte delta summaries

Provide deterministic raw-first delta analysis over selected byte/field ranges.

At minimum support useful summaries such as:

- per-offset change count/frequency;
- first/last observed change frame/time;
- distinct-value count within bounded limits;
- unchanged/stable ratio;
- simple signed/unsigned raw transition summaries only when width/interpretation is explicitly specified by the caller;
- range/window filters.

Do not label an offset as player X/Y, enemy type, attack ID, danger, target, etc. unless that semantic mapping is independently supplied as descriptive research metadata. Raw statistics are not semantic authority.

### 8. Cross-capture / controlled-scene diff

Support comparing two or more V4 datasets or explicit frame windows to find raw fields whose behavior differs between controlled captures.

At minimum support deterministic comparison facts such as:

- change-frequency difference;
- distinct-value-set difference within bounded output;
- stable-in-A / varying-in-B and varying-in-A / stable-in-B;
- value-transition distribution difference;
- optional aligned window comparison when the caller supplies explicit comparable ranges.

Do not invent temporal alignment from scene labels or filenames. If captures lack an authoritative common event marker, report that limitation rather than pretending frame N corresponds semantically across captures.

### 9. Transition / temporal precursor mining

Provide a conservative, generic research operation for transitions around caller-specified raw predicates/events.

Examples of allowed caller-specified research predicates:

- exact byte/word offset changes;
- value enters/leaves a caller-provided set;
- explicit frame marker/window supplied by external metadata.

The tool may report candidate offsets/changes that statistically precede/follow the specified event within a bounded window.

Requirements:

- deterministic window definitions;
- counts/support shown explicitly;
- no causal claim;
- no promotion to production danger/target authority;
- output wording/fields should use terms such as `candidate`, `association`, `support`, `leadFrames`, not `confirmed danger precursor`.

### 10. Candidate offset ranking

Provide deterministic ranking suitable for research triage.

Ranking may combine clearly documented raw metrics such as:

- controlled-change selectivity;
- stability in held-stable captures;
- transition support;
- repeated-trial consistency;
- noise/change-rate penalty.

Requirements:

- formula/version/parameters recorded in output;
- all component metrics exposed;
- ties deterministically ordered;
- no opaque ML model required for V6;
- rank is research priority only, never semantic authority.

### 11. Repeated-trial / experiment grouping

Reuse V4 explicit `experimentId`, `trialId`, `repeatGroupId`, `trialOrdinal`, and related metadata when present.

Support aggregating repeated trials without synthesizing group membership from filenames.

At minimum report:

- trials included/excluded;
- source dataset IDs;
- per-trial support;
- aggregate support/consistency;
- missing or incomparable trial reasons.

No group metadata -> no invented group.

### 12. Structured scene metadata preservation

Expose V3/V4 operator-provided metadata to the researcher, including where present:

- sceneLabel;
- playerConfig;
- operatorAction;
- changedVariable;
- heldStableVariables;
- researchQuestion;
- confounders;
- notes.

This metadata is descriptive provenance. V6 may filter/group by it but must never reinterpret raw bytes to backfill missing labels.

### 13. Deterministic CLI

Provide a practical CLI/module following repository conventions. Conceptual operations may include:

- `inspect` / `show`;
- `frames` or `stream-info`;
- `delta`;
- `compare`;
- `transitions`;
- `rank`;
- `verify`.

Exact names may follow repository conventions.

Requirements:

- structured JSON output suitable for future automation;
- concise human-readable output where useful;
- deterministic ordering;
- explicit dataset/range parameters;
- bounded result limits to avoid accidental giant output;
- stable exit codes/reasons;
- no mutating operation against capture/catalog/archive authority.

### 14. Derived analysis artifact safety

If V6 writes optional analysis result files:

- use a separate derived-analysis namespace/path;
- never place them where V3/V4/V5 could mistake them for raw capture authority;
- bind exact source dataset IDs/hashes and analysis parameters;
- use temporary + atomic finalize for completed result files;
- incomplete/cancelled analysis must not be marked COMPLETE;
- derived files are disposable/recomputable research artifacts, not the sole authority for source evidence.

### 15. Integrity/conflict behavior

Fail closed or explicitly downgrade analysis completeness on:

- dataset ID conflict;
- source namespace mismatch;
- missing required V3 segment;
- raw/segment/archive hash mismatch;
- manifest/task/capture/session binding mismatch;
- frame record truncation;
- impossible frame sequence/order;
- V5 receipt mismatch when reading archived-only evidence;
- unknown ownership;
- malformed analysis parameters;
- non-finite/coercible numeric parameters where strict numbers are required.

Do not silently skip corrupt evidence and still call the full analysis complete.

### 16. Side-lane isolation

Hard boundaries:

- no `product/alpha/**` changes;
- no Alpha release/proof/runtime changes;
- no danger-rule or target-semantic changes;
- no Transport/Recorder/PYLAUNCH/OneClick changes;
- no Training Farm runtime, PPO/RL, savestate, action injection or 10-worker scheduling changes;
- no WinKawaks gameplay input injection;
- no game-memory writes;
- no ROM/BIOS/game asset commits.

Collector remains:

```text
readOnly=true
writesGameMemory=false
inputInjection=false
```

V6 is offline/read-side research tooling. It is not an AI policy and does not act on the game.

## Implementation-owned self-checks

Finish the coherent module first, then run only necessary implementation-owned checks.

Cover at least:

- strict analysis schema/parameter validation;
- duplicate/current-authority preflight behavior at claim level;
- V3 COMPLETE multi-segment logical stream continuity;
- missing/duplicate/reordered/corrupt segment rejection;
- explicit partial-evidence analysis without COMPLETE masquerade;
- legacy raw/burst compatibility;
- gzip/raw hash verification where available;
- V5 archived-only verified read path if repository architecture supports it;
- archive receipt/hash mismatch fail-closed;
- bounded-memory/chunk-boundary deterministic equivalence;
- field delta correctness on deterministic fixture;
- cross-capture diff correctness;
- transition window boundary cases;
- candidate ranking deterministic ties/formula;
- repeated-trial aggregation and missing-group behavior;
- no semantic-label inference;
- source namespace isolation;
- analysis result identity stability;
- no mutation of V3/V4/V5 authority;
- V3/V4/V5 regression compatibility needed to prove reader integration did not weaken them.

Do not create Fresh QA, second opinion, cross-check, QA V2/V3/V4/V5/V6, Browser/WOF testing, real WinKawaks capture, or Training Farm testing from this implementation task.

If implementation self-check finds a concrete defect, fix the related V6 defect cluster and rerun the affected checks. Do not multiply QA stages.

## Durable completion

Before COMPLETE, write a durable RESULT under `parallel/PM/**` recording at minimum:

- exact final bridge HEAD/tree;
- exact changed files/blobs;
- analysis/read schema and version;
- input/dataset authority contract;
- V3 logical segmented stream behavior;
- legacy reader behavior;
- V5 archived-read behavior if implemented;
- partial/incomplete evidence contract;
- streaming/bounded-memory design;
- delta/compare/transition/rank operations;
- repeated-trial behavior;
- analysis result identity/provenance contract;
- research-only/no-semantic-promotion rules;
- CLI commands/output contract;
- implementation-owned self-check commands/results;
- any remaining runtime/data-format limitation.

Close canonical and stage claims correctly under canonical dedup v2.

## Stop

Do not stop at claim acquisition, repository inspection, one reader helper, one analysis operation, one test, or documentation-only progress.

Keep implementation reporting sparse. Continue through the complete assigned V6 reader/analysis module, integration, implementation-owned self-checks, documentation, durable RESULT and claim/stage closeout.

Do not move on to V7 batch acquisition automation from this worker.

Stop only at:

`COMPLETE — WINKAWAKS COLLECTOR V6 SEGMENT-AWARE ANALYSIS READER — REUSABLE RAW RESEARCH TOOLKIT COMPLETE`

or:

`BLOCKED — WINKAWAKS COLLECTOR V6 SEGMENT-AWARE ANALYSIS READER — <precise unavoidable blocker>`

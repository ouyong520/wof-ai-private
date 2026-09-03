# WOF Unified Collector V11 — Training Farm Adapter + Unified Task/Data Stack

stageId: `WOF_UNIFIED_COLLECTOR_V11_TRAINING_FARM_ADAPTER_UNIFIED_TASK_DATA_STACK_V1`
dedupProtocol: `v2`
dedupKey: `wof.unified-collector.v11.training-farm-adapter-unified-task-data-stack`
dedupMode: `exclusive`

Priority: **P0 architecture convergence / final one-collector program**

## Owner final direction

The Owner has explicitly required that all general WOF collection converge to exactly **one Collector product**:

```text
Git collection requirement / task
        |
        v
WOF Unified Collector Agent
        |
        +--> browser-wasm adapter
        +--> winkawaks adapter
        +--> stable-retro-fbneo / Training Farm adapter
        |
        v
one task/status/result plane
one source-aware dataset/provenance stack
one retention/storage layer
one analysis layer
one DuckDB warehouse/query layer
one reuse-first planning layer
```

There must not be a separately maintained Browser collector, WinKawaks collector, or generic Training Farm collector after the final V12 consolidation. Runtime-specific adapters/hooks are required, but they are modules feeding the same Collector control/data plane.

Final roadmap authority:

`parallel/PM/COLLECTOR_V9_TO_V12_FINAL_UNIFIED_COLLECTOR_ROADMAP.md`

V11 is the second real convergence stage. V10 already merged Browser/WASM + WinKawaks into one Agent. V11 must add Training Farm as the third source and generalize the V4–V9 data/research stack so all three namespaces share one generic source-aware layer without erasing runtime provenance.

---

## Exact starting authority — re-read before work

### Unified Collector V10 COMPLETE

Implementation repository:

`ouyong520/wof-winkawaks-bridge`

V10 final implementation HEAD:

`31ec55650ccce29fad60dcab2ca099425a1ecc0b`

V10 final tree:

`26e621944bc6adcf9a3530eb3e815fe125812fda`

V10 durable RESULT:

`parallel/PM/WOF_UNIFIED_COLLECTOR_V10_AGENT_FOUNDATION_BROWSER_WASM_MULTI_PAGE_ADAPTER_RESULT.md`

V10 RESULT commit:

`21fec94b7c132920500e6709d3c76db3fc49be5d`

Final V10 maintained CI:

- workflow: `Collector V10 Unified Agent Regression`
- run: `33710701482`
- job: `100509341864`
- V3–V9 maintained regression: `151/151 PASS`
- V10 fake-CDP + Unified Agent regression: `36/36 PASS`
- combined: `187/187 PASS`
- schema/examples/source/safety/launcher gate: PASS

V10 canonical/stage claims are COMPLETE. Do not reopen or modify them.

V10 source namespaces are currently exactly:

```text
browser-wasm
winkawaks
```

V11 adds:

```text
stable-retro-fbneo
```

V10 normal Git control plane already exists and must remain the single normal plane:

```text
tasks/queue/<taskId>.json
status/by_task/<taskId>.json
results/by_task/<taskId>.json
```

Do not create `training_tasks/**`, `farm_results/**`, a second queue daemon, or a second normal launcher.

### Training Farm current authority

PM / Training Farm repository:

`ouyong520/wof-ai-private`

At V11 staging, current main was inspected as:

`e1296e971c4aca305ddcfe269ffab3b1021f4aa9`

This main contains concurrent Alpha work. V11 must re-read current main before every shared-file mutation and must not overwrite unrelated changes.

Training Farm current source namespace remains exactly:

`stable-retro-fbneo`

Existing `TrainingFarmAdapter` boundary includes:

```text
reset()
step(...)
step_frame(...)
read_ram()
read_ram_blocks()
save_state()
load_state(...)
runtime_identity_components()
```

Existing R0.4 deterministic fork authority already records source-specific facts such as:

- runtime identity and runtime identity SHA-256;
- ROM SHA-256 / fixture marker;
- Farm candidate/source identity;
- root savestate SHA-256;
- root RAM / RAM-block SHA-256;
- memory-layout identity;
- fork set / root / branch identities;
- action-sequence SHA-256;
- frame/checkpoint metadata;
- final RAM / RAM blocks / savestate hashes;
- deterministic replay outcome fingerprints.

Reuse these facts; do not invent replacement Training Farm identity semantics.

R0.4.7 closeout successor authority is COMPLETE at:

`parallel/TRAINING_FARM_R0_4_7_WINDOWS_PORTABLE_REAL_WOF_PROOF_BUNDLE_V1_CLOSEOUT_RECOVERY_V3/RESULT.md`

commit:

`7b175c576b8397e83b63160c055906e7c10c5af0`

That authority explicitly states real R0.2/R0.4 WOF proof is still required and R0.5 remains locked. V11 is a Collector/data integration stage and must not bypass that proof gate or authorize R0.5.

### Current Training Farm worker-budget truth

`training/farm/background_runtime.py` currently defines a configurable worker ceiling up to 10 and default policy values that conceptually budget for a future 10-worker fleet.

However its current R0.4.5 `StageGuard` is intentionally stricter:

```text
maxRealEmulatorWorkersThisStage = 1
realWorkerLaunchEnabled = false
realWofProofClaimed = false
r0_5Authorized = false
```

Therefore V11 may implement and fixture-test a protocol that addresses one worker, an explicit worker set, or up to 10 already-active workers, but **must not start 2/4/8/10 real emulator workers merely to prove the Collector**.

10-worker live acceptance remains future runtime evidence / V12 acceptance once Training Farm authority actually permits such a fleet.

---

## Mandatory duplicate-forward preflight

Before substantive work, re-read both current mains and check:

- this exact V11 START_PROMPT;
- the V9→V12 final roadmap;
- V10 durable RESULT and COMPLETE claims;
- any V11 canonical claim;
- any V11 stage claim;
- any V11 durable RESULT;
- any materially equivalent Training Farm / Stable-Retro Unified Collector adapter task/result;
- any newer V11 recovery/successor authority;
- current Training Farm implementation files and current source hashes;
- current V10 adapter/Agent/schema/data-stack source files.

If the same/materially equivalent V11 is already legitimately ACTIVE, COMPLETE or superseded, do not execute duplicate work:

`DUPLICATE / ALREADY COMPLETE / SUPERSEDED — NO EXECUTION — <current authority>`

Do not create a Recovery generation merely to bypass an existing legitimate claim.

If no equivalent current authority exists, acquire and verify a fresh V11 canonical dedup-v2 claim and matching stage claim before substantive implementation.

---

## Read and obey

- `parallel/PM/COLLECTOR_V9_TO_V12_FINAL_UNIFIED_COLLECTOR_ROADMAP.md`
- `parallel/PM/WOF_UNIFIED_COLLECTOR_V10_AGENT_FOUNDATION_BROWSER_WASM_MULTI_PAGE_ADAPTER_RESULT.md`
- `parallel/PM/COLLECTOR_WORKER_EXECUTION_POLICY.md`
- `parallel/PM/PROJECT_EXTERNAL_GITHUB_REUSE_POLICY.md`
- `parallel/PM/COLLECTOR_EXTERNAL_GITHUB_REUSE_POLICY.md`
- `parallel/PM/TESTING_CADENCE_POLICY.md`
- `parallel/PM/STAGE_DEDUP_GUARD.md`
- `COLLECTOR_ROUTING.md`
- `RUNTIME_DATA_SOURCE_BOUNDARIES.md`
- `training/farm/README.md`
- `training/farm/adapter.py`
- `training/farm/identity.py`
- current R0.4 fork contract/branch/runner modules
- `training/farm/background_runtime.py`
- current R0.4.7 durable authority above

Do not infer hidden semantics from file names alone. Re-read current code before binding an interface.

---

## External GitHub reuse preflight — mandatory but bounded

Do not restart broad tool research already decided in V7–V10.

Retain existing maintained decisions unless current facts prove otherwise:

- DuckDB `1.5.5` — `DIRECT_USE` for derived warehouse/query;
- APScheduler `3.11.3` — `DIRECT_USE` only where bounded local scheduling remains useful;
- `websocket-client==1.9.2` — existing V10 Browser CDP transport only;
- Playwright — `DEFER` unless a measured Browser requirement appears; V11 is not a Browser rewrite;
- Polars — `DEFER`;
- Prefect — `DEFER`;
- OR-Tools — `DEFER`.

For Training Farm attachment/export specifically, prefer the narrowest existing project-owned source hook plus Python stdlib/local filesystem contracts over adding a new message broker, server, database, RPC framework, Docker service, Redis, ZeroMQ, gRPC, Kafka, NATS or similar infrastructure.

Evaluate `psutil` only if process/resource discovery is genuinely needed. If explicit Training Farm worker-export registry/manifest identity already provides enough authority, keep `psutil` deferred rather than broadening the runtime surface.

Record the final V11 reuse decision in the durable RESULT.

---

# V11 primary implementation scope

## 1. Add `stable-retro-fbneo` as a third Unified Collector source adapter

In `ouyong520/wof-winkawaks-bridge`, extend the maintained V10 adapter interface with a source adapter for:

`stable-retro-fbneo`

The adapter must be an observation/export consumer, not a training controller.

It may collect only evidence already exposed by an existing Training Farm worker/export hook. It must not call or own gameplay policy decisions.

Required safety interpretation:

```text
Collector readOnly = true
Collector writesGameMemory = false
Collector inputInjection = false
```

Training Farm itself may have emulator-core action input as part of training. The Collector may record those actions/results as evidence, but the Collector must not select, inject, schedule or alter them.

Hard forbidden from V11 Collector code:

- calling `reset()` to create a collection scene;
- calling `step()` / `step_frame()` to drive gameplay for collection;
- calling `load_state()` to branch or rewind for collection;
- selecting PPO/RL/policy actions;
- changing search/branch strategy;
- starting Training Farm workers;
- changing Training Farm worker count;
- sending OS/global keyboard/mouse input;
- reclassifying emulator action permissions as Collector permissions.

## 2. Add a narrow Training Farm read-only export/observer contract

A running Training Farm process needs a source-specific way to expose evidence to the Unified Collector without giving the Collector training-control authority.

Implement the narrowest coherent source hook under `training/farm/**` in `ouyong520/wof-ai-private`.

Preferred architecture:

```text
Training Farm worker/runtime
  -> optional source-owned read-only exporter / observer
  -> local per-worker registry + immutable/bounded evidence artifacts
  -> Unified Collector stable-retro-fbneo adapter reads them
```

The export path must be local-machine only, explicit, bounded and independently identifiable.

Do not build another Git task consumer or another Collector service under `training/farm/**`.

The Training Farm side may publish source facts, but must not own:

- Git Collector queue consumption;
- Collector task terminal authority;
- generic dataset catalog;
- generic retention/archive;
- generic DuckDB warehouse;
- generic reuse planner.

Those belong to the Unified Collector stack.

### Exported worker identity

Every published worker record must preserve source-owned facts sufficient to distinguish workers and generations, including where available:

- `sourceNamespace=stable-retro-fbneo`;
- worker ID;
- worker generation / process generation if one exists;
- process ID as run-local metadata, not cross-process semantic identity;
- runtime/core/backend identity;
- ROM SHA-256 or fixture marker;
- Farm candidate/source identity;
- memory-layout identity;
- episode identity / episode generation where available;
- logical frame / step counter where available;
- active root/fork/branch identity where available;
- current action/result metadata already produced by Training Farm where available;
- exporter schema/version and exporter source identity;
- timestamps / monotonic sequence;
- completeness/health state.

Do not invent values that current Training Farm does not own. Missing optional facts must remain explicitly unavailable rather than guessed.

### Export atomicity / stale detection

Use atomic local updates and generation/sequence binding so the Collector can detect:

- worker restart;
- stale worker record;
- duplicate worker ID with conflicting generation;
- runtime identity change;
- memory-layout change;
- episode/root/branch change during a bounded capture;
- partial/incomplete stream artifacts;
- file replacement/race.

A capture must fail closed or become explicit PARTIAL/FAILED according to contract; it must never splice two worker generations into one PASS artifact.

## 3. Unified Training Farm target selectors — strict and bounded

Extend the versioned Unified Collector task envelope so `sourceNamespace=stable-retro-fbneo` supports strict selectors for at least:

```text
ONE
WORKER_IDS
ALL_ACTIVE
```

Suggested semantics:

- `ONE`: exactly one eligible active worker; ambiguity fails closed;
- `WORKER_IDS`: explicit unique 1..10 worker IDs;
- `ALL_ACTIVE`: explicit native-integer `maxWorkers` in `[1,10]`; if eligible workers exceed the requested bound, fail closed rather than silently truncating.

Do not coerce booleans/strings/floats into worker counts or IDs.

A task must never silently broaden from one worker to all workers.

## 4. Training Farm collection actions

Support a coherent bounded set that maps to evidence the Training Farm exporter can actually provide.

At minimum support, where the current exporter contract has authority:

- RAM / observation snapshot;
- bounded RAM / observation stream;
- worker/runtime identity snapshot;
- episode/trajectory metadata snapshot;
- existing action/result trajectory record ingestion;
- root/fork/branch/savestate identity metadata ingestion;
- runtime/resource/timing metadata snapshot.

Do not claim support for a data type that is not actually exported and validated.

Raw RAM offsets remain `stable-retro-fbneo` source-native facts only. Never copy Browser/WASM or WinKawaks numeric offsets into Training Farm tasks as semantic authority.

## 5. Preserve one Git task/hash/status/result authority

All three sources must continue to use one normal plane:

```text
tasks/queue/<taskId>.json
status/by_task/<taskId>.json
results/by_task/<taskId>.json
```

Every terminal result must remain bound to the exact task bytes / Git blob SHA according to the V10 Agent authority.

Generalize the strict Unified schema/version as needed. If a schema version must advance, do so explicitly and preserve a strict compatibility path for V10 v1 Browser/WinKawaks tasks rather than silently changing v1 meaning.

Recommended direction:

```text
wof_unified_collector_task_v2
wof_unified_collector_status_v2
wof_unified_collector_result_v2
```

if adding the third namespace cannot be represented without changing the closed V10 v1 allowlist/shape. Do not mutate the meaning of an immutable version string.

The Agent may accept both strict V10 v1 and V11 v2 if needed, but terminal authority must remain one system.

## 6. Generalize immutable dataset/provenance catalog from V4 concepts

V11 must establish one source-aware generic dataset catalog for all three namespaces.

Preserve the strong V4 principles:

- immutable content identity;
- content/provenance hash separation where appropriate;
- exact producer task/result binding;
- completeness/integrity separate from semantic authority;
- conflict detection;
- no mutable label becoming evidence authority.

Every unified dataset must preserve at minimum:

- `sourceNamespace`;
- adapter/exporter version;
- taskId + task blob SHA;
- result identity;
- runtime/session/worker provenance appropriate to that source;
- capture/segment/trajectory identities;
- frame/time bounds;
- artifact SHA-256 and bytes;
- acquisition metadata;
- completeness / partial state;
- migration/registration provenance when historical evidence is registered.

Do not rewrite historical WinKawaks/Browser/Training Farm artifacts to pretend they were originally produced by the V11 schema.

Historical registration must preserve original path/schema/hash/source and add explicit V11 registration provenance.

## 7. Generalize V5 retention/archive/pressure safety

Reuse the existing V5 storage/retention manager rather than creating source-specific cleanup stacks.

V11 must make retention decisions source-aware while preserving:

- local-first raw data by default;
- archive verification;
- partial/in-progress protection;
- two-phase prune/delete safety;
- disk pressure guard;
- explicit health state;
- no deletion of current/incomplete authority.

A source namespace is metadata for policy/query; it must not weaken integrity checks.

## 8. Generalize V6 analysis result envelope with source readers

Reuse V6 transition/delta/compare/ranking logic where the input representation is compatible, but require an explicit source reader/adapter.

Do not build one fake generic RAM reader that assumes identical address spaces.

Good:

```text
common analysis engine
  <- browser-wasm reader
  <- winkawaks reader
  <- stable-retro-fbneo reader
```

Bad:

```text
one offset table assumed valid everywhere
```

All V11 analysis remains:

```text
researchOnly = true
semanticAuthority = false
```

unless an existing source-specific authority explicitly says otherwise. Cross-source numeric similarity is never semantic proof.

## 9. Generalize V7 collection batch/scheduling only where applicable

Reuse the existing V7 bounded local scheduling/task materialization machinery.

For Training Farm this means scheduling **collection/export reads**, not gameplay actions or worker orchestration.

The Collector may schedule “collect worker 3 observation snapshot at X” or a bounded stream read if supported.

It must not schedule “press attack”, “reset episode”, “load savestate”, “run branch”, “train PPO”, or “scale fleet to 10”.

Training Farm action/search scheduling stays in Training Farm.

## 10. Generalize V8 DuckDB warehouse to all three sources

Reuse DuckDB 1.5.5.

The derived warehouse must support source-aware query across:

```text
browser-wasm
winkawaks
stable-retro-fbneo
```

Every relevant table/view must preserve `sourceNamespace` and source provenance keys by default.

Cross-source joins must retain both sides' source/provenance columns. Do not collapse them into a generic `wof` authority.

Warehouse remains rebuildable/disposable derived state. Source artifacts/catalog remain authority.

Keep existing query safety boundaries: no arbitrary dangerous SQL/file/network extension surface.

## 11. Generalize V9 reuse-first planner — no cross-source semantic guessing

Reuse V9 exact reuse-first planning.

Default reuse policy must be **same-source exact-authority reuse**.

A Browser request must not be satisfied by a WinKawaks dataset merely because scene metadata looks similar.

A Training Farm request must not be satisfied by a WinKawaks dataset merely because a numeric offset matches.

Cross-source evidence may be presented as related research context only when explicit mapping provenance exists, but it must not satisfy a strict missing-slot requirement unless the request itself authorizes a separately proven cross-source mapping contract.

When no exact reusable dataset exists, compile only the missing collection jobs. For Training Farm, compilation must remain collection-only and never turn into training action orchestration.

## 12. 10-worker protocol coverage without violating current stage guard

V11 implementation self-check must include deterministic ROM-free fixtures for:

- one active Training Farm worker;
- explicit worker ID selection;
- multiple workers with independent generation identity;
- 10 active fixture workers selected by bounded `ALL_ACTIVE maxWorkers=10`;
- 11 eligible fixture workers fail closed when max is 10;
- duplicate worker ID/conflicting generation fail closed;
- worker restart during capture withholds PASS;
- episode/root/branch identity change during capture withholds PASS or becomes explicit PARTIAL according to contract;
- two workers never splice artifacts/frames;
- one worker failure cannot falsely mark the other worker's artifact as its own;
- stale export record rejected;
- malformed/coercible worker selector rejected.

These are repository fixtures only. They are not proof that 10 real emulator workers currently run.

Do not change `StageGuard` to enable 10 real workers for V11 testing.

## 13. Historical data registration / migration

V11 should provide a bounded deterministic registration/migration mechanism for existing evidence from:

- current WinKawaks V4 catalog;
- V10 Browser results/artifacts where present;
- Training Farm existing deterministic/fork/observation results that are structurally eligible.

Migration means “register existing immutable evidence into the unified catalog with explicit provenance”, not “rewrite old bytes into a new source identity”.

Required migration facts include:

- original repository/path/artifact identity;
- original schema/version;
- original SHA-256;
- source namespace;
- registration/migration schema/version;
- registration timestamp/task if applicable;
- whether raw artifact bytes are directly available or metadata-only;
- any limitations.

No synthetic re-attribution.

---

# Source/authority hard rules

## One Collector product does not mean one runtime authority

Hard rule:

```text
browser-wasm offset
!= automatically winkawaks offset
!= automatically stable-retro-fbneo offset
```

Do not silently share:

- numeric offsets;
- raw address-space layout;
- runtime/session identities;
- Worker generation;
- emulator worker generation;
- savestate identity;
- branch/root identity;
- Browser projection/render authority;
- source-specific timing/RNG assumptions.

## Browser V10 safety/identity must not regress

Preserve:

- localhost-only narrow CDP;
- exact World 921031 SHA gate;
- Page/Worker/WASM generation isolation;
- max 10 Browser targets;
- no Browser input/navigation/DOM/game RAM mutation;
- V10 fake-CDP regressions.

## WinKawaks V3–V9 compatibility must not regress

Preserve existing:

- snapshot/burst/segmented capture;
- V3 segmented terminal authority;
- V4 catalog authority;
- V5 retention safety;
- V6 analysis reader;
- V7 batch acquisition;
- V8 DuckDB warehouse;
- V9 exact reuse-first planner;
- legacy task compatibility through the Unified Agent;
- read-only/no-input boundary.

## Training Farm control authority must remain separate

Do not modify training policy/search merely to make collection easier.

If a narrow exporter hook is necessary, it must be observation-only and must not affect action choice or timing authority.

---

# Implementation ownership / repository writes

Primary Unified Collector implementation remains:

`ouyong520/wof-winkawaks-bridge`

Training Farm source hook lives only where source ownership requires it:

`ouyong520/wof-ai-private/training/farm/**`

PM authority/results/claims live in:

`ouyong520/wof-ai-private/parallel/PM/**`

Because `wof-ai-private/main` is concurrently modified by Alpha workers, re-read current main immediately before each write and preserve unrelated commits.

Do not modify:

- `product/alpha/**`;
- Alpha release/proof/live acceptance/danger/target/projection logic;
- Browser PYLAUNCH/OneClick merely for Collector convenience;
- Training Farm proof gates/R0.5 authorization;
- ROM files or copyrighted game bytes.

---

# Testing cadence

Follow `TESTING_CADENCE_POLICY.md`.

This is one coherent V11 implementation module, not a chain of Fresh QA generations.

Required final implementation-owned boundary:

1. compile current maintained V3–V11 modules;
2. exact maintained V3–V10 regressions remain PASS;
3. V11 Training Farm exporter/adapter fixtures PASS;
4. unified task/status/result strict-schema tests PASS;
5. unified catalog/storage/analysis/batch/warehouse/planner tests PASS;
6. historical registration/migration fixtures PASS;
7. source isolation/safety tests PASS;
8. one maintained GitHub Actions V3–V11 regression workflow tied to exact final bridge HEAD PASS.

If a concrete defect is found, fix it and rerun affected + final current-head boundary. Do not manufacture QA loops.

No real Browser/WOF session is required for V11 repository implementation acceptance unless an actual implementation defect cannot be resolved without it.

No real 2/4/8/10-worker Training Farm launch is authorized by V11.

---

# Required durable RESULT

On successful completion, write:

`parallel/PM/WOF_UNIFIED_COLLECTOR_V11_TRAINING_FARM_ADAPTER_UNIFIED_TASK_DATA_STACK_RESULT.md`

The RESULT must record at minimum:

- final exact bridge HEAD/tree;
- exact relevant `wof-ai-private` Training Farm hook source commit/blobs;
- V10 starting authority;
- all V11 schema/adapter/exporter versions;
- source namespace allowlist;
- exact task/status/result compatibility semantics;
- Training Farm worker/export identity model;
- one/set/all-active selector semantics and max-10 bound;
- stale/restart/generation/episode/root/branch fail-close behavior;
- exact collection actions supported;
- proof that Collector cannot drive Training Farm actions;
- unified dataset identity/catalog model;
- V5 retention generalization;
- V6 source-reader analysis model;
- V7 collection-only scheduling model for Training Farm;
- V8 multi-source DuckDB schema/query behavior;
- V9 same-source exact reuse behavior and cross-source non-equivalence rule;
- historical registration/migration behavior;
- exact dependencies/reuse classifications;
- exact test counts/results;
- exact successful V3–V11 workflow run ID/job ID/head SHA;
- current real Training Farm stage limitation (`maxRealEmulatorWorkersThisStage=1`, no V11 real 10-worker proof);
- Alpha/ROM/proof-gate isolation;
- remaining V12 work.

Allowed success verdict:

`COMPLETE — WOF UNIFIED COLLECTOR V11 TRAINING FARM ADAPTER + UNIFIED TASK/DATA STACK — THREE SOURCE NAMESPACES ON ONE COLLECTOR DATA PLANE COMPLETE`

Otherwise only a precise unavoidable:

`BLOCKED — WOF UNIFIED COLLECTOR V11 TRAINING FARM ADAPTER + UNIFIED TASK/DATA STACK — <exact external/unresolvable blocker>`

A failing repository test is not automatically an external blocker; repair concrete implementation defects first.

---

# Claim/stage closeout

After and only after the durable V11 RESULT is committed:

1. update the V11 canonical claim to `COMPLETE` with exact RESULT path/commit and final bridge head/tree;
2. update the matching V11 stage claim to `COMPLETE` with the same terminal authority;
3. preserve all V10 and Training Farm historical claims/results unchanged;
4. do not start V12 implementation inside V11 closeout.

---

# V11 stop condition

Do not stop at:

- claim acquisition;
- exporter skeleton;
- adapter skeleton;
- schema creation;
- one-worker fixture;
- 10-worker synthetic fixture alone;
- catalog generalization alone;
- DuckDB query alone;
- local tests;
- CI launch;
- CI PASS without RESULT/claim closeout.

Continue until exactly one of:

- `COMPLETE` with coherent V11 implementation + final V3–V11 regression + durable RESULT + canonical/stage COMPLETE;
- precise unavoidable `BLOCKED`;
- duplicate/already-complete/superseded `NO EXECUTION` from mandatory preflight.

## Final architecture after V11

When V11 is COMPLETE, normal collection architecture must be:

```text
ONE Git queue
-> ONE Unified Collector Agent
   -> browser-wasm adapter
   -> winkawaks adapter
   -> stable-retro-fbneo adapter
-> ONE task/status/result family
-> ONE source-aware catalog/storage/analysis/warehouse/planner stack
```

V12 then performs final OneClick/legacy retirement/live acceptance/freeze. Do not create a V13/V14 roadmap merely to continue activity.

# WinKawaks Collector V7 — Reuse-First Batch Acquisition Automation Lite

stageId: `WINKAWAKS_COLLECTOR_V7_REUSE_FIRST_BATCH_ACQUISITION_AUTOMATION_LITE_V1`
dedupProtocol: `v2`
dedupKey: `winkawaks.collector.v7.reuse-first-batch-acquisition-automation-lite`
dedupMode: `exclusive`

Priority: **P2 batch acquisition automation / reuse-first orchestration MVP**

## Duplicate-forward preflight — mandatory

Read and obey:

- `parallel/PM/COLLECTOR_WORKER_EXECUTION_POLICY.md`
- `parallel/PM/PROJECT_EXTERNAL_GITHUB_REUSE_POLICY.md`
- `parallel/PM/COLLECTOR_EXTERNAL_GITHUB_REUSE_POLICY.md`
- `parallel/PM/TESTING_CADENCE_POLICY.md`
- `parallel/PM/STAGE_DEDUP_GUARD.md`
- `COLLECTOR_ROUTING.md`
- `RUNTIME_DATA_SOURCE_BOUNDARIES.md`

Treat this post as potentially duplicated until current authority is checked. Before substantive implementation verify both current mains, this exact START_PROMPT, canonical/stage claims, any same/equivalent V7 RESULT, and any newer recovery/successor authority.

If the same/materially equivalent V7 is already legitimately ACTIVE under another current generation, already COMPLETE, or superseded by a newer active/completed successor, do not execute duplicate implementation. Stop:

`DUPLICATE / ALREADY COMPLETE / SUPERSEDED — NO EXECUTION — <current authority>`

Do not create a second equivalent claim, do not invent a recovery to bypass dedup, and do not rerun completed work merely to create activity.

If not duplicate, acquire canonical dedup-v2 canonical/stage ownership before substantive implementation.

## Current completed Collector authority

At task creation:

- V3 segmented long-session capture: COMPLETE;
- V4 dataset catalog / immutable capture identity: COMPLETE;
- V5 long-run storage / retention / archive / pressure guard: COMPLETE;
- V6 segment-aware analysis reader: COMPLETE through Recovery V2;
- exact V6 final bridge candidate: `c20c9dbe0684c645b4bb8760ab5110b00d12b09c`;
- V6 Recovery V2 durable RESULT exists and canonical/stage claims are closed;
- no V7 batch-acquisition module/claim/RESULT was found before this START_PROMPT was staged.

Do not rerun or rewrite V3/V4/V5/V6 merely because V7 consumes them.

## Mandatory external GitHub reuse decision

The PM reuse preflight selected a mature upstream rather than custom-building a scheduler.

### DIRECT_USE — APScheduler

Preferred upstream:

- repository: `agronholm/apscheduler`
- stable release inspected by PM: `3.11.3`
- release date: `2026-06-28`
- license: MIT
- upstream still actively maintained in late August 2026

V7 MVP should use APScheduler as a normal dependency/library. **Do not fork APScheduler.**

Before coding, verify the exact stable version compatible with the bridge's current supported Python/Windows environment. Prefer `3.11.3` if compatible. If repository facts force another stable version, record the exact version, upstream commit/tag/license and reason in V7 docs/RESULT.

### DEFER — Prefect

`PrefectHQ/prefect` is a strong later orchestration candidate (PM inspected stable `3.8.4`, Apache-2.0, active), but it is intentionally **not part of this V7 Lite MVP**.

Do not add Prefect server, Docker, PostgreSQL, Redis, cloud orchestration, work pools or dashboard deployment in V7 Lite.

The architecture should leave a narrow future orchestration adapter boundary so a later module can replace the local scheduler without changing Collector task/result authority.

### No unnecessary rewrites

Do not replace working V3–V6 code with Polars/DuckDB/psutil/Pymem merely because they are available. V7 is the first reuse-first orchestration module; only add an external dependency where it materially removes commodity scheduler work.

## Purpose

Turn the existing single-task GitHub Collector queue into a small, reliable local batch experiment runner so the Owner can describe a batch once and let Collector execute several already-supported capture tasks serially with exact identity, storage protection and optional post-analysis.

Operating principle:

`batch plan -> deterministic task materialization -> remote exact task blob -> existing Collector queue execution -> exact result verification -> optional V4/V5/V6 post-step -> durable batch result`

V7 must orchestrate existing authority. It must not create a second task/capture/result truth system.

## MVP boundary

Target a deliberately small useful MVP:

- one local WinKawaks Collector instance;
- one active batch at a time;
- serial task execution by default (`maxConcurrentCaptures=1`);
- roughly 1–100 tasks per batch with conservative repository limits;
- repeated capture trials and timed spacing;
- existing snapshot / burst / segmented-v3 actions only;
- existing task schema validation and queue execution path;
- V5 storage guard before each capture;
- optional V4 catalog refresh after authoritative results;
- optional V6 post-analysis after selected task/batch completion;
- structured batch status/result/manifest;
- local-first Windows deployment;
- no gameplay automation.

Do not turn this into a distributed scheduler platform.

## Required capabilities

### 1. Versioned batch-plan schema

Define one strict versioned machine-readable batch plan, e.g. `wof_collector_batch_plan_v1`.

At minimum bind:

- `batchId`;
- plan schema/version;
- deterministic canonical `planSha256`;
- optional explicit `experimentId` / `repeatGroupId`;
- human description/research question;
- ordered steps/tasks;
- schedule policy;
- failure policy;
- storage policy reference/identity where applicable;
- optional post-analysis declarations;
- creator/source provenance;
- safety invariants.

Unknown keys fail closed unless explicitly versioned/allowed. Numeric values must be strict finite native numbers/integers, not coercible strings/bools.

Plan identity must depend on canonical plan content, not path/filename/display labels.

### 2. Task materialization must preserve existing queue authority

Each capture step must become an ordinary existing Collector task using the current task schema and `_validate_task`/equivalent authority.

Do not bypass the existing GitHub queue contract by calling low-level capture directly from a batch and then inventing a result.

For each materialized task:

1. derive a deterministic unique task identity from batch identity + step/trial/attempt identity using a documented versioned formula;
2. validate with the current Collector task validator;
3. publish/create the task under the existing `tasks/queue/**` authority using create-only or exact-same-content idempotent semantics;
4. read the remote task back and obtain its actual Git blob SHA;
5. only then allow the existing queue execution path to run it;
6. verify result/status against exact `taskId + taskBlobSha` and V3 segmented authority when applicable.

A local plan hash is never a substitute for remote `taskBlobSha`.

If the target task path already exists with different bytes/content, fail closed. Never overwrite a conflicting task in order to make a rerun work.

### 3. Reuse existing queue runner

Current `bridge/collector_queue_runner.py` already owns important authority including:

- queue discovery/order;
- exact terminal-result duplicate handling;
- `taskId + taskBlobSha` checks;
- V3 segmented terminal authority;
- current task validation;
- existing capture execution and result publication.

V7 must call/wrap this existing path rather than duplicate its capture/result logic.

Any small adapter needed for exact single-task invocation may be added, but authority stays in the existing runner/validators.

### 4. APScheduler integration

Use APScheduler only for commodity local scheduling/timing.

Required behavior:

- exact pinned/tested upstream version recorded;
- one batch-local scheduler adapter owned by Collector;
- deterministic job IDs tied to batch/step identity;
- serial capture execution by default;
- no overlapping capture jobs;
- bounded delay/interval support;
- clean cancellation/shutdown;
- no scheduler state may override Collector task/result truth;
- a scheduler callback crash must not mark a Collector task/batch COMPLETE;
- restarting the V7 runner reconstructs state from durable batch/task/result authority rather than trusting only volatile scheduler memory.

The scheduler is infrastructure, not evidence authority.

### 5. Repeated trials

Support practical repeated acquisition without manual creation of many queue JSON files.

A step may request bounded `repeatCount` and optional bounded interval/delay.

Each trial gets its own exact immutable task identity and explicit:

- batchId;
- experimentId where supplied;
- repeatGroupId;
- trialId;
- trialOrdinal;
- attemptOrdinal if retry creates a successor task.

Do not infer group membership from filenames later.

### 6. Retry semantics — new identity, never false replay

Default should be conservative: no automatic retry unless explicitly enabled in the batch policy.

If retry is enabled:

- retries are bounded;
- a retry after terminal FAILED/PARTIAL creates a **new task identity** with explicit predecessor/attempt lineage;
- never mutate an old task blob or overwrite old result/status;
- never call an old failed terminal task successful because a later retry passed;
- batch result must expose every attempt.

V3 runtime/session rules remain unchanged; V7 must never stitch two sessions/attempts into one capture.

### 7. V5 storage guard before every capture

Before materializing/executing each capture, consume the current V5 storage/pressure authority.

If V5 says new capture is blocked/critical or conservative projected capacity is insufficient:

- do not start the capture;
- preserve prior completed tasks;
- mark the batch step with an exact storage-pressure disposition;
- follow batch failure policy;
- do not prune/archive automatically merely to force the batch through unless a separate explicit existing V5 action/policy was requested.

V7 must not weaken V5 reserve/budget/sole-copy protections.

### 8. Batch state / durable checkpoint

Implement a durable local batch manifest/checkpoint with strict versioning and atomic writes.

Suggested states may include:

- `PLANNED`
- `RUNNING`
- `WAITING`
- `PARTIAL`
- `FAILED`
- `COMPLETE`
- `CANCELLED`

Exact names may follow repository conventions, but terminal meaning must be unambiguous.

Durable state must bind:

- batchId / planSha256;
- exact step order;
- materialized task IDs and remote taskBlobShas;
- result/status refs and hashes where available;
- attempt lineage;
- scheduling metadata;
- current/next step;
- V5 preflight disposition;
- optional V4/V6 post-step results;
- failure/cancel reason;
- timestamps.

Atomic/restart-safe behavior is required. A crash between remote task creation and execution must be resumable without duplicating the task.

### 9. Idempotent resume

Rerunning an unchanged batch plan must not create duplicate captures for already-authoritatively-completed steps.

Resume algorithm must reconcile:

- local checkpoint;
- exact remote task blob;
- exact existing remote result/status;
- segmented authority where applicable.

Remote exact task/result authority outranks stale local scheduler memory.

If local checkpoint and remote authority conflict materially, fail closed and report the conflict.

### 10. Failure policy

Support a small explicit policy surface, at minimum:

- `stopOnFailure=true` default;
- optional continue-to-next-step for research batches where requested;
- bounded retry count when explicitly enabled.

Never hide failed/partial steps behind an overall COMPLETE.

A batch may be COMPLETE only when every required step has an authoritative successful terminal result according to its underlying action contract and all required post-steps passed.

### 11. V4 catalog integration

After an authoritative capture result, V7 may invoke the existing V4 index/update path where appropriate so new datasets become discoverable.

Do not create a second catalog or alter V4 lifecycle/integrity semantics.

If catalog refresh fails, capture authority remains intact; batch output must report the post-step failure honestly according to required/optional policy.

### 12. Optional V6 post-analysis

Allow an explicit, bounded post-analysis declaration using existing V6 operations where practical.

Examples:

- delta on a completed trial;
- compare selected completed trials;
- rank across an explicit repeated-trial group.

Rules:

- opt-in only;
- V6 `researchOnly=true / semanticAuthority=false` remains intact;
- analysis cannot turn a failed/partial capture into a successful capture;
- no gameplay semantic promotion;
- no giant unbounded output.

### 13. Operator/gameplay boundary

V7 does **not** automate the game.

Hard rule:

```text
readOnly=true
writesGameMemory=false
inputInjection=false
```

Do not add keyboard/gamepad injection, macros, Lua gameplay control, savestate stepping, AI actions, automatic scene navigation or Training Farm behavior.

If a future experiment needs the Owner to change a scene between captures, V7 Lite may expose a clear manual checkpoint/waiting state, but it must not solve that by injecting input.

### 14. CLI / Windows-local UX

Provide a small practical CLI following repository conventions, conceptually:

- `validate-plan`
- `run`
- `resume`
- `status`
- `cancel`
- `show`

Exact naming may differ.

Requirements:

- Windows-friendly paths and UTF-8;
- structured JSON output;
- concise human status;
- clear dependency-missing error for APScheduler;
- deterministic ordering;
- explicit batch plan path;
- no daemon/server requirement for MVP;
- no Docker/PostgreSQL/Redis/Prefect requirement.

Document the shortest install/run path for an Owner/local executor.

### 15. Dependency / license record

Record the exact APScheduler version tested and its MIT license attribution in V7 documentation/dependency metadata.

Prefer a normal package dependency with a narrow import surface. Do not copy large upstream source trees into this repository.

If this repository has no existing Python dependency manifest, add the smallest clear Collector-owned dependency surface rather than introducing a heavy packaging migration unrelated to V7.

### 16. Security / path / concurrency

Fail closed on:

- malformed batch plan;
- duplicate/conflicting batch ID with different plan hash;
- conflicting remote task path/content;
- non-exact task blob/result binding;
- concurrent second batch attempting to own the same local runner when exclusive mode is required;
- stale local checkpoint claiming completion not backed by remote authority;
- invalid V5 capacity state;
- invalid scheduler/job identity;
- path traversal for local batch/derived result paths;
- cancellation during an active capture being misreported as clean COMPLETE.

Use a narrow local lock/ownership contract for one active V7 batch runner.

### 17. Side-lane isolation

Do not modify:

- `product/alpha/**`;
- Alpha release/proof/live acceptance/danger/target semantics;
- Transport / Recorder / PYLAUNCH / OneClick;
- Training Farm / Stable-Retro / FBNeo / PPO/RL / savestate/action injection / 10-worker scheduling;
- V3/V4/V5/V6 authority semantics except narrow compatibility adapters required for V7 consumption.

Collector V7 incomplete/blocked is not an Alpha V1 or Training Farm blocker.

## Implementation-owned self-checks

Finish the coherent V7 Lite module first, then run the necessary implementation-owned checks. Do not open Fresh QA/cross-check/second opinion.

Cover at least:

- strict batch-plan schema and canonical hash;
- APScheduler exact dependency/import/version path;
- deterministic scheduler job IDs;
- `maxConcurrentCaptures=1` / no overlap;
- task materialization through current validator;
- create-only/idempotent same-content remote task behavior;
- conflicting task path fail-close;
- remote taskBlobSha readback before execution;
- current queue runner used for execution/terminal authority;
- unchanged-plan resume skips authoritative completed tasks;
- stale local checkpoint cannot fake complete;
- crash after task publish / before execute resumes without duplicate task creation;
- repeatCount/trial IDs/group metadata;
- retry creates successor task identity and preserves failed predecessor;
- V5 blocked capacity prevents capture start;
- optional V4 refresh wiring;
- optional V6 research-only post-analysis wiring;
- stopOnFailure and continue policy;
- cancellation semantics;
- lock/concurrent-runner behavior;
- missing APScheduler gives precise dependency error;
- no gameplay input/memory write boundary;
- necessary V3/V4/V5/V6 regression compatibility.

Use mocks/deterministic fixtures for GitHub remote writes and scheduler timing where practical. **Do not start real WinKawaks, Browser/WOF, Training Farm, or gameplay automation for repository self-check.**

If self-check finds a concrete V7 defect, fix that defect cluster and rerun affected checks. Do not manufacture QA stages.

## Documentation

Document at minimum:

- why APScheduler was selected over custom scheduling and why Prefect is deferred;
- exact upstream version/license;
- install command/Windows-local prerequisites;
- batch plan example;
- batch identity/task identity/retry lineage;
- resume/reconciliation behavior;
- V5/V4/V6 integration;
- failure/cancel semantics;
- current intentional limitation: no gameplay/scene automation.

Do not commit ROM/BIOS/game assets or captured private/raw data merely for docs/tests.

## Durable completion

Before COMPLETE, write a durable RESULT under `parallel/PM/**` recording at minimum:

- exact final bridge HEAD/tree;
- exact changed files/blobs;
- APScheduler upstream repo/version/license and reuse classification `DIRECT_USE`;
- Prefect reuse classification `DEFER` and reason;
- batch plan/schema/version;
- batch/task identity formulas;
- remote task materialization and taskBlob authority;
- scheduling/max-concurrency contract;
- repeat/retry/resume contract;
- V5/V4/V6 integration;
- CLI/dependency UX;
- safety/isolation boundaries;
- implementation-owned self-check commands/results;
- any remaining real-runtime limitation.

Close canonical and stage claims correctly under canonical dedup v2.

## Stop

Do not stop at external-library research, claim acquisition, dependency addition, one scheduler helper, one test, documentation-only progress or an intermediate status report.

Keep reporting sparse. Continue through the complete V7 Lite batch-acquisition orchestration module, integration, implementation-owned self-checks, docs, durable RESULT and claim/stage closeout.

Do not move to Prefect/full distributed orchestration, gameplay automation or a V8 module from this worker.

Stop only at:

`COMPLETE — WINKAWAKS COLLECTOR V7 REUSE-FIRST BATCH ACQUISITION AUTOMATION LITE — LOCAL SERIAL BATCH MVP COMPLETE`

or:

`BLOCKED — WINKAWAKS COLLECTOR V7 REUSE-FIRST BATCH ACQUISITION AUTOMATION LITE — <precise unavoidable blocker>`

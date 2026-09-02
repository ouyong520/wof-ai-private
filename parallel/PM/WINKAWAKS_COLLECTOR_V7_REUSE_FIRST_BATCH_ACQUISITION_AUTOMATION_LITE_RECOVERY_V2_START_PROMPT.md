# WinKawaks Collector V7 — Reuse-First Batch Acquisition Automation Lite Recovery V2

stageId: `WINKAWAKS_COLLECTOR_V7_REUSE_FIRST_BATCH_ACQUISITION_AUTOMATION_LITE_RECOVERY_V2`
dedupProtocol: `v2`
dedupKey: `winkawaks.collector.v7.reuse-first-batch-acquisition-automation-lite.recovery-v2`
dedupMode: `exclusive`

Priority: **P2 implementation recovery / integration + closeout**

## PM recovery authorization

This is a PM-authorized implementation recovery for the existing V7 module. It is **not Fresh QA**, not a redesign, and not permission to restart V7 from scratch.

The original V7 worker was confirmed by Owner-forwarded terminal report to have stopped because its tool execution window ended while preparing the Collector smoke workflow. The worker explicitly reported that it had not completed repository V3–V7 regression/CI, defect-fix closure, durable PM RESULT, or canonical/stage claim completion.

Git verification at Recovery V2 staging confirms the same repository facts:

- original V7 canonical claim remains historical `ACTIVE` under owner `chatgpt-gpt-5.6-sol-v7-lite`;
- original V7 durable RESULT path does not exist;
- current `ouyong520/wof-winkawaks-bridge/main` is still `5a49a42bc8c269be3bcc07b35b1762c6b8e76d1a`;
- exact tree at that candidate: `eab8fdc1a3c20f41c5c4f13fe2e8fe0176047445`;
- no later V7 implementation commit was found after `5a49a42...` at recovery staging;
- no newer V7 Recovery V3/successor authority was found at recovery staging.

Recovery V2 therefore exists only to continue the already-landed V7 implementation from current HEAD, repair concrete integration defects if found, run one coherent implementation-owned regression boundary, write durable RESULT, and close Recovery V2 canonical/stage authority.

Do **not** edit, delete, rewrite, or falsely close the historical original V7 ACTIVE claim. Recovery V2 will supersede that stopped generation as successor authority if COMPLETE.

## Mandatory duplicate-forward preflight

Treat this Recovery V2 post itself as potentially duplicated.

Before substantive work, re-read:

- both current repository mains;
- `parallel/PM/WINKAWAKS_COLLECTOR_V7_REUSE_FIRST_BATCH_ACQUISITION_AUTOMATION_LITE_START_PROMPT.md`;
- original V7 canonical/stage claims;
- this exact Recovery V2 START_PROMPT;
- any Recovery V2 canonical/stage claim;
- any original or Recovery V2 durable V7 RESULT;
- any newer V7 recovery/successor authority.

If this same/materially equivalent Recovery V2 is already legitimately ACTIVE under another current owner, already COMPLETE, or superseded, stop immediately:

`DUPLICATE / ALREADY COMPLETE / SUPERSEDED — NO EXECUTION — <current authority>`

Do not create a second equivalent claim, do not invent Recovery V3 to bypass dedup, and do not rerun completed regression merely to create activity.

If no current Recovery V2 authority exists, acquire the Recovery V2 canonical dedup-v2 claim and matching stage claim before substantive implementation.

## Read and obey

- `parallel/PM/COLLECTOR_WORKER_EXECUTION_POLICY.md`
- `parallel/PM/PROJECT_EXTERNAL_GITHUB_REUSE_POLICY.md`
- `parallel/PM/COLLECTOR_EXTERNAL_GITHUB_REUSE_POLICY.md`
- `parallel/PM/TESTING_CADENCE_POLICY.md`
- `parallel/PM/STAGE_DEDUP_GUARD.md`
- `COLLECTOR_ROUTING.md`
- `RUNTIME_DATA_SOURCE_BOUNDARIES.md`
- original V7 START_PROMPT above

All original V7 functional requirements remain in force except where this Recovery V2 explicitly narrows the remaining work to current-head completion.

## Exact current V7 implementation lineage — preserve, inspect, do not redo

Current V7 bridge lineage already landed:

1. `6e55fccf42c00f2cfce8ccecdb5c7beac3cf09c4` — pin APScheduler reuse dependency;
2. `5a583d3751e1c88d9d9075bef06d6becc7848113` — strict V7 batch-plan schema;
3. `694fafade2ffdec1ae71ba3bb4755b229372ccb9` — batch-plan example;
4. `a913a4bc53d0291125a33aafa6aa988ef7954a31` — V7 reuse-first local batch runner documentation;
5. `af348d3ebcf4c8cbd207ed3ece600fd43453e567` — ignore local batch state / derived outputs;
6. `bfc298bca0ead49d2c977aeda440a2969c6c2e04` — core `bridge/batch_acquisition.py` implementation;
7. `5a49a42bc8c269be3bcc07b35b1762c6b8e76d1a` — deterministic implementation self-checks.

Important current facts already intentionally implemented:

- `requirements-collector-v7.txt` pins `APScheduler==3.11.3`;
- upstream record: `agronholm/apscheduler` tag `3.11.3` at `4308ec95b94069f5dbdddb6c60fb792dfc8c40a4`;
- license: MIT;
- classification: `DIRECT_USE`;
- APScheduler is used as dependency/library; no vendoring/fork;
- Prefect remains `DEFER` and is not part of V7 Lite;
- core V7 uses current Collector task validator/queue runner rather than creating capture/result truth;
- V5 storage guard, V4 catalog and V6 research-only analysis adapters are present;
- deterministic V7 tests already exist at `tests/test_batch_acquisition.py`.

Do not rewrite these components merely to make the recovery look active. Inspect current code and patch only real defects or missing integration.

## Recovery V2 primary work

### 1. Finish Collector smoke integration

The stopped worker specifically had not yet completed `.github/workflows/collector-python-smoke.yml` integration.

Update the current workflow conservatively so the exact V7 candidate is exercised with V3–V7 compatibility.

At minimum ensure workflow path triggers cover the material V7 surfaces, including as applicable:

- `bridge/batch_acquisition.py`;
- `tests/test_batch_acquisition.py`;
- V7 batch-plan schema;
- `requirements-collector-v7.txt`;
- V7 example/docs when they materially affect contract wiring;
- `.github/workflows/collector-python-smoke.yml` itself.

The workflow must install the exact pinned V7 dependency before V7 import/tests, using the small existing dependency file rather than broad packaging migration.

Compile current V7 module together with the existing Collector modules.

Add one explicit V7 implementation-owned self-check step that exercises the current deterministic tests and minimal CLI/schema/dependency invariants.

Keep the workflow:

```text
permissions:
  contents: read
```

Do not reintroduce the V6-style repository-writing mutable “latest PASS receipt” mechanism. Do not give the workflow `contents: write`, do not commit/push PASS files from CI, and do not make public mutable status files terminal implementation authority.

The immutable GitHub Actions run tied to exact head SHA is the implementation self-check evidence.

### 2. Run one coherent V3–V7 regression boundary

After smoke integration is complete, run the necessary current-head implementation checks as one coherent boundary.

Required coverage:

- Python compile for current Collector modules including V7;
- V3 segmented tests;
- V4 catalog tests/current retained-evidence index;
- V5 storage retention + hardening tests/current status wiring;
- V6 analysis reader tests + research-only/schema invariants;
- V7 deterministic batch acquisition tests;
- V7 CLI/import/dependency/version checks;
- existing immutable discovery / segmented authority / V5 capture guard / V6 source-authority wiring;
- V7 safety/source boundary.

Do not start real WinKawaks, Browser/WOF, Training Farm or gameplay automation.

No Fresh QA, second opinion, cross-check, historical PASS rerun chain, or separate QA generation.

If the coherent run exposes a concrete defect cluster, fix the actual defect and rerun affected/current-head checks once. Do not loop implementation -> QA -> fix -> QA unnecessarily.

### 3. Verify current V7 authority semantics — fail closed

Recovery must verify, and repair only if repository facts show a defect, that current V7 still satisfies the original contract:

- strict `wof_collector_batch_plan_v1` parsing; unknown/coercible/non-finite values fail closed;
- deterministic `planSha256` from canonical plan content;
- deterministic task/trial/job identity formulas;
- unique retry successor task identity with predecessor/attempt lineage;
- one active local batch / serial capture semantics (`maxConcurrentCaptures=1`);
- no overlapping captures;
- materialized tasks go through current `_validate_task`/existing task authority;
- create-only or exact-same-content task publication;
- conflicting remote task bytes fail closed;
- actual remote Git task blob SHA is read before execution;
- existing `collector_queue_runner.run_queued_task()` / equivalent current queue authority performs capture/result handling;
- exact `taskId + taskBlobSha` result binding;
- V3 segmented terminal authority remains authoritative for segmented actions;
- restart/resume reconciles durable local checkpoint with remote task/result authority;
- stale local checkpoint cannot fake COMPLETE;
- crash after task publish but before execution resumes without duplicate task creation;
- V5 guard runs before capture/material execution and can block new capture safely;
- V4 integration reuses existing catalog semantics rather than creating a second catalog;
- V6 post-analysis remains `researchOnly=true / semanticAuthority=false`;
- required post-analysis failure cannot be hidden by capture success;
- optional post-analysis/catalog failures remain explicit according to policy;
- cancellation cannot turn active/failed work into COMPLETE;
- terminal batch COMPLETE means every required capture/post-step has exact success authority;
- no game input automation, memory writes, Lua/macros, savestate stepping or Training Farm behavior.

### 4. APScheduler reuse decision is already made — do not restart research

Retain:

```text
APScheduler==3.11.3
upstream: agronholm/apscheduler
tag commit: 4308ec95b94069f5dbdddb6c60fb792dfc8c40a4
license: MIT
classification: DIRECT_USE
```

Do not fork APScheduler. Do not copy upstream source into the bridge. Do not replace the current scheduling adapter with a custom scheduler unless exact current repository facts prove the existing adapter unusable; if so, BLOCK with a concrete reason rather than silently broadening scope.

Prefect remains deferred. Do not add Prefect server, Docker, PostgreSQL, Redis, work pools, dashboard, cloud orchestration or distributed workers in Recovery V2.

### 5. Preserve completed V3–V6 authority

Do not redesign or rewrite:

- V3 acquisition/segmented terminal authority;
- V4 immutable dataset/lifecycle authority;
- V5 storage/archive/prune safety;
- V6 analysis result/research-only authority.

Narrow compatibility fixes are permitted only if current V7 integration reveals a real defect, and the RESULT must state exactly what changed and why.

## Safety / lane isolation

Still mandatory:

```text
sourceNamespace=winkawaks
readOnly=true
writesGameMemory=false
inputInjection=false
```

Do not modify or block:

- `product/alpha/**`;
- Alpha V1 release/proof/live acceptance/danger/target semantics;
- Transport / Recorder / PYLAUNCH / OneClick;
- Training Farm / Stable-Retro / FBNeo / PPO/RL / 10-worker scheduling;
- gameplay controls/input automation.

Collector V7 incomplete/blocked does not block Alpha V1 or Training Farm.

## Recovery-owned interruption discipline

Do not treat claim acquisition, workflow edit, one patch, or one test as a stopping point.

If the execution environment is forcibly interrupted again, do not falsely write COMPLETE/BLOCKED. Preserve landed commits and leave Recovery V2 claim ACTIVE unless a durable terminal RESULT has actually been written. If the environment still permits a final Git write before interruption, a concise progress note may be added to the Recovery V2 claim/stage metadata without changing terminal state; this note is coordination metadata only, not success authority.

## Durable RESULT

On successful completion, write:

`parallel/PM/WINKAWAKS_COLLECTOR_V7_REUSE_FIRST_BATCH_ACQUISITION_AUTOMATION_LITE_RECOVERY_V2_RESULT.md`

The RESULT must record at minimum:

- final exact bridge HEAD and tree;
- V7 implementation lineage and exact relevant blob SHAs;
- exact APScheduler version/tag commit/license/classification;
- V7 schema/version/task/trial/job identity versions;
- batch-plan strictness and canonical plan identity;
- queue/taskBlob/result authority reuse;
- segmented authority behavior;
- serial scheduling/no-overlap behavior;
- retry/attempt lineage;
- resume/checkpoint reconciliation;
- V5 storage guard behavior;
- V4 catalog behavior;
- V6 research-only post-analysis behavior;
- cancellation/failure/COMPLETE semantics;
- CLI/Windows-local dependency path;
- final smoke workflow changes;
- exact implementation-owned test commands/counts/results where available;
- exact successful GitHub Actions workflow run ID and head SHA;
- safety/source isolation;
- intentional limitations: one local WinKawaks Collector, one active batch, serial capture, no gameplay automation, no Prefect/distributed orchestration;
- any remaining non-blocking runtime/operator limitations.

Final allowed success verdict:

`COMPLETE — WINKAWAKS COLLECTOR V7 REUSE-FIRST BATCH ACQUISITION AUTOMATION LITE — LOCAL SERIAL BATCH ORCHESTRATION COMPLETE`

Otherwise only a precise unavoidable:

`BLOCKED — WINKAWAKS COLLECTOR V7 REUSE-FIRST BATCH ACQUISITION AUTOMATION LITE RECOVERY V2 — <exact external/unresolvable blocker>`

A failing implementation test is not automatically an external blocker: fix concrete repository defects first.

## Claim/stage closeout

After and only after the durable Recovery V2 RESULT is committed:

1. update the Recovery V2 canonical claim to `COMPLETE` with exact RESULT path/commit, final bridge commit/tree, and exact successful workflow run ID;
2. update the matching Recovery V2 stage claim to `COMPLETE` with the same terminal authority;
3. preserve the original stopped V7 canonical/stage claim unchanged as historical ACTIVE residue;
4. record that Recovery V2 supersedes the original V7 dedup key.

Do not modify the original stopped claim merely to make history look clean.

## Stop condition

Continue through implementation integration, regression, concrete fixes, durable RESULT, and Recovery V2 claim/stage closeout.

Do not stop at claim acquisition, code review, workflow edit, local test, CI launch, or PASS observation.

Only stop at:

- `COMPLETE` with durable RESULT + Recovery V2 canonical/stage closeout;
- precise unavoidable `BLOCKED`;
- duplicate/already-complete/superseded `NO EXECUTION` from the mandatory preflight.

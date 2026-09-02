# WinKawaks Collector V7 — Reuse-First Batch Acquisition Automation Lite Recovery V2 RESULT

Status: **COMPLETE**

Date: 2026-09-02

stageId: `WINKAWAKS_COLLECTOR_V7_REUSE_FIRST_BATCH_ACQUISITION_AUTOMATION_LITE_RECOVERY_V2`
dedupKey: `winkawaks.collector.v7.reuse-first-batch-acquisition-automation-lite.recovery-v2`
claimToken: `c8f114f6638b4a71867f29f5d2a4ee9b`

## Recovery disposition

Recovery V2 resumed the interrupted V7 implementation from the already-landed bridge candidate `5a49a42bc8c269be3bcc07b35b1762c6b8e76d1a`. The V7 core, strict plan schema, APScheduler dependency pin, example plan, documentation, local serial batch runner and deterministic implementation self-checks were already present and were not rewritten.

The concrete remaining defect was the missing V7 integration in the maintained Collector smoke workflow: current CI covered V3–V6 but did not install the V7 dependency, compile the V7 module, run its deterministic tests/CLI/schema checks, or include V7 in the maintained authority/safety wiring check. Recovery V2 fixed that integration gap only, then ran the coherent V3–V7 regression boundary.

No additional V7 core defect was exposed by the completed regression. No defect was invented merely to create activity.

## Final bridge candidate

Repository: `ouyong520/wof-winkawaks-bridge`

Final main commit:

`4eb4b33bd09cfaeeb6644110a59b3452c489ea9e`

Final tree:

`19f96fa973fc608e367e66325731e1ec869a44bc`

Recovery commit:

`4eb4b33bd09cfaeeb6644110a59b3452c489ea9e` — `Collector V7 recovery: integrate batch automation smoke`

Parent / pre-recovery V7 candidate:

`5a49a42bc8c269be3bcc07b35b1762c6b8e76d1a`

Exact V7 implementation lineage retained:

- `6e55fccf42c00f2cfce8ccecdb5c7beac3cf09c4` — pin APScheduler reuse dependency
- `5a583d3751e1c88d9d9075bef06d6becc7848113` — strict batch plan schema
- `694fafade2ffdec1ae71ba3bb4755b229372ccb9` — batch plan example
- `a913a4bc53d0291125a33aafa6aa988ef7954a31` — V7 reuse-first local batch documentation
- `af348d3ebcf4c8cbd207ed3ece600fd43453e567` — ignore local batch state / derived outputs
- `bfc298bca0ead49d2c977aeda440a2969c6c2e04` — reuse-first local serial batch acquisition core
- `5a49a42bc8c269be3bcc07b35b1762c6b8e76d1a` — deterministic implementation self-checks
- `4eb4b33bd09cfaeeb6644110a59b3452c489ea9e` — Recovery V2 maintained smoke/CI integration

Relevant exact current blobs:

- `bridge/batch_acquisition.py` — `95cc4d6df4a5c4676ab9226342356d88a7ebf8f4`
- `tests/test_batch_acquisition.py` — `2369a1878d30e1c20cffbf51fcf98922cd7071a7`
- `schemas/collector_batch_plan_v1.schema.json` — `91cad9a3fafc3f940cd4d973457ea103c5866543`
- `requirements-collector-v7.txt` — `ae81eace03831c88519b2f51cbd7191c912065be`
- `examples/collector_batch_plan_v1.example.json` — `e345e6a61d51965098fda796a4ec0a4e4b6d1f7d`
- `docs/COLLECTOR_V7_REUSE_FIRST_BATCH_ACQUISITION.md` — `c8835360c8023b727ff687e23077ce77ee28ff8b`
- `.github/workflows/collector-python-smoke.yml` — `fed9b9338379c0ba624e36f1dc5251f763b3e9ae`
- `bridge/collector_queue_runner.py` — `8a25187b0e85cf839599a1be18376f06d63c0bd6`
- `bridge/collector_task_runner.py` — `babfa7345721dce39aea110f2f2d2da1b9c31f8f`
- `bridge/collector_segmented_authority.py` — `4814b6471ec1d597b304a3b68680518c375cc558`
- `bridge/collector_segmented_session.py` — `2370791a686de75d3b7e5eca00555266a90635fc`
- `bridge/dataset_catalog.py` — `a6f26e0624840f4b040ff4bb48af6b74a8020bfd`
- `bridge/collector_platform.py` — `981640b5dead5d291366daad0017252c5e4dde33`
- `bridge/analysis_reader.py` — `667a2290603d5f494947417db05eab8a6ac97b43`

## External reuse decision

V7 preserves the PM-authorized reuse decision:

- classification: `DIRECT_USE`
- upstream: `agronholm/apscheduler`
- version: `3.11.3`
- inspected upstream tag commit: `4308ec95b94069f5dbdddb6c60fb792dfc8c40a4`
- license: MIT
- dependency: `APScheduler==3.11.3`
- fork/vendor: none

`PrefectHQ/prefect` remains `DEFER`. Recovery V2 did not add Prefect, Docker, PostgreSQL, Redis, cloud orchestration, work pools or a scheduler server.

## V7 authority retained

Plan schema/version:

`wof_collector_batch_plan_v1`

Identity formula versions:

- task: `wof_collector_v7_task_identity_v1`
- trial: `wof_collector_v7_trial_identity_v1`
- scheduler job: `wof_collector_v7_scheduler_job_identity_v1`

The task identity remains bound to batch/plan/step/trial/attempt content. Trial identity stays stable across retry attempts, while each retry receives a successor task identity and preserves its predecessor lineage.

The example plan validated to canonical:

`planSha256=f359cc7067e31119913db6cb2640b9a98cf762a837365f908e3a95244732801e`

Strict runtime/schema behavior remains fail-closed for unknown keys and coercible/non-finite values. `maxConcurrentCaptures` remains strict integer `1`.

Each materialized capture still goes through the current Collector task validator and existing queue authority. V7 publishes only under `tasks/queue/<taskId>.json` with create-only / exact-same-content idempotence, reads the actual remote Git blob SHA back, and requires exact `taskId + taskBlobSha` result/status authority before success. Conflicting task bytes fail closed.

V3 segmented terminal authority remains in force; V7 does not stitch attempts or sessions and does not create a second capture-result truth system.

## Scheduling, retry, resume and terminal semantics

APScheduler is used only as commodity local timing infrastructure. Collector-owned authority remains outside scheduler memory.

- one active local batch runner
- serial capture execution (`maxConcurrentCaptures=1`)
- deterministic job identity
- bounded delay/interval
- no scheduler callback can manufacture Collector success
- cooperative cancellation cannot become clean `COMPLETE`
- unchanged-plan resume reconciles durable checkpoint with exact remote task/result/status authority
- a crash after task publication but before execution resumes the same exact task rather than duplicating capture
- stale local completion cannot override missing/conflicting remote authority
- default retry is disabled; when explicitly enabled, retry creates a new task identity and retains failed predecessor evidence
- `stopOnFailure=true` remains default; continue policy may execute later research steps but cannot hide earlier failure behind overall `COMPLETE`

## V5 / V4 / V6 integration retained

V5 storage pressure/capacity guard is consumed before each capture attempt; blocked capacity prevents task publication/start, and V7 does not archive/prune automatically to force progress.

Optional V4 catalog refresh uses the existing dataset catalog authority. It does not create a second catalog or alter V4 lifecycle/integrity semantics.

Optional V6 post-analysis remains opt-in and bounded, and must retain:

`researchOnly=true`

`semanticAuthority=false`

V6 analysis cannot promote a failed/partial capture or create gameplay/production semantics.

## CLI / local Windows boundary

Current CLI surface remains:

- `validate-plan`
- `show`
- `run`
- `resume`
- `status`
- `cancel`

The V7 dependency is installed from `requirements-collector-v7.txt`. Missing or wrong APScheduler version is a precise dependency failure.

This remains a local-first serial MVP. Real capture still uses the existing Windows Collector environment and authenticated GitHub CLI, with manual operator scene preparation when an existing task requests it. There is no daemon/server requirement added by V7 itself.

## Safety and lane isolation

Exact Collector safety contract remains:

```text
readOnly=true
writesGameMemory=false
inputInjection=false
```

Recovery V2 did not add game-memory writes, keyboard/gamepad injection, macros, Lua gameplay control, savestate stepping, AI actions, scene automation or Training Farm behavior.

No `product/alpha/**`, Alpha release/proof/live acceptance, Transport, Recorder, PYLAUNCH, OneClick, Training Farm, Stable-Retro, FBNeo, PPO/RL or 10-worker scheduling authority was modified.

## Maintained smoke / CI repair

Recovery V2 extended `.github/workflows/collector-python-smoke.yml` so the maintained smoke boundary now watches V7-owned code/tests/schema/dependency/example/docs, installs exact `APScheduler==3.11.3`, compiles `bridge/batch_acquisition.py`, runs V7 deterministic tests and CLI/schema/dependency checks, and includes V7 in the existing V3/V5/V6 source-authority and capture-guard wiring assertions.

The workflow retains:

`permissions: contents: read`

The successful run's token reported `Contents: read` and `Metadata: read`. No workflow writeback or mutable latest PASS receipt was introduced.

## Coherent V3–V7 self-check result

Exact successful GitHub Actions run:

- workflow: `Collector Python smoke check`
- run ID: `33650865968`
- run number: `16`
- event: `push`
- head SHA: `4eb4b33bd09cfaeeb6644110a59b3452c489ea9e`
- head tree: `19f96fa973fc608e367e66325731e1ec869a44bc`
- job ID: `100317219981`
- status: `completed`
- conclusion: `success`
- Python: `3.12.14`
- installed APScheduler: `3.11.3`

Executed regression boundary:

- V3 segmented implementation regressions: `15/15 PASS`
- V4 dataset catalog self-check: `20/20 PASS`
- V5 storage retention + Recovery regressions: `28/28 PASS`
- V6 segment-aware analysis reader self-check: `31/31 PASS`
- V7 reuse-first batch acquisition self-check: `20/20 PASS`

Total: `114/114 unittest PASS`.

Additional maintained checks passed:

- all selected Collector modules compile, including V7
- V6 CLI/result-schema contract
- V7 CLI/schema/dependency/direct-use contract
- example V7 plan canonical validation
- exact APScheduler `3.11.3` installed and matches code authority
- V7 upstream/license and Prefect `DEFER` assertions
- V7 strict safety schema and serial scheduling invariant
- current retained V4 evidence index: `33` records, `8` active reusable records
- V5 policy/schema health valid; policy SHA-256 `46017615b37d1ce739d3090eaedd130fcd54cf82122c1cfd0624164cf2a73703`
- immutable discovery / V3 segmented authority / V5 capture guard / V6 research-only / V7 batch wiring checks

The only workflow log warning was GitHub-hosted Actions' Node 20 deprecation compatibility notice for `actions/checkout@v4` / `actions/setup-python@v5`, which GitHub ran under Node 24. It did not fail any Collector step and is not a V7 correctness or safety defect.

## Historical claim authority

The original canonical claim:

`parallel/PM/DEDUP_CLAIMS/winkawaks.collector.v7.reuse-first-batch-acquisition-automation-lite.json`

is intentionally left unchanged as historical ACTIVE residue from the interrupted worker. Recovery V2 is the PM-authorized successor authority and supersedes that residue. Historical evidence is not rewritten to manufacture closure.

## Final verdict

**COMPLETE — WINKAWAKS COLLECTOR V7 REUSE-FIRST BATCH ACQUISITION AUTOMATION LITE — LOCAL SERIAL BATCH ORCHESTRATION COMPLETE**

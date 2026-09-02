# WinKawaks 10-Room Remote-Command Capture / Analysis Loop — PM Addendum

Status: **RECORDED OWNER REQUIREMENT — NOT YET AN IMPLEMENTATION STAGE**

Date: 2026-09-02

This addendum extends `parallel/PM/WINKAWAKS_10_ROOM_AUTOCAPTURE_PIPELINE_IDEA.md`.

## Owner intent

The long-term collector should be remotely steerable without repeatedly changing/releasing the client program.

The client remains a stable generic collector. What data is needed next is described by a small remote instruction file stored in GitHub. The client periodically fetches that instruction, validates it, shows a simple human-readable prompt, waits for Owner confirmation, then captures and uploads exactly the requested data.

AI then consumes only the newly uploaded dataset referenced by the instruction/result ledger, writes durable structured analysis, ACKs the exact input hashes, and the cleanup policy may delete analysed raw working data.

## Target operator workflow

```text
PM/AI decides what evidence is needed next
-> write/update one remote capture instruction in GitHub
-> local collector polls/fetches current instruction
-> validates instruction/version/hash
-> tray/console shows: "需要采集：<human description>，准备好后按回车"
-> Owner opens/arranges 1..10 rooms
-> Owner presses Enter
-> collector discovers eligible rooms and begins capture
-> per-room chunks are validated/compressed/hashed
-> automatic upload
-> upload manifest/result becomes durable
-> remote analysis queue marks exact dataset READY_FOR_ANALYSIS
-> AI analyses that dataset only
-> AI writes structured result + input hashes + coverage update
-> ANALYSED_ACKED
-> raw enters cleanup and may be deleted
-> next remote instruction can be issued
```

Owner should not need to manually select files, rename captures, upload files, tell AI which files are new, or remember which captures were already analysed.

## Remote instruction file

Prefer one small machine-readable control file, conceptually:

`collector/control/current_capture_request.json`

Example schema direction:

```json
{
  "schemaVersion": 1,
  "requestId": "CAPREQ-...",
  "state": "READY",
  "humanPromptZh": "开 10 个房间，保持敌人正常活动，准备好后按回车开始采集",
  "roomCountMin": 1,
  "roomCountMax": 10,
  "capture": {
    "mode": "raw_ram_chunked",
    "durationSeconds": 3600,
    "hz": 60,
    "chunkSeconds": 60
  },
  "requiredFieldsProfile": "wof-basecap-v1",
  "sceneFilter": null,
  "enemyFilter": null,
  "specialObservations": [],
  "readOnly": true,
  "ramWrites": 0,
  "inputInjection": false
}
```

The exact schema may evolve, but the principle is fixed: **change the remote instruction to change what is collected; do not require a new client build for ordinary collection-plan changes.**

## What can be adjusted remotely

The instruction should eventually be able to request, within the capabilities already implemented by the client:

```text
capture duration
sampling Hz
chunk duration
number of rooms accepted
which RAM/object field profile to retain
whole-session vs bounded event windows
specific stage/scene/wave tag when known
specific enemy type/slot cohort when observable
attack/state/target transition focus
pre/post-event time window
whether screenshots/video are requested as optional side evidence
whether repeated observations are required
minimum sample count / coverage target
stop conditions
upload destination/queue label
analysis recipe/profile to run after upload
```

If a requested field/profile is not supported by the installed collector version, the client must fail closed with `UNSUPPORTED_REQUEST` rather than silently collecting a different dataset.

## Client behavior

The stable client should:

1. poll/fetch the remote request at a bounded interval or on manual "check task" action;
2. pin `requestId + instruction blob/hash + schemaVersion` before Owner confirmation;
3. display only a concise Chinese instruction;
4. wait for explicit Enter/Start confirmation before the capture begins;
5. discover currently eligible local rooms only after confirmation;
6. bind each room to lifecycle-safe `roomId/roomGeneration`;
7. collect read-only data only;
8. chunk locally so a crash loses at most the current chunk, not the whole hour;
9. hash and validate each chunk before upload;
10. upload with exact `requestId`, room identity, capture interval, schema/profile and sha256;
11. create a final capture manifest listing every successfully uploaded chunk and every failed/missing room;
12. never mark the request capture-complete merely because the client process exited cleanly.

## Upload completion / analysis handoff

A request becomes `READY_FOR_ANALYSIS` only when a durable manifest exists with exact uploaded chunk hashes.

Conceptual manifest:

```text
requestId
instructionHash
collectorVersion
roomsObserved
chunks[]:
  captureId
  roomId
  roomGeneration
  startedAt
  endedAt
  sha256
  byteSize
  uploadObject/path
captureStatus
```

AI analysis must use this exact manifest rather than scanning arbitrary folders and guessing which files belong together.

## Automatic AI analysis

The remote request may carry an `analysisProfile`, for example:

```text
base_enemy_transition_mining
retarget_mining
enemy_attack_sequence_mining
rare_attack_coverage
specific_enemy_type_deep_dive
stage_wave_atlas_update
coverage_gap_check
```

After upload completion:

```text
READY_FOR_ANALYSIS
-> analyser claims requestId
-> reads exact manifest + unacked hashes only
-> produces structured result
-> updates atlas/catalog/coverage
-> writes ANALYSED_ACKED(input hashes, result id/commit)
-> raw cleanup becomes eligible
```

No re-analysis of already ACKed input hashes unless a new analysis-version/request explicitly asks for it.

## Cleanup rule

Raw cleanup remains fail-closed. Delete only after:

- exact input hashes were successfully analysed;
- structured result is durable;
- analysis version is recorded;
- `ANALYSED_ACKED` is durable;
- all required catalog/coverage updates have completed.

If analysis fails, times out, or produces an incomplete result, raw remains available for retry.

## Human experience target

The Owner-facing experience should be approximately:

```text
启动 Collector

[远端任务已获取]
今天需要：10 房基础状态/攻击采集，约 60 分钟。
请先把房间开好。
准备好后按 Enter 开始。

<Owner presses Enter>

自动发现 8/10 个可用房间
开始采集...
自动分片...
自动上传...
上传完成 480/480 chunks
本次任务已提交给 AI 分析。
```

After this point the Owner should not need to perform an analysis/upload operation manually.

## Architectural principle

Keep these responsibilities separate:

```text
Remote Git instruction = what evidence is wanted
Stable local client     = how supported evidence is safely collected
Upload manifest         = exactly what was obtained
AI analysis profile     = how the new dataset is analysed
Analysis ACK            = proof that raw can be cleaned
```

This allows future research needs to change by editing small remote instruction/analysis-profile files while keeping the local collector stable.

## Current decision

Record only. Do not interrupt Alpha V1 release work and do not implement this pipeline until PM explicitly promotes it to an implementation stage.

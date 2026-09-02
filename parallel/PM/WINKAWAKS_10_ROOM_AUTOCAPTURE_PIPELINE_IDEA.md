# WinKawaks 10-Room Auto-Capture / Auto-Analyze / Auto-Cleanup Pipeline — PM Idea Record

Status: **RECORDED PRODUCT/R&D DIRECTION — NOT YET AN IMPLEMENTATION STAGE**

Date: 2026-09-02

## Owner intent

Move local WOF / 三国志II discovery collection away from one-hour/manual batch handling toward an always-available 10-room pipeline.

Desired operator experience:

1. Owner opens up to 10 local WOF rooms/instances when available.
2. A local collector automatically discovers/attaches to the eligible rooms.
3. Each room continuously captures bounded read-only RAM data into small independent chunks.
4. Chunks are automatically validated, uniquely identified, compressed and uploaded.
5. AI continuously consumes only new/unanalysed chunks and produces durable structured analysis/atlas/coverage results.
6. After a chunk has been successfully analysed and its durable result is committed/acknowledged, the raw analysed chunk is automatically removed from the active data queue/storage.
7. Owner should not need to manually upload, rename, sort, or repeatedly tell AI which chunk was already analysed.

Target human workflow:

```text
每天有房间时：
开 1~10 个房间
-> 启动/保持 Auto Collector
-> 正常让房间运行
-> 自动采集
-> 自动上传
-> AI 自动分析新增数据
-> 分析成功后自动清理已分析 raw
```

## Core architecture direction

```text
1..10 WOF rooms
    ↓
room discovery / stable room identity
    ↓
read-only collectors
    ↓
small immutable capture chunks
    ↓
local validation + compression + sha256
    ↓
upload queue
    ↓
remote incoming/raw queue
    ↓
AI incremental analyser
    ↓
structured durable results / atlas / coverage gaps
    ↓
analysis ACK bound to exact input sha256
    ↓
automatic raw cleanup
```

## Required data lifecycle

Every chunk must have a unique immutable identity, at minimum:

```text
captureId
roomId / roomGeneration
startedAt / endedAt
duration / hz
sha256
byteSize
schemaVersion
collectorVersion
readOnly=true
ramWrites=0
inputInjection=false
analysisState
```

Suggested states:

```text
CAPTURING
READY_TO_UPLOAD
UPLOADED
QUEUED_FOR_ANALYSIS
ANALYSING
ANALYSED_ACKED
CLEANUP_PENDING
CLEANED
FAILED_RETRYABLE
QUARANTINED
```

Raw deletion is allowed only after all of the following are true:

1. exact raw `sha256` was successfully read by the analyser;
2. analysis completed successfully;
3. a durable structured result exists and references the exact input captureId + sha256;
4. coverage/catalog/atlas bookkeeping has been updated as required;
5. an explicit `ANALYSED_ACKED` state is durable;
6. cleanup operation itself is idempotent and records what was removed.

If any condition is missing, raw must remain retained/retryable rather than silently deleted.

## Important Git storage caveat

Normal Git commits retain deleted file contents in repository history. Therefore "upload raw to normal Git commits, then delete after analysis" does **not** actually reclaim repository history size.

Before implementation, storage must be chosen so analysed raw can truly expire. Preferred directions to evaluate:

- a dedicated rotating data transport/storage layer rather than permanent normal Git history;
- GitHub artifact/release/object-style temporary storage with bounded retention where compatible with AI consumption;
- a dedicated data repository/branch with an explicitly designed rotation/compaction policy;
- local retained queue + durable compact derived results in `wof-ai-private`.

The durable long-term repository should preferentially retain **derived structured knowledge**, not every raw frame forever.

## AI incremental-analysis rule

AI should not repeatedly rescan all historical captures.

Maintain a durable ledger keyed by exact input hash:

```text
sha256 -> analysisResultId -> resultBlob/resultCommit -> status
```

Only `UPLOADED/QUEUED_FOR_ANALYSIS` hashes without a valid prior ACK are analysed.

Outputs should accumulate reusable compact knowledge such as:

- enemy type census;
- state/action/attack transitions;
- target/retarget observations;
- ordered sequence candidates;
- stage/scene/wave atlas;
- rare attack coverage;
- coverage gaps;
- candidate rules needing Browser prospective validation;
- confidence/sample counts/provenance.

Once this durable knowledge exists, raw can be treated as expendable working data under the cleanup policy above.

## 10-room isolation requirements

The future collector must not mix rooms.

Each room needs lifecycle-safe identity/generation. A restarted/replaced room must produce a new generation even if it reuses the same numeric slot/port/process location.

Per-room capture must remain isolated so that:

- one room crash does not stop the other nine;
- duplicate chunks are hash-deduplicated;
- stale room generations cannot append to a new room generation;
- upload retry is per chunk;
- analysis/cleanup ACK applies only to the exact capture hash;
- no game RAM writes or gameplay input injection are introduced by the collection pipeline.

## Initial implementation preference

Do not begin with one giant 10-room monolith. Recommended progression when this is promoted to an implementation stage:

```text
1 room automatic chunking/upload/ACK/cleanup
-> 2 rooms isolation
-> 4 rooms
-> 8 rooms
-> 10 rooms
```

The operator-facing target is still one-click 10-room collection; the staged rollout is only for deterministic engineering validation.

## Relation to existing BASECAP workflow

This direction supersedes the manual operational burden, not the data-authority boundary.

WinKawaks remains discovery/research evidence. Browser/WOF remains the required prospective validation / production proof lane before discovered candidates are promoted into production behavior.

Do not treat local multi-room raw volume as Browser production proof.

## Current decision

Record this as a future R&D/collector architecture requirement only. Do not interrupt Alpha V1 release-critical work to implement it unless PM explicitly promotes it to a stage.

Owner's desired end state:

> 有房间就开 1~10 个，系统自己采、自己上传，AI 只分析新数据；分析成功并落出结果后自动删除已经分析过的 raw，只长期保留有用的结构化知识和索引。

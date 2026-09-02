# WinKawaks 10-Room Dynamic Room Hotplug — PM Addendum

Status: **RECORDED OWNER REQUIREMENT — NOT YET AN IMPLEMENTATION STAGE**

Date: 2026-09-02

This addendum extends the recorded 10-room auto-capture / remote-command collector direction.

## Owner-facing workflow

The target human workflow is explicitly:

```text
双击 CMD
-> 采集器读取/确认远端任务
-> 按一次 Enter 进入持续采集模式
-> Owner 去开房间
-> 挂着
```

The Owner does **not** need to wait until all rooms exist before pressing Enter.

After Enter, the collector enters a long-lived discovery/capture loop and continuously discovers eligible WinKawaks/WOF rooms as they appear.

## Dynamic room count requirement

Room count is dynamic from `0..10` during the whole run.

The following must be normal supported behavior and must not stop or restart the collector service:

- start with zero rooms, then open rooms later;
- 1 room becomes 2/3/.../10 rooms;
- any room closes while other rooms keep running;
- room count decreases from 10 to any lower number;
- a previously closed room is reopened;
- a new WinKawaks process reuses an old numeric slot/PID/port-like locator;
- one room crashes/hangs while other rooms remain healthy;
- rooms are opened and closed repeatedly during a long capture day.

The collector must not require another Enter for ordinary room joins/leaves after the initial start confirmation.

## Required room lifecycle model

Each live room must be tracked independently with lifecycle-safe identity:

```text
roomId
roomGeneration
process/runtime identity
firstSeenAt
lastSeenAt
state
activeChunkId
lastUploadedChunk
```

A closed/restarted/replaced room must receive a new `roomGeneration` even if it reuses an old locator. Stale data from a previous generation must never append to a new generation.

Suggested per-room states:

```text
DISCOVERED
ATTACHING
CAPTURING
TEMP_UNAVAILABLE
CLOSED
REPLACED
ERROR_RETRYABLE
```

## Hot-add behavior

When a new eligible room appears after collection has already started:

```text
periodic discovery notices new room
-> validate WOF/runtime identity
-> allocate new roomGeneration
-> begin a fresh capture chunk boundary
-> join normal upload cycle
```

No global restart and no interruption to existing rooms.

## Hot-remove behavior

When a room disappears/closes:

```text
room disappears
-> finalize currently valid partial chunk if policy permits, otherwise discard/quarantine only that partial chunk
-> mark exact roomGeneration CLOSED
-> stop polling that room
-> keep all other rooms capturing and uploading
```

A room closing must never terminate the entire collection run.

## Isolation requirement

Every room operates as an isolated collection lane under one CMD supervisor.

At minimum:

- per-room capture state;
- per-room chunk rotation;
- per-room upload retry;
- per-room error/reconnect handling;
- per-room generation identity;
- per-room progress counters;
- no cross-room frame mixing;
- no one-room crash taking down the other rooms.

## CMD status target

The single CMD window should remain simple and continuously show useful changes, for example:

```text
[WOF采集器] 持续采集模式已启动。现在可以打开/关闭房间。
[WOF采集器] 当前在线房间：0/10

[12:01:04] + 发现房间 R01，开始采集
[12:01:11] + 发现房间 R02，开始采集
[12:03:00] R01 chunk-001 上传完成
[12:03:05] R02 chunk-001 上传完成
[12:18:22] - R01 已关闭；其它房间继续
[12:19:08] + 新房间 R03/generation-1 加入
[12:20:31] + R01/generation-2 重新加入

当前在线：3/10
累计上传：...
AI待分析：...
```

## Stop behavior

The collector remains running until the Owner explicitly closes/stops the collector itself.

Closing game rooms is not a stop command.

The service should be able to sit at `0/10` rooms indefinitely while still polling the remote instruction and local room discovery loop.

## Safety boundary

Dynamic discovery must preserve the existing collection safety intent:

- read-only observation;
- `ramWrites=0`;
- no gameplay input injection;
- no automatic gameplay/control actions merely to keep rooms alive;
- failure of one room fails closed for that room only;
- remote task changes cannot silently attach unsupported runtimes.

## Final owner requirement

> 双击 CMD -> 回车 -> 去开房间 -> 挂着。房间后开、先开、关闭、增加、减少、重开都不影响采集器本身；在线的房间自动采，消失的房间自动退出，新出现的房间自动加入，直到我主动停止采集器。

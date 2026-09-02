# WinKawaks / Browser 10-Room Tampermonkey Auto-Room Lifecycle — PM Addendum

Status: **RECORDED OWNER REQUIREMENT — NOT YET AN IMPLEMENTATION STAGE**

Date: 2026-09-02

This extends the previously recorded 10-room dynamic capture direction.

## Owner intent

Combine the long-running CMD collector with a browser/Tampermonkey room manager so the Owner does not manually maintain room count.

Target operator experience:

```text
双击 CMD Collector
-> 回车授权本次采集会话
-> 油猴/浏览器房间管理器自动补房
-> Collector 自动发现当前可采房间
-> 持续采集 / 分片 / 上传
-> 房间关闭、增加、减少都不影响其他房间
-> 空房自动关闭
-> 当可用房间低于目标值时自动补开新房
-> 一直挂着直到 Owner 主动停止
```

## Separation of responsibilities

```text
Tampermonkey / browser room manager
  = open/close browser game rooms and maintain desired room population

CMD Collector
  = discover eligible live rooms, bind lifecycle-safe identity, read-only capture, chunk, upload

Remote Git instruction
  = what data is wanted and target room policy

AI analyser
  = analyse new uploaded manifests, ACK exact hashes, update structured knowledge, allow cleanup
```

The collector must not depend on any fixed set of room tabs existing at startup.

## Dynamic room lifecycle

Desired room pool is hot-pluggable from 0..10 rooms.

Requirements:

- New eligible room appears -> auto-discover -> assign new `roomId/roomGeneration` -> start capture without restarting CMD.
- Existing room disappears/crashes/closes -> finalize current chunk if valid, stop only that room lane, other rooms continue unaffected.
- Same tab/slot/URL later reused by a new game runtime -> must get a new generation; never append to the prior room generation.
- Room count may rise/fall at any time; no global capture reset.
- If all rooms disappear, collector remains alive in waiting mode and resumes when new rooms appear.

## Tampermonkey room-manager behavior

The userscript should maintain a target room policy supplied by the current remote instruction, for example:

```text
minRooms: 1
maxRooms: 10
targetRooms: 10
autoOpen: true
autoCloseEmpty: true
```

Conceptual behavior:

```text
periodically inspect managed room tabs
-> classify each as STARTING / ACTIVE / EMPTY / CLOSED / ERROR
-> ACTIVE count below target -> open replacement room(s), bounded by maxRooms
-> EMPTY for a stable grace period -> close that room only
-> CLOSED/ERROR -> forget that generation and optionally replace
-> never close a room merely because one transient poll fails
```

`EMPTY` must be based on an explicit observable room/game criterion defined by the implementation (for example no active human/game occupant state for a bounded grace window). Do not use a single DOM glitch or one missed heartbeat as sufficient authority to close a room.

## Empty-room close safety

Before auto-close:

1. room identity/generation is current;
2. empty condition has remained true for a configured grace period;
3. no current valid capture chunk is being silently discarded;
4. collector is informed/able to finalize or mark the partial chunk appropriately;
5. close action targets only the exact current managed tab/room generation.

If empty status is ambiguous, keep the room open rather than closing a potentially useful live room.

## Auto-open safety

Auto-open must be bounded:

- never exceed configured `maxRooms`;
- rate-limit replacement/open attempts;
- do not create runaway tabs if the site fails to initialize;
- each opened tab gets a locally tracked generation/token;
- retry/backoff on repeated room-open failure;
- no gameplay input automation is required for this room-lifecycle layer unless separately authorized later.

## Collector independence

The CMD Collector must treat room lifecycle as external and unreliable. It should continue to work even if the userscript is disabled:

```text
userscript present -> rooms can be auto-maintained
userscript absent  -> manually opened rooms are still discovered and captured
```

This prevents browser-room automation failures from taking down the data collector.

## Desired unattended loop

```text
Remote Git request READY
-> Owner starts CMD and presses Enter once
-> Tampermonkey keeps room pool near target count
-> Collector hot-plugs rooms as they come/go
-> per-room immutable chunks upload continuously
-> AI analyses only new manifests/hashes
-> ANALYSED_ACKED
-> eligible raw cleanup
-> remote request may change collection/analysis policy later
```

Owner should be able to leave this running for long periods without manually replacing empty rooms.

## Current decision

Record only. Do not interrupt Alpha V1 release-critical work. Promote this to implementation only when PM explicitly schedules the 10-room collection pipeline.

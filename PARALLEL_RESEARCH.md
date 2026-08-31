# WOF Project — Parallel Research Topology

Updated: 2026-08-31

## Purpose

The WOF project intentionally runs one Browser/Web production mainline plus several independent WinKawaks discovery lanes in parallel. These lanes share the Collector as a data-acquisition service but do not share production-rule authority.

The current Browser/Web mainline is whatever `WOF_AI_HANDOFF.md` marks as `Current next` (currently WOF-046; WOF-045 is completed). Future WOF-0xx mainlines inherit the same isolation rules automatically.

## Active lanes

```text
MAINLINE  = Browser/Web Future Danger production research
GEO-*     = WinKawaks player geometry / coordinates / left-right / top-bottom research
EFIELD-*  = WinKawaks enemy 0xE0 field-atlas research
RAWMINE-* = generic WinKawaks raw diff / transition / offset-ranking research
```

All four are allowed to progress concurrently.

## Hard isolation from the mainline

Parallel lanes MUST NOT:

- modify, advance, replace, or rewrite the current WOF mainline coordinator/validator;
- change existing production-shadow rules or their Browser semantics;
- promote a WinKawaks-local offset directly into a Browser/WASM production rule;
- treat local Collector evidence as final Browser production proof;
- write game memory or inject automatic game input.

The Browser/Web mainline remains authoritative for production-context validation and promotion.

## Single-writer file ownership

Parallel AI chats MUST NOT co-edit the same research file.

Write ownership is fixed as follows:

```text
MAINLINE / project controller only:
  WOF_AI_HANDOFF.md
  WOF_AI_CURRENT_FRONTIER.md
  WOF_AI_MASTER_PROGRESS.md
  COLLECTOR_ROUTING.md
  PARALLEL_RESEARCH.md

GEO lane only:
  parallel/GEO/**

EFIELD lane only:
  parallel/EFIELD/**

RAWMINE lane only:
  parallel/RAWMINE/**
```

A parallel lane may READ files owned by another lane, but MUST NOT edit them. Cross-lane findings are consumed by reading the owning lane's artifacts/results.

No parallel lane may use a generic shared `latest.md`, `frontier.md`, `result.json`, or similarly collision-prone path outside its assigned directory.

Collector-side task/result files are already isolated by unique task ID. Every lane MUST use its own prefix:

```text
GEO-
EFIELD-
RAWMINE-
```

Therefore queue/status/result ownership is naturally separated:

```text
tasks/queue/GEO-*.json
status/by_task/GEO-*.json
results/by_task/GEO-*.json

tasks/queue/EFIELD-*.json
status/by_task/EFIELD-*.json
results/by_task/EFIELD-*.json

tasks/queue/RAWMINE-*.json
status/by_task/RAWMINE-*.json
results/by_task/RAWMINE-*.json
```

If a lane discovers that a file it intends to write is owned by another lane or has been concurrently changed, it must stop that write, re-read the repository state, and write only inside its own namespace. It must never overwrite another lane's work to resolve a conflict.

## Collector concurrency model

GEO, EFIELD, RAWMINE, and any other research producers may submit Collector tasks concurrently under:

```text
tasks/queue/<taskId>.json
```

The local Collector owns exactly one WinKawaks runtime and executes captures strictly serially. Therefore AI threads are concurrent producers, while emulator capture ownership is serialized and isolated.

Per-task authority remains:

```text
status/by_task/<taskId>.json
results/by_task/<taskId>.json
```

Consumers must match `taskId + taskBlobSha` before accepting a result.

## Operator-gated work

Prefer unattended collection whenever possible. A lane may request `operatorGate.required=true` only when a specific scene is genuinely required. The operator prepares the requested scene and runs `READY_WOF_TASK.bat`; later queued tasks must not jump ahead.

## Cross-lane cooperation

Parallel lanes cooperate through GitHub artifacts/results, not by asking the operator to copy logs, JSON, hashes, or raw data between chats.

RAWMINE may analyze raw captures produced for GEO or EFIELD when the task/result identity is clear. GEO and EFIELD may consume RAWMINE candidate rankings as discovery hints. Any finding that could affect Future Danger must still return to Browser/Web for independent prospective validation before promotion.

## `继续` behavior for parallel AI chats

When the operator sends only `继续`, each parallel AI should:

1. inspect its own latest GitHub task/result/frontier;
2. analyze the previous result;
3. decide and submit the next bounded Collector task when useful;
4. continue within its own lane;
5. avoid touching the Browser/Web mainline unless explicitly reassigned by the project controller.

If human game操作 is not required, do not interrupt the operator merely to relay machine-readable data.

## Precedence

For current production milestone/state, `WOF_AI_HANDOFF.md` is authoritative.
For data-source choice and Collector use, `COLLECTOR_ROUTING.md` is authoritative.
For parallel ownership/isolation, this file is authoritative.
For Collector task/result mechanics, `ouyong520/wof-winkawaks-bridge/docs/COLLECTOR_V1_CONTRACT.md` is authoritative.

# WOF Project — Parallel Research Topology

Updated: 2026-09-01

## Purpose

The WOF project intentionally runs one Browser/Web production mainline plus several independent WinKawaks discovery lanes in parallel. These lanes share the Collector as a data-acquisition service but do not share production-rule authority.

The current Browser/Web mainline is whatever `WOF_AI_HANDOFF.md` marks as `Current next`. Future WOF-0xx mainlines inherit the same isolation rules automatically.

## Active lanes

```text
MAINLINE  = Browser/Web Future Danger production research
BASECAP-* = shared labeled WinKawaks baseline-capture dataset
GEO-*     = WinKawaks player geometry / coordinates / left-right / top-bottom research
EFIELD-*  = WinKawaks enemy 0xE0 field-atlas research
RAWMINE-* = generic WinKawaks raw diff / transition / offset-ranking research
```

All lanes are allowed to progress concurrently as research producers. Collector execution against one WinKawaks instance remains serialized.

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

BASECAP lane only:
  parallel/BASECAP/**

GEO lane only:
  parallel/GEO/**

EFIELD lane only:
  parallel/EFIELD/**

RAWMINE lane only:
  parallel/RAWMINE/**
```

A parallel lane may READ files owned by another lane, but MUST NOT edit them. Cross-lane findings are consumed by reading the owning lane's artifacts/results.

No parallel lane may use a generic shared `latest.md`, `frontier.md`, `result.json`, or similarly collision-prone path outside its assigned directory.

Collector-side task/result files are isolated by unique task ID. Every lane MUST use its own prefix:

```text
BASECAP-
GEO-
EFIELD-
RAWMINE-
```

Therefore queue/status/result ownership is naturally separated:

```text
tasks/queue/BASECAP-*.json
status/by_task/BASECAP-*.json
results/by_task/BASECAP-*.json

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

A task ID is an immutable dataset identity and MUST NEVER be reused for a later capture. If a capture must be repeated or corrected, create a new task ID and mark the older capture as superseded in the owning lane's catalog rather than overwriting it.

If a lane discovers that a file it intends to write is owned by another lane or has been concurrently changed, it must stop that write, re-read the repository state, and write only inside its own namespace. It must never overwrite another lane's work to resolve a conflict.

## Shared labeled baseline captures

`BASECAP` exists to prevent GEO, EFIELD, RAWMINE, or future local research chats from repeatedly collecting the same basic scenes.

Authoritative catalog:

```text
parallel/BASECAP/BASE_CAPTURE_CATALOG.md
```

Before submitting a new Collector task, every local research lane SHOULD first inspect this catalog and reuse an existing retained capture when all material conditions already match the question.

A reusable baseline capture should normally use:

```text
uploadRawStream = true
```

so the raw artifact is available through GitHub at:

```text
captures/<taskId>.jsonl.gz
```

Each catalog entry must state at minimum:

```text
captureId / taskId
raw artifact path
capture date/time
ROM/game/session identity when known
player occupancy/configuration
scene/setup before READY
operator action during capture
duration + Hz
object layout / bytes per frame
what variable was intentionally changed
what variables were intentionally held stable
intended reuse questions
known confounders / limitations
status: VALID / SUPERSEDED / INVALID
```

A raw file without a reliable scene label must not be promoted to a reusable baseline merely because its bytes look useful.

If an existing baseline answers the question, reuse it instead of asking the operator to repeat the scene. Only collect a new baseline when the existing dataset lacks a required condition, has a known confounder, or a specific discriminator is needed.

BASECAP only owns acquisition metadata and reusable labeled datasets. It does not own GEO/EFIELD semantic conclusions and must not rename fields on their behalf.

## Collector concurrency model

BASECAP, GEO, EFIELD, RAWMINE, and any other research producers may submit Collector tasks concurrently under:

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

For reusable BASECAP captures, the gate instructions must be precise enough that another researcher can understand exactly what the operator did. `READY_WOF_TASK.bat` is a one-task release signal, not a persistent mode.

## Cross-lane cooperation

Parallel lanes cooperate through GitHub artifacts/results, not by asking the operator to copy logs, JSON, hashes, or raw data between chats.

RAWMINE may analyze raw captures produced for BASECAP, GEO, or EFIELD when the task/result identity is clear. GEO and EFIELD may consume BASECAP datasets and RAWMINE candidate rankings as discovery evidence. BASECAP may index existing GEO/EFIELD captures as reusable only when their scene conditions are recoverable from authoritative task/result/artifact metadata; it must not invent missing labels.

Any finding that could affect Future Danger must still return to Browser/Web for independent prospective validation before promotion.

## `继续` behavior for parallel AI chats

When the operator sends only `继续`, each parallel AI should:

1. inspect its own latest GitHub task/result/frontier;
2. inspect the BASECAP catalog before requesting duplicate basic data;
3. analyze the previous result;
4. decide and submit the next bounded Collector task only when useful;
5. continue within its own lane;
6. avoid touching the Browser/Web mainline unless explicitly reassigned by the project controller.

If human game操作 is not required, do not interrupt the operator merely to relay machine-readable data.

## Precedence

For current production milestone/state, `WOF_AI_HANDOFF.md` is authoritative.
For data-source choice and Collector reuse, `COLLECTOR_ROUTING.md` is authoritative.
For parallel ownership/isolation, this file is authoritative.
For Collector task/result mechanics, `ouyong520/wof-winkawaks-bridge/docs/COLLECTOR_V1_CONTRACT.md` is authoritative.

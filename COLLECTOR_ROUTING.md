# WOF research data-source routing

## Two authoritative roles

The original WOF project may use two complementary capture sources. They must not be silently merged.

### Browser/Web capture

Use Browser/Web when the research question depends on the real online/browser environment:

```text
real online rooms
multi-room behavior
1P / 2P / 3P coverage in production context
Browser Worker / WASM field semantics
final prospective validation before promoting a rule
production-context false-positive / false-negative evidence
```

Browser/Web remains the authority for Browser/WASM runtime semantics and final production-context rule validation.

### WinKawaks Collector

Use `ouyong520/wof-winkawaks-bridge` for fast, repeatable, high-frequency local runtime evidence:

```text
raw RAM snapshots
~60 Hz bounded raw streams
field-change discovery
transition/diff analysis
large local sample acquisition
repeated scene experiments
quick checks of whether a candidate field really changes
```

The collector is a research accelerator, not an AI/rule implementation.

## Default routing rule

```text
Need to discover / inspect / diff / collect lots of raw RAM quickly?
-> WinKawaks Collector first.

Need to prove a finding in the real online/browser environment or promote it into a production rule?
-> Browser/Web validation.
```

Standard flow:

```text
Browser observation/question
-> local WinKawaks high-speed evidence when useful
-> candidate interpretation
-> Browser/Web prospective validation
-> only then promote to production conclusion/rule
```

## Reuse before recapture

Before creating a new WinKawaks Collector task, first check the shared labeled baseline catalog:

```text
parallel/BASECAP/BASE_CAPTURE_CATALOG.md
```

If a retained capture already matches the required scene, controlled variable, player configuration, sampling rate, and other material conditions, reuse that capture rather than asking the operator to repeat the same collection.

The preferred local-discovery flow is:

```text
research question
-> inspect BASECAP catalog
-> reuse matching retained raw if available
-> run GEO / EFIELD / RAWMINE analysis against that capture
-> only create a new capture for a missing condition or explicit discriminator
```

Reusable baseline data should normally be collected with:

```json
"uploadRawStream": true
```

so it remains available at the immutable task-specific path:

```text
captures/<taskId>.jsonl.gz
```

Collector artifacts are task-specific. A new unique `taskId` produces a new task/result/raw identity rather than intentionally replacing an older capture. Research producers MUST NEVER reuse an old task ID for a new dataset. If a scene must be repeated, use a new ID and mark the old catalog entry `SUPERSEDED` when appropriate.

Every reusable capture must be labeled with enough acquisition metadata to make later reuse safe. At minimum record:

```text
captureId / taskId
raw path
capture time
ROM/game/session identity when known
player occupancy/configuration
scene before capture / before READY
operator action during the burst
duration + Hz
object layout / bytes per frame
intentional changed variable
intentional held-stable variables
intended research questions
known confounders / limitations
VALID / SUPERSEDED / INVALID
```

Do not infer a missing scene label from raw bytes alone. A capture with uncertain acquisition conditions may still be useful for exploratory analysis, but it is not a canonical reusable baseline.

## Frozen Collector v1 consumer contract

```text
repo: ouyong520/wof-winkawaks-bridge
contract: docs/COLLECTOR_V1_CONTRACT.md
delivery: docs/COLLECTOR_V1_DELIVERY.md
queue: tasks/queue/<taskId>.json
status: status/by_task/<taskId>.json
result: results/by_task/<taskId>.json
latest compatibility pointer: results/collector_task_remote_result_latest.json
```

Supported v1 actions:

```text
capture_raw_snapshot
capture_raw_burst
```

Multiple AI/research threads may submit tasks concurrently. The local Collector owns one WinKawaks runtime and executes tasks strictly serially; producers must not assume concurrent emulator ownership.

For scene-specific tasks, use an operator gate. The Collector publishes the active waiting task, and the operator prepares that scene before releasing it with `READY_WOF_TASK.bat`. Later queued tasks do not jump ahead.

Consumers must match both `taskId` and `taskBlobSha` before treating a per-task result as belonging to their request.

## Raw retention

Default full raw data remains local:

```text
diagnostics/latest/collector_task_stream_<taskId>.jsonl
```

When full frames are genuinely needed by this project, request:

```json
"uploadRawStream": true
```

The collector returns:

```text
captures/<taskId>.jsonl.gz
```

For reusable BASECAP datasets, prefer `uploadRawStream=true` so future AI chats can consume the exact same capture without asking the operator to recapture it. Collector v1 still applies its per-capture compressed GitHub size limit from the contract.

## Source namespace rule

Never assume Browser/WASM offsets equal WinKawaks normalized offsets.

Current examples:

```text
Browser enemy target selector: +0x7E
WinKawaks normalized canonical selected-player reference: +0x6D
```

A local WinKawaks discovery may motivate a Browser test, but does not by itself prove the same numeric field or semantic contract exists in Browser/WASM.

## Runtime operation

Collector runtime does not require AI. When local collection is requested, the operator uses:

```text
START_WOF_COLLECTOR.bat
READY_WOF_TASK.bat   # only when the active task requests scene preparation
STOP_WOF_COLLECTOR.bat
```

The old development-time Codex/Luna watcher is not part of the delivered runtime.

AI/research logic decides what evidence to request and how to interpret it; the local collector performs only mechanical read-only capture and handoff.

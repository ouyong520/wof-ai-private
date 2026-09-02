# WOF research data-source routing

Project-wide authority boundary:

`RUNTIME_DATA_SOURCE_BOUNDARIES.md`

## Collector project status — independent non-blocking side lane

WinKawaks Collector / Data Acquisition Infrastructure is an **independent R&D side-lane project**.

It may continue development, recovery, self-check, module-level QA, dataset tooling and acquisition automation in parallel with the rest of the WOF program, but it is **not part of the Alpha V1 release-critical path unless Owner explicitly changes that policy in a later PM authority document**.

Hard project-management rule:

```text
Collector incomplete / ACTIVE / BLOCKED / awaiting QA
!= Alpha V1 release blocker
!= reason to stop bounded real Browser/WOF acceptance
!= reason to stop or delay Training Farm work
!= reason to stop or delay the current 10-worker training lane
```

Collector work must not modify or destabilize the Alpha V1 release/runtime surface merely to make Collector development easier. In particular, Collector tasks must not modify:

```text
product/alpha/**
Alpha danger rules or target semantics
Browser/WOF production projection authority
Transport
Recorder
PYLAUNCH
OneClick packaging
Alpha acceptance / release proof tooling
```

Collector work must also remain operationally and architecturally separate from Training Farm / automated training. It must not modify or take ownership of:

```text
training/farm/** runtime semantics
Stable-Retro / FBNeo training adapters
PPO / RL / policy code
10-worker scheduling
training action injection
savestate-search control logic
```

The current Training Farm / 10-worker lane may continue while Collector development is incomplete. Repository-only Collector development and self-checks should proceed independently when they do not materially contend for the same local machine resources.

The only operational caveat is physical-resource contention on the same machine: a critical/canonical long-duration WinKawaks capture may require temporarily pausing or capping a heavy Training Farm fleet to protect capture cadence and data quality. That is a **runtime scheduling concern only**, not a project dependency and not a release gate.

Collector remains a read-only observation system:

```text
readOnly=true
writesGameMemory=false
inputInjection=false
```

Any future feature that would require Collector itself to play the game, inject gameplay input, become an AI policy runtime, or act as Training Farm is out of scope unless Owner creates a separate explicit project lane.

## Three authoritative roles

The WOF project uses three complementary runtime/data sources. They must not be silently merged, and numeric offsets/runtime authority do not automatically transfer between them.

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
~60 Hz or higher bounded raw streams
long-session segmented raw capture
field-change discovery
transition/diff analysis
large local sample acquisition
repeated scene experiments
quick checks of whether a candidate field really changes
```

The Collector answers primarily: **what is actually happening in this real local WinKawaks runtime?**

The Collector is a research accelerator and observation system, not an AI/rule implementation or automated gameplay engine. Its default safety boundary remains read-only, no game-memory writes and no input injection.

### Training Farm / Stable-Retro + FBNeo

Use `training/farm/**` for isolated automated experiments where the research question requires trying actions rather than only observing them:

```text
reset / step / read_ram
save_state / load_state
savestate fork search
one state -> many independent action branches
automated action-result experiments
trajectory generation
branch scoring
search-teacher data
future 1 -> 2 -> 4 -> 8 -> 10 worker scaling
```

Training Farm answers primarily: **from this state, what happens if many different actions are tried automatically?**

Training Farm automation belongs only to the isolated emulator/training environment. It does not authorize automated input in Browser V1 or the live WinKawaks Collector.

## Default routing rule

```text
Need to discover / inspect / diff / collect lots of real WinKawaks raw RAM quickly?
-> WinKawaks Collector first.

Need to automatically try actions / fork savestates / generate action-result trajectories?
-> Training Farm.

Need to prove a finding in the real online/browser environment or promote it into a production rule?
-> Browser/Web validation.
```

Typical flows:

```text
Browser observation/question
-> local WinKawaks high-speed evidence when useful
-> candidate interpretation
-> Browser/Web prospective validation
-> only then promote to production conclusion/rule
```

and, for future movement/policy research:

```text
real gameplay/research question
-> Collector for controlled observation / semantic calibration
-> Training Farm for automated counterfactual action exploration
-> candidate policy / route / model
-> bounded Browser/product validation when the conclusion is intended for production
```

No step implies automatic cross-source offset equivalence.

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
source namespace
captureId / taskId
raw path
capture time
ROM/game/session identity when known
player occupancy/configuration
scene before capture / before READY
operator action during the burst/session
duration + Hz
object layout / bytes per frame
intentional changed variable
intentional held-stable variables
intended research questions
known confounders / limitations
VALID / SUPERSEDED / INVALID
```

Do not infer a missing scene label from raw bytes alone. A capture with uncertain acquisition conditions may still be useful for exploratory analysis, but it is not a canonical reusable baseline.

## Collector consumer contract

Current stable v1 consumer contract remains:

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

Collector V3 long-session segmented capture is a forward development lane. Until its contract is completed and adopted, consumers must not pretend the v1 frozen contract already includes V3 actions.

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

Hard rule:

```text
browser-wasm
winkawaks
stable-retro-fbneo
```

are different source namespaces.

Never assume Browser/WASM offsets equal WinKawaks normalized offsets or Stable-Retro/FBNeo-visible CPS offsets.

Current example:

```text
Browser enemy target selector: +0x7E
WinKawaks normalized canonical selected-player reference: +0x6D
```

Therefore:

```text
Browser offset
!= automatically WinKawaks offset
!= automatically Stable-Retro/FBNeo offset
```

A local WinKawaks discovery may motivate a Browser test or Training Farm calibration, but does not by itself prove the same numeric field or semantic contract exists in those runtimes.

Cross-source semantic mappings require explicit evidence/calibration and must retain provenance.

## Collector vs Training Farm overlap

Some generic infrastructure may be reusable across both lanes:

- SHA/integrity helpers;
- dataset catalog concepts;
- structured metadata vocabulary;
- generic transition/diff/statistical analysis;
- experiment/trial grouping;
- source-agnostic trajectory envelopes.

Do not build two incompatible generic stacks when one explicit source-aware abstraction can be reused.

But source adapters, runtime/session authority, offsets, lifecycle identity and action permissions remain separate.

Preferred pattern:

```text
common analyzer
  <- winkawaks adapter
  <- stable-retro-fbneo adapter
```

Forbidden pattern:

```text
one generic WOF RAM reader that assumes all offsets are identical
```

## Same-machine runtime resource rule

Until measurements prove isolation is safe, do not run a heavy 8/10-worker Training Farm workload at the same time as an important long-duration WinKawaks Collector capture.

Reason: Training Farm can materially consume CPU, RAM, disk I/O, scheduler and thermal budget, while canonical Collector sessions depend on stable sampling cadence and low read error/jitter.

Default operating sequence:

```text
critical/canonical Collector capture
-> pause or cap heavy Training Farm fleet
-> capture completes
-> resume Training Farm
```

This is only a same-machine resource scheduling precaution. It does **not** make Collector a dependency of Training Farm or Training Farm a dependency of Collector, and it does not make either lane a blocker for Alpha V1.

Repository-only development/self-checks may proceed in parallel when they do not materially load the local runtime.

## Runtime operation

Collector runtime does not require AI. When local collection is requested, the operator uses:

```text
START_WOF_COLLECTOR.bat
READY_WOF_TASK.bat   # only when the active task requests scene preparation
STOP_WOF_COLLECTOR.bat
```

The old development-time Codex/Luna watcher is not part of the delivered runtime.

AI/research logic decides what evidence to request and how to interpret it; the local collector performs only mechanical read-only capture and handoff.

For complete project-wide runtime/data boundaries, always defer to:

`RUNTIME_DATA_SOURCE_BOUNDARIES.md`

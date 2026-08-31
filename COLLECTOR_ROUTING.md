# WOF research data-source routing

## Two authoritative roles

The original WOF project may use two different capture sources. They are complementary and must not be silently merged.

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

Browser/Web remains the authority for claims about Browser/WASM runtime semantics and for final production-context rule validation.

### WinKawaks Collector

Use `ouyong520/wof-winkawaks-bridge` when the research question benefits from fast, repeatable, high-frequency local runtime evidence:

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

A useful standard flow is:

```text
Browser observation/question
-> local WinKawaks high-speed evidence when useful
-> candidate interpretation
-> Browser/Web prospective validation
-> only then promote to production conclusion/rule
```

## Collector consumer contract

Stable bridge contract:

```text
repo: ouyong520/wof-winkawaks-bridge
doc: docs/COLLECTOR_V1_CONTRACT.md
task: tasks/CURRENT_TASK.json
result: results/collector_task_remote_result_latest.json
```

Supported v1 task actions:

```text
capture_raw_snapshot
capture_raw_burst
```

Default full raw data remains on the local collector machine. When full frames are genuinely needed by this project, request:

```json
"uploadRawStream": true
```

and the collector returns a gzip capture under:

```text
captures/<taskId>.jsonl.gz
```

## Source namespace rule

Never assume Browser/WASM offsets equal WinKawaks normalized offsets.

Examples already proven in current research:

```text
Browser enemy target selector: +0x7E
WinKawaks normalized canonical selected-player reference: +0x6D
```

A local WinKawaks discovery may motivate a Browser test, but does not by itself prove the same numeric field or semantic contract exists in Browser/WASM.

## Runtime operation

The collector itself does not need AI after deployment. On the collector machine:

```text
START_WOF_COLLECTOR.bat
```

starts the waiting service, and:

```text
STOP_WOF_COLLECTOR.bat
```

requests a clean stop.

AI/research logic may decide what evidence to request and how to interpret it; the local collector only performs mechanical read-only capture and handoff.

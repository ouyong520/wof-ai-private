# WOF052L Recorder Long-Capture QA Retest v1

**Stage:** `WOF052L_RECORDER_LONG_CAPTURE_QA_RETEST_V1`  
**Status:** **READY**  
**Production code changed:** **No**

## Decision

The current WOF052L Recorder baseline is READY for this bounded-equivalent long-capture QA stage.

The retest exercised the current room-isolation and fleet-supervisor behavior with a 12-room / 12-endpoint simulated fleet, repeated stress loops, stale-room failure injection, a real filesystem write failure, repeated safe-name/path checks, and structural validation of JSON, JSONL action-log, overlay, snapshot, and fleet-index artifacts.

Two independent bounded-equivalent executions passed with the same behavioral outcome.

## Grounded production baseline

Claim/start commit:

- `f6886b057ebdb0b5654a37568fb677e2bf4b94c9`

Production blobs locked by the QA harness and re-verified on current `main` before finalization:

- `parallel/WOF052L_RECORDER/recorder.py` — `9552d168534f3b742e7390597ff07ea5cfcaeaa2`
- `parallel/WOF052L_RECORDER/fleet_recorder.py` — `9398ef1569815439e6c141890f069674a30dca0f`

The relevant current production behavior is:

- `RecorderManager.poll_rooms()` catches an exception per live room, marks that room with the exception, finalizes it as `worker-cdp-error`, and continues iterating the remaining rooms.
- `FleetSupervisor.start_endpoint()` gives each Browser Fleet endpoint its own manager and daemon thread.
- `FleetSupervisor.merged_index()` tolerates a missing/unreadable child run file and still emits a machine-readable fleet index row for that child.
- production `safe_name()` removes unsafe separators/characters and bounds names.
- production `atomic_write_json()` creates parent directories, writes a temporary JSON file, and replaces the target atomically.

From the stage start commit to the concurrency check, `main` advanced by unrelated parallel work; the compare contained no changes under `parallel/WOF052L_RECORDER/**`. A later direct blob check on current `main` still returned the two production SHAs above.

## QA artifacts

Committed under the allowed QA path only:

- `parallel/WOF052L_RECORDER_QA_LONG_CAPTURE/test_recorder_long_capture.py`
- `parallel/WOF052L_RECORDER_QA_LONG_CAPTURE/LONG_CAPTURE_EVIDENCE.json`
- `parallel/WOF052L_RECORDER_QA_LONG_CAPTURE/LONG_CAPTURE_EVIDENCE_SECOND.json`
- `parallel/WOF052L_RECORDER_QA_LONG_CAPTURE/SAMPLES/action_log.sample.jsonl`
- `parallel/WOF052L_RECORDER_QA_LONG_CAPTURE/SAMPLES/overlay.sample.json`
- `parallel/WOF052L_RECORDER_QA_LONG_CAPTURE/SAMPLES/snapshot.sample.json`
- this `RESULT.md`

The harness imports `parallel/WOF052L_RECORDER` directly in a normal repository checkout and, by default, fails closed unless the production `recorder.py` and `fleet_recorder.py` Git blob SHAs equal the locked baseline above. This makes the committed QA layer sensitive to drift in the actual committed production path rather than being documentation-only.

## Execution environment and commands

Connector-side isolated execution environment:

- Python `3.13.5`
- Linux `6.18.35 x86_64`, glibc `2.41`
- `PYTHONDONTWRITEBYTECODE=1`
- private GitHub checkout was not mounted into the execution container

Because the GitHub connector exposes private file contents but does not mount the private repository into the execution container, the recorded executions used `WOF052L_QA_SOURCE_MIRROR=1` with extracted copies of the exact tested production paths (`RecorderManager.poll_rooms`, `safe_name`, `atomic_write_json`, and `FleetSupervisor`/manifest/index paths). This exception is recorded explicitly in both evidence JSON files. In a normal checkout, omit this variable; the harness then imports and SHA-locks the production files directly.

Recorded run A:

```bash
WOF052L_QA_SOURCE_MIRROR=1 PYTHONDONTWRITEBYTECODE=1 python parallel/WOF052L_RECORDER_QA_LONG_CAPTURE/test_recorder_long_capture.py --preserve-samples
```

Recorded run B:

```bash
WOF052L_QA_SOURCE_MIRROR=1 PYTHONDONTWRITEBYTECODE=1 python parallel/WOF052L_RECORDER_QA_LONG_CAPTURE/test_recorder_long_capture.py --evidence-out parallel/WOF052L_RECORDER_QA_LONG_CAPTURE/LONG_CAPTURE_EVIDENCE_SECOND.json
```

Direct-checkout command encoded by the committed harness:

```bash
PYTHONDONTWRITEBYTECODE=1 python parallel/WOF052L_RECORDER_QA_LONG_CAPTURE/test_recorder_long_capture.py --preserve-samples
```

## Bounded-equivalent stress window

Each run used:

- 12 simulated rooms
- 240 room polling loops
- 2,880 room-poll opportunities
- 12 simulated fleet endpoints
- 180 artifact cycles per healthy endpoint
- 11 healthy endpoints after one injected failure
- 1,980 healthy fleet artifact cycles
- 1,980 repeated unsafe-name normalization/path-safety assertions

Observed wall-clock duration:

- run A: `0.906 s`
- run B: `0.910 s`

This is intentionally a bounded-equivalent stress loop rather than a scarce >1-hour real long run, consistent with `TRUE_LONGRUN_EXECUTION_POLICY.md` preference for simulation when it provides the required failure/isolation evidence.

## Failure injection and isolation results

### 1. Single-room stale/CDP failure

Injection:

- room index `4` raises `RuntimeError("injected-stale-cdp-room")` on its 41st poll.

Expected/current-path behavior:

- `RecorderManager.poll_rooms()` catches the failure and finalizes only that room as `worker-cdp-error`.

Observed in both runs:

- broken room finalized at poll `41`
- finalization reason: `worker-cdp-error`
- healthy rooms remaining: `11`
- every healthy room completed all `240` polls and all `240` checkpoint opportunities
- main-loop exception: `null`

**PASS** — one stale/broken room did not stop healthy rooms.

### 2. Real artifact-path/write failure in one fleet worker

Injection:

- `blocked-artifact-parent` is first created as a regular file.
- endpoint index `7` then invokes production `atomic_write_json()` on `blocked-artifact-parent/must-fail.json`.

Observed in both runs:

- endpoint `7` raised/captured `FileExistsError`
- the failure remained confined to thread `wof052l-fleet-7`
- main thread survived
- the other `11` fleet workers completed all `180` cycles
- aggregate healthy samples in final fleet index: `1,980`
- final fleet index still contained `12` child rows, including the child whose run file was absent

**PASS** — a broken write path in one fleet worker did not prevent healthy workers or final fleet-index generation.

## Naming and path safety

Each healthy endpoint repeatedly normalized a deliberately hostile/raw label containing:

- `../`
- spaces
- Unicode (`♥`)
- path separators
- per-cycle suffixes

Across each run, `1,980` repeated naming checks asserted that the production `safe_name()` result:

- contained no `/`
- contained no `\\`
- stayed within the production 80-character bound

The resulting artifact paths remained under the temporary QA root.

**PASS**.

## Artifact structural validity

Per run, the harness generated and parsed:

- `11` JSONL action-log files
- `1,980` JSONL action rows
- `11` overlay JSON files
- `11` snapshot JSON files
- `11` healthy child run JSON files
- one final fleet merged JSON index

Validation included:

- every JSONL line parses as an object and retains expected `kind`/`ok` fields
- every overlay parses and has schema `wof052l-qa-overlay-v1` with final cycle `179`
- every snapshot parses and has production recorder schema `wof-052l-recorder-v1` with final cycle `179`
- fleet merged JSON has schema `wof-052l-fleet-supervisor-v1`, status `complete`, `12` child rows, and aggregate sample count `1,980`

Preserved representative samples are committed under `SAMPLES/`.

**PASS**.

## Regression / governance

### WOF Regression Gate V3

**Not run / not required for this stage.**

Reason: this task made no production behavior or production source changes. All writes are confined to the permitted QA directory plus the exact stage-claim file. The prompt requires Regression Gate V3 only when production behavior changes.

The existing WOF052L GitHub Actions workflow also does not include `parallel/WOF052L_RECORDER_QA_LONG_CAPTURE/**` in its path trigger and does not invoke this new harness, so no automatic CI result is claimed here.

### Owner / governance

No Owner intervention is required for this bounded-equivalent isolated QA run. No production procedure, unsafe production action, broad-scope edit, or true scarce >1-hour long run was requested or performed.

A future real >1-hour scarce/environmental long run would require the authorization/runtime/cost/abort/logging controls defined by `parallel/PM/TRUE_LONGRUN_EXECUTION_POLICY.md`; that is not a blocker for this bounded-equivalent stage.

## Final status

**READY**

Stop-condition checklist:

- stage claim acquired: PASS
- plan grounded in current committed Recorder/Fleet modules: PASS
- meaningful long-capture/failure-injection attempt: PASS (two bounded-equivalent runs)
- QA harness/evidence/samples committed under permitted QA path: PASS
- fresh result written: PASS
- production source edits: NONE
- Owner/governance blocker: NONE

# WOF Unified Collector V12 — Reuse / Legacy Readiness Preflight Recovery V2 RESULT

Status: **READY_FOR_V12_IMPLEMENTATION_WITH_MVP**

Stage: `WOF_UNIFIED_COLLECTOR_V12_REUSE_LEGACY_READINESS_PREFLIGHT_RECOVERY_V2`

Dedup key: `wof.unified-collector.v12.preflight.reuse-legacy-readiness-recovery-v2`

Claim token: `v12-reuse-legacy-recovery-v2-6b57d318883e4c69bb8f96f141ad9ae4`

## 1. Scope / non-overlap

This recovery is preflight only. It modified no production file in either repository and ran no historical regression/test suite. It did not acquire the V12 implementation umbrella claim.

The already-COMPLETE V12 acceptance/fixture readiness preflight remains authoritative for fixture names, deterministic acceptance semantics, CI coverage, and the minimum irreplaceable Windows/Browser/WOF acceptance. Those findings were consumed, not repeated.

This RESULT owns only:

- GitHub / official-ecosystem reuse-first selection for Windows lifecycle;
- current and historical Collector entrypoint classification;
- the directly executable V12 Windows launcher / stop / status / health MVP;
- an exact implementation file boundary and migration recommendation.

## 2. Evidence snapshot

Recovery claim start commit (`wof-ai-private`):

- `a0c724c73c19c19da9ed9933d88bf2ff4fa45415`

Latest main snapshots re-read before RESULT creation:

- `ouyong520/wof-ai-private`: `6c9cef2c388346598795b482b8d5e188ff708d80`
- `ouyong520/wof-winkawaks-bridge`: `7e9fdcd478623c6ad8a6f18c81d1d44ed11ecc52`

The bridge moved concurrently during this preflight. A compare from `5021ba56e0ef81a5f033cde83b08cabe853b6d68` to `7e9fdcd478623c6ad8a6f18c81d1d44ed11ecc52` changed only V11 terminal regression / stable-retro adapter files; it did not touch the launcher/lifecycle files classified below. The final launcher contents were nevertheless re-read at `7e9fdcd...`.

Two exact searches in current `wof-ai-private` for `START_WOF_UNIFIED_COLLECTOR` and `unified_collector_agent` returned no runtime implementation. Therefore the private repository currently contributes PM/acceptance authority, not a second Collector runtime entrypoint.

## 3. Current concrete lifecycle facts

At bridge `7e9fdcd...`:

- `START_WOF_UNIFIED_COLLECTOR.bat` resolves its own directory with `cd /d "%~dp0"`, but then searches PATH for `python` and `py`; it does **not** enforce the repository `.venv`.
- The same launcher deletes `runtime\STOP_COLLECTOR` before it starts the agent. This can erase a stop request belonging to an already-running instance before duplicate-instance rejection occurs.
- `START_WOF_COLLECTOR.bat` is a compatibility launcher, but it does not forward `%*` arguments.
- `STOP_WOF_UNIFIED_COLLECTOR.bat` and `STOP_WOF_COLLECTOR.bat` independently write the same unscoped plain sentinel `runtime\STOP_COLLECTOR`; the latter is not actually a wrapper today.
- `READY_WOF_TASK.bat` explicitly says it is disabled/retired.
- `bridge/unified_collector_agent.py` is V11 and already has one-agent dispatch for WinKawaks + Browser/WASM + stable-retro-fbneo, task-level terminal authority, `runtime/unified_collector_health.json`, `runtime/ACTIVE_TASK.json`, and `runtime/STOP_COLLECTOR`.
- `bridge/collector_single_instance.py` already uses a Windows named mutex (`Global\\WOF_WINKAWAKS_COLLECTOR_V1`) via `CreateMutexW`; duplicate agent start returns exit 34. The OS releases the mutex when the owning process exits.
- Current health is useful adapter/task evidence but is not a standalone operator `status`/`health` command and has no instance token/PID binding.

These are V12 lifecycle gaps, not reasons to replace the V3–V11 collection/data-stack implementation.

## 4. Mandatory A/B/C/D classification

Definitions:

- **A — compatibility wrapper**: retained public compatibility surface that delegates to one canonical V12 path.
- **B — standalone legacy path publicly deprecated**: current/historical implementation surface that still has useful internals but must not remain a separate public operator path.
- **C — retired/blocked**: must not be resurrected as a V12 operator path.
- **D — V12-owned canonical path**: only after V12 implementation owns it.

### 4.1 Current bridge Windows / runtime surfaces

| Surface | Current class | V12 disposition |
|---|---|---|
| `START_WOF_COLLECTOR.bat` | **A** | Keep as warning compatibility wrapper; forward `%*` to `START_WOF_UNIFIED_COLLECTOR.bat`. |
| `START_WOF_UNIFIED_COLLECTOR.bat` | **B** today | Modify in place; becomes **D** only when V12 implementation lands. Do not create another public start BAT. |
| `STOP_WOF_UNIFIED_COLLECTOR.bat` | **B** | Replace body with a compatibility call to canonical `START_WOF_UNIFIED_COLLECTOR.bat stop`; no direct sentinel write. |
| `STOP_WOF_COLLECTOR.bat` | **B** | It is currently a duplicate sentinel writer, not a wrapper. Convert to **A** compatibility call to canonical `... stop`. |
| `READY_WOF_TASK.bat` | **C** | Keep disabled/blocked; do not restore the old READY flow. |
| `bridge/unified_collector_agent.py` | **B** today | Evolve in place; becomes the V12 **D** unified agent/core. No second agent. |
| `bridge/collector_single_instance.py` | **B** helper | Adapt/reuse the existing named-mutex guard; do not create a competing lock primitive. |
| `bridge/collector_queue_runner.py` | **B** internal legacy execution path | Retain behind unified agent for compatibility; never expose as the V12 public launcher. |
| `bridge/collector_task_runner.py` | **B** internal legacy execution path | Reuse task/domain semantics; no independent public launch path. |
| `bridge/collector_service.py` | **B** internal orchestration overlap | Keep internal or fold callers toward unified agent; no public V12 service entrypoint. |
| `bridge/collector_daemon.py` | **B** legacy PM/GitHub service path | Internal transport/client reuse only; do not advertise as a second operator daemon. |
| `bridge/collector_analysis.py` | **B** internal legacy Collector helper | Reuse behind data stack only; not an operator entrypoint. |
| `runtime/unified_collector_health.json` | **B** current health surface | Reuse/extend in place for V12 instance-bound health. |
| `runtime/ACTIVE_TASK.json` | **B** current status surface | Reuse as task-level activity evidence; do not confuse with process health. |
| `runtime/STOP_COLLECTOR` | **B** legacy unscoped stop surface | Retire from canonical write path; replace with instance-bound JSON stop request. |

### 4.2 Historical overlapping paths

The earlier bridge snapshot seen at the beginning of the recovery still exposed old launchers including `START_WOF_AI.bat`, `START_WOF_ALL.bat`, `START_WOF_ALL_DIRECT.bat`, `START_WOF_ALL_STD.bat`, and `START_WOF_V1.bat`; these are absent from the final current root snapshot. All are **C — retired/blocked** for V12 and must not be reintroduced.

`bridge/m8_continuous_capture.py` is a bounded, direct WinKawaks continuous-capture CLI writing M8 diagnostic/result streams. It is **C as a V12 public Collector entrypoint**: useful historical diagnostic code may remain, but it must not compete with the unified agent/adapter route.

### 4.3 Current D-class inventory

**NONE.**

This is deliberate. V12 implementation has not started under this recovery, so no current path may be mislabeled as V12-owned canonical. The target D paths are listed in section 7.

## 5. Reuse-first review

### Selected

1. **Existing `bridge/collector_single_instance.py` named mutex — ADAPT_AND_REUSE**
   - Origin/license: repository-local code; no new third-party component or license is introduced. No root `LICENSE` file was observed at the bridge snapshot, so this preflight makes no unsupported SPDX assertion for repository-local code.
   - Maintenance: current V11 agent imports it directly.
   - Security: Windows kernel mutex is stronger than PID-name matching for exclusivity and is automatically released on process exit. Preserve the existing mutex name through migration so V11 and V12 cannot run simultaneously.
   - Adaptation: add instance metadata/token helpers around the mutex; do not replace it with a second lock.

2. **Existing `bridge/unified_collector_agent.py` health / active-task surfaces — ADAPT_AND_REUSE**
   - Origin/license: repository-local; no new dependency/license.
   - Maintenance: current V11 canonical agent.
   - Security: already preserves `readOnly=true`, `writesGameMemory=false`, `inputInjection=false` and source/task terminal authority. Extend only lifecycle metadata/readiness; do not rewrite domain semantics.

3. **Python standard library (`pathlib`, `json`, `uuid`, `os.replace`, `logging.handlers.RotatingFileHandler`) — DIRECT_USE**
   - License: Python Software Foundation License Version 2 for Python software/documentation (official Python license page).
   - Maintenance: CPython standard library; no added package/supply-chain surface.
   - Security: sufficient for atomic JSON state replacement, UUID instance identity, normalized paths and bounded log rotation.

### Evaluated but not selected

4. **`winsw/winsw` — REJECT_FOR_V12_MVP**
   - GitHub: `https://github.com/winsw/winsw`
   - License: MIT (`LICENSE.txt`; GitHub reports SPDX `MIT`).
   - Maintenance: non-archived; default branch `v3`; repository pushed 2026-07-30 and was active/updated in the evidence window.
   - Why rejected: WinSW solves Windows Service installation/management and commonly crosses into service/UAC/admin semantics. V12 needs one user-level Collector launcher, not an installed system service. Adopting it would add binary/configuration/supply-chain/admin surface without replacing any missing domain functionality.

5. **PowerShell process/CIM inspection — CONCEPT_ONLY**
   - Upstream GitHub `PowerShell/PowerShell` is MIT and maintained.
   - Possible later use: verified emergency force-stop using PID + process creation time + executable/cmdline identity.
   - MVP decision: do not require PowerShell and do not implement force-kill. Instance-bound cooperative stop plus named-mutex liveness is safer and smaller.

Rejected patterns independent of library choice: `taskkill /IM python.exe`, PID-only kill, unverified stale PID reuse, service installation, administrator requirement, PATH-selected Python, and a second launcher/agent stack.

## 6. Directly executable V12 Windows lifecycle MVP

### 6.1 One public launcher

Canonical public file remains:

`START_WOF_UNIFIED_COLLECTOR.bat`

Supported verbs:

```text
START_WOF_UNIFIED_COLLECTOR.bat
START_WOF_UNIFIED_COLLECTOR.bat start
START_WOF_UNIFIED_COLLECTOR.bat stop
START_WOF_UNIFIED_COLLECTOR.bat status
START_WOF_UNIFIED_COLLECTOR.bat health
```

No argument is exactly equivalent to `start` for existing users.

The BAT must:

1. `setlocal EnableExtensions`;
2. resolve repo root from `%~dp0` and `cd /d` there, independent of caller CWD;
3. use only `%~dp0.venv\Scripts\python.exe`;
4. fail with deterministic prerequisite status if that exact interpreter is missing; **no `where python`, no `py`, no PATH fallback**;
5. delegate the requested verb to `bridge/collector_lifecycle.py`;
6. never delete a stop/state file before single-instance authority has been established.

`START_WOF_COLLECTOR.bat` stays A-class and must use `call "%~dp0START_WOF_UNIFIED_COLLECTOR.bat" %*` after one compatibility warning.

### 6.2 Single-instance and instance identity

Reuse the current Windows named mutex unchanged through migration.

New lifecycle state root:

`runtime/collector-v12/`

Files:

- `instance.json` — atomically written `{schemaVersion, instanceId, pid, startedAtUtc, repoRoot, pythonExe, entrypoint}`.
- `heartbeat.json` — atomically replaced every ~2 s by the running agent/lifecycle helper, with matching `instanceId`, `pid`, `heartbeatAtUtc`, lifecycle state and task/readiness summary.
- `stop-request.json` — cooperative stop request `{schemaVersion, instanceId, pid, requestedAtUtc}`.
- `tmp/` — lifecycle-owned atomic-write scratch only.

`runtime/unified_collector_health.json` remains the operator/domain health document and is extended with the same `instanceId`/`pid`; do not fork a second adapter-health schema.

The running agent accepts a stop request only when `instanceId` matches its own current instance. A stale request from a prior process is ignored/cleaned only after the new process owns the mutex.

### 6.3 `status`

`status` is process/lifecycle state, not task result state.

Deterministic states:

- `RUNNING` — named mutex is held by another process and instance metadata is coherent.
- `STOP_REQUESTED` — current instance has a matching cooperative stop request.
- `STALE_STATE` — mutex is free but lifecycle state files remain; caller may clean only lifecycle-owned stale state after it successfully acquires/releases the mutex.
- `STOPPED` — mutex free and no current state.

Output should be one human line plus one machine-readable JSON object. It must never infer liveness from PID alone.

### 6.4 `health` and readiness

Separate three layers:

1. **process liveness**: current named mutex + matching `instanceId`;
2. **health**: liveness plus fresh lifecycle heartbeat (target 2 s; unhealthy after 10 s without a fresh heartbeat) plus no fatal lifecycle error;
3. **readiness**: health plus unified agent initialization complete and required local queue/status paths writable/readable. Adapter-specific states (`winkawaks`, `browser-wasm`, `stable-retro-fbneo`) remain visible independently and do not get collapsed into a false global READY.

Task-level states such as `RUNNING`, `DONE`, `FAILED`, `WAITING_FOR_OPERATOR` remain task authority and are not process-health states.

Suggested deterministic CLI return contract:

- `0`: requested operation healthy/successful (`start` accepted, `stop` completed/already stopped, `status` RUNNING, `health` HEALTHY);
- `2`: launcher/prerequisite/config error;
- `3`: `status` STOPPED;
- `4`: duplicate start / already running;
- `5`: running but NOT_READY/UNHEALTHY;
- `6`: stale lifecycle state or bounded stop timeout.

`stop` is idempotent. If running, it writes the instance-bound request and waits a bounded interval for mutex release; timeout returns 6 and does **not** kill a process. If already stopped, return 0.

### 6.5 Logs / temp / safety

Use Python stdlib rotation only; no new logging package:

- canonical operator log: `logs/unified_collector.jsonl`;
- `RotatingFileHandler`, 10 MiB per file, 5 backups is the MVP bound;
- lifecycle JSON writes use sibling `*.tmp` + `os.replace` for atomic replacement;
- cleanup is restricted to `runtime/collector-v12/` and only while the caller owns the mutex;
- never delete `~/.wof/attempts`, dataset artifacts, V5 retention data, Git queue results/status, or Training Farm exports;
- no game RAM write, no input injection, no Training Farm reset/step/load_state/start/schedule action is introduced by lifecycle work.

## 7. Exact future V12 implementation file boundary

Bridge runtime files intended for the MVP:

1. `START_WOF_UNIFIED_COLLECTOR.bat` — modify in place; target **D** public dispatcher.
2. `START_WOF_COLLECTOR.bat` — modify wrapper only; remains **A** and forwards `%*`.
3. `STOP_WOF_UNIFIED_COLLECTOR.bat` — modify into deprecated compatibility delegate to canonical `stop`.
4. `STOP_WOF_COLLECTOR.bat` — modify into **A** compatibility delegate to canonical `stop`.
5. `bridge/unified_collector_agent.py` — extend in place with instance-bound lifecycle/heartbeat integration; target **D** core.
6. `bridge/collector_single_instance.py` — adapt existing named-mutex helper; no replacement lock.
7. `bridge/collector_lifecycle.py` — **new**, target **D** lifecycle CLI/module only; it must not own collection/domain logic.
8. `README.md` — document one launcher and compatibility/deprecation table.

No other production file is required for the lifecycle MVP. In particular, do not create a second agent, service wrapper, Windows service, PowerShell launcher, or replacement queue/task runner.

Acceptance fixture/test filenames and CI additions are intentionally not re-specified here; the already-COMPLETE acceptance/fixture readiness preflight owns that matrix.

## 8. Migration recommendation

1. Implement `collector_lifecycle.py` around the existing mutex + existing unified agent.
2. Remove PATH Python fallback from the canonical BAT and require repo `.venv`.
3. Stop deleting `STOP_COLLECTOR` in the launcher; introduce instance-bound stop request.
4. Add instance identity + independent heartbeat and extend existing health JSON.
5. Convert both old stop BATs to delegates; make `START_WOF_COLLECTOR.bat` forward all args.
6. Keep `READY_WOF_TASK.bat` and removed V1/ALL/AI launchers retired.
7. Keep daemon/service/task-runner/M8 paths internal/historical; do not advertise them to operators.
8. Only after implementation lands, reclassify `START_WOF_UNIFIED_COLLECTOR.bat`, `bridge/unified_collector_agent.py`, and `bridge/collector_lifecycle.py` as V12 **D** canonical paths.

## 9. Final decision

**READY_FOR_V12_IMPLEMENTATION_WITH_MVP**

No Owner action is required by this preflight. No production edit or old-test execution was performed. The remaining work is implementation under a separate V12 umbrella authority, using the file boundary and lifecycle contract above.

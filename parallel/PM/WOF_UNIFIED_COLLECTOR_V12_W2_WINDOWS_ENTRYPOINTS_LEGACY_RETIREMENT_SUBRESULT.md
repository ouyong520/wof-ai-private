# WOF Unified Collector V12 W2 — Windows Entrypoints / Legacy Retirement SUBRESULT

Status: **SUBCOMPLETE**

Dedup key: `wof.unified-collector.v12.workstream.windows-entrypoints-legacy-retirement`

Parent dispatch: `parallel/PM/WOF_UNIFIED_COLLECTOR_V12_PARALLEL_3_WORKER_DISPATCH.md`

## Authority / boundary

- W2 subworkstream canonical claim only; V12 umbrella authority was not acquired or modified by W2.
- Production edits were confined to the W2-owned Windows public surface in `ouyong520/wof-winkawaks-bridge`.
- No lifecycle/Agent, adapter/data-stack, W3 test/workflow/harness, Training Farm, or Alpha production files were modified.

## Bridge baseline and landed W2 candidate

- Consumed V11 bridge baseline: `e80257d9486cd3129b115d4e1007bf24335b8852`.
- W2 bridge HEAD at focused self-check: `e7a4cffefe72c45c0f902512b23ac9c0efccd0d6`.
- Compare baseline -> W2 HEAD: ahead by 6 commits, exactly 5 modified W2-owned BAT files.
- W2 commits:
  - `79fc0e3093dcd05c6746b077b4995e4c2e7a890c` — canonical lifecycle entrypoint foundation;
  - `96765fe0836e3dee706a5a15f2906df4a0a606ff` — legacy START compatibility wrapper;
  - `a1787c2d1ab56513a23d58aaf2170e269d8c1beb` — unified STOP compatibility wrapper;
  - `fcc68f7730e9998fae1ce8b3fb9a6d7477dd908c` — legacy STOP compatibility wrapper;
  - `4011e79e147e73a548490ca5c4aa0feeeab48e73` — explicit READY retirement message;
  - `e7a4cffefe72c45c0f902512b23ac9c0efccd0d6` — explicit canonical verb gate / final W2 BAT candidate.

## Implemented public contract

### `START_WOF_UNIFIED_COLLECTOR.bat`

- Sole canonical Windows control entrypoint.
- Resolves and `cd /d` to `%~dp0`.
- Uses only `%~dp0.venv\Scripts\python.exe`.
- Missing repository interpreter fails deterministically with exit code `2`.
- No argument maps to `start`.
- Explicitly accepts only `start`, `stop`, `status`, `health` as first verb.
- Delegates lifecycle behavior to `python -m bridge.collector_lifecycle ...` and propagates its exit code.
- Does not delete/write legacy stop sentinels and contains no PATH/`py` interpreter fallback.

### Compatibility / retired public surfaces

- `START_WOF_COLLECTOR.bat`: warning-only compatibility wrapper; forwards `%*` to `START_WOF_UNIFIED_COLLECTOR.bat`.
- `STOP_WOF_UNIFIED_COLLECTOR.bat`: warning compatibility wrapper; calls canonical entrypoint with `stop` and forwards `%*`; no sentinel write.
- `STOP_WOF_COLLECTOR.bat`: warning compatibility wrapper; calls canonical entrypoint with `stop` and forwards `%*`; no sentinel write.
- `READY_WOF_TASK.bat`: explicitly remains retired and points operators only at `START_WOF_UNIFIED_COLLECTOR.bat` for start/stop/status/health.
- Historical removed start paths were not recreated; internal legacy Python runners/services were not promoted or advertised.

## Focused W2 self-check

Result: **PASS — static/public-surface contract**.

Checked on bridge HEAD `e7a4cffefe72c45c0f902512b23ac9c0efccd0d6`:

1. canonical BAT contains exact `.venv\Scripts\python.exe` resolution, no legacy sentinel deletion/write, explicit four-verb gate, no-arg `start`, and one `bridge.collector_lifecycle` delegation path;
2. legacy START forwards `%*` to the canonical BAT;
3. both STOP BATs route through canonical `stop`, forward trailing args, and no longer contain `runtime\STOP_COLLECTOR` writes;
4. READY path is explicitly retired and no longer advertises `START_WOF_COLLECTOR.bat` as the normal entrypoint;
5. root BAT inventory shows the maintained public surface is the canonical BAT plus the two compatibility STOP/one compatibility START wrappers and retired READY path; no historical launcher was resurrected;
6. baseline-to-W2 compare shows only the five W2-owned BAT files changed.

Per W2 dispatch, no broad V3–V11 regression was run.

## W1 integration dependency

At the final W2 self-check, `bridge/collector_lifecycle.py` was not yet present on bridge main. The BAT boundary therefore targets the exact parent/W1 contract (`python -m bridge.collector_lifecycle <verb>`) without creating any alternative BAT/PowerShell lifecycle implementation. Dynamic lifecycle execution belongs to W1/W3 integration after the W1 module lands.

W2 implementation itself is complete and integration-ready under the parallel dispatch contract.

**V12 terminal authority not claimed**.

Terminal W2 disposition: **SUBCOMPLETE — WINDOWS PUBLIC ENTRYPOINT / LEGACY RETIREMENT READY FOR W1 INTEGRATION**

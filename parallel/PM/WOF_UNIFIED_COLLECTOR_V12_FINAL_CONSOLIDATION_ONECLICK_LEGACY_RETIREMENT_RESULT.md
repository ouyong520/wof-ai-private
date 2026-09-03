# WOF Unified Collector V12 — Final Consolidation / OneClick / Legacy Retirement — RESULT

Status: **COMPLETE**

Canonical terminal token:

`COMPLETE — WOF UNIFIED COLLECTOR V12 FINAL CONSOLIDATION — ONE GIT-CONTROLLED COLLECTOR / ONECLICK WINDOWS UX / LEGACY RETIRED — FEATURE FROZEN`

Recovery closeout verdict:

`COMPLETE — WOF UNIFIED COLLECTOR V12 FINAL CONSOLIDATION / ONECLICK / LEGACY RETIREMENT — ONE COLLECTOR + THREE ADAPTERS TERMINAL COMPLETE`

Date: 2026-09-03

## 1. Final candidate authority

Final `ouyong520/wof-winkawaks-bridge` candidate:

- HEAD: `9b7c6897149cc7de615dd372e072d7b21e9de8f7`
- tree: `9da51bd18af28c5093095cc2684e74c669f3eebe`
- final commit: `Collector V12: align stale-stop acceptance with observed target`

Exact V11 terminal authority consumed without forking:

- V11 terminal bridge head: `e80257d9486cd3129b115d4e1007bf24335b8852`
- durable authority: `parallel/PM/WOF_UNIFIED_COLLECTOR_V11_TERMINAL_INTEGRATION_CLOSEOUT_RECOVERY_V2_RESULT.md`

Consumed V12 preflight authorities:

- `parallel/PM/WOF_UNIFIED_COLLECTOR_V12_REUSE_LEGACY_READINESS_PREFLIGHT_RECOVERY_V2_RESULT.md`
  - status: `READY_FOR_V12_IMPLEMENTATION_WITH_MVP`
  - selected reuse: existing named mutex + existing Unified Agent health/task surfaces + Python stdlib atomic state/logging primitives
- `parallel/PM/WOF_UNIFIED_COLLECTOR_V12_ACCEPTANCE_FIXTURE_READINESS_PREFLIGHT_RESULT.md`
  - status: `COMPLETE — V12 ACCEPTANCE / FIXTURE READINESS PREFLIGHT — MINIMAL FINAL EVIDENCE PLAN DURABLE`

Consumed completed parallel subworkstreams without redoing them:

- W2: `parallel/PM/WOF_UNIFIED_COLLECTOR_V12_W2_WINDOWS_ENTRYPOINTS_LEGACY_RETIREMENT_SUBRESULT.md`
  - durable bridge candidate: `e7a4cffefe72c45c0f902512b23ac9c0efccd0d6`
  - disposition: `SUBCOMPLETE`, consumed by terminal coordinator
- W3: `parallel/PM/WOF_UNIFIED_COLLECTOR_V12_W3_ACCEPTANCE_HARNESS_CI_SUBRESULT.md`
  - durable bridge candidate: `b5540d9678d572fc1a6a09cb5bbcf4e3014defd2`
  - disposition: `SUBCOMPLETE`, consumed by terminal coordinator

Original W1 implementation authority consumed:

- lifecycle core: `8725c7063a8a6817bb40cb9edcff04bdf63e75b1`
- Unified Agent lifecycle binding: `ccf11433362ac79030fa971e29250b417d1aef29`

During terminal execution PM authorized `WOF_UNIFIED_COLLECTOR_V12_TERMINAL_INTEGRATION_CLOSEOUT_RECOVERY_V2`; that recovery only reconciles the stopped W1 terminal responsibility. It does not create another product or repeat W2/W3 implementation.

## 2. Terminal architecture

V12 leaves exactly one maintained operational Collector product:

```text
START_WOF_UNIFIED_COLLECTOR.bat
  -> bridge.collector_lifecycle
     -> bridge.unified_collector_agent
        -> browser-wasm adapter
        -> winkawaks adapter
        -> stable-retro-fbneo adapter
```

There is still exactly one established Git control/result plane:

```text
tasks/queue
status/by_task
results/by_task
```

The existing source-aware dataset/provenance, retention/storage, analysis, DuckDB warehouse/query, and reuse-first planner authorities are reused in place. V12 introduced no second queue, catalog, warehouse, analysis engine, planner, or source-specific Collector service.

The three maintained source namespaces remain exactly:

- `browser-wasm`
- `winkawaks`
- `stable-retro-fbneo`

## 3. Windows public entrypoint / legacy disposition

| Surface | V12 final disposition |
|---|---|
| `START_WOF_UNIFIED_COLLECTOR.bat` | sole canonical public `start` / `stop` / `status` / `health` entrypoint; no argument = `start`; repo-root normalized; repo `.venv\\Scripts\\python.exe` only; no PATH/`py` fallback |
| `START_WOF_COLLECTOR.bat` | compatibility wrapper only; forwards `%*` to canonical entrypoint |
| `STOP_WOF_UNIFIED_COLLECTOR.bat` | compatibility wrapper only; delegates canonical `stop`; no independent sentinel write |
| `STOP_WOF_COLLECTOR.bat` | compatibility wrapper only; delegates canonical `stop`; no independent sentinel write |
| `READY_WOF_TASK.bat` | remains retired/blocked |
| historical `START_WOF_AI.bat`, `START_WOF_ALL*.bat`, `START_WOF_V1.bat` | remain retired; not resurrected |
| old Python runner/service/daemon helpers | internal compatibility/reuse surfaces only, not a second normal operator entrypoint |

## 4. Lifecycle / Agent integration facts

V12 lifecycle state remains local under `runtime/collector-v12/`:

- `instance.json`
- `heartbeat.json`
- `stop-request.json`
- lifecycle-owned `tmp/`

Writes use temporary files plus `os.replace`.

Single-instance authority reuses the existing Windows named mutex `Global\\WOF_WINKAWAKS_COLLECTOR_V1`; duplicate start remains fail-closed and is mapped to V12 exit code 4.

`status`, process health, and Agent readiness remain distinct. Lifecycle status exposes `RUNNING`, `STOP_REQUESTED`, `STALE_STATE`, or `STOPPED`; health includes heartbeat freshness/fatal lifecycle state; readiness additionally requires Agent initialization and current-instance-bound domain health. `runtime/unified_collector_health.json` remains the one Agent/domain health surface and exposes all three adapter states.

Cooperative stop is idempotent and does not force-kill a process.

## 5. Real terminal integration defect fixed

Terminal review found a real stale-stop TOCTOU in the initial W1 lifecycle implementation:

1. `request_stop()` first observed RUNNING instance A via `status_snapshot()`;
2. it then independently re-read `instance.json` to construct the stop request;
3. if A exited and replacement B acquired the mutex/wrote new instance metadata between those reads, the old operator stop could accidentally bind to B.

Production fix:

- commit `a89fe3754282181069f26f368ff6494977821029`
- `request_stop()` now freezes `target_instance_id` and `target_pid` from the first lifecycle status observation;
- the stop request is always bound to that observed target;
- if a different current `instanceId` appears while waiting, V12 reports `TARGET_INSTANCE_EXITED_NEW_INSTANCE_LEFT_RUNNING` with `staleStopProtected=true` and leaves the replacement running;
- the replacement instance ignores/removes the stale old-instance request fail-closed.

Focused regression was strengthened at commit `459c79d66e01d484411e0e49bb73de70a4fbc74f` to exercise an explicit A -> B rollover and prove the emitted request still targets A/PID A, never B.

The first post-fix V12 focused CI exposed only a W3 static-detector mismatch: the detector still searched for the old implementation spelling `instance["instanceId"]`. The new rollover regression itself was PASS. The detector was corrected, not weakened, at final commit `9b7c6897149cc7de615dd372e072d7b21e9de8f7` to require the stronger observed-target semantics (`target_instance_id`, `target_pid`, replacement-instance branch, and `staleStopProtected`).

## 6. Final affected verification / CI

### 6.1 V12 final focused acceptance — exact final candidate

Workflow: `Collector V12 Focused Acceptance`

- run: `33722396068`
- job: `100544061556`
- exact checkout: `9b7c6897149cc7de615dd372e072d7b21e9de8f7`
- compile gate: PASS
- focused unittest count: `19/19 PASS`
- machine repository acceptance: `PASS:9 BLOCKED:0 DEFERRED:0`
- acceptance bundle: `runtime/v12-acceptance/collector-v12-repository-acceptance.json`
- uploaded artifact id: `9880645917`
- artifact name: `collector-v12-repository-acceptance-9b7c6897149c`
- artifact ZIP digest: `sha256:dc3fa07806df45c431aaf7abf1bc9b3baad936fda05750117663341d63286ca0`

The nine repository facts cover canonical entrypoint, wrapper delegation, legacy retirement, instance-bound stale-stop protection, single-instance authority, status/health/readiness separation, all-three-adapter health visibility, one Git queue/status/result plane, and exact V11 terminal ancestry.

### 6.2 Affected V10/V11 compatibility — reused exact material-SUT run

`bridge/unified_collector_agent.py` was materially changed by W1 at `ccf11433362ac79030fa971e29250b417d1aef29`, so the existing push-triggered affected suites ran once on that exact Agent candidate after W2 launcher work was already present:

V10 affected regression:

- workflow job: `v3-v10-regression`
- run: `33720816956`
- job: `100539399338`
- V3-V9 maintained: `151/151 PASS`
- V10 Unified Agent/fake-CDP compatibility: `36/36 PASS`
- combined: `187/187 PASS`
- V10 schema/examples/source/safety/launcher compatibility gate: PASS

V11 terminal affected regression:

- workflow job: `v3-v11-terminal`
- run: `33720816923`
- job: `100539399267`
- V3-V9 maintained: `151/151 PASS`
- V10 compatibility: `36/36 PASS`
- V11 terminal integration: `2/2 PASS`
- combined: `189/189 PASS`
- V11 three-source provenance/safety gate: PASS

From `ccf11433362ac79030fa971e29250b417d1aef29` to final `9b7c6897149cc7de615dd372e072d7b21e9de8f7`, the changed files are only:

- `.github/workflows/collector-v12-focused-acceptance.yml`
- `bridge/collector_lifecycle.py`
- `tests/test_unified_collector_v12_acceptance.py`
- `tests/v12_acceptance_harness.py`

No V10/V11 Agent, adapter, queue/data-stack, warehouse, or planner SUT changed after the already-green affected run. Therefore V10/V11 historical suites were not rerun merely for confidence; their exact affected PASS evidence is reused according to `TESTING_CADENCE_POLICY.md`.

## 7. Machine-readable acceptance authority

The final repository acceptance bundle is bound to the final bridge candidate and validates:

- final bridge commit/tree identity;
- exact V11 terminal ancestor consumption;
- exactly three source namespaces;
- `readOnly=true`;
- `writesGameMemory=false`;
- `inputInjection=false`;
- all nine repository acceptance facts PASS.

The bundle validator explicitly refuses to convert a real-runtime fact into PASS without runtime evidence containing session identity, SHA-256 evidence binding, and provenance.

## 8. Safety invariants

Preserved at terminal closeout:

```text
readOnly=true
writesGameMemory=false
inputInjection=false
```

Also preserved:

- exact World/source identity boundaries;
- no Training Farm action selection;
- no Collector `reset`, `step`, `load_state` authority;
- no Collector launch/scale authority over the Training Farm fleet;
- no cross-source RAM/semantic-equivalence promotion;
- no Alpha production modification;
- no real 10-worker fleet launch during V12 terminal integration.

## 9. Real-runtime acceptance status — explicitly not fabricated

Repository/CI terminal acceptance is complete and green. Real-runtime facts that repository fixtures cannot legitimately manufacture remain explicitly external:

1. **Real Windows Browser/WOF acceptance** — `BLOCKED` as an external runtime fact with reason code `REAL_WINDOWS_WOF_ENVIRONMENT_REQUIRED`.
   - required only when Owner authorizes/provides one bounded Windows/WOF acceptance session;
   - repository CI does not claim real Page -> Worker -> WASM discovery occurred.
2. **Live bounded Training Farm 10-worker acceptance** — `DEFERRED` with reason code `TRAINING_FARM_LIVE_FLEET_AUTHORITY_GATED`.
   - current Training Farm StageGuard authority must first permit bounded 10-worker execution;
   - V12 retains the already-green ROM-free ten-worker isolation evidence and does not bypass the gate.

These facts are recorded exactly because the V12 acceptance contract explicitly prohibits fabricating unavailable live proof and permits external/runtime acceptance conditions to remain recorded after the repository candidate is frozen and its authorized repository gates are satisfied. They are not relabeled PASS.

## 10. Terminal conclusion

V12 terminal consolidation is complete at bridge `9b7c6897149cc7de615dd372e072d7b21e9de8f7` / tree `9da51bd18af28c5093095cc2684e74c669f3eebe`.

The resulting maintained product is exactly:

**one Git-controlled Unified Collector + one Windows lifecycle entrypoint + three adapters + one queue/status/result/data stack.**

Legacy overlapping public launch paths are retired or compatibility-only. Stale stop requests are replacement-safe. Single-instance, lifecycle status, heartbeat health, readiness, adapter state visibility, and final machine acceptance are all bound to the integrated candidate.

Collector feature work is now **FROZEN**. Do not create V13/V14 for activity; only reopen for a materially demonstrated defect or an explicitly authorized external real-runtime acceptance session.

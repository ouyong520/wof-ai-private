# WOF Unified Collector V12 — Final Consolidation / OneClick / Legacy Retirement — RESULT

Status: **COMPLETE**

Canonical terminal token:

`COMPLETE — WOF UNIFIED COLLECTOR V12 FINAL CONSOLIDATION — ONE GIT-CONTROLLED COLLECTOR / ONECLICK WINDOWS UX / LEGACY RETIRED — FEATURE FROZEN`

Date: 2026-09-03

## Final candidate authority

Final `ouyong520/wof-winkawaks-bridge` candidate:

- HEAD: `9b7c6897149cc7de615dd372e072d7b21e9de8f7`
- tree: `9da51bd18af28c5093095cc2684e74c669f3eebe`
- final commit: `Collector V12: align stale-stop acceptance with observed target`

Consumed exact V11 terminal authority without forking:

- bridge HEAD: `e80257d9486cd3129b115d4e1007bf24335b8852`
- RESULT: `parallel/PM/WOF_UNIFIED_COLLECTOR_V11_TERMINAL_INTEGRATION_CLOSEOUT_RECOVERY_V2_RESULT.md`

Consumed V12 preflight authorities:

- `parallel/PM/WOF_UNIFIED_COLLECTOR_V12_REUSE_LEGACY_READINESS_PREFLIGHT_RECOVERY_V2_RESULT.md`
- `parallel/PM/WOF_UNIFIED_COLLECTOR_V12_ACCEPTANCE_FIXTURE_READINESS_PREFLIGHT_RESULT.md`

Consumed completed subworkstreams without redoing them:

- W2 public entrypoint / legacy retirement: `parallel/PM/WOF_UNIFIED_COLLECTOR_V12_W2_WINDOWS_ENTRYPOINTS_LEGACY_RETIREMENT_SUBRESULT.md`, bridge candidate `e7a4cffefe72c45c0f902512b23ac9c0efccd0d6`, `SUBCOMPLETE`.
- W3 acceptance harness / focused CI: `parallel/PM/WOF_UNIFIED_COLLECTOR_V12_W3_ACCEPTANCE_HARNESS_CI_SUBRESULT.md`, bridge candidate `b5540d9678d572fc1a6a09cb5bbcf4e3014defd2`, `SUBCOMPLETE`.
- W1 lifecycle core: `8725c7063a8a6817bb40cb9edcff04bdf63e75b1`.
- W1 Unified Agent lifecycle binding: `ccf11433362ac79030fa971e29250b417d1aef29`.

PM-authorized terminal reconciliation authority `wof.unified-collector.v12.terminal-integration-closeout-recovery-v2` is COMPLETE and did not create a second Collector product.

## Terminal architecture

Exactly one maintained operational Collector remains:

```text
START_WOF_UNIFIED_COLLECTOR.bat
  -> bridge.collector_lifecycle
     -> bridge.unified_collector_agent
        -> browser-wasm
        -> winkawaks
        -> stable-retro-fbneo
```

The established Git control/result plane remains singular:

```text
tasks/queue
status/by_task
results/by_task
```

Existing source-aware dataset/provenance, retention/storage, analysis, DuckDB warehouse/query and reuse-first planner authorities are reused in place. V12 adds no second queue, catalog, warehouse, planner, normal collector daemon, or source-specific control plane.

## Lifecycle integration and terminal defect closure

Lifecycle state is under `runtime/collector-v12/` with atomic `instance.json`, `heartbeat.json`, `stop-request.json` and lifecycle-owned `tmp/`. Existing Windows named mutex `Global\\WOF_WINKAWAKS_COLLECTOR_V1` remains the single-instance authority.

`status`, heartbeat/process health, and Unified Agent readiness are distinct. `runtime/unified_collector_health.json` remains the one domain health surface and continues to expose all three adapter states.

Terminal integration found and fixed a real stale-stop rollover race. Commit `a89fe3754282181069f26f368ff6494977821029` binds a stop request to the initially observed `instanceId` + PID, rather than re-reading replacement instance metadata. Commit `459c79d66e01d484411e0e49bb73de70a4fbc74f` adds the A -> B rollover regression. Final commit `9b7c6897149cc7de615dd372e072d7b21e9de8f7` aligns the W3 static acceptance detector with the stronger observed-target contract.

Cooperative stop remains idempotent and never force-kills a process.

## Windows public entrypoint / legacy disposition

| Surface | V12 final disposition |
|---|---|
| `START_WOF_UNIFIED_COLLECTOR.bat` | sole canonical `start` / `stop` / `status` / `health` entrypoint; no argument = `start`; repo `.venv\\Scripts\\python.exe` only; no PATH/`py` fallback |
| `START_WOF_COLLECTOR.bat` | warning compatibility wrapper forwarding `%*` |
| `STOP_WOF_UNIFIED_COLLECTOR.bat` | compatibility wrapper to canonical `stop`; no sentinel write |
| `STOP_WOF_COLLECTOR.bat` | compatibility wrapper to canonical `stop`; no sentinel write |
| `READY_WOF_TASK.bat` | retired/blocked |
| historical `START_WOF_AI.bat`, `START_WOF_ALL*.bat`, `START_WOF_V1.bat` | remain retired; not resurrected |
| old Python runner/service/daemon helpers | internal compatibility/reuse only, not normal public operator paths |

## Final affected verification / CI

Final focused workflow: `Collector V12 Focused Acceptance`.

- run: `33722396068`
- job: `100544061556`
- exact checkout: `9b7c6897149cc7de615dd372e072d7b21e9de8f7`
- compile gate: PASS
- focused tests: `19/19 PASS`
- machine repository acceptance: `PASS:9 BLOCKED:0 DEFERRED:0`
- generated JSON bundle ID: `collector-v12-repository-9b7c6897149c`
- generated JSON SHA-256: `3a264c01c77091c058be546eb3ba9896d85bbc08264e729bde19b97481f24c6f`
- uploaded artifact id: `9880685207`
- artifact name: `collector-v12-repository-acceptance-9b7c6897149cc7de615dd372e072d7b21e9de8f7`
- artifact ZIP SHA-256: `90a0e3e21068cbd9b5a1ce4819917cdbfa0a5503eb5c1957b4195faccea407cf`
- artifact retention: 14 days

Durable terminal machine-readable bundle:

`parallel/PM/WOF_UNIFIED_COLLECTOR_V12_FINAL_CONSOLIDATION_ONECLICK_LEGACY_RETIREMENT_ACCEPTANCE_BUNDLE.json`

The durable bundle preserves the exact CI artifact metadata and repository acceptance facts, and separately records external runtime facts as `BLOCKED` / `DEFERRED` rather than manufacturing PASS.

### Affected V10/V11 compatibility reuse

`bridge/unified_collector_agent.py` was materially changed at `ccf11433362ac79030fa971e29250b417d1aef29`, so the directly affected suites already ran once on that material Agent candidate after W2 launcher work was present:

- V10 affected regression: run `33720816956`, job `100539399338`, `187/187 PASS` including `36/36` V10 Unified Agent/fake-CDP compatibility.
- V11 terminal affected regression: run `33720816923`, job `100539399267`, `189/189 PASS` including `2/2` V11 terminal integration.

After `ccf11433362ac79030fa971e29250b417d1aef29`, only V12 workflow/lifecycle/acceptance-test surfaces changed; no V10/V11 Agent/adapter/data-stack/warehouse/planner SUT changed. Historical V10/V11 regressions were therefore not rerun again for confidence.

## Safety / source invariants

Preserved:

```text
readOnly=true
writesGameMemory=false
inputInjection=false
```

Exactly three maintained source namespaces remain:

- `browser-wasm`
- `winkawaks`
- `stable-retro-fbneo`

Collector has no Training Farm action selection, `reset` / `step` / `load_state`, worker launch/scale authority, cross-source RAM/semantic-equivalence promotion, or Alpha production mutation.

## Real-runtime acceptance — explicitly not fabricated

Repository/CI acceptance is terminal green. Unavailable real-runtime facts remain external:

1. **Real Windows/WOF acceptance** — `BLOCKED`, reason `REAL_WINDOWS_WOF_ENVIRONMENT_REQUIRED`. No repository or Linux CI evidence is labeled as real Windows/Page/Worker/WASM/WOF proof.
2. **Live bounded Training Farm 10-worker acceptance** — `DEFERRED`, reason `TRAINING_FARM_LIVE_FLEET_AUTHORITY_GATED`. Existing ROM-free ten-worker isolation evidence is retained, but it is not relabeled live-fleet proof.

These external facts do not invalidate the authorized repository terminal closeout because the parent authority explicitly permits precise external/runtime gating and forbids fabricated PASS.

## Terminal conclusion

V12 is terminal COMPLETE at bridge `9b7c6897149cc7de615dd372e072d7b21e9de8f7` / tree `9da51bd18af28c5093095cc2684e74c669f3eebe`.

The maintained product is exactly:

**one Git-controlled Unified Collector + one Windows lifecycle entrypoint + three adapters + one queue/status/result/data stack.**

Collector feature work is now **FROZEN**. Reopen only for a materially demonstrated defect, supported-runtime/data-integrity/security fix, measured bottleneck, explicitly approved new source adapter, or an authorized external real-runtime acceptance session.

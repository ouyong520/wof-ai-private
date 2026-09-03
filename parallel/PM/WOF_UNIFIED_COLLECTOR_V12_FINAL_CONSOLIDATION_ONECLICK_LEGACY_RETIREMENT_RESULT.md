# WOF Unified Collector V12 — Final Consolidation / OneClick / Legacy Retirement — RESULT

Status: **COMPLETE**

Canonical terminal token:

`COMPLETE — WOF UNIFIED COLLECTOR V12 FINAL CONSOLIDATION — ONE GIT-CONTROLLED COLLECTOR / ONECLICK WINDOWS UX / LEGACY RETIRED — FEATURE FROZEN`

Date: 2026-09-03

## Final candidate authority

Final `ouyong520/wof-winkawaks-bridge` candidate:

- HEAD: `65831cb0cf3ec3fcfdfe0f20bade5ee24deafc95`
- tree: `6102471dde9c4f8b6b6f85fed3d1c7cc54d41d55`
- final commit: `Collector V12: close lifecycle identity and readiness races`

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

A PM-authorized terminal reconciliation authority, `wof.unified-collector.v12.terminal-integration-closeout-recovery-v2`, was already present on current main during terminal execution. It is COMPLETE, was consumed rather than duplicated, and did not create a second Collector product or redo W2/W3.

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

Lifecycle state remains under `runtime/collector-v12/` with atomic `instance.json`, `heartbeat.json`, `stop-request.json` and lifecycle-owned `tmp/`. Existing Windows named mutex `Global\\WOF_WINKAWAKS_COLLECTOR_V1` remains the single-instance authority.

`status`, heartbeat/process health, and Unified Agent/control-plane readiness remain distinct. `runtime/unified_collector_health.json` is still the one domain health surface and exposes the three adapter states only when that health document is bound to the same live lifecycle instance.

Terminal integration fixed the real rollover defect already found after W1/W2/W3 integration:

- `a89fe3754282181069f26f368ff6494977821029` binds a stop request to the initially observed `instanceId` + PID rather than re-reading replacement instance metadata.
- `459c79d66e01d484411e0e49bb73de70a4fbc74f` adds an explicit A -> B replacement regression proving the emitted stop still targets A.
- `9b7c6897149cc7de615dd372e072d7b21e9de8f7` aligns the W3 repository detector with the stronger observed-target contract.

Final review then found and closed four remaining lifecycle/control-plane boundary gaps in `65831cb0cf3ec3fcfdfe0f20bade5ee24deafc95`:

1. A stale mismatched `stop-request.json` is now ignored and preserved rather than unlinked. This removes the read-stale / concurrent-atomic-replace / unlink race that could otherwise erase a newly matching stop request.
2. `health` now rejects a lifecycle `instance.json` that changes after the status observation (`INSTANCE_CHANGED_DURING_HEALTH_SNAPSHOT`) instead of mixing old status with replacement heartbeat/domain state.
3. Adapter states are surfaced only from a `runtime/unified_collector_health.json` document bound to the current lifecycle instance and PID; stale-domain adapter state no longer leaks into current health.
4. readiness now requires `agentInitialized=true`, `controlPlaneReady=true`, fresh/nonfatal lifecycle heartbeat, and current-instance-bound domain health. Lifecycle instance metadata also records the canonical public entrypoint `START_WOF_UNIFIED_COLLECTOR.bat`.

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

- run: `33723112765`
- job: `100546230865`
- exact checkout: `65831cb0cf3ec3fcfdfe0f20bade5ee24deafc95`
- exact tree: `6102471dde9c4f8b6b6f85fed3d1c7cc54d41d55`
- Python compile gate: PASS
- focused V12 tests: `19/19 PASS`
- machine repository acceptance: `PASS:9 BLOCKED:0 DEFERRED:0`
- generated repository bundle ID: `collector-v12-repository-65831cb0cf3e`
- generated repository JSON SHA-256: `86b3439e58d1b31103c1ef35cc6176d582931b78042ba56f2136e9f406fa3f41`
- uploaded artifact id: `9880942586`
- artifact name: `collector-v12-repository-acceptance-65831cb0cf3ec3fcfdfe0f20bade5ee24deafc95`
- artifact ZIP SHA-256: `b2d8871036459d60b79b35a1f3de59874230fbdcba05f84fa4a0e4f8f04ef3f8`
- artifact retention: 14 days

Durable terminal machine-readable bundle:

`parallel/PM/WOF_UNIFIED_COLLECTOR_V12_FINAL_CONSOLIDATION_ONECLICK_LEGACY_RETIREMENT_ACCEPTANCE_BUNDLE.json`

- durable bundle update commit: `63ecacee09d78fa40bb4c3f58526e35048a6ff2b`
- repository acceptance embedded byte-for-byte from the final CI artifact
- external runtime facts remain separately `BLOCKED` / `DEFERRED`; no unavailable live proof is manufactured as PASS

### Affected V10/V11 compatibility reuse

`bridge/unified_collector_agent.py` was materially changed at `ccf11433362ac79030fa971e29250b417d1aef29`. The directly affected maintained suites ran once on that material Agent candidate after the W2 launcher work was already present:

- V10 affected regression: run `33720816956`, job `100539399338`, `187/187 PASS`, including `36/36` V10 Unified Agent/fake-CDP compatibility.
- V11 terminal affected regression: run `33720816923`, job `100539399267`, `189/189 PASS`, including `2/2` V11 terminal integration and the three-source provenance/safety gate.

From `ccf11433362ac79030fa971e29250b417d1aef29` through final `65831cb0cf3ec3fcfdfe0f20bade5ee24deafc95`, no Agent, adapter base, queue/data stack, warehouse, analysis, or planner SUT changed after those already-green affected runs. The final correction changes only lifecycle plus its V12 acceptance tests. Per `TESTING_CADENCE_POLICY.md`, V10/V11 were therefore not rerun again merely for confidence.

## Machine-readable repository acceptance facts

The final CI-bound repository bundle proves nine repository facts, all PASS:

- one canonical Windows lifecycle entrypoint;
- compatibility wrappers delegate correctly;
- stale-stop protection is instance-bound;
- existing named mutex remains the single-instance authority;
- status / health / readiness are distinct;
- one Agent health surface exposes exactly the three maintained adapter namespaces;
- one Git task/status/result plane remains intact;
- legacy public paths remain retired/compatibility-only;
- exact V11 terminal authority remains an ancestor of the final bridge candidate.

The exact maintained source namespaces remain:

- `browser-wasm`
- `winkawaks`
- `stable-retro-fbneo`

## Safety / architecture invariants

Preserved:

```text
readOnly=true
writesGameMemory=false
inputInjection=false
```

Also preserved:

- one Unified Collector product, not one Collector per RAM/source authority;
- no Training Farm action selection;
- no Collector `reset` / `step` / `load_state` authority;
- no Collector worker launch/scale authority;
- no cross-source RAM/semantic-equivalence promotion;
- no Alpha production mutation;
- no real 10-worker fleet launch during repository terminal integration.

## Real-runtime acceptance — explicitly not fabricated

Repository/CI acceptance is terminal green. Unavailable real-runtime facts remain external and are recorded in the durable terminal bundle:

1. **Real Windows/WOF acceptance** — `BLOCKED`, reason `REAL_WINDOWS_WOF_ENVIRONMENT_REQUIRED`. Repository/Linux CI does not claim a real Windows Page -> Worker -> WASM / WOF session occurred. This becomes executable only with an Owner-authorized bounded Windows/WOF acceptance session.
2. **Live bounded Training Farm 10-worker acceptance** — `DEFERRED`, reason `TRAINING_FARM_LIVE_FLEET_AUTHORITY_GATED`. Current Training Farm StageGuard must first permit bounded live 10-worker execution. Existing ROM-free isolation evidence is retained but is not relabeled live-fleet proof.

These facts are not relabeled PASS and do not invalidate the authorized repository terminal closeout: the parent contract explicitly requires precise external/runtime gating instead of fabricated proof.

## Terminal conclusion

V12 is terminal COMPLETE at bridge `65831cb0cf3ec3fcfdfe0f20bade5ee24deafc95` / tree `6102471dde9c4f8b6b6f85fed3d1c7cc54d41d55`.

The maintained product is exactly:

**one Git-controlled Unified Collector + one Windows lifecycle entrypoint + three adapters + one queue/status/result/data stack.**

W1, the original V12 umbrella canonical authority, and the V12 stage remain COMPLETE under their existing claim lineage; terminal evidence bindings are updated to this final candidate rather than reopening or re-claiming them.

Collector feature work is now **FROZEN**. Reopen only for a materially demonstrated defect, supported-runtime/data-integrity/security fix, measured bottleneck, explicitly approved new source adapter, or an authorized external real-runtime acceptance session.

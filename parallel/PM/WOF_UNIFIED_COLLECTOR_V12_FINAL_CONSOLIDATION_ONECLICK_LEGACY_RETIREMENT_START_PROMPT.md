# WOF Unified Collector V12 — Final Consolidation / OneClick / Legacy Retirement

stageId: `WOF_UNIFIED_COLLECTOR_V12_FINAL_CONSOLIDATION_ONECLICK_LEGACY_RETIREMENT_V1`
dedupProtocol: `v2`
dedupKey: `wof.unified-collector.v12.final-consolidation-oneclick-legacy-retirement`
dedupMode: `exclusive`

Priority: **P0 — final Collector implementation / feature freeze candidate**

## Owner final direction

V12 is the final implementation stage for the Unified Collector program. After V12 COMPLETE the Collector is **FEATURE FROZEN** except for real defects, supported-runtime compatibility, data-integrity/security fixes, measured performance bottlenecks, or an explicitly approved new source adapter.

Final product statement:

**ONE GIT-CONTROLLED WOF UNIFIED COLLECTOR — Browser/WASM + WinKawaks + Training Farm collection — one Agent, one task/result/data stack, source authority kept explicit.**

Do not create V13/V14 merely to continue development.

## Mandatory current authority

Re-read current main before any work.

At PM staging time:

- `ouyong520/wof-winkawaks-bridge` V11 terminal HEAD: `e80257d9486cd3129b115d4e1007bf24335b8852`
- V11 terminal tree: `8b42c7b06ba090e1a2d669140adfc9715f2ab4a7`
- V11 terminal RESULT: `parallel/PM/WOF_UNIFIED_COLLECTOR_V11_TERMINAL_INTEGRATION_CLOSEOUT_RECOVERY_V2_RESULT.md`
- V11 terminal CI: workflow `Collector V11 Terminal V3-V11 Regression`, run `33718216943`, job `100531770680`, **189/189 PASS**
- V11 successor recovery canonical/stage claims are COMPLETE.
- Historical predecessor V11/W1 ACTIVE claims are stale historical records superseded by the V11 terminal recovery; do not reopen or overwrite them.

V11 has already closed the real cross-component joins:

1. actual W1 Training Farm exporter -> actual stable-retro-fbneo adapter;
2. actual unified v2 Training Farm result -> source-aware V4/V8/V9 data stack.

Do **not** rebuild or re-test those joins unless V12 materially changes their SUT.

## Required V12 preflight results — consume, do not repeat

### Reuse / legacy readiness

`parallel/PM/WOF_UNIFIED_COLLECTOR_V12_REUSE_LEGACY_READINESS_PREFLIGHT_RECOVERY_V2_RESULT.md`

Decision: `READY_FOR_V12_IMPLEMENTATION_WITH_MVP`.

Key durable implementation decisions:

- existing `bridge/collector_single_instance.py` Windows named mutex: **ADAPT_AND_REUSE**;
- existing `bridge/unified_collector_agent.py` health/active-task surfaces: **ADAPT_AND_REUSE**;
- Python stdlib (`pathlib`, `json`, `uuid`, `os.replace`, `logging.handlers.RotatingFileHandler`): **DIRECT_USE**;
- WinSW/service installation: **REJECT_FOR_V12_MVP**;
- PowerShell process inspection: **CONCEPT_ONLY / DEFER**;
- no Docker, Redis, broker, service framework, new tray framework, PID-only kill, `taskkill /IM python.exe`, PATH-selected Python, or second agent/launcher stack.

### Acceptance / fixture readiness

`parallel/PM/WOF_UNIFIED_COLLECTOR_V12_ACCEPTANCE_FIXTURE_READINESS_PREFLIGHT_RESULT.md`

Key durable decisions:

- Browser one/10-page isolation, exact World/read-only safety, V10 compatibility, Training Farm selectors/10-worker ROM-free isolation, W3 three-source catalog/DuckDB/reuse behavior are already durably proven and are not confidence-rerun targets.
- V11 terminal already supplied the previously conditional W1->W2 and W2->W3 joins.
- V12 new repository-side tests should focus only on final lifecycle/entrypoint/legacy-retirement/acceptance-harness changes plus directly affected suites if shared core is modified.
- real Windows/Browser/WinKawaks/Training-Farm facts are reserved for one bounded final Owner acceptance after repository gates are green and only where runtime authority permits them.

## Global rules

Read and obey:

- root `AGENTS.md`
- `parallel/PM/PM_CORE_OPERATING_CHARTER.md`
- `parallel/PM/GLOBAL_PM_WORKER_HANDOFF_RULES.md`
- `parallel/PM/GLOBAL_GITHUB_REUSE_FIRST_POLICY.md`
- `parallel/PM/STAGE_DEDUP_GUARD.md`
- `parallel/PM/TESTING_CADENCE_POLICY.md`
- `parallel/PM/OWNER_INTERVENTION_GATE.md`
- `parallel/PM/COLLECTOR_WORKER_EXECUTION_POLICY.md`
- `parallel/PM/COLLECTOR_V9_TO_V12_FINAL_UNIFIED_COLLECTOR_ROADMAP.md`
- `RUNTIME_DATA_SOURCE_BOUNDARIES.md`

## Dedup preflight

Before substantive work, re-read both mains and check:

- this exact V12 START_PROMPT;
- any V12 canonical/stage claim;
- any V12 terminal RESULT;
- recent materially equivalent one-click/final-consolidation implementation;
- any newer V12 recovery/successor.

If equivalent V12 implementation is already ACTIVE/claimed:

`ALREADY ACTIVE / CLAIMED — NO EXECUTION`

If equivalent V12 is already COMPLETE:

`ALREADY COMPLETE — NO EXECUTION`

If superseded, follow the newer authority and do not revive this prompt.

Otherwise acquire and verify a fresh V12 canonical claim and matching stage claim before substantive work.

## V12 scope — smallest final MVP

V12 is not a rewrite. Extend the current V11 system in place.

### 1. Exactly one canonical Windows operator entrypoint

Canonical public entrypoint remains:

`START_WOF_UNIFIED_COLLECTOR.bat`

Required verbs:

```text
START_WOF_UNIFIED_COLLECTOR.bat
START_WOF_UNIFIED_COLLECTOR.bat start
START_WOF_UNIFIED_COLLECTOR.bat stop
START_WOF_UNIFIED_COLLECTOR.bat status
START_WOF_UNIFIED_COLLECTOR.bat health
```

No argument must remain equivalent to `start`.

The BAT must:

- resolve repo root from `%~dp0` and `cd /d` there;
- use only `%~dp0.venv\Scripts\python.exe`;
- fail deterministically if that interpreter is absent;
- never fall back to `where python`, PATH `python`, or `py`;
- delegate lifecycle behavior to one Python lifecycle module;
- never delete a stop/state file before single-instance authority is established.

No second normal public start BAT may be introduced.

### 2. One lifecycle authority

Create/evolve a narrow lifecycle layer, preferably:

`bridge/collector_lifecycle.py`

Reuse the existing named mutex in `bridge/collector_single_instance.py`; preserve the mutex name through migration so old/current collector instances cannot overlap.

Canonical lifecycle state root:

`runtime/collector-v12/`

Required instance-bound atomic JSON state:

- `instance.json`
- `heartbeat.json`
- `stop-request.json`
- lifecycle-owned `tmp/`

At minimum bind lifecycle state to:

- schema version;
- `instanceId`;
- PID;
- UTC start/request/heartbeat times;
- repo root;
- exact Python executable;
- canonical entrypoint.

Use sibling temporary file + `os.replace` for lifecycle JSON writes.

A running Collector must accept a stop request only when `instanceId` matches its current instance. Stale stop requests must never terminate a new instance.

### 3. Deterministic start / stop / status / health

`status` is process/lifecycle truth, not task result truth.

Required states:

- `RUNNING`
- `STOP_REQUESTED`
- `STALE_STATE`
- `STOPPED`

Liveness must not be inferred from PID alone.

`health` must distinguish:

1. process liveness;
2. lifecycle heartbeat freshness / fatal lifecycle error;
3. readiness of the unified Agent/control-plane.

Adapter-specific state remains independent for:

- `browser-wasm`
- `winkawaks`
- `stable-retro-fbneo`

Do not collapse unavailable adapters into a false global READY if the actual readiness contract says otherwise.

`stop` must be idempotent and cooperative. It may wait a bounded interval for mutex release but must not force-kill a process in the MVP.

Prefer the preflight return-code contract unless current implementation facts require a stricter compatible refinement:

- 0 success/healthy;
- 2 prerequisite/config error;
- 3 stopped status;
- 4 duplicate start/already running;
- 5 running but not-ready/unhealthy;
- 6 stale-state or bounded stop timeout.

### 4. Reuse existing Agent health instead of creating a second health plane

`runtime/unified_collector_health.json` remains the canonical domain/operator health document and should be extended with current lifecycle `instanceId`/PID as needed.

`runtime/ACTIVE_TASK.json` remains task-level activity evidence.

Do not create a competing adapter-health database/schema/service.

Canonical operator log should remain one bounded local JSONL log, using Python stdlib rotation only where implementation requires it.

### 5. Legacy retirement / compatibility wrappers

Apply the durable legacy inventory.

Required public dispositions:

- `START_WOF_UNIFIED_COLLECTOR.bat`: becomes the sole V12 canonical start/stop/status/health path.
- `START_WOF_COLLECTOR.bat`: compatibility wrapper only; warning + forwards `%*` to canonical entrypoint.
- `STOP_WOF_UNIFIED_COLLECTOR.bat`: compatibility wrapper to canonical `... stop`; must not independently write a sentinel.
- `STOP_WOF_COLLECTOR.bat`: compatibility wrapper to canonical `... stop`; must not independently write a sentinel.
- `READY_WOF_TASK.bat`: remains retired/blocked.
- historical removed launchers such as `START_WOF_AI.bat`, `START_WOF_ALL*.bat`, `START_WOF_V1.bat`: remain retired and must not be resurrected.
- `bridge/collector_queue_runner.py`, `collector_task_runner.py`, `collector_service.py`, `collector_daemon.py`, `collector_analysis.py`: may remain internal compatibility/reuse surfaces but must not be advertised as second normal operator entrypoints.
- historical direct diagnostic capture tools may remain diagnostic/test-only but cannot compete with the unified public path.

There must be no two maintained overlapping normal production Collector paths after V12.

### 6. Final acceptance harness / evidence bundle

Add one V12-owned deterministic acceptance harness/fixture and maintained CI workflow for **only the V12 change boundary**.

It must automatically verify where repository-side evidence can prove the fact:

- one canonical lifecycle/entrypoint contract;
- compatibility wrappers delegate correctly;
- stale lifecycle/stop-request cannot terminate a new instance;
- duplicate start/single-instance semantics;
- status/health/readiness separation;
- all three adapter states remain surfaced by the one Agent;
- one Git task/result plane remains intact;
- legacy-retirement static gate: no second maintained normal production path;
- exact V11 three-source terminal/data-plane authority remains referenced and not forked.

Do not add a new test framework. Use the existing Python unittest / GitHub Actions approach.

If V12 changes only lifecycle/launcher files, do not rerun V3–V11 broadly. If `bridge/unified_collector_agent.py` or shared adapter base is materially changed, run the directly affected V10/V11 suites once. Escalate to broad V3–V11 regression only for shared-core drift or a real cross-layer defect.

### 7. Real-runtime final acceptance

Do not use Owner as debugger.

Only after V12 repository gates are green and the candidate is frozen may the implementation prepare one bounded Windows acceptance entrypoint/bundle.

The automated acceptance should, as authority/runtime availability permits, cover in one session:

- canonical V12 start/status/health/stop;
- one real eligible WOF Browser page;
- bounded real 10-page Browser case;
- one real WinKawaks/WOF task on the same control/result plane;
- one Training Farm worker;
- bounded 10-worker Training Farm only when Training Farm authority actually permits the live fleet;
- machine verification of IDs/hashes/provenance;
- one three-source DuckDB query preserving source identity;
- one reuse-before-recapture decision proving no silent cross-source semantic reuse;
- one final evidence bundle.

If current Training Farm authority still forbids the real 10-worker fleet, do not bypass or weaken that gate and do not fabricate live proof. Record the precise deferred external/runtime acceptance condition while retaining the already-green ROM-free 10-worker isolation evidence.

Owner should never be asked to manually inspect hashes/schemas/logs or run separate test scripts.

## Safety / architecture invariants

Exactly three maintained source namespaces:

```text
browser-wasm
winkawaks
stable-retro-fbneo
```

Hard invariants:

```text
readOnly=true
writesGameMemory=false
inputInjection=false
one Collector product != one RAM authority
```

Collector must not:

- choose Training Farm actions;
- call Training Farm reset/step/load_state for collection;
- launch/scale Training Farm workers;
- infer RAM/semantic equivalence across sources;
- modify Alpha/product behavior to simplify Collector acceptance.

Do not add a second Git queue, catalog, warehouse, analysis engine, planner, or normal collector daemon.

## Parallel execution authority

A separate PM parallel-dispatch file may assign up to three non-overlapping V12 workstreams. Only the designated coordinator may acquire/close the V12 umbrella canonical/stage authority and write the terminal V12 RESULT. Subworkers use distinct subworkstream dedup keys and must not declare terminal V12 COMPLETE.

## Required terminal RESULT

Write:

`parallel/PM/WOF_UNIFIED_COLLECTOR_V12_FINAL_CONSOLIDATION_ONECLICK_LEGACY_RETIREMENT_RESULT.md`

The terminal RESULT must include:

- exact final repo HEAD/tree;
- consumed V11 terminal authority and both V12 preflight authorities;
- exact lifecycle/entrypoint architecture;
- legacy disposition table;
- dependency/reuse decisions actually implemented;
- V12 focused CI workflow/run/job and test counts;
- any affected V10/V11 regression rerun, only if material SUT change required it;
- source/safety invariants;
- final Owner acceptance status and evidence bundle identity if real-runtime acceptance is legitimately executable;
- any exact external/runtime acceptance item that remains impossible solely because current authority/environment forbids it;
- final statement that one maintained operational Collector product remains.

Then close the V12 canonical/stage claims COMPLETE only when the stage's required repository implementation and authorized acceptance contract are satisfied. Do not silently label an unavailable real-runtime proof PASS.

Terminal success token:

`COMPLETE — WOF UNIFIED COLLECTOR V12 FINAL CONSOLIDATION — ONE GIT-CONTROLLED COLLECTOR / ONECLICK WINDOWS UX / LEGACY RETIRED — FEATURE FROZEN`

Do not stop at a launcher patch, lifecycle helper, fixture, workflow, CI PASS, package, or partial acceptance. Continue through the complete coherent V12 module, durable RESULT and authority closeout, unless a genuinely Owner-required precise BLOCKED remains. Test by complete module boundary, not step-by-step. Report sparingly.
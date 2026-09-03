# WOF Unified Collector V12 — Parallel 3 Worker Dispatch

Status: **PM-AUTHORIZED PARALLEL IMPLEMENTATION SPLIT**

Parent authority:

`parallel/PM/WOF_UNIFIED_COLLECTOR_V12_FINAL_CONSOLIDATION_ONECLICK_LEGACY_RETIREMENT_START_PROMPT.md`

This file supplements the parent. It does not create three Collector products or three terminal V12 authorities.

## One terminal V12 authority

There is exactly one umbrella logical task:

- dedup key: `wof.unified-collector.v12.final-consolidation-oneclick-legacy-retirement`
- terminal RESULT: `parallel/PM/WOF_UNIFIED_COLLECTOR_V12_FINAL_CONSOLIDATION_ONECLICK_LEGACY_RETIREMENT_RESULT.md`

**W1 is the coordinator and the only worker authorized to acquire/close the V12 umbrella canonical/stage claims and write the terminal V12 RESULT.**

W2/W3 must never acquire the umbrella dedup key or declare terminal V12 COMPLETE.

Distinct subworkstream dedup keys:

- W1: `wof.unified-collector.v12.workstream.lifecycle-agent-coordinator`
- W2: `wof.unified-collector.v12.workstream.windows-entrypoints-legacy-retirement`
- W3: `wof.unified-collector.v12.workstream.acceptance-harness-ci`

Subworkstream completion is `SUBCOMPLETE`, not terminal V12 completion.

## Shared starting truth

All workers must re-read current mains before work.

The V11 terminal authority is COMPLETE at:

`parallel/PM/WOF_UNIFIED_COLLECTOR_V11_TERMINAL_INTEGRATION_CLOSEOUT_RECOVERY_V2_RESULT.md`

Final V11 bridge candidate:

`e80257d9486cd3129b115d4e1007bf24335b8852`

V12 preflights already COMPLETE:

- `parallel/PM/WOF_UNIFIED_COLLECTOR_V12_REUSE_LEGACY_READINESS_PREFLIGHT_RECOVERY_V2_RESULT.md`
- `parallel/PM/WOF_UNIFIED_COLLECTOR_V12_ACCEPTANCE_FIXTURE_READINESS_PREFLIGHT_RESULT.md`

Do not repeat their research or historical PASS tests.

## W1 — lifecycle / Agent core + coordinator

Primary implementation repo: `ouyong520/wof-winkawaks-bridge`

W1 owns:

1. V12 umbrella canonical/stage claim and W1 subworkstream claim.
2. `bridge/collector_lifecycle.py` new/equivalent lifecycle core.
3. strict additive changes to `bridge/collector_single_instance.py` as needed to expose reliable mutex/lifecycle authority without creating a second lock primitive.
4. minimal lifecycle integration in `bridge/unified_collector_agent.py`, including instance identity, heartbeat, instance-bound cooperative stop, readiness/health integration and bounded operator log/state behavior.
5. any lifecycle-only internal helper under `bridge/**` needed by this core, provided it does not overlap W2/W3 ownership.
6. lifecycle-focused deterministic self-checks that do not claim final V12 acceptance; coordinate test filenames with W3 to avoid collisions.
7. after W2/W3 durable subresults are visible, re-read their exact landed commits, perform final integration, fix cross-workstream defects, run the final affected V12 CI/regression boundary, write terminal RESULT and close umbrella + W1 claims.

W1 must preserve:

- the existing Windows named mutex identity;
- one Unified Collector Agent;
- one Git task/status/result plane;
- all V11 source/data-stack authority;
- `readOnly=true`, `writesGameMemory=false`, `inputInjection=false`;
- no Training Farm action/control/worker-launch authority.

During parallel phase W1 must not edit W2-owned BAT/docs files or W3-owned acceptance/workflow files. Final integration patches to those surfaces are allowed only after both subresults are durable and W1 has re-read current main.

W1 must not declare V12 COMPLETE merely because repository CI is green if the parent START_PROMPT still requires a legitimate final acceptance disposition. If a real-runtime fact is unavailable solely because Owner/environment/runtime authority is required, record the exact gate and follow the parent authority rather than fabricating PASS.

## W2 — Windows entrypoints + legacy retirement

Primary implementation repo: `ouyong520/wof-winkawaks-bridge`

W2 owns only the Windows entrypoint / legacy-public-surface slice.

Owned production files:

- `START_WOF_UNIFIED_COLLECTOR.bat`
- `START_WOF_COLLECTOR.bat`
- `STOP_WOF_UNIFIED_COLLECTOR.bat`
- `STOP_WOF_COLLECTOR.bat`
- `READY_WOF_TASK.bat` only if a minimal explicit-retired message adjustment is required
- a V12 legacy classification/owner UX document if useful, under existing docs convention

Required behavior:

- sole canonical public entrypoint is `START_WOF_UNIFIED_COLLECTOR.bat`;
- no arg == `start`;
- support `start`, `stop`, `status`, `health` by delegating to the W1 lifecycle Python entry contract described by the parent START_PROMPT;
- resolve `%~dp0`, use only `.venv\Scripts\python.exe`, no PATH/`py` fallback;
- `START_WOF_COLLECTOR.bat` becomes warning compatibility wrapper forwarding `%*`;
- both STOP BATs become wrappers to canonical `... stop` and must not write their own sentinel;
- retired historical start paths stay retired and are not resurrected;
- internal legacy runners/services remain internal-only, not advertised as parallel public collectors.

W2 must not modify:

- `bridge/collector_lifecycle.py`;
- `bridge/collector_single_instance.py`;
- `bridge/unified_collector_agent.py`;
- adapters/data stack;
- W3 tests/workflow/harness.

If the lifecycle module is not yet landed, implement strictly to the parent contract and keep the BAT boundary thin. Do not create an alternative lifecycle implementation in BAT/PowerShell.

W2 may run cheap BAT/static self-checks but must not run broad V3–V11 regressions.

Required durable output:

`parallel/PM/WOF_UNIFIED_COLLECTOR_V12_W2_WINDOWS_ENTRYPOINTS_LEGACY_RETIREMENT_SUBRESULT.md`

Then close only the W2 subworkstream claim as `SUBCOMPLETE` and state:

`V12 terminal authority not claimed`.

## W3 — V12 acceptance harness / focused CI

Primary implementation repo: `ouyong520/wof-winkawaks-bridge`

W3 owns only the verification/acceptance infrastructure for V12; it must not change normal production runtime behavior.

Owned files should be confined to:

- new V12 acceptance/fixture tests under `tests/**` with unique V12 filenames;
- a new V12 acceptance helper/runner under a test/tools/docs location that is clearly non-production, if needed;
- one V12-focused GitHub Actions workflow under `.github/workflows/**`;
- acceptance fixture/data/docs required by that harness.

Required repository-side coverage:

1. canonical start/stop/status/health entrypoint contract;
2. compatibility wrappers delegate and forward arguments correctly;
3. stale stop/lifecycle state cannot target a new instance;
4. duplicate-start/single-instance semantics;
5. lifecycle `status` vs `health` vs readiness separation;
6. all three adapter states remain visible in the one Agent health surface;
7. one Git task/status/result family remains the only normal plane;
8. legacy-retirement static gate: no second maintained normal production Collector path;
9. V11 terminal authority is consumed, not forked or replaced;
10. acceptance bundle schema/helper verifies machine-readable IDs/hashes/provenance and can represent real-runtime `PASS`, precise `BLOCKED`, or authority-gated/deferred facts without fabricating live proof.

W3 must consume the already-COMPLETE acceptance-preflight matrix. It must not rebuild V10/V11 isolation/data-stack tests.

Parallel-phase rule: if W1/W2 production surfaces have not landed yet, W3 may build fixture/harness infrastructure against the parent contract, but must not commit a knowingly permanently failing maintained workflow. Before writing the durable subresult, re-read current main and, if W1/W2 commits are visible, run the focused V12 harness against the real landed surfaces. If they are not yet visible, keep the result explicit about the pending integration dependency and stop `SUBCOMPLETE` only when the harness itself is complete and integration-ready.

W3 must not modify:

- any BAT launcher/stop file;
- `bridge/collector_lifecycle.py`;
- `bridge/collector_single_instance.py`;
- `bridge/unified_collector_agent.py`;
- adapters or data stack;
- Training Farm / Alpha.

Required durable output:

`parallel/PM/WOF_UNIFIED_COLLECTOR_V12_W3_ACCEPTANCE_HARNESS_CI_SUBRESULT.md`

Then close only W3 claim as `SUBCOMPLETE` and state:

`V12 terminal authority not claimed`.

## Merge / sequencing rules

1. All three workers do canonical dedup preflight before substantive work.
2. W1 alone owns umbrella V12 authority; W2/W3 use only their distinct subworkstream keys.
3. Re-read current main before every shared-repo mutation. Never overwrite another worker's newer commit.
4. Keep commits small/coherent; no force push.
5. File ownership boundaries are mandatory during parallel implementation.
6. W2 and W3 stop after durable `SUBCOMPLETE`; they do not run terminal V12 closeout.
7. W1 waits for or consumes W2/W3 subresults, then performs the only final cross-workstream integration review.
8. Final regression scope follows material SUT change. Do not ritualistically replay all V3–V11 tests when V12 only changed lifecycle/entrypoint surfaces.
9. If W1 materially changes `unified_collector_agent.py`, rerun directly affected V10/V11 suites once plus V12 focused tests. Broad V3–V11 only if shared-core drift/defect blast radius justifies it.
10. Only W1 writes terminal V12 RESULT and closes umbrella claims.
11. V12 COMPLETE => Collector FEATURE FROZEN. No V13/V14 without a real new requirement/defect.

## Final success condition

Exactly one maintained Windows operator path controls exactly one Unified Collector Agent. That Agent exposes Browser/WASM, WinKawaks and Stable-Retro/FBNeo adapters on one Git task/status/result and one source-aware data/research stack. Legacy public duplicates are compatibility-only or retired. Repository evidence is green on the V12 change boundary, and real-runtime acceptance is either legitimately proven in one bounded automated session or precisely gated without fabricating evidence.

# WOF Unified Collector V12 — Terminal Integration Closeout Recovery V2 — START PROMPT

Status: **PM-AUTHORIZED TERMINAL RECOVERY**

## Why this recovery exists

The original V12 W1 terminal coordinator acquired the umbrella + W1 authority and landed the lifecycle core / Unified Agent lifecycle binding, but then stopped before terminal integration, final affected regression/CI, durable V12 RESULT, and W1/umbrella closeout.

W2 and W3 are already durable **SUBCOMPLETE** and MUST NOT be redone:

- W2 Windows entrypoints / legacy retirement sub-result:
  `parallel/PM/WOF_UNIFIED_COLLECTOR_V12_W2_WINDOWS_ENTRYPOINTS_LEGACY_RETIREMENT_SUBRESULT.md`
- W3 acceptance harness / focused CI sub-result:
  `parallel/PM/WOF_UNIFIED_COLLECTOR_V12_W3_ACCEPTANCE_HARNESS_CI_SUBRESULT.md`

The current bridge candidate already contains:

- canonical Windows entrypoint + legacy wrappers;
- `bridge/collector_lifecycle.py` instance-bound lifecycle core;
- Unified Agent lifecycle binding;
- W3 acceptance harness, schema, fixtures, and focused CI;
- all completed V11 three-source Unified Collector/data-plane authority.

This recovery exists only to finish the stopped W1 terminal responsibility.

## Repositories

- `ouyong520/wof-ai-private`
- `ouyong520/wof-winkawaks-bridge`

## Dedup / authority

- dedup protocol: `v2`
- dedup key: `wof.unified-collector.v12.terminal-integration-closeout-recovery-v2`
- dedup mode: `exclusive`
- stageId: `WOF_UNIFIED_COLLECTOR_V12_TERMINAL_INTEGRATION_CLOSEOUT_RECOVERY_V2`

Before execution:

1. read current main in both repos;
2. read root `AGENTS.md`, global reuse/testing/handoff rules, V12 parent START_PROMPT and 3-worker dispatch;
3. verify W2 and W3 durable SUBCOMPLETE authority;
4. verify original V12 umbrella/W1 claims remain ACTIVE only because the original W1 worker stopped;
5. verify no equivalent ACTIVE/COMPLETE terminal recovery already exists.

If equivalent recovery is ACTIVE/COMPLETE/superseded: **NO EXECUTION**.

Acquire only this recovery canonical/stage authority. Do not create a second V12 implementation umbrella and do not re-run/re-claim W2 or W3.

## Hard architecture invariant

There is exactly **one Unified Collector product**:

`one Unified Collector Agent -> browser-wasm adapter + winkawaks adapter + stable-retro-fbneo adapter`

Adapters are modules, not separate collectors.

Maintain exactly:

- one canonical start/stop/status/health entrypoint;
- one Agent;
- one Git task/status/result plane;
- one dataset/provenance stack;
- one retention/storage stack;
- one DuckDB warehouse/query plane;
- one analysis/reuse planner.

Do not introduce a browser collector, WinKawaks collector, or Training Farm collector as separate maintained products/services.

## Recovery scope

Consume the existing landed W1/W2/W3 work and finish terminal integration only.

Required checks/fixes include, as materially necessary:

1. canonical BAT -> `bridge.collector_lifecycle` dynamic execution works as intended;
2. lifecycle start owns the existing named mutex, creates coherent instance identity, heartbeat and instance-bound stop authority;
3. stale stop requests cannot terminate a replacement instance;
4. duplicate start fails closed through the existing single-instance authority;
5. lifecycle status / process health / Agent readiness remain distinct and machine-readable;
6. one Agent health surface exposes all three adapter namespaces:
   - `browser-wasm`
   - `winkawaks`
   - `stable-retro-fbneo`
7. one established Git queue/status/result plane remains authoritative;
8. old START/STOP public surfaces remain compatibility-only wrappers and retired READY path stays retired;
9. W3 machine-readable acceptance bundle correctly binds the final integrated candidate;
10. no duplicate runtime/queue/data stack/warehouse/planner is introduced.

Fix real cross-component defects if found. Do not expand V12 scope.

## Testing cadence

Use the complete integrated V12 candidate as the test boundary.

Do not rerun historical V10/V11 PASS suites merely for confidence when their material SUT did not change.

Run only the final affected regression/CI needed for the material V12 surfaces, including lifecycle/Agent/entrypoint/acceptance integration and any historically affected compatibility tests required by an actual fix.

The final CI must bind the exact final bridge commit used in the durable RESULT.

## Safety

Preserve:

- `readOnly = true`
- `writesGameMemory = false`
- `inputInjection = false`
- exact World/source identity boundaries
- no Training Farm reset/step/load_state/action selection
- no real 10-worker fleet launch
- no Alpha production changes.

## Terminal durable closeout

On success, write/update the canonical V12 terminal RESULT:

`parallel/PM/WOF_UNIFIED_COLLECTOR_V12_FINAL_CONSOLIDATION_ONECLICK_LEGACY_RETIREMENT_RESULT.md`

RESULT must record at minimum:

- exact final bridge HEAD/tree;
- exact consumed W2/W3 sub-results;
- final lifecycle/Agent/entrypoint integration facts;
- final affected regression/CI run and counts;
- machine-readable acceptance bundle authority;
- proof of one Unified Collector / three adapters / one Git-data plane;
- safety invariants;
- any real-runtime acceptance still intentionally not manufactured by repository fixtures.

Then reconcile and close:

- recovery canonical/stage claims COMPLETE;
- original V12 W1 claim COMPLETE/superseded-by-this-terminal-recovery as appropriate under canonical dedup v2;
- original V12 umbrella canonical/stage COMPLETE using the existing umbrella authority lineage.

Do not leave stale ACTIVE terminal claims after a COMPLETE verdict.

## Success verdict

`COMPLETE — WOF UNIFIED COLLECTOR V12 FINAL CONSOLIDATION / ONECLICK / LEGACY RETIREMENT — ONE COLLECTOR + THREE ADAPTERS TERMINAL COMPLETE`

After this terminal COMPLETE, Collector feature work is **FROZEN**. Do not create V13/V14 for activity.

Only stop on:

- terminal COMPLETE above; or
- a precise blocker that genuinely requires Owner action and cannot be resolved from source/CI/fixtures.

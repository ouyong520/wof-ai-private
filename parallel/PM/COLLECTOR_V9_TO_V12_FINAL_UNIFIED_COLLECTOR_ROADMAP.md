# Collector V9→V12 Final Unified Collector Roadmap

Owner authority date: 2026-09-03

## Final Owner decision

The WOF program must converge to exactly **one operational collection system**.

Final collection flow:

```text
Git collection requirement / task
        |
        v
WOF Unified Collector Agent
        |
        +--> browser-wasm adapter
        +--> winkawaks adapter
        +--> stable-retro-fbneo / Training Farm adapter
        |
        v
one task/status/result plane
one dataset/provenance model
one retention/storage layer
one warehouse/query layer
one analysis/planning layer
```

There must not be a separately maintained Browser collector product, WinKawaks collector product, or Training Farm collector product after V12. Multiple source adapters are allowed and required because the runtimes differ, but they are modules of one Collector runtime and one Git-controlled task plane.

The implementation foundation remains:

`ouyong520/wof-winkawaks-bridge`

Do not create a second replacement collector repository. Extend/reframe the existing Collector into the final Unified Collector.

The PM / authority / research repository remains:

`ouyong520/wof-ai-private`

This repository split is only source-code/project-management responsibility; it does not authorize two collector products.

## One Git control plane

All normal collection requirements are submitted through Git using one versioned task envelope.

Every task must explicitly specify:

- `sourceNamespace`;
- target selector / runtime identity constraints;
- capture action/type;
- region/fields/raw representation;
- duration/rate/bounds;
- structured experiment metadata;
- raw retention/upload policy;
- reuse/planning policy where applicable;
- read-only / safety requirements.

The local Unified Collector mechanically consumes the Git task, validates it, binds the requested source runtime(s), captures evidence, and returns status/result artifacts through one task/result system.

The Owner must not edit code/scripts to change ordinary collection requirements.

## Supported source namespaces

Final maintained source namespaces:

```text
browser-wasm
winkawaks
stable-retro-fbneo
```

Operational unification does **not** mean offset/semantic authority unification.

Hard rule:

```text
one Collector product != one RAM authority
```

Browser/WASM offsets, WinKawaks normalized offsets, and Stable-Retro/FBNeo offsets/lifecycle identities remain source-specific unless explicit calibration evidence maps them.

Every task/capture/segment/dataset/result must carry source namespace plus runtime/session/worker provenance.

## Browser collection requirement

The final Collector must support the Owner workflow:

```text
1. start one Unified Collector
2. open up to 10 eligible WOF Browser pages/tabs/windows
3. Git publishes Browser collection task
4. Collector discovers requested Page -> Worker -> WASM targets
5. Collector captures requested data for one/many/all eligible pages
6. each page/session remains independently identified and hashed
7. results return through the same task/result plane
```

No separate Browser collector service/launcher is allowed for the normal final path.

Browser collection remains read-only by default:

```text
writesGameMemory=false
inputInjection=false
```

Collection must not modify `product/alpha/**`, danger/target semantics, Transport, Recorder, PYLAUNCH, OneClick, or Alpha production behavior merely to make the Collector easier to implement.

Reuse existing proven Browser Worker/WASM discovery and read-only capture knowledge where safe. Prefer a maintained browser-control/CDP dependency such as Playwright rather than reimplementing browser plumbing; exact dependency/version must be verified/pinned during V10 implementation preflight.

## WinKawaks collection requirement

All existing V3–V9 WinKawaks capability remains available, but as the `winkawaks` adapter inside the Unified Collector.

Preserve/reuse rather than rewrite:

- raw snapshots/bursts;
- long segmented capture;
- immutable dataset identity/catalog;
- retention/archive/pressure guard;
- segment-aware analysis;
- local serial batch acquisition;
- DuckDB warehouse/query;
- reuse-first planning.

After V12 the Owner must not need to run a separate WinKawaks Collector daemon for normal collection.

## 10训 / Training Farm collection requirement

The Unified Collector must also be able to collect data from the running Training Farm / Stable-Retro + FBNeo environment through the `stable-retro-fbneo` adapter.

This means Git tasks may request collection from one or more Training Farm workers, including up to the currently supported 10-worker fleet, subject to bounded resource budgets.

Collector-visible Training Farm evidence may include, as explicitly requested and supported:

- RAM/observation snapshots;
- bounded observation streams;
- worker/runtime identity;
- episode/trajectory metadata;
- action/result trajectory records already produced by Training Farm;
- savestate/root/branch identity metadata already produced by Training Farm;
- timing/performance/resource observations;
- structured experiment/trial metadata.

The Collector is the collection/data plane, not the training-control plane.

Therefore the Unified Collector must **not** take ownership of:

- PPO/RL/policy execution;
- selecting gameplay actions;
- training action injection;
- reset/step policy decisions;
- savestate-search control decisions;
- 10-worker training scheduling/orchestration.

Training Farm may continue to execute/train. The Collector attaches as a source-aware observation/export adapter and records the resulting evidence through the one shared collection/data system.

There must not be a separately evolving generic Training Farm collector/catalog/warehouse if the same functionality belongs in the Unified Collector. Source-specific runtime hooks may remain in `training/farm/**`, but their normal collection output must feed the shared Collector task/result/dataset contracts.

## V9 status

At roadmap creation, V9 is already legitimately ACTIVE under its current canonical/stage claim. Do not steal/restart/broaden it mid-flight.

V9 remains the existing reuse-first WinKawaks experiment planner / gap-to-batch compiler and must finish normally with durable RESULT + canonical/stage COMPLETE before the next convergence stage begins, unless precisely BLOCKED.

## V10 — Unified Agent Foundation + Browser/WASM Multi-Page Adapter

Primary goal: first real operational merge.

Required:

1. introduce one Unified Collector Agent process in the existing implementation repo;
2. introduce strict versioned source-adapter interface;
3. wrap existing WinKawaks runtime as `winkawaks` adapter rather than rewrite V3–V9;
4. add `browser-wasm` adapter;
5. support bounded discovery/binding of up to 10 eligible Browser pages and their exact Worker/WASM generations;
6. one Git task intake/status/result plane for Browser and WinKawaks;
7. per-page/session fail-closed identity; never splice two pages/workers;
8. Agent health shows adapter state, discovered Browser sessions and WinKawaks runtime;
9. keep read-only collection boundary;
10. use maintained browser automation/CDP project via DIRECT_USE/ADAPT where possible, no unnecessary fork/vendor.

V10 completion means Owner can start **one service** and use it for Browser or WinKawaks collection.

## V11 — Training Farm Adapter + Unified Task/Data Stack

Primary goal: make all three requested collection sources use the same generic data system.

Required:

1. add `stable-retro-fbneo` / Training Farm collection adapter;
2. allow explicit Git tasks to target one worker, worker set, or bounded all-active-worker set;
3. preserve worker/episode/root/branch/runtime identities exactly;
4. ingest existing Training Farm trajectory/observation evidence without changing training-control semantics;
5. generalize task envelope from V10 to all three namespaces;
6. one task/hash/queue/status/result model;
7. one immutable source-aware dataset/provenance catalog derived from V4 concepts;
8. one retention/archive/pressure layer derived from V5;
9. one analysis/result envelope derived from V6 with source-specific readers;
10. one collection batch/scheduling layer derived from V7 where applicable;
11. one multi-source DuckDB warehouse derived from V8;
12. one reuse-first planner generalized from V9;
13. migrate/consume historical WinKawaks/Browser/Training Farm evidence with explicit migration provenance, never synthetic re-attribution;
14. cross-source query/join must retain source columns and provenance by default.

After V11, there is one generic collection/data stack. Remaining source-specific components are adapters, compatibility code, runtime hooks, or fixtures—not independent collector products.

## V12 — Final Consolidation / OneClick Unified Collector / Legacy Retirement

Primary goal: final feature-complete freeze.

### Exactly one Owner runtime

Normal Windows UX must expose one start and one stop path, e.g.:

```text
START_WOF_UNIFIED_COLLECTOR.bat
STOP_WOF_UNIFIED_COLLECTOR.bat
```

The launcher/status view must show:

- Git task/control-plane connectivity/configuration;
- Browser adapter + discovered eligible page count/identities;
- WinKawaks adapter/runtime state;
- Training Farm adapter + worker count/identities;
- active/queued task(s);
- resource-budget state;
- latest result/error/BLOCKED reason.

### One Git collection workflow

Examples of ordinary final requests:

```text
source=browser-wasm -> capture one page
source=browser-wasm -> capture all 10 eligible pages
source=winkawaks -> segmented long capture
source=stable-retro-fbneo -> collect worker 3 observations
source=stable-retro-fbneo -> collect all 10 worker trajectory metadata
```

All use the same top-level task/result family and source-specific payloads.

### One shared research stack

Final maintained stack:

```text
Git task plane
-> adapter binding
-> collection
-> immutable provenance/dataset identity
-> retention/storage
-> analysis
-> DuckDB warehouse/query
-> reuse-first planning
```

No source may silently bypass the common provenance/data-integrity layer for normal collection.

### Legacy retirement

Inventory every historical collection entrypoint/script/service and classify:

- `MIGRATED_TO_UNIFIED_AGENT`
- `COMPATIBILITY_ONLY`
- `TEST_FIXTURE_ONLY`
- `DEPRECATED_DO_NOT_USE`
- `REMOVED`

There must be no two maintained production collection paths with overlapping purpose after V12.

Alpha-specific Recorder/proof tooling may remain if its purpose is acceptance/proof rather than general research collection. It must not be advertised/maintained as a second general Collector product.

### Final Owner acceptance

At minimum prove:

1. one Unified Collector starts successfully on Windows;
2. one Browser task can capture one eligible WOF page;
3. one Browser task can capture 10 eligible pages without cross-page mixing;
4. one WinKawaks task uses the same control/result plane;
5. one Training Farm task captures one worker;
6. one Training Farm task captures the bounded 10-worker set without worker mixing;
7. task/result/dataset provenance is source-specific and independently verifiable;
8. shared warehouse can query all three namespaces while preserving source identity;
9. reuse-before-recapture works without cross-source semantic guessing;
10. old duplicate normal collection launchers are retired/deprecated.

## Dependency/reuse direction

Preserve current direct-use decisions:

- DuckDB 1.5.5 for derived warehouse/query;
- APScheduler 3.11.3 where bounded local scheduling is still needed.

Re-evaluate before implementation:

- Playwright Python as preferred Browser/CDP integration candidate;
- psutil for process/worker/resource discovery where useful.

Continue to DEFER unless measured need appears:

- Polars;
- Prefect;
- OR-Tools.

Follow:

- `parallel/PM/PROJECT_EXTERNAL_GITHUB_REUSE_POLICY.md`
- `parallel/PM/COLLECTOR_EXTERNAL_GITHUB_REUSE_POLICY.md`

## Safety / authority

Unified Collector is an observation/data system.

Default collection invariants:

```text
writesGameMemory=false
inputInjection=false
```

Training Farm itself may inject actions because it is a training runtime; those actions are not authorized or chosen by the Collector. Collector may record them as evidence if exposed by Training Farm.

Never silently transfer numeric offsets/runtime authority across source namespaces.

## Dedup / testing / completion policy

All V9→V12 implementation tasks must obey canonical dedup v2, stage dedup guard, duplicate-forward detection and current authority.

Do not manufacture implement/QA/fix loops. Complete each coherent version, run implementation self-check/current regression, repair real defects, produce durable RESULT, and close canonical/stage claims.

If an existing equivalent version/recovery is ACTIVE/COMPLETE/superseded, do not execute duplicate work.

## Post-V12 policy — FEATURE FROZEN

After V12 COMPLETE, the Unified Collector enters stable/feature-frozen mode.

Default allowed follow-up work:

- actual defects;
- supported Browser/Windows/runtime compatibility fixes;
- data-integrity/security fixes;
- measured performance bottlenecks;
- explicitly approved new source adapter when genuinely necessary.

Do not continue V13/V14 merely to keep a worker busy.

Final product statement:

**ONE GIT-CONTROLLED WOF UNIFIED COLLECTOR — Browser/WASM + WinKawaks + Training Farm collection — one Agent, one task/result/data stack, source authority kept explicit.**

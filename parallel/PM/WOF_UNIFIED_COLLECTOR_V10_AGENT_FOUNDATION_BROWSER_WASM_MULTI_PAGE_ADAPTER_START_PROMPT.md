# WOF Unified Collector V10 — Unified Agent Foundation + Browser/WASM Multi-Page Adapter

stageId: `WOF_UNIFIED_COLLECTOR_V10_AGENT_FOUNDATION_BROWSER_WASM_MULTI_PAGE_ADAPTER_V1`
dedupProtocol: `v2`
dedupKey: `wof.unified-collector.v10.agent-foundation-browser-wasm-multi-page-adapter`
dedupMode: `exclusive`

Priority: **P0 architecture convergence / P1 acquisition capability**

## Owner final direction

Owner has explicitly decided that the WOF program must end with **one collection product, not two or three**.

Final roadmap authority:

`parallel/PM/COLLECTOR_V9_TO_V12_FINAL_UNIFIED_COLLECTOR_ROADMAP.md`

The final maintained product is:

```text
Git collection requirement/task
        |
        v
WOF Unified Collector Agent
        |
        +--> browser-wasm adapter
        +--> winkawaks adapter
        +--> stable-retro-fbneo / Training Farm adapter   # V11
        |
        v
one task/status/result plane
one source-aware data stack
```

V10 is the first real operational merge. It must make **Browser/WASM + current WinKawaks collection use one Agent and one Git task/result plane**.

Do not create a replacement repository. The implementation foundation remains:

`ouyong520/wof-winkawaks-bridge`

The PM/authority/research repository remains:

`ouyong520/wof-ai-private`

That repository split does not authorize two Collector products.

---

## Duplicate-forward preflight — mandatory

Before substantive work, re-read current `main` in both repositories and verify:

- this exact START_PROMPT;
- `parallel/PM/COLLECTOR_V9_TO_V12_FINAL_UNIFIED_COLLECTOR_ROADMAP.md`;
- canonical/stage claims for this V10 dedup key;
- any same/materially equivalent Unified Collector / Browser adapter RESULT;
- any newer V10 recovery/successor authority;
- current V9 COMPLETE authority;
- current Browser/PYLAUNCH/Fleet source code used as reuse evidence.

If the same/materially equivalent V10 is already legitimately ACTIVE, COMPLETE or superseded, do not execute duplicate implementation:

`DUPLICATE / ALREADY COMPLETE / SUPERSEDED — NO EXECUTION — <current authority>`

Do not create a Recovery generation merely to bypass dedup.

If not duplicate, acquire and verify the canonical dedup-v2 claim and matching stage claim before substantive implementation.

---

## Read and obey

- `parallel/PM/COLLECTOR_V9_TO_V12_FINAL_UNIFIED_COLLECTOR_ROADMAP.md`
- `parallel/PM/COLLECTOR_WORKER_EXECUTION_POLICY.md`
- `parallel/PM/PROJECT_EXTERNAL_GITHUB_REUSE_POLICY.md`
- `parallel/PM/COLLECTOR_EXTERNAL_GITHUB_REUSE_POLICY.md`
- `parallel/PM/TESTING_CADENCE_POLICY.md`
- `parallel/PM/STAGE_DEDUP_GUARD.md`
- `COLLECTOR_ROUTING.md`
- `RUNTIME_DATA_SOURCE_BOUNDARIES.md`

This is implementation, not a fresh QA lane.

Complete the coherent V10 module first, run implementation self-check/current regressions once, repair actual defects, then write durable RESULT and close canonical/stage claims.

---

## Current completed Collector authority — preserve

Collector V9 is COMPLETE.

Final V9 authority:

- bridge HEAD: `9f4e9b4ff918e0abc75d4ffd5f727d39ea991249`;
- bridge tree: `a3c92ead3bb818b887617bd5e9533fa4e3d55900`;
- workflow run: `33660656297`;
- exact V3–V9 regression: **151/151 PASS**;
- V3 segmented: 15/15;
- V4 dataset catalog: 20/20;
- V5 storage retention: 28/28;
- V6 analysis reader: 31/31;
- V7 batch acquisition: 20/20;
- V8 research warehouse: 16/16;
- V9 experiment planner: 21/21;
- V9 RESULT: `parallel/PM/WINKAWAKS_COLLECTOR_V9_REUSE_FIRST_EXPERIMENT_PLANNER_GAP_TO_BATCH_COMPILER_RESULT.md`;
- V9 canonical and stage claim are COMPLETE.

Do not rewrite V3–V9 merely to make V10 look unified.

Existing WinKawaks functionality must remain available through a source adapter/wrapper and preserve exact task/result/data authority.

---

## Current WinKawaks control plane — reuse, do not replace

Current implementation already has a useful Git-controlled operational path:

```text
tasks/queue/<taskId>.json
-> discover_pending_tasks()
-> taskBlobSha binding
-> status/by_task/<taskId>.json
-> execution
-> results/by_task/<taskId>.json
-> latest compatibility pointer
```

Key existing implementation includes:

- `bridge/collector_service.py`;
- `bridge/collector_queue_runner.py`;
- `bridge/collector_task_runner.py`;
- current V3 segmented authority;
- current V4–V9 data/research stack.

V10 must evolve this into a source-aware Unified Agent instead of creating a second Browser queue/service beside it.

---

## Current Browser authority/reuse evidence — preserve safety

The Browser side already contains proven read-only discovery/identity knowledge in `ouyong520/wof-ai-private`.

Relevant current sources include, at minimum:

- `parallel/PYLAUNCH/wof_launcher/cdp.py`;
- `parallel/PYLAUNCH/wof_launcher/discovery_v2.py`;
- `parallel/PYLAUNCH/wof_launcher/probe.py`;
- `parallel/BROWSER_FLEET/fleet_discovery_v2.py`;
- `parallel/BROWSER_FLEET/fleet_manager.py`;
- `parallel/RUNTIMESPEED_PROBE/browser_capture.js`.

Reuse the proven mechanics/algorithms/contracts as source material. Do **not** make the final Collector depend at runtime on mutable Alpha/product state or modify `product/alpha/**` to expose data.

Current proven Browser discovery model:

```text
localhost Chrome/Edge CDP
-> page target
-> Target.setAutoAttach(flatten=true)
-> related iframe/worker topology
-> fixed read-only Worker probe
-> Emscripten Module / HEAPU8 / HEAPU32
-> exact World identity
```

Current exact supported World 921031 CPU-logical SHA-256 authority:

`5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62`

V10 must not weaken that identity merely to increase discovery success.

---

## Mandatory external GitHub reuse preflight

### DIRECT_USE — websocket-client 1.9.2

PM preflight checked `websocket-client/websocket-client` on 2026-09-03:

- actively maintained;
- Apache-2.0;
- latest stable inspected: `v1.9.2`, published 2026-08-31;
- current PYLAUNCH already uses the same dependency family (`websocket-client>=1.8,<2`).

Classification for V10 Browser CDP transport: **DIRECT_USE**.

Prefer a strict pin such as `websocket-client==1.9.2` in the V10 requirement surface unless current compatibility evidence requires another exact 1.x version.

Do not fork/vendor websocket-client.

### DEFER — Playwright Python 1.62.0

PM preflight checked `microsoft/playwright-python`:

- actively maintained;
- Apache-2.0;
- latest stable inspected: `v1.62.0`, published 2026-07-31;
- supports Chromium/Chrome/Edge automation and CDP attachment.

However V10 already has repository-proven WOF Browser discovery built on a narrow source-controlled CDP allowlist. Playwright would introduce a much broader navigation/input/automation surface and another browser-management layer, while exact nested Page→Worker target/generation authority still benefits from the proven raw CDP path.

Classification for V10 MVP: **DEFER**.

This is not permission to reimplement arbitrary WebSocket/CDP transport. Reuse the existing narrow CDP design over `websocket-client`.

If implementation proves a concrete blocker that Playwright uniquely solves, record the evidence and scope the use to read-only attachment/discovery only; do not silently broaden the task.

### DEFER — psutil

`giampaolo/psutil` is actively maintained (BSD-3-Clause) and appropriate for generic process/resource monitoring, but V10 does not need a new process abstraction if current WinKawaks and Browser Fleet identities already provide the required process/session facts.

Classification: **DEFER unless a concrete process-liveness/identity gap appears**.

### Preserve prior decisions

- APScheduler 3.11.3: existing V7 use only;
- DuckDB 1.5.5: existing V8 use only;
- Polars: DEFER;
- Prefect: DEFER;
- OR-Tools: DEFER.

---

# V10 primary goal

Deliver **one local Unified Collector Agent process** that consumes the existing Git collection queue and can execute either:

1. current `winkawaks` collection through the existing implementation; or
2. new `browser-wasm` read-only collection against one or up to 10 explicitly eligible WOF Browser sessions.

V10 completion means the Owner no longer needs a separate normal Browser collection service beside the WinKawaks collection service.

V10 does **not** add Training Farm collection. That belongs to V11.

---

## Required architecture

Preferred shape:

```text
Unified Collector Agent
  |
  +-- Git queue/status/result control plane
  |
  +-- adapter registry
        |
        +-- winkawaks
        |     -> existing V3–V9 capture/runtime code
        |
        +-- browser-wasm
              -> localhost CDP discovery
              -> exact Page/Worker/WASM/World binding
              -> fixed read-only raw capture
```

Source adapters are internal modules, not independently launched Collector products.

Suggested implementation files may include:

- `bridge/unified_collector_service.py`;
- `bridge/source_adapters.py` or package `bridge/adapters/**`;
- `bridge/browser_wasm_adapter.py`;
- `bridge/browser_cdp.py`;
- strict schema under `schemas/**`;
- V10 tests under `tests/**`;
- concise docs under `docs/**`;
- one V10 requirements file if needed.

Exact names may differ if the implementation is simpler, but the architecture and authority requirements may not be weakened.

---

## One versioned Git task envelope

Introduce a strict new source-aware task envelope, suggested version:

`wof_unified_collector_task_v1`

It must include explicit source authority and safety rather than inferring source from action names.

At minimum include:

- `schemaVersion`;
- `taskId`;
- `createdAtUtc` where current queue ordering requires it;
- `issuedBy`;
- `consumerProject` when applicable;
- `sourceNamespace`;
- `action`;
- source-specific `targetSelector`;
- bounded `parameters`;
- structured acquisition/experiment metadata where applicable;
- `operatorGate` compatibility where applicable;
- `readOnly=true`;
- `writesGameMemory=false`;
- `inputInjection=false`.

V10 source namespace allowlist is exactly:

```text
browser-wasm
winkawaks
```

Do not add `stable-retro-fbneo` prematurely. V11 owns that integration.

Unknown keys fail closed unless explicitly versioned.

Booleans/numbers must be strict native values; reject bool-as-int and coercible numeric strings.

Task identity continues to bind the exact Git blob SHA (`taskBlobSha`).

A task may target one source namespace only in V10. Do not create cross-source multi-action transactions.

---

## Legacy WinKawaks task compatibility

Existing valid `wof_collector_task_v1` / `wof_collector_task_v3` queue tasks must continue to work.

Compatibility rule:

- legacy schemas are treated strictly as `winkawaks` compatibility tasks;
- do not infer Browser from legacy action text;
- the new Unified task envelope should dispatch to the same existing WinKawaks runner/capture authority;
- existing taskBlobSha/result duplicate semantics remain valid;
- existing V3 segmented authority remains unchanged;
- current V4–V9 dataset/storage/analysis/warehouse/planner behavior remains unchanged.

Do not copy/paste the WinKawaks runtime into a new adapter implementation. Wrap/delegate to the current code.

---

## Unified queue/status/result plane

Normal V10 collection must use one control plane:

```text
tasks/queue/<taskId>.json
status/by_task/<taskId>.json
results/by_task/<taskId>.json
```

The same Agent polls/discovers pending tasks and dispatches them by source namespace.

Preserve exact duplicate guards:

- same taskId + same taskBlobSha + valid terminal result -> no execution;
- same taskId with changed taskBlobSha is a different immutable task version and must not inherit stale success;
- malformed or detached status/result must not become collection authority.

Every new V10 status/result must explicitly carry `sourceNamespace`.

Do not create `browser_tasks/**`, `browser_results/**`, a second daemon queue, or any other parallel normal control plane.

---

# Browser/WASM adapter

## Browser connection boundary

V10 Browser collection may attach only to explicitly configured/discovered **localhost** Chrome/Edge CDP endpoints.

Allowed host boundary:

```text
127.0.0.1
localhost
::1
```

Do not scan arbitrary LAN/WAN addresses.

Do not expose remote-debugging connectivity as a generic URL supplied by untrusted Git task content.

Prefer explicit local configuration and/or the existing Browser Fleet manifest/known bounded port allocation.

Reject endpoint/port identity mismatch fail-closed.

The Collector may attach to an existing Browser Fleet / dedicated debug profile. It must not require the Owner to open DevTools or paste JavaScript.

---

## Strict CDP method allowlist

Browser adapter must retain a narrow read-only CDP surface.

Allowed minimum methods may include the already-proven set:

```text
Target.getTargets
Target.attachToTarget
Target.detachFromTarget
Target.setAutoAttach
Runtime.enable
Runtime.evaluate
```

If an additional read-only CDP method is genuinely required, document why and test the allowlist.

Forbidden examples include:

```text
Input.*
Page.navigate
DOM mutation
Network.set*
Runtime.callFunctionOn
Debugger mutation
Browser download/control mutation
```

`Runtime.evaluate` must accept only source-controlled fixed probe/capture expressions. A Git task must never provide arbitrary JavaScript/expression text.

No Worker replacement/wrapping, no ObjectURL/Blob worker injection, no game callback invocation, no page navigation.

---

## Exact WOF Browser identity

A Browser capture target is eligible only after fail-closed WOF identity.

At minimum preserve:

1. exact page/Worker association;
2. valid Emscripten Module with shared `HEAPU8` / `HEAPU32` buffer;
3. exactly one supported World program candidate;
4. exact World 921031 CPU-logical SHA-256:
   `5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62`;
5. no ambiguous accepted page/Worker pair for a selector that requires uniqueness.

Wrong/missing/ambiguous identity fails closed.

Do not use page title/URL or `gstyphoon` text as final identity authority. Those are only discovery hints.

---

## Page -> Worker topology and generation authority

Reuse the proven page-session auto-attach model.

Support realistic Chromium topologies such as:

```text
page -> worker
page -> iframe -> worker
page -> shared_worker
```

Discovery must be bounded in depth/session count.

Each accepted Browser session must have an explicit, stable-for-that-live-generation identity derived from authoritative current facts such as:

- local CDP endpoint/port identity;
- browser process/runtime identity when authoritatively available;
- page target ID;
- Worker target/session ID;
- module/heap identity facts;
- exact World 921031 SHA;
- adapter/session generation or equivalent rollover identity.

Do not use URL/title alone as session identity.

On any of these events, revoke the old binding before accepting new capture frames:

- page reload/replacement;
- Worker target replacement;
- CDP disconnect/reconnect;
- Emscripten Module/heap replacement;
- World identity change;
- endpoint/browser process replacement;
- target ambiguity.

Never splice frames from two Worker generations into one capture.

A mid-burst generation change must produce explicit PARTIAL/FAILED target evidence, preserving completed frames if safely attributable, rather than silently continuing under the new Worker.

---

## Browser target selector

Support deterministic bounded selection of one or multiple eligible sessions.

Suggested selector modes:

```text
ONE_EXACT
ALL_ELIGIBLE
EXPLICIT_SET
```

Exact enum naming may differ.

Hard rules:

- maximum accepted target count per task: `10`;
- `ALL_ELIGIBLE` must be bounded by explicit `maxTargets <= 10`;
- if eligible count exceeds the requested/allowed bound, fail closed rather than silently taking the first 10;
- one-target selection must use exact discovered identity/selector facts, never nondeterministic "first page" ordering;
- explicit set must reject duplicate target identities;
- result ordering must be deterministic.

---

## Browser capture actions in V10

V10 minimum Browser capability:

```text
capture_raw_snapshot
capture_raw_burst
```

Do not expand Browser scope merely to mirror every WinKawaks V3–V9 action in one generation.

A later stage may generalize additional actions if needed.

Browser raw capture should reuse the current proven logical CPS RAM acquisition model where appropriate:

- logical range: 64 KiB CPS RAM corresponding to `0xFF0000..0xFFFFFF`;
- source: current World 921031 Browser/WASM HEAP;
- normalize host byte ordering into a documented CPU-logical representation;
- preserve exact bytes-per-sample, sample timestamps, achieved Hz, duration and SHA-256;
- no semantic address interpretation is required to capture raw data.

If V10 introduces a more generic explicit region contract, it must remain allowlisted/bounded and may not become arbitrary WASM memory exfiltration.

Conservative limits should be at least as strict as current Collector/Browser capture limits.

---

## Multi-page collection

One Browser Git task may target up to 10 eligible WOF Browser sessions.

Each target is independently bound and independently reported.

A multi-page task result must contain, per target:

- exact target/session identity;
- page/Worker/runtime provenance;
- World identity SHA;
- capture start/end timestamps;
- requested/achieved sampling facts;
- byte/frame counts;
- raw artifact/path/hash facts;
- terminal disposition;
- generation-change/identity error if any;
- `readOnly=true`;
- `writesGameMemory=false`;
- `inputInjection=false`.

Do not concatenate raw streams from different pages into a source-indistinguishable blob.

If raw data is packed into one task artifact, the container must preserve independently hashed per-target members and an auditable manifest.

Record task-level start skew/end skew when multiple targets are captured, but do not claim strict simultaneity unless actually implemented/measured.

Overall terminal status must be derived explicitly from target results. Do not report whole-task PASS when a required target failed identity/capture.

---

## Browser raw retention/handoff

Reuse the current local-first Collector policy where practical:

- full raw stays local by default;
- explicit upload policy may create gzip artifact(s);
- uploaded artifacts must retain exact taskId/taskBlobSha/source/target identity;
- per-target SHA-256 required;
- Git size limits remain bounded.

Do not upload full Browser RAM merely because the adapter exists.

---

# Unified Agent service

Introduce one Unified Collector service process.

It should own:

- one instance lock;
- one Git queue poller;
- one task dispatcher;
- adapter registry;
- adapter health/discovery state;
- one active-task view;
- one stop path;
- one result/status writer.

V10 may remain serial at the Git-task level. Multi-target work inside one Browser task is permitted only as a bounded implementation detail.

Do not run two daemon processes where one owns WinKawaks and another owns Browser.

---

## Unified health/status

Provide a bounded machine-readable health view, suggested path:

`runtime/unified_collector_health.json`

At minimum include:

- Agent version;
- service started/heartbeat time;
- queue depth;
- active task/source;
- `winkawaks` adapter state;
- `browser-wasm` adapter state;
- discovered eligible Browser session count, capped/detail bounded;
- each Browser session's non-secret identity summary;
- Browser endpoint/Worker/world identity readiness;
- read-only safety flags;
- latest adapter error/revocation reason.

Health/status is diagnostic, not evidence authority.

Do not dump raw memory into health JSON.

---

## V10 launcher / Owner operation

V10 must provide one normal service entrypoint for Browser + WinKawaks collection.

Preferred provisional launcher:

```text
START_WOF_UNIFIED_COLLECTOR.bat
STOP_WOF_UNIFIED_COLLECTOR.bat
```

V12 owns final packaging/legacy retirement, so V10 may retain old launchers as explicit compatibility shims.

If `START_WOF_COLLECTOR.bat` remains, it should either delegate to the Unified Agent or be clearly marked compatibility-only. Do not keep two independently maintained normal daemons.

Normal Owner workflow should be:

```text
start Unified Collector once
-> prepare/open WinKawaks and/or up to 10 eligible WOF Browser pages
-> Git publishes collection task
-> Agent executes the correct adapter
-> Git receives status/result
```

No DevTools, pasted JS, code edits or per-source daemon switching for ordinary collection.

---

# Source authority / provenance

Hard rule:

```text
one Collector product != one RAM authority
```

V10 maintained namespaces:

```text
browser-wasm
winkawaks
```

Never silently translate or reuse numeric offsets across them.

Every status/result/raw manifest must retain source namespace.

Browser output must retain Browser page/Worker/runtime generation authority.

WinKawaks output must retain current task/session/capture/segment authority.

Do not relabel existing WinKawaks datasets as Browser datasets or vice versa.

V10 does not attempt cross-source semantic mapping.

---

# Data-stack boundary for V10

Do **not** prematurely generalize all V4–V9 storage/analysis/warehouse/planning code to Browser in V10.

V10 goal is operational unification:

```text
one Agent
one Git task/status/result plane
browser-wasm adapter
winkawaks adapter
```

V11 owns the larger **Unified Task/Data Stack** generalization across Browser, WinKawaks and Training Farm.

However Browser V10 result/provenance formats must be clean enough for V11 to ingest/migrate without synthetic re-attribution.

Do not create a parallel Browser-only warehouse/catalog that V11 would immediately need to delete.

---

# Training Farm boundary — V11, not V10

V10 must not modify or take ownership of:

- `training/farm/**` runtime semantics;
- Stable-Retro/FBNeo adapter behavior;
- PPO/RL/policy code;
- training action injection;
- savestate-search decisions;
- 10-worker scheduling;
- Training Farm collection/data migration.

Only design the source-adapter interface so V11 can add `stable-retro-fbneo` cleanly.

Do not implement a fake/stub Training Farm adapter that claims support before V11.

---

# Alpha / production boundary

Do not modify or destabilize:

```text
product/alpha/**
danger rules
target semantics
projection authority
Transport
Recorder
PYLAUNCH production/proof behavior
OneClick Alpha packaging
live acceptance proof rules
```

V10 may reuse/read source-controlled Browser discovery/probe algorithms as implementation references, but must not weaken Alpha authority or turn Collector output into production proof.

Browser Collector data is research/acquisition evidence unless separately promoted by the appropriate Browser/product authority.

---

# Required implementation self-check

Complete the coherent V10 implementation, then run one implementation-owned self-check/regression boundary.

At minimum cover:

## Unified envelope / dispatch

- strict new task schema;
- unknown-key rejection;
- native bool/number validation;
- exact sourceNamespace allowlist;
- legacy WinKawaks v1/v3 compatibility;
- deterministic taskBlobSha binding;
- duplicate terminal result no-execution;
- same taskId + changed blob SHA does not inherit old success;
- Browser task cannot dispatch to WinKawaks;
- WinKawaks task cannot dispatch to Browser.

## Browser discovery / identity

- direct Page->Worker topology;
- Page->iframe->Worker topology;
- worker/shared_worker variations already supported by current discovery;
- no page;
- page-only / Worker not ready;
- Module/heap missing;
- wrong World SHA;
- two exact page/Worker pairs when ONE_EXACT expected -> ambiguity fail-close;
- endpoint/port crossing -> fail-close;
- stale/replaced Worker generation invalidates old binding;
- CDP disconnect invalidates old binding;
- fixed CDP allowlist rejects `Input.dispatchKeyEvent`, `Page.navigate`, `Runtime.callFunctionOn` and arbitrary user expression.

## Multi-page

- 1 eligible page;
- 10 eligible pages;
- 11 eligible pages with max 10 -> fail closed, no silent truncation;
- explicit set deterministic ordering;
- duplicate target identity rejection;
- per-target output identity/hash isolation;
- one target generation changes during burst -> no frame splice and overall required-target PASS is withheld;
- no target raw bytes appear under another target's manifest/hash.

## Capture

- snapshot exact 64 KiB logical representation or exact documented bounded region;
- burst monotonic timestamps;
- achieved Hz calculation;
- raw SHA-256 stability;
- read-only flags always present;
- no memory write/input/navigation methods reachable.

## WinKawaks regression

Current V3–V9 regression must remain green. Do not replace it with only new V10 tests.

Target combined current-head smoke should include the maintained **151/151 V3–V9** cases plus V10-specific cases.

---

# Integration smoke

Add/extend maintained CI so current `main` proves, without real game/ROM/browser dependency:

1. all existing V3–V9 tests pass;
2. V10 unified task schema/API/dispatch self-check passes;
3. a deterministic fake/local CDP fixture models exact World-valid one-page Browser capture;
4. a deterministic fixture models 10 independent exact Browser sessions through one Agent task;
5. a wrong/changed Worker/world fixture fails closed;
6. a legacy WinKawaks task still routes through the same Unified Agent control plane;
7. no Browser test can reach input/navigation/write methods;
8. no Training Farm code is imported or modified.

Do not fake a real Browser acceptance claim. Repository fixtures prove implementation wiring only.

A real Owner Browser proof is not required to manufacture repository PASS in V10; final one-page/10-page live acceptance belongs to the V12 final consolidation acceptance unless Owner separately authorizes an earlier bounded live check.

---

# Performance/resource bounds

Browser discovery must be cheap while idle.

Requirements:

- bounded polling;
- bounded target/session recursion;
- max 10 accepted Browser targets per task;
- no continuous full-RAM capture when no task requests it;
- close/detach CDP sessions when not needed;
- stale session cleanup;
- no unbounded in-memory frame accumulation for bursts;
- bounded raw artifact size / streaming or chunking where practical.

Do not let Browser idle health polling materially disturb gameplay.

---

# Documentation

Document at minimum:

- one-Agent architecture;
- source adapter contract;
- unified task schema examples for `winkawaks` and `browser-wasm`;
- Browser target selection;
- exact World identity authority;
- multi-page up-to-10 behavior;
- local CDP configuration / Browser Fleet relationship;
- read-only CDP allowlist;
- raw retention;
- legacy launcher/task compatibility;
- V10 vs V11/V12 boundary;
- dependency decisions and licenses.

Owner-facing instructions should be Simplified Chinese where practical.

---

# Durable RESULT / closeout

Before stopping, write:

`parallel/PM/WOF_UNIFIED_COLLECTOR_V10_AGENT_FOUNDATION_BROWSER_WASM_MULTI_PAGE_ADAPTER_RESULT.md`

The RESULT must record:

- verdict;
- exact implementation HEAD/tree;
- exact important blobs/contracts;
- external reuse decisions/versions/licenses;
- unified task/result schema versions;
- adapter versions;
- Browser exact identity rules;
- one-page/10-page fixture results;
- V3–V10 regression counts;
- maintained workflow run/job IDs and result;
- safety invariants;
- intentional limitations deferred to V11/V12;
- proof that no second normal Browser daemon/control plane was created;
- proof that Training Farm was not prematurely modified.

Then close the same V10 canonical and stage claims to COMPLETE using the same claim token/result authority.

Do not stop at:

- claim acquisition;
- adapter interface only;
- schema only;
- Browser discovery only;
- one-page fixture only;
- a single patch;
- unit tests only;
- CI PASS without RESULT/claim closeout.

Allowed final outcomes only:

1. `COMPLETE — WOF UNIFIED COLLECTOR V10 AGENT FOUNDATION + BROWSER/WASM MULTI-PAGE ADAPTER — ONE AGENT / ONE GIT TASK-RESULT PLANE FOR BROWSER + WINKAWAKS COMPLETE`
2. `BLOCKED — <precise unavoidable external blocker and exact evidence>`
3. `DUPLICATE / ALREADY COMPLETE / SUPERSEDED — NO EXECUTION — <current authority>`

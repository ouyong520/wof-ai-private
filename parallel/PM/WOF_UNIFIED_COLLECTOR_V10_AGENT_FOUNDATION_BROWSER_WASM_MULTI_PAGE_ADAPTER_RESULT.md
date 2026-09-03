# WOF Unified Collector V10 — Agent Foundation + Browser/WASM Multi-Page Adapter — RESULT

Date: 2026-09-03

## Verdict

**COMPLETE — WOF UNIFIED COLLECTOR V10 AGENT FOUNDATION + BROWSER/WASM MULTI-PAGE ADAPTER — ONE AGENT / ONE GIT TASK-RESULT PLANE FOR BROWSER + WINKAWAKS COMPLETE**

V10 is complete at the repository implementation boundary. No V11 work was started and no new recovery generation was opened.

## Authority

- PM stageId: `WOF_UNIFIED_COLLECTOR_V10_AGENT_FOUNDATION_BROWSER_WASM_MULTI_PAGE_ADAPTER_V1`
- canonical dedup key: `wof.unified-collector.v10.agent-foundation-browser-wasm-multi-page-adapter`
- claim token: `v10-1de0957eaa9dbecd1f80e7fadcd9145d`
- implementation repository: `ouyong520/wof-winkawaks-bridge`
- V9 bridge baseline: `9f4e9b4ff918e0abc75d4ffd5f727d39ea991249`
- final implementation HEAD: `31ec55650ccce29fad60dcab2ca099425a1ecc0b`
- final implementation tree: `26e621944bc6adcf9a3530eb3e815fe125812fda`

## Concrete V10 CI defect repaired

The maintained V10 CI run `33709022809` failed only at:

`tests.test_unified_collector_agent.BrowserFixtureTests.test_iframe_worker_autoattach_topology_supported`

The failing assertion expected `result["status"] == "PASS"` but received `FAILED`. V3–V9 had already passed 151/151 and the other 35 V10 cases passed.

Root cause was in the Browser CDP adapter session abstraction. Direct worker probing used the transport-owned `client.attach()` session path, while `page -> iframe -> worker` auto-attach discovery constructed `CdpSession(client, targetId, sessionId)` directly. That bypassed the client/session materialization contract for an already-auto-attached child session and made nested topology behavior inconsistent with direct worker behavior.

Fix commit:

`31ec55650ccce29fad60dcab2ca099425a1ecc0b` — `Collector V10: preserve auto-attached session transport semantics`

The production `CdpClient` now exposes an `attached_session(target_id, session_id)` materializer and `attach()` delegates through it. Auto-attached child targets are materialized through the client-owned path; compatibility transports that own their session wrapper behind `attach()` remain supported. The production path keeps the exact Chromium-provided auto-attach `sessionId`. No World identity, write/input safety, target-count, namespace, or Git authority rule was relaxed.

The same final core also enforces the already-required explicit `ALL_ELIGIBLE.maxTargets` bound and records task-level non-simultaneity timing facts; these remain aligned with the product-facing Browser adapter contract.

## Final implementation / important blobs

- `bridge/adapters/base.py` — `6ef4dc39581ebe8b1f0a49a8f2f6016cd764922a`
- `bridge/adapters/winkawaks.py` — `f35f6d268e3ebf7217378b57f55e26ad4b387b47`
- `bridge/adapters/browser_wasm.py` — `f1198295fc4406867d4b46552dd4aa2d826e1000`
- `bridge/adapters/browser_wasm_contract.py` — `6893573c9c055e2e27e3b0cc9c942b8dd77c401c`
- `bridge/unified_collector_agent.py` — `5a80c149d9326df93490ba532d1b463cfac6eda6`
- `schemas/unified_collector_task_v1.schema.json` — `106d7326dab9674ca9fc9c3454929d53aa162ea9`
- `schemas/unified_collector_status_v1.schema.json` — `dac91f1315e5011b5270723157a6d443a7ff7edd`
- `schemas/unified_collector_result_v1.schema.json` — `94de5ce3f83be9867bb379fef4a45076699fced1`
- `tests/test_unified_collector_agent.py` — `9e84620b9752b4c2619af91f10a691e7c4414c3b`
- `.github/workflows/collector-v10-regression.yml` — `e6d8546f7c75dd04ce33253069275a1c9c127ff8`
- `requirements-collector-v10.txt` — `fc72877072d1306b2552b3d92af07ebb85ef220f`
- `docs/COLLECTOR_V10_UNIFIED_AGENT_BROWSER_WASM.md` — `efbdcd323fc98496beb4928f040c55ca6ec4aedd`
- `START_WOF_COLLECTOR.bat` compatibility shim — `6629f497d0899d3c4a1879d45536bfe9be9b6a3b`
- `START_WOF_UNIFIED_COLLECTOR.bat` — `a10c0b4eac82103cbd6ea9961b3736c6945ed788`
- `STOP_WOF_UNIFIED_COLLECTOR.bat` — `10e53b4fcdf47c8e17e53f05588507a913343a02`

## Unified contracts and versions

Unified schema versions:

- task: `wof_unified_collector_task_v1`
- status: `wof_unified_collector_status_v1`
- result: `wof_unified_collector_result_v1`

Maintained source namespace allowlist is exactly:

- `browser-wasm`
- `winkawaks`

Adapter / Agent versions:

- Unified Agent: `wof-unified-collector-agent-v10`
- Browser/WASM adapter: `wof-unified-collector-browser-wasm-adapter-v1`
- WinKawaks adapter: `wof-unified-collector-winkawaks-adapter-v1`

Normal control plane remains exactly one queue/status/result plane:

- `tasks/queue/<taskId>.json`
- `status/by_task/<taskId>.json`
- `results/by_task/<taskId>.json`

Legacy `wof_collector_task_v1` / `wof_collector_task_v3` remain strict WinKawaks compatibility tasks and route through the existing queue runner/result authority rather than a duplicated runtime.

## Browser exact identity and lifecycle authority

Browser/WASM eligibility remains fail-closed and requires:

1. localhost CDP endpoint only: `127.0.0.1`, `localhost`, or `::1`;
2. unique Page/Worker association;
3. valid Emscripten Module with shared `HEAPU8` / `HEAPU32` buffer;
4. exactly one supported World program candidate;
5. exact World 921031 CPU-logical SHA-256:
   `5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62`;
6. stable binding facts covering endpoint/websocket identity, page target, worker target/type, isolate, module/heap/RAM base, World locator/SHA and association topology;
7. pre/post capture generation verification; Worker/page/module/heap/World changes withhold PASS and never splice generations.

Supported bounded topology includes:

- Page -> Worker
- Page -> iframe -> Worker
- Page -> shared_worker

`ALL_ELIGIBLE` is explicitly bounded by native integer `maxTargets <= 10`; exceeding the requested/allowed bound fails closed. Per-target raw artifacts remain independently identified and hashed. Multi-target output does not claim strict simultaneity.

## Capture and safety invariants

Browser V10 actions are limited to:

- `capture_raw_snapshot`
- `capture_raw_burst`

Browser capture is 64 KiB logical CPS RAM (`0xFF0000..0xFFFFFF`) with documented host-lane normalization, timestamps, sample count, achieved Hz and artifact SHA-256. Raw is local-only by default; explicit upload reuses bounded gzip handoff.

Required safety invariants remain exact:

- `readOnly = true`
- `writesGameMemory = false`
- `inputInjection = false`

The source-controlled CDP allowlist remains narrow (`Target.getTargets`, attach/detach/auto-attach, `Page.getFrameTree`, `Runtime.enable`, fixed `Runtime.evaluate`, `Runtime.getIsolateId`). Input, navigation, arbitrary task-supplied JavaScript, `Runtime.callFunctionOn`, debugger mutation, network mutation, DOM mutation, Worker replacement, Blob/ObjectURL injection and game callback invocation remain unreachable by V10 task input.

## Dependency reuse decisions

- `websocket-client==1.9.2` — **DIRECT_USE**, Apache-2.0; narrow raw CDP transport, no fork/vendor.
- Playwright Python 1.62.0 — **DEFER**, Apache-2.0; not introduced because its wider browser-management surface is unnecessary for V10.
- psutil — **DEFER**, BSD-3-Clause.
- APScheduler 3.11.3 — existing V7 use only.
- DuckDB 1.5.5 — existing V8 use only.
- Polars / Prefect / OR-Tools — **DEFER**.

## Maintained regression / CI authority

Superseded failing run:

- workflow run: `33709022809`
- failure: only `test_iframe_worker_autoattach_topology_supported` (`FAILED` vs expected `PASS`)
- V3–V9: 151/151 PASS before the V10 failure

Final maintained run on `31ec55650ccce29fad60dcab2ca099425a1ecc0b`:

- workflow: `Collector V10 Unified Agent Regression`
- workflow run: `33710701482`
- job: `100509341864` (`v3-v10-regression`)
- job conclusion: **success**
- compile maintained V3–V10 Python modules: PASS
- maintained V3–V9 regression: **151/151 PASS**
- V10 fake-CDP + Unified Agent regression: **36/36 PASS**
- combined maintained regression: **187/187 PASS**
- previously failing iframe auto-attach test: **PASS**
- one-page exact World snapshot fixture: **PASS**
- 10-page exact World isolation fixture: **PASS**
- 11-page/max-10 fail-close fixture: **PASS**
- shared-worker fixture: **PASS**
- wrong World SHA fail-close: **PASS**
- Worker generation change withholds PASS: **PASS**
- legacy WinKawaks route-through-existing-runner fixture: **PASS**
- schema/examples/source/safety/launcher boundary gate: **PASS**

The final run checked out exact HEAD `31ec55650ccce29fad60dcab2ca099425a1ecc0b`.

## One Agent / no second normal daemon proof

`START_WOF_UNIFIED_COLLECTOR.bat` starts only `python -m bridge.unified_collector_agent` (or `py -m ...`). Historical `START_WOF_COLLECTOR.bat` is now a compatibility shim that delegates to `START_WOF_UNIFIED_COLLECTOR.bat`; it does not start `bridge.collector_service` or another Browser daemon. The maintained CI has a fail-closed launcher assertion for this boundary.

No `browser_tasks/**`, `browser_results/**`, second Browser queue, or second normal Browser service was introduced.

## Training Farm / Alpha boundary proof

Comparing the completed V9 bridge baseline `9f4e9b4ff918e0abc75d4ffd5f727d39ea991249` to final V10 HEAD `31ec55650ccce29fad60dcab2ca099425a1ecc0b` yields 21 V10 commits affecting only the V10 adapters/agent/contracts/schemas/examples/tests/docs/dependency/workflow and Owner launchers. There are no `training/farm/**` changes and no Alpha production changes.

The final CI source-boundary gate also rejects `training.farm`, `stable_retro`, `stable-retro-fbneo`, and `product/alpha` references in the V10 source set.

## Intentional V11 / V12 deferrals

V10 intentionally does not implement:

- `stable-retro-fbneo` / Training Farm adapter;
- Training Farm runtime semantics, 10-worker scheduling, RL/PPO/action injection;
- Browser-only catalog/warehouse or cross-source semantic offset translation;
- broad V4–V9 Browser data-stack generalization;
- Alpha production/proof/danger/projection/Recorder/Transport changes;
- V12 final consolidation/package/live one-page/10-page acceptance.

Those remain V11/V12 authority. Repository fake-CDP fixtures are implementation wiring evidence only and do not manufacture a real Browser acceptance claim.

## Closeout

Implementation is coherent, maintained regression is green, the concrete iframe auto-attach defect is repaired, the exact World/read-only/identity isolation boundaries remain intact, and V10 is ready for canonical/stage claim closure with the same claim token.

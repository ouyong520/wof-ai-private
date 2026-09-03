# WOF Unified Collector V12 — Acceptance / Fixture Readiness Preflight — RESULT

Date: 2026-09-03

## Verdict

**COMPLETE — V12 ACCEPTANCE / FIXTURE READINESS PREFLIGHT — MINIMAL FINAL EVIDENCE PLAN DURABLE**

This is a read-only preflight result only. It does not declare V12 COMPLETE and does not claim V12 implementation authority.

## Authority / inspected heads

- stageId: `WOF_UNIFIED_COLLECTOR_V12_ACCEPTANCE_FIXTURE_READINESS_PREFLIGHT_V1`
- dedup key: `wof.unified-collector.v12.preflight.acceptance-fixture-readiness`
- claim token: `efe8c23fda8f7a273ca582c4d643265d`
- `ouyong520/wof-ai-private` inspected current main: `631a8af8d5f53d482c762654e7dc5b5b4fe00e75`
- `ouyong520/wof-winkawaks-bridge` inspected current main: `8905732d93032a814e79d6fb3dd8077df0828ac0`
- V10 final implementation authority: `31ec55650ccce29fad60dcab2ca099425a1ecc0b`
- V10 durable RESULT commit: `21fec94b7c132920500e6709d3c76db3fc49be5d`
- V11 W2 reviewed handoff head: `8905732d93032a814e79d6fb3dd8077df0828ac0`
- V11 W3 reviewed handoff commit: `8468c2fed5efeef068bd980c437384885d4f07d4`

The private-repository main moved after this preflight claim was created only through unrelated PM/Alpha authority; the V12 preflight canonical claim remained ACTIVE with the exact token above at the final pre-result recheck.

## Dedup verdict

No equivalent ACTIVE/COMPLETE/superseding V12 acceptance/fixture-readiness preflight existed before claim acquisition. A fresh canonical dedup-v2 claim and matching stage claim were acquired and verified. No V12 umbrella implementation claim was acquired.

This work intentionally does not duplicate `WOF_UNIFIED_COLLECTOR_V12_REUSE_LEGACY_READINESS_PREFLIGHT_V1`; launcher/package inventory and historical legacy-path classification remain that sibling preflight's ownership. This result only records the acceptance implication for the roadmap's legacy-retirement row.

## Current V11 terminal state

The V11 umbrella claim `wof.unified-collector.v11.training-farm-adapter-unified-task-data-stack` is still `ACTIVE` under token `v11-8ae06246ff6533ce7ba6df8d37fc5f93`.

Therefore W1/W2/W3 sub-evidence is reusable durable component evidence, but it must not be promoted to a V11 terminal COMPLETE claim by this preflight. Rows whose only missing authority is the V11 terminal integration are explicitly classified `BLOCKED_BY_V11_TERMINAL_AUTHORITY` below rather than triggering duplicate regressions.

## Durable evidence inventory to reuse

### V10 — Unified Agent + Browser/WASM + WinKawaks

Durable RESULT:

`parallel/PM/WOF_UNIFIED_COLLECTOR_V10_AGENT_FOUNDATION_BROWSER_WASM_MULTI_PAGE_ADAPTER_RESULT.md`

Maintained CI authority recorded by the V11 START_PROMPT / V10 RESULT:

- workflow: `Collector V10 Unified Agent Regression`
- run: `33710701482`
- job: `100509341864`
- V3–V9 maintained regression: `151/151 PASS`
- V10 fake-CDP + Unified Agent: `36/36 PASS`
- combined: `187/187 PASS`
- schema/examples/source/safety/launcher gate: PASS

Current focused surfaces that remain useful:

- `tests/test_unified_collector_agent.py`
- `.github/workflows/collector-v10-regression.yml`

Already-proven fixture facts include:

- one exact-World Browser page capture through the Browser adapter;
- exact World 921031 SHA check and read-only CDP allowlist;
- one 64 KiB raw Browser snapshot with immutable artifact hash;
- bounded `ALL_ELIGIBLE maxTargets=10` validation;
- 10-page fake-CDP capture with 10 distinct page bindings, artifact paths and artifact hashes;
- 11 pages fail closed when the requested bound is 10;
- post-capture Worker/isolate-generation change withholds PASS;
- WinKawaks task validation and routing through the same Unified Agent/task-result family;
- V10 source-specific adapters remain closed to Training Farm implementation authority;
- legacy `START_WOF_COLLECTOR.bat` is checked to delegate to the Unified launcher rather than own a second normal daemon.

None of these green tests need a V12 confidence rerun unless V12 materially changes their SUT.

### V11 W1 — Training Farm source-owned exporter

Current private-repository implementation evidence includes:

- `f87256d576149db00c46275c7a6ffb2ea0f432f7` — source-owned read-only exporter;
- `5eafc04c6cbd37de5dbd15e3999126750445e9c5` — ROM-free exporter isolation fixtures;
- `e49eb6ed596ada6d1fec38347f26ee0e12a71ad5` — ROM-free ten-worker exporter fixture;
- `db20d7d18ac47771452596aaf61208f158fca487` — exporter fixture test.

`training/farm/tests/test_collector_export_fixture.py` proves a 10-worker ROM-free fixture with:

- 10 unique worker IDs;
- 10 unique worker generations;
- 10 unique capture-binding hashes;
- 10 distinct artifact hashes;
- zero real worker launches;
- no Collector `reset`, `step`, `load_state`, process-launch or orchestration authority.

This is strong fixture evidence, not V11 terminal authority. No independent W1 terminal RESULT is promoted here.

The V11 START_PROMPT also records a hard runtime fact important for V12 planning: current Training Farm `StageGuard` permits at most one real emulator worker for the stage, disables real worker launch, and explicitly defers live 10-worker acceptance to V12 once Training Farm authority actually permits that fleet. V12 must not ask the Owner to launch 10 real workers before that authority exists.

### V11 W2 — stable-retro-fbneo adapter / v2 contract / Agent routing

Durable sub-result:

`parallel/PM/WOF_UNIFIED_COLLECTOR_V11_W2_ADAPTER_SCHEMA_AGENT_RESULT.md`

Exact-head focused CI:

- workflow: `Collector V11 W2 Adapter Agent Regression`
- run: `33714170008`
- job: `100519730722`
- exact checkout: `8905732d93032a814e79d6fb3dd8077df0828ac0`
- V10 compatibility: `36/36 PASS`
- V11 W2 adapter/Agent/worker-isolation: `19/19 PASS`
- v2 task/status/result schema checks: PASS
- ONE / WORKER_IDS / ALL_ACTIVE examples: PASS
- no Training Farm control authority static gate: PASS

Current focused surfaces:

- `tests/test_unified_collector_v11_adapter.py`
- `tests/test_unified_collector_v11_worker_isolation.py`
- `.github/workflows/collector-v11-w2-regression.yml`

Already-proven fixture facts include:

- v2 namespace allowlist exactly `browser-wasm`, `winkawaks`, `stable-retro-fbneo` while V10 v1 remains closed to its original two namespaces;
- Training Farm v2 task uses the same `tasks/queue` -> `status/by_task` -> `results/by_task` Agent authority;
- `ONE`, exact `WORKER_IDS`, and bounded `ALL_ACTIVE <= 10` selectors;
- 10-worker ALL_ACTIVE PASS fixture;
- over-bound, stale, unknown/ineligible worker and missing evidence fail closed;
- worker-generation, episode/root/branch and capture-binding continuity checks;
- immutable artifact bytes/hash verification;
- per-worker failure isolation: a corrupt worker cannot splice into or hide a valid sibling result.

### V11 W3 — source-aware V4–V9 shared data stack

Durable sub-result:

`parallel/PM/WOF_UNIFIED_COLLECTOR_V11_W3_UNIFIED_DATA_STACK_SUBRESULT.md`

Focused CI:

- workflow: `.github/workflows/collector-v11-w3-unified-data-stack.yml`
- run: `33714040635`
- job: `100519361741`
- validated commit: `8468c2fed5efeef068bd980c437384885d4f07d4`
- new three-source focused regression: `8/8 PASS`
- existing V4–V9 compatibility: `136/136 PASS`
- total: `144/144 PASS`
- DuckDB exact `1.5.5` / existing V8 DB authority guard: PASS
- source namespaces exactly all three: PASS
- source-local RAM/semantic-authority guard: PASS

Current focused surfaces:

- `tests/test_unified_data_stack_v11.py`
- `.github/workflows/collector-v11-w3-unified-data-stack.yml`

Already-proven fixture facts include:

- one V4 catalog can hold identical task IDs independently under all three source namespaces without identity collision;
- source/runtime/result/artifact/registration provenance remains explicit;
- V5 storage/retention authority is reused rather than forked;
- V6 source readers reject mixed-source semantic interpretation;
- V7 integration reuses the existing queue and is read-only;
- the same V8 DuckDB authority receives source-aware derived projections for all three namespaces;
- reuse-first is exact same-source by default;
- cross-source reuse never follows numeric/name similarity and requires an immutable mapping contract plus explicit authorization.

## V12 acceptance matrix

| Roadmap acceptance requirement | Current classification | Durable evidence already reusable | Exact remaining gap |
|---|---|---|---|
| One Unified Collector start/stop path | `V12_IMPLEMENTATION_THEN_CI` | V10 already has one Unified Agent and launcher compatibility gate; legacy start delegates rather than owning a second normal daemon | V12 must freeze the final single Windows start/stop/status UX after sibling legacy/reuse inventory is consumed. Add only launcher/status/retirement CI for material V12 changes, then one real Windows start/stop acceptance. |
| One Browser task / one eligible page | `REAL_WINDOWS_ACCEPTANCE_INTRINSICALLY_REQUIRED` | V10 `36/36` fake-CDP suite proves exact World identity, one-page binding, read-only capture, artifact hash and fail-closed semantics | Logic is already proven. Final roadmap still requires one actual eligible WOF Browser page on Windows so real Page->Worker->WASM discovery/runtime compatibility cannot be replaced by fake CDP. |
| One Browser task / 10 eligible pages, no cross-page splice | `REAL_WINDOWS_ACCEPTANCE_INTRINSICALLY_REQUIRED` | V10 fixture proves 10 distinct binding hashes / artifact paths / artifact hashes; 11-over-bound fails closed | Do not rewrite the 10-page isolation fixture. Final V12 still needs one bounded real 10-page WOF Browser run to prove runtime discovery/scaling. Cross-page integrity should be machine-verified from the evidence bundle, not manually inspected. |
| One WinKawaks task through same Git control/result plane | `REAL_WINDOWS_ACCEPTANCE_INTRINSICALLY_REQUIRED` | V10 Unified Agent task validation/routing and V3–V9 compatibility are durable; V11 v2 preserves closed V10 compatibility | Same-plane semantics do not need another synthetic proof unless V12 changes Agent routing. Final acceptance still needs one actual Windows WinKawaks/WOF task through the single V12 entrypoint/control plane. |
| One Training Farm worker | `BLOCKED_BY_V11_TERMINAL_AUTHORITY` | W1 source-owned exporter fixture + W2 ONE selector/read-only adapter/same Git result-plane evidence are already strong | V11 umbrella is still ACTIVE. Terminal integration must first freeze the real W1-exporter <-> W2-adapter contract. If terminal evidence does not directly join them, V12 needs one ROM-free cross-repo fixture join, not new production code. |
| Bounded 10-worker Training Farm, no worker mixing | `BLOCKED_BY_V11_TERMINAL_AUTHORITY` | W1 builds 10 unique worker/generation/binding/artifact fixtures with zero launches; W2 `19/19` includes 10-worker PASS, over-bound rejection and per-worker corruption isolation | First consume V11 terminal authority. Separately, the V11 START_PROMPT explicitly leaves live 10-worker proof to V12 only after Training Farm authority permits such a fleet. No Owner request is valid before that gate is lifted. |
| Source-specific task/result/dataset provenance | `BLOCKED_BY_V11_TERMINAL_AUTHORITY` | W2 binds v2 task/result/worker artifact identity; W3 `8/8` proves three-source catalog/runtime/result/artifact provenance and no semantic promotion | Component evidence is already durable. Only the terminal W2-result -> W3-registration evidence join is not yet frozen as umbrella authority. If V11 terminal does not prove it, add one CI fixture join. No real WOF is intrinsically needed for this row. |
| One shared DuckDB query surface preserving source identity | `BLOCKED_BY_V11_TERMINAL_AUTHORITY` | W3 `144/144` focused+compatibility run proves one DuckDB 1.5.5 authority, three-source projections and preserved runtime/source provenance | Wait for V11 terminal authority; no new warehouse test framework or real WOF acceptance is needed unless V12 changes the data-stack SUT. |
| Reuse-before-recapture without cross-source semantic guessing | `BLOCKED_BY_V11_TERMINAL_AUTHORITY` | W3 proves exact same-source reuse default, missing-capture disposition, immutable mapping-contract gate and no numeric/name semantic guessing | Wait for V11 terminal authority. If unchanged, reuse this durable evidence; no Owner/manual WOF proof is needed. |
| Legacy production-path retirement evidence | `V12_IMPLEMENTATION_THEN_CI` | V10 launcher compatibility already prevents one old launcher from owning a second daemon | Exact legacy inventory/classification is intentionally owned by the sibling V12 reuse/legacy preflight and is not duplicated here. V12 should consume that inventory, change only final production paths, and add a deterministic static/entrypoint retirement gate. |

## What is already proven vs. what is not

### Already durably proven at the component/fixture level

1. Browser one-page and bounded 10-page identity/isolation logic.
2. Browser exact World/read-only/fail-closed safety logic.
3. WinKawaks compatibility with the Unified Agent control/result model.
4. Training Farm ONE / WORKER_IDS / ALL_ACTIVE<=10 selector and artifact/generation isolation logic.
5. Ten-worker ROM-free Training Farm exporter identity fixture with no real worker launches or Collector control authority.
6. Three-source source-aware catalog/provenance rules.
7. One shared DuckDB 1.5.5 query surface preserving source identity.
8. Same-source-first reuse with explicit mapping-contract-only cross-source relationships.

### Evidence-only CI joins still potentially needed

These are **conditional gaps only if V11 terminal integration does not already publish equivalent durable evidence**:

1. **W1 -> W2 join fixture:** produce an export tree with the actual `training/farm/collector_export_fixture.py` contract and consume that exact tree through `StableRetroFbneoAdapter`, for ONE and bounded 10-worker cases. This tests contract compatibility across repositories without starting WOF or real workers.
2. **W2 -> W3 join fixture:** take an actual unified v2 Training Farm terminal result/envelope and register/query/reuse it through the W3 source-aware facade, verifying task/result/runtime/artifact provenance remains intact end-to-end.
3. **V12 consolidated-entrypoint fixture:** after V12 implements the final one-click start/stop/status path, prove Browser/WinKawaks/Training-Farm adapter states and task/result routing are surfaced by that one runtime. This is a V12-change test, not a rerun of adapter internals.
4. **Legacy-retirement static gate:** consume the sibling preflight's classified inventory and fail CI if more than one maintained normal production collection path remains.

No new test framework is justified. Existing Python `unittest`/GitHub Actions surfaces are sufficient.

## Critical-path gap list

### P0 — consume V11 terminal authority

The V11 umbrella claim is still ACTIVE. V12 implementation must not begin from W1/W2/W3 subresults as though they were terminal authority. The V11 main worker should integrate and close V11 under its existing authority. This preflight must not rerun already-green V10/W2/W3 regressions.

### P1 — close only missing evidence joins

After V11 terminal COMPLETE, compare its terminal evidence with the two conditional cross-workstream joins above. Add only whichever join is genuinely absent. Do not rebuild W1/W2/W3 test suites.

### P1 — V12 final UX / retirement implementation

The one final Windows start/stop/status path and duplicate normal production-path retirement are V12 implementation work. This preflight does not inspect or classify historical launchers because that is the sibling V12 preflight's assigned scope.

### P2 — real-environment acceptance

Real runtime facts that fixtures cannot replace are:

- Windows can start and stop the final one Unified Collector runtime;
- actual eligible WOF Browser Page->Worker->WASM discovery/capture works for one page;
- actual WOF Browser discovery/capture works for the bounded 10-page case;
- actual Windows WinKawaks/WOF capture works through the same control/result plane;
- actual Training Farm one-worker and 10-worker collection works once Training Farm authority permits those live workers.

The last item is currently gated by Training Farm authority. V11 explicitly forbids launching a real 10-worker fleet merely to prove the Collector and defers that live proof to V12 when the fleet becomes authorized.

## Minimal V12 regression / CI plan

This preflight executed **zero tests**. It reused the durable green evidence above in accordance with `TESTING_CADENCE_POLICY.md`.

For V12 implementation, use the smallest affected boundary:

1. Add one V12 acceptance fixture module/workflow covering only final consolidation joins and one-runtime UX semantics.
2. If V11 terminal did not already prove W1->W2 or W2->W3 joining, add those bounded fixture cases there; otherwise reuse terminal evidence and do not duplicate them.
3. If V12 changes only launchers/status/legacy entrypoints, run only the new V12 launcher/status/retirement checks plus any directly touched launcher smoke. Do not rerun V3–V11 adapter/data-stack suites.
4. If V12 changes `bridge/unified_collector_agent.py` or shared adapter base, rerun the existing affected V10 `tests/test_unified_collector_agent.py` and V11 W2 adapter/isolation suites once, in addition to V12 tests.
5. If V12 changes W3 source-aware data glue, rerun `tests/test_unified_data_stack_v11.py` once; otherwise reuse W3 `144/144` durable authority.
6. Escalate to the broad maintained V3–V11 regression only for shared-core drift, dependency/environment drift, unclear terminal evidence, or a real defect whose blast radius crosses those layers. Do not make a full-suite rerun a ritual V12 gate when SUT is unchanged.

## Minimal unavoidable Owner acceptance plan

Do not ask the Owner to test anything while V11 is still ACTIVE or while Training Farm live-fleet authority remains locked.

When V12 implementation and required runtime authorities are ready, prefer **one bounded Windows acceptance session driven by one final acceptance entrypoint**. The script, not the Owner, should submit tasks, poll status/results, verify IDs/hashes/provenance, query DuckDB, check reuse disposition, stop the runtime, and package one machine-readable evidence bundle.

The Owner's unavoidable responsibilities should be limited to making the real runtimes available when automation cannot legitimately create them:

1. start the final V12 acceptance entrypoint once;
2. make one real eligible WOF Browser page available, then make the bounded 10-page eligible set available if the final launcher cannot safely create those sessions itself;
3. make one real WinKawaks WOF session available;
4. make authorized Training Farm workers available only after Training Farm authority permits the requested one-worker / 10-worker live acceptance;
5. allow the acceptance script to finish and produce the final bundle; no manual log/hash/schema inspection and no separate test-script sequence.

The automated acceptance bundle should contain at minimum:

- inspected V12 build/commit identity;
- single start/stop runtime evidence;
- task blob identity and terminal result identity for each source;
- Browser page/Worker/WASM identities and per-page artifact hashes;
- WinKawaks runtime/session identity and result binding;
- Training Farm worker/generation/capture-binding identities and per-worker artifact hashes;
- source-specific dataset IDs/provenance;
- one three-source DuckDB query output preserving source columns;
- one reuse-before-recapture decision showing no silent cross-source semantic reuse;
- final stop/terminal state;
- hashes for the evidence files themselves.

One successful automated session should satisfy the real-environment acceptance; the Owner should not be asked to repeat CI-provable isolation, schema or hash checks by hand.

## Explicit non-actions

- No production code was modified.
- No test file was modified.
- No workflow was modified.
- No Training Farm file was modified.
- No Alpha file was modified.
- No Browser/WOF/WinKawaks/Training Farm runtime was started.
- No already-green V10/V11 test was rerun.
- No V11 claim was modified.
- No V12 umbrella implementation authority was claimed.
- No sibling V12 reuse/legacy inventory was duplicated.

## Handoff

V12 should begin only after V11 terminal authority is frozen. At that point, consume this matrix plus the sibling reuse/legacy preflight, add only missing cross-workstream evidence joins, implement the final one-runtime Windows UX/retirement delta, and reserve Owner involvement for the one bounded real-runtime acceptance session described above.

**COMPLETE — V12 ACCEPTANCE / FIXTURE READINESS PREFLIGHT — MINIMAL FINAL EVIDENCE PLAN DURABLE**

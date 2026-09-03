# WOF Unified Collector V12 W3 — Acceptance Harness / Focused CI SUBRESULT

Status: **SUBCOMPLETE**

Dedup key: `wof.unified-collector.v12.workstream.acceptance-harness-ci`

Claim token: `v12-w3-4e8c6f7a31d24c0b9f2a1e65d8b473ac`

Parent dispatch: `parallel/PM/WOF_UNIFIED_COLLECTOR_V12_PARALLEL_3_WORKER_DISPATCH.md`

## Authority / boundary

- W3 acquired only the W3 subworkstream claim; V12 umbrella/stage authority was not acquired or modified.
- W3 changed only acceptance tests, fixtures/helper, and one focused workflow in `ouyong520/wof-winkawaks-bridge`.
- W3 did **not** modify BAT, lifecycle, single-instance implementation, Unified Agent, adapters/data-stack, Training Farm, or Alpha production.
- Historical V10/V11 green regression suites were not rerun.

## Consumed landed authority

- Exact V11 terminal bridge authority remains ancestor: `e80257d9486cd3129b115d4e1007bf24335b8852`.
- W2 public-entrypoint candidate consumed: `e7a4cffefe72c45c0f902512b23ac9c0efccd0d6`.
- W1 lifecycle core visible in candidate history: `8725c7063a8a6817bb40cb9edcff04bdf63e75b1`.
- W1 Agent/lifecycle binding visible in candidate history: `ccf11433362ac79030fa971e29250b417d1aef29`.
- Final W3 focused candidate / current bridge main at closeout check: `b5540d9678d572fc1a6a09cb5bbcf4e3014defd2`.
- Candidate tree: `87d636087d12e1cd025ce3dfacef756618690f8a`.

## W3-owned acceptance surface

- `tests/v12_acceptance_harness.py`
  - deterministic repository acceptance collector;
  - exact V11 ancestry guard;
  - strict PASS/BLOCKED/DEFERRED machine semantics;
  - real-runtime PASS requires explicit session id, evidence SHA-256, provenance, and evidence reference, preventing repository-only false live PASS.
- `tests/test_unified_collector_v12_acceptance.py`
  - focused V12-only acceptance regression;
  - deterministic temporary lifecycle fixtures; no Browser/WOF/Training Farm live execution.
- `tests/fixtures/collector_v12_acceptance_bundle.schema.json`
  - machine-readable bundle schema.
- `tests/fixtures/collector_v12_acceptance_authority_gated.json`
  - deterministic examples for precise BLOCKED and authority-gated DEFERRED runtime facts.
- `.github/workflows/collector-v12-focused-acceptance.yml`
  - V12-path-scoped CI only; full git history fetched solely for exact V11 ancestry validation.

## Acceptance coverage

| V12 acceptance fact | Final repository verdict | Evidence mode |
|---|---:|---|
| sole canonical `start/stop/status/health` public BAT | PASS | static exact contract |
| legacy START/STOP wrapper delegation + argument forwarding | PASS | static exact contract |
| instance-bound stop / stale stop cannot target replacement instance | PASS | deterministic lifecycle fixture + source guard |
| duplicate start / stable named-mutex single-instance authority | PASS | focused contract guard |
| lifecycle status vs process health vs Agent readiness distinction | PASS | deterministic lifecycle/health fixture |
| Browser/WASM + WinKawaks + stable-retro-fbneo states on one Agent health document | PASS | focused Agent health surface guard |
| one established Git task/status/result plane | PASS | queue/Agent/lifecycle routing guard |
| legacy retirement / no old launcher resurrection | PASS | root BAT retirement gate |
| exact V11 terminal authority consumed, not forked/replaced | PASS | `git merge-base --is-ancestor` |

Machine bundle final repository summary: **9 PASS / 0 BLOCKED / 0 DEFERRED**.

The repository bundle does not claim real Windows/WOF or live ten-worker proof. The schema/harness can represent those later as PASS only with runtime evidence, or as precise BLOCKED/DEFERRED without manufacturing evidence.

## Focused CI

Workflow: `Collector V12 Focused Acceptance`

Final successful run:

- run id: `33721059586`
- job id: `100540119852`
- candidate: `b5540d9678d572fc1a6a09cb5bbcf4e3014defd2`
- focused tests: **19/19 PASS**
- generated repository acceptance: **PASS:9 BLOCKED:0 DEFERRED:0**
- bundle validator: PASS
- log marker: `COLLECTOR_V10_V11_HISTORICAL_REGRESSION=NOT_RERUN_BY_W3`

Acceptance artifact:

- artifact id: `9880234761`
- name: `collector-v12-repository-acceptance-b5540d9678d572fc1a6a09cb5bbcf4e3014defd2`
- uploaded ZIP digest: `sha256:6d504de7609dc08e93fe314c7e8aead4889f5ae53fccc32f7787c5051a28b25f`
- retention: 14 days

The first workflow run `33720878955` exposed one W3-only false-negative detector for the already-correct instance-bound stop source. That detector was corrected in `b5540d9678d572fc1a6a09cb5bbcf4e3014defd2`; no production code was changed for the fix, and the final run above is green.

## Safety / scope result

- `readOnly=true`
- `writesGameMemory=false`
- `inputInjection=false`
- no real WOF launch
- no Training Farm live fleet launch
- no V10/V11 historical regression replay

W3 acceptance harness and focused CI are complete and integration-ready for the W1 terminal coordinator.

**V12 terminal authority not claimed**.

Terminal W3 disposition: **SUBCOMPLETE — ACCEPTANCE HARNESS / FOCUSED CI READY FOR TERMINAL INTEGRATION**

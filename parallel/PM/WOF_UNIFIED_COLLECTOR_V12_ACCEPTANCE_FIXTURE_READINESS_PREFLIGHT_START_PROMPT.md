# WOF Unified Collector V12 — Acceptance / Fixture Readiness Preflight

Status: PM-AUTHORIZED READ-ONLY PREFLIGHT

This is **not V12 implementation** and does not authorize production changes before V11 terminal COMPLETE.

## Dedup

- dedupProtocol: `v2`
- dedupKey: `wof.unified-collector.v12.preflight.acceptance-fixture-readiness`
- dedupMode: `exclusive`
- stageId: `WOF_UNIFIED_COLLECTOR_V12_ACCEPTANCE_FIXTURE_READINESS_PREFLIGHT_V1`

Before work, perform canonical dedup v2 preflight against current main, relevant RESULTs/claims, recent equivalent commits and this START_PROMPT. If equivalent ACTIVE/COMPLETE/superseded, return NO EXECUTION.

## Purpose

Shorten V12 final consolidation by producing an implementation-ready acceptance evidence map while V11 terminal integration is still active. This preflight is independent from the already-active V12 reuse/legacy readiness preflight: it does **not** research launchers, external packages, process supervisors, tray UX, or legacy retirement classifications.

## Hard boundary

- Read-only analysis except for this preflight's PM RESULT/claim files.
- Do not modify `ouyong520/wof-winkawaks-bridge` production code, tests, workflows, schemas, launchers or docs.
- Do not modify `training/farm/**` or `product/alpha/**`.
- Do not acquire the future V12 umbrella implementation claim.
- Do not declare V12 COMPLETE.
- Do not start Browser/WOF/WinKawaks/Training Farm runtimes.
- Do not rerun V10/V11 tests merely for confidence; inspect durable workflow/test evidence instead.
- Do not duplicate `WOF_UNIFIED_COLLECTOR_V12_REUSE_LEGACY_READINESS_PREFLIGHT_V1`.

## Required work

1. Read latest `AGENTS.md`, PM global rules, V9→V12 roadmap, V10 RESULT, V11 W1/W2/W3 durable artifacts available on current main, and existing Collector test/workflow surfaces.
2. Build an exact V12 acceptance matrix for the roadmap requirements:
   - one Unified Collector start/stop path;
   - one Browser task / one eligible page;
   - one Browser task / 10 eligible pages with no cross-page splice;
   - one WinKawaks task through the same Git control/result plane;
   - one Training Farm worker;
   - bounded 10-worker Training Farm fixture/acceptance without worker mixing;
   - source-specific task/result/dataset provenance;
   - one shared DuckDB query surface preserving source identity;
   - reuse-before-recapture without cross-source semantic guessing;
   - legacy production-path retirement evidence.
3. For each requirement, classify current evidence as:
   - `ALREADY_DURABLY_PROVEN`
   - `V12_CI_FIXTURE_NEEDED`
   - `V12_IMPLEMENTATION_THEN_CI`
   - `REAL_WINDOWS_ACCEPTANCE_INTRINSICALLY_REQUIRED`
   - `BLOCKED_BY_V11_TERMINAL_AUTHORITY`
4. Identify exact existing tests/workflows/fixtures/results that V12 should reuse rather than rewrite or rerun unnecessarily.
5. Identify only genuine missing fixtures or evidence joins. Do not propose a new test framework if existing unittest/GitHub Actions surfaces are sufficient.
6. Design the smallest coherent V12 regression boundary. It should reuse already-green V3–V11 evidence where SUT is unchanged and add only tests for V12 consolidation/launcher/legacy-retirement material changes.
7. Minimize Owner work. Specify the smallest final real-environment acceptance that cannot be replaced by CI/fixtures. Prefer one bounded Windows acceptance flow with automated evidence collection when feasible; do not ask Owner to manually inspect logs, hashes or multiple scripts.
8. Produce an implementation-ready gap list ordered by critical path, distinguishing code gaps from evidence-only gaps and real-environment-only facts.

## Required durable output

Write:

`parallel/PM/WOF_UNIFIED_COLLECTOR_V12_ACCEPTANCE_FIXTURE_READINESS_PREFLIGHT_RESULT.md`

The RESULT must include:

- exact repo HEADs inspected;
- dedup verdict;
- V12 acceptance matrix;
- existing durable evidence reused for each row;
- exact missing fixture/evidence gaps;
- minimal V12 regression/CI plan;
- minimal unavoidable Owner acceptance plan;
- explicit statement that no production code/tests/workflows were modified and `V12 implementation authority not claimed`.

Then mark only this preflight claim COMPLETE. Do not touch V11 or future V12 umbrella claims.

## Stop condition

`COMPLETE — V12 ACCEPTANCE / FIXTURE READINESS PREFLIGHT — MINIMAL FINAL EVIDENCE PLAN DURABLE`

or precise `BLOCKED` if a genuinely unavailable durable fact prevents the read-only inventory.

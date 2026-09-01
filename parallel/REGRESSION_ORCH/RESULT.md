# REGRESSION ORCHESTRATOR READY

Status: **READY**

Validated: 2026-09-01

## READY evidence

GitHub Actions validation run `33509541268` on a real Windows runner proved the orchestrator contract:

- `orchestrator-contract`: PASS
- safe runner compile: PASS
- orchestrator self-tests: PASS
- generated/dependency path exclusion self-tests: PASS
- complete regression runner executed through all allowlisted suites and uploaded summary/logs
- PYLAUNCH offline suite: PASS after switching to its documented `python -m unittest discover` invocation
- Browser Fleet suite: PASS
- WOF-052L Recorder suite: PASS
- Prospective Validator suite: PASS
- Evidence Ingestor suite: PASS
- Project Status Scanner suite: PASS
- Alpha RC5 Product Regression: PASS
- Alpha RC5 Independent QA Harness: PASS
- test allowlist safety gate: PASS
- Windows owner CMD smoke: PASS

The runner no longer treats `.venv/site-packages`, `node_modules`, or other generated dependency trees as repository tests.

## Current repository health is separate from orchestrator readiness

At the validation snapshot, the complete offline repository result was still `FAIL` because the orchestrator correctly exposed three external lane regressions instead of hiding them:

1. `owner_chinese_ux`: the existing OPTOOLKIT Chinese UX test still expects the old `owner_zh_cn.py` Recorder frontend while the current Recorder CMD has moved to `owner_v2_zh_cn.py`.
2. `owner_oneclick`: the pinned package manifest is behind the current PYLAUNCH files.
3. `operator_toolkit`: Windows temporary-path normalization tests currently disagree on long vs 8.3 short paths, plus the same stale Chinese frontend assertion.

These are component/lane issues and were not modified by REGRESSION_ORCH.

`REGRESSION ORCHESTRATOR READY` means one command/double-click now produces a faithful current repository regression summary; it does **not** mean every independently changing component is green at every instant.

## Owner entry

Double-click:

```text
parallel/REGRESSION_ORCH/RUN_ALL_REGRESSION.cmd
```

or run:

```text
python parallel/REGRESSION_ORCH/runner.py --repo-root .
```

Stable outputs:

- `parallel/REGRESSION_ORCH/REGRESSION_SUMMARY.json`
- `parallel/REGRESSION_ORCH/回归结果.txt`
- `parallel/REGRESSION_ORCH/logs/<run-id>/*.log`

## Human proof policy

The orchestrator does not auto-run:

- PYLAUNCH真人 Windows / Browser proof
- Alpha真人 Browser acceptance

Those remain `NOT_RUN/BLOCKED` until a human performs them; they are never promoted to PASS by offline automation.

## Safety

- read-only
- `ramWrites=0`
- no gameplay input injection
- no `window.Worker` replacement
- no automatic game entry
- no production rule changes
- no changes to `product/alpha/**`
- no changes to component core implementations

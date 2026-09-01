# WOF Windows Operator Toolkit

Status: **WINDOWS V1 READY**

Entry point from repository root:

```text
WOF_TOOLKIT.cmd
```

The Toolkit is an operator shell. It does not reimplement Alpha, PYLAUNCH, WOF-052L Recorder, or Browser Fleet. It invokes the current repository tools, keeps Python dependencies in one external Toolkit venv, and gathers operator outputs under one results root.

Default results root:

```text
%USERPROFILE%\Documents\WOF_RESULTS
```

Override with `WOF_RESULTS_DIR` when needed.

## Menu contract

```text
1 Update Project
2 Start Python Launcher
3 Start Multi-Room Recorder
4 Start Browser Fleet
5 Run Regression
6 Run Live Proof
7 Collect Diagnostics
8 Package Results
9 Open Results Folder
0 Exit
```

### 1 Update Project

Runs Git fetch plus fast-forward-only pull. If local changes exist, Toolkit refuses to pull over them and prints the affected paths. Reopen Toolkit after an update so newly pulled Toolkit/dependency changes are loaded.

### 2 Start Python Launcher

Invokes the existing `parallel/PYLAUNCH/launcher.py` with the Toolkit Python environment.

### 3 Start Multi-Room Recorder

Invokes `parallel/WOF052L_RECORDER/recorder.py` directly and passes:

```text
--output-dir <WOF_RESULTS>\recorder
```

This avoids a repo-local recorder venv and puts WOF-052L room/checkpoint/run JSON under the unified results folder.

### 4 Start Browser Fleet

Invokes `parallel/BROWSER_FLEET/RUN_WOF_FLEET.cmd`, preserving its existing first-run configuration and interactive 1/5/10 count UX. Fleet keeps its discovery manifest at the established `%LOCALAPPDATA%` contract location; Toolkit Diagnostics collects it when present.

### 5 Run Regression

Runs existing checks rather than duplicating their assertions:

- `product/alpha/regression.mjs` read-only product regression;
- `parallel/ALPHAQA_RC5/independent_bootstrap_retest.mjs`;
- WOF-052L `recorder.py --self-test`;
- PYLAUNCH Python tests;
- Browser Fleet Python tests;
- Toolkit Python tests.

Outputs plus `regression_summary.json` are written to `WOF_RESULTS\regression_<timestamp>`.

Node.js-dependent checks are reported as `BLOCKED` when Node is unavailable; Python checks still run.

### 6 Run Live Proof

Reuses the existing PYLAUNCH proof path:

```text
launcher.py --proof-json <WOF_RESULTS>\live_proof_<timestamp>\WINDOWS_PROOF_STATUS.json
```

No DevTools or Worker-console step is added.

### 7 Collect Diagnostics

Creates `WOF_RESULTS\diagnostics_<timestamp>` and collects available operator/status material: PYLAUNCH proof/result, RC5 QA result/status/findings, committed Alpha regression result as a copy, PM priority/readiness files, Git head/branch/status, Python/Node/platform info, Browser Fleet `instances.json`, latest WOF-052L merged run JSON, and Toolkit log.

### 8 Package Results

Creates a ZIP under `WOF_RESULTS\packages` containing the latest diagnostics, regression, and live-proof folders plus the latest WOF-052L merged run JSON when present. `PACKAGE_MANIFEST.json` records the safety contract.

### 9 Open Results Folder

Opens the unified results folder in Explorer.

## Environment behavior

`WOF_TOOLKIT.cmd`:

- locates the repository from its own location without asking for a path;
- detects `py -3` or `python`;
- creates one external venv at `%LOCALAPPDATA%\WOF Toolkit\venv` (fallback `%TEMP%\WOF_TOOLKIT\venv`);
- installs/updates existing PYLAUNCH requirements;
- installs/updates WOF-052L requirements when present;
- does not create Toolkit/PYLAUNCH/Recorder venv files inside the Git checkout.

## Safety boundary

Toolkit itself has the fixed declaration:

```json
{"readOnly": true, "ramWrites": 0, "inputInjection": false}
```

It does not modify `product/alpha/**`, write game RAM, inject keyboard/mouse/controller/gameplay input, replace `window.Worker`, create Blob Workers, or rewrite Worker URLs.

Option 5 reads `product/alpha/**` only because the existing regression harness lives there; it does not edit product files.

## Error policy

Expected operator failures are translated into short messages: missing Python/Git/Node/component, dirty Git checkout, dependency-install failure, failed fast-forward, component launch error, or timeout. A failed Toolkit action does not intentionally close or alter the base game/browser.

## Offline validation

```text
python -m py_compile parallel/OPTOOLKIT/toolkit.py
python -m unittest discover -s parallel/OPTOOLKIT/tests -p test_*.py -v
```

V1 tests cover the safety contract, exact WOF-052L/Fleet discovery, rejection of unrelated/old component names, exclusion of `product/alpha/**` as components, external result location, and result-package assembly.

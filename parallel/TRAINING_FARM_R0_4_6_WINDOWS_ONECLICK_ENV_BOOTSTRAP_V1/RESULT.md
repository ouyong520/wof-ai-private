# Training Farm R0.4.6 — Windows OneClick Environment Bootstrap V1 Result

Date: 2026-09-02
Stage: `TRAINING_FARM_R0_4_6_WINDOWS_ONECLICK_ENV_BOOTSTRAP_V1`
Dedup key: `training.farm.r0.4.6.windows-oneclick-env-bootstrap-v1`
Status: **REPOSITORY IMPLEMENTATION COMPLETE — OWNER REAL R0.2/R0.4 PROOF STILL REQUIRED**

## Verdict

R0.4.6 Windows OneClick Environment Bootstrap V1 is complete. The repository now has a Windows beginner one-click environment-preparation path that discovers a supported Python, creates/reuses a dedicated local `.venv`, synchronizes the checked-in dependency authority, verifies the exact Stable-Retro pin plus FBNeo capability without using ROM bytes, creates a safe external evidence/workspace layout, and then hands off to the existing strict beginner real-WOF launcher using the dedicated venv Python.

This stage is bootstrap/UX only. It does **not** claim R0.2 real determinism PASS, R0.4 real fork PASS, or any R0.5 authorization.

## Dedup / ownership

- start commit immediately before canonical claim: `62c461b1ce7034812a96bd6f4966206311784bd9`
- canonical claim token: `28343a9306bce8e7fcf8933934cf470f813aaccea8cde9e5`
- canonical claim: `parallel/PM/DEDUP_CLAIMS/training.farm.r0.4.6.windows-oneclick-env-bootstrap-v1.json`
- stage claim: `parallel/PM/STAGE_CLAIMS/TRAINING_FARM_R0_4_6_WINDOWS_ONECLICK_ENV_BOOTSTRAP_V1.json`

Both claims were create-only acquired and post-create token verified before implementation work began.

## Exact source candidate / current-main reconciliation

Exact completed R0.4.6 source/documentation candidate before RESULT creation:

`1771e3940ed91d1d0a5c68c08f8782b6d1aa1d0c`

Current `main` was re-read immediately before RESULT creation and was exactly that candidate.

Comparison from the pre-claim source HEAD `62c461b1ce7034812a96bd6f4966206311784bd9` through the candidate is 15 commits ahead. The only Training Farm implementation additions are the four R0.4.6 files below plus this task's canonical/stage claim records. Other intervening changes are concurrent OPTOOLKIT/PYLAUNCH work outside Training Farm; no existing R0.2/R0.4/R0.4.5 implementation file was modified by R0.4.6.

Exact candidate blobs:

- `training/farm/windows_oneclick_bootstrap.py` — `9edbfab10eebb054000e015a96b7d0f03ea91d0c`
- `training/farm/run_windows_oneclick_env_bootstrap.cmd` — `2897a840aa4784ec3e83ec7dffb09227fee8f5bb`
- `training/farm/tests/test_windows_oneclick_bootstrap.py` — `e8d8de6c52a58c4117d6bbbe1efb0f98085b0f78`
- `training/farm/R0_4_6_WINDOWS_ONECLICK_ENV_BOOTSTRAP.md` — `0ba7afacc4f3c4c30272a1b9e0022d27d47dd60f`

Current upstream authority blobs were re-read after the implementation commits and remain unchanged:

- R0.2 `training/farm/determinism.py` — `7cedcd78fe21835b8cc674c2ad781676146984d5`
- R0.4 `training/farm/savestate_fork_runner.py` — `4a76b3db49dc8c9970765cc435152920abb4549a`
- Stable-Retro/FBNeo adapter `training/farm/stable_retro_backend.py` — `14ba7bf41019900d5189931f7dbb0a2819e53998`
- strict Owner runner `training/farm/real_wof_proof_owner_runner.py` — `c966538befeb25f8b6fd694183fa4984ec73b9be`
- existing beginner launcher `training/farm/beginner_real_wof_launcher.py` — `17491953c7d20c76a91b0169c1f8ab68971ce056`
- R0.4.5 background runtime `training/farm/background_runtime.py` — `12cb776323895d894be8efe273b9039355edee41`
- dependency authority `training/farm/requirements-r0.1.txt` — `b98c2e248020600645f4ef65b22ce7f970b5c6db`

Thus R0.4.6 is additive around the existing proof path; proof code/semantics remain byte-for-byte untouched.

## Implemented Windows flow

Beginner entry point:

```text
training\farm\run_windows_oneclick_env_bootstrap.cmd
```

The `.cmd`:

- resolves the repository root from its own path;
- enables UTF-8 console/Python behavior where practical;
- safely handles quoted paths including Chinese characters, spaces and parentheses;
- tries an explicitly configured bootstrap Python, the default dedicated `.venv`, `py -3.14` down through `py -3.10`, then `python` and `python3`;
- rejects unsupported versions before importing the module;
- keeps the terminal open unless `WOF_BOOTSTRAP_NO_PAUSE` is explicitly set for automation/tests;
- preserves the Python/bootstrap child exit code;
- never downloads Python, ROM, BIOS, emulator assets, or changes system/global Python state.

If no supported Python exists, it stops `WAITING_PREREQUISITE` and instructs the Owner to install one supported Python 3.10..3.14 without uninstalling the existing default Python.

## Python discovery and dedicated venv

`windows_oneclick_bootstrap.py` imports the supported range directly from current `stable_retro_backend.py`; the current authority is 3.10..3.14.

Discovery is deterministic and records every examined candidate with command/source, observed executable/version, accepted flag and precise reject reason. It prefers supported candidates over an unsupported default `python` and supports an explicitly supplied interpreter plus an already-created dedicated venv.

Default local root is the repository parent, matching the beginner layout where source is one child of a machine-local root. A configurable local root is supported; the implementation does not hard-code `F:` or bind source identity to a machine path.

The dedicated environment is `<local-root>/.venv`. Repeated execution reuses a valid supported venv. A missing interpreter inside an existing venv is `BROKEN`; an unsupported venv Python is `STALE_UNSUPPORTED`. Those states fail clearly rather than silently deleting/overwriting an unknown local environment. New venv creation uses only the selected supported interpreter and `python -m venv`.

No global package mutation is used when the dedicated venv is available.

## Strict dependency authority and FBNeo probe

The bootstrap reads the checked-in `training/farm/requirements-r0.1.txt`, SHA-256s it for diagnostics, parses exactly one `stable-retro==...` requirement, and compares that requirement to `PINNED_STABLE_RETRO` imported from the current backend source. Current authority is exactly `stable-retro==0.9.8`.

A requirement/backend mismatch is a fail-closed bootstrap `BLOCKED`; the bootstrap never edits either pin to make setup pass.

Package synchronization runs only through the dedicated venv Python with the checked-in requirements file. Failure classification distinguishes:

- network/package-index/connectivity failure -> `WAITING_PREREQUISITE`;
- wheel/build failure -> precise `BLOCKED`;
- other package-install failure -> precise `BLOCKED`;
- wrong installed Stable-Retro version -> `BLOCKED`;
- FBNeo button capability or ZIP mapping failure -> `BLOCKED`.

The post-install probe reuses `training.farm.stable_retro_backend.dependency_probe`. For bootstrap probing, `WOF_ROM_PATH` is removed from the child environment so the probe validates Stable-Retro version and FBNeo capability without reading/statting an Owner ROM path. Runtime proof readiness is not fabricated from this ROM-free probe.

## Workspace / evidence / launcher integration

The local helper creates only directories:

- `ROM`
- `evidence`
- `logs`
- `runtime`
- `training-data`
- `checkpoints`

It never copies, moves, imports or creates ROM bytes. `ROM` is only an empty optional location convention.

Evidence defaults to `<local-root>/evidence`, is required to remain outside the repository, and is only created/passed through. R0.4.6 does not rewrite `summary.json`, synthesize missing proof outputs, or merge old evidence.

After readiness the bootstrap invokes, using the dedicated venv Python:

```text
-m training.farm.beginner_real_wof_launcher --evidence-root <external-root>
```

The existing launcher retains authority for the Windows ROM picker, current Owner size/SHA identity check and session-local `WOF_ROM_PATH` handoff. The existing strict Owner runner remains the only orchestrator/validator for current-source R0.2 -> R0.4 real proof. Its stdout/stderr and exit code are surfaced unchanged by the bootstrap layer.

## ROM-free diagnostics

CLI:

```text
python -m training.farm.windows_oneclick_bootstrap --diagnostics-json
```

Diagnostics report repository/local roots, all Python candidates and selection, expected/observed venv path/version/state, requirement authority path/SHA, expected Stable-Retro pin, dependency sync/probe state, evidence root/safety, launcher readiness, and explicitly:

```text
romAccessed=false
realWofProof=false
r0_5Authorized=false
realWorkerExecutionStarted=false
```

Diagnostics do not create a venv, execute pip, start proof, open a ROM picker, or turn bootstrap readiness into proof evidence.

`--prepare-only` performs the real environment preparation but stops at `READY_FOR_OWNER_PROOF` before ROM selection/proof.

## Compact implementation-owned self-check

One coherent ROM-free implementation self-check was performed after the complete module was assembled; no independent QA stage was opened.

The available connected GitHub surface does not provide a mounted private-repository checkout and direct network clone is unavailable. Therefore the exact committed R0.4.6 module/test blobs were reconstructed locally and Git-blob SHA checked against GitHub before execution. The exact committed executable bootstrap blob `9edbfab...` and exact committed test blob `e8d8de6...` were executed with mocked interpreter/pip/FBNeo/proof subprocesses; Stable-Retro installation and Internet were not required.

Commands/operations:

```text
python -m compileall -q training
python -m unittest training.farm.tests.test_windows_oneclick_bootstrap -v
python -m training.farm.windows_oneclick_bootstrap --diagnostics-json
```

Final exact-blob self-check outcome:

- bytecode compilation: PASS;
- bootstrap tests: **20/20 PASS**;
- ROM-free diagnostics assertions: PASS;
- supported candidate selected even when default `python` is 3.15/unsupported: PASS;
- strict Python 3.10 and 3.14 bounds accepted; 3.9/3.15 and coercible malformed versions rejected: PASS;
- Chinese/space/parentheses workspace: PASS;
- valid venv reuse: PASS;
- broken/stale venv detection: PASS;
- venv creation command via safe mock: PASS;
- requirements path/hash/pin authority: PASS;
- requirement/backend mismatch fail-closed: PASS;
- exact installed Stable-Retro mismatch rejection: PASS;
- mocked pip success/network/build failure classification: PASS;
- FBNeo probe success/failure and capability-false propagation: PASS;
- parent `WOF_ROM_PATH` stripped from ROM-free dependency probe: PASS;
- evidence creation and repository-local evidence rejection: PASS;
- existing beginner launcher invoked with dedicated venv Python + evidence path: PASS;
- child nonzero exit preserved (`7` remained `7`): PASS;
- `--prepare-only` did not launch proof: PASS;
- no host-input/focus/system-global mutation authority introduced: PASS.

The current source comparison and exact upstream blobs above are the targeted R0.2/R0.4/R0.4.5 compatibility/source-drift check. No existing Training Farm proof/runtime implementation file changed.

## Proof / safety boundary

No real WOF ROM was available or used in implementation/self-check. No ROM bytes were read, copied, encoded, uploaded, committed or distributed. No real Stable-Retro gameplay was executed. No 2+ worker launch, Reward, Search, RL, semantic RAM address guessing, host input injection, focus switching, service/driver installation, Administrator requirement, or global environment mutation was introduced.

Therefore this RESULT explicitly does **not** claim:

- R0.2 `REAL_WOF` PASS;
- R0.4 `REAL_WOF_FORK` PASS;
- `realWofProof=true`;
- R0.5 authorization.

## Exact next Owner action

Use the current repository candidate, not the old environment-assuming entry directly:

1. extract/current-checkout the repository under a local root, e.g. `F:\三国\三国10训\wof-ai-private-main\`;
2. double-click `training\farm\run_windows_oneclick_env_bootstrap.cmd`;
3. if it reports missing Python, install one supported Python 3.10..3.14 and double-click again;
4. when it reaches `READY_FOR_OWNER_PROOF`, the existing beginner launcher opens the ROM picker;
5. select the legally held external WOF ZIP outside the repository;
6. preserve the strict runner's evidence path/result.

Only an actual strict:

`PASS — R0.2 REAL WOF DETERMINISM + R0.4 REAL FORK SMOKE`

may satisfy the remaining real-proof gate. R0.5 remains locked until those real proofs plus separate PM authorization exist.

## Stop condition

**COMPLETE — TRAINING FARM R0.4.6 WINDOWS ONECLICK ENV BOOTSTRAP V1 — OWNER SETUP BURDEN REDUCED; REAL R0.2/R0.4 PROOF STILL REQUIRED**

# Training Farm R0.4.6 — Windows OneClick Environment Bootstrap V1

## PM authority / dedup

- stageId: `TRAINING_FARM_R0_4_6_WINDOWS_ONECLICK_ENV_BOOTSTRAP_V1`
- dedupProtocol: `v2`
- dedupKey: `training.farm.r0.4.6.windows-oneclick-env-bootstrap-v1`
- dedupMode: `exclusive`
- canonical claim path: `parallel/PM/DEDUP_CLAIMS/training.farm.r0.4.6.windows-oneclick-env-bootstrap-v1.json`
- stage claim path: `parallel/PM/STAGE_CLAIMS/TRAINING_FARM_R0_4_6_WINDOWS_ONECLICK_ENV_BOOTSTRAP_V1.json`

Before any mutation, strictly re-read current `main`, this prompt, `parallel/PM/STAGE_DEDUP_GUARD.md`, `parallel/PM/TESTING_CADENCE_POLICY.md`, current R0.2/R0.4/R0.4.5 durable RESULTs, the existing beginner real-WOF launcher/runner, and search for equivalent claims/results/prompts. If equivalent work is already COMPLETE, stop `ALREADY COMPLETE — SAFE TO CLOSE`. If already validly claimed, stop `ALREADY CLAIMED — SAFE TO CLOSE`. Do not steal historical stale claims; only PM-authorized recovery may supersede them.

## Context

Training Farm R0.1-R0.4 repository implementation is complete, and R0.4.5 headless/background runtime foundation is COMPLETE. The remaining hard gate before R0.5 is still Owner-local real-WOF proof: current-source R0.2 determinism PASS followed by authoritative R0.4 real fork PASS.

The Owner is a Windows beginner and has already hit a concrete prerequisite problem: the existing `training/farm/run_real_wof_proof_beginner.cmd` correctly rejected an unsupported Python version. The existing beginner launcher reduces ROM-selection complexity but still assumes a supported Python and installed pinned Stable-Retro environment.

This stage is a narrow **gate-reducer/bootstrap implementation**, not proof-authority work and not R0.5. Its purpose is to let repository development reduce Owner setup burden while the real proof remains external and strict.

Owner-local preferred root is currently `F:\三国\三国10训`, but repository source must remain portable: do not hard-code that path as global authority. It may be used as an example/default in a local wrapper/configurable entry point, while all core logic must support arbitrary Windows paths including Chinese characters, spaces, and parentheses.

## Hard scope boundary

This task MAY implement a Windows-first one-click environment/bootstrap layer around the already-existing strict proof runner.

This task MUST NOT:

- claim or fabricate real R0.2/R0.4 PASS;
- modify `realWofProof`, proof scope, determinism/fork acceptance, runtime/ROM/source identity, or evidence validation to make proof easier;
- alter R0.2/R0.4 proof semantics or schemas except for a proven compatibility defect that cannot be solved outside proof authority, in which case BLOCKED rather than weakening;
- start R0.5 Reward/Search/RL or 2+ real WOF workers;
- guess WOF semantic RAM addresses;
- download, vendor, commit, encode, split, redistribute, or silently copy ROM/BIOS/game assets;
- install system-wide services/drivers or require Administrator when a user-space solution exists;
- use `SendInput`, AutoHotkey gameplay automation, global keyboard/mouse injection, or focus switching;
- modify `product/alpha/**`, Alpha/Transport/Recorder/PYLAUNCH/WinKawaks Collector lanes.

Fixture/bootstrap PASS is never real-WOF proof.

## Required implementation

### 1. Windows one-click bootstrap entry

Add a beginner-facing Windows entry under `training/farm/**`, for example a `.cmd` plus Python bootstrap module, that can be launched from an extracted GitHub ZIP or normal checkout.

The entry must:

- resolve repository root robustly from its own location;
- support Windows paths containing Chinese characters, spaces and parentheses;
- preserve UTF-8 console behavior where practical;
- keep the terminal open on beginner-facing failure/success unless explicitly suppressed for tests;
- produce clear Chinese-first status: `PASS`, `READY_FOR_OWNER_PROOF`, `WAITING_PREREQUISITE`, or precise `BLOCKED`;
- never hide a failing child exit code or convert failure to success.

### 2. Compatible Python discovery

Implement deterministic discovery of a supported interpreter in the existing allowed range from repository authority (`3.10..3.14` unless current source says otherwise).

Discovery should inspect safe local candidates such as:

- Windows `py` launcher enumerations/candidates;
- `python`/`python3` on PATH;
- an already-created bootstrap venv under the configured Training Farm local root;
- explicitly supplied interpreter path.

Requirements:

- prefer exact supported interpreters over an unsupported default `python`;
- do not uninstall or overwrite the Owner's existing Python installations;
- strict version parsing, no coercible string guessing;
- structured diagnostics list what was examined and why a candidate was accepted/rejected;
- if no supported Python exists, stop `WAITING_PREREQUISITE` with an exact beginner instruction rather than modifying proof logic.

Do not silently download/install Python in repository implementation. Optional future package-manager installation may be documented but must not be required for module self-check.

### 3. Dedicated local venv bootstrap

Support a configurable local Training Farm root and create/reuse a dedicated `.venv` outside proof authority.

Preferred Owner example:

`F:\三国\三国10训\.venv`

But implementation must accept arbitrary local roots and must not bind Git source identity to this machine-specific path.

Requirements:

- create venv with the selected supported interpreter;
- detect broken/stale venv and fail clearly or repair only when safe;
- record selected base Python and venv Python versions/paths in local bootstrap diagnostics;
- never mutate global Python package state when the dedicated venv path is available;
- repeated execution is idempotent.

### 4. Strict dependency synchronization

Read dependency authority from current repository files, especially `training/farm/requirements-r0.1.txt` and the current `stable_retro_backend.py` pin. Do not duplicate the version as an unrelated second source of truth when avoidable.

Bootstrap must be able to:

- install/synchronize required Python packages into the dedicated venv using that checked-in requirement authority;
- verify the observed Stable-Retro version exactly matches the current pin (currently expected `0.9.8`, but source authority wins);
- run current FBNeo capability/ZIP mapping probe using existing Farm code where possible;
- distinguish network/package-install failure, wheel/build failure, unsupported Python, wrong Stable-Retro version, and FBNeo capability failure;
- never patch the requirement/pin merely to make local setup pass.

Tests must mock package installation; implementation self-check must not require Internet.

### 5. Local workspace layout helper

Provide an optional configurable workspace convention for beginner use. For the Owner's current machine, documentation/example may show:

`F:\三国\三国10训\`

with:

- `wof-ai-private-main\` source
- `.venv\`
- `ROM\`
- `evidence\`
- `logs\`
- `runtime\`
- future `training-data\` and `checkpoints\`

But the repository must not assume drive `F:` exists.

The helper may create non-ROM directories. It MUST NOT move/copy/import ROM bytes automatically. The ROM remains Owner-selected external data.

### 6. Existing strict beginner launcher integration

After environment readiness, bootstrap must invoke/reuse the existing strict flow rather than creating a second proof implementation.

Preferred integration:

- execute the current `training.farm.beginner_real_wof_launcher` using the dedicated venv Python;
- preserve Windows file-picker ROM selection;
- pass a configured evidence root to the existing strict owner runner where supported;
- keep `WOF_ROM_PATH` child/session-local, not global registry/system environment;
- surface exact strict result/evidence locations.

Do not duplicate or fork R0.2/R0.4 proof code.

### 7. Evidence-root convenience

Support configurable evidence root, with beginner example:

`F:\三国\三国10训\evidence`

The bootstrap must create the directory if safe, then pass it through existing supported interfaces. It must not rewrite evidence JSON or synthesize missing proof files.

At completion of a real Owner run, expected files remain the existing authority outputs such as:

- `summary.txt`
- `summary.json`
- `r0_2_real_determinism.json`
- `r0_4_real_fork_smoke.json`

This stage itself may test only path propagation/diagnostics, not claim these real files exist.

### 8. ROM safety

Retain strict ROM boundaries:

- Owner ROM stays outside repository tree;
- no automatic download;
- no upload/commit/vendor/base64/encryption/splitting;
- no automatic copy into workspace/repository;
- hash in place only via existing strict launcher when selected;
- filename alone is not identity;
- current recorded Owner ROM metadata may be read from `OWNER_LOCAL_ROM_REFERENCE.md`, but do not loosen size/SHA checks.

### 9. Structured ROM-free diagnostics

Provide a CLI or JSON-capable bootstrap diagnostics mode that can run without ROM and without Stable-Retro installed.

It should report at least:

- repository root;
- configured local root;
- Python candidates and selected interpreter;
- venv expected/observed state;
- requirement authority path/hash or deterministic identity;
- pinned Stable-Retro expected version from source authority;
- dependency sync/probe state;
- evidence root;
- proof launcher readiness;
- `realWofProof=false` for bootstrap-only diagnostics;
- `r0_5Authorized=false`;
- no ROM bytes accessed in ROM-free mode.

### 10. Documentation / beginner UX

Write a short beginner document explaining the intended final local flow:

1. download/extract repository;
2. double-click one bootstrap entry;
3. bootstrap locates compatible Python and prepares `.venv`/dependencies;
4. if Python itself is missing, user receives one exact prerequisite message;
5. when environment is ready, proof launcher opens ROM picker;
6. select local WOF ZIP outside repository;
7. strict R0.2 then R0.4 proof runs and evidence path is shown.

Do not require the Owner to manually set environment variables, find Python paths, or type a long command sequence in the normal flow.

## Integration constraints

- Preserve R0.4.5 headless/no-host-input policy and do not regress it.
- Preserve current direct Stable-Retro/FBNeo adapter and proof code byte-for-byte unless a genuine bootstrap integration hook is needed; prefer new wrapper/helper modules.
- Do not bind portable source authority to `F:\三国\三国10训`.
- Do not introduce a second emulator stack.
- Do not add RL packages.
- No ROM bytes in tests/fixtures/logs/RESULT/Git.

## Implementation-owned self-check

After the coherent module is complete, run one compact self-check. Cover at least:

- supported Python candidate selection when default `python` is unsupported;
- strict 3.10 and 3.14 boundary acceptance, below/above rejection;
- Chinese/space/parentheses workspace paths;
- existing valid venv reuse;
- broken/stale venv detection;
- venv creation command construction via safe mocks;
- requirement authority resolution from repository source;
- exact pinned Stable-Retro mismatch rejection;
- package-install success/failure via mocked subprocess, with no real network requirement;
- FBNeo probe success/failure propagation via mocked/current adapter boundary;
- evidence-root creation/path propagation;
- no ROM access in diagnostics mode;
- existing beginner proof launcher invocation using dedicated venv Python;
- child failure remains failure;
- no host-input/focus/system-global mutation introduced;
- targeted R0.2/R0.4/R0.4.5 compatibility/source-drift checks.

Do not call bootstrap self-check real-WOF proof.

## Durable RESULT and closeout

Write durable RESULT under:

`parallel/TRAINING_FARM_R0_4_6_WINDOWS_ONECLICK_ENV_BOOTSTRAP_V1/RESULT.md`

Include:

- exact source candidate/current-main reconciliation;
- files/blobs changed;
- Python discovery/venv/dependency authority behavior;
- exact self-check commands/outcomes;
- explicit statement that no real-WOF proof was claimed;
- explicit R0.5 lock remains;
- exact next legitimate Owner action after bootstrap is repository-complete.

Then token-verify and close canonical and stage claims COMPLETE. Do not stop at claim creation, one patch, one test, or WAITING when repository implementation itself is complete.

## Stop condition

Only:

- `COMPLETE — TRAINING FARM R0.4.6 WINDOWS ONECLICK ENV BOOTSTRAP V1 — OWNER SETUP BURDEN REDUCED; REAL R0.2/R0.4 PROOF STILL REQUIRED`
- precise irreducible `BLOCKED — <exact blocker>`
- canonical duplicate stop.

# Training Farm R0.4 — Owner Beginner Real-WOF Launcher V1

stageId: `TRAINING_FARM_R0_4_OWNER_BEGINNER_REAL_WOF_LAUNCHER_V1`
dedupProtocol: `v2`
dedupKey: `training.farm.r0.4.owner-beginner-real-wof-launcher-v1`
dedupMode: `exclusive`

Priority: **Owner usability bridge for the already-complete R0.4 real-WOF proof runner**

## Dedup / duplicate-stop is mandatory

This task may be reposted by Owner. Before any substantive mutation, re-read current `main`, current PM policies, existing R0.4 Owner-runner RESULT/claims and all equivalent beginner/onboarding launcher work.

If an equivalent beginner launcher is already COMPLETE, stop immediately:

`ALREADY COMPLETE — SAFE TO CLOSE`

If an equivalent canonical claim is already ACTIVE under another valid token, stop immediately:

`ALREADY CLAIMED — SAFE TO CLOSE`

Do not repeat implementation just because the same post was forwarded again.

Canonical claim path:

`parallel/PM/DEDUP_CLAIMS/training.farm.r0.4.owner-beginner-real-wof-launcher-v1.json`

Stage claim path:

`parallel/PM/STAGE_CLAIMS/TRAINING_FARM_R0_4_OWNER_BEGINNER_REAL_WOF_LAUNCHER_V1.json`

Follow canonical dedup v2 exactly; no stealing or reusing another token.

## Context

Current repository already has a strict real-proof Owner package:

- `training/farm/run_real_wof_proof.cmd`
- `training/farm/real_wof_proof_owner_runner.py`
- `training/farm/real_wof_fork_smoke.plan.json`
- `training/farm/R0_4_REAL_WOF_OWNER_RUNNER.md`
- durable RESULT: `parallel/TRAINING_FARM_R0_4_REAL_WOF_PROOF_OWNER_RUNNER_PREP/RESULT.md`

That package is COMPLETE and must remain the proof authority. Do not reimplement R0.2 determinism or R0.4 fork logic.

Owner is a Windows beginner. The remaining usability problem is that the strict runner expects `WOF_ROM_PATH` and environment prerequisites, which forces manual command-line setup.

Repository also records an Owner-local ROM reference only as metadata, never as ROM bytes:

`training/farm/OWNER_LOCAL_ROM_REFERENCE.md`

Recorded reference at PM creation time:

- display filename: `wof(2).zip`
- size: `6366259` bytes
- SHA256: `6355d82b9457433725fe53cf1723f94eef752b569f3c07b51ac7e57be4a3cbaa`

This reference is for accidental-wrong-file protection only. ROM bytes remain local/external and must never be committed.

## Goal

Create a Windows-first **beginner launcher** so Owner can:

1. double-click one obvious `.cmd` file;
2. choose the local WOF `.zip` through a normal Windows file picker (or equivalent drag/drop fallback);
3. receive clear Chinese prerequisite guidance without manually setting `WOF_ROM_PATH`;
4. run the existing strict Owner real-proof runner unchanged in authority semantics;
5. get one final Chinese/English PASS / WAITING_PREREQUISITE / BLOCKED summary;
6. automatically see where `summary.txt`, `summary.json`, R0.2 JSON and R0.4 JSON were saved.

This is an Owner UX/onboarding module only. It does not authorize R0.5.

## Required implementation

### 1. One obvious beginner entry point

Add an obvious Windows entry, preferred name:

`training/farm/run_real_wof_proof_beginner.cmd`

Double-click must be the primary path. It may delegate to PowerShell/Python helper code under `training/farm/**`.

No PowerShell execution-policy weakening, registry mutation, admin requirement, global keyboard injection or unsafe shell tricks.

### 2. ROM chooser

When `WOF_ROM_PATH` is absent, open a standard Windows `.zip` file picker or provide an equivalently beginner-safe selection UX.

Requirements:

- selected path must remain outside repository;
- `.zip` only;
- preserve spaces / Chinese path names / parentheses;
- never copy the ROM into repo;
- never unzip/copy ROM bytes into repo artifacts;
- set `WOF_ROM_PATH` only for the launched proof process/session unless Owner explicitly already configured it globally;
- cancel => clean `WAITING_PREREQUISITE`, not traceback.

### 3. Recorded-ROM reference check

Read the current `training/farm/OWNER_LOCAL_ROM_REFERENCE.md` if present.

For the recorded Owner ROM, show a clear confirmation when the selected file matches the recorded SHA256/size.

If it does not match, default fail closed with a beginner-readable message like:

`WAITING_PREREQUISITE — 选择的 ZIP 与当前 Owner ROM 记录不一致，请重新选择正确文件`

Do not silently rewrite the recorded hash. Do not accept filename equality as identity.

Provide an expert-only explicit CLI override only if truly necessary for a future different legally-held ROM; beginner double-click flow should not bypass the recorded identity by default.

### 4. Dependency guidance

Keep the existing strict runtime preflight authoritative.

The beginner launcher may detect obvious missing prerequisites before handoff and translate them to Chinese, including:

- Python unavailable/unsupported;
- `stable-retro==0.9.8` missing/wrong version;
- FBNeo capability not ready;
- ROM selection missing/wrong;
- evidence directory unavailable.

Do not silently install packages by default.

If you add an optional dependency-install helper, it must require explicit Owner confirmation and may install only the pinned open-source Python dependency required by current Farm policy. It must never download ROM, BIOS, proprietary emulator binaries or copyrighted game assets.

### 5. Preserve proof authority

The beginner layer must ultimately call the existing:

`python -m training.farm.real_wof_proof_owner_runner`

or an authority-equivalent direct entry to that same current module.

Do not duplicate, relax or replace:

- R0.2 real determinism consumer;
- R0.4 real fork validation;
- source-drift guard;
- ROM SHA binding;
- proof scopes;
- evidence directory rules;
- `realWofProof=true` requirements.

No fixture/synthetic result may become real proof because of beginner UX.

### 6. Beginner final screen

At end, keep the console visible long enough for a beginner to read the result.

Show one primary verdict:

- `PASS — R0.2 REAL WOF DETERMINISM + R0.4 REAL FORK SMOKE`
- `WAITING_PREREQUISITE — ...`
- `BLOCKED — R0.2 REAL DETERMINISM — ...`
- `BLOCKED — R0.4 REAL FORK SMOKE — ...`

Also show:

- exact local evidence directory;
- which JSON files exist;
- simple instruction: PASS => tell PM `1`; WAITING/BLOCKED => send `summary.txt` or screenshot.

If practical without weakening security, open the evidence directory after completion or provide a one-key/open-folder option.

### 7. Windows path robustness

Implementation-owned self-check must cover at minimum:

- ROM path with spaces;
- Chinese directory names;
- parentheses filename like `wof(2).zip`;
- picker cancel;
- wrong ZIP/hash;
- matching recorded hash;
- existing `WOF_ROM_PATH` behavior;
- no ROM copy into repo;
- runner child environment receives exact selected path;
- PASS/WAITING/BLOCKED final messaging;
- duplicate/reposted task preflight behavior remains policy-compliant.

Use mocked/stubbed proof execution where real runtime is unavailable. Never label mock result as real WOF proof.

## Boundaries

Allowed writes:

- `training/farm/**` beginner UX/helper/tests/docs;
- `parallel/TRAINING_FARM_R0_4_OWNER_BEGINNER_REAL_WOF_LAUNCHER_V1/**`;
- this task's canonical/stage claims and RESULT.

Do not modify:

- `product/alpha/**`;
- Browser/Transport/Recorder/PYLAUNCH/OneClick product semantics;
- WinKawaks Collector;
- R0.5 implementation;
- Reward/search/multi-worker/RL semantics;
- ROM/BIOS/game binary assets.

Do not commit, vendor, base64, split, encrypt or otherwise smuggle the Owner ROM into Git.

## Testing cadence

Follow `parallel/PM/TESTING_CADENCE_POLICY.md`:

`implement complete beginner UX -> integrate with existing strict runner -> one compact implementation-owned self-check -> fix only concrete failures -> durable RESULT -> close claim/stage`

No Fresh QA / second-opinion / cross-check generation from this task.

## Durable RESULT

Write:

`parallel/TRAINING_FARM_R0_4_OWNER_BEGINNER_REAL_WOF_LAUNCHER_V1/RESULT.md`

Record:

- exact implementation candidate;
- files changed;
- self-check commands/results;
- current Owner ROM reference hash used for UX guard;
- explicit statement that ROM bytes were never committed;
- explicit statement that no real proof was fabricated;
- exact beginner command/path;
- remaining Owner action;
- claim/stage closeout state.

## Stop condition

Do not stop after adding a picker or one `.cmd` patch. Continue until the full beginner flow, integration, tests, docs, RESULT and claims are complete unless a concrete external blocker prevents further repository work.

Allowed final states only:

`COMPLETE — TRAINING FARM R0.4 OWNER BEGINNER REAL-WOF LAUNCHER V1 — READY FOR OWNER DOUBLE-CLICK RUN`

or

`BLOCKED — TRAINING FARM R0.4 OWNER BEGINNER REAL-WOF LAUNCHER V1 — <exact blocker>`

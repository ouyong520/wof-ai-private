# Training Farm R0.4.7 — Windows Portable Real-WOF Proof Bundle V1

## PM authority / dedup

- stageId: `TRAINING_FARM_R0_4_7_WINDOWS_PORTABLE_REAL_WOF_PROOF_BUNDLE_V1`
- dedupProtocol: `v2`
- dedupKey: `training.farm.r0.4.7.windows-portable-real-wof-proof-bundle-v1`
- dedupMode: `exclusive`
- canonical claim path: `parallel/PM/DEDUP_CLAIMS/training.farm.r0.4.7.windows-portable-real-wof-proof-bundle-v1.json`
- stage claim path: `parallel/PM/STAGE_CLAIMS/TRAINING_FARM_R0_4_7_WINDOWS_PORTABLE_REAL_WOF_PROOF_BUNDLE_V1.json`

Canonical dedup v2 is mandatory. Before any mutation, re-read current `main`, this prompt, `parallel/PM/STAGE_DEDUP_GUARD.md`, `parallel/PM/TESTING_CADENCE_POLICY.md`, current R0.2/R0.4/R0.4.5/R0.4.6 durable RESULTs, their current source blobs, and search for equivalent claims/results/prompts/packages. If equivalent work is already COMPLETE, stop `ALREADY COMPLETE — SAFE TO CLOSE`. If validly claimed, stop `ALREADY CLAIMED — SAFE TO CLOSE`. Never steal or overwrite historical claims; only PM-authorized recovery may supersede them.

## Context

Training Farm repository implementation through R0.4.6 is complete, while authoritative real WOF proof is still Owner-local. Current Owner burden has been reduced by the strict proof runner, beginner ROM picker, and R0.4.6 environment bootstrap, but those flows still assume the Owner has downloaded/extracted the full private repository tree.

The Owner is a beginner and wants a direct, portable Windows package that can be downloaded, extracted under a simple local root such as `F:\三国\三国10训`, and run without understanding the repository layout.

This is another **gate-reduction / packaging stage**, not R0.5 and not real-proof execution authority.

## Hard boundaries

This task MUST NOT:

- claim or fabricate R0.2 `REAL_WOF` PASS;
- claim or fabricate R0.4 `REAL_WOF_FORK` PASS;
- alter `realWofProof`, proof scope, exact runtime/ROM/source identity, determinism, fork semantics, or strict Owner runner acceptance;
- modify proof code merely to make a portable package easier;
- start Reward/Search/RL, 2/4/8/10 worker execution, teacher or safe-path work;
- guess WOF semantic RAM addresses;
- download, include, vendor, copy, encode, split, transform, or distribute any ROM/BIOS/game asset;
- package user-local ROM bytes or any ROM-derived payload other than permitted metadata/hash authority already in the repository;
- use host/global keyboard or mouse injection, `SendInput`, AutoHotkey gameplay control, focus switching, or visible emulator automation;
- modify `product/alpha/**`, Collector, Transport, Recorder, PYLAUNCH, OneClick Alpha packaging, or unrelated lanes.

A portable package is not proof. Fixture/self-check evidence must remain `realWofProof=false`.

## Goal

Produce a deterministic, immutable, Windows-first **portable proof bundle** containing only the minimum repository source/configuration required to:

1. bootstrap/reuse a supported local Python 3.10..3.14 environment;
2. create/reuse the dedicated `.venv` outside or adjacent to the portable source package as designed by R0.4.6;
3. install the exact checked-in dependency authority, currently `stable-retro==0.9.8` unless current source authority says otherwise;
4. validate Stable-Retro + FBNeo capability ROM-free;
5. open the existing beginner ROM picker for an Owner-local external WOF ZIP;
6. run the existing strict current-source R0.2 then R0.4 real proof path;
7. write evidence to an obvious external/local `evidence` directory;
8. show PASS / WAITING_PREREQUISITE / BLOCKED clearly.

The Owner should not need to clone the repo, install Git, understand `training\farm`, or copy individual files manually.

## Required implementation

### 1. Minimal portable source closure

Determine the exact transitive source/config/schema/document closure needed by:

- `training.farm.windows_oneclick_bootstrap`;
- `training.farm.beginner_real_wof_launcher`;
- `training.farm.real_wof_proof_owner_runner`;
- current R0.2 determinism runtime;
- current R0.4 fork runtime;
- current Stable-Retro/FBNeo adapter and runtime identity;
- any exact plans/actions/schemas required by the strict Owner proof.

Do not simply copy the whole private repository. Build a narrow allowlisted closure. Explicitly exclude unrelated Alpha/Collector/private PM history, tests not needed at runtime, ROM/BIOS/game files, `.git`, caches, secrets, local evidence and local virtualenvs.

If some repository metadata is truly required for source identity, include only the exact required files and document why.

### 2. Deterministic package manifest

Create a strict manifest with at least:

- manifest schema/version;
- package/stage ID;
- exact source candidate commit;
- package build timestamp only if it is not part of immutable identity, otherwise use deterministic metadata;
- every included relative path;
- exact byte size;
- SHA-256;
- executable/role classification where useful;
- exact R0.2/R0.4/R0.4.6 authority blobs consumed;
- exact dependency-authority file/hash;
- explicit `containsRomBytes=false`;
- explicit `realWofProof=false`;
- explicit `r0_5Authorized=false`;
- package payload aggregate SHA-256 or Merkle/canonical identity;
- builder/source identity.

Manifest parsing/validation must reject missing, extra, duplicate, path traversal, absolute paths, malformed hashes, and payload drift.

### 3. Deterministic package builder

Add a ROM-free package builder under `training/farm/**` or a clearly scoped packaging path. It must:

- operate from current source;
- assemble the exact allowlisted portable tree in a clean staging directory;
- verify each selected source blob before packaging;
- produce a deterministic ZIP where practical (stable file ordering, stable archive paths, stable timestamps/metadata or document unavoidable platform limits);
- never follow unsafe symlinks/path traversal;
- never include ignored/local ROM/evidence/venv/cache files;
- fail closed if selected source has drifted from manifest/build authority;
- emit package SHA-256 and manifest SHA-256;
- be safe to run without ROM and without Stable-Retro.

Do not commit third-party wheels or Python installers unless repository policy and licenses clearly authorize it. Normal package may install dependencies from the configured package index through R0.4.6.

### 4. Root-level beginner entry

Inside the portable bundle, provide an obvious Windows entry such as:

`开始三国10训实机验证.cmd`

or equivalent ASCII fallback if codepage/ZIP tooling requires it.

It should:

- resolve its own portable root;
- invoke the existing R0.4.6 bootstrap using packaged source;
- default local data root to the portable bundle parent or a sibling `三国10训-data`/documented root without hard-coding one machine drive;
- keep `.venv`, `ROM`, `evidence`, `logs`, `runtime`, `training-data`, `checkpoints` outside the immutable payload if that improves source-identity stability;
- handle Chinese characters, spaces and parentheses in Windows paths;
- preserve child exit code and keep the window visible on error;
- never silently elevate, change global Python, registry, PATH, system policy or firewall;
- never download ROM/BIOS.

If an explicit local root such as `F:\三国\三国10训` is supplied, it may be accepted as configuration, but must not be repository-global authority.

### 5. Package verification command

Provide a no-ROM verifier that the Owner/PM can run before proof. It should validate:

- manifest structure;
- every packaged file size/hash;
- aggregate package identity if applicable;
- selected source authority/current package candidate;
- no forbidden ROM/BIOS/game extensions or known local-only paths;
- no path traversal/absolute entries;
- no unexpected extra files inside immutable payload;
- bootstrap entry exists;
- proof runner closure is complete.

Return clear PASS/BLOCKED structured output.

### 6. Optional immutable artifact publication

If repository/tooling supports it safely, produce a durable immutable ZIP artifact with a versioned name containing a short package identity, for example:

`WOF_Training_Farm_R0_4_7_Portable_Proof_<shortsha>.zip`

If committing binary ZIP to Git is undesirable, do not force it. Instead provide the deterministic builder plus durable manifest and, if available, a GitHub Actions artifact/release mechanism that does not include ROM bytes. The RESULT must state exactly how the Owner obtains the ZIP.

Do not publish a package that cannot be tied to an exact manifest/source candidate.

### 7. Portable package documentation

Write beginner documentation that says, in simple Chinese:

1. download the one ZIP;
2. extract to e.g. `F:\三国\三国10训`;
3. double-click the top-level start `.cmd`;
4. if Python is missing, install supported Python and rerun;
5. select the Owner-local WOF ZIP when prompted;
6. find final evidence path and send `summary.txt`/`summary.json` plus strict JSON results back to PM if needed.

Clearly state ROM is not included and must remain external/local.

## Current-source authority preservation

The portable package must consume the **current** strict proof implementation and must not fork a second weaker copy.

At minimum compare/reconcile exact current blobs for:

- `training/farm/stable_retro_backend.py`;
- `training/farm/identity.py`;
- `training/farm/determinism.py` and schema/actions;
- R0.4 fork modules/schemas/plan;
- `training/farm/real_wof_proof_owner_runner.py`;
- `training/farm/beginner_real_wof_launcher.py`;
- `training/farm/windows_oneclick_bootstrap.py`;
- `training/farm/requirements-r0.1.txt`;
- any metadata consumed for Owner ROM identity.

If current source changed materially while packaging, rebuild/re-pin the package. Never package a stale proof runtime and call it current.

## Safety / path rules

- ROM path remains outside immutable source payload.
- Evidence remains outside immutable source payload.
- `.venv` remains uncommitted/unpackaged unless there is an explicitly justified safe design; default is to create it locally.
- Never write ROM bytes to logs, manifest, evidence summaries beyond allowed SHA/path metadata already used by strict proof.
- Reject extraction/package entries containing `..`, drive-qualified absolute paths, UNC escape paths, or equivalent traversal.
- Windows Chinese/space/parentheses paths must be tested.

## Implementation-owned self-check

After coherent implementation, run one compact ROM-free self-check. Cover at least:

- exact allowlist closure builds successfully;
- deterministic repeated build gives identical payload/manifest identity where intended;
- manifest strict parse and full payload verification;
- one-byte tamper rejection;
- missing file rejection;
- extra file rejection;
- duplicate/path traversal/absolute-path ZIP entry rejection;
- forbidden ROM-like payload rejection;
- Chinese/space/parentheses extraction path;
- root-level `.cmd` resolves packaged source correctly via mocks/fixture;
- R0.4.6 bootstrap invocation preserves local-root/evidence arguments and child exit code;
- package contains no ROM bytes, venv, evidence, cache or unrelated private project trees;
- current R0.2/R0.4 strict source blobs are unmodified in the selected closure;
- package verifier is ROM-free;
- `realWofProof=false`, `r0_5Authorized=false`, and no real emulator worker executed.

Use only implementation self-check; do not open repetitive Fresh QA unless a concrete package defect warrants it.

## Durable RESULT / closeout

Write durable RESULT at:

`parallel/TRAINING_FARM_R0_4_7_WINDOWS_PORTABLE_REAL_WOF_PROOF_BUNDLE_V1/RESULT.md`

Include:

- exact source/package candidate;
- current-main reconciliation;
- included runtime closure and exact blobs;
- package/manifest SHA-256;
- exact artifact/download/build path;
- self-check commands and observed outcomes;
- explicit `containsRomBytes=false`;
- explicit no real-WOF PASS claim;
- explicit R0.5 still locked;
- exact next Owner action.

Token-verify and close canonical + stage claims to COMPLETE. Do not stop at claim acquisition, package build, single test, or WAITING if repository work is complete.

## Stop condition

Only:

- `COMPLETE — TRAINING FARM R0.4.7 WINDOWS PORTABLE REAL-WOF PROOF BUNDLE V1 — IMMUTABLE OWNER PACKAGE READY; REAL R0.2/R0.4 PROOF STILL REQUIRED`
- precise irreducible `BLOCKED — <exact blocker>`
- canonical duplicate stop.

# WOF Training Farm R0.4 — Real-WOF Proof Owner Runner Prep

stageId: `TRAINING_FARM_R0_4_REAL_WOF_PROOF_OWNER_RUNNER_PREP_V1`
dedupProtocol: `v2`
dedupKey: `training.farm.r0.4.real-wof-proof-owner-runner-prep`
dedupMode: `exclusive`

Priority: **Training Farm current highest-value repository-side gate reducer**

## Goal

R0.2, R0.3 tooling prep and R0.4 fork primitive are repository-complete, but progression remains blocked on an intrinsically local authority fact: a legal local WOF ROM running under pinned Stable-Retro/FBNeo must produce a current-source real R0.2 determinism PASS before any authoritative real R0.4 fork proof or later R0.5 progression.

This stage must reduce that Owner burden to one bounded, obvious local command/package. Build a complete Owner-facing **real-proof runner/preflight/evidence-capture package** that:

1. detects and reports local prerequisites without guessing or silently fixing unsupported conditions;
2. runs the exact current-source R0.2 real determinism proof against a legal external WOF ROM;
3. validates and preserves the resulting structured JSON authority;
4. only if R0.2 real proof passes, runs one bounded current-source R0.4 real fork smoke using that exact proof;
5. validates and preserves the R0.4 structured result;
6. produces one concise final Owner summary telling PM whether the real gate is PASS, SKIP, or BLOCKED and where the local JSON evidence lives.

This is a repository implementation/preparation stage. It must **not** fabricate real WOF evidence, include ROM bytes, claim PASS from fixtures, implement R0.5, change Reward/search policy, or modify Alpha/Collector lanes.

## Mandatory duplicate / canonical-dedup preflight

Before any substantive work, re-read current `main`, `parallel/PM/STAGE_DEDUP_GUARD.md`, `parallel/PM/TESTING_CADENCE_POLICY.md`, `parallel/PM/WORKER_HANDOFF_FORMAT_POLICY.md`, `RUNTIME_DATA_SOURCE_BOUNDARIES.md`, current Training Farm RESULT/claim state, and recent Training Farm commits.

Specifically inspect:

- `parallel/TRAINING_FARM_R0_2/RESULT.md`;
- `parallel/TRAINING_FARM_R0_3_OBSERVATION_DISCOVERY_TOOLING_PREP/RESULT.md`;
- `parallel/TRAINING_FARM_R0_3_OBSERVATION_DISCOVERY_TOOLING_PREP_CLOSEOUT_RECOVERY_V2/RESULT.md`;
- `parallel/TRAINING_FARM_R0_4/RESULT.md`;
- current R0.4 Recovery V2 canonical/stage claims;
- current `training/farm/**` CLI/schema/runtime files.

If an equivalent Owner real-proof runner package is already COMPLETE, stop immediately:

`ALREADY COMPLETE — SAFE TO CLOSE`

If the canonical logical task is already validly claimed by another worker, stop immediately:

`ALREADY CLAIMED — SAFE TO CLOSE`

Do not execute duplicate work merely because the Owner forwarded the same or an equivalent prompt twice.

If work is still needed, first mutation must be create-only canonical claim:

`parallel/PM/DEDUP_CLAIMS/training.farm.r0.4.real-wof-proof-owner-runner-prep.json`

Generate a fresh unpredictable `claimToken`, re-read current `main` and the exact canonical claim, verify all metadata/token fields, then create:

`parallel/PM/STAGE_CLAIMS/TRAINING_FARM_R0_4_REAL_WOF_PROOF_OWNER_RUNNER_PREP_V1.json`

Any ambiguity => fail closed; never steal or overwrite another active claim.

## Required module surface

### 1. One obvious Owner command

Provide one obvious Windows-first command/package suitable for the Owner machine, with a Python implementation underneath so behavior is testable and not dependent on shell parsing alone.

Preferred shape:

- a Python runner under `training/farm/**`;
- a small `.cmd` or PowerShell wrapper if useful for Windows one-click use;
- optional Linux invocation documented for development only.

The Owner should not need to manually assemble R0.2/R0.4 commands, copy hashes, edit JSON, or decide whether a fixture result is authoritative.

### 2. Strict prerequisite preflight

The runner must explicitly check and report at minimum:

- current source namespace exactly `stable-retro-fbneo`;
- supported Python version according to current Training Farm contract;
- pinned `stable-retro==0.9.8` availability/version;
- `WOF_ROM_PATH` presence;
- ROM path is external to the repository and resolves to a readable file;
- ROM SHA-256 can be computed in place;
- current R0.2/R0.4 schemas/CLIs are present;
- local proof output directory is writable;
- no repository-local ROM/BIOS/core/savestate material is required or copied.

Do not silently download ROMs, BIOS files, emulator binaries, or copyrighted game data.

Dependency installation may be documented and optionally invoked only for the already-authorized pinned Python package dependency when safe, but the runner must not make network installation success part of proof authority.

### 3. Current-source R0.2 real determinism execution

Use the existing current-source R0.2 implementation as authority; do not reimplement determinism logic.

Run the exact real path with a bounded explicit action sequence, exact frame horizon and repetitions, writing JSON to a local-only proof file.

The runner must validate the result using the repository schema and strict semantic checks before treating it as a gate PASS.

Required PASS authority includes at minimum:

- `status = PASS`;
- `reasonCode = DETERMINISM_MATCH`;
- `proofScope = REAL_WOF`;
- `realWofProof = true`;
- source namespace/current Farm candidate identity matches the current source contract;
- ROM/runtime/backend/core identity is structurally valid and bound;
- all required repetitions/checkpoints complete;
- no malformed/coercible result fields accepted.

Fixture/synthetic PASS must never satisfy this gate.

If R0.2 returns SKIP/FAIL/ERROR, stop before R0.4 and preserve exact diagnostics.

### 4. Bounded R0.4 real fork smoke after R0.2 PASS

Only after the exact current run's validated R0.2 real proof passes, run one bounded R0.4 real fork smoke using the existing fork primitive and that exact R0.2 proof.

Do not invent gameplay reward or semantic meaning. Use a small canonical branch fixture appropriate for proving:

- root authority capture;
- multiple explicit branches;
- branch isolation;
- repeated deterministic replay;
- complete result authority;
- `REAL_WOF_FORK` / real proof classification only when the existing R0.4 contract itself authorizes it.

Validate the R0.4 result strictly against its current published schema/runtime contract. A malformed, partial, skipped, non-deterministic, wrong-proof-scope, stale-source, or wrong-ROM result cannot be summarized as PASS.

### 5. Local-only evidence bundle

Create a local-only output layout ignored by Git, for example under a clearly named Training Farm local proof directory.

Preserve compact evidence only:

- R0.2 structured JSON;
- R0.4 structured JSON when run;
- concise preflight/final summary JSON or text;
- hashes/identity metadata already produced by existing modules.

Do **not** store in Git:

- ROM bytes;
- savestate bytes;
- BIOS/core binaries;
- raw full RAM dumps;
- copyrighted game assets.

Update `.gitignore` only if required to ensure generated local proof artifacts cannot be accidentally committed.

### 6. Final Owner verdict

The runner must end with one machine-readable and human-readable final state such as:

- `PASS — R0.2 REAL WOF DETERMINISM + R0.4 REAL FORK SMOKE`;
- `WAITING_PREREQUISITE — <exact missing local prerequisite>`;
- `BLOCKED — R0.2 REAL DETERMINISM — <exact failure>`;
- `BLOCKED — R0.4 REAL FORK SMOKE — <exact failure>`.

Include exact local evidence paths and relevant result hashes/IDs without printing ROM contents.

No ambiguous “probably ready” state.

### 7. Authority / source drift protection

The preparation package must fail closed if the current repository source changes in a way that invalidates the R0.2/R0.4 candidate identities between preparation and execution.

Do not hard-code old candidate hashes from historical RESULT files as current authority. Consume current repository/runtime contracts and validate what the existing modules emit.

Do not import Browser/WASM or WinKawaks numeric offsets, semantics, lifecycle identities, or timing authority.

### 8. No R0.5 implementation

This stage does not authorize:

- 2/4/8/10 worker orchestration;
- Reward V0;
- best-branch selection;
- beam/MCTS/A*/route search;
- PPO/SB3/RL;
- search teacher;
- safe-route or safe-action recommendation;
- semantic WOF address mapping without separate live evidence.

The only goal is to make the existing real authority gates executable by the Owner with minimal manual work.

## Integration / documentation

Document:

- the one Owner command;
- prerequisite meaning;
- where local evidence is written;
- exact PASS/SKIP/BLOCKED interpretation;
- why fixture PASS is insufficient;
- legal/external ROM boundary;
- what PM may legitimately start only after a real PASS.

Keep R0.1/R0.2/R0.3/R0.4 existing commands compatible unless a narrow backward-compatible refactor is necessary.

## Testing cadence

Follow `parallel/PM/TESTING_CADENCE_POLICY.md`.

Preferred order:

`implement complete owner-runner/preflight/evidence package -> integrate docs/local-output safety -> one compact implementation-owned self-check using fake/stubbed subprocess results -> fix concrete failures -> rerun affected checks -> durable RESULT/claim closeout`

Do not create Fresh QA, second opinion, cross-check, or per-helper QA.

Repository self-check must prove at minimum:

- prerequisite missing -> exact WAITING state;
- fake R0.2 PASS cannot unlock R0.4;
- malformed R0.2 result rejected;
- validated synthetic test double for a REAL-shaped PASS can exercise orchestration without being relabeled as real evidence;
- R0.2 non-PASS stops R0.4 execution;
- R0.4 malformed/partial/non-deterministic result cannot produce final PASS;
- exact local evidence paths/summary are produced;
- no ROM/savestate bytes are written to repository-tracked output;
- duplicate/second run handling does not merge evidence from different ROM/source identities.

Synthetic/stub self-checks are implementation evidence only and must never create a durable real-WOF PASS claim.

## Write boundary

Allowed:

- `training/farm/**`;
- `parallel/TRAINING_FARM_R0_4_REAL_WOF_PROOF_OWNER_RUNNER_PREP/**`;
- necessary canonical/stage claim records.

Forbidden without explicit Owner authority:

- `product/alpha/**`;
- Alpha/Browser proof/release behavior;
- Transport / Recorder / PYLAUNCH / OneClick product lane;
- WinKawaks Collector code/contracts/results;
- ROM/BIOS/emulator binary/copyrighted game assets;
- R0.5 search/reward/multi-worker implementation.

Cross-line dependency => BLOCKED; do not edit another lane to make this package pass.

## Durable RESULT

Before stopping, write:

`parallel/TRAINING_FARM_R0_4_REAL_WOF_PROOF_OWNER_RUNNER_PREP/RESULT.md`

Record:

- exact source candidate/blobs or commit;
- implemented runner/preflight/evidence surface;
- command the Owner will run;
- compact self-check commands/results;
- whether this worker had a real local WOF runtime available;
- real proof result only if legitimately executed with legal local runtime;
- otherwise explicit `OWNER LOCAL RUN REQUIRED`;
- exact next legitimate Training Farm gate after PASS;
- any remaining concrete blocker.

Close canonical/stage claims only while the exact recovery token still matches current Git authority.

## Stop discipline

Do not stop after adding a wrapper, preflight helper, one subprocess call, documentation, or one passing fixture. Finish the entire Owner-runner package, integration, local-output safety, self-check, durable RESULT and claim closeout before stopping unless a genuine repository-side blocker prevents further in-scope progress.

Allowed final states:

`COMPLETE — TRAINING FARM R0.4 REAL-WOF PROOF OWNER RUNNER PREP — OWNER LOCAL RUN REQUIRED`

or, only if a legitimate legal local real run actually occurred and passed:

`COMPLETE — TRAINING FARM R0.4 REAL-WOF PROOF OWNER RUNNER PREP — REAL R0.2 + R0.4 PROOF PASS`

or:

`BLOCKED — TRAINING FARM R0.4 REAL-WOF PROOF OWNER RUNNER PREP — <exact concrete blocker>`

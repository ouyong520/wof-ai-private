# WOF Training Farm R0.3 — Observation Discovery Tooling Prep

stageId: `TRAINING_FARM_R0_3_OBSERVATION_DISCOVERY_TOOLING_PREP_V1`
dedupProtocol: `v2`
dedupKey: `training.farm.r0.3.observation-discovery-tooling-prep`
dedupMode: `exclusive`

Priority: **Training Farm current highest-priority repository implementation while R0.2 real-WOF proof is externally pending**

## Purpose

R0.2 repository implementation is COMPLETE, but real WOF determinism authority is still pending because the worker environment did not have the legal local ROM/runtime. Do not reopen or redo R0.2.

Use this stage to build the complete **observation-discovery tooling module** needed for future R0.3 mapping, without claiming any real WOF address/semantic mapping yet.

This is preparation tooling only. Actual authoritative WOF observation mapping remains locked until a real R0.2 result proves `PASS / DETERMINISM_MATCH` with `realWofProof=true` for the same Stable-Retro/FBNeo runtime/ROM/source identity.

## Start / ownership

Before substantive work, re-read current `main`, at minimum:

- `parallel/PM/STAGE_DEDUP_GUARD.md`;
- `parallel/PM/TESTING_CADENCE_POLICY.md`;
- `parallel/PM/WORKER_HANDOFF_FORMAT_POLICY.md`;
- `RUNTIME_DATA_SOURCE_BOUNDARIES.md`;
- `training/farm/README.md`;
- `parallel/TRAINING_FARM_R0_2/RESULT.md`;
- current `training/farm/**`;
- current Training Farm canonical/stage claims and recent commits.

If equivalent tooling is already COMPLETE, stop `ALREADY COMPLETE — SAFE TO CLOSE`.

Otherwise first mutation must be create-only canonical claim:

`parallel/PM/DEDUP_CLAIMS/training.farm.r0.3.observation-discovery-tooling-prep.json`

Use a fresh unpredictable `claimToken`, re-read current `main` and the exact canonical claim, verify ownership, then create:

`parallel/PM/STAGE_CLAIMS/TRAINING_FARM_R0_3_OBSERVATION_DISCOVERY_TOOLING_PREP_V1.json`

Any ownership ambiguity => `ALREADY CLAIMED — SAFE TO CLOSE`.

## Complete module

Finish one coherent observation-discovery tooling module under `training/farm/**` before stopping.

### 1. Preserve address-aware RAM layout

R0.2's flat RAM fingerprint is sufficient for determinism but not for observation discovery. Add a narrow source-specific read interface that can expose the Stable-Retro/FBNeo memory blocks with their real block/base offsets and byte lengths, without removing or breaking the existing flat `read_ram()` compatibility path.

Requirements:

- exact integer base address/offset and bytes for every exposed block;
- deterministic stable ordering;
- reject duplicate/overlapping/malformed block metadata fail-closed where detectable;
- record a canonical memory-layout identity/hash;
- bind layout to `stable-retro-fbneo`, runtime identity, ROM SHA and Farm candidate identity;
- do not import Browser/WASM or WinKawaks offsets.

If upstream Stable-Retro cannot expose a required address fact, preserve the strongest exact information it does expose and report the limitation explicitly rather than inventing addresses.

### 2. Observation experiment contract

Define a strict JSON experiment-plan contract for controlled single-instance observation discovery.

At minimum support:

- experiment/fixture id;
- starting savestate identity;
- baseline action sequence;
- one or more intervention action sequences;
- exact frame horizon;
- repetitions;
- capture/checkpoint frames;
- optional human semantic label/hypothesis stored only as metadata, never as authority.

All player/button/frame/repetition/checkpoint values must remain strict and non-coercive. Reuse R0.2 explicit all-player frame input semantics.

### 3. Controlled replay capture

Build the runner so every baseline/intervention comparison:

- starts from the exact same savestate;
- uses the same runtime/ROM/source/layout identity;
- runs exact frame horizons;
- captures address-aware RAM snapshots/checkpoints;
- preserves experiment/action/savestate identity hashes;
- fails closed on identity drift, layout drift, missing checkpoint, failed restore, bad action, or frame mismatch.

Do not use wall-clock timing as authority.

### 4. Candidate-change analysis

Implement deterministic analysis that compares controlled runs and produces **candidate offsets only**, not semantic truth.

At minimum provide per candidate byte/word location where practical:

- source block/base address context;
- offset within block;
- absolute/source-native address when actually available from the backend;
- baseline values;
- intervention values;
- changed/stable counts across repetitions;
- consistency/stability score based only on observed evidence;
- first/last observed changed frame when available;
- whether the candidate also changed in the control/baseline and therefore should be downgraded;
- deterministic ranking/order.

Keep the analysis bounded. Do not dump enormous RAM histories into Git by default.

### 5. Authority classification

Every output must explicitly distinguish:

- `IMPLEMENTATION_FIXTURE` — fake/ROM-free tooling self-check;
- `REAL_RUNTIME_OBSERVATION_UNVERIFIED` — real runtime data, if ever collected without an accepted same-identity R0.2 proof;
- `REAL_RUNTIME_OBSERVATION_ELIGIBLE` — only when the supplied R0.2 proof is a real PASS and matches the exact current runtime/ROM/source identity.

This stage still must **not** convert candidates into authoritative `playerHp`, `playerX`, `playerY`, enemy slot/state, camera, attack ID, or lifecycle mappings. That semantic proof belongs to the later real R0.3 mapping stage.

Synthetic/fake results can never upgrade themselves to real mapping authority.

### 6. R0.2 proof gate for real discovery

Add a strict consumer/validator for the R0.2 determinism JSON used to authorize future real observation discovery.

Before any real run can be classified eligible, require at minimum:

- correct R0.2 schema/result shape;
- `status == PASS`;
- `reasonCode == DETERMINISM_MATCH`;
- `realWofProof == true`;
- real proof scope, not implementation fixture;
- exact ROM SHA match;
- exact source namespace match;
- exact Stable-Retro/core/runtime identity fields needed by current authority;
- exact Farm candidate/source compatibility according to an explicit documented rule;
- no malformed/coercible identity fields.

Missing, fixture, stale or mismatched proof => fail closed. Tooling may still run ROM-free fixtures, but it must not label real discovery eligible.

Do not create a fake proof merely to exercise this gate; module tests may construct synthetic fixture objects clearly marked test-only.

### 7. CLI and structured outputs

Provide one obvious CLI for the observation-discovery tooling, for example a module-owned command taking an experiment-plan JSON and optional R0.2 proof JSON.

Output structured JSON with at minimum:

- schema version;
- source namespace;
- experiment id;
- authority classification;
- runtime/ROM/source/layout identity;
- starting savestate identity;
- action-sequence identities;
- frame horizon/repetitions/checkpoints;
- ranked candidate changes;
- exact failure/skip reason;
- whether real R0.3 semantic mapping is unlocked (`false` in fake/prep-only execution).

Large raw captures/savestates remain local-only by default. Repository may contain schemas, small fixtures/examples, code, tests and compact result metadata.

### 8. Fake backend / implementation fixture

Extend the existing fake backend or add a narrow module-owned fixture so the complete capture + layout + diff/ranking + authority-gate control flow can be self-checked without a ROM.

The fake fixture should contain a few known synthetic changing locations so the analyzer can prove it ranks deterministic candidates correctly.

Fixture success must remain clearly non-authoritative for WOF.

### 9. Documentation / integration

Update Training Farm docs for:

- what the observation-discovery tooling does;
- why address-aware blocks differ from the R0.2 flat determinism fingerprint;
- exact CLI examples;
- R0.2 proof gate;
- output interpretation;
- local-only artifact handling;
- explicit statement that no WOF semantic address is proven by this prep stage.

Keep R0.1/R0.2 commands compatible unless a small compatible refactor is required.

## Testing cadence

Follow `parallel/PM/TESTING_CADENCE_POLICY.md`.

Preferred order:

`implement complete tooling -> wire schemas/CLI/docs -> compact module-owned self-check -> fix concrete failures -> rerun only affected checks -> RESULT/claim closeout`

Do not open Fresh QA, cross-check, second opinion, or per-helper QA from this task.

Use enough self-check coverage to prove:

- layout preservation and deterministic identity;
- experiment strictness;
- same-state controlled replay;
- candidate diff/ranking;
- R0.2 proof gate fail-closed;
- fixture cannot masquerade as real mapping authority.

Do not multiply test cases after these module contracts are established.

## Write boundary

Allowed:

- `training/farm/**`;
- `parallel/TRAINING_FARM_R0_3_OBSERVATION_DISCOVERY_TOOLING_PREP/**`;
- canonical/stage claim updates for this stage.

Forbidden:

- `product/alpha/**`;
- Alpha/Browser proof/release files;
- Transport / Recorder / PYLAUNCH / OneClick;
- WinKawaks Collector repository/contracts/results;
- Browser/WinKawaks numeric offsets as Stable-Retro authority;
- actual authoritative WOF semantic mapping claims without the real R0.2 gate;
- 2/4/8/10 worker orchestration;
- PPO/SB3/RL;
- route/search-teacher/safe-path implementation.

Cross-line dependency => BLOCKED; do not edit the other lane.

## Durable result

Before stopping write:

`parallel/TRAINING_FARM_R0_3_OBSERVATION_DISCOVERY_TOOLING_PREP/RESULT.md`

Record:

- exact implementation commit/blobs;
- implemented module surface;
- commands actually run;
- compact self-check results;
- schema/CLI paths;
- whether real R0.2 proof was available;
- authority classification reached;
- exact remaining Owner action;
- whether **real R0.3 semantic observation mapping** is unlocked.

Expected in the current known environment: tooling can be COMPLETE while real semantic mapping remains locked pending Owner local R0.2 proof.

Close canonical/stage claims only with the matching `claimToken` and current blob SHA.

## Stop discipline

**Do not stop after analysis, interface design, one helper, one schema, one CLI, or one passing unit test. Finish the full address-aware capture + controlled experiment + candidate analysis + R0.2 proof gate + structured output + documentation + compact self-check + durable RESULT + claim closeout before stopping, unless a genuine external blocker makes further in-scope repository work impossible.**

Keep progress reporting minimal. Prefer implementation over narration.

Allowed final states:

`COMPLETE — TRAINING FARM R0.3 OBSERVATION DISCOVERY TOOLING PREP — REAL SEMANTIC MAPPING LOCKED PENDING R0.2 REAL-WOF PROOF`

or, only if a valid matching real R0.2 proof is actually available and the tooling is fully complete:

`COMPLETE — TRAINING FARM R0.3 OBSERVATION DISCOVERY TOOLING PREP — READY FOR REAL R0.3 SEMANTIC MAPPING`

or:

`BLOCKED — TRAINING FARM R0.3 OBSERVATION DISCOVERY TOOLING PREP — <exact concrete blocker>`

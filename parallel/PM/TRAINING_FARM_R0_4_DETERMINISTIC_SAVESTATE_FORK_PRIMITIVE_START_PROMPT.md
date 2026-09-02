# WOF Training Farm R0.4 — Deterministic Savestate Fork Primitive

stageId: `TRAINING_FARM_R0_4_DETERMINISTIC_SAVESTATE_FORK_PRIMITIVE_V1`
dedupProtocol: `v2`
dedupKey: `training.farm.r0.4.deterministic-savestate-fork-primitive`
dedupMode: `exclusive`

Priority: **Training Farm next coherent implementation module**

## Goal

Build the complete R0.4 deterministic savestate fork primitive on the current R0.2/R0.3 Training Farm stack.

The primitive must support:

`one authoritative root savestate -> N explicit action branches -> isolated deterministic branch outcomes`

This stage is about the branch/fork execution substrate only. It must not invent WOF semantic addresses, implement multi-worker orchestration, define Reward V0, choose a “best” branch, train a policy, or start safe-route/search-teacher work.

## Start / ownership

Before substantive work, re-read current `main`, `parallel/PM/STAGE_DEDUP_GUARD.md`, `parallel/PM/TESTING_CADENCE_POLICY.md`, `parallel/PM/WORKER_HANDOFF_FORMAT_POLICY.md`, `RUNTIME_DATA_SOURCE_BOUNDARIES.md`, current `training/farm/**`, and at minimum:

- `parallel/TRAINING_FARM_R0_2/RESULT.md`;
- `parallel/TRAINING_FARM_R0_3_OBSERVATION_DISCOVERY_TOOLING_PREP/RESULT.md`;
- `parallel/TRAINING_FARM_R0_3_OBSERVATION_DISCOVERY_TOOLING_PREP_CLOSEOUT_RECOVERY_V2/RESULT.md`;
- current Training Farm canonical/stage claims and recent Training Farm commits.

If equivalent R0.4 fork work is already COMPLETE, stop `ALREADY COMPLETE — SAFE TO CLOSE`.

Otherwise first mutation must be create-only canonical claim:

`parallel/PM/DEDUP_CLAIMS/training.farm.r0.4.deterministic-savestate-fork-primitive.json`

Generate a fresh unpredictable `claimToken`, re-read current `main` and exact canonical claim, verify ownership exactly, then create:

`parallel/PM/STAGE_CLAIMS/TRAINING_FARM_R0_4_DETERMINISTIC_SAVESTATE_FORK_PRIMITIVE_V1.json`

Any ownership ambiguity => `ALREADY CLAIMED — SAFE TO CLOSE`.

## Complete module requirements

Finish one coherent R0.4 module before stopping.

### 1. Root savestate authority

Create a strict root-state envelope containing at minimum:

- source namespace exactly `stable-retro-fbneo`;
- root savestate SHA-256;
- root RAM SHA-256 and address-aware layout identity when available;
- runtime / ROM / backend / Farm candidate identity;
- experiment/fork-set identity;
- root capture frame / logical frame counter where the module can authoritatively maintain it.

The root state must be immutable for one fork set. Runtime/ROM/source/layout drift invalidates the fork set fail-closed.

Do not serialize legal ROM bytes into repository artifacts.

### 2. Canonical branch contract

Define a strict branch specification with stable branch identity. At minimum each branch must bind:

- `branchId`;
- canonical explicit action sequence using current all-player frame input semantics;
- exact horizon in emulator frames;
- action-sequence SHA-256;
- optional human metadata/label that is never execution authority.

Reject duplicate branch IDs, malformed/coercible integers, malformed action inputs, mismatched horizon, unsupported player/button values, or non-canonical branch structures.

Branch ordering must be deterministic and must not change execution meaning.

### 3. Fork execution primitive

For every branch:

1. verify current authority against the fork-set root;
2. load the exact root savestate;
3. verify restored RAM and savestate roundtrip authority before branch execution;
4. execute only that branch's explicit action sequence for the exact frame horizon;
5. capture deterministic outcome evidence;
6. never allow state/input from a previous branch to leak into the next branch;
7. restore from root again before the next branch.

At minimum outcome evidence must include:

- branchId;
- action/horizon identity;
- executed frame count;
- final RAM SHA-256;
- useful bounded checkpoint hashes sufficient to locate branch execution divergence;
- final savestate SHA-256 if stable and meaningful under the current backend contract;
- address-aware RAM layout identity where available;
- status/reason code.

### 4. Deterministic branch replay

The primitive must be able to rerun a branch from the same root and verify deterministic equality.

Provide a compact repeat count appropriate for implementation proof. A branch cannot be classified deterministic unless all required repetitions complete and match exactly for the observables used by the module.

A mismatch must identify the first known divergent checkpoint/frame when possible.

Fake backend evidence remains implementation-only and cannot become real WOF proof.

### 5. Cross-branch isolation / fail-closed

Explicitly protect against:

- previous branch input mask persisting into the next branch;
- previous branch RAM/state being used as another branch's root;
- branch result being attached to the wrong branchId/action hash;
- root state changing mid-set;
- runtime/ROM/core/Farm source/layout identity drift;
- missing or duplicate branch completion;
- partial execution being reported as whole-set PASS;
- malformed result objects being accepted as authoritative fork evidence.

One failed branch may be reported individually, but the overall fork set must not claim complete success when a required branch is missing/failed/non-deterministic.

### 6. Interruption / resumability

Preserve already-completed branch result metadata when the process is intentionally interrupted or a later branch fails, provided that evidence is still bound to the exact root/fork-set identity.

If resumability is implemented, it must validate the existing durable partial result before reuse and must never merge results from another root/runtime/ROM/source/fork-set identity.

Do not add distributed worker coordination in R0.4.

### 7. Structured JSON + schema

Provide a machine-readable schema/result suitable for later R0.5 branch search.

At minimum include:

- schema version;
- source namespace;
- forkSetId;
- root authority/identity;
- branch specification identities;
- per-branch repetitions/outcomes/status;
- deterministic flag;
- first divergence when known;
- overall status/reason;
- proof scope / real-WOF-proof classification.

Large savestate bytes and raw full RAM histories remain local-only by default; repository results should remain compact metadata/hashes.

### 8. CLI / integration

Provide one obvious CLI for a fork-set run and one ROM-free fake/fixture mode.

Reuse the existing R0.2 adapter/action/determinism authority and R0.3 address-aware RAM plumbing where appropriate. Do not create a parallel emulator stack or duplicate generic contracts unnecessarily.

Document the command and result interpretation in `training/farm/README.md` or an R0.4-specific Farm document.

### 9. Real-runtime authority gate

Repository implementation may be completed without a legal local ROM.

If a matching current-source real R0.2 deterministic proof and legal local Stable-Retro/FBNeo WOF runtime are available, the worker may execute a bounded real R0.4 fork smoke after the module is complete.

If they are unavailable, finish all in-scope implementation first and classify the durable result honestly. Do not fabricate real WOF PASS.

R0.3 semantic mapping is not required to implement the generic fork primitive, but R0.4 must not infer or advertise HP/X/Y/enemy/camera/attack meanings from raw addresses while that semantic gate remains locked.

### 10. No Reward / search policy yet

R0.4 outputs branch outcomes; it does **not** decide which branch is better.

Do not add:

- Reward V0;
- score/fitness semantics claiming gameplay quality;
- best-action selection;
- beam/MCTS/A*/route search;
- PPO/SB3/RL;
- search teacher;
- safe action/path recommendations.

Those belong to later stages after their prerequisites are explicit.

## Testing cadence

Follow `parallel/PM/TESTING_CADENCE_POLICY.md`.

Preferred order:

`implement whole fork module -> integrate schema/CLI/docs/resume boundary -> one compact implementation-owned self-check set -> fix concrete failures -> rerun only affected checks -> durable RESULT/claim closeout`

Do not create Fresh QA, second-opinion, cross-check, or per-helper QA from this stage.

Use enough fake-backend/module-owned checks to prove the fork control flow, authority binding, isolation, deterministic replay, malformed input rejection and partial-result fail-closed behavior. Do not inflate test count merely for confidence.

## Write boundary

Allowed:

- `training/farm/**`;
- `parallel/TRAINING_FARM_R0_4/**`;
- this stage/canonical claim updates required for ownership and closeout.

Forbidden without explicit Owner authority:

- `product/alpha/**`;
- Alpha/Browser release/proof behavior;
- Transport / Recorder / PYLAUNCH / OneClick;
- WinKawaks Collector code/contracts/results;
- Browser/WinKawaks offsets treated as Stable-Retro authority;
- actual R0.3 semantic WOF mappings without live evidence;
- 2/4/8/10-worker orchestration;
- Reward V0 / search policy / PPO/RL / safe route.

Cross-line dependency => fail closed and report it; do not edit another lane to make R0.4 pass.

## Durable result

Before stopping, write:

`parallel/TRAINING_FARM_R0_4/RESULT.md`

It must record:

- exact candidate/source blobs or commit;
- implemented fork/root/branch/isolation/resume surface;
- commands actually run;
- compact self-check result;
- whether real WOF runtime/proof was available;
- real fork smoke result if legitimately run;
- remaining Owner action if any;
- precise next legitimate Training Farm gate.

Close canonical/stage claims only while the exact `claimToken` still matches.

## Stop discipline

**Do not stop after analysis, the root-state helper, branch parser, one working branch, CLI wiring, schema creation, or the first passing test. Continue until the entire R0.4 fork primitive is implemented, integrated, self-checked, documented, durable RESULT is written, and claims are closed, unless a genuine external blocker makes further in-scope repository work impossible.**

Keep progress reporting minimal. Prefer implementation over narration.

Allowed final states only:

`COMPLETE — TRAINING FARM R0.4 DETERMINISTIC SAVESTATE FORK PRIMITIVE — REAL WOF FORK SMOKE PASS`

or, when repository implementation is complete but real runtime authority is unavailable:

`COMPLETE — TRAINING FARM R0.4 DETERMINISTIC SAVESTATE FORK PRIMITIVE IMPLEMENTED — REAL WOF FORK PROOF PENDING`

or:

`BLOCKED — TRAINING FARM R0.4 DETERMINISTIC SAVESTATE FORK PRIMITIVE — <exact concrete blocker>`

# WOF Training Farm R0.4 — Deterministic Savestate Fork Primitive Recovery V2

stageId: `TRAINING_FARM_R0_4_DETERMINISTIC_SAVESTATE_FORK_PRIMITIVE_RECOVERY_V2`
dedupProtocol: `v2`
dedupKey: `training.farm.r0.4.deterministic-savestate-fork-primitive-recovery-v2`
dedupMode: `exclusive`

Priority: **Training Farm current highest-priority implementation recovery**

## Recovery authority

This is PM-authorized recovery for the unfinished historical R0.4 stage:

- historical canonical key: `training.farm.r0.4.deterministic-savestate-fork-primitive`;
- historical stage: `TRAINING_FARM_R0_4_DETERMINISTIC_SAVESTATE_FORK_PRIMITIVE_V1`;
- historical canonical/stage claims remain `ACTIVE` and must be preserved as history;
- do not overwrite, delete, rename, reuse, or steal the historical claim/token.

The previous worker already landed substantial R0.4 implementation through current `training/farm/**`, including strict fork contracts, isolated branch execution, resumable runner, CLI, source binding, schemas, fixture/self-check coverage and documentation. There is no durable `parallel/TRAINING_FARM_R0_4/RESULT.md` yet and the historical claim is not closed.

Resume from current `main`. Do not restart R0.4 from scratch.

## Start / canonical dedup v2

Before substantive work, re-read:

- current `main`;
- `parallel/PM/STAGE_DEDUP_GUARD.md`;
- `parallel/PM/TESTING_CADENCE_POLICY.md`;
- `parallel/PM/WORKER_HANDOFF_FORMAT_POLICY.md`;
- `RUNTIME_DATA_SOURCE_BOUNDARIES.md`;
- `parallel/PM/TRAINING_FARM_R0_4_DETERMINISTIC_SAVESTATE_FORK_PRIMITIVE_START_PROMPT.md`;
- historical R0.4 canonical/stage claims;
- current `training/farm/**`;
- recent R0.4 commits, especially the already-landed fork implementation/schema/CLI/test/docs sequence.

If a newer successor already completed this exact recovery objective, stop `ALREADY COMPLETE — SAFE TO CLOSE`.

Otherwise first mutation must be create-only canonical claim:

`parallel/PM/DEDUP_CLAIMS/training.farm.r0.4.deterministic-savestate-fork-primitive-recovery-v2.json`

Use a fresh unpredictable `claimToken`, re-read current `main` and the exact canonical claim, verify ownership, then create:

`parallel/PM/STAGE_CLAIMS/TRAINING_FARM_R0_4_DETERMINISTIC_SAVESTATE_FORK_PRIMITIVE_RECOVERY_V2.json`

The recovery records must explicitly name the superseded historical canonical/stage claims. Any ownership ambiguity => `ALREADY CLAIMED — SAFE TO CLOSE`.

## Objective

Finish the **same R0.4 module end-to-end** from the current HEAD. Preserve all valid existing work and only fill actual gaps.

The completed module must still satisfy the original R0.4 contract:

`one authoritative root savestate -> N explicit action branches -> isolated deterministic branch outcomes`

Required finished surface:

1. strict immutable root savestate/runtime/ROM/source/layout authority;
2. canonical branch IDs/action sequences/horizons and strict input validation;
3. root restore before every branch and no cross-branch input/RAM/state leakage;
4. deterministic repeated branch replay with bounded checkpoints/divergence diagnostics;
5. fail-closed handling for drift, malformed identities/results, missing/duplicate/partial branches;
6. partial-result preservation/resume bound to the exact root/fork-set identity;
7. structured JSON + schema with proof scope and real-WOF classification;
8. obvious CLI + ROM-free fixture mode;
9. integration with existing R0.2/R0.3 adapter/identity/address-aware plumbing without a second emulator stack;
10. documentation and durable RESULT/claim closeout.

Do not add Reward V0, best-branch selection, beam/MCTS/A*/route search, PPO/SB3/RL, search teacher, safe path, multi-worker orchestration, or guessed WOF semantic addresses.

## Recovery method

First determine what is already complete in current `training/farm/**` and recent R0.4 commits.

- Do not rewrite working root/branch/fork/resume/schema/CLI/test/docs just to make a recovery diff.
- If the current source already satisfies an original requirement, retain it.
- If a concrete implementation/integration gap exists, fix that gap in this recovery.
- If current source drift after the historical worker invalidated an R0.4 assumption, repair only the affected R0.4 surface.
- Do not touch Alpha V1 or WinKawaks Collector to make R0.4 pass.

## Testing cadence

Follow `parallel/PM/TESTING_CADENCE_POLICY.md` strictly.

The previous worker already added module-owned self-checks. Do not start a Fresh QA, second opinion or cross-check.

Preferred recovery flow:

`reconcile current R0.4 implementation -> finish any actual missing integration -> run one compact module-level implementation self-check -> fix only concrete failures -> durable RESULT -> recovery claim closeout`

Do not repeatedly rerun the same broad suite after every small patch. If source is already coherent, one final compact implementation self-check is sufficient.

## Real WOF gate

R0.4 repository implementation is allowed to complete without legal local ROM/runtime authority.

If a matching current-source real R0.2 proof plus legal Stable-Retro/FBNeo WOF runtime is available, a bounded real fork smoke may be run after repository implementation is complete.

If unavailable, do not fake real proof and do not leave repository work unfinished. Final result may honestly state real WOF fork proof is pending.

R0.3 semantic mapping remains separately gated; R0.4 must not infer HP/X/Y/enemy/camera/attack meanings from raw addresses.

## Write boundary

Allowed:

- `training/farm/**` only where an actual R0.4 gap/fix remains;
- `parallel/TRAINING_FARM_R0_4/**`;
- this recovery canonical/stage claim and closeout metadata.

Forbidden without explicit Owner authority:

- `product/alpha/**`;
- Alpha/Browser release or proof behavior;
- Transport / Recorder / PYLAUNCH / OneClick;
- WinKawaks Collector code/contracts/results;
- Browser/WinKawaks offsets treated as Stable-Retro authority;
- actual semantic WOF address claims without live evidence;
- 2/4/8/10-worker orchestration;
- Reward/search/RL/safe-route implementation.

Cross-line dependency => fail closed and report the exact blocker; do not opportunistically edit another lane.

## Durable RESULT

Before stopping, create or complete:

`parallel/TRAINING_FARM_R0_4/RESULT.md`

Record:

- exact final R0.4 candidate/source commit/blobs;
- which existing work was retained and any recovery fixes made;
- final root/branch/isolation/determinism/resume/schema/CLI surface;
- commands actually run and compact self-check outcome;
- real WOF runtime/proof availability and real smoke result if legitimately run;
- remaining Owner action, if any;
- precise next legitimate Training Farm gate.

Then close only the **recovery** canonical/stage claims with the matching recovery `claimToken`, setting them `COMPLETE` and attaching durable RESULT path/commit. Preserve the historical ACTIVE records unchanged as superseded stale history.

## Stop discipline

**Do not stop after claim, inspection, one patch, CLI check, schema check, or one passing test. Do not hand back work that is still inside R0.4. Continue from current HEAD until the complete R0.4 module is reconciled, any actual gaps are fixed, integration is coherent, one compact implementation self-check is complete, durable RESULT exists, and recovery claims are fully closed. Stop only at COMPLETE or a genuine precise external BLOCKED condition.**

Keep progress reporting minimal. Prefer doing the work over narrating it.

Allowed final states only:

`COMPLETE — TRAINING FARM R0.4 DETERMINISTIC SAVESTATE FORK PRIMITIVE RECOVERY V2 — MODULE + RESULT + CLAIM CLOSEOUT COMPLETE`

or:

`BLOCKED — TRAINING FARM R0.4 DETERMINISTIC SAVESTATE FORK PRIMITIVE RECOVERY V2 — <exact concrete blocker>`

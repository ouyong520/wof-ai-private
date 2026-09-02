# WOF Training Farm R0.4 — Deterministic Savestate Fork Primitive Recovery V2 Result

Date: 2026-09-02
Stage: `TRAINING_FARM_R0_4_DETERMINISTIC_SAVESTATE_FORK_PRIMITIVE_RECOVERY_V2`
Dedup key: `training.farm.r0.4.deterministic-savestate-fork-primitive-recovery-v2`
Status: **MODULE + RECOVERY IMPLEMENTATION COMPLETE — REAL WOF FORK PROOF REMAINS EXTERNAL/OWNER-GATED**

## Verdict

The Training Farm R0.4 deterministic savestate fork primitive is complete on the current repository candidate.

The historical R0.4 worker had already landed the root/branch contract, exact-root isolation execution, repeated deterministic replay, bounded checkpoints/divergence, partial/resume orchestration, CLI, JSON schemas, fixture plan, self-checks, and documentation, but stopped before a durable RESULT and claim closeout.

Recovery V2 preserved all of that work and fixed one concrete remaining authority gap discovered during current-HEAD reconciliation: the resume consumer previously validated execution hashes and selected fields, but did not enforce the complete published result/root/branch/outcome envelope. A malformed durable result could therefore carry extra/unvalidated fields, and the root's run-local `runtimeIdentitySha256` was not independently revalidated before PASS branch reuse. Duplicate non-PASS branch rows were also not independently rejected because duplicate detection was coupled to the reusable-PASS map.

Recovery V2 now makes durable resume evidence fail closed on those cases without changing R0.4 execution semantics or expanding into R0.5.

## Exact recovery implementation candidate

Last R0.4 source/test commit before durable RESULT creation:

`107fc70db53143e95e32e0e9d60fb57aae4d392f`

Current `main` was reconciled through:

`0cf94ab483ec3991a2a491e3ddcdecdb689ea0ef`

Comparison from the historical documented R0.4 candidate `12a2f542d36db85cf2e2ea8576add8da080e0adf` through that current HEAD shows only these R0.4 source/test changes:

- `training/farm/savestate_fork_runner.py`
- `training/farm/tests/test_savestate_fork.py`

All other intervening changes belong to PM metadata or unrelated Alpha/PYLAUNCH/OneClick lanes. There is no competing `training/farm/**` drift after the recovery source commit.

Exact current R0.4 blobs used for reconciliation:

- `training/farm/savestate_fork.py` — `dee25c68054c9a79c8af04a854def3dfc6352fd7`
- `training/farm/savestate_fork_contract.py` — `c9b05f1a7383f56802a9d3983e507915b1bfd810`
- `training/farm/savestate_fork_branch.py` — `db35b377eb3c1f0995b4882c187681ecb4698103`
- `training/farm/savestate_fork_runner.py` — `4a76b3db49dc8c9970765cc435152920abb4549a`
- `training/farm/savestate_fork_plan.schema.json` — `851dea648c09c8a079d0ba6a33f2c36c74a8ebc9`
- `training/farm/savestate_fork_result.schema.json` — `8069e389c6b714de6add708a908b7f9c78d4ea4f`
- `training/farm/savestate_fork_plan.example.json` — `a2ef1c1366ee195a9973a7ca223ead8e508c50c0`
- `training/farm/tests/test_savestate_fork.py` — `f24e4d7c5fa55fa2297f5eec5e410268ca5db645`
- `training/farm/R0_4.md` — `7c0db850087afa2105693c6059d5a7c1af54ff43`
- `training/farm/README.md` — `2866c642987a40c871d41efe527c3f10c7fda6fe`

## Recovery V2 authority hardening

`training/farm/savestate_fork_runner.py` now validates a resume result before reusing any PASS branch with the following additional fail-closed rules:

1. top-level result keys must exactly match the published result envelope;
2. `runId`, status, proof flags, required/attempted/completed counts, resume provenance and proof-scope fields are strict and internally consistent;
3. prior root keys must exactly match the published root envelope;
4. prior root `runtimeIdentity` is revalidated for fixture/real scope;
5. `runtimeIdentitySha256` must recompute exactly from that identity;
6. `stableRuntimeAuthority` must recompute exactly from that identity;
7. root ROM/Farm bindings must match the validated runtime identity;
8. root authority and fork-set authority hashes must remain self-consistent and equal the newly recaptured current root authority;
9. branch specifications must have the exact published shape and exact current execution payload/action/identity authority; human label remains non-execution authority;
10. branch result and outcome objects must have the exact published shape;
11. branch counts/outcome counts and deterministic flags must be strict and consistent;
12. duplicate branch rows are rejected independently of PASS reuse status;
13. only complete deterministic `PASS / BRANCH_DETERMINISTIC` rows with all required repeated outcomes are reusable.

The published JSON schema and CLI did not require a format change; this recovery brings runtime resume validation up to the already-published strict schema/authority contract.

## R0.4 module surface retained

The completed module retains the existing R0.4 contract:

- one immutable savestate root bound to Stable-Retro/FBNeo runtime, ROM, Farm source, R0.4 source, RAM and address-aware memory-layout authority;
- canonical branch IDs, explicit all-player per-frame input masks, exact action sequence hashes and exact frame horizons;
- restore of the exact root before every branch repetition;
- no implicit host-input persistence as branch authority;
- per-branch repeated replay with bounded deterministic RAM checkpoints plus final RAM/block/savestate hashes;
- first-divergence reporting and branch-level failure without converting incomplete/failing work to PASS;
- durable partial preservation and exact-authority resume;
- structured `PASS / PARTIAL / FAIL / ERROR / SKIP` JSON;
- explicit `IMPLEMENTATION_FIXTURE` versus `REAL_WOF_FORK` proof scope;
- real fork execution gated by a matching current-source real R0.2 determinism proof;
- obvious CLI and ROM-free fixture mode;
- reuse of the existing R0.1/R0.2/R0.3 adapter/runtime stack, not a second emulator stack.

No Reward, search policy, semantic WOF address guessing, PPO/SB3/RL, multi-worker orchestration, safe-route logic, Browser authority, WinKawaks authority, or Alpha release behavior was added.

## Compact implementation self-check

Recovery V2 performed one compact ROM-free implementation self-check after the authority patch.

Because the connected GitHub interface in this worker does not expose a mounted checkout or arbitrary GitHub Actions command runner, the executable check used an isolated local fixture reconstruction of the re-read current R0.4 fork-core logic. The modified runner logic, root/branch fork logic, strict plan/action semantics, adapter/fake-backend behavior and runtime identity semantics were exercised; Stable-Retro real-runtime and R0.3 real-proof consumer paths were intentionally stubbed because no real-WOF authority was being claimed. This check is implementation evidence only, not Fresh QA and not real-WOF proof.

Observed checks: **14/14 PASS**:

1. complete two-branch fixture fork -> `PASS / FORK_SET_DETERMINISTIC`;
2. execution-limited fork -> `PARTIAL / EXECUTION_LIMIT_REACHED`;
3. matching partial -> resumed PASS with only the completed branch reused;
4. extra top-level result field -> `ERROR / INVALID_RESUME_RESULT`;
5. tampered root `runtimeIdentitySha256` -> `ERROR / INVALID_RESUME_RESULT`;
6. duplicate non-PASS branch rows -> `ERROR / INVALID_RESUME_RESULT`;
7. tampered branch action-sequence SHA -> `ERROR / INVALID_RESUME_RESULT`;
8. plan authority remains branch-order independent;
9. duplicate plan branch ID rejected;
10. coercible/string horizon rejected;
11. standalone neutral branch matches the same branch in a multi-branch set, while action branches diverge as expected, confirming cross-branch isolation;
12. deliberately diverging backend -> deterministic branch failure with first RAM checkpoint divergence at frame 1;
13. runtime/core identity drift during execution cannot PASS;
14. 1000-frame branch checkpoint set remains bounded to <=64 and includes the exact final frame.

The reconstructed fixture package also passed Python bytecode compilation for the exercised Training Farm modules.

The current GitHub blobs for the modified runner and regression file were then re-read after the commits to confirm the durable source contains the recovery validation and regressions.

## Real WOF authority

Recovery V2 does **not** claim a real-WOF fork PASS.

A real R0.4 `REAL_WOF_FORK` proof remains gated by the existing R0.2 authority contract: a legal local WOF ROM, pinned Stable-Retro/FBNeo runtime, and matching current-source R0.2 real determinism PASS must exist before a real fork run can be authoritative.

No legal local WOF ROM or matching current-source real R0.2 proof was available to this worker. Fixture PASS therefore remains `realWofProof=false` and cannot unlock semantic mapping, multi-worker training, or later search/RL stages.

This is an external Owner/runtime prerequisite, not an unfinished R0.4 repository implementation item.

## Historical claim preservation and Recovery V2 authority

Historical ownership records are deliberately preserved unchanged as stale `ACTIVE` history:

- `parallel/PM/DEDUP_CLAIMS/training.farm.r0.4.deterministic-savestate-fork-primitive.json`
- `parallel/PM/STAGE_CLAIMS/TRAINING_FARM_R0_4_DETERMINISTIC_SAVESTATE_FORK_PRIMITIVE_V1.json`

Recovery V2 owns only:

- canonical: `parallel/PM/DEDUP_CLAIMS/training.farm.r0.4.deterministic-savestate-fork-primitive-recovery-v2.json`
- stage: `parallel/PM/STAGE_CLAIMS/TRAINING_FARM_R0_4_DETERMINISTIC_SAVESTATE_FORK_PRIMITIVE_RECOVERY_V2.json`
- claim token: `fd407f1104aa298a253e8d88c63686f6571d985a308384c2`

Only those Recovery V2 records are to be closed by this result.

## Precise next legitimate Training Farm gate

Repository implementation must not jump directly to R0.5 from fixture evidence alone.

The existing authority path remains:

**Owner current-source R0.2 real-WOF determinism PASS -> authoritative real R0.4 fork run when needed by the next explicitly authorized Training Farm stage.**

This Recovery V2 task itself is repository-complete.

## Stop condition

**COMPLETE — TRAINING FARM R0.4 DETERMINISTIC SAVESTATE FORK PRIMITIVE RECOVERY V2 — MODULE + RESULT + CLAIM CLOSEOUT COMPLETE**

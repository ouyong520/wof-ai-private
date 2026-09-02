# WOF Training Farm R0.2 — Single-Instance Determinism Module

stageId: `TRAINING_FARM_R0_2_SINGLE_INSTANCE_DETERMINISM_V1`
dedupProtocol: `v2`
dedupKey: `training.farm.r0.2.single-instance-determinism`
dedupMode: `exclusive`

Priority: **Training Farm current highest-priority implementation module**

## Goal

Build the complete R0.2 single-instance determinism module on top of R0.1. The module must make one Stable-Retro + FBNeo WOF instance able to prove or fail-closed on:

`same savestate + same action sequence + same frame horizon -> same observable result`

Do not start multi-worker, observation-address calibration, PPO/RL, route search, or dataset expansion yet.

## Start / ownership

Before substantive work, re-read current `main`, `parallel/PM/STAGE_DEDUP_GUARD.md`, `parallel/PM/TESTING_CADENCE_POLICY.md`, `RUNTIME_DATA_SOURCE_BOUNDARIES.md`, `training/farm/README.md`, `parallel/TRAINING_FARM_R0_1/RESULT.md`, current `training/farm/**`, recent Training Farm commits, and current Training Farm claims.

If equivalent R0.2 work is already COMPLETE, stop `ALREADY COMPLETE — SAFE TO CLOSE`.

Otherwise the first mutation must be the canonical create-only claim:

`parallel/PM/DEDUP_CLAIMS/training.farm.r0.2.single-instance-determinism.json`

Use a fresh unpredictable `claimToken`, re-read current `main` and the canonical claim, verify the token/metadata exactly, then create:

`parallel/PM/STAGE_CLAIMS/TRAINING_FARM_R0_2_SINGLE_INSTANCE_DETERMINISM_V1.json`

Any ownership ambiguity => `ALREADY CLAIMED — SAFE TO CLOSE`.

## Complete module requirements

Finish the whole coherent module before stopping.

Implement under `training/farm/**`:

1. **Runtime identity**
   - source namespace must be `stable-retro-fbneo`;
   - record pinned/observed Stable-Retro version;
   - record OS/Python/runtime information needed to distinguish runs;
   - record local ROM SHA-256 without copying/uploading ROM bytes;
   - record Farm source/candidate identity sufficient to distinguish changed implementation;
   - include backend/core identity when the runtime exposes it reliably;
   - identity fields used for determinism comparison must be strict and non-coercive.

2. **Deterministic replay primitive**
   - save one starting savestate;
   - accept a deterministic explicit action sequence and frame horizon;
   - restore the exact same starting state before every repetition;
   - execute the same sequence for multiple repetitions;
   - capture at minimum starting-state hash, final RAM hash, and enough per-step/checkpoint hashes to locate divergence;
   - compare repetitions exactly;
   - success only when all required observable outputs match.

3. **Action/horizon contract**
   - use emulator/core API only;
   - no OS/global keyboard, SendInput, focus automation, Browser input, or WinKawaks input;
   - reject malformed/coercible player/button/horizon/repeat values fail-closed;
   - make neutral input explicit rather than implicit host timing behavior;
   - no wall-clock timing as authority for frame progression.

4. **Identity binding / fail-closed behavior**
   - a replay result is valid only for one runtime/ROM/source identity;
   - runtime/core/ROM/source identity change must invalidate comparison rather than merge results;
   - malformed/partial identity must not produce a PASS;
   - savestate hash mismatch, load failure, RAM-read failure, action failure, frame-count mismatch, or missing repetition must not produce a PASS.

5. **Diagnostics/report**
   - emit structured JSON suitable for durable later automation;
   - include repetition count, horizon, action-sequence identity/hash, runtime identity, start-state hash, final/checkpoint hashes, PASS/FAIL/SKIP/ERROR state, and exact first divergence when known;
   - do not serialize ROM bytes or copyrighted game data into repository artifacts;
   - distinguish `runtime prerequisite unavailable` from `determinism mismatch`.

6. **CLI/integration**
   - provide one obvious single-instance command for the determinism run;
   - reuse R0.1 adapter/backend instead of building a second emulator stack;
   - keep existing R0.1 probe compatibility unless a small compatible refactor is required for this module;
   - document the command and interpretation in `training/farm/README.md` or an R0.2-specific Farm doc.

7. **ROM-free implementation coverage**
   - extend the fake/deterministic backend or a narrow module-owned fixture only as needed to exercise the complete replay/identity/fail-closed control flow;
   - fake PASS is implementation evidence only and must never be labeled real-WOF determinism proof.

## Real WOF handling

If the execution environment has pinned Stable-Retro plus a legal local external WOF ROM, run the real single-instance determinism command after implementation is complete and record the exact result.

If the environment lacks the ROM/dependency, **do not stop early**. Finish the entire repository implementation, documentation, result schema, failure paths, and module-owned self-check first. Only after the module is complete may the durable RESULT state that local real-WOF proof is still Owner action.

Missing legal ROM by itself is not permission to fake real-WOF PASS and is not a reason to leave the implementation half-finished.

## Testing cadence

Follow `parallel/PM/TESTING_CADENCE_POLICY.md` strictly.

Preferred order:

`implement whole R0.2 module -> wire integration/docs/result -> run one compact implementation-owned self-check set -> fix concrete failures -> rerun only affected checks -> stop`

Do not create Fresh QA, second opinion, cross-check, recovery, or per-subfeature test stages from this task.

Do not spend time multiplying test cases after the module already has enough narrow coverage to establish the implementation contract. Independent QA, if PM later wants one, is a separate module-boundary decision.

## Write boundary

Allowed:

- `training/farm/**`;
- `parallel/TRAINING_FARM_R0_2/**`;
- this stage/canonical claim updates required for ownership/closeout.

Forbidden without explicit Owner authority:

- `product/alpha/**`;
- Alpha/Browser release gates or proof tooling;
- Transport / Recorder / PYLAUNCH / OneClick;
- WinKawaks Collector repositories/contracts;
- copying Browser/WinKawaks numeric offsets into Farm as if authoritative;
- multi-worker 2/4/8/10 orchestration;
- PPO/SB3/RL/search-teacher/safe-route implementation.

Cross-line dependency discovered => fail closed and report it; do not opportunistically edit the other lane.

## Durable result

Before stopping, write:

`parallel/TRAINING_FARM_R0_2/RESULT.md`

It must state exact current source blobs/commit, implemented surface, commands actually run, compact self-check outcome, whether real WOF runtime was available, real runtime result if run, remaining Owner action if any, and the precise next legitimate Farm gate.

Close canonical/stage claims only with matching `claimToken` and current blob SHA.

## Stop discipline

**Do not stop after analysis, partial implementation, one helper, one CLI, documentation, or the first passing test. Do not hand back a TODO list for work that is inside this module. Continue until the entire R0.2 module above is implemented, integrated, self-checked, documented, RESULT is durable, and claims are closed or a genuine external blocker makes further in-scope work impossible.**

Keep progress reporting minimal. Prefer doing the work over narrating it.

Allowed final states only:

`COMPLETE — TRAINING FARM R0.2 SINGLE-INSTANCE DETERMINISM MODULE — REAL WOF PROOF PASS`

or, when repository implementation is fully complete but the legal local runtime is unavailable:

`COMPLETE — TRAINING FARM R0.2 SINGLE-INSTANCE DETERMINISM MODULE IMPLEMENTED — OWNER LOCAL REAL-WOF PROOF REQUIRED`

or:

`BLOCKED — TRAINING FARM R0.2 SINGLE-INSTANCE DETERMINISM MODULE — <exact concrete blocker>`

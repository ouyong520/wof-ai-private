# WOF Training Farm R0.3 — Observation Discovery Tooling Prep Closeout Recovery V2

stageId: `TRAINING_FARM_R0_3_OBSERVATION_DISCOVERY_TOOLING_PREP_CLOSEOUT_RECOVERY_V2`
dedupProtocol: `v2`
dedupKey: `training.farm.r0.3.observation-discovery-tooling-prep-closeout-recovery-v2`
dedupMode: `exclusive`

Priority: **Training Farm current highest-priority recovery / closeout**

Superseded historical canonical claim:

`parallel/PM/DEDUP_CLAIMS/training.farm.r0.3.observation-discovery-tooling-prep.json`

Historical stage claim:

`parallel/PM/STAGE_CLAIMS/TRAINING_FARM_R0_3_OBSERVATION_DISCOVERY_TOOLING_PREP_V1.json`

Both historical claims are currently `ACTIVE` even though the implementation RESULT is already durable. This is a PM-authorized recovery. Do not overwrite, delete, rename, reuse, or steal the historical claim/token.

## Goal

Finish only the missing durable closeout for the already-implemented R0.3 observation-discovery tooling prep module. Verify the current exact Training Farm candidate still matches the durable implementation RESULT or classify any real drift precisely. If the candidate remains valid, publish a successor recovery RESULT and close this recovery claim/stage as COMPLETE so PM can safely move to the next Training Farm module without treating the historical ACTIVE record as live ownership.

Do not redo the R0.3 module, do not add features, do not start semantic WOF address mapping, and do not open independent QA.

## Start / recovery ownership

Before substantive work, re-read current `main`, `parallel/PM/STAGE_DEDUP_GUARD.md`, `parallel/PM/TESTING_CADENCE_POLICY.md`, `parallel/PM/WORKER_HANDOFF_FORMAT_POLICY.md`, `RUNTIME_DATA_SOURCE_BOUNDARIES.md`, the historical R0.3 canonical/stage claims, and:

`parallel/TRAINING_FARM_R0_3_OBSERVATION_DISCOVERY_TOOLING_PREP/RESULT.md`

Also inspect current `training/farm/**` only as needed to verify whether the RESULT candidate has drifted.

If an equivalent successor recovery is already COMPLETE, stop `ALREADY COMPLETE — SAFE TO CLOSE`.

Otherwise first mutation must be the create-only canonical recovery claim:

`parallel/PM/DEDUP_CLAIMS/training.farm.r0.3.observation-discovery-tooling-prep-closeout-recovery-v2.json`

Use a fresh unpredictable `claimToken`, re-read current `main` and the new recovery claim, verify exact ownership, then create:

`parallel/PM/STAGE_CLAIMS/TRAINING_FARM_R0_3_OBSERVATION_DISCOVERY_TOOLING_PREP_CLOSEOUT_RECOVERY_V2.json`

Any ownership ambiguity => `ALREADY CLAIMED — SAFE TO CLOSE`.

## Recovery work

1. Confirm the durable R0.3 RESULT exists and records the coherent module candidate, implemented surface, compact self-check evidence, real-runtime limitation, and next gate.
2. Compare current `training/farm/**` with the candidate/evidence recorded in that RESULT.
3. If no material Training Farm source drift affects R0.3, do **not** rerun the whole historical test matrix. A minimal syntax/hash or directly affected compact self-check is enough when needed to establish current-candidate compatibility.
4. If there is later `training/farm/**` drift, classify whether it changes R0.3 behavior/authority. Rerun only the affected compact module-owned checks needed to rebind the successor result.
5. Do not modify implementation merely to produce a recovery PASS. A real implementation defect => `BLOCKED` with the smallest precise defect.
6. Preserve the existing authority boundary: no real WOF semantic address claim is unlocked without a matching current-source real R0.2 `PASS / DETERMINISM_MATCH` with `realWofProof=true`.
7. Preserve the historical ACTIVE canonical/stage claim files unchanged. They are historical stale records superseded only by this explicit PM recovery result; this worker does not own their old `claimToken`.

## Durable successor result

Write:

`parallel/TRAINING_FARM_R0_3_OBSERVATION_DISCOVERY_TOOLING_PREP_CLOSEOUT_RECOVERY_V2/RESULT.md`

It must state:

- current `main` checked;
- historical R0.3 RESULT path and candidate identity;
- whether current `training/farm/**` materially drifted;
- exact checks actually run, if any;
- whether the prior module verdict remains valid;
- historical ACTIVE claim/stage are preserved and explicitly superseded by this PM-authorized recovery generation;
- real semantic mapping remains locked until current-source R0.2 real-WOF proof;
- precise next legitimate Training Farm module/gate.

Close only this recovery canonical/stage claim using this recovery worker's matching token/current blob SHA.

## Testing cadence

This is closeout recovery, not a new QA generation. Do not repeat 19/19 plus every prior CLI merely for confidence. Run only the minimum current-candidate checks needed if source drift requires them. Do not create Fresh QA, cross-check, second opinion, or another recovery from this task.

## Write boundary

Allowed:

- `parallel/TRAINING_FARM_R0_3_OBSERVATION_DISCOVERY_TOOLING_PREP_CLOSEOUT_RECOVERY_V2/**`;
- this recovery canonical/stage claim updates.

Do not modify:

- historical R0.3 canonical/stage claims;
- `training/farm/**` unless a concrete current-source defect is discovered and the prompt cannot legally close without a separate PM implementation authorization — in that case BLOCKED rather than opportunistically patching;
- `product/alpha/**`;
- WinKawaks Collector;
- Transport / Recorder / PYLAUNCH / OneClick.

## Stop discipline

Do not stop after merely observing that the old claim is ACTIVE. Finish the recovery ownership, current-candidate reconciliation, durable successor RESULT, and this recovery claim/stage closeout before stopping, unless a genuine concrete blocker prevents that.

Keep reporting minimal. Prefer completing the recovery over narrating it.

Allowed final states only:

`COMPLETE — TRAINING FARM R0.3 OBSERVATION DISCOVERY TOOLING PREP CLOSEOUT RECOVERY V2 — SUCCESSOR AUTHORITY DURABLE`

or:

`BLOCKED — TRAINING FARM R0.3 OBSERVATION DISCOVERY TOOLING PREP CLOSEOUT RECOVERY V2 — <exact concrete blocker>`

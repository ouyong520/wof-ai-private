# Training Farm R0.4.7 Windows Portable Real-WOF Proof Bundle V1 — Closeout Recovery V3

stageId: `TRAINING_FARM_R0_4_7_WINDOWS_PORTABLE_REAL_WOF_PROOF_BUNDLE_V1_CLOSEOUT_RECOVERY_V3`

dedupProtocol: `v2`

dedupKey: `training.farm.r0.4.7.windows-portable-real-wof-proof-bundle-v1.closeout-recovery-v3`

dedupMode: `exclusive`

Priority: **P0 narrow successor authority correction / closeout reconciliation**

## PM authorization

This is a PM-authorized **closeout authority correction only** for Training Farm R0.4.7.

Do not redo implementation, rebuild/republish the portable ZIP, rerun historical PASS QA without a concrete source drift reason, execute Browser/WOF, ask the Owner to retest, create R0.4.8, or enter R0.5.

The original R0.4.7 implementation/package authority remains the frozen candidate/artifact/result chain below. Closeout Recovery V2 reached `COMPLETE` claims, but its successor RESULT contains artifact identity statements that conflict with the original durable R0.4.7 RESULT and current Git objects, and its COMPLETE claim files omit closeout metadata required by its own prompt. Therefore V2 must remain immutable historical evidence and be superseded by a fresh V3 authority; do not edit V2 in place.

## Mandatory duplicate preflight

Before mutation, re-read current `main` and inspect:

- this exact START_PROMPT;
- `parallel/PM/STAGE_DEDUP_GUARD.md`;
- `parallel/PM/TESTING_CADENCE_POLICY.md`;
- original R0.4.7 durable RESULT:
  - `parallel/TRAINING_FARM_R0_4_7_WINDOWS_PORTABLE_REAL_WOF_PROOF_BUNDLE_V1/RESULT.md`;
- original R0.4.7 canonical/stage claims;
- Closeout Recovery V2 START_PROMPT, RESULT, canonical claim and stage claim;
- any equivalent/newer V3 recovery authority;
- current Training Farm source/package drift.

If this exact V3 generation is already ACTIVE/COMPLETE, or superseded by a newer valid recovery, stop with canonical duplicate authority and do no work.

If not duplicate, acquire a fresh canonical dedup-v2 claim and matching stage claim for this V3 key before substantive reconciliation. Never reuse or overwrite original R0.4.7 or V2 claim tokens.

## Frozen R0.4.7 authority

Reconcile against the actual durable original authority, not against the inconsistent V2 RESULT fields:

- implementation/source candidate: `ba1fc43c2ea2a5f04909a1b3dca88b69845d62c8`;
- immutable artifact commit: `985015de1779186906af2b570764c975d94015f3`;
- original durable RESULT commit: `a85c3d509e931e48ddccb6bcf45ff5c4189c6b2f`;
- original durable RESULT path:
  - `parallel/TRAINING_FARM_R0_4_7_WINDOWS_PORTABLE_REAL_WOF_PROOF_BUNDLE_V1/RESULT.md`;
- ZIP path:
  - `training/farm/dist/WOF_Training_Farm_R0_4_7_Portable_Proof_ba1fc43c.zip`;
- ZIP Git blob recorded by original RESULT: `864f858901e770aa46208e1d00bab0d5eb65a963`;
- ZIP SHA256 recorded by original RESULT/current sidecar: `4e51fe3300237a6142b88acdd25436ee82512a5719ea527c5f26c3d9ba55ddd5`;
- ZIP size: `261003` bytes;
- sidecar path:
  - `training/farm/dist/WOF_Training_Farm_R0_4_7_Portable_Proof_ba1fc43c.manifest.json`;
- sidecar Git blob recorded by original RESULT/current Git: `7999e2fc10ae3744253a5951f47fdf4ec273a54a`;
- sidecar SHA256 recorded by original RESULT: `cfd21b35845dd7ee25f020140cc1f58f654e00e91f1b2911267a398f1c981aab`;
- sidecar size: `718` bytes;
- inner manifest SHA256: `82a7733c186fdc120766a09485f76afc6d1b9b3e6a6120d98296fbe8b6ed0350`;
- payload aggregate SHA256: `44f111ea9237309ba8c24cd2351d94818d24a34cefc7246c8f02d1ca6840910c`;
- publisher workflow run: `33662983175`, historically successful.

These values are inputs to verify against current Git objects. Do not blindly copy them if current Git proves a material mismatch; fail closed instead.

## Confirmed V2 authority defect to reconcile

At PM V3 authorization, Closeout Recovery V2 RESULT currently states artifact values including:

- ZIP SHA256 `7af95b01401d3d3be059de9223397bba39cdbf16080b5d4a516be77d34c8b511`;
- manifest SHA256 `b8b464f2f84dd53672dbdc06d32a0c4d5599d254797265b76e08f14fe1a83100`;
- manifest/current Git blob `b45fc7f1a60fdf73bf78135a7e3f06cc4c93ca80`;
- manifest fields such as `sourceCommit`, `archiveFile`, `archiveSha256`, `truthLabel`, and `realWofExecuted`.

Those statements conflict with the current original R0.4.7 durable RESULT and current sidecar object, which currently exposes Git blob `7999e2fc10ae3744253a5951f47fdf4ec273a54a` and `zipSha256=4e51fe3300237a6142b88acdd25436ee82512a5719ea527c5f26c3d9ba55ddd5`.

Also, the V2 fresh canonical/stage claims currently show `state=COMPLETE` but omit the V2 prompt-required exact closeout fields such as `sourceCandidate`, `resultPath`, and `resultCommit`.

Do not edit those V2 records. V3 must explicitly document that V2 is superseded for final closeout authority because its RESULT/claim metadata is internally inconsistent with the durable original artifact authority.

## Narrow execution scope

### 1. Current-main and drift reconciliation

After acquiring V3 claims, re-read current `main`.

Compare current Training Farm proof/package source from the frozen source candidate/artifact commit to current main. Classify changes and determine whether any strict R0.2/R0.4 proof runtime, R0.4.6 bootstrap, R0.4.7 builder/verifier/source closure or immutable artifact has materially drifted.

Expected PM/RESULT/claim/workflow/unrelated Alpha/Collector changes are not material by themselves.

If a material runtime/package drift exists, do not bless the old package. Stop `BLOCKED` with exact changed file/blob and reason.

### 2. Artifact identity reconciliation

Verify using current Git/object evidence:

- original RESULT exists and retains the frozen candidate/artifact authority;
- ZIP exists at the recorded path with the expected Git blob identity;
- sidecar exists and its current Git blob/content matches the original RESULT authority;
- sidecar binds the expected source candidate, ZIP name/hash/size, inner manifest hash/size and payload aggregate hash;
- immutable artifact commit remains in history and no later commit materially replaced the intended R0.4.7 package authority.

Do not access ROM bytes. Do not rebuild merely to create activity.

If the current Git object truth differs materially from the original durable RESULT, stop `BLOCKED` instead of inventing a reconciliation.

### 3. Preserve all historical generations

Do not modify in place:

- original R0.4.7 canonical/stage claims;
- Closeout Recovery V2 canonical/stage claims;
- Closeout Recovery V2 RESULT.

V3 is the successor correction authority and must supersede V2 only by explicit durable successor statement.

### 4. Real-proof gate check

Search current repository authority for genuine current-authority-valid:

- R0.2 `REAL_WOF` PASS / `DETERMINISM_MATCH`, `proofScope=REAL_WOF`, `realWofProof=true`;
- R0.4 `REAL_WOF_FORK` PASS / `FORK_SET_DETERMINISTIC`, `proofScope=REAL_WOF_FORK`, `realWofProof=true`.

Do not count launchers, package checks, fixtures, synthetic/self-checks, expected strings, or Owner instructions as proof.

If both do not exist, V3 RESULT must record `realWofProof=false` and `r0_5Authorized=false`; exact next action remains Owner-local execution of the existing immutable R0.4.7 package.

Even if genuine proof appears concurrently, this recovery itself does not enter R0.5. Record it and stop after closeout for PM reconciliation.

## Required V3 durable RESULT

Write:

`parallel/TRAINING_FARM_R0_4_7_WINDOWS_PORTABLE_REAL_WOF_PROOF_BUNDLE_V1_CLOSEOUT_RECOVERY_V3/RESULT.md`

Include at minimum:

- current main inspected;
- V3 canonical/stage paths and exact fresh claim token;
- frozen source candidate `ba1fc43c2ea2a5f04909a1b3dca88b69845d62c8`;
- immutable artifact commit `985015de1779186906af2b570764c975d94015f3`;
- original RESULT path/commit;
- current-main drift classification;
- exact verified ZIP path/blob/SHA256/size;
- exact verified sidecar path/blob/SHA256/size;
- exact verified inner manifest and payload aggregate hashes;
- explicit description of the V2 artifact/claim metadata inconsistency;
- explicit statement that original and V2 historical files were not modified;
- explicit statement that V3 supersedes V2 for final R0.4.7 closeout authority;
- `containsRomBytes=false`;
- `realWofProof=false` unless genuine current repository proof is found;
- `r0_5Authorized=false` unless separately PM-authorized after proof validation; V3 itself never authorizes R0.5;
- exact Owner next action if real proof is absent;
- final verdict.

## Claim closeout requirements

After V3 RESULT is durable:

1. token-verify V3 canonical claim;
2. update only V3 canonical claim to `COMPLETE` and include all of:
   - `sourceCandidate` = exact V3 reconciliation candidate/current authority commit used for closeout;
   - `resultPath` = exact V3 RESULT path;
   - `resultCommit` = exact commit making V3 RESULT durable;
3. token-verify V3 stage claim;
4. update only V3 stage claim to `COMPLETE` with the same `sourceCandidate`, `resultPath`, and `resultCommit`;
5. re-read current main, V3 RESULT, V3 canonical claim and V3 stage claim;
6. verify both V3 claims are `COMPLETE`, token-consistent, and include non-null closeout metadata;
7. verify original R0.4.7 and V2 historical records remain unchanged.

Do not stop after RESULT, after only one COMPLETE claim, or with missing `sourceCandidate/resultPath/resultCommit` metadata.

## Final stop condition

Only one of:

`COMPLETE — TRAINING FARM R0.4.7 WINDOWS PORTABLE REAL-WOF PROOF BUNDLE V1 CLOSEOUT RECOVERY V3 — CORRECT SUCCESSOR CLOSEOUT AUTHORITY DURABLE; REAL R0.2/R0.4 PROOF STILL REQUIRED`

or if real proof appeared concurrently:

`COMPLETE — TRAINING FARM R0.4.7 WINDOWS PORTABLE REAL-WOF PROOF BUNDLE V1 CLOSEOUT RECOVERY V3 — CORRECT SUCCESSOR CLOSEOUT AUTHORITY DURABLE; REAL PROOF REQUIRES PM RECONCILIATION BEFORE NEXT STAGE`

or precise irreducible:

`BLOCKED — <exact material drift / artifact identity / authority defect>`

or canonical duplicate stop.

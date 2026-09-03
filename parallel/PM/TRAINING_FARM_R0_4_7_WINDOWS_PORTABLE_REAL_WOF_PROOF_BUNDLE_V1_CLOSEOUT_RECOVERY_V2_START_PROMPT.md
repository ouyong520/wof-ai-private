# Training Farm R0.4.7 Windows Portable Real-WOF Proof Bundle V1 — Closeout Recovery V2

stageId: `TRAINING_FARM_R0_4_7_WINDOWS_PORTABLE_REAL_WOF_PROOF_BUNDLE_V1_CLOSEOUT_RECOVERY_V2`

dedupProtocol: `v2`

dedupKey: `training.farm.r0.4.7.windows-portable-real-wof-proof-bundle-v1.closeout-recovery-v2`

dedupMode: `exclusive`

Priority: **P0 narrow authority closeout reconciliation**

## PM authorization

This is a PM-authorized **closeout recovery only** for Training Farm R0.4.7.

The original R0.4.7 implementation, deterministic portable package, immutable ZIP publication, ROM-free verification workflow and durable RESULT already exist. The original canonical/stage claims remain historical `STARTED`, so they must not be stolen, rewritten or retroactively converted to COMPLETE.

This recovery exists only to establish a fresh successor dedup-v2 authority that reconciles the already-complete R0.4.7 implementation and records a durable COMPLETE closeout.

Do **not** redo implementation, rebuild the package merely to create activity, rerun historical PASS checks without a concrete drift reason, run Browser/WOF, ask the Owner to test, or enter R0.5.

## Mandatory duplicate preflight

Before any mutation, re-read current `main` and inspect:

- this exact START_PROMPT;
- `parallel/PM/STAGE_DEDUP_GUARD.md`;
- `parallel/PM/TESTING_CADENCE_POLICY.md`;
- original R0.4.7 durable RESULT:
  - `parallel/TRAINING_FARM_R0_4_7_WINDOWS_PORTABLE_REAL_WOF_PROOF_BUNDLE_V1/RESULT.md`;
- original historical canonical claim:
  - `parallel/PM/DEDUP_CLAIMS/training.farm.r0.4.7.windows-portable-real-wof-proof-bundle-v1.json`;
- original historical stage claim:
  - `parallel/PM/STAGE_CLAIMS/TRAINING_FARM_R0_4_7_WINDOWS_PORTABLE_REAL_WOF_PROOF_BUNDLE_V1.json`;
- any equivalent/newer R0.4.7 recovery RESULT, canonical claim or stage claim;
- current Training Farm runtime/package source drift since the recorded implementation candidate.

If this exact recovery generation is already legitimately ACTIVE under another worker, COMPLETE, or superseded by a newer recovery, do not execute duplicate work. Stop with the exact current authority:

`DUPLICATE / ALREADY COMPLETE / SUPERSEDED — NO EXECUTION — <authority>`

If not duplicate, acquire a **new** canonical dedup-v2 claim and matching stage claim for this recovery dedup key before substantive closeout work.

Never overwrite or repurpose the original R0.4.7 claim token.

## Frozen completed R0.4.7 authority to reconcile

At PM authorization, current repository evidence records:

- R0.4.7 implementation/source candidate: `ba1fc43c2ea2a5f04909a1b3dca88b69845d62c8`;
- immutable artifact commit: `985015de1779186906af2b570764c975d94015f3`;
- durable RESULT commit/current main immediately before this recovery authorization: `a85c3d509e931e48ddccb6bcf45ff5c4189c6b2f`;
- package path: `training/farm/dist/WOF_Training_Farm_R0_4_7_Portable_Proof_ba1fc43c.zip`;
- sidecar manifest path: `training/farm/dist/WOF_Training_Farm_R0_4_7_Portable_Proof_ba1fc43c.manifest.json`;
- ZIP SHA256 recorded by RESULT: `4e51fe3300237a6142b88acdd25436ee82512a5719ea527c5f26c3d9ba55ddd5`;
- sidecar SHA256 recorded by RESULT: `cfd21b35845dd7ee25f020140cc1f58f654e00e91f1b2911267a398f1c981aab`;
- inner manifest SHA256 recorded by RESULT: `82a7733c186fdc120766a09485f76afc6d1b9b3e6a6120d98296fbe8b6ed0350`;
- payload aggregate SHA256 recorded by RESULT: `44f111ea9237309ba8c24cd2351d94818d24a34cefc7246c8f02d1ca6840910c`;
- publisher workflow run `33662983175` succeeded;
- durable RESULT explicitly records `containsRomBytes=false`, `realWofProof=false`, `r0_5Authorized=false`;
- authoritative R0.2 REAL_WOF PASS was not available;
- authoritative R0.4 REAL_WOF_FORK PASS was not available;
- therefore R0.5 remained locked.

These values are reconciliation inputs, not permission to skip verification against current Git.

## Why recovery is needed

The original durable RESULT is complete, but both original R0.4.7 claim documents still show historical `state=STARTED` and `resultCommit=null`.

That mismatch must not be fixed by mutating the historical generation after the fact.

Instead, this recovery must establish successor authority proving:

1. the completed R0.4.7 implementation/result/package still exist;
2. no material Training Farm proof/package runtime drift invalidates the frozen artifact authority;
3. the original historical STARTED claims are preserved unchanged;
4. this fresh recovery generation supersedes those stale closeout markers for PM scheduling purposes;
5. R0.5 is still locked until real Owner-local R0.2/R0.4 proof exists.

## Narrow execution scope

### 1. Current-main reconciliation

Re-read current `main` after acquiring the recovery claim.

Compare current Training Farm runtime/package source with the frozen R0.4.7 implementation candidate and immutable artifact/result commits.

Classify all changes since `ba1fc43c2ea2a5f04909a1b3dca88b69845d62c8`.

Changes limited to:

- immutable package publication;
- workflow/publisher plumbing;
- RESULT/PM metadata;
- unrelated Alpha/Collector lanes;
- this recovery prompt/claims;

are not material proof-runtime drift by themselves.

If any current change modifies the strict R0.2/R0.4 proof runtime, R0.4.6 bootstrap, R0.4.7 builder/verifier/package closure in a way that makes the recorded immutable package no longer the intended current package authority, do not silently bless the old artifact. Stop with a precise `BLOCKED` describing the exact changed file/blob and why a new implementation/package generation would be required.

### 2. Durable evidence existence check

Verify the original durable RESULT exists and is internally consistent with current Git objects.

Verify the immutable ZIP and sidecar manifest exist at the recorded paths and correspond to the recorded artifact commit/current repository content.

Use Git object/content identity and existing recorded hashes. A full redundant rebuild is not required unless a concrete inconsistency is found.

Do not access ROM bytes.

### 3. Original claim preservation

Do not modify:

- `parallel/PM/DEDUP_CLAIMS/training.farm.r0.4.7.windows-portable-real-wof-proof-bundle-v1.json`;
- `parallel/PM/STAGE_CLAIMS/TRAINING_FARM_R0_4_7_WINDOWS_PORTABLE_REAL_WOF_PROOF_BUNDLE_V1.json`.

Their historical `STARTED` state is intentionally preserved as stale history.

The successor recovery RESULT must explicitly state that these historical claims are superseded for closeout authority by this recovery generation.

### 4. No implementation/QA expansion

Do not:

- change `training/farm/**` implementation;
- rebuild or republish a new ZIP if the recorded package remains materially valid;
- modify strict R0.2/R0.4 proof acceptance;
- modify `stable-retro==0.9.8` authority;
- run real emulator/WOF;
- fabricate real proof;
- start multi-worker Reward/Search/RL;
- create R0.4.8;
- enter R0.5;
- open Fresh QA merely because this recovery exists.

If a material implementation defect is discovered, this closeout recovery must stop `BLOCKED` and identify the exact defect. A separate PM-authorized implementation recovery would then be required.

### 5. Real-proof gate check

Search current repository authority only for a genuine successor R0.2 `REAL_WOF` proof and R0.4 `REAL_WOF_FORK` proof.

Do not infer Owner-local proof from this recovery, from fixture/self-check evidence, or from the existence of the portable package.

Unless both strict real proofs are actually present and current-authority-valid, record:

- `realWofProof=false` for this closeout recovery;
- R0.5 remains locked;
- exact next action remains Owner-local execution of the existing immutable R0.4.7 package.

Even if new proof appears concurrently, do not enter R0.5 inside this recovery. Record the fact and stop after closeout; PM will schedule the next stage separately after verifying proof authority.

## Required successor durable RESULT

Write:

`parallel/TRAINING_FARM_R0_4_7_WINDOWS_PORTABLE_REAL_WOF_PROOF_BUNDLE_V1_CLOSEOUT_RECOVERY_V2/RESULT.md`

Include at minimum:

- current main inspected;
- fresh recovery canonical/stage claim token and paths;
- exact original R0.4.7 implementation candidate;
- immutable artifact commit;
- original durable RESULT commit/path;
- current-main drift classification;
- confirmation whether strict proof/package runtime materially drifted;
- immutable ZIP/manifest existence and identities checked;
- explicit statement that historical original STARTED claims were not modified;
- explicit successor supersession statement;
- `containsRomBytes=false`;
- `realWofProof=false` unless current repository contains genuine real proof authority;
- `r0_5Authorized=false` unless PM separately authorizes after strict proof validation; this recovery itself never authorizes R0.5;
- exact Owner next action if real proof remains absent;
- final stop verdict.

## Claim closeout

After the successor RESULT is durable:

1. token-verify the fresh recovery canonical claim;
2. update only the fresh recovery canonical claim to `COMPLETE` with exact source/reconciliation candidate and result commit/path;
3. token-verify the fresh recovery stage claim;
4. update only the fresh recovery stage claim to `COMPLETE`;
5. re-read both fresh recovery claims and RESULT from current `main`;
6. verify the original historical R0.4.7 claims remain unchanged.

Do not stop after writing only RESULT or only one claim.

## Final stop condition

Only one of:

`COMPLETE — TRAINING FARM R0.4.7 WINDOWS PORTABLE REAL-WOF PROOF BUNDLE V1 CLOSEOUT RECOVERY V2 — SUCCESSOR CLOSEOUT AUTHORITY DURABLE; REAL R0.2/R0.4 PROOF STILL REQUIRED`

or, if genuine real proof appeared concurrently:

`COMPLETE — TRAINING FARM R0.4.7 WINDOWS PORTABLE REAL-WOF PROOF BUNDLE V1 CLOSEOUT RECOVERY V2 — SUCCESSOR CLOSEOUT AUTHORITY DURABLE; REAL PROOF REQUIRES PM RECONCILIATION BEFORE NEXT STAGE`

or precise irreducible:

`BLOCKED — <exact material drift / missing artifact / authority defect>`

or canonical duplicate stop.

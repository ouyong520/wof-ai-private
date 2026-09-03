# Training Farm R0.4.7 Windows Portable Real-WOF Proof Bundle V1 — Closeout Recovery V2

## Final state

`COMPLETE — TRAINING FARM R0.4.7 WINDOWS PORTABLE REAL-WOF PROOF BUNDLE V1 — CLOSEOUT RECOVERY V2`

This recovery is closeout/reconciliation only. It does not rebuild the R0.4.7 package, execute Browser/WOF, rerun repository QA, or enter R0.5.

## Recovery authority

- authorization/base main: `53c3c4f0beb7a5e3008c378f3abd3cd6a540f6ef`
- dedup protocol: `v2`
- dedup mode: `exclusive`
- dedup key / effective key: `training.farm.r0.4.7.windows-portable-real-wof-proof-bundle-v1.closeout-recovery-v2`
- stageId: `TRAINING_FARM_R0_4_7_WINDOWS_PORTABLE_REAL_WOF_PROOF_BUNDLE_V1_CLOSEOUT_RECOVERY_V2`
- claim token: `r047-closeout-v2-20260903-0815-2f7c9a63d4e1b8a5`
- fresh canonical claim acquisition commit: `1659e43021b92d9f437f06d411685a46d0107a1d`
- fresh stage claim acquisition commit: `fe4b2ede9fa78710418e2f23ae265dd2afdca264`

Before either claim was created, the exact canonical and stage paths were absent and no equivalent ACTIVE/COMPLETE Recovery V2 authority was found. The canonical claim was created first with create-only semantics and read back with the exact token; only then was the stage claim created and token-verified.

## Frozen R0.4.7 candidate revalidation

Frozen implementation candidate:

`ba1fc43c2ea2a5f04909a1b3dca88b69845d62c8`

The candidate commit exists and is the R0.4.7 portable-proof canonicalization candidate. Its Training Farm implementation changes are limited to the R0.4.7 bundle builder/verifier surface.

Immutable artifact commit:

`985015de1779186906af2b570764c975d94015f3`

The immutable artifact commit exists and adds the R0.4.7 ZIP plus manifest.

## Durable artifact authority preserved

The original durable result still exists at:

`parallel/TRAINING_FARM_R0_4_7_WINDOWS_PORTABLE_REAL_WOF_PROOF_BUNDLE_V1/RESULT.md`

It records the same frozen candidate and immutable artifact authority.

The immutable artifact remains represented by:

- ZIP: `training/farm/dist/WOF_Training_Farm_R0_4_7_Portable_Proof_ba1fc43c.zip`
  - recorded SHA256: `7af95b01401d3d3be059de9223397bba39cdbf16080b5d4a516be77d34c8b511`
  - Git blob: `864f858901e770aa46208e1d00bab0d5eb65a963`
- manifest: `training/farm/dist/WOF_Training_Farm_R0_4_7_Portable_Proof_ba1fc43c.manifest.json`
  - recorded SHA256: `b8b464f2f84dd53672dbdc06d32a0c4d5599d254797265b76e08f14fe1a83100`
  - current Git blob: `b45fc7f1a60fdf73bf78135a7e3f06cc4c93ca80`

The current manifest still binds:

- `sourceCommit = ba1fc43c2ea2a5f04909a1b3dca88b69845d62c8`
- `archiveFile = WOF_Training_Farm_R0_4_7_Portable_Proof_ba1fc43c.zip`
- `archiveSha256 = 7af95b01401d3d3be059de9223397bba39cdbf16080b5d4a516be77d34c8b511`
- `truthLabel = TEST_FORMULA_PARITY_ONLY_NOT_REAL_WOF_RUN`
- `realWofExecuted = false`

Publisher workflow run `33662983175` is still `completed / success` for the R0.4.7 portable bundle publish flow.

## Drift reconciliation

Comparison from frozen candidate `ba1fc43c2ea2a5f04909a1b3dca88b69845d62c8` through the Recovery V2 authorization base showed only the expected R0.4.7 publishing/artifact records, PM metadata/results, and later unrelated repository work. No material change to the frozen R0.4.7 Training Farm runtime/package implementation surface was found.

Comparison from immutable artifact commit `985015de1779186906af2b570764c975d94015f3` through the authorization base likewise showed no replacement or mutation of the immutable R0.4.7 ZIP/manifest authority and no material R0.4.7 package/runtime drift requiring rebuild or repeated QA.

Therefore this closeout reuses the existing green durable evidence under the repository testing-cadence policy.

## Historical R0.4.7 claims preserved

The original historical R0.4.7 claims remain intentionally untouched:

- `parallel/PM/DEDUP_CLAIMS/training.farm.r0.4.7.windows-portable-real-wof-proof-bundle-v1.json`
- `parallel/PM/STAGE_CLAIMS/TRAINING_FARM_R0_4_7_WINDOWS_PORTABLE_REAL_WOF_PROOF_BUNDLE_V1.json`

Both historical records remain `STARTED` with their original token. This Recovery V2 does not rewrite, delete, supersede in-place, or normalize those historical claim files; it closes only its own fresh recovery authority.

## No duplicate execution

Per the closeout prompt and testing cadence:

- no package rebuild was performed;
- no Browser/WOF execution was performed;
- no duplicate repository QA was run;
- no R0.5 implementation or authorization was started.

## Real-WOF proof authority search

Repository authority was searched specifically for genuine R0.2 `REAL_WOF` and R0.4 `REAL_WOF_FORK` PASS evidence rather than preparation, launcher, synthetic, or gate-only records.

The existing durable Owner proof-runner preparation result explicitly states that no legal local WOF ROM/runtime was available to that worker, no real WOF execution was attempted, no R0.2 `REAL_WOF` PASS was claimed, and no R0.4 `REAL_WOF_FORK` PASS was claimed.

The later beginner real-WOF launcher result is likewise an Owner UX/onboarding completion and explicitly states that it does not claim either real proof PASS; the remaining strict proof must be produced by the Owner's local legal WOF + Stable-Retro/FBNeo run.

Repository search found no later qualifying durable proof that establishes both genuine gates. Preparation plans, launchers, validators, expected proof strings, synthetic/self-check evidence, and owner-run instructions are not accepted as real proof authority.

Therefore:

`R0.5 REMAINS LOCKED — NO QUALIFYING R0.2 REAL_WOF + R0.4 REAL_WOF_FORK DURABLE PASS AUTHORITY FOUND`

## Closeout protocol

This successor RESULT is written before claim-state mutation. After this RESULT is durable, the Recovery V2 canonical and stage claims must be read back again and the exact token verified. Only those two fresh Recovery V2 claims may then transition from `ACTIVE` to `COMPLETE`; the historical R0.4.7 `STARTED` claims remain untouched.

The recovery is complete only after a final repository reread confirms this RESULT and both fresh Recovery V2 claims as durable `COMPLETE` records.

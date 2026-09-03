# Training Farm R0.4.7 Windows Portable Real-WOF Proof Bundle V1 — Closeout Recovery V3

## Final verdict

`COMPLETE — TRAINING FARM R0.4.7 WINDOWS PORTABLE REAL-WOF PROOF BUNDLE V1 CLOSEOUT RECOVERY V3 — CORRECT SUCCESSOR CLOSEOUT AUTHORITY DURABLE; REAL R0.2/R0.4 PROOF STILL REQUIRED`

This V3 is a PM-authorized closeout authority correction only. It did not rebuild or republish the immutable R0.4.7 ZIP, modify Training Farm implementation, execute Browser/WOF, rerun historical QA, create R0.4.8, or enter R0.5.

## V3 authority

- authorization main: `dcd269d9ef30f1e1aab61d59f1ee11b06f1b3714`
- current main inspected after V3 claim acquisition and before durable RESULT: `c2dfe8c0e1033c082a4bfa9b84017f08b8da10b7`
- V3 reconciliation sourceCandidate/current authority commit used for closeout: `c2dfe8c0e1033c082a4bfa9b84017f08b8da10b7`
- dedup protocol: `v2`
- dedup mode: `exclusive`
- dedup key / effective key: `training.farm.r0.4.7.windows-portable-real-wof-proof-bundle-v1.closeout-recovery-v3`
- stageId: `TRAINING_FARM_R0_4_7_WINDOWS_PORTABLE_REAL_WOF_PROOF_BUNDLE_V1_CLOSEOUT_RECOVERY_V3`
- claim token: `r047-closeout-v3-20260903-84c40b730eefa20ec09c`
- canonical claim: `parallel/PM/DEDUP_CLAIMS/training.farm.r0.4.7.windows-portable-real-wof-proof-bundle-v1.closeout-recovery-v3.json`
- canonical acquisition commit: `bba5593aa245497f2a6f3cde70634430a7a6cd41`
- stage claim: `parallel/PM/STAGE_CLAIMS/TRAINING_FARM_R0_4_7_WINDOWS_PORTABLE_REAL_WOF_PROOF_BUNDLE_V1_CLOSEOUT_RECOVERY_V3.json`
- stage acquisition commit: `93855f454b394990f373bc7202bacd9b6d2e1c5a`

Duplicate preflight found no existing V3 canonical claim, no V3 stage claim, no V3 RESULT, and no equivalent/newer V3 ACTIVE/COMPLETE authority. The canonical claim was created first with create-only semantics and then read back from `main` with the exact token and ACTIVE state. The matching stage claim was created only after canonical ownership verification and was likewise read back with the exact token and ACTIVE state.

## Frozen original R0.4.7 authority

- frozen implementation/source candidate: `ba1fc43c2ea2a5f04909a1b3dca88b69845d62c8`
- immutable artifact commit: `985015de1779186906af2b570764c975d94015f3`
- original durable RESULT path: `parallel/TRAINING_FARM_R0_4_7_WINDOWS_PORTABLE_REAL_WOF_PROOF_BUNDLE_V1/RESULT.md`
- original durable RESULT commit: `a85c3d509e931e48ddccb6bcf45ff5c4189c6b2f`

Both the immutable artifact commit and original RESULT commit were directly re-read. The original RESULT still records the frozen source candidate, artifact commit and exact package identities below.

## Current Git object truth

ZIP:

- path: `training/farm/dist/WOF_Training_Farm_R0_4_7_Portable_Proof_ba1fc43c.zip`
- current Git blob: `864f858901e770aa46208e1d00bab0d5eb65a963`
- SHA256: `4e51fe3300237a6142b88acdd25436ee82512a5719ea527c5f26c3d9ba55ddd5`
- size: `261003` bytes

The ZIP path was re-read from current `main` and exposes the expected Git blob. Its SHA256 and size are bound by both the original durable RESULT and the current immutable sidecar created by artifact commit `985015de1779186906af2b570764c975d94015f3`.

Sidecar:

- path: `training/farm/dist/WOF_Training_Farm_R0_4_7_Portable_Proof_ba1fc43c.manifest.json`
- current Git blob: `7999e2fc10ae3744253a5951f47fdf4ec273a54a`
- SHA256: `cfd21b35845dd7ee25f020140cc1f58f654e00e91f1b2911267a398f1c981aab`
- size: `718` bytes
- sourceCandidate: `ba1fc43c2ea2a5f04909a1b3dca88b69845d62c8`
- zipFile: `WOF_Training_Farm_R0_4_7_Portable_Proof_ba1fc43c.zip`
- zipSha256: `4e51fe3300237a6142b88acdd25436ee82512a5719ea527c5f26c3d9ba55ddd5`
- zipSize: `261003`
- inner manifest path: `portable_manifest.json`
- inner manifest SHA256: `82a7733c186fdc120766a09485f76afc6d1b9b3e6a6120d98296fbe8b6ed0350`
- inner manifest size: `11929`
- payload aggregate SHA256: `44f111ea9237309ba8c24cd2351d94818d24a34cefc7246c8f02d1ca6840910c`
- `containsRomBytes=false`
- `realWofProof=false`
- `r0_5Authorized=false`

The current sidecar bytes were re-read directly from `main`; their byte length is 718 and their SHA256 recomputes to `cfd21b35845dd7ee25f020140cc1f58f654e00e91f1b2911267a398f1c981aab`.

## Drift classification

Comparison from frozen source candidate `ba1fc43c2ea2a5f04909a1b3dca88b69845d62c8` to current `main` shows the expected R0.4.7 publisher workflow, immutable artifact publication, original RESULT/claim metadata, closeout V2/V3 PM metadata/results/claims, and unrelated Alpha/Collector PM work. It does not show a later material modification of the frozen strict R0.2/R0.4 proof runtime, R0.4.6 bootstrap, R0.4.7 builder/verifier/source closure, or immutable R0.4.7 package authority.

Comparison from immutable artifact commit `985015de1779186906af2b570764c975d94015f3` to current `main` contains no later `training/farm/**` runtime/package modification at all; subsequent Training Farm changes in that comparison are PM/RESULT/claim authority records. The current ZIP and sidecar retain the same Git object identities established by the immutable artifact commit.

Classification: `NO MATERIAL R0.4.7 RUNTIME/PACKAGE DRIFT`.

The concurrent commit `c2dfe8c0e1033c082a4bfa9b84017f08b8da10b7` adds only an unrelated Alpha V1 PM start prompt and does not affect Training Farm package/runtime authority.

## V2 defect and successor supersession

Historical Closeout Recovery V2 RESULT remains immutable at:

`parallel/TRAINING_FARM_R0_4_7_WINDOWS_PORTABLE_REAL_WOF_PROOF_BUNDLE_V1_CLOSEOUT_RECOVERY_V2/RESULT.md`

It states artifact identity values including ZIP SHA256 `7af95b01401d3d3be059de9223397bba39cdbf16080b5d4a516be77d34c8b511`, manifest SHA256 `b8b464f2f84dd53672dbdc06d32a0c4d5599d254797265b76e08f14fe1a83100`, and manifest/current-Git blob `b45fc7f1a60fdf73bf78135a7e3f06cc4c93ca80`, plus a different manifest field model. Those statements conflict with the original durable R0.4.7 RESULT, immutable artifact commit and current Git object truth verified above.

The V2 canonical and stage claims are both historical `COMPLETE` records, but current re-read confirms that both omit the V2 prompt-required closeout metadata fields `sourceCandidate`, `resultPath`, and `resultCommit`.

V3 does not edit, normalize or repair V2 in place. V3 explicitly supersedes V2 as the final R0.4.7 closeout authority because V2's RESULT artifact metadata and COMPLETE-claim metadata are internally inconsistent with the durable original artifact authority and its own closeout contract.

The original R0.4.7 RESULT/artifact/claims and all V2 files were left unchanged by V3. V3 adds and later closes only its own canonical claim, stage claim and successor RESULT.

## Real-WOF proof gate

The existing durable Owner proof-runner authority defines the only acceptable real proof shapes as current-authority-valid:

- R0.2: `PASS / DETERMINISM_MATCH`, `proofScope=REAL_WOF`, `realWofProof=true`;
- R0.4: `PASS / FORK_SET_DETERMINISTIC`, `proofScope=REAL_WOF_FORK`, `realWofProof=true`.

Closeout Recovery V2's durable repository search found no qualifying pair and explicitly rejected launchers, package checks, fixtures, synthetic/self-checks, expected strings and Owner instructions as proof. A commit-level comparison from the V2 durable RESULT commit `e1ea46593bba5f15fb2872d9b8361fa372d87d63` through the V3 current-main inspection commit shows only V2 claim-state updates, the V3 authorization/claims, and an unrelated Alpha PM prompt; no Training Farm real-proof/evidence file was added or changed after that search.

Therefore no genuine current repository authority establishes both required real gates.

- `realWofProof=false`
- `r0_5Authorized=false`
- `containsRomBytes=false`
- R0.5 remains locked.

This recovery itself never authorizes R0.5 even if real proof later appears; any later genuine proof requires separate PM reconciliation/authorization.

## Exact Owner next action

On the Owner Windows machine, use the existing immutable R0.4.7 ZIP `WOF_Training_Farm_R0_4_7_Portable_Proof_ba1fc43c.zip`, extract it to a normal local directory, optionally run `验证便携包.cmd`, then run `开始三国10训实机验证.cmd` (or `START_WOF_PROOF.cmd`). Select only the Owner's legally held local WOF ZIP outside the immutable package. The existing strict Owner-local runner must produce both an accepted R0.2 `REAL_WOF / DETERMINISM_MATCH / realWofProof=true` result and an accepted R0.4 `REAL_WOF_FORK / FORK_SET_DETERMINISTIC / realWofProof=true` result before any later proof-gated stage can be considered.

## Closeout sequencing

This RESULT is intentionally made durable before either V3 claim transitions to COMPLETE. After the RESULT commit is known, V3 must token-verify the canonical claim and stage claim, then update only those V3 files to COMPLETE with identical non-empty `sourceCandidate`, `resultPath`, and `resultCommit` metadata. A final reread of current `main`, this RESULT and both claims is required before stopping.

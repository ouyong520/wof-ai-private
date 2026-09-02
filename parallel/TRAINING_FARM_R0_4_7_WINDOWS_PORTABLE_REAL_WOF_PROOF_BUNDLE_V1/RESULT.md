# Training Farm R0.4.7 Windows Portable Real-WOF Proof Bundle V1 — RESULT

## Authority

- Stage: `TRAINING_FARM_R0_4_7_WINDOWS_PORTABLE_REAL_WOF_PROOF_BUNDLE_V1`
- Dedup key: `training.farm.r0.4.7.windows-portable-real-wof-proof-bundle-v1`
- Status: `COMPLETE` for the R0.4.7 portable packaging scope only.
- Claim token: `19417695d39c83c46fb67666355a187043b9091d129a4827`
- Authority base inspected at task continuation: `2eda82450191ce3260e14b93d9d075a0da6cba0d`
- R0.4.7 implementation/source candidate: `ba1fc43c2ea2a5f04909a1b3dca88b69845d62c8`
- Immutable artifact commit: `985015de1779186906af2b570764c975d94015f3`
- The earlier claim metadata value `89730c40fe4e425c80e02f1ccc882107ff6d28f6` was a Collector V8 commit, not an R0.4.7 candidate. It was corrected under the same existing claim/token before closeout and is not used as R0.4.7 package authority.

## Immutable owner package

- Package ID: `WOF_Training_Farm_R0_4_7_Windows_Portable_Real_WOF_Proof_Bundle_V1`
- ZIP: `training/farm/dist/WOF_Training_Farm_R0_4_7_Portable_Proof_ba1fc43c.zip`
- ZIP Git blob: `864f858901e770aa46208e1d00bab0d5eb65a963`
- ZIP SHA256: `4e51fe3300237a6142b88acdd25436ee82512a5719ea527c5f26c3d9ba55ddd5`
- ZIP size: `261003` bytes
- Sidecar manifest: `training/farm/dist/WOF_Training_Farm_R0_4_7_Portable_Proof_ba1fc43c.manifest.json`
- Sidecar Git blob: `7999e2fc10ae3744253a5951f47fdf4ec273a54a`
- Sidecar SHA256: `cfd21b35845dd7ee25f020140cc1f58f654e00e91f1b2911267a398f1c981aab`
- Sidecar size: `718` bytes
- Inner manifest: `portable_manifest.json`
- Inner manifest SHA256: `82a7733c186fdc120766a09485f76afc6d1b9b3e6a6120d98296fbe8b6ed0350`
- Inner manifest size: `11929` bytes
- Payload aggregate SHA256: `44f111ea9237309ba8c24cd2351d94818d24a34cefc7246c8f02d1ca6840910c`

The package was built twice from the exact frozen source candidate. The two ZIP byte streams compared equal and had the same SHA256/size above. The immutable ZIP and sidecar were then committed to `main` by the successful ROM-free publisher run.

## Minimal portable source closure

The package contains only the audited source closure needed to preserve the existing R0.2/R0.4 proof path and R0.4.6 Windows bootstrap, plus the R0.4.7 verifier/schema and generated owner-facing top-level files. Exact proof runtime/source files are pinned by Git blob identity; source drift fails closed before packaging.

Included authority families are:

- Stable-Retro/FBNeo adapter and fake backend support used by existing deterministic runtime.
- R0.2 determinism runtime, schema/actions and proof-shape validation dependency.
- R0.4 deterministic savestate fork runtime, contracts/schemas and `real_wof_fork_smoke.plan.json`.
- Existing strict `real_wof_proof_owner_runner.py` and `beginner_real_wof_launcher.py` unchanged.
- Existing R0.4.6 `windows_oneclick_bootstrap.py` and `run_windows_oneclick_env_bootstrap.cmd` unchanged.
- Exact dependency authority `stable-retro==0.9.8` from `training/farm/requirements-r0.1.txt`.
- `OWNER_LOCAL_ROM_REFERENCE.md` metadata/reference documentation only; no ROM bytes.
- R0.4.7 shipped verifier and manifest schema.

Excluded from the immutable package are repository history/Git metadata, unrelated Alpha/Collector/PM lanes, tests, `.venv`/venvs, caches, logs, evidence, checkpoints, generated runtime state, training data, ROMs, BIOS files, savestate evidence, and game assets.

## Owner entrypoints and mutable-state boundary

Top-level package entrypoints:

- `开始三国10训实机验证.cmd`
- ASCII fallback: `START_WOF_PROOF.cmd`
- ROM-free package integrity check: `验证便携包.cmd`
- Instructions: `README_开始这里.txt`

The Chinese start entry keeps mutable state outside the immutable bundle by default under a sibling `三国10训-data` root, forwards that root and its `evidence` directory into the existing R0.4.6 bootstrap, and preserves the downstream child exit code. The R0.4.6 bootstrap retains its existing Python detection/managed-environment/dependency behavior and delegates to the existing strict Owner launcher/runner. The portable layer does not fork or weaken proof acceptance semantics.

## Determinism and fail-closed verifier

The deterministic builder uses:

- stable lexicographic entry order;
- normalized `/` archive paths;
- fixed DOS ZIP timestamp `1980-01-01 00:00:00`;
- `ZIP_STORED` for reproducible bytes;
- explicit per-file byte size, SHA256 and Git blob identity for repository-source members;
- sidecar artifact manifest for ZIP SHA256/size, avoiding self-hash recursion.

The shipped verifier/build path rejects:

- tampered payload bytes;
- missing members;
- extra/unallowlisted members;
- duplicate members and Windows case-fold collisions;
- `..` traversal/non-normalized paths;
- absolute, drive-qualified or separator-invalid paths;
- ROM/archive/game-like payload suffixes;
- forbidden mutable/local-state directories;
- symlinks in an extracted immutable tree;
- source Git-blob drift;
- non-deterministic ZIP timestamp/compression metadata.

Chinese characters, spaces and parentheses in the extracted Windows-style owner path were exercised by the ROM-free self-check.

## Verification evidence

Successful publisher workflow:

- Workflow: `Training Farm R0.4.7 Portable Bundle Publish`
- Run ID: `33662983175`
- Job ID: `100357773405`
- Conclusion: `success`

That run materialized the exact `ba1fc43c2ea2a5f04909a1b3dca88b69845d62c8` candidate with `git archive` and completed all of the following without ROM access:

1. `python -m unittest training.farm.test_windows_portable_real_wof_bundle -v` — PASS, 6/6.
2. `python training/farm/scripts/test_windows_host_dry_run_offline.py` — PASS; `deterministic=true`, `unicodeSpaceParenthesesPath=true`, `romAccessed=false`, `realWofProof=false`, `r0_5Authorized=false`.
3. `python -m py_compile` for builder and shipped verifier — PASS.
4. Existing R0.4.6 `windows_oneclick_bootstrap --diagnostics-json` under a Chinese/space/parentheses local/evidence path — PASS with `romAccessed=false`, `realWofProof=false`, `r0_5Authorized=false`, `realWorkerExecutionStarted=false`.
5. Two independent deterministic package builds — PASS and byte-identical via `cmp`.
6. ZIP verifier against the frozen source candidate — PASS.
7. Extracted-tree verifier under `/tmp/三国 10训 (portable)` — PASS.
8. Immutable ZIP + sidecar repository publication — PASS in artifact commit `985015de1779186906af2b570764c975d94015f3`.

The 6-test suite explicitly exercises deterministic output/flags, tamper/missing/extra rejection, duplicate/traversal/absolute/drive/ROM-like rejection, Unicode/space/parentheses extracted paths, source-blob drift rejection, and owner-entry local-root/child-exit-code contracts.

## Proof boundary — intentionally not satisfied by this package

This RESULT is **not** a real-WOF proof result.

- `containsRomBytes: false`
- `realWofProof: false`
- `readOnlyProof: true`
- `ramWrites: 0`
- `inputInjection: false`
- `r0_5Authorized: false`
- Authoritative R0.2 `REAL_WOF PASS`: **not available yet**.
- Authoritative R0.4 `REAL_WOF_FORK PASS`: **not available yet**.
- R0.5 remains locked.

No ROM/BIOS/game asset was included, downloaded, copied into the repository, or used by the ROM-free package build/self-check. Only the existing strict Owner-local runner may establish the missing R0.2/R0.4 real-WOF proof gates.

## Exact Owner next action

On the Owner Windows machine, obtain the immutable ZIP above, extract it to a normal local directory (Chinese characters, spaces and parentheses are supported), optionally double-click `验证便携包.cmd`, then double-click `开始三国10训实机验证.cmd`. Select only the Owner's legally held local WOF ZIP located outside the immutable package. The existing strict launcher will validate the recorded WOF identity and the existing R0.2/R0.4 runner will write evidence outside the immutable source tree. Only explicit downstream `REAL_WOF PASS` plus `REAL_WOF_FORK PASS` may unlock later proof-gated work; R0.4.7 itself does not do so.

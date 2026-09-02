# Training Farm R0.4 Owner Beginner Real-WOF Launcher V1 — RESULT

## Final state

`COMPLETE — TRAINING FARM R0.4 OWNER BEGINNER REAL-WOF LAUNCHER V1 — READY FOR OWNER DOUBLE-CLICK RUN`

This is an Owner UX/onboarding implementation result. It does **not** claim that R0.2 real determinism or R0.4 real fork smoke has passed on a real WOF runtime. The remaining real proof must be produced by the Owner's local legal ROM + Stable-Retro/FBNeo runtime through the unchanged strict runner.

## Authority / dedup

- stageId: `TRAINING_FARM_R0_4_OWNER_BEGINNER_REAL_WOF_LAUNCHER_V1`
- dedupProtocol: `v2`
- dedupKey / effectiveDedupKey: `training.farm.r0.4.owner-beginner-real-wof-launcher-v1`
- claimToken: `f4a97c3b8e1d4a72b6c095e3d8f21a6c`
- start commit: `1e926dc81de0b8e336ef7db01786dc260c498447`
- implementation candidate commit: `f5edce51a9e2d1bad0c0bb9125adff767cc42199`
- canonical claim: `parallel/PM/DEDUP_CLAIMS/training.farm.r0.4.owner-beginner-real-wof-launcher-v1.json`
- stage claim: `parallel/PM/STAGE_CLAIMS/TRAINING_FARM_R0_4_OWNER_BEGINNER_REAL_WOF_LAUNCHER_V1.json`
- duplicate/repost behavior was checked before mutation: no prior equivalent RESULT/launcher and no occupied canonical/stage claim existed; create-only v2 ownership was acquired and token-verified before implementation.
- canonical claim closeout: `COMPLETE`, commit `77a80cabcfdc18500d93126932c8d2a843c8c409`.
- stage claim closeout: `COMPLETE`, commit `a0c083f39c5e7947acf8dcd8cf73661126bca97e`.
- both closeout records retain the exact original claimToken and reference the durable RESULT path/creation commit `1474541af3f501b6872c3a0524de5a87c5721d09`.

## Exact implementation candidate

Files owned/changed by this module:

- `training/farm/beginner_real_wof_launcher.py`
  - blob: `17491953c7d20c76a91b0169c1f8ab68971ce056`
- `training/farm/run_real_wof_proof_beginner.cmd`
  - blob: `9d4cf2d02261a40e70fa36fde17f1e9afb0445fa`
- `training/farm/tests/test_beginner_real_wof_launcher.py`
  - blob: `5a487ec3584bfada30114b80baf455d42620ae26`
- `training/farm/R0_4_OWNER_BEGINNER_REAL_WOF_LAUNCHER.md`
  - blob: `faf54e6e201acb7963c8c01ff52d9b09086c1f0c`
- `training/farm/OWNER_LOCAL_ROM_REFERENCE.md`
  - blob: `e84053558e6acb2613223554792041b3f87a5fb9`
  - metadata/documentation only; ROM bytes are not present.

The existing strict proof authority remains unchanged:

- `training/farm/real_wof_proof_owner_runner.py`
  - current blob: `c966538befeb25f8b6fd694183fa4984ec73b9be`
  - identical to the already-COMPLETE R0.4 Owner proof runner candidate recorded before this task.

No R0.2/R0.4 proof validator, runtime identity, fork semantics, proof scope, source-drift guard, `realWofProof=true` requirement, Reward/search/multi-worker/RL path, or R0.5 implementation was changed.

## Beginner Windows flow

Primary Owner entry point:

```text
training\farm\run_real_wof_proof_beginner.cmd
```

Behavior:

1. changes to repository root safely;
2. probes `py -3` and then `python` without PowerShell policy changes, registry changes, admin elevation, global input injection, or unsafe shell setup;
3. rejects unsupported Python before importing the 3.10+ launcher and shows `WAITING_PREREQUISITE` for versions outside 3.10..3.14;
4. if `WOF_ROM_PATH` already exists, uses it without changing the parent/global environment;
5. otherwise opens a standard Tk/Windows ZIP picker;
6. drag/drop of a ZIP onto the `.cmd` is an explicit fallback because the path is accepted as the launcher's positional argument;
7. picker cancel returns clean `WAITING_PREREQUISITE`, not a traceback;
8. the console remains visible via `pause` for the double-click flow; `WOF_BEGINNER_NO_PAUSE` is an expert/automation escape hatch only.

## Recorded Owner ROM identity guard

Current repository reference consumed by the launcher:

- display filename: `wof(2).zip`
- size: `6366259` bytes
- SHA256: `6355d82b9457433725fe53cf1723f94eef752b569f3c07b51ac7e57be4a3cbaa`

Identity acceptance is **not** based on filename. The default beginner flow requires both exact recorded size and exact SHA256.

Mismatch fails closed with a beginner-readable `WAITING_PREREQUISITE` asking the Owner to reselect the correct ZIP. Missing/malformed `OWNER_LOCAL_ROM_REFERENCE.md` also fails closed by default.

Expert-only future-ROM override exists only as an explicit CLI flag:

```text
--allow-unrecorded-rom
```

It does not appear in the double-click default and cannot bypass the strict runner's external-path, ROM SHA binding, real proof scope, source identity, R0.2 gate, R0.4 validator, or `realWofProof=true` requirements.

## ROM / evidence safety

The launcher:

- hashes the external ZIP in place;
- never copies the ROM into the repository;
- never unzips the ROM;
- never writes ROM bytes, savestates or raw RAM into task RESULT artifacts;
- rejects repository-local ZIP paths before handoff;
- sets `WOF_ROM_PATH` only in a copied child environment when the path came from picker/drag/drop/CLI;
- preserves an existing parent/global `WOF_ROM_PATH` rather than mutating it;
- passes any requested evidence root unchanged to the strict runner, which remains authoritative for external/writable evidence-directory validation.

## Dependency guidance

Before strict handoff the beginner layer translates the obvious prerequisites:

- unsupported Python;
- missing `stable-retro==0.9.8`;
- wrong Stable-Retro version;
- FBNeo capability failure;
- missing/wrong/external-path-invalid ROM selection.

It never silently installs packages. It never downloads ROM, BIOS, proprietary emulator binaries or copyrighted game assets. Evidence-directory availability remains enforced by the unchanged strict runner and appears as `WAITING_PREREQUISITE` if unavailable.

## Strict authority handoff

The only proof execution launched by this UX is:

```text
<current Python> -m training.farm.real_wof_proof_owner_runner
```

The selected exact external path is placed in the child process `WOF_ROM_PATH`. The beginner layer does not implement its own determinism/fork proof consumer and cannot turn mocked/synthetic output into real proof.

PASS is additionally fail-closed at the UX layer: a PASS line is rejected if the strict child exit code is non-zero or if no valid `summary.json` is present in the reported evidence directory.

## Final screen contract

The final screen preserves the strict primary verdicts:

```text
PASS — R0.2 REAL WOF DETERMINISM + R0.4 REAL FORK SMOKE
WAITING_PREREQUISITE — ...
BLOCKED — R0.2 REAL DETERMINISM — ...
BLOCKED — R0.4 REAL FORK SMOKE — ...
```

It then displays:

- selected local ZIP path when available;
- recorded-ROM identity match state;
- exact evidence directory, or explicit `not created` when preflight stopped before a run directory existed;
- existence/path of `summary.txt`;
- existence/path of `summary.json`;
- existence/path of `r0_2_real_determinism.json`;
- existence/path of `r0_4_real_fork_smoke.json`;
- `PASS => 告诉 PM：1`;
- `WAITING/BLOCKED => 发送 summary.txt；若尚未生成则发送最终窗口截图`.

On interactive Windows, the Owner may type `O` to open the evidence folder. This is optional UX only and does not affect proof state.

## Implementation-owned self-check

Authored repository self-check:

```text
python -m unittest training.farm.tests.test_beginner_real_wof_launcher
```

It contains 11 focused cases covering:

- recorded reference parsing;
- matching SHA256/size;
- wrong SHA256 fail-closed;
- explicit expert override does not claim a match;
- repository-local ZIP rejection;
- spaces + Chinese directory + `wof(2).zip` parentheses path;
- picker cancel;
- existing `WOF_ROM_PATH` precedence;
- exact session-local child environment path and no parent mutation;
- dependency guidance;
- PASS / WAITING / R0.2 BLOCKED / R0.4 BLOCKED messaging;
- missing reference fail-closed;
- no ROM copy into repository.

The available worker execution surface did not expose a checkout of this private repository and the repository has no current CI status attached to the candidate commit. Therefore the checked-in unittest file could not be invoked directly from the GitHub worktree here.

A compact isolated reconstruction of the committed launcher functions was executed once after the module was complete, using only temporary fake ZIP bytes and stubbed proof subprocesses. Results:

```text
full reconstructed module py_compile: PASS
12/12 focused launcher assertions: PASS
```

The 12 assertions covered reference parse, matching identity, wrong hash rejection, Unicode/space/parentheses path, no repo copy, picker cancel, exact child env, dependency ready/missing, PASS verdict, R0.2 BLOCKED verdict, R0.4 BLOCKED verdict, and PASS-summary/evidence integration.

Mock/stub output from this self-check is implementation evidence only. It is **not** real WOF proof and was never written as R0.2/R0.4 real evidence.

## Real local proof status / remaining Owner action

`OWNER DOUBLE-CLICK RUN REQUIRED`

Owner action:

1. ensure a supported Python 3.10..3.14 and pinned Stable-Retro/FBNeo environment are installed;
2. double-click `training\farm\run_real_wof_proof_beginner.cmd`;
3. select the legal local WOF ZIP when prompted;
4. if final verdict is PASS, tell PM `1`;
5. if WAITING/BLOCKED, send `summary.txt`, or a screenshot if no summary was created.

No real WOF execution was attempted by this implementation worker, no real proof was fabricated, and this RESULT does not authorize R0.5.

## Scope confirmation

No changes were made to:

- `product/alpha/**`;
- Browser / Transport / Recorder / PYLAUNCH / OneClick product semantics;
- WinKawaks Collector;
- R0.2 proof semantics;
- R0.4 fork proof semantics;
- R0.5;
- Reward / search / multi-worker / RL semantics;
- ROM / BIOS / proprietary emulator/game binary assets.

## Stop condition

`COMPLETE — TRAINING FARM R0.4 OWNER BEGINNER REAL-WOF LAUNCHER V1 — READY FOR OWNER DOUBLE-CLICK RUN`

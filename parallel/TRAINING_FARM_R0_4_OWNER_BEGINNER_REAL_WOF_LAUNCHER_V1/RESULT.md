# Training Farm R0.4 Owner Beginner Real-WOF Launcher V1 — RESULT

## Final state

`COMPLETE — TRAINING FARM R0.4 OWNER BEGINNER REAL-WOF LAUNCHER V1 — READY FOR OWNER DOUBLE-CLICK RUN`

This is repository-side Owner UX/onboarding completion only. No real WOF proof was fabricated or claimed. The remaining real R0.2/R0.4 proof must be produced locally by Owner using a legally held external ROM and the unchanged strict runner.

## Authority / dedup

- stageId: `TRAINING_FARM_R0_4_OWNER_BEGINNER_REAL_WOF_LAUNCHER_V1`
- dedupProtocol: `v2`
- dedupKey / effectiveDedupKey: `training.farm.r0.4.owner-beginner-real-wof-launcher-v1`
- claimToken: `f4a97c3b8e1d4a72b6c095e3d8f21a6c`
- start commit: `1e926dc81de0b8e336ef7db01786dc260c498447`
- implementation candidate: `f5edce51a9e2d1bad0c0bb9125adff767cc42199`
- canonical claim: `parallel/PM/DEDUP_CLAIMS/training.farm.r0.4.owner-beginner-real-wof-launcher-v1.json`
- stage claim: `parallel/PM/STAGE_CLAIMS/TRAINING_FARM_R0_4_OWNER_BEGINNER_REAL_WOF_LAUNCHER_V1.json`
- canonical and stage claims were both token-verified and transitioned to `COMPLETE` before this final RESULT revision.
- duplicate/repost preflight was policy-compliant: no prior equivalent COMPLETE launcher and no occupied canonical/stage claim existed before create-only acquisition. Future reposts must stop on the completed canonical result.
- after this final RESULT revision is created, both already-COMPLETE claim records are repinned to this revision without changing their state/token.

## Exact implementation

- `training/farm/beginner_real_wof_launcher.py`
  - blob `17491953c7d20c76a91b0169c1f8ab68971ce056`
- `training/farm/run_real_wof_proof_beginner.cmd`
  - blob `9d4cf2d02261a40e70fa36fde17f1e9afb0445fa`
- `training/farm/tests/test_beginner_real_wof_launcher.py`
  - blob `5a487ec3584bfada30114b80baf455d42620ae26`
- `training/farm/R0_4_OWNER_BEGINNER_REAL_WOF_LAUNCHER.md`
  - blob `faf54e6e201acb7963c8c01ff52d9b09086c1f0c`
- `training/farm/OWNER_LOCAL_ROM_REFERENCE.md`
  - blob `e84053558e6acb2613223554792041b3f87a5fb9`
  - metadata/documentation only; no ROM bytes.

Existing strict proof authority remained unchanged:

- `training/farm/real_wof_proof_owner_runner.py`
  - blob `c966538befeb25f8b6fd694183fa4984ec73b9be`

No R0.2/R0.4 proof validator, runtime identity, fork semantics, source-drift guard, proof scope, `realWofProof=true`, R0.5, Reward, search, multi-worker or RL semantics were modified.

## Beginner entry point

Owner double-click path:

```text
training\farm\run_real_wof_proof_beginner.cmd
```

The `.cmd`:

- prefers a supported `py -3`, then supported `python`;
- checks Python 3.10..3.14 before importing the launcher, so unsupported Python gets a readable `WAITING_PREREQUISITE` instead of a syntax traceback;
- preserves quoted drag/drop arguments including spaces, Chinese path names and parentheses;
- keeps the console visible with `pause` for the normal double-click flow;
- performs no PowerShell execution-policy weakening, registry mutation, admin elevation or global keyboard injection.

## ROM chooser and identity guard

Resolution order:

1. explicit drag/drop/CLI ZIP argument;
2. existing `WOF_ROM_PATH`;
3. standard Tk/Windows ZIP picker.

Picker cancel returns clean `WAITING_PREREQUISITE`.

Current Owner ROM metadata guard:

- filename display: `wof(2).zip`
- size: `6366259` bytes
- SHA256: `6355d82b9457433725fe53cf1723f94eef752b569f3c07b51ac7e57be4a3cbaa`

Default acceptance requires exact **size + SHA256**; filename equality is never identity. Wrong/missing/malformed reference fails closed with beginner-readable guidance.

An expert-only `--allow-unrecorded-rom` exists for a future different legally held external ZIP. It is absent from the beginner double-click default and does not bypass strict runner proof authority.

## ROM safety

The launcher hashes the selected ZIP in place and never:

- copies it into the repository;
- unzips it;
- vendors/base64/splits/encrypts it;
- stores ROM bytes in evidence or RESULT;
- accepts a repository-local ZIP.

When the path is selected by picker/drag/drop/CLI, `WOF_ROM_PATH` is set only in a copied child-process environment. An existing parent/global value is read but not mutated.

## Dependency guidance

Beginner-readable preflight covers:

- unsupported Python;
- missing `stable-retro==0.9.8`;
- wrong Stable-Retro version;
- FBNeo capability not ready;
- ROM missing/wrong/not external/not `.zip`;
- evidence-directory unavailability remains enforced by the unchanged strict runner and is surfaced as `WAITING_PREREQUISITE`.

The launcher does not silently install dependencies and never downloads ROM, BIOS, proprietary emulator binaries or copyrighted game assets.

## Proof authority handoff

The only real proof process launched by this UX is:

```text
<current supported Python> -m training.farm.real_wof_proof_owner_runner
```

The beginner layer does not reimplement determinism or fork validation. The existing runner remains authoritative for R0.2 real determinism, R0.4 real fork validation, ROM SHA binding, proof scopes, source drift, external evidence rules and `realWofProof=true`.

The beginner layer is additionally fail-closed on final PASS: a PASS line is not accepted for display as final success unless the strict child exits 0 and a parseable `summary.json` exists in the reported evidence directory.

## Final screen

Primary verdict remains one of:

```text
PASS — R0.2 REAL WOF DETERMINISM + R0.4 REAL FORK SMOKE
WAITING_PREREQUISITE — ...
BLOCKED — R0.2 REAL DETERMINISM — ...
BLOCKED — R0.4 REAL FORK SMOKE — ...
```

It also shows:

- exact selected ZIP path when available;
- ROM reference match state;
- exact evidence directory, or explicit `not created` when preflight stopped before one existed;
- `summary.txt` existence/path;
- `summary.json` existence/path;
- R0.2 JSON existence/path;
- R0.4 JSON existence/path;
- PASS => tell PM `1`;
- WAITING/BLOCKED => send `summary.txt`, or screenshot if no summary exists.

Interactive Windows also offers `O` to open the evidence folder.

## Implementation-owned self-check

Repository test authored:

```text
python -m unittest training.farm.tests.test_beginner_real_wof_launcher
```

It contains 11 focused cases for reference parsing, matching/wrong hash, expert override, repository-local rejection, Unicode/space/parentheses paths, picker cancel, existing `WOF_ROM_PATH`, exact child environment, dependency guidance, final verdicts, missing reference and no ROM copy.

The available worker surface exposes GitHub content/mutations but not a checkout of this private repository, and the candidate had no CI status attached. Therefore the checked-in unittest file could not be invoked directly from the repository worktree here.

One compact isolated reconstruction of the completed committed launcher logic was executed instead, with temporary fake ZIP bytes and stubbed proof subprocesses only:

```text
full reconstructed module py_compile: PASS
12/12 focused launcher assertions: PASS
```

Covered: reference parse, matching identity, wrong hash rejection, Chinese/space/`wof(2).zip` path, no repository ROM copy, picker cancel, exact session-local child env, dependency ready/missing, PASS, R0.2 BLOCKED, R0.4 BLOCKED, and PASS summary/evidence integration.

These mock/stub checks are implementation evidence only and were never labeled or persisted as real WOF proof.

## Remaining Owner action

`OWNER DOUBLE-CLICK RUN REQUIRED`

1. Ensure supported Python 3.10..3.14 plus the current pinned Stable-Retro/FBNeo prerequisites.
2. Double-click `training\farm\run_real_wof_proof_beginner.cmd`.
3. Select the legal local WOF ZIP.
4. PASS => tell PM `1`.
5. WAITING/BLOCKED => send `summary.txt`, or screenshot if summary was not created.

No real WOF execution was attempted here, ROM bytes were never committed, and R0.5 remains unauthorized.

## Stop condition

`COMPLETE — TRAINING FARM R0.4 OWNER BEGINNER REAL-WOF LAUNCHER V1 — READY FOR OWNER DOUBLE-CLICK RUN`

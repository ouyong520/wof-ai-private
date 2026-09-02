# Training Farm R0.4 Real-WOF Proof Owner Runner Prep — RESULT

## Final state

`COMPLETE — TRAINING FARM R0.4 REAL-WOF PROOF OWNER RUNNER PREP — OWNER LOCAL RUN REQUIRED`

This is a repository-side implementation/preparation completion only. No legal local WOF ROM or Owner Stable-Retro/FBNeo runtime was available to this worker, so this RESULT does **not** claim a real R0.2 determinism PASS or real R0.4 fork PASS.

## Authority / dedup

- stageId: `TRAINING_FARM_R0_4_REAL_WOF_PROOF_OWNER_RUNNER_PREP_V1`
- dedupKey: `training.farm.r0.4.real-wof-proof-owner-runner-prep`
- claimToken: `5d4e07b116210bd958890270db4818ac8091557f330d948e`
- start commit: `fd0dd8ebfa11d426cde768a061e70ea877093bc6`
- implementation candidate commit: `c27456256cc14c4dcb756c2e0c189e8e1239cfa5`
- current-main drift check at closeout: no later commit observed; current Training Farm changes are this stage only. Unrelated concurrent Alpha/Collector PM records were not modified by this worker.

## Implemented Owner package

### Windows-first one-command entry point

Owner command:

```cmd
training\farm\run_real_wof_proof.cmd
```

The wrapper changes to repository root, prefers `py -3`, falls back to `python`, and invokes:

```text
python -m training.farm.real_wof_proof_owner_runner
```

Files:

- `training/farm/run_real_wof_proof.cmd`
  - blob: `ae978ba73ae9330714db1923db4188649bacf776`
- `training/farm/real_wof_proof_owner_runner.py`
  - blob: `c966538befeb25f8b6fd694183fa4984ec73b9be`
- `training/farm/real_wof_fork_smoke.plan.json`
  - blob: `4fdc9156730bda758f1a342e332dd39f043d617a`
- `training/farm/R0_4_REAL_WOF_OWNER_RUNNER.md`
  - blob: `bc5476f60831116920220539d7884088bab424aa`
- `training/farm/tests/test_real_wof_owner_runner.py`
  - blob: `0987891108dfb5ce7a33f224caaacbf0158c9f6e`

## Strict prerequisite preflight

The runner fails closed before real execution unless it can establish:

- exact source namespace `stable-retro-fbneo`;
- Windows or Linux runtime;
- current Training Farm supported Python range;
- pinned `stable-retro==0.9.8`;
- FBNeo capability probe;
- `WOF_ROM_PATH` is present;
- ROM path is absolute, external to the repository, readable, `.zip`, and hashable in place;
- current R0.2/R0.4 CLI/schema/plan/runner files exist;
- evidence directory is outside the repository and writable.

It does not download or copy ROM, BIOS, emulator/core binaries, savestates, raw RAM, or copyrighted assets.

## R0.2 real determinism orchestration

The Owner runner reuses the existing R0.2 implementation; it does not reimplement determinism.

It runs current-source R0.2 with:

- `training/farm/determinism_actions.example.json`;
- horizon `8` frames;
- `3` repetitions;
- output `r0_2_real_determinism.json` in the unique external local evidence directory.

Before R0.4 may run, the R0.2 output must pass repository schema surface checks and the existing strict R0.2 semantic proof consumer, and additionally bind to:

- `PASS / DETERMINISM_MATCH`;
- `REAL_WOF`;
- `realWofProof = true`;
- exact Owner action-sequence hash / horizon / repetitions;
- strict real Stable-Retro/FBNeo runtime identity;
- current Farm source candidate/files;
- exact preflight ROM SHA-256;
- recomputed runtime-identity SHA-256.

Fixture/synthetic PASS cannot unlock R0.4. Any R0.2 SKIP/FAIL/ERROR or malformed/stale/wrong-ROM result stops before R0.4.

## Bounded R0.4 real fork smoke

Only after that exact R0.2 proof validates, the runner invokes the existing current-source R0.4 fork primitive with the exact R0.2 JSON and:

`training/farm/real_wof_fork_smoke.plan.json`

The bounded smoke has one reset root, two explicit branches, 8-frame horizons and two repetitions per branch:

- `neutral-8f`;
- `button0-4f-neutral-4f`.

No gameplay reward, semantic WOF address, search policy, best-branch selection or R0.5 behavior is introduced.

R0.4 PASS validation reuses the existing Recovery V2 published result/resume contract validator and then additionally requires:

- `PASS / FORK_SET_DETERMINISTIC`;
- `REAL_WOF_FORK`;
- `realWofProof = true`;
- deterministic complete branch set;
- exact fork plan authority;
- exact current R0.4 fork source candidate/files;
- exact current ROM/Farm identity;
- accepted exact R0.2 `runId` and runtime identity SHA;
- no resume reuse in this Owner smoke.

Malformed, partial, skipped, non-deterministic, stale-source, wrong-proof-scope or wrong-ROM evidence cannot become final PASS.

## Local-only evidence bundle

Default external evidence root:

- Windows: `%LOCALAPPDATA%\WofTrainingFarm\real-proof\<UTC-run-id>\`
- Linux development: `$XDG_STATE_HOME/WofTrainingFarm/real-proof/<UTC-run-id>/` or `~/.local/state/...`

Every invocation creates a new unique run directory; previous/different ROM or source identities are not merged.

Compact output only:

```text
r0_2_real_determinism.json
r0_4_real_fork_smoke.json   # only if R0.4 ran
summary.json
summary.txt
```

The summary contains hashes/IDs/paths, not ROM or savestate bytes. Repository-internal evidence roots are rejected.

## Final Owner verdict contract

Human/machine output is unambiguous:

```text
PASS — R0.2 REAL WOF DETERMINISM + R0.4 REAL FORK SMOKE
WAITING_PREREQUISITE — <exact missing local prerequisite>
BLOCKED — R0.2 REAL DETERMINISM — <exact failure>
BLOCKED — R0.4 REAL FORK SMOKE — <exact failure>
```

`summary.json` records the evidence directory, R0.2 path/runId/runtime identity SHA and R0.4 path/runId/fork-set authority SHA when available.

## Source-drift protection

A source guard hashes the current R0.2/R0.4 implementation/schema/plan/Owner-runner surface before execution and rechecks it before/after proof stages. Source drift during an Owner run blocks instead of combining evidence from different candidates.

R0.2 also has to report the current Farm source candidate. R0.4 has to report the current fork source candidate. Historical RESULT hashes are not hard-coded as current authority.

## Implementation-owned self-check

Repository self-check source:

`training/farm/tests/test_real_wof_owner_runner.py`

It covers missing prerequisite, R0.2 non-PASS short-circuit, fixture PASS rejection, malformed R0.2 rejection, synthetic REAL-shaped orchestration double leading only to blocked R0.4 evidence, unique evidence directories, repository-local path detection and unambiguous final verdicts.

The available execution environment for this worker exposes GitHub content/mutations but no repository checkout and no legal WOF ROM. Direct network checkout from the local container is disabled. Therefore no real WOF execution was attempted and no fixture result was relabeled as real authority.

A compact isolated orchestration reconstruction using stubbed subprocess/result objects was executed once after implementation hardening. Result:

`11/11 PASS`

Covered cases:

1. missing prerequisite -> `WAITING_PREREQUISITE`;
2. fixture R0.2 PASS cannot unlock R0.4;
3. malformed R0.2 rejected;
4. R0.2 non-PASS stops R0.4;
5. R0.4 partial cannot PASS;
6. R0.4 non-deterministic cannot PASS;
7. R0.4 malformed cannot PASS;
8. exact local summary/evidence files produced;
9. repository-local evidence rejected;
10. second run creates a distinct evidence directory / no merge;
11. source drift fails closed.

This self-check is implementation evidence only. It is **not** a durable real-WOF proof.

## Real local proof status

`OWNER LOCAL RUN REQUIRED`

This worker did not possess or use a legal local WOF ROM and did not execute Stable-Retro/FBNeo real gameplay. Therefore:

- no R0.2 `REAL_WOF` PASS is claimed here;
- no R0.4 `REAL_WOF_FORK` PASS is claimed here;
- R0.5 remains unauthorized by this RESULT alone.

## Next legitimate gate after a real PASS

After the Owner command itself produces and preserves a validated:

`PASS — R0.2 REAL WOF DETERMINISM + R0.4 REAL FORK SMOKE`

PM may consume those exact local JSON authorities and separately authorize the next Training Farm stage. This RESULT does not define or implement R0.5 and does not guess a Reward/search/multi-worker contract that is not separately authorized.

## Scope confirmation

No changes were made to:

- `product/alpha/**`;
- Transport / Recorder / PYLAUNCH / OneClick product lane;
- WinKawaks Collector implementation/contracts/results;
- R0.5 Reward/search/multi-worker implementation;
- ROM/BIOS/emulator binary/copyrighted game assets.

## Stop condition

`COMPLETE — TRAINING FARM R0.4 REAL-WOF PROOF OWNER RUNNER PREP — OWNER LOCAL RUN REQUIRED`

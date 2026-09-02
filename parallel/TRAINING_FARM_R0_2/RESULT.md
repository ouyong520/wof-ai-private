# WOF Training Farm R0.2 — Single-Instance Determinism Result

Date: 2026-09-02
Stage: `TRAINING_FARM_R0_2_SINGLE_INSTANCE_DETERMINISM_V1`
Dedup key: `training.farm.r0.2.single-instance-determinism`
Repository status: **MODULE IMPLEMENTED — OWNER LOCAL REAL-WOF PROOF REQUIRED**

## Verdict

The complete R0.2 single-instance determinism module is implemented on top of the R0.1 Stable-Retro + FBNeo adapter. It now has strict runtime/ROM/source identity, real external ROM SHA-256 binding, exact savestate replay, explicit action/frame-horizon semantics, fail-closed comparison, structured JSON output/schema, an obvious CLI, compact module-owned self-checks, and R0.1 compatibility.

No real-WOF PASS is claimed. The execution environment used for this implementation has neither `stable-retro==0.9.8` installed nor `WOF_ROM_PATH` configured, so the real command correctly returned `SKIP / RUNTIME_PREREQUISITE_UNAVAILABLE` with exit code `2`.

## Exact candidate

Training Farm R0.2 source candidate commit:

`3bfa08a5528028ca4733b6e98f274c7385fc37bd`

Current `main` was re-read at `2051f33ff82fee7bad16ab778868e941db8e7026`. The only commit after the R0.2 candidate was an unrelated Alpha PM authorization file; no `training/farm/**` blob changed.

Exact current R0.2 blobs:

- `training/farm/README.md` — `246ce9a0d199fb9eab8c19c274f778e1df4116c4`
- `training/farm/__init__.py` — `0af58f30065a9143b6de1ed939d8b9e9d557c15d`
- `training/farm/adapter.py` — `9b6f0eace26fc1fe63b8b9aa1b81be1d8135ef6b`
- `training/farm/fake_backend.py` — `c3050be40d37471cce25d1fd4cfb45dad7564eae`
- `training/farm/stable_retro_backend.py` — `d6d618e8ca8708c4e8850327655a4593e26ab839`
- `training/farm/identity.py` — `9bfa117478b381ec5ac0ff21f02a1363c3271148`
- `training/farm/determinism.py` — `7cedcd78fe21835b8cc674c2ad781676146984d5`
- `training/farm/determinism.schema.json` — `22e0a25065f2d03864d759d9a3e01b187fe22462`
- `training/farm/determinism_actions.example.json` — `ff273d576c8ecb8b3ef9db1805d142b7d408a3c0`
- `training/farm/tests/test_contract.py` — `5349a5dea05e6e1a79b61d9d27213ce86d9a393c`
- `training/farm/tests/test_determinism.py` — `7df0d6977f0b7e6cc6d40c5e514dbdf4a3ead675`

The Farm runtime/source identity calculated from the module-owned identity files during the final fixture run was:

`farmCandidateSha256 = c7cba14a0f050f6faa0b101b8c97ad6a0776f5d1ae43ed91dc0039ec58022b7d`

## Implemented surface

### Runtime / ROM / source identity

- source namespace is exactly `stable-retro-fbneo`;
- records pinned and observed Stable-Retro version;
- records OS, release, machine, Python implementation/version/executable and process ID;
- real runs hash the legal local external ROM with SHA-256 in place and never serialize ROM bytes;
- hashes the R0.2 Farm runtime/schema source set into one candidate identity;
- records backend/core identity and a reliable FBNeo button-declaration hash;
- validates identity with exact keys and strict, non-coercive types;
- recomputes identity through the replay and invalidates evidence on runtime/core/ROM/source drift.

### Deterministic replay

- resets one emulator instance and saves one starting savestate;
- hashes starting savestate and starting RAM;
- restores that exact savestate before every required repetition;
- requires restored RAM and a load/save savestate roundtrip to match the original hashes;
- executes the same explicit action sequence to the exact frame horizon;
- records a RAM SHA-256 checkpoint every emulated frame plus final RAM SHA-256;
- compares repetitions exactly and reports the first divergent frame/action step when known;
- missing repetition, frame-count mismatch, state mismatch, load/save/RAM/action failure, malformed identity, or identity drift cannot produce PASS.

### Action / frame contract

R0.2 adds `CoreFrameInput` and `TrainingFarmAdapter.step_frame(...)`. Every replay frame sets all four emulator-player masks explicitly before one core step. Neutral input is an explicit empty pressed-button tuple/JSON array; no host key persistence or wall-clock timing is replay authority.

Player/button/frame/horizon/repetition values reject booleans, strings, floats, partial player sets, duplicates, or other coercible malformed values.

### JSON / CLI

Primary command:

```bash
python -m training.farm.determinism --actions training/farm/determinism_actions.example.json --horizon 8 --repetitions 3
```

ROM-free implementation fixture:

```bash
python -m training.farm.determinism --fake --actions training/farm/determinism_actions.example.json --horizon 8 --repetitions 3
```

Results use `wof-training-farm-determinism-result-v1` and distinguish `PASS`, `FAIL`, `SKIP`, and `ERROR`, including `reasonCode`, identity, action-sequence identity, start-state/RAM hashes, per-repetition checkpoints, and `firstDivergence`.

Fixture output is always `proofScope = IMPLEMENTATION_FIXTURE` and `realWofProof = false`; it is not real-WOF proof.

## Commands actually run against the final candidate

```bash
python -m compileall -q training
python -m unittest discover -s training/farm/tests -v
python -m training.farm.determinism --fake --actions training/farm/determinism_actions.example.json --horizon 8 --repetitions 3
python -m training.farm.smoke
python -m training.farm.probe
python -m training.farm.determinism --actions training/farm/determinism_actions.example.json --horizon 8 --repetitions 3
```

Observed compact result:

- compileall: PASS;
- module-owned unittest discovery: **13/13 PASS**;
- fake repeated replay: `PASS / DETERMINISM_MATCH`, 3/3 repetitions, 8/8 frames each, `realWofProof=false`;
- action sequence SHA-256: `bea11229c7d8870be303231ff2d8dd77414404b4e311ca66ae09fa5382bf51ec`;
- fixture runtime identity SHA-256: `cc2a34ee97b765d2aa449f442275ba46e4d17b15f77dd9d0753824e7d3fb2cad`;
- starting savestate SHA-256: `d4817aa5497628e7c77e6b606107042bbba3130888c5f47a375e6179be789fbb`;
- fixture final RAM SHA-256: `27cd350c43c5db9273bc688b5323f6d36d78e7f5807e584c502bd58c935f9363`;
- R0.1 smoke compatibility: PASS;
- structured fake PASS and structured real-runtime SKIP both validate against `determinism.schema.json`;
- environment probe: Linux / Python `3.13.5`, Stable-Retro absent, ROM not configured, runtime-ready false;
- real R0.2 command: `SKIP / RUNTIME_PREREQUISITE_UNAVAILABLE`, exit `2`, `realWofProof=false`.

The fail-closed self-checks specifically exercise deterministic mismatch/first-divergence reporting, mid-run identity change, malformed identity, coercible contract rejection, load failure, savestate roundtrip hash mismatch, explicit neutral input, and horizon mismatch.

## Real WOF availability / Owner action

Real local WOF runtime was **not available** in this execution environment:

- `stable-retro==0.9.8`: not installed;
- `WOF_ROM_PATH`: not set;
- legal local ROM bytes: not available to this worker and not copied/uploaded.

Remaining Owner action is only the real single-instance proof:

1. install the pinned dependency from `training/farm/requirements-r0.1.txt`;
2. set `WOF_ROM_PATH` to a legally obtained external WOF `.zip` outside the repository;
3. run the R0.2 real command above;
4. preserve its structured JSON result.

## Scope boundary preserved

This stage did not modify `product/alpha/**`, Alpha release/proof logic, Transport, Recorder, PYLAUNCH, OneClick, or WinKawaks Collector. It did not add Browser/WinKawaks input, observation-address calibration, PPO/SB3/RL, route search, dataset expansion, or 2/4/8/10-worker orchestration.

## Precise next legitimate Farm gate

The next legitimate Training Farm gate is **one legal local WOF + pinned Stable-Retro/FBNeo R0.2 determinism run producing a real `PASS / DETERMINISM_MATCH` bound to the actual ROM/runtime/source identity**.

Do not advance to multi-worker scaling from fixture PASS alone.

## Stop condition

**COMPLETE — TRAINING FARM R0.2 SINGLE-INSTANCE DETERMINISM MODULE IMPLEMENTED — OWNER LOCAL REAL-WOF PROOF REQUIRED**

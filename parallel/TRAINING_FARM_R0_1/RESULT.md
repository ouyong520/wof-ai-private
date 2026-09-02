# WOF Training Farm R0.1 — Stable-Retro + FBNeo Bootstrap Result

Date: 2026-09-02
Stage: `TRAINING_FARM_R0_1_STABLE_RETRO_FBNEO_BOOTSTRAP_V1`
Dedup key: `training.farm.r0.1.stable-retro-fbneo-bootstrap`
Repository status: **BOOTSTRAP READY FOR LOCAL WOF PROOF**

## Verdict

The narrow repository bootstrap is complete. A reusable single-instance adapter/host boundary now exists under `training/farm/**`, with deterministic ROM-free contract/error-path smoke and an optional explicit local WOF runtime probe.

This result does **not** claim that real WOF + FBNeo execution has already passed deterministic one-instance proof. The execution environment used for this stage had neither the pinned Stable-Retro runtime installed nor a legal local WOF ROM configured, so the real runtime probe correctly remained `SKIP`.

## Implemented surface

The project-owned thin boundary is `TrainingFarmAdapter` with:

- `reset()`
- `step(CoreAction(...))`
- `read_ram()`
- `save_state()`
- `load_state(state)`

The real backend is `StableRetroFbneoBackend`:

- consumes Stable-Retro rather than vendoring/forking an emulator;
- supplies an external filesystem ROM path directly to Stable-Retro `RetroEmulator`;
- relies on Stable-Retro's `.zip -> FBNeo` core mapping;
- sends per-frame player input through `RetroEmulator.set_button_mask(...)`;
- reads the RAM blocks exposed through `GameData.memory.blocks` in sorted-address order;
- uses `RetroEmulator.get_state()` / `set_state()` for state serialization/unserialization;
- remains one emulator instance only for R0.1.

There is no global keyboard/focus injection path in this bootstrap.

## ROM / binary boundary

Runtime ROM configuration is only through the external absolute path environment variable:

`WOF_ROM_PATH`

The probe rejects repository-local paths for real runtime readiness. `training/farm/.gitignore` also blocks common ROM/BIOS/state/core-binary forms and local `roms/` / `bios/` directories.

No ROM, BIOS, copyrighted game data, Stable-Retro/FBNeo source tree, or third-party emulator binary was added by this stage.

## Dependency / environment assumptions

Recorded R0.1 assumptions:

- Python: `3.10..3.14`
- Stable-Retro: `0.9.8` pinned by `training/farm/requirements-r0.1.txt`
- target OS for this bootstrap: Windows or Linux
- FBNeo arcade ROM input: external `.zip` path
- Stable-Retro package import: `stable_retro`

The repository does not automatically install dependencies. The environment probe reports exact readiness/failure reasons before a runtime attempt.

## Repository smoke evidence

Commands executed against the authored bootstrap content:

```bash
python -m compileall -q training
python -m unittest training.farm.tests.test_contract -v
python -m training.farm.smoke
python -m training.farm.probe
python -m training.farm.probe --runtime
```

Observed results:

- `compileall`: PASS
- unittest: **4/4 PASS**
- contract exercised: `reset / step / read_ram / save_state / load_state`
- deterministic save/load replay: PASS
- malformed savestate fail-closed: PASS
- closed-adapter fail-closed: PASS
- coercible/invalid action types rejected: PASS
- external-path configuration boundary: PASS
- deterministic replay RAM SHA-256: `c6176ba6ade1047d4f8eada39d819c4b586d8839cd505b0e2ccc9662fff209ad`

Execution environment observed:

- platform: Linux
- Python: `3.13.5`
- Stable-Retro installed: no
- `WOF_ROM_PATH`: not set
- ordinary dependency probe: reports not runtime-ready without failing repository smoke
- explicit `--runtime` probe: `SKIP`, exit code `2`

Missing Stable-Retro/ROM is therefore treated as an expected local-runtime prerequisite gap, not as a repository implementation defect.

## Real one-instance probe contract

When a legal local WOF ROM and the pinned dependency are available, the optional runtime probe performs only:

1. create one Stable-Retro/FBNeo instance;
2. reset;
3. snapshot exposed RAM;
4. save state;
5. run one neutral input frame through the emulator API;
6. load the saved state;
7. require restored RAM to equal the reset RAM snapshot.

That future local run is the first real WOF runtime evidence. It is intentionally not replaced by the fake deterministic backend.

## Scope exclusions preserved

This stage did not add or run:

- PPO / SB3 / neural-network training;
- 10 workers or any multi-worker orchestration;
- safe-route search;
- Browser/WOF release proof;
- player-facing input injection.

This stage did not intentionally modify `product/alpha/**`, Transport, HUDANCHOR, or V1 release-gate/proof behavior. During execution, another concurrent PM thread added unrelated release-gate prompt/claim files to `main`; those are not part of this stage's implementation or verdict.

## Limitations / next gate

Real WOF deterministic behavior, actual FBNeo RAM exposure for the local WOF romset, state restoration, and frame/input behavior remain **unverified in this environment** because no legal local ROM and no installed Stable-Retro runtime were available here.

The next legitimate gate is exactly one legal local WOF instance using `python -m training.farm.probe --runtime`. Do not advance to 2/4/8/10 workers or route/training work from this result alone.

## Stop condition

**COMPLETE — TRAINING FARM R0.1 STABLE-RETRO/FBNEO BOOTSTRAP — READY FOR LOCAL WOF ONE-INSTANCE PROOF**

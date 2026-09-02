# WOF Training Farm R0.1 — Stable-Retro + FBNeo bootstrap

This directory is an isolated internal R&D bootstrap. It is **not** part of
`product/alpha/**`, does not ship ROMs/BIOS, and contains no PPO/SB3, multi-worker
training, safe-route search, or player-input injection.

## R0.1 API

`TrainingFarmAdapter` exposes the required thin boundary:

- `reset()`
- `step(CoreAction(...))`
- `read_ram()`
- `save_state()`
- `load_state(state)`

The real backend uses Stable-Retro's low-level `RetroEmulator` directly. For a
`.zip` ROM path Stable-Retro selects the FBNeo core. Input is applied with
`RetroEmulator.set_button_mask(...)`; there is no OS/global keyboard path.
RAM is the sorted concatenation of the memory blocks exposed through
`GameData.memory.blocks`, matching Stable-Retro's `RetroEnv.get_ram()` ordering.
Savestates use `RetroEmulator.get_state()` / `set_state()`.

## Legal/local ROM boundary

Set a local external path only:

```text
WOF_ROM_PATH=/absolute/path/to/your/legally-obtained/wof.zip
```

Do not copy ROMs, BIOS files, copyrighted game data, or third-party binaries
into this repository. R0.1 does not download or import a ROM and does not hash
or identify a copyrighted ROM set. Any support files required by a local runtime
must remain outside the repository as well.

## Runtime assumptions

R0.1 records these narrow assumptions:

- Python 3.10 through 3.14.
- `stable-retro==0.9.8`.
- Windows or Linux for the FBNeo path.
- FBNeo arcade input/state/RAM is consumed through Stable-Retro.
- A local arcade romset is a `.zip`, which Stable-Retro maps to FBNeo.

Install only when doing a local emulator probe:

```bash
python -m pip install -r training/farm/requirements-r0.1.txt
```

If a wheel is not available for the local interpreter/platform, follow the
Stable-Retro upstream source-build prerequisites rather than committing build
products here.

## ROM-free deterministic smoke

This is the repository gate and requires no ROM or Stable-Retro installation:

```bash
python -m unittest training.farm.tests.test_contract -v
python -m training.farm.smoke
```

The fake backend exists only to exercise the adapter contract, deterministic
save/load replay, configuration boundary, and error paths. It is not evidence
that real WOF/FBNeo execution is deterministic.

## Environment/dependency probe

```bash
python -m training.farm.probe
```

The command reports Python/platform, Stable-Retro version, FBNeo declaration
and `.zip` mapping when the dependency is installed, plus `WOF_ROM_PATH`
status. Missing ROM is reported but is **not** an R0.1 repository-smoke failure.

## Explicit one-instance local WOF probe

Only on a machine that already has a legal local WOF ROM:

```bash
set WOF_ROM_PATH=C:\path\to\wof.zip
python -m training.farm.probe --runtime
```

Linux:

```bash
export WOF_ROM_PATH=/path/to/wof.zip
python -m training.farm.probe --runtime
```

The runtime probe performs one instance only: reset, RAM snapshot, savestate,
one neutral frame, restore, and RAM equality check. It does not train, does not
spawn workers, and does not search routes.

A missing dependency/ROM causes the explicit runtime probe to return `SKIP`
(exit 2), not to rewrite the repository bootstrap verdict.

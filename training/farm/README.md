# WOF Training Farm R0.1 — Stable-Retro + FBNeo bootstrap

This directory is an isolated internal R&D bootstrap. It is **not** part of
`product/alpha/**`, does not ship ROMs/BIOS, and contains no PPO/SB3, multi-worker
training, safe-route search, or player-input injection.

## Project-line isolation — Owner policy

Training Farm / `10训` is an **independent non-blocking R&D side lane**. It may
continue development, deterministic-runtime proof, savestate experiments,
trajectory/search tooling, and later multi-worker scaling in parallel with Alpha
V1 and WinKawaks Collector, but it is not part of the Alpha V1 release-critical
path unless Owner explicitly changes that policy in a later PM authority document.

Hard project-management rule:

```text
Training Farm incomplete / ACTIVE / BLOCKED / awaiting QA
!= Alpha V1 release blocker
!= reason to stop or delay bounded real Browser/WOF acceptance
!= WinKawaks Collector blocker
!= reason to stop or delay Collector development/capture
```

Default Training Farm write ownership is limited to:

```text
training/farm/**
Training-Farm-owned tests / docs / schemas / claims / RESULT metadata
```

Without explicit Owner authority, Training Farm work must not modify, block,
refactor, or take ownership of:

```text
product/alpha/**
Alpha danger rules or target semantics
Browser/WOF production projection/proof authority
Transport / Recorder / PYLAUNCH / OneClick
Alpha acceptance or release gates
WinKawaks Collector code/config/contracts/results
Collector read-only/input-safety semantics
```

If a Training Farm task discovers that a cross-line change is required, it must
**fail closed**: mark that Training Farm task `BLOCKED`, report the exact external
dependency, and leave the other project line unchanged. It must not make an
opportunistic cross-line edit just to make the Farm task pass.

Runtime authority is also isolated. Browser/WASM, WinKawaks, and
Stable-Retro/FBNeo numeric addresses, layouts, lifecycle identities, timing
assumptions, and calibrations are not interchangeable. Training Farm memory
semantics must be independently proven in its own runtime and durable Farm data
must identify its source as `stable-retro-fbneo`.

Training Farm input remains inside emulator/core APIs only. Permission to automate
input in this isolated training runtime does not grant permission to add
SendInput/global keyboard injection, autonomous input to the live Browser product,
or gameplay input to WinKawaks Collector.

The only intended interaction with the other lanes is operational resource
scheduling on the same physical machine. Heavy 2/4/8/10-worker Farm runs should
be paused or capped while a critical Alpha acceptance run or canonical long
WinKawaks capture needs stable CPU/RAM/I/O/cadence. That is a machine-resource
precaution only; it does **not** create a project dependency or release gate.

Project-wide runtime/data-source authority remains governed by
`RUNTIME_DATA_SOURCE_BOUNDARIES.md`.

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
set WOF_ROM_PATH=C:\\path\\to\\wof.zip
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

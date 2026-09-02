# WOF Training Farm R0.2 — single-instance determinism

This directory is the isolated Stable-Retro + FBNeo Training Farm lane. R0.2
extends the R0.1 one-instance bootstrap with a strict determinism module:

```text
same savestate + same explicit action sequence + same frame horizon
-> same observable result
```

R0.2 remains an internal R&D module. It is not Alpha V1, is not WinKawaks
Collector, and contains no PPO/SB3, route search, dataset expansion, or
multi-worker orchestration.

## Lane and authority boundary

Training Farm / `10训` is an independent non-blocking R&D side lane. Its runtime
authority is `stable-retro-fbneo`. Browser/WASM and WinKawaks numeric offsets,
runtime identities, timing assumptions, and lifecycle authority are not imported
as if they applied to Stable-Retro/FBNeo.

Training Farm input is allowed only through emulator/core APIs. This directory
contains no OS/global keyboard path, `SendInput`, focus automation, Browser input,
or WinKawaks input.

The Farm may not modify or block:

```text
product/alpha/**
Alpha release/proof gates
Transport / Recorder / PYLAUNCH / OneClick
WinKawaks Collector code/contracts/results
```

Project-wide provenance rules remain governed by
`RUNTIME_DATA_SOURCE_BOUNDARIES.md`.

## Reused R0.1 single-instance adapter

`TrainingFarmAdapter` still exposes the R0.1-compatible boundary:

- `reset()`
- `step(CoreAction(...))`
- `read_ram()`
- `save_state()`
- `load_state(state)`

R0.2 adds:

- `step_frame(CoreFrameInput(...))`
- backend runtime/core identity components

`step_frame` is the determinism path. It sets the input mask for **all four
players before one emulator frame advances**. A neutral player is represented by
an explicit empty `pressed` list; omitted players are rejected.

The real backend remains `StableRetroFbneoBackend`, using one Stable-Retro
`RetroEmulator` and the `.zip -> FBNeo` core mapping. It does not build a second
emulator stack.

## Runtime identity and ROM binding

Every real determinism comparison is bound to one strict runtime identity with:

- `sourceNamespace = stable-retro-fbneo`;
- pinned and observed Stable-Retro version;
- OS, release, machine, Python implementation/version/executable and process ID;
- real external ROM SHA-256;
- Farm candidate SHA-256 plus hashes of the module-owned runtime/schema files;
- backend name and reliable FBNeo core/button identity.

The ROM is hashed in place from the legal local external path. ROM bytes are
never copied into the result, repository, or source identity.

The identity is recomputed before/after replay repetitions. A runtime/core/ROM/
Farm-source identity change invalidates the run instead of merging evidence.

## Action sequence and frame horizon contract

The CLI consumes canonical JSON. Each sequence step has:

```json
{
  "frames": 2,
  "inputs": [
    {"player": 0, "pressed": [0]},
    {"player": 1, "pressed": []},
    {"player": 2, "pressed": []},
    {"player": 3, "pressed": []}
  ]
}
```

Rules are fail-closed:

- `frames`, `player`, button indices, horizon, and repetition count are strict
  integers; booleans, strings, floats and boxed/coercible equivalents are not
  accepted by the internal contract;
- every step lists players exactly in order `0,1,2,3`;
- neutral input is the explicit empty `pressed` array;
- sequence frame counts must sum exactly to the declared horizon;
- horizon is `1..100000` frames;
- repetitions are `2..100`;
- frame progression is driven only by emulator steps, never wall-clock timing.

`training/farm/determinism_actions.example.json` is a ROM-free example covering
8 frames.

## Deterministic replay primitive

For one run, R0.2:

1. resets one instance;
2. saves one starting savestate and hashes it;
3. records starting RAM SHA-256;
4. before every repetition, verifies bound identity and loads the exact same
   starting savestate;
5. requires restored RAM to match starting RAM;
6. re-saves the restored state and requires the savestate SHA-256 to match;
7. executes the exact same explicit action sequence to the exact frame horizon;
8. records a RAM SHA-256 checkpoint for every emulated frame and final RAM hash;
9. verifies identity again after the repetition;
10. compares every repetition exactly and reports the first divergent frame when
    known.

A PASS is impossible when identity is malformed/partial, a savestate hash or
restored RAM differs, load/save/RAM/action fails, frame count differs, or required
repetitions are missing.

## Structured result

The CLI writes JSON to stdout and optionally to `--output`.

Schema:

```text
training/farm/determinism.schema.json
```

Important fields include:

- `runId`;
- `status`: `PASS | FAIL | SKIP | ERROR`;
- `reasonCode`;
- `proofScope`;
- `realWofProof`;
- repetition count and frame horizon;
- canonical action sequence and its SHA-256;
- strict runtime identity and identity SHA-256;
- starting savestate/RAM SHA-256;
- per-repetition per-frame RAM checkpoints and final RAM SHA-256;
- `firstDivergence`.

Meaning:

- `PASS / DETERMINISM_MATCH`: all required observables matched;
- `FAIL / DETERMINISM_MISMATCH`: replay observables diverged;
- `SKIP / RUNTIME_PREREQUISITE_UNAVAILABLE`: pinned real runtime or legal local
  ROM is unavailable;
- `ERROR`: malformed contract, identity invalidation, save/load/RAM/action error,
  frame-count error, or other fail-closed runtime defect.

Fake-backend PASS is always marked:

```text
proofScope = IMPLEMENTATION_FIXTURE
realWofProof = false
```

It is implementation evidence only and is never a real-WOF determinism proof.

## Legal/local ROM boundary

Configure a legal local ROM outside the repository:

Windows:

```bat
set WOF_ROM_PATH=C:\path\to\wof.zip
```

Linux:

```bash
export WOF_ROM_PATH=/path/to/wof.zip
```

Do not copy ROMs, BIOS files, copyrighted game data, savestates, emulator cores,
or third-party binaries into this repository. `training/farm/.gitignore` blocks
common local ROM/BIOS/state/core-binary forms.

R0.2 hashes the local ROM **only for identity binding**. The JSON report stores
the SHA-256 digest, never ROM bytes.

## Runtime assumptions

Current pin remains:

```text
stable-retro==0.9.8
Python 3.10..3.14
Windows or Linux
FBNeo for external arcade .zip ROM
```

Install only for a legal local emulator run:

```bash
python -m pip install -r training/farm/requirements-r0.1.txt
```

## R0.2 commands

### Real single-instance determinism run

With `WOF_ROM_PATH` set and the pinned runtime installed:

```bash
python -m training.farm.determinism \
  --actions training/farm/determinism_actions.example.json \
  --horizon 8 \
  --repetitions 3
```

On Windows `cmd.exe`, put the command on one line or use `^` line continuation.

If prerequisites are unavailable, the same command returns structured `SKIP`
and exit code `2`. It must not claim PASS.

### ROM-free implementation self-check

```bash
python -m compileall -q training
python -m unittest discover -s training/farm/tests -v
python -m training.farm.determinism \
  --fake \
  --actions training/farm/determinism_actions.example.json \
  --horizon 8 \
  --repetitions 3
```

The fake command returns PASS only for the module control flow and deterministic
fixture.

### R0.1 compatibility probes

The prior probes remain available:

```bash
python -m training.farm.probe
python -m training.farm.probe --runtime
python -m training.farm.smoke
```

R0.1 `probe --runtime` remains a narrow one-frame save/load probe; the R0.2
`determinism` command is the full repeated replay authority.

## Exit codes

For `python -m training.farm.determinism`:

- `0`: PASS;
- `1`: FAIL or ERROR;
- `2`: real runtime prerequisite unavailable (`SKIP`).

## R0.2 scope stop

R0.2 intentionally stops at one instance and deterministic replay. Do not infer
authorization for:

- 2/4/8/10 worker orchestration;
- observation-address calibration;
- PPO/SB3/RL;
- route/search-teacher implementation;
- dataset expansion;
- Browser/WOF or WinKawaks input automation.

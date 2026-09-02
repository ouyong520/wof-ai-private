# WOF Training Farm R0.3 — observation discovery tooling prep

This directory is the isolated Stable-Retro + FBNeo Training Farm lane. R0.3
extends the completed R0.2 single-instance determinism module with preparation
tooling for controlled, address-aware observation discovery.

R0.3 does **not** prove any WOF semantic address. It does not claim a candidate is
`playerHp`, `playerX`, `playerY`, enemy state/slot, camera, attack ID, lifecycle,
or any other gameplay field. It only produces evidence-ranked candidate
locations for a later real-runtime mapping stage.

The source namespace remains exactly:

```text
stable-retro-fbneo
```

Browser/WASM and WinKawaks offsets, host addresses, runtime identities and timing
assumptions are not imported into this lane.

## Project boundary

Training Farm is an independent non-blocking R&D lane. R0.3 does not modify or
take ownership of:

```text
product/alpha/**
Alpha release/proof gates
Transport / Recorder / PYLAUNCH / OneClick
WinKawaks Collector code/contracts/results
```

There is still no PPO/SB3/RL, route search, dataset expansion, or 2/4/8/10-worker
orchestration in this module. Programmatic input remains inside the emulator/core
API only; there is no OS/global keyboard, SendInput, Browser input, focus
automation, or WinKawaks input path.

Project-wide provenance rules remain governed by
`RUNTIME_DATA_SOURCE_BOUNDARIES.md`.

## R0.1 / R0.2 compatibility

`TrainingFarmAdapter` preserves the existing boundary:

- `reset()`
- `step(CoreAction(...))`
- `step_frame(CoreFrameInput(...))`
- `read_ram()`
- `save_state()`
- `load_state(state)`
- `runtime_identity_components()`

R0.3 adds one source-specific observation primitive:

- `read_ram_blocks()`

R0.2 `read_ram()` remains the deterministic flat RAM fingerprint. R0.3
`read_ram_blocks()` returns stable ordered `RamBlockSnapshot` values containing:

- exact non-negative integer block/base key exposed by the backend;
- exact bytes in that block;
- exact block byte length.

The adapter rejects malformed, duplicate/out-of-order, or overlapping block
metadata fail-closed.

## Stable-Retro address provenance

For the real backend, `StableRetroFbneoBackend.read_ram_blocks()` preserves the
integer keys exposed by:

```text
GameData.memory.blocks
```

Those keys are the strongest address-aware facts this backend currently obtains
from Stable-Retro. R0.3 records them exactly and calls a candidate's native
location:

```text
Stable-Retro memory-block key + byte offset within that block
```

That does **not** imply the value equals a Browser/WASM address, WinKawaks host
address, operating-system address, or any other runtime's address space. R0.3
will report that limitation rather than inventing an equivalence.

## Memory-layout identity

Every controlled experiment binds its RAM layout to:

- `sourceNamespace = stable-retro-fbneo`;
- ordered block base keys and lengths;
- canonical layout-shape SHA-256;
- current R0.2 runtime identity SHA-256;
- ROM SHA-256 / fixture marker from that runtime identity;
- R0.2 Farm candidate/source identity;
- R0.3 observation-discovery candidate/source identity.

Any runtime, ROM, R0.2 source, R0.3 source, or layout change during capture fails
closed. Results from different identities are not merged.

## Strict experiment plan

Plan schema:

```text
training/farm/observation_plan.schema.json
```

Example:

```text
training/farm/observation_plan.example.json
```

A plan contains exactly:

- `experimentId`;
- `startingSavestateId`;
- optional expected starting-savestate SHA-256;
- one baseline action sequence;
- one or more named intervention action sequences;
- exact `horizonFrames`;
- `repetitions`;
- exact `captureFrames`;
- optional `semanticLabel` / `hypothesis` metadata.

Player, button, frame, repetition and checkpoint values are strict integers.
Booleans, strings, floats and coercible replacements are rejected. Every action
step reuses R0.2's explicit all-four-player frame input, including explicit empty
pressed-button arrays for neutral input. Capture frames must be strictly
increasing, unique, inside the horizon and include the final horizon frame.

`semanticLabel` and `hypothesis` are human notes only. They never become address
authority.

## Controlled same-savestate capture

For one observation run the tool:

1. creates one adapter/emulator instance;
2. resets it once and saves one starting savestate;
3. records the exact starting savestate SHA-256 and address-aware RAM snapshot;
4. records the bound runtime/ROM/source/layout identity;
5. before every baseline/intervention repetition, restores the exact same state;
6. requires the save/load roundtrip and restored address-aware RAM to match;
7. advances only by exact emulator frames using R0.2 full-frame inputs;
8. captures only the requested address-aware checkpoint frames;
9. rechecks runtime/source/layout identity through the experiment;
10. analyzes only after all required controlled captures complete.

Wall-clock timing is not frame authority.

Large raw captures and savestates are not written into the repository by this
command. The normal JSON result contains compact checkpoint hashes and ranked
candidate evidence; local raw runtime material remains local-only.

## Candidate-change analysis

R0.3 emits **candidate offsets only**, never semantic truth. For changed locations
it analyzes bounded byte candidates and adjacent two-byte little-endian windows
where possible. Each candidate records, among other evidence:

- source block index/base and length;
- offset within block;
- `sourceNativeAddress = blockBaseAddress + offsetWithinBlock`;
- address provenance string;
- width and analysis-only encoding;
- baseline values and intervention values observed at checkpoints;
- changed/stable comparison counts across repetitions;
- baseline/intervention repetition stability;
- first/last observed changed frame;
- baseline-control temporal change count;
- whether baseline/control also changed and therefore the candidate was
  downgraded;
- deterministic evidence-only consistency score.

Ranking is deterministic. Equal evidence prefers the narrower byte candidate
before a word window, then stable address order. This is a discovery heuristic,
not a declaration of data type or gameplay meaning.

Analysis is bounded by default:

```text
maximum changed byte locations analyzed per intervention: 50,000
maximum ranked candidates serialized: 128
```

The output records when the bounded analysis was truncated.

## R0.2 real-proof gate

R0.3 repository tooling can be complete while real semantic mapping remains
locked. A real R0.3 capture is classified eligible only when the supplied R0.2
result passes a strict consumer gate requiring at minimum:

```text
schema = wof-training-farm-determinism-result-v1
status = PASS
reasonCode = DETERMINISM_MATCH
proofScope = REAL_WOF
realWofProof = true
sourceNamespace = stable-retro-fbneo
complete repetitions/checkpoints
valid action-sequence hash
valid starting-state/RAM hashes
strict real Stable-Retro/FBNeo runtime identity
matching ROM/runtime/core/source identity
```

The gate recomputes the R0.2 runtime-identity SHA and validates the internal proof
shape rather than trusting public labels alone.

### Cross-process compatibility rule

A saved R0.2 proof is normally produced by one CLI process and consumed by a later
R0.3 CLI process. Therefore the proof comparison requires every validated
runtime/ROM/source/backend identity field to match exactly **except `processId`**.
`processId` remains a required positive strict integer in both identities, but is
run-local and may differ across those two processes. No ROM/core/source field is
relaxed.

### Current-source consequence

R0.3 changes Farm adapter/backend source files that are part of the R0.2 Farm
candidate identity. Therefore a real R0.2 proof produced against an older Farm
source candidate is intentionally stale for current R0.3 eligibility. The Owner
must run R0.2 determinism again against the current source, then provide that
current proof JSON to R0.3.

The tool never fabricates or upgrades a fake R0.2 proof.

## Authority classifications

Every R0.3 result explicitly uses one of:

```text
IMPLEMENTATION_FIXTURE
REAL_RUNTIME_OBSERVATION_UNVERIFIED
REAL_RUNTIME_OBSERVATION_ELIGIBLE
```

Meaning:

- `IMPLEMENTATION_FIXTURE`: ROM-free fake backend implementation evidence only;
- `REAL_RUNTIME_OBSERVATION_UNVERIFIED`: real Stable-Retro/FBNeo observation was
  captured but no accepted matching current R0.2 proof authorized semantic
  mapping;
- `REAL_RUNTIME_OBSERVATION_ELIGIBLE`: real runtime plus accepted matching R0.2
  proof; the result may proceed to the later real R0.3 semantic-mapping stage.

`semanticMappingUnlocked` is always `false` for fake fixtures. Synthetic/fake
results cannot upgrade themselves by supplying any proof-looking object.

Even when `REAL_RUNTIME_OBSERVATION_ELIGIBLE`, the candidate list itself is still
non-semantic discovery evidence. A later mapping stage must prove actual gameplay
meaning with controlled real scenes before naming fields.

## Structured output

Result schema:

```text
training/farm/observation_discovery.schema.json
```

Primary CLI:

```bash
python -m training.farm.observation_discovery \
  --plan training/farm/observation_plan.example.json
```

Optional real R0.2 proof:

```bash
python -m training.farm.observation_discovery \
  --plan /path/to/real-observation-plan.json \
  --r0-2-proof /path/to/current-r0.2-real-proof.json \
  --output /path/to/local-result.json
```

If Stable-Retro / legal local ROM prerequisites are missing, the real command
returns structured `SKIP / RUNTIME_PREREQUISITE_UNAVAILABLE` with exit code `2`.
It does not claim real observation authority.

ROM-free tooling fixture:

```bash
python -m training.farm.observation_discovery \
  --fake \
  --plan training/farm/observation_plan.example.json
```

The fixture intentionally contains synthetic address-aware blocks at `0x1000`
and `0x2000`. Those addresses exist only to exercise layout/diff/ranking code and
are not WOF addresses.

## R0.2 determinism command remains available

Real current-source R0.2 proof command, after configuring the legal local runtime:

```bash
python -m training.farm.determinism \
  --actions training/farm/determinism_actions.example.json \
  --horizon 8 \
  --repetitions 3 \
  --output /path/to/current-r0.2-real-proof.json
```

ROM-free R0.2 fixture remains:

```bash
python -m training.farm.determinism \
  --fake \
  --actions training/farm/determinism_actions.example.json \
  --horizon 8 \
  --repetitions 3
```

R0.1 compatibility probes remain:

```bash
python -m training.farm.probe
python -m training.farm.probe --runtime
python -m training.farm.smoke
```

## Legal/local ROM boundary

Configure only a legally obtained external `.zip` ROM outside this repository:

Windows:

```bat
set WOF_ROM_PATH=C:\path\to\wof.zip
```

Linux:

```bash
export WOF_ROM_PATH=/path/to/wof.zip
```

Current runtime pin remains:

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

Do not commit ROMs, BIOS files, copyrighted game data, savestates, emulator cores,
or third-party binaries. R0.2/R0.3 identity records SHA-256 values only; it does
not serialize ROM bytes.

## Compact implementation self-check

The module-owned repository check is intentionally narrow:

```bash
python -m compileall -q training
python -m unittest discover -s training/farm/tests -v
python -m training.farm.determinism \
  --fake \
  --actions training/farm/determinism_actions.example.json \
  --horizon 8 \
  --repetitions 3
python -m training.farm.observation_discovery \
  --fake \
  --plan training/farm/observation_plan.example.json
```

It covers layout preservation, strict experiment parsing, same-state replay,
candidate ranking, layout drift, strict R0.2 proof gating and fixture
non-escalation. This is implementation self-check evidence, not independent QA or
real WOF mapping proof.

## R0.3 stop boundary

This preparation module stops before:

- declaring any real WOF semantic RAM mapping;
- importing Browser/WinKawaks numeric offsets;
- multi-worker 2/4/8/10 orchestration;
- PPO/SB3/RL;
- route/search-teacher/safe-path implementation;
- Alpha/Browser or WinKawaks input automation.

Until a matching **current-source** real R0.2 proof exists, real R0.3 semantic
observation mapping remains locked.

# Training Farm R1 fleet runtime

Status: implementation-ready runtime layer; real-WOF authority is still gated
by the existing legal external ROM and pinned Stable-Retro/FBNeo preflight.

`training/farm/fleet.py` is the source-owned supervisor for real worker
processes. It reuses the existing `TrainingFarmAdapter`, `StableRetroFbneoBackend`,
R0.4 savestate fork contract, R0.4.5 policy boundary, and V11
`TrainingFarmReadOnlyExporter`.

## Runtime contract

```text
fleet supervisor
  -> worker-01..worker-10, one Stable-Retro/FBNeo instance per process
  -> worker identity + generation
  -> in-memory root savestate fork + action-result experiment
  -> heartbeat + best-effort CPU/RSS telemetry
  -> parent-serialized source-owned exporter publication
  -> existing Unified Collector stable-retro-fbneo adapter
```

The default staged ladder is:

```text
1 -> 2 -> 4 -> 8 -> 10
```

The supervisor owns start, clean stop, restart, scale-up, scale-down and
failure isolation. A failed worker is recorded and restarted within its bounded
restart budget; sibling workers are not terminated because one worker failed.

The parent process is the only exporter writer. Workers perform emulator/core
operations and send bounded evidence messages to the parent. This keeps the
existing registry/artifact format and avoids creating a second Collector data
plane or concurrent Windows registry writers.

## Safety and provenance

Every record remains:

```text
sourceNamespace = stable-retro-fbneo
readOnlyExporter = true
writesGameMemory = false
inputInjection = false
gameplayInputAuthority = emulator-core-api-only
```

Savestates are process-local in-memory bytes. They are forked and restored for
the experiment, but never written to the repository or committed. ROMs, BIOS,
emulator binaries and game assets are never created by the fleet.

Fleet metadata carries the fleet source identity, worker generation, fork-plan
authority, action-result trajectory, root savestate hash, memory-layout
identity, and resource timing. Stable-Retro memory-block keys remain local to
the `stable-retro-fbneo` namespace; no Browser/WASM or WinKawaks offset is
imported.

The `--fake` option is a deterministic implementation fixture only. A fake
10-worker run must never be reported as real 10训. Real mode returns
`WAITING_PREREQUISITE` without launching workers until `WOF_ROM_PATH` or
`--rom` points to an external legal FBNeo ZIP and the existing dependency probe
passes.

## Local commands

Fixture-only orchestration check:

```powershell
python -m training.farm.fleet --fake --workers 10 `
  --stage-seconds 0 --run-seconds 1 `
  --export-root "$env:TEMP\wof-fleet\exports" `
  --status-root "$env:TEMP\wof-fleet\status"
```

Real run after the existing Owner ROM/runtime gate is satisfied:

```powershell
python -m training.farm.fleet --workers 10 `
  --stage-seconds 30 --run-seconds 300 `
  --export-root "$env:LOCALAPPDATA\WofTrainingFarm\exports" `
  --status-root "$env:LOCALAPPDATA\WofTrainingFarm\fleet"
```

The Unified Collector remains the consumer. Point its existing V12 entrypoint
at the same local exporter root using `--training-farm-export-root`; it may
select `ONE`, explicit `WORKER_IDS`, or `ALL_ACTIVE` up to ten workers. It does
not start, stop, schedule, or inject actions into the farm.

Real 10-worker product completion still requires a bounded Owner-local run
with a legal ROM and observed Stable-Retro/FBNeo worker outputs. Fixture tests,
exporter records, and repository CI do not substitute for that proof.

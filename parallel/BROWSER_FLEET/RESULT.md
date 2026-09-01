# WOF Browser Fleet Manager — Result

Updated: 2026-09-01

Verdict: **REPOSITORY-SIDE READY — one bounded real Windows proof remains.**

This is project-acceleration tooling only. It does not modify Alpha product logic or attack research.

## Delivered

### One-click Windows fleet entry

`parallel/BROWSER_FLEET/RUN_WOF_FLEET.cmd`

First run only stores Browser preference and an optional WOF URL. Normal repeated owner path is:

`double-click CMD -> enter 1 / 5 / 10 -> browser windows launch automatically`

Default empty input means 10.

### Independent Browser isolation

Every numbered instance has its own:
- Chrome/Edge user-data/profile directory;
- localhost CDP port (`9323 + N - 1` by default);
- launch process entry;
- window rectangle;
- fleet manifest row.

No two fleet instances intentionally share a profile or CDP port.

### Window management

The manager calculates a primary-screen grid and passes independent window position/size for each launch.

Console commands:
- `S` refresh status;
- `R` restart one numbered instance;
- `X` close one numbered instance;
- `A` close all managed instances and exit;
- `Q` quit only the manager and leave browser windows running.

### Basic status

Per instance the Fleet console reports:
- Browser/CDP up/down;
- non-blank page presence;
- basic `gstyphoon*.js` Worker target presence;
- PID;
- profile id.

The Fleet Worker row is deliberately only a cheap status indicator. Authoritative Worker/WASM/heap/World-921031 proof remains PYLAUNCH's existing read-only CDP discovery path.

### Shared discovery registry

Default manifest:

`%LOCALAPPDATA%\WOF Future Danger\Fleet\instances.json`

Version:

`wof-browser-fleet-v1`

The registry includes instance id, localhost host/port, profile, PID, manager run id, layout and basic status plus fixed top-level safety declarations:
- `readOnly=true`;
- `ramWrites=0`;
- `inputInjection=false`;
- `windowWorkerReplacement=false`.

Consumers must independently re-probe listed CDP endpoints rather than trust stale status.

### PYLAUNCH discovery

Added `parallel/PYLAUNCH/wof_launcher/fleet.py` and CLI selection:

```bat
launcher.py --fleet-auto
launcher.py --fleet-instance N
```

Fleet selection is attach-only. Down/stale endpoints are ignored. Once selected, PYLAUNCH uses its existing authoritative read-only page / native Worker / WASM / heap / exact World-921031 probe.

The normal single-instance `9223` PYLAUNCH proof path is unchanged unless a Fleet flag is explicitly supplied.

### WOF-052L Recorder discovery

`RUN_WOF052L_RECORDER.cmd` now starts `fleet_recorder.py`.

If Browser Fleet entries exist:
- each Fleet CDP endpoint gets an independent `RecorderManager` thread/client;
- a child is pinned to its assigned endpoint and never falls across to another Fleet port;
- a browser/reload/disconnect affects only that child/session while other recorder workers continue;
- new manifest entries may join while supervisor is running;
- each child retains its normal per-room/checkpoint/merged JSON behavior;
- supervisor shutdown writes an additional fleet-level merged/index JSON.

If no Fleet entries exist, WOF-052L automatically falls back to the original single-CDP recorder path.

## Offline regression status

Completed during this implementation:
- Browser Fleet manager regression: **4/4 PASS**;
- PYLAUNCH fleet registry regression: **2/2 PASS**;
- Fleet recorder manifest/localhost/fail-open regression added;
- `fleet_recorder.py` syntax/static construction checked before commit.

Covered invariants include:
- 10-window grid is bounded/unique;
- fleet size/port guards;
- independent profile and port allocation;
- settings round-trip;
- manifest safety declarations;
- stale endpoint filtering in PYLAUNCH;
- first/numbered Fleet selection;
- localhost-only WOF-052L fleet entries;
- missing/wrong Fleet manifest fails open to the original recorder path.

## Safety review

Preserved:
- no `product/alpha/**` modification in this lane;
- no `window.Worker` replacement/wrap;
- no Blob Worker interception/URL rewrite;
- no game RAM writes;
- no keyboard/mouse/controller/gameplay input injection;
- no game speed control;
- no attack automation;
- localhost-only CDP exposure;
- Browser/game remains independent of manager/consumer attachment failures.

## Remaining real Windows proof — minimal

Only a real Windows Chrome/Edge run can prove process/window behavior and live native Worker exposure.

1. Double-click `parallel/BROWSER_FLEET/RUN_WOF_FLEET.cmd`.
2. First run only: choose Browser (`auto` is fine) and optionally store the real WOF URL.
3. Enter `10`.
4. Confirm 10 numbered browser instances/windows appear in a grid.
5. Enter WOF normally in at least two instances; press `S` and confirm their Browser/page rows become `OK` and Worker becomes `OK` when the native game Worker is exposed.
6. Use `R` on one instance. Confirm another running WOF instance is unaffected.
7. Optional integration proof: from PYLAUNCH run `launcher.py --fleet-instance 1 --no-tray` and confirm its existing Browser/page/Worker/WASM/World read-only status reaches the expected state.
8. Optional recorder proof: double-click `parallel/WOF052L_RECORDER/RUN_WOF052L_RECORDER.cmd`; confirm Fleet entries/recorder workers appear and one room can finalize without stopping another.
9. Return to Fleet console and press `A`; confirm all managed Fleet windows close.

No DevTools, Worker-console selection, pasted JavaScript, RAM inspection, gameplay capture, or injected input is required.

## Stop condition

The repository-side Browser Fleet Manager implementation is complete enough for the requested acceleration goal. Do not add more features before the bounded Windows proof unless that proof exposes a concrete defect.

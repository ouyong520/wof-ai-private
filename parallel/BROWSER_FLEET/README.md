# WOF Browser Fleet Manager

Status: repository-side tooling READY; one real Windows fleet proof remains.

This lane is project acceleration only. It launches multiple ordinary Chrome/Edge WOF browser instances without changing Alpha, replacing `window.Worker`, writing game RAM, or injecting gameplay input.

## Owner path

Double-click:

`RUN_WOF_FLEET.cmd`

First run only:
1. choose `auto`, `chrome`, or `edge`;
2. optionally paste the WOF page/room URL to remember it.

Every later run:
1. double-click the CMD;
2. enter `1`, `5`, `10`, or another count up to 50;
3. the tool launches that many isolated windows and arranges them on the primary screen.

The console numbers each instance and shows:
- Browser/CDP;
- page presence;
- basic `gstyphoon*.js` Worker presence;
- PID;
- profile name;
- permanent safety banner: `READ ONLY / RAM writes: 0 / input injection: NO / window.Worker replacement: NO`.

Interactive commands:
- `S` — refresh status;
- `R` — restart one numbered instance;
- `X` — close one numbered instance;
- `A` — close all managed instances and exit;
- `Q` — quit only the manager, leaving browser windows running.

## Isolation model

Each fleet member gets its own:
- `%LOCALAPPDATA%\WOF Future Danger\Fleet\Profiles\Fleet_XX` user-data directory;
- localhost CDP port (`9323 + instance_id - 1` by default);
- browser launch process;
- window rectangle;
- manifest entry.

No profile is shared between fleet members. One browser crash/reload does not intentionally stop or clear any other member.

The default port can be changed in the saved settings JSON if another local tool already uses the range.

## Discovery contract

The fleet writes:

`%LOCALAPPDATA%\WOF Future Danger\Fleet\instances.json`

Format version:

`wof-browser-fleet-v1`

Each live entry includes:
- `id`;
- `host`;
- `port`;
- `endpoint`;
- `profileDir`;
- `pid`;
- `managerRunId`;
- launch time / configured game URL;
- basic Browser/page/Worker status.

Top-level safety fields are always:
- `readOnly: true`;
- `ramWrites: 0`;
- `inputInjection: false`;
- `windowWorkerReplacement: false`.

`parallel/PYLAUNCH/wof_launcher/fleet.py` is the shared stdlib reader. PYLAUNCH can attach to the first live fleet endpoint with `--fleet-auto`, or a numbered endpoint with `--fleet-instance N`. WOF-052L can import the same reader and enumerate all live entries.

The Fleet Manager's Worker status is intentionally only a cheap HTTP target-list indicator. Authoritative Worker/WASM/heap/World-921031 validation stays in PYLAUNCH's existing read-only CDP probe.

## Commands

Direct start:

```bat
py -3 fleet_manager.py start 10 --interactive
```

One-off browser selection / URL:

```bat
py -3 fleet_manager.py start 5 --interactive --browser edge --game-url "https://YOUR-WOF-PAGE/"
```

Reconfigure remembered defaults:

```bat
py -3 fleet_manager.py configure
```

Print the current manifest:

```bat
py -3 fleet_manager.py status
```

## Safety / non-goals

This tool does not:
- modify `product/alpha/**`;
- replace or wrap `window.Worker`;
- create Blob Workers or rewrite Worker URLs;
- write game RAM;
- send keyboard/mouse/controller/gameplay inputs;
- alter game speed;
- inject attack logic;
- depend on Alpha bootstrap.

CDP exposure is localhost-only. The game/browser remains usable if the manager exits.

## Offline regression

From repository root:

```bat
py -3 -m unittest discover parallel\BROWSER_FLEET\tests -v
py -3 -m unittest discover parallel\PYLAUNCH\tests -v
```

Repository-side offline coverage checks window tiling, count/port guards, independent profile/port allocation, settings persistence, manifest safety fields, and fleet registry selection.

## Remaining real Windows proof

The only remaining Fleet proof is bounded:

1. double-click `RUN_WOF_FLEET.cmd`;
2. enter `10`;
3. confirm 10 windows appear and are tiled;
4. enter/join WOF normally in at least two windows (or use the remembered WOF URL);
5. press `S` and confirm each relevant row independently reaches Browser `OK`, page `OK`, and Worker `OK` when its room is running;
6. restart one instance with `R` and confirm the others stay running;
7. close all with `A`.

No DevTools, Worker-console selection, RAM inspection, or input injection is required.

# WOF Python Launcher Foundation

Status: foundation prototype, **READ ONLY**.

This lane implements the post-start launcher path requested by PM without modifying `product/alpha/**` or WOF-052. The browser/game creates its native `gstyphoon*.js` Worker normally. The launcher attaches afterwards through localhost Chrome/Edge DevTools Protocol (CDP), discovers the live page/Worker, finds the Emscripten/WASM module and heap, and verifies the authoritative **WOF / World 921031** 1 MiB CPU-logical SHA-256.

## Safety contract

- no `window.Worker` replacement or wrapping;
- no Tampermonkey dependency;
- no game RAM writes;
- no keyboard/mouse/gameplay input injection;
- no one-key moves, command injection, autoplay, or speed control;
- CDP method allowlist blocks `Input.*` and every method outside the small discovery/evaluation set;
- if CDP/browser attachment fails, only launcher status changes; the game is unaffected.

Foundation identity constant:

`5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62`

This is the repository's authoritative `wof / Warriors of Fate (World 921031)` full CPU-logical program hash. Reset vector / dispatch are only locator/sanity evidence.

## Why a dedicated browser profile is required

Chrome 136+ ignores `--remote-debugging-port` / `--remote-debugging-pipe` when they target Chrome's default data directory. The launcher therefore starts Chrome/Edge with a dedicated WOF profile plus localhost remote debugging. This is intentionally separate from the user's normal browser profile.

The launcher does **not** require the game Worker to be changed. The only browser requirement is that the browser instance itself expose CDP.

## Windows setup

Use 64-bit Python 3.11+. The smallest owner path is to double-click `RUN_WOF_LAUNCHER.bat` (or run it from a terminal). It creates `.venv`, installs the three small dependencies, and starts the tray launcher.

Manual equivalent:

```bat
cd parallel\PYLAUNCH
py -3 -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python launcher.py
```

Normal behavior:

1. the launcher attaches to `127.0.0.1:9223` if a compatible WOF browser is already running with CDP;
2. otherwise it starts Chrome/Edge with a dedicated `%LOCALAPPDATA%\WOF Future Danger\BrowserProfile` and CDP on localhost;
3. the owner enters WOF normally (or supplies `--game-url` so the launcher opens it);
4. the launcher polls target discovery, only considers `gstyphoon*.js` dedicated workers, and probes them read-only;
5. a unique Worker is accepted only after module/heap discovery and exact World 921031 SHA-256 verification;
6. tray status changes without taking focus from the game.

The browser keeps working if the launcher exits or fails to attach.

## Useful commands

Attach only to an already-debuggable browser:

```bat
.venv\Scripts\python launcher.py --attach-only
```

CLI status proof without tray:

```bat
.venv\Scripts\python launcher.py --no-tray
```

Choose Edge:

```bat
.venv\Scripts\python launcher.py --browser edge
```

Open a configured game URL in the dedicated debug profile:

```bat
.venv\Scripts\python launcher.py --game-url "https://YOUR-WOF-PAGE/"
```

## Tray UI

Single-click/default activation opens the status dialog where supported by the tray backend. Right-click the WOF tray icon for:

- Connection status;
- Browser;
- WOF page;
- Worker;
- WASM / heap;
- World 921031;
- permanent `READ ONLY / RAM writes: 0` indicator;
- Reconnect;
- Launch / Open game;
- Settings;
- Diagnostics / Logs;
- reserved Future Danger / HUD / Sound / Hotkeys rows;
- `Assist Mode (NOT IMPLEMENTED)`;
- About / Quit.

Settings opens a larger window only on demand. Closing it does not intentionally stop the launcher. The foundation uses a generated in-memory tray icon, so no image asset is required.

## Current proof boundary

Offline code/tests can prove the launcher is fail-closed, Worker-selective, exact-hash-gated, and contains no input or RAM-write path. This environment cannot prove a real Windows Chrome/Edge target exposes the same Worker/session behavior. The remaining owner proof is one bounded run described in `RESULT.md`.

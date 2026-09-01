# WOF Python Launcher — Windows Tray UI Requirements

Updated: 2026-09-01

## Product shape

The preferred user experience is a background Windows utility packaged toward a single `WOF Future Danger.exe`.

The launcher should not require a permanently open console or large main window. After startup it should live primarily in the Windows notification area/system tray at the bottom-right.

## Tray behavior

- one small WOF icon in the Windows tray;
- single-click may show a compact status panel if the chosen toolkit supports it cleanly;
- right-click must expose the main tray menu;
- Settings opens a larger configuration window only on demand;
- closing the settings window returns the app to tray rather than exiting;
- explicit Quit exits the launcher;
- tray icon should reflect connection state when practical: disconnected / connecting / connected / error;
- the game remains foreground; launcher UI must stay unobtrusive.

## Foundation-stage menu

The first read-only prototype should expose or reserve:

- Connection status
- WOF page found
- WOF Worker found
- WASM/module/heap found
- Build identity / World 921031 status
- Read-only mode indicator
- Reconnect
- Launch/Open game
- Settings
- Diagnostics / Logs
- About
- Quit

## Settings-window structure

Design the settings shell so later features can be added without redesigning the app. Suggested sections:

### General
- launch game / browser preference
- start minimized
- start with Windows (later)
- reconnect behavior

### Future Danger
- enable/disable warnings
- HUD enable/disable
- HUD options
- warning sound options

### Hotkeys
- reserved UI for future shortcuts
- no gameplay injection in the foundation stage

### Assist Mode — future only
- disabled/not implemented in foundation
- later home for one-key moves / command injection
- must be visually separate from read-only Future Danger mode

### Diagnostics
- browser/CDP status
- page target
- Worker target
- module/heap status
- build identity
- last reconnect/error
- read-only / RAM write counters

## Safety UX

The UI must make the operating mode obvious:

- `READ ONLY` should be visible in the foundation stage.
- A future `ASSIST MODE` must require explicit user activation and must not silently inherit from prior failures/restarts.
- If browser/Worker attachment fails, the tray may show an error/disconnected state, but the base game must remain unaffected.

## Packaging direction

Long term:
- single Windows EXE where practical;
- no visible Python console for normal users;
- tray icon starts automatically with launcher;
- dependencies bundled;
- settings stored locally with safe defaults;
- update mechanism can be added later.

## Current non-goals

Do not implement yet:
- RAM writes;
- input injection;
- one-key moves;
- command injection;
- autoplay;
- game-speed control.

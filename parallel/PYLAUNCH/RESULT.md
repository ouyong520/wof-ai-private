# WOF Python Launcher Foundation — Result

Date: 2026-09-01
Status: **FOUNDATION IMPLEMENTED; ONE REAL WINDOWS/BROWSER PROOF REMAINS**

## Proven from repository + offline implementation

- New code is isolated under `parallel/PYLAUNCH/**`; no `product/alpha/**` or WOF-052 modification.
- No Tampermonkey dependency.
- No `window.Worker` replacement, wrapper, Blob Worker, Worker URL rewrite, or page startup injection.
- Browser attachment is post-start through localhost CDP.
- Worker discovery is restricted to `gstyphoon*.js` targets and then verified by module/heap + exact World 921031 identity.
- Authoritative build gate is exact 1 MiB CPU-logical SHA-256 `5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62`.
- Read-only CDP allowlist contains no `Input.*` method and exposes no arbitrary JavaScript input.
- Status explicitly reports Browser / WOF page / Worker / WASM-heap / World 921031 / READ ONLY.
- Tray UI and Settings shell reserve Future Danger, HUD, sound, hotkeys, and Assist Mode positions. Assist Mode is visibly not implemented.
- Reconnect clears stale browser/page/Worker/module/identity state before retry.
- Failure to start/attach updates only launcher status; it does not touch or close the game.

## Known browser constraint handled

Chrome 136+ does not honor remote-debugging switches against the default Chrome data directory. Foundation uses a dedicated WOF browser profile and localhost debug port. A totally ordinary already-running Chrome/Edge instance with no CDP endpoint cannot be retroactively attached through supported CDP; this is a browser platform boundary, not something the launcher should bypass with process-memory hooks.

## One remaining owner proof

On Windows, from this directory run exactly:

```bat
py -3 -m venv .venv && .venv\Scripts\python -m pip install -r requirements.txt && .venv\Scripts\python launcher.py
```

Then enter the WOF room normally in the Chrome/Edge window opened by the launcher. Do not open DevTools and do not paste JavaScript.

Pass condition: tray status reaches all of these simultaneously:

```text
Browser: OK
WOF page: OK
Worker: OK
WASM / heap: OK
World 921031: OK
READ ONLY / RAM writes: 0
```

Also confirm the room remains playable while the launcher is attached. If it does not reach this state, open **Diagnostics / Logs** and return that single JSON snapshot; no gameplay capture or memory collection is needed.

# WOF Python Launcher Foundation — Architecture

## Data/control path

```text
Python launcher
  -> localhost HTTP /json/version
  -> browser-level CDP WebSocket
  -> Target.getTargets
  -> exact gstyphoon*.js Worker candidates
  -> Target.attachToTarget(flatten=true)
  -> Runtime.evaluate(fixed read-only probes only)
     -> locate Emscripten module / HEAPU8 / HEAPU32
     -> locate exactly one World program candidate
     -> hash 1 MiB CPU-logical bytes
  -> status store
  -> Windows tray / on-demand Tk settings
```

The launcher never interposes on page startup. Native page JavaScript constructs the native Worker first. CDP attaches to an existing target afterwards.

## Worker selection

The launcher does not attach to an arbitrary Worker and call it WOF.

1. Browser target must be type `worker`.
2. Target URL must match `gstyphoon*.js` (query strings allowed).
3. Lightweight fixed probe must find one object with a shared Emscripten `HEAPU8`/`HEAPU32` buffer.
4. Exact build probe must locate exactly one 1 MiB program region using reset-vector + dispatch sanity.
5. CPU-logical SHA-256 must equal the authoritative World 921031 digest.
6. If two live tabs both satisfy the same supported identity, the foundation fails closed as ambiguous rather than selecting one silently.

## Page selection

Preferred association is Worker `openerId` -> page target when Chromium exposes it. Fallback is a fixed read-only page probe for the known game WebGL surface (`I_GF1TC` / `I_fdC8Q`). Multiple matching pages remain ambiguous unless exactly one carries a WOF/Warriors-of-Fate URL/title hint.

## Reconnect model

The monitor re-queries targets periodically. Browser close/restart, page reload, room transition, Worker destruction or replacement naturally invalidates the previous target/session IDs. Any CDP failure clears all page/Worker/module/build status before retrying. No stale Worker object is used after disconnect.

A manual **Reconnect** forces the same teardown immediately.

## Read-only enforcement

Foundation CDP methods are allowlisted in `wof_launcher/cdp.py`:

- `Target.getTargets`
- `Target.attachToTarget`
- `Target.detachFromTarget`
- `Runtime.enable`
- `Runtime.evaluate`

No `Input.*`, `DOM.*`, `Network.set*`, `Page.navigate`, debugger mutation, game callback invocation, or arbitrary console bridge is exposed. `Runtime.evaluate` is used only with source-controlled fixed probes in `probe.py`; no user-entered JavaScript is accepted.

All probe results include `readOnly:true`, `ramWrites:0`, `inputInjection:false`; the Python status model independently hard-codes the same foundation invariants.

## Browser profile choice

Chrome 136+ requires a non-default `--user-data-dir` for remote debugging switches. The default launcher path is therefore:

```text
%LOCALAPPDATA%\WOF Future Danger\BrowserProfile
```

The debugging address is `127.0.0.1` only. This also avoids placing the user's normal Chrome/Edge profile behind a debugging endpoint.

## Dependencies

- `websocket-client`: small synchronous WebSocket transport for browser-level CDP; avoids Selenium/Playwright and their browser-control surface.
- `pystray`: Windows notification-area icon/menu.
- `Pillow`: creates the tray icon in memory for pystray.
- Tkinter: settings/diagnostics shell; included with normal Windows Python, no PyPI dependency.

## Packaging direction

PyInstaller one-file/windowed is the intended next packaging step after the live Windows proof. See `PACKAGING.md`. Packaging must not enable writes or input features.

# WOF Python Launcher — Real Chromium Discovery Architecture

## Current route

```text
Python Launcher
  -> localhost Chrome/Edge CDP only
  -> browser Target.getTargets
  -> independently probe page targets
  -> attach to each candidate page
  -> Target.setAutoAttach(flatten=true, waitForDebuggerOnStart=false)
  -> collect directly related existing/new iframe/worker targets
  -> recurse through related iframe targets (bounded depth/session count)
  -> fixed read-only WOF Worker probe
  -> existing exact World 921031 identity probe
  -> status / Chinese tray / proof JSON
```

The old direct browser-root Worker path remains as a backward-compatible fallback. It is no longer required that the browser root list expose exactly `type=worker + gstyphoon*.js` before WOF page discovery can proceed.

## Why this fixes the real Chrome failure

The previous implementation returned immediately when browser-level `Target.getTargets` contained no target matching `type=worker` plus a `gstyphoon*.js` URL. That also prevented page probing, which explains the real Windows evidence where Chrome/CDP and the room worked but both `wof_page_found` and `worker_found` remained false.

Chromium may expose a game Worker through the page's attached target tree, including page -> iframe -> Worker layouts or worker-like target types/URLs that differ from the historical assumption. The new discovery layer derives Worker membership from that page session relationship first.

## Acceptance remains fail-closed

A target is never accepted merely because it is related to a WOF-looking page.

Acceptance still requires:
1. a unique page/Worker association;
2. fixed read-only Emscripten module / HEAPU8 / HEAPU32 probe;
3. exactly one valid World program candidate;
4. exact full CPU-logical SHA-256 equal to `5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62`;
5. ambiguity across multiple valid page/Worker pairs fails closed.

Blob/Data/JavaScript worker URLs are rejected. Stale target IDs are not reused after reconnect/reload; identity cache is keyed by live target ID.

## Read-only enforcement

Allowed CDP methods are limited to:
- `Target.getTargets`
- `Target.attachToTarget`
- `Target.detachFromTarget`
- `Target.setAutoAttach`
- `Runtime.enable`
- `Runtime.evaluate`

`Target.setAutoAttach` changes debugger discovery/attachment state only. No `Input.*`, navigation, DOM mutation, arbitrary `Runtime.callFunctionOn`, Worker replacement, Worker URL rewrite, game RAM write, native process hook, or gameplay input path is enabled.

Fixed Runtime.evaluate expressions remain source-controlled in `probe.py`; owner-entered JavaScript is not accepted.

## Diagnostics

Proof/status now records the discovery path and bounded target topology metadata: type, URL, parent/opener/parent-frame relationships and page signals. Diagnostics are advisory only; World identity remains authoritative.

## Owner UX

Normal owner-facing tray, settings, status, errors and CMD workflow are Simplified Chinese. Technical JSON keys remain English for compatibility.

The one-click owner flow is:

```text
WOF_ONECLICK_PROOF_CN.cmd
-> download latest launcher
-> start dedicated localhost-CDP Chrome/Edge profile
-> owner enters WOF normally
-> launcher automatically validates page / Worker / WASM / World 921031
```

No DevTools, Worker Console selection or pasted JavaScript is required.

# WOF Alpha RC5 — Fresh Independent QA / Retest Findings

Updated: 2026-09-01  
Overall: **PASS**  
Final verdict: **PASS — RC5 ROOM-ENTRY REPAIR QA**

QA product changes: **0**. This lane did not modify `product/alpha/**`, `parallel/PYLAUNCH/**`, Python Launcher, or WOF-052L.

## A. RC5 room-entry repair verdict — PASS

The owner supplied the required real-Browser retest with:

- `WOF Future Danger Alpha RC5 Safe Bootstrap` enabled;
- Browser Acceptance Helper disabled;
- game entering a room normally;
- no HUD/warnings while no safe external live-Worker transport is connected.

Independent source inspection supports accepting that real-Browser result and closing the specific former P0 **“Alpha prevents room entry.”**

The current RC5 bootstrap:

- never assigns to or wraps `window.Worker`;
- constructs zero game Workers itself;
- contains no Blob Worker creation, ObjectURL Worker replacement, `importScripts()` wrapper, or rewritten game Worker URL path;
- leaves the original native Worker constructor identity intact;
- does not fetch/evaluate the page HUD before a valid same-session detector `state` is observed;
- degrades to `DISABLED` without changing Worker construction if secure session creation or BroadcastChannel setup fails.

A fresh independent VM harness under this QA lane passed the native-Worker identity, original URL/options pass-through, zero pre-pair HUD fetch, zero Blob/ObjectURL, secure-random failure fail-open, BroadcastChannel failure fail-open, and foreign-session pre-pair rejection checks.

Therefore the real-Browser room-entry success is consistent with and independently supported by the RC5 no-replacement design. No RC5 P0/P1 was found that invalidates the room-entry repair.

## Warning behavior without external transport — PASS / intentionally silent

When no safe non-replacing live-Worker detector transport exists, RC5 starts in `WAITING_EXTERNAL_TRANSPORT`, does not load the HUD, and cannot publish production warnings.

This is the required fail-closed warning behavior and fail-open gameplay behavior. The current absence of HUD/warnings is **not** evidence that detector/HUD Browser acceptance has passed; it is the expected pre-transport state.

## Worker / Blob / URL-rewrite audit — PASS

Current `product/alpha/wof_alpha_bootstrap.user.js` exposes:

- `workerIntercepted:false`;
- `workerReplacement:false`;
- `gameWorkerUntouched:true`;
- transport requirement `external-live-worker-required`.

The file contains no `window.Worker = ...`, no `new Blob(...)`, no `URL.createObjectURL(...)`, and no `importScripts(...)` replacement path. The independent VM harness additionally constructs an ordinary native Worker after bootstrap and confirms the exact URL and original options object pass through unchanged.

## Gameplay fail-open audit — PASS

Two bootstrap failure injections were independently reproduced:

1. secure `crypto.getRandomValues()` failure;
2. `BroadcastChannel` construction failure.

In both cases bootstrap evaluation remains contained, the game Worker constructor identity remains exact, no game Worker is constructed by Alpha, no Blob/ObjectURL is produced, and no HUD/loader fetch occurs. These failures disable Alpha only.

Because RC5 no longer substitutes the game Worker target, the former asynchronous Blob-wrapper failure class that could break room entry is removed rather than hidden behind a synchronous constructor fallback.

## RC4 safety gates — preserved

The four critical RC4 implementation blobs are byte-identical by Git blob SHA to the prior independent RC4 QA snapshot:

- `wof_alpha_core.js` — `267a44190744b6848b0685712c3d5572627d3a8a`
- `wof_alpha_loader.js` — `ef6c74fc6cba3c101654a851c411b2b2b005d447`
- `wof_alpha_hud.js` — `f93f90cc3cc898083d9613841927349159a0d4ae`
- `wof_alpha_hud_model.js` — `16641129ff651c2733aebc6fae09a280e4bac49b`

That preservation was also cross-checked against current source/regression guards. The following RC4 gates remain intact:

- exact `wof / World 921031` full 1 MiB CPU-logical SHA-256 equality gate;
- golden digest `5c369ce2de4f53d8cef87eca5623a1f0d39a779e885532d6f185b81357878f62`;
- pending/missing/malformed/mismatch/hash-error identity remains fail-closed;
- exactly two T18 current-level production rules remain active;
- F1-F4/history-dependent rules remain quarantined;
- BODY4728 attack-specific candidate remains excluded;
- same-type same-slot replacement cannot inherit warning history;
- first current nonmatch clears current-level warning immediately;
- per-page random session and exact schema/session transport acceptance remain enforced;
- simultaneous warning aggregation remains multi-warning;
- legacy research HUD disposal remains required;
- accepted current-session runtime `diag` immediately clears `lastMsg` and `lastRx` warning authority;
- foreign-session `diag` is rejected before mutation;
- a later legal paired state may become authoritative again;
- ordinary no-diag staleness remains fresh through 1500 ms and stale after 1500 ms;
- target selector is reread live and side is recomputed from current geometry;
- invalid/UNKNOWN target remains silent;
- detector access remains read-only with `ramWrites:0`;
- no gameplay input injection path exists;
- HUD WebGL touched state remains snapshotted/restored.

Current `rules_manifest.json` records the RC5 gameplay-fail-open bootstrap policy while leaving the production rule inventory unchanged.

## B. Alpha release verdict — NOT release-ready yet

Closing the room-entry P0 does **not** complete Alpha Browser acceptance.

A usable Alpha still requires a proven safe **non-replacing live-Worker transport** that can connect the existing detector to the RC5 session/channel without changing native game Worker semantics. Only after that transport exists can the bounded real-Browser acceptance exercise live World 921031 identity acceptance, detector state, HUD rendering, warnings, runtime diagnostics, and real-host behavior.

This QA lane does not implement that transport and does not duplicate Python Launcher work.

## Stop condition

No deterministic P0/P1 was found in RC5 that invalidates the room-entry repair.

**PASS — RC5 ROOM-ENTRY REPAIR QA**

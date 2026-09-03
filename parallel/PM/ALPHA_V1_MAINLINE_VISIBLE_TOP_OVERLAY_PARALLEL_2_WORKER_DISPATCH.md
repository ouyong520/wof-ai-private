# Alpha V1 — Visible Top-Overlay Mainline Parallel 2-Worker Dispatch

Status: **AUTHORITATIVE MAINLINE ACCELERATION — SAME ACTIVE ALPHA V1 / V3 UMBRELLA — NO NEW W7/W8**

Parent correction:
`parallel/PM/ALPHA_V1_MAINLINE_VISIBLE_PRODUCT_CONVERGENCE_CORRECTION.md`

Existing V3 umbrella remains the sole integration/package/RESULT authority. This dispatch does not create a new recovery generation, does not create W7/W8, and does not replace W4/W5/W6 authority. It only uses two newly freed workers on two non-overlapping slices of the same visible-product mainline.

## Current concrete defect

The currently selected `parallel/RENDER_AUTHORITY_V3/measurement_runner.py` still declares:

- `productionOverlayEnabled=false`
- terminal summary `productionOverlaySuppressed=true`

while the existing Alpha production page HUD already contains actual WebGL drawing paths for:

- enemy target labels `1P` / `2P` / `3P`;
- player-head danger warning badge `危险`;
- stale/loss suppression semantics;
- GL state save/restore and read-only overlay rendering.

Therefore the immediate mainline defect is not “we have no renderer”; it is that the current menu-6 / V3 selected path is still an authority/measurement path that deliberately suppresses the production overlay instead of reaching the already-maintained visible product path.

The next Owner-facing candidate must stop doing that.

## Slice A — runtime visible-overlay integration

### Ownership

Runtime/product integration only. Primary files may include, as materially necessary:

- `parallel/RENDER_AUTHORITY_V3/measurement_runner.py`
- `parallel/PYLAUNCH/wof_launcher/head_visual_tracker.py`
- a new narrowly-scoped adapter under `parallel/PYLAUNCH/wof_launcher/` if needed
- existing `product/alpha/**` runtime/HUD modules only when required to consume the current verified authority

Do **not** modify Owner menu/package/manifest files; Slice B owns those.

### Goal

Turn the selected menu-6 V3 runtime from “measurement completes while production overlay is suppressed” into a real visible-product runtime:

`authority acquired -> P1 head authority established -> production top overlay visible -> loss hides -> recovery reappears -> lifecycle/re-entry reacquires`

Required behavior:

1. Automatic semantic acquisition still runs first.
2. SAFE_UNIQUE may reach tracking with zero clicks.
3. If automatic identity acquisition fails safely, the existing bounded one-click-on-real-P1-head fallback may seed the same production tracker.
4. Either path must reach the same **production** visible top-overlay path.
5. Do not treat the white diagnostic/acquisition marker alone as the product overlay.
6. Reuse maintained Alpha HUD/label modules where they can consume current verified authority; do not fork a second product HUD.
7. Do not resurrect unproved/legacy projection guessing. `manualCalibration=false`, `legacyProjectionSelected=false` remain hard requirements.
8. If an old Alpha production module can only draw via authority that the current V3 correction explicitly superseded, adapt it to the current verified screen-space/runtime authority or fail precisely; do not silently re-enable stale authority.
9. Loss/stale/mismatch must hide rather than leave a stale label.
10. Preserve `readOnly=true`, `ramWrites=0`, `inputInjection=false`.

### Finish condition

Land one coherent runtime integration plus focused behavior regression for the actual visible path. Hand off exact commits/files to the umbrella coordinator. Do not generate the Owner package and do not close V3 claims.

## Slice B — Owner menu/status/package selection

### Ownership

Owner-facing entry/status/package selection only. Primary files may include, as materially necessary:

- `parallel/OPTOOLKIT/owner_zh_cn.py`
- menu-6 launcher/entry glue
- `parallel/OWNER_ONECLICK/**`
- package manifest/generator and package-facing acceptance metadata

Do **not** modify tracker/runtime/Alpha HUD algorithms; Slice A owns runtime visible-overlay integration.

### Goal

Make the next package select and expose the real visible-product path rather than a diagnostic/overlay-suppressed measurement path.

Required behavior:

1. Menu 6 must enter/reuse the real WOF session and start the selected visible-overlay runtime.
2. Tray/status remains visible and tells the Owner what is happening without requiring terminal interpretation.
3. States must distinguish at minimum: starting/waiting WOF, auto acquiring P1, one-click fallback required, head tracking/overlay visible, temporarily lost/recovering, blocked.
4. Do not open an empty browser as a successful result.
5. Do not publish a package that still advertises `productionOverlayEnabled=false` or `productionOverlaySuppressed=true` for the selected normal path.
6. Do not publish until Slice A runtime commit is known and pinned.
7. The package must contain the exact selected runtime/HUD dependencies and preserve zero-click-first / max-one-click-fallback semantics.
8. Preserve read-only safety and no manual calibration.

### Finish condition

Prepare the Owner-visible selection/status/package wiring and focused package gate. Once Slice A lands, pin the exact runtime and hand off to the umbrella coordinator for one final integrated regression/package publication. Do not independently publish an Owner package or close V3 claims.

## Umbrella coordinator

The existing V3 umbrella worker remains terminal coordinator and must:

1. keep mainline authority;
2. consume Slice A and Slice B only after checking their exact commits;
3. keep W4/W5/W6 as zero-click dependencies, but **do not withhold the visible-product path merely because normal zero-click authority is still unresolved**;
4. run one coherent affected regression on the actual selected visible runtime;
5. generate one immutable Owner-visible package only after the production overlay is actually selected and enabled;
6. record RESULT with a clear split between visible-product readiness, zero-click readiness, and real-WOF-only proof;
7. send no engineering intermediate package to Owner.

## Product acceptance target

The immediate target is:

`menu 6 -> WOF -> status visible -> automatic P1 attempt -> zero-click when safe OR max-one-click fallback -> production top-of-head display -> loss hides -> recovery returns -> re-entry continues`

A repository PASS that still suppresses the production overlay is a FAIL for this mainline target.

# ALPHA V1 LIVE ACCEPTANCE RENDER AUTHORITY SPRITE COORDINATE RECOVERY V2 — RESULT

## Verdict

**COMPLETE — BOUNDED AUTOMATIC RENDER-AUTHORITY MEASUREMENT PACKAGE READY — OWNER ACTION: NORMAL PLAY ONLY**

This recovery reached the PM-authorized bounded feasibility exit: repository/exact-runtime introspection did not expose a previously proven CPS1 renderer sprite/object screen-space list that could safely be consumed as production authority without one more live World 921031 measurement. V2 therefore does **not** guess an OBJ base, does **not** reuse the superseded Y / Y-Z / Y+Z path, and does **not** ask for head-click calibration.

## Authority finding

Available package-selected runtime code establishes all of the following:

- exact World 921031 Worker/WASM identity and current runtime-generation authority are available;
- gameplay actor RAM/lifecycle state is readable and can be used only as an association/time-continuity label;
- the existing WebGL HUD hook draws post-composition markers from externally supplied coordinates and does not expose the emulator's CPS1 per-object screen-space list;
- the superseded projection worker reads gameplay x/y/z and camera candidates rather than consuming a renderer object table;
- no repository-selected exact-runtime symbol/export already proves CPS-A OBJ base, renderer `ObjMem`/equivalent, or decoded frame-synchronous sprite/object coordinates.

Public CPS1 emulator source was used only as architecture context. No public-source constant/address was promoted to live authority.

## V2 implementation

Source implementation tip: `e1296e971c4aca305ddcfe269ffab3b1021f4aa9`

Implemented:

1. `parallel/RENDER_AUTHORITY_V2/wof_render_authority_capture_worker.js`
   - binds to exact World SHA + accepted authority key + fresh runtime epoch;
   - remains read-only (`ramWrites=0`, `inputInjection=false`);
   - records exact Worker/WASM module surface metadata and bounded heap evidence;
   - records lifecycle-labelled P1/P2/P3/enemy RAM samples for future strict actor/render association without deriving screen Y from world Y/Z;
   - scans bounded memory windows for CPS1-like 8-byte structural regions in both 16-bit byte orders, but labels every hit `UNVERIFIED_CANDIDATE_ONLY` and never turns one into overlay authority;
   - completes automatically after a 30-second bounded window;
   - `overlayEnabled=false` and `guessedConstantsAccepted=false` throughout.

2. `parallel/PYLAUNCH/wof_launcher/render_authority_capture.py`
   - launcher-side exact authority/runtime-generation binding;
   - rejects malformed, stale or mismatched terminal evidence;
   - enforces safety fields before accepting any capture state/result.

3. `parallel/RENDER_AUTHORITY_V2/measurement_runner.py`
   - zero-calibration Owner flow;
   - automatically discovers Page/Worker/WASM/exact World 921031;
   - revokes a capture on runtime-generation replacement and rediscovers instead of mixing generations;
   - explicitly disposes the superseded projection UI / Alpha HUD before measurement so an unproved coordinate path cannot appear as production overlay;
   - automatically writes `RENDER_AUTHORITY_CAPTURE_RESULT.json`, session timeline, summary and `WOF_LIVE_ACCEPTANCE_<session>.zip`.

4. `parallel/PYLAUNCH/render_authority_measurement_entry.py`
   - package-safe entry from the existing PYLAUNCH environment.

5. `parallel/OPTOOLKIT/owner_zh_cn.py`
   - menu 6 now says only: enter WOF and normally play 20–30 seconds;
   - removes all P1 head-click, Y/Y-Z/Y+Z, depth/jump/resize/fullscreen calibration instructions;
   - clearly states production overlay is suppressed until exact render authority is verified.

## Deterministic implementation self-check

`parallel/RENDER_AUTHORITY_V2/selftest.mjs` covers the capture boundary with a deterministic mock linear-memory/runtime fixture:

- idle/measurement overlay is disabled;
- structural candidates remain `UNVERIFIED_CANDIDATE_ONLY`;
- wrong World SHA is rejected;
- exact World/runtime binding enters MEASURING;
- bounded time advances to `MEASUREMENT_COMPLETE`;
- terminal verdict is `BOUNDED_CAPTURE_READY_FOR_RENDER_AUTHORITY_ANALYSIS`;
- guessed constants remain rejected.

Implementation-owned local execution during this recovery: `node selftest.mjs` equivalent fixture **PASS**; new Python capture module also passed `py_compile` syntax validation. No emulator/browser QA chain was opened because the only remaining evidence is the explicitly authorized focused Owner live measurement.

## Successor package

Package version: `2026.09.03.renderauthv2.e1296e971c4a`

Manifest publication commit: `612b81cf6628a3b07e19813564e66fcc1112a9ab`

Immutable publication descriptor commit: `f5aa4b710c6c2116ec307ac9f5cdab7e8c58acf8`

Immutable descriptor:

`parallel/OWNER_ONECLICK_IMMUTABLE/2026.09.03.renderauthv2.e1296e971c4a/IMMUTABLE_PACKAGE.json`

The manifest is pinned to source commit `e1296e971c4aca305ddcfe269ffab3b1021f4aa9` and keeps bootstrap blob-integrity verification. The superseded HUDANCHOR projection proof files are not selected by the successor's render-authority component/menu-6 path.

Safety contract remains:

- `readOnly=true`
- `ramWrites=0`
- `inputInjection=false`
- `manualCalibration=false`
- legacy projection not selected for menu 6
- production overlay suppressed until exact renderer/object screen-space authority is proven

## Historical V1 claims

The superseded Projection Transform + Owner UX Recovery V1 canonical/stage claims remain historical `ACTIVE` records exactly as required by PM. V2 does not modify, close, reuse or repair them.

## One remaining live measurement

Owner action is intentionally only:

**正常进入 WOF，正常玩 20–30 秒。**

The resulting ZIP is the one bounded measurement needed to identify/verify the exact World 921031 renderer/object authority and then permit production actor anchors. No head click, projection model selection, coordinate math, special movement checklist, DevTools, Python command or manual evidence packaging is required.

## Terminal

`COMPLETE — ALPHA V1 LIVE ACCEPTANCE RENDER AUTHORITY SPRITE COORDINATE RECOVERY V2 — BOUNDED AUTOMATIC RENDER-AUTHORITY MEASUREMENT PACKAGE READY — OWNER ACTION: NORMAL PLAY ONLY`

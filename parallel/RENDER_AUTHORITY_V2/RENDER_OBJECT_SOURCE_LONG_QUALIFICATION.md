# W3 Renderer/Object Source Long Qualification

## Scope and truth boundary

This module exhausts the repository-side renderer/object qualification work without inventing authority. A structural HEAP region, nearest object, row order, screenshot coordinate, world-coordinate projection, guessed offset, stale buffer, or prior point is never enough to become production position authority.

The only PASS path is a direct causal proof that the sampled native object rows feed the displayed CPS1 frame, with the exact World/runtime/renderer epochs and explicit actor association + generation carried with that proof.

## Repository reverse trace

The checked-in causal chain currently reaches:

1. `measurement_runner.py` discovers and accepts exact World 921031 Page/Worker/WASM runtime authority.
2. `wof_launcher/render_authority_capture.py` creates a fresh `runtimeEpoch` + `rendererEpoch`, binds the exact Worker, and injects only the maintained W3 capture worker.
3. `wof_render_authority_capture_worker.js` reads the accepted Worker `Module` HEAP read-only, samples actor lifecycle/generation context, and scans structural 8-byte `[x,y,tile,attr]` candidates.
4. The worker emits `candidateRegions` / `candidateTimeline` and explicitly labels them `UNVERIFIED_CANDIDATE_ONLY`.
5. Verification screenshots are captured only as external evidence and are explicitly `VERIFICATION_ONLY_NOT_POSITION_AUTHORITY`.
6. The canonical consumer remains fail-closed until a renderer source is actually proven.

The repository does **not** currently contain a causal edge from the displayed CPS1 renderer/object submission (buffered object list, renderer command buffer, renderer-side equivalent, or exact deterministic write sequence) to the candidate HEAP address/window. The existing `_0x515056` Module discovery and `HEAPU32[0x2e39e4 >>> 2]` RAM reference establish Worker/game-memory context only; they do not prove a renderer object buffer.

Therefore a high structural score or a uniquely stable region remains diagnostic evidence only. It cannot self-qualify.

## Deterministic analyzer

`qualification_analyzer.py` consumes `RENDER_AUTHORITY_CAPTURE_RESULT.json` and emits:

- `PASS`: only when `wof-renderer-source-proof-v1` proves a direct displayed-frame renderer/object causal link, source-traced/direct-hook pointer derivation, native `384x224` renderer coordinates, explicit unambiguous actor association + generation, matching authority/runtime/renderer epochs, and multiple monotonic direct frame samples.
- `INCONCLUSIVE`: evidence is safe/valid but the displayed-frame causal proof is still missing or uniqueness is not proved.
- `REJECTED`: safety boundary mismatch, stale epoch mixing, malformed candidate rows/cadence, ambiguous claimed actor association, guessed address, screenshot/world projection production coordinates, or an unproven source falsely claiming qualification.

Candidate stability is summarized deterministically but never converted into authority by score ranking.

## One-command bounded Owner gate

From the repository root on the Owner Windows machine:

```powershell
py parallel\RENDER_AUTHORITY_V2\run_long_qualification.py
```

No coordinate clicks, DevTools, head/foot calibration, or Y/Y-Z/Y+Z choice are required. The existing exact-World runner binds a fresh runtime/renderer epoch, captures the bounded normal-play timeline plus verification-only frames, stops automatically, then the wrapper runs the deterministic analyzer and writes:

- `%LOCALAPPDATA%\WOF_ALPHA_RENDER_AUTHORITY\LATEST_W3_RENDER_SOURCE_QUALIFICATION.json`
- per-session `RENDER_SOURCE_QUALIFICATION.json`
- per-session `RENDER_SOURCE_QUALIFICATION.md`
- one `WOF_W3_QUALIFIED_*.zip` evidence bundle containing raw capture + qualification outputs + verification evidence.

For repository/offline dry analysis of an existing capture:

```powershell
py parallel\RENDER_AUTHORITY_V2\run_long_qualification.py --capture-json <RENDER_AUTHORITY_CAPTURE_RESULT.json>
```

## Canonical producer readiness

Until the analyzer returns PASS, any future `wof-render-object-frame-v1` frame must keep `rendererSource.proven=false` and remain suppressed downstream. Screenshot/world projection coordinates are forbidden as fallback.

A PASS proof must carry exact `worldSha256`, `authorityKey`, `runtimeEpoch`, `rendererEpoch`, native `384x224`, explicit actor association + generation, deterministic body roles, and no ambiguous identity. Only then may W3 expose `rendererSource.proven=true` for the already-maintained P12/P10 chain.

## Remaining live dependency

Repository-side reverse tracing and qualification tooling cannot manufacture the missing displayed-frame causal edge. With current checked-in evidence, the remaining gate is exactly one bounded exact-World normal-play sample through the command above. That run is automatically analyzed; if it still lacks a direct renderer/object causal proof, the correct outcome remains `INCONCLUSIVE`, not a guessed PASS.

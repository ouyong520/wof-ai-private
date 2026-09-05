# Alpha V1 W3 Renderer/Object Source Long Qualification Result

## Outcome

`SUBCOMPLETE` under the existing ACTIVE claim `d8496ca1-62a2-44a6-85f5-b782a16af2c7`.

The repository-side W3 qualification workstream is exhausted. The maintained chain now has a documented renderer/object reverse trace, an offline deterministic fail-closed analyzer, and a one-command bounded exact-World normal-play runner that automatically performs capture -> qualification -> compact evidence bundle output.

The remaining truth boundary is unchanged: checked-in evidence does not currently prove the causal edge from the displayed CPS1 frame renderer/object submission to an exact HEAP object source/pointer/object row. Structural `[x,y,tile,attr]` similarity, candidate score, row order, screenshots, world coordinates, nearest-object matching, guessed offsets, stale buffers, or prior points are not proof. Therefore `rendererSource.proven` must remain false and the downstream canonical producer/HUD remains suppressed.

## Changes

- Added `parallel/RENDER_AUTHORITY_V2/qualification_analyzer.py` with deterministic `PASS / INCONCLUSIVE / REJECTED` output.
- PASS requires an explicit `wof-renderer-source-proof-v1` direct displayed-frame causal proof, source-traced/direct-hook pointer derivation, native `384x224` renderer/object coordinates, matching authority/runtime/renderer epochs, explicit unambiguous actor association + generation, and multiple monotonic direct frame samples.
- REJECTED covers stale epoch mixing, malformed candidate evidence, guessed address/pointer derivation, screenshot/world-projection production coordinates, ambiguous actor association, and unproven sources falsely claiming qualification.
- Candidate stability/uniqueness is diagnostic only and can never self-promote to authority by score.
- Added `parallel/RENDER_AUTHORITY_V2/run_long_qualification.py`. With no arguments it reuses the maintained exact-World bounded measurement runner, then automatically writes qualification JSON/Markdown, a stable `LATEST_W3_RENDER_SOURCE_QUALIFICATION.json`, and one `WOF_W3_QUALIFIED_*.zip` containing raw capture plus qualification evidence.
- Added offline `--capture-json` dry mode for deterministic analysis without CDP/live runtime.
- Added `parallel/RENDER_AUTHORITY_V2/RENDER_OBJECT_SOURCE_LONG_QUALIFICATION.md` documenting the complete proven/unproven reverse-trace boundary and canonical producer readiness.
- No canonical/stage claim was created, modified, recovered, or stolen. No P15/P10/P12/P11 implementation ownership was touched.

Implementation commit: `c491f24ac597fa59a39da30abf2b2efb55ea376d`.

## Tests

Focused checks passed:

- `python -m unittest discover -s parallel/RENDER_AUTHORITY_V2 -p 'test_*qualification*.py'` equivalent isolated run: **9 passed**.
- Covered candidate-only -> INCONCLUSIVE, synthetic explicit direct causal proof -> PASS, screenshot production source -> REJECTED, world projection -> REJECTED, guessed address -> REJECTED, stale renderer epoch -> REJECTED, ambiguous stable candidates -> INCONCLUSIVE, deterministic output equality, and offline runner JSON/MD/latest-pointer/ZIP bundling.
- Python compile check passed for analyzer, runner, and both focused test modules.
- Main integration was concurrency-safe: stale fast-forward attempts were rejected; no force push was used; W3 implementation was rebuilt on latest concurrent main and landed with `force=false`.

## Integration

Repository-side tooling is ready, but product integration is intentionally **not** marked ready because the renderer source itself is still unproven. The existing W3 capture already binds exact World 921031 + accepted Worker/WASM + fresh runtime/renderer epochs and records bounded candidate timelines plus verification-only screenshots. The new analyzer now makes the missing causal proof explicit instead of allowing a heuristic winner.

Until a live qualification returns PASS, any `wof-render-object-frame-v1` output must keep `rendererSource.proven=false`; screenshot/world projection coordinates remain forbidden as production fallback.

## Owner Action

Run exactly once on the Owner Windows exact-World runtime:

`py parallel\RENDER_AUTHORITY_V2\run_long_qualification.py`

Then simply play normally for the bounded capture. No clicks, DevTools, coordinate calibration, head/foot selection, or Y/Y-Z/Y+Z ritual is required. The runner stops automatically and writes the qualification result plus qualified ZIP.

This single run does not guarantee PASS: if it still lacks a direct displayed-frame renderer/object causal proof, the correct result remains `INCONCLUSIVE` and no address may be guessed.

## Recommended Next

PM/Owner should consume `%LOCALAPPDATA%\WOF_ALPHA_RENDER_AUTHORITY\LATEST_W3_RENDER_SOURCE_QUALIFICATION.json` and the referenced `WOF_W3_QUALIFIED_*.zip`. Only a `PASS` satisfying the direct proof contract may unlock `rendererSource.proven=true` for the maintained P12/P10 chain. Otherwise keep the canonical producer suppressed and retain this W3 truth boundary.

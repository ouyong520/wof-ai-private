# Alpha V1 P43 — Bounded Zero-Click Live Diagnostic Harness

P43 is a **diagnostic harness only** for one later, separately authorized bounded WOF run. This worker task does not run the game.

The final P43 continuation consumes terminal-tested P45 and P46 rather than duplicating them:

- exact P45 tested candidate `3dac7a9e2cbe4a23c3de44eb15cf45f19b136149` supplies the maintained default-off P39 → P42 staging integration;
- exact P46 tested commit `210efdda5bbf3715989c751eb90442f26f42d0a9` / probe blob `efd71e25e28f171e080774eb5aa1309a0d7bbe2b` supplies bounded WASM/WebGL call-site evidence;
- exact P39/P42 dependencies remain P45-owned and are consumed through P45's staging readout, not reimplemented by P43;
- P29/P32/P36 authority criteria are unchanged and P40 remains blocked by `NATIVE_PLAYER_MARKER_DISPLAYED_SUBMIT_SOURCE_EXPORT_NOT_PRESENT`.

No click, avatar selection, manual seed, input injection, RAM write, install, promotion, or `alpha-live` movement is performed.

## Exact invocation contract

Use `WOF_ALPHA_P43_BOUNDED_DIAGNOSTIC.cmd`. It refuses Python fallback and runs only the existing WOF managed interpreter:

`%LOCALAPPDATA%\WOF Alpha Current Main\venv\Scripts\python.exe`

Required inputs are explicit; there is **no implicit HEAD**:

1. metadata repository root;
2. existing clean exact source checkout;
3. exact 40-hex `sourceCommit`;
4. exact 40-hex `metadataCommit`;
5. candidate pointer repository-relative path;
6. provenance repository-relative path;
7. existing browser WebSocket debugger URL;
8. output directory.

Optional inputs include `--p16-evidence`, `--p17-bundle`, `--runtime-log`, repeated `--staging-log`, and `--duration <0.1..60>`.

The source checkout HEAD must exactly equal `sourceCommit` and be clean. Candidate, attestation, manifest, pointer, and provenance are read from the explicit `metadataCommit`, SHA-256/Git-blob verified, and copied verbatim into `raw/candidate_binding/` after the binding gate passes.

## Exact P45 consumption

P43 materializes only the terminal-tested P45 diagnostic bytes into the run output directory and verifies each Git blob before use. It loads P45's exact `P45LiveDiagnosticStagingRuntime` plus exact P39 implementation bytes, then invokes only P45's attach-only diagnostic install/readout/teardown seam against the already P16-bound Page.

P43 deliberately does **not** call P45's normal `ensure_running()` path and does not ask P45 to recreate or rebind the maintained Alpha runtime. P45 therefore remains the owner of P39/P42 staging semantics while P43 remains the owner of bounded orchestration.

The P45 readout is preserved without filtering and contains:

- exact `runtimeEpoch` / `rendererEpoch` / `authorityKey` binding;
- P39 `UNVERIFIED_AUTO_BASELINE` P1/P2/P3 tracker/HUD status;
- visible/hidden/lost/stale/ambiguous/reacquire lifecycle state;
- complete P42 `wof-gstyphoon-renderer-correlation-probe-v1` raw bundle;
- P42 seal reason and teardown state.

## Exact P46 composition

P46 is injected only after P45 has installed P39 and P42. The deterministic WebGL wrapper stack is:

`P46 → P45/P42 → original runtime WebGL method`

P46's tested wrapper calls its captured lower wrapper/original first and then records its call-site evidence. Teardown is strict LIFO:

`P46 stop/readback → P45 P42/P39 stop/readback`

P46 restores a method only when its own exact wrapper is still at the top; external replacement is preserved as a teardown conflict rather than overwritten.

The P46 raw artifact keeps the complete bounded call-site bundle, including:

- raw JavaScript stack text;
- normalized call-site fingerprint;
- observed WASM function index/name/offset when exposed;
- explicit `NOT_AVAILABLE` / `UNRESOLVED` truth states when the browser does not expose those facts;
- JS wrapper/import caller identity with semantic role left `UNRESOLVED` unless observed;
- Module and Module.asm identity/relationship at start and per event;
- event sequence, draw submission sequence, buffer events and vertex-attrib setup events;
- exact object/state associations only;
- mapping assessment and teardown conflicts.

Stale/mixed binding and Module/Module.asm identity drift fail closed. P43 never guesses a WASM symbol or offset and never promotes timing/order/nearest correlation into authority.

## Evidence captured

Each run writes `P43_DIAGNOSTIC_RECEIPT.json`, `P43_DIAGNOSTIC_RECEIPT.md`, and bounded raw artifacts. The final receipt preserves:

- exact source/package/candidate/manifest/attestation/pointer/provenance identity and raw bytes;
- all Page targets and authoritative Page/Worker/WASM association;
- P16, P9, P36/P32 and P17 gate state;
- shared `runtimeEpoch` / `rendererEpoch` / `authorityKey` diagnostics binding;
- P36 raw source discovery, candidate rejection reasons, direct renderer-submit bundle, producer result and unchanged P32 qualifier result;
- exact P45 P39/P42 readout and complete P42 raw correlation bundle;
- exact P46 raw call-site bundle and teardown;
- browser/page console events, supplied runtime/staging logs, exceptions, chronological event/gate timelines;
- `firstFailingGate` plus every gate already successful before that failure;
- exact P45/P46 dependency materialization hashes and Git blobs;
- safety readback including unchanged `alpha-live` refs.

The stable receipt does not embed its own hash. Its SHA-256 is printed after final JSON bytes are written.

## Gate interpretation

The converged chronology includes the original P43 gates plus P45/P46 setup and LIFO teardown. It is designed to answer directly:

> Which gate failed first, and which earlier gates had already succeeded?

A P45 stale binding, P46 Module/asm drift, P46 wrapper conflict, P36 source absence, unchanged-P32 rejection, or P17 decision remains its own raw gate reason; none is collapsed into a generic evidence mismatch.

## Authority boundary

P39/P42/P46 evidence is diagnostic only. P43 does not create `__WOF_NATIVE_MARKER_RENDERER_SUBMIT_SOURCE_V1__` or `WOFNativeMarkerRendererSubmitSourceV1`, does not mint `rendererSourceProof`, P29 PASS, P32 qualification, retry eligibility, or promotion eligibility, and does not turn screenshot/OCR/template/timing/order/nearest/guessed-WASM evidence into authority.

This terminal harness work proves repository-side orchestration only. Real-WOF acceptance, Owner visual acceptance, promotion, source mapping, and resolution of P40 all remain outside P43.

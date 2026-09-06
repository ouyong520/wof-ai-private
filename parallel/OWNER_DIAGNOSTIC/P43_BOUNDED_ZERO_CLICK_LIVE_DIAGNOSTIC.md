# Alpha V1 P43 — Bounded Zero-Click Live Diagnostic Harness

P43 is a **diagnostic harness only** for one later, separately authorized bounded WOF run. This worker task does not run the game.

The harness is deliberately fail-closed and preserves existing authority boundaries:

- P29/P32/P36 acceptance criteria are not modified.
- P37/P39 data is always labelled `UNVERIFIED_AUTO_BASELINE` and never becomes renderer authority or production coordinates.
- P42 exact tested probe bytes are pinned to tested commit `7b523187a955179b04155b758847c82aaf569a0d` / blob `32b9c50e8a72de1a097b8ce5dc91b69bdcef0219`. When exact P16 binding and those bytes are locally available, P43 automatically loads, starts, stops, and archives P42 as diagnostic correlation evidence only (`authorityEligible=false`). Otherwise the receipt records `P42_CORRELATION_PROBE_NOT_PRESENT` with the exact reason.
- No click, avatar selection, manual seed, input injection, RAM write, promotion, or `alpha-live` movement is performed.
- No package install, PATH edit, site-packages edit, or global environment mutation is allowed.

## Exact invocation contract

Use `WOF_ALPHA_P43_BOUNDED_DIAGNOSTIC.cmd`. It refuses Python fallback and runs only the existing WOF managed interpreter:

`%LOCALAPPDATA%\WOF Alpha Current Main\venv\Scripts\python.exe`

Required inputs are explicit. There is **no implicit HEAD**:

1. metadata repository root;
2. existing clean exact source checkout;
3. exact 40-hex `sourceCommit`;
4. exact 40-hex `metadataCommit`;
5. candidate pointer repository-relative path;
6. provenance repository-relative path;
7. existing browser WebSocket debugger URL;
8. output directory.

Optional arguments are passed through to the Python harness, including:

- `--p16-evidence <path>`
- `--p17-bundle <path>`
- `--runtime-log <path>`
- repeated `--staging-log <path>`
- `--duration <0.1..60>` (default 15 seconds)

The source checkout HEAD must equal the explicit `sourceCommit` and must be clean. Candidate, attestation, rebuild manifest, pointer, and provenance bytes are read from the explicit `metadataCommit`, SHA-256 verified, Git-blob hashed, and cross-bound to the explicit source/package before browser observation begins. The accepted raw bytes are then copied verbatim into `raw/candidate_binding/` with their source path, SHA-256, Git blob, size, and metadata commit recorded.

## Evidence captured

Each run writes a machine-readable `P43_DIAGNOSTIC_RECEIPT.json` plus `P43_DIAGNOSTIC_RECEIPT.md`, and bounded raw artifacts under `raw/`.

The receipt contains:

- exact source/metadata commit + tree;
- exact candidate/attestation/manifest/pointer/provenance raw bytes plus path, SHA-256, Git blob, package version and runtime pins;
- every Page target returned by CDP and the P31 authoritative Page/Worker/WASM association diagnostics;
- P16, live P9/P8/HUD seam, and P17 gate states;
- runtimeEpoch / rendererEpoch / authorityKey when P16 supplies them;
- P36 raw source discovery, every discovered candidate with exact rejection reasons, raw direct renderer-submit bundle/events, deterministic teardown reason, P36 producer output, and the unchanged P32 qualifier result embedded in each producer result;
- P37/P39 P1/P2/P3 state, visible/hidden, stale, lost, ambiguous and reacquire fields, always under `UNVERIFIED_AUTO_BASELINE`;
- P42 raw correlation bundle and artifact hash/path after deterministic P43 teardown when exact P42 can run, otherwise `P42_CORRELATION_PROBE_NOT_PRESENT`;
- browser/page console + exception events, supplied runtime/staging logs, full harness exception strings/tracebacks, event chronology, gate-transition chronology, first failing gate, and gates that had already passed before it;
- bounded teardown and safety readback.

P43 keeps collecting independent diagnostics after a fail-closed gate when doing so remains safe and bounded. It never converts `FAILED_EVIDENCE_MISMATCH` into a generic answer: the receipt retains the exact gate and exact underlying reason.

The stable receipt wrapper deliberately does **not** persist a hash of the receipt inside the receipt itself (which would be self-referential and unstable). It prints the final receipt SHA-256 after the final JSON bytes are written; P42 and all raw evidence artifacts retain normal hash/path records inside the receipt.

## Gate interpretation

The diagnostic gate sequence is observable rather than promotive:

`CANDIDATE_BINDING → DEDICATED_RUNTIME_ENVIRONMENT → BROWSER_ENDPOINT → PAGE_WORKER_WASM_ASSOCIATION → P16_GATE → P9_GATE → P36_SOURCE_GATE → P36_PRODUCER_P32_GATE → P17_GATE → ALPHA_LIVE_SAFETY`

The human receipt directly answers:

> Which gate failed first, and which earlier gates had already succeeded?

A P17 automatic decision is preserved verbatim. A P36 source absence, stale/mixed binding, ambiguity, producer rejection, or unchanged-P32 rejection remains its own exact failure/blocker reason.

## Boundedness

- live observation duration is capped at 60 seconds;
- P36 keeps its own existing 96-event / 15-second bounds;
- P42 keeps its exact tested bounded limits, including its 15-second default wall limit and deterministic teardown;
- browser console capture is capped at 512 events;
- each copied runtime/staging log is capped to the final 8 MiB, with source byte count and truncation offset recorded;
- every CDP session, the P36 observer, and any P42 live probe created by P43 are deterministically torn down.

This is implementation proof only. Real-WOF acceptance, Owner visual acceptance, promotion, and `alpha-live` movement remain outside P43.

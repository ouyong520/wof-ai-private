# Alpha V1 P48 — One Bounded Owner Live Diagnostic Execution

StageId:
`ALPHA_V1_PRODUCT_TAKEOVER_P48_ONE_BOUNDED_OWNER_LIVE_DIAGNOSTIC_EXECUTION`

DedupKey:
`alpha.v1.product-takeover.one-bounded-owner-live-diagnostic-execution-v1`

Fresh PM authority at dispatch:
- main: `01c4548f5906fa1583135a667ebd1d1178ae9878`;
- P47 terminal COMPLETE and accepted:
  - tested commit `f0634c81f0efb54819cef10e0c4cf8567cd5ca9a`;
  - result commit `e825e146ebac6b4758340af4393947f7acdcdacd`;
  - readiness `READY_FOR_ONE_BOUNDED_OWNER_DIAGNOSTIC`;
  - run budget `1`;
- P43 exact diagnostic candidate: `0c23e22b0387d0b3042c5601ab0a9e897ce1c476`;
- P45 exact tested candidate: `3dac7a9e2cbe4a23c3de44eb15cf45f19b136149`;
- P46 exact tested commit: `210efdda5bbf3715989c751eb90442f26f42d0a9`;
- P40 remains terminal BLOCKED by `NATIVE_PLAYER_MARKER_DISPLAYED_SUBMIT_SOURCE_EXPORT_NOT_PRESENT`;
- this dispatch separately authorizes exactly one real bounded Owner diagnostic run;
- no promotion and no `alpha-live` movement are authorized.

## Purpose

Execute exactly one bounded zero-click real-WOF diagnostic using the exact P43/P45/P46 bytes that P47 classified READY, archive the complete unfiltered receipt/raw bundle, and stop. This task is evidence collection only. It must not promote diagnostic correlation into renderer authority.

## Exclusive one-run rule

1. Fresh-read main and P47 terminal RESULT + closed canonical/stage claims before doing anything else.
2. Acquire one exclusive P48 dedup-v2 claim before the real run.
3. Fresh-read whether any prior P48 terminal receipt/result exists. If the run budget has already been consumed, do not run again; fail closed as `OWNER_DIAGNOSTIC_RUN_BUDGET_ALREADY_CONSUMED`.
4. `runBudget=1` means at most one real-game launch/attachment attempt for this stage. Once the bounded live run starts, the budget is consumed even if the run later fails, times out, loses binding, or tears down with an error. No automatic retry.
5. Preflight failures before the real run starts do not consume the run, but they must be recorded exactly and may not be bypassed.

## Exact bytes and invocation

Use the exact P43 tested diagnostic candidate and its documented invocation contract:
- `parallel/OWNER_DIAGNOSTIC/WOF_ALPHA_P43_BOUNDED_DIAGNOSTIC.cmd`
- `parallel/OWNER_DIAGNOSTIC/P43_BOUNDED_ZERO_CLICK_LIVE_DIAGNOSTIC.md`
- `parallel/OWNER_DIAGNOSTIC/P43_POST_P45_P46_INTEGRATED_CANDIDATE.json`
- `parallel/OWNER_DIAGNOSTIC/P43_POST_P45_P46_DEPENDENCY_PINS.json`

Do not substitute HEAD bytes for the exact tested P43/P45/P46 bytes. Verify the tested commit/tree/blob pins before the live run. Any byte drift or dependency mismatch => fail closed before launch.

Use only the existing WOF managed interpreter required by P43. No package install, no alternate Python fallback, no repo mutation to make the runtime work.

Required P43 inputs remain explicit: exact metadata repo root, clean exact source checkout, exact sourceCommit, exact metadataCommit, candidate pointer path, provenance path, existing browser WebSocket debugger URL, and output directory. Resolve them from the accepted repo/runtime provenance and fresh-read them; do not guess paths, commits, debugger targets, or source identity.

## Live-run bounds and safety

The one run must remain:
- zero click / zero manual seed;
- read-only;
- RAM writes = 0;
- no input injection;
- no install;
- bounded wall time (`P43 <= 60s`, P46 internal default `<= 15s` unless exact tested configuration says otherwise);
- bounded console/event/log capture;
- deterministic LIFO teardown;
- no promotion;
- no `alpha-live` movement.

If Page/Worker/WASM association is ambiguous, candidate provenance mismatches, runtimeEpoch/rendererEpoch/authorityKey becomes stale or mixed, Module/Module.asm identity drifts, a wrapper conflict occurs, or any required dependency is missing: fail closed and preserve the exact raw reason. Do not retry.

## Evidence that must be archived unfiltered

From the same single run preserve:
- exact sourceCommit / metadataCommit / packageVersion / candidate / manifest / attestation / pointer / provenance identities and hashes;
- all Page targets and authoritative Page/Worker/WASM association evidence;
- P16 / P9 / P17 gate states;
- P36 raw source discovery, candidates, rejection reasons, direct renderer-submit events if any, producer result, and unchanged P32 qualifier result;
- P39 P1/P2/P3 diagnostic lifecycle state: visible / hidden / lost / stale / ambiguous / reacquire;
- complete P42 raw WebGL correlation bundle, binding, seal, teardown;
- complete P46 raw JS stack, normalized call-site fingerprint, WASM function index/name/offset truth states, JS caller identity, Module/Module.asm identities, eventSequence/drawSubmissionSequence, exact object/state associations, and teardown;
- runtime/console/staging logs and raw exceptions;
- exact chronological gate timeline, first failing gate, and gates passed before first failure;
- exact receipt SHA-256 after final bytes are written.

P46 WASM fields may only be `AVAILABLE`, `NOT_AVAILABLE`, or `UNRESOLVED` as observed. Never guess symbols, offsets, semantic roles, or source identity.

## Authority boundary

This run does NOT by itself:
- create `__WOF_NATIVE_MARKER_RENDERER_SUBMIT_SOURCE_V1__` or `WOFNativeMarkerRendererSubmitSourceV1`;
- mint `rendererSourceProof`;
- change P29 acceptance;
- change P32 qualification;
- resolve P40 merely because correlation looks plausible;
- create retry or promotion eligibility;
- authorize another live run.

Even if the raw evidence strongly correlates a WASM/WebGL call-site with native marker behavior, keep it classified as diagnostic evidence until a separately dispatched qualification/repair stage validates an authority-eligible direct source edge.

## Terminalization

After the one run (or a preflight fail-closed before run start):
1. archive the complete P43 receipt directory and raw evidence without filtering;
2. publish a machine-readable P48 RESULT recording whether the live run actually started, whether the one-run budget was consumed, exact receipt paths/hashes, safety readback, first failing gate, and concise evidence classification;
3. close canonical/stage P48 claims;
4. publish terminal PROGRESS 100%.

Terminal COMPLETE means the authorized one-run execution/receipt workflow is finished and truthfully recorded. It does not mean P40 is resolved or promotion is allowed.

Required final commit prefix:
`WORKER_RESULT ALPHA_V1_PRODUCT_TAKEOVER_P48_ONE_BOUNDED_OWNER_LIVE_DIAGNOSTIC_EXECUTION COMPLETE`

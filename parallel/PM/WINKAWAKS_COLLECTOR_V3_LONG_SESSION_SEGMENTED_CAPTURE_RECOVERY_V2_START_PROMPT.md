# WinKawaks Collector V3 — Long-Session Segmented Capture Recovery V2

stageId: `WINKAWAKS_COLLECTOR_V3_LONG_SESSION_SEGMENTED_CAPTURE_RECOVERY_V2`
dedupProtocol: `v2`
dedupKey: `winkawaks.collector.v3.long-session-segmented-capture.recovery-v2`
dedupMode: `exclusive`

Priority: **P0/P1 Collector side-lane recovery**

## Read first

- `parallel/PM/WINKAWAKS_COLLECTOR_V3_LONG_SESSION_SEGMENTED_CAPTURE_START_PROMPT.md`
- `parallel/PM/COLLECTOR_WORKER_EXECUTION_POLICY.md`
- `parallel/PM/TESTING_CADENCE_POLICY.md`
- `parallel/PM/STAGE_DEDUP_GUARD.md`
- `COLLECTOR_ROUTING.md`
- `RUNTIME_DATA_SOURCE_BOUNDARIES.md`
- current V3 canonical/stage claims
- current `ouyong520/wof-winkawaks-bridge/main`

This is PM-authorized implementation recovery. The original worker stopped after substantial V3 implementation landed. Resume from current HEAD; do not restart from zero and do not open QA.

## Current landed implementation to preserve and verify

Recent bridge main includes at least:

- `fd2930fa...` long-session segmented capture core;
- `1de046e8...` per-segment gzip handoff;
- `9fffff66...` segmented-session task schema integration;
- `029d2e52...` serialized queue integration;
- `eea5c584...` implementation self-checks;
- `a149ed4d...` contract/manifest documentation;
- `c5ee0a4b...` serialized results bound to local segmented evidence;
- `5f438e07...` serialized duplicate authority validation.

Treat these as current repository facts, not as proof that the module is complete. Re-read current main in case newer commits exist.

## Recovery objective

Finish the original V3 functional/module scope end-to-end and produce the durable implementation RESULT/claim closeout that the stopped worker did not finish.

Required final behavior remains:

- explicit `capture_raw_segmented_session` action;
- bounded long sessions materially beyond the legacy 60-second burst;
- deterministic automatic segmentation;
- per-segment capture/session identity, index, timestamps, frame range, requested/achieved Hz, frame count, bytes, raw SHA-256, optional gzip SHA-256, terminal segment state;
- authoritative ordered session manifest;
- strict `taskId + taskBlobSha + capture/session + source/runtime identity` binding;
- missing/duplicate/reordered/corrupt/hash-mismatched segment cannot produce COMPLETE;
- runtime/session identity drift/disappearance/ambiguity stops capture fail-closed and preserves completed segments as PARTIAL/FAILED evidence;
- interruption durability / atomic checkpoint behavior;
- local-only default retention;
- optional per-segment gzip remote handoff with exact original/compressed hashes and size boundaries;
- structured scene metadata preserved as descriptive provenance only;
- snapshot and <=60s burst backward compatibility;
- one WinKawaks owner / operator gate / serialized queue semantics preserved;
- `readOnly=true`, `writesGameMemory=false`, `inputInjection=false`;
- Browser / WinKawaks / Training Farm provenance never silently mixed.

## Priority checks for the recovery tail

Pay particular attention to the area the stopped worker was still hardening:

1. serialized/public terminal result must remain cryptographically/integrity bound to local manifest and ordered segment evidence;
2. stale/replayed/duplicate terminal result must not bypass current local segmented authority;
3. local manifest replacement/mutation, missing segment, duplicate segment, order change, raw hash mismatch or gzip hash mismatch must fail closed;
4. exact task identity and exact source/runtime identity must be enforced through terminal serialization;
5. partial/interrupted evidence must never be upgraded to COMPLETE merely because a public result says DONE/COMPLETE.

If current code already satisfies an item, verify with implementation-owned self-checks instead of rewriting it.

## Self-check and testing cadence

This is still implementation recovery, not independent QA.

Run only implementation-owned checks needed to establish a coherent candidate, such as:

- Python compile/parse;
- current Collector unit/regression tests;
- segmented-session deterministic fake/mock tests;
- strict malformed/coercible/non-finite parameter tests;
- segment order/hash/manifest consistency;
- serialized result/local evidence binding;
- replay/duplicate/stale result fail-closed;
- identity drift -> PARTIAL/FAILED;
- interruption preserves completed segments;
- snapshot/burst compatibility;
- read-only/no-input invariants.

Fix concrete defects found by these checks inside the recovery scope. Do not create Fresh QA / cross-check / second opinion / QA V2/V3/V4 from this task.

## Durable completion

Before COMPLETE, write a concise durable implementation RESULT under `parallel/PM/**` that records at minimum:

- exact final `wof-winkawaks-bridge` candidate HEAD;
- changed implementation/docs/test blobs relevant to V3;
- final action/schema and limits;
- segment and session manifest authority contract;
- task/source/runtime identity binding;
- duplicate/replay/serialized-result behavior;
- interruption/partial behavior;
- structured metadata behavior;
- backward compatibility;
- self-check commands/results;
- any limitation requiring the Owner's real WinKawaks runtime rather than repository fixtures.

Then close the Recovery claim/stage correctly under canonical dedup v2. Preserve historical truth: do not rewrite the stopped original worker as if it completed normally.

Collector remains an independent side lane and must not block Alpha V1 or the current Training Farm/10-worker lane.

## Stop

Do not stop at an intermediate milestone. Keep implementation reporting sparse. Continue through the complete assigned functional/module scope, implementation-owned self-checks, durable RESULT and required claim/stage closeout. Stop only at:

`COMPLETE — WINKAWAKS COLLECTOR V3 LONG-SESSION SEGMENTED CAPTURE MODULE — COHERENT IMPLEMENTATION / MANIFEST / SELF-CHECK COMPLETE`

or:

`BLOCKED — WINKAWAKS COLLECTOR V3 LONG-SESSION SEGMENTED CAPTURE MODULE — <precise unavoidable blocker>`

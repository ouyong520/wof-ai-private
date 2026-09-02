# WinKawaks Collector V3 — Long-Session Segmented Capture Module

stageId: `WINKAWAKS_COLLECTOR_V3_LONG_SESSION_SEGMENTED_CAPTURE_V1`
dedupProtocol: `v2`
dedupKey: `winkawaks.collector.v3.long-session-segmented-capture`
dedupMode: `exclusive`

Priority: **R&D accelerator / collection capability**

## Owner directive / testing cadence

Follow `parallel/PM/TESTING_CADENCE_POLICY.md`.

This is an implementation module, not a QA stage. Complete the whole functional module first. During development, run only implementation-owned syntax/unit/narrow regression/self-checks needed to avoid committing broken code. Do **not** open or request Fresh QA, second-opinion, cross-check, closeout QA, or retest stages from inside this task.

## Purpose

Upgrade the existing read-only WinKawaks Collector so one queued task can capture a long local WOF session without relying on one oversized raw file.

Current authoritative Collector v1 only supports:

- `capture_raw_snapshot`
- `capture_raw_burst`

with burst duration capped at 60 seconds. Keep those actions backward-compatible.

Add one coherent V3 long-session segmented-capture capability that is useful for large local evidence acquisition while preserving the existing single-owner/read-only/raw-first contract.

## Repositories

PM / contract authority:

`ouyong520/wof-ai-private`

Implementation target:

`ouyong520/wof-winkawaks-bridge`

Before implementation, re-read current `main` in both repositories and at minimum:

- `parallel/PM/TESTING_CADENCE_POLICY.md`
- `parallel/PM/STAGE_DEDUP_GUARD.md`
- `COLLECTOR_ROUTING.md`
- `ouyong520/wof-winkawaks-bridge/docs/COLLECTOR_V1_CONTRACT.md`
- current `bridge/collector_*` implementation
- current raw handoff / queue / status / result code
- recent Collector commits/results

If equivalent long-session segmented capture is already complete, stop `ALREADY COMPLETE — SAFE TO CLOSE`.

Otherwise acquire canonical dedup v2 ownership before substantive work.

## Functional module requirements

### 1. New long-session action

Add a new explicit task action for long read-only sessions, preferably a stable name such as:

`capture_raw_segmented_session`

Do not overload or silently change existing snapshot/burst semantics.

The task must define at minimum:

- total requested duration;
- target Hz;
- segment/chunk duration;
- raw retention mode;
- optional structured acquisition metadata / scene label.

Use strict primitive validation and fail closed on malformed/coercible/non-finite values.

Choose bounded limits from current Collector/runtime facts; do not invent unlimited capture. Long-session limits should be materially larger than the current 60-second burst while remaining safe for the local single-owner runtime.

### 2. Segmented raw artifacts

A long session must not depend on one huge JSONL artifact.

Implement deterministic per-segment artifacts with:

- session/capture ID;
- segment index;
- segment start/end timestamps;
- frame sequence range;
- requested/achieved Hz;
- frame count;
- byte count;
- raw SHA-256;
- gzip SHA-256 when uploaded;
- exact source/session identity metadata;
- explicit COMPLETE / PARTIAL / FAILED segment state.

Preserve the existing raw frame layout and raw-first principle unless repository facts require a versioned extension.

### 3. Session manifest

Produce one authoritative long-session manifest/result that binds all segments in order.

The manifest must include at minimum:

- taskId + taskBlobSha;
- capture/session ID;
- collector version;
- source/runtime identity;
- requested duration / target Hz / segment duration;
- total frames / total bytes;
- ordered segment list with exact hashes;
- first/last timestamps;
- achieved aggregate rate;
- read/frame-size error totals;
- whether runtime identity stayed continuous;
- raw retention mode;
- readOnly=true;
- writesGameMemory=false;
- no AI/rule execution;
- terminal state and precise failure reason when incomplete.

A serialized public result must never claim COMPLETE when any required segment is missing, mismatched, duplicated, reordered, or corrupted.

### 4. Runtime/session identity continuity

Do not allow a single long-session manifest to silently splice different WinKawaks sessions/runtime identities.

At segment boundaries, re-check the current authoritative runtime/session identity using existing Collector discovery/identity mechanisms.

If identity changes, disappears, becomes ambiguous, or cannot be proven continuous:

- stop the long capture fail-closed;
- retain already completed segments as partial evidence;
- publish terminal PARTIAL/FAILED result with exact reason;
- never label cross-session data as one coherent capture.

### 5. Crash / interruption durability

Design the module so a mid-session process interruption does not erase all completed work.

At minimum:

- completed segments are durably finalized before advancing;
- manifest/checkpoint state is updated atomically or with equivalent safe replacement semantics;
- restart must not silently append to an old task unless exact task/session/manifest authority permits it;
- duplicate/replayed task handling remains deterministic.

A full automatic resume feature is optional unless it can be implemented cleanly without weakening authority. Fail-closed restart with preserved partial evidence is acceptable.

### 6. Raw handoff / GitHub size handling

Preserve the existing default local-only behavior.

When remote raw upload is requested:

- upload segments individually rather than building one oversized archive;
- preserve the existing per-artifact GitHub size safety boundary;
- record exact original/compressed hashes and sizes per segment;
- if one segment cannot be uploaded safely, fail/partial clearly instead of truncating or pretending success.

Do not commit ROM, BIOS, game assets, emulator binaries, or unrelated large generated data.

### 7. Reusable capture metadata

Add a compact optional metadata block so future research can safely understand what was intentionally collected without inferring scene conditions from bytes.

Support fields such as:

- sceneLabel;
- player configuration / occupancy if supplied;
- operator action / scenario description;
- intentional changed variable;
- intentional held-stable variables;
- intended research question;
- known confounders / notes.

This metadata is descriptive only and must not become gameplay/rule authority.

### 8. Backward compatibility

Existing Collector v1/v2 workflows must continue to work:

- snapshot;
- <=60s burst;
- queue serialization;
- one WinKawaks owner;
- operator gate;
- taskId + taskBlobSha result binding;
- local raw retention;
- optional gzip upload;
- Chinese one-window operator UX where currently present.

Do not require consumers to migrate existing tasks merely to retain current behavior.

### 9. Read-only / research boundary

Hard invariants:

- read-only memory access only;
- `writesGameMemory=false`;
- no gameplay input injection;
- no Future Danger rule execution;
- no AI policy/decision logic in Collector;
- single local WinKawaks owner remains authoritative;
- Browser/WASM and WinKawaks namespaces remain separate.

## Implementation scope

Primary writes should stay in `ouyong520/wof-winkawaks-bridge` Collector code/docs/tests required by this module.

PM claim/result metadata may be written under `ouyong520/wof-ai-private/parallel/PM/**` as required by canonical dedup v2.

Do not modify:

- `product/alpha/**`;
- Alpha release/proof tooling;
- Transport;
- PYLAUNCH;
- Recorder Browser/WOF release runtime;
- Training Farm emulator adapter;
- production danger rules.

## Development self-checks

Complete the whole module before stopping. Run only implementation-owned checks, for example:

- Python compile/parse;
- existing Collector unit/regression suite relevant to changed code;
- new deterministic segmented-session tests using fake/mock raw source;
- malformed numeric/type validation;
- segment ordering/hash/manifest consistency;
- identity-change -> PARTIAL/FAILED fail-closed;
- interrupted session preserves completed segments;
- existing snapshot/burst compatibility regression;
- readOnly / writesGameMemory=false invariants.

These are self-checks under the implementation stage, **not independent QA**.

## Durable result

Write a concise durable implementation RESULT describing:

- final action/schema;
- exact changed implementation files/blobs;
- segment/manifest contract;
- compatibility behavior;
- self-check results;
- any real-runtime limitation not provable without the Owner's WinKawaks machine.

Do not schedule a separate QA from this task. Under the new testing cadence, this Collector module should be independently tested later only at a meaningful Collector functional boundary, preferably together with any closely related Collector development finished in the same phase.

## Stop

Success:

`COMPLETE — WINKAWAKS COLLECTOR V3 LONG-SESSION SEGMENTED CAPTURE MODULE — COHERENT IMPLEMENTATION / MANIFEST / SELF-CHECK COMPLETE`

Blocked:

`BLOCKED — WINKAWAKS COLLECTOR V3 LONG-SESSION SEGMENTED CAPTURE MODULE — <precise implementation blocker>`

# WinKawaks Collector V5 — Long-run Storage & Retention Manager

stageId: `WINKAWAKS_COLLECTOR_V5_LONG_RUN_STORAGE_RETENTION_MANAGER_V1`
dedupProtocol: `v2`
dedupKey: `winkawaks.collector.v5.long-run-storage-retention-manager`
dedupMode: `exclusive`

Priority: **P1 large-scale acquisition / storage durability**

## Read first

- `parallel/PM/COLLECTOR_WORKER_EXECUTION_POLICY.md`
- `parallel/PM/TESTING_CADENCE_POLICY.md`
- `parallel/PM/STAGE_DEDUP_GUARD.md`
- `COLLECTOR_ROUTING.md`
- `RUNTIME_DATA_SOURCE_BOUNDARIES.md`
- `parallel/BASECAP/BASE_CAPTURE_CATALOG.md`
- `parallel/PM/WINKAWAKS_COLLECTOR_V3_LONG_SESSION_SEGMENTED_CAPTURE_RECOVERY_V2_RESULT.md`
- `parallel/PM/WINKAWAKS_COLLECTOR_V4_DATASET_CATALOG_CAPTURE_IDENTITY_INDEX_RECOVERY_V3_RESULT.md`
- current `ouyong520/wof-ai-private/main`
- current `ouyong520/wof-winkawaks-bridge/main`

Current Collector module authority:

- V3 segmented long-session capture is COMPLETE;
- V4 dataset catalog / capture identity index is COMPLETE at bridge `c48cdd03b0136247d794078d879a868d10e1f49c`;
- V4 Recovery V3 is the durable completed successor authority;
- the later staged `...RECOVERY_V4_START_PROMPT.md` never acquired a recovery-v4 canonical claim and must not be run or treated as newer authority.

This is a new implementation module, not QA.

Acquire canonical dedup v2 ownership before substantive work. If an equivalent current module already exists and is complete, stop duplicate/already-complete rather than reimplementing it.

## Purpose

Make Collector safe for sustained large-scale local acquisition without filling the disk, losing partial evidence, deleting the only authoritative copy, or forcing the Owner to manually manage hundreds of capture artifacts.

The V5 manager is a **storage/retention layer** over completed Collector evidence. It must reuse V3 integrity authority and V4 catalog identity rather than inventing a second capture-validity system.

Target operating principle:

`capture -> finalize immutable evidence -> catalog -> account storage -> archive/preserve according to policy -> prune only when another verified copy exists and policy explicitly permits it`

## Primary implementation target

Prefer reusable Collector tooling under:

`ouyong520/wof-winkawaks-bridge`

PM claim/result metadata may be written only under:

`ouyong520/wof-ai-private/parallel/PM/**`

Do not modify Alpha V1 or Training Farm runtime/policy.

## Required module capabilities

### 1. Versioned storage policy schema

Define one versioned machine-readable storage/retention policy.

At minimum support bounded settings for:

- storage root(s);
- archive root;
- minimum free-space reserve;
- warning threshold / block-new-capture threshold;
- optional total Collector storage budget;
- optional retention age/budget rules;
- archive enable/disable;
- prune enable/disable;
- grace period before destructive source pruning;
- lifecycle classes eligible for pruning;
- pin/protect rules;
- partial/failed evidence preservation rules;
- dry-run/default-safe behavior.

All numeric values must be strict primitive finite non-negative values with sensible bounded limits. Unknown policy keys fail closed.

The default policy must be conservative and non-destructive.

### 2. Storage accounting and discovery

Provide deterministic accounting for Collector-owned retained evidence, including where present:

- legacy snapshot/burst raw artifacts;
- V3 segmented session directories, manifests and raw segments;
- local gzip/remote metadata references;
- V4 catalog/index files;
- archive copies created by V5;
- partial/interrupted session evidence;
- orphan/unindexed Collector artifacts.

Do not count unrelated repository/game/emulator files as Collector-owned merely because they are under the same disk.

Report exact byte totals and per-dataset/per-session storage where authority permits.

### 3. Disk-pressure health states

Expose stable health states such as:

- `HEALTHY`;
- `WARNING`;
- `BLOCK_NEW_CAPTURE`;
- `CRITICAL`.

Health must be derived from exact available disk space plus configured reserve/budget, not from guesswork.

Produce structured JSON including at minimum:

- free bytes;
- Collector-owned bytes;
- configured reserve/budget;
- current pressure state;
- protected bytes;
- archive backlog bytes;
- prune-candidate bytes;
- partial evidence bytes;
- unindexed/orphan bytes;
- integrity/storage conflicts;
- timestamp and policy identity/hash.

### 4. Capture budget guard

Integrate a narrow preflight/continuation budget guard with Collector capture execution where repository facts permit it.

Before starting a new raw capture, and for V3 long sessions at safe segment boundaries, Collector must be able to determine whether enough disk reserve remains to continue safely.

Requirements:

- use current task parameters and known current raw frame/layout facts where available;
- use conservative bounded estimates rather than optimistic guesses;
- preserve configured minimum reserve;
- reject or stop before disk exhaustion;
- V3 already-finalized segments remain preserved;
- insufficient disk during a long session yields precise `PARTIAL`/`FAILED` storage-pressure reason according to existing V3 semantics;
- never splice/retry into another session merely because disk space later changes.

Do not weaken V3 runtime/session/segment integrity authority.

### 5. Exact byte-preserving archive

Implement local archive of immutable Collector datasets/session evidence without silently changing capture identity.

Archive behavior must:

- copy/move the exact authoritative artifact set for one dataset/session;
- preserve exact bytes and hashes;
- verify destination size/hash before considering archive complete;
- write an archive receipt/record binding datasetId/task/capture/session identity, source paths, destination paths, bytes/hashes, policy identity and timestamps;
- use temporary path + fsync + atomic finalize or equivalent crash-safe semantics;
- fail closed on partial copy, hash mismatch, path collision or pre-existing different bytes;
- never overwrite a different archival artifact.

Do not recompress or transform authoritative raw bytes merely for convenience unless a versioned, hash-preserving repository contract already exists. V5 archive should default to exact byte-preserving relocation/copy.

### 6. Two-phase prune safety

Pruning must be separate from archive and must never silently delete the sole authoritative copy.

A source artifact may be pruned only when all required conditions hold:

1. policy explicitly allows pruning;
2. the dataset/session is not active/in-progress;
3. required grace period is satisfied;
4. the exact archive copy is independently reverified;
5. at least one verified authoritative copy remains after prune;
6. dataset identity and archive receipt still match current V4/V3 authority;
7. the artifact is not pinned/protected;
8. lifecycle/policy class is eligible;
9. no current lock/ownership conflict exists.

Default behavior must be `plan/dry-run` rather than destructive apply.

Destructive apply must require an explicit CLI flag/action and emit an exact structured operation record.

Never use recursive broad deletion against an unconstrained path.

### 7. Partial/interrupted evidence protection

Partial evidence is valuable research evidence and must not be treated as garbage by default.

Requirements:

- active/in-progress sessions are never archived/pruned destructively;
- finalized V3 partial segments and checkpoint remain discoverable;
- recent partial/failed evidence is protected by default;
- policy may later archive partial evidence exactly;
- destructive pruning of partial/failed evidence requires explicit policy eligibility plus the same verified-copy guarantees;
- a storage manager action must never upgrade PARTIAL/FAILED to COMPLETE.

### 8. Pins / protected canonical datasets

Support an explicit storage protection surface independent of gameplay semantics.

At minimum:

- canonical BASECAP `VALID` reusable datasets should be protected by default unless explicit policy says otherwise;
- allow manual dataset/session pinning by immutable V4 dataset ID or authoritative task/capture identity;
- pins do not alter V4 dataset identity or semantic lifecycle;
- pin state belongs to storage policy/metadata only.

Do not infer pins from raw bytes or filenames.

### 9. V4 catalog integration

Reuse V4 immutable dataset IDs and lifecycle/integrity separation.

V5 may expose storage availability metadata such as:

- local present;
- archived present;
- remote reference present;
- source pruned after verified archive;
- bytes by location;
- archive receipt identity.

But V5 must not silently change:

- `VALID / INVALID / SUPERSEDED / UNREVIEWED` semantic lifecycle;
- V4 capture identity;
- V3 COMPLETE/PARTIAL/FAILED authority.

Storage location is not gameplay or semantic authority.

### 10. Orphan / conflict handling

Detect but do not guess when Collector-owned artifacts cannot be reconciled with V4 catalog or V3/legacy authority.

Classify clearly, for example:

- unindexed but structurally recognizable;
- missing catalog reference;
- missing local artifact;
- archive receipt mismatch;
- hash mismatch;
- duplicate path/content conflict;
- unknown ownership.

Unknown/conflicting evidence is never automatically deleted.

Provide a structured remediation/plan output.

### 11. Deterministic plan/apply/verify/status CLI

Provide a practical CLI/module following repository conventions, with conceptual operations such as:

- `status`;
- `plan`;
- `archive` or `apply`;
- `verify`;
- `prune`;
- `show`.

Exact names may follow current conventions.

Requirements:

- JSON output option suitable for future automation;
- deterministic ordering;
- idempotent rerun on unchanged state;
- lock/serialization for mutating operations;
- explicit dry-run;
- exact operation IDs/receipts;
- clear exit codes/reasons;
- no last-writer-wins conflict resolution.

### 12. Crash / concurrency durability

Mutating storage actions must survive interruption without making evidence look complete when it is not.

At minimum:

- operation journal/receipt state;
- temporary archive destinations are not authoritative until verified/finalized;
- lock protects concurrent archive/prune managers;
- restart can classify incomplete operations safely;
- incomplete archive never authorizes source prune;
- repeated apply is deterministic/idempotent where possible.

### 13. Path and filesystem safety

Fail closed on:

- path traversal;
- archive root escaping;
- symlink/reparse-point ambiguity where it could redirect destructive operations;
- same source/destination aliasing;
- destination collision with different bytes;
- unexpected file type;
- filesystem errors;
- non-atomic unsafe replacement where it would weaken evidence durability.

Do not delete ROM/BIOS/emulator/game assets or unrelated files under any condition.

### 14. Side-lane isolation

Hard boundaries:

- no `product/alpha/**` changes;
- no Alpha release/proof/runtime changes;
- no Transport/Recorder/PYLAUNCH/OneClick changes;
- no Training Farm runtime, action, PPO/RL, 10-worker scheduling or savestate changes;
- no gameplay input injection;
- no game-memory writes;
- no ROM/BIOS/game asset commits;
- Browser / WinKawaks / Training Farm provenance stays separate.

Collector remains:

```text
readOnly=true
writesGameMemory=false
inputInjection=false
```

Collector V5 incomplete or blocked is not an Alpha V1 or Training Farm/10-worker blocker.

## Implementation-owned self-checks

Finish the coherent module first, then run necessary implementation self-checks.

Cover at least:

- policy schema strict validation;
- deterministic storage accounting;
- free-space pressure thresholds;
- capture budget preflight;
- V3 segment-boundary disk-pressure partial stop;
- exact archive copy/hash verification;
- destination collision fail-closed;
- interrupted archive cannot authorize prune;
- no sole-copy deletion;
- pin/protection behavior;
- BASECAP canonical protection;
- partial evidence preservation;
- archive receipt mismatch rejection;
- orphan/conflict no-delete behavior;
- dry-run vs explicit destructive apply;
- idempotent rerun;
- concurrent lock behavior;
- path traversal/symlink safety where testable;
- V3/V4 regression compatibility;
- read-only/no-input boundaries.

Do not open Fresh QA, cross-check, second opinion, QA V2/V3/V4/V5, readiness audit, Browser/WOF test, real WinKawaks capture, or Training Farm test from this implementation task.

If self-check finds concrete defects, fix the related V5 defect cluster and rerun the affected checks; do not multiply QA stages.

## Durable completion

Before COMPLETE, write a durable RESULT under `parallel/PM/**` recording at minimum:

- exact final bridge HEAD/tree;
- exact changed files/blobs;
- storage policy schema/version;
- disk pressure state contract;
- capture budget guard contract;
- archive receipt/authority contract;
- prune safety rules;
- partial/pin protection behavior;
- V4 catalog integration;
- orphan/conflict behavior;
- CLI/status JSON surface;
- crash/concurrency/path safety;
- implementation-owned self-check commands/results;
- any remaining real-runtime/local-filesystem limitation.

Close canonical and stage claims correctly under canonical dedup v2.

## Stop

Do not stop at claim acquisition, repository inspection, one patch, one helper, one test run, or documentation-only progress.

Keep implementation reporting sparse. Continue through the complete V5 storage/retention functional module, integration, implementation-owned self-checks, documentation, durable RESULT and claim/stage closeout.

Do not move on to V6 from this worker.

Stop only at:

`COMPLETE — WINKAWAKS COLLECTOR V5 LONG-RUN STORAGE & RETENTION MANAGER — SAFE LARGE-SCALE LOCAL RETENTION MODULE COMPLETE`

or:

`BLOCKED — WINKAWAKS COLLECTOR V5 LONG-RUN STORAGE & RETENTION MANAGER — <precise unavoidable blocker>`

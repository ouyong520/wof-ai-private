# WinKawaks Collector V5 — Long-run Storage & Retention Manager Recovery V2

stageId: `WINKAWAKS_COLLECTOR_V5_LONG_RUN_STORAGE_RETENTION_MANAGER_RECOVERY_V2`
dedupProtocol: `v2`
dedupKey: `winkawaks.collector.v5.long-run-storage-retention-manager.recovery-v2`
dedupMode: `exclusive`

Priority: **P1 large-scale acquisition / storage durability recovery**

## Read first

- `parallel/PM/WINKAWAKS_COLLECTOR_V5_LONG_RUN_STORAGE_RETENTION_MANAGER_START_PROMPT.md`
- `parallel/PM/COLLECTOR_WORKER_EXECUTION_POLICY.md`
- `parallel/PM/TESTING_CADENCE_POLICY.md`
- `parallel/PM/STAGE_DEDUP_GUARD.md`
- `COLLECTOR_ROUTING.md`
- `RUNTIME_DATA_SOURCE_BOUNDARIES.md`
- `parallel/PM/WINKAWAKS_COLLECTOR_V3_LONG_SESSION_SEGMENTED_CAPTURE_RECOVERY_V2_RESULT.md`
- `parallel/PM/WINKAWAKS_COLLECTOR_V4_DATASET_CATALOG_CAPTURE_IDENTITY_INDEX_RECOVERY_V3_RESULT.md`
- current original V5 canonical/stage claims
- current `ouyong520/wof-ai-private/main`
- current `ouyong520/wof-winkawaks-bridge/main`

This is PM-authorized **implementation recovery** for the stopped V5 worker. It is not Fresh QA and must not restart V5 from zero.

The original V5 canonical claim remains historical `ACTIVE` because the worker stopped before durable RESULT/claim closeout. Recovery V2 must acquire its own canonical dedup v2 recovery claim/stage and supersede the stopped generation only when the module is genuinely complete.

## Current implementation facts to preserve

At recovery staging time, `ouyong520/wof-winkawaks-bridge/main` is `c66d7cd73b33fb084c5d620fd6911dacb977363b` and already contains substantial V5 implementation:

- `5958311c04743da005e406681e9c3eb4e138152b` — conservative storage policy;
- `a9f0bb52a87d74d8521f8067745f4b5e44d1d7a6` — storage policy schema;
- `bdab7fb166b62addff45e45cb28ba1ef0c3f304e` — storage policy/authority core;
- `adc3b3921fb4c82419739728ce555241569bc0ca` — storage accounting and capture pressure guard;
- `3af11f77dd4f3c53f2072ca6facd6111342a7801` — exact archive and two-phase prune;
- `b898fc99ae3e0dcffdc8cfaeab897ff65884fa64` — storage retention CLI and health status;
- `8fdbef87cdb63f92afd7d24e2ae6842e924603ad` — raw capture storage-pressure guard;
- `e84cea7938636f137813138a38ddc998b2858833` — V5 implementation regressions;
- `9ac839fe6083b42dab3c50843b0172370294cc80` — storage/retention contract docs;
- `c66d7cd73b33fb084c5d620fd6911dacb977363b` — V5 storage self-check integrated into Collector smoke.

Re-read current HEAD before changing anything. Preserve all valid landed implementation. Do not reimplement already-complete V5 surfaces merely because the original worker stopped.

## Recovery objective

Finish the original V5 module end-to-end from current HEAD, fixing only concrete remaining gaps in implementation, authority, integration, self-check, documentation consistency, or durable closeout.

The completed module must still satisfy the original V5 contract, especially:

- strict versioned conservative storage policy;
- deterministic Collector-owned storage accounting without counting unrelated files;
- stable `HEALTHY / WARNING / BLOCK_NEW_CAPTURE / CRITICAL` pressure states;
- conservative capture budget guard before new capture and at V3 safe segment boundaries;
- exact byte/hash-preserving archive with crash-safe receipt/finalization;
- two-phase prune with dry-run default and explicit destructive apply;
- no deletion of sole authoritative copy;
- active/in-progress and recent partial/failed evidence protection;
- BASECAP/canonical dataset protection and explicit immutable-ID pinning;
- V4 dataset identity/lifecycle authority reused rather than duplicated;
- V3 COMPLETE/PARTIAL/FAILED authority never changed by storage actions;
- orphan/conflicting/unknown evidence detected but never guessed/deleted;
- deterministic JSON-capable status/plan/apply/archive/verify/prune/show CLI according to final repository conventions;
- mutation serialization/locking and interruption-safe operation records;
- path traversal, archive-root escape, aliasing, collision, unexpected-file and symlink/reparse ambiguity fail-closed;
- read-only/no-input Collector boundary preserved.

## Recovery-tail priority checks

Because most implementation has already landed, prioritize validating and closing the module boundary rather than adding unrelated features.

Verify current HEAD for these specific risks:

1. policy schema, default policy, docs and runtime parser agree exactly;
2. strict primitive finite numeric validation and unknown-key rejection cannot be bypassed by coercion;
3. disk-pressure thresholds and budget guard are monotonic and fail closed at exact boundaries;
4. V3 long-session storage-pressure stop preserves already-finalized segments and returns existing PARTIAL/FAILED semantics without session append/retry;
5. archive receipt binds exact dataset/task/capture/session identity, source/destination paths, bytes/hashes and policy identity;
6. incomplete/failed archive can never authorize prune;
7. archive destination collision or same-source/destination alias never overwrites different evidence;
8. prune requires verified surviving authoritative copy, eligibility, grace period, not-active state and no pin/protection;
9. dry-run/plan cannot mutate or delete;
10. repeated archive/prune/apply on unchanged state is deterministic/idempotent where promised;
11. active/recent partial evidence and BASECAP protected data cannot fall through generic cleanup rules;
12. orphan/conflict classification never becomes an implicit delete candidate;
13. lock/journal/restart behavior cannot make an interrupted operation look complete;
14. filesystem/path safety cannot escape Collector-owned roots or touch ROM/BIOS/emulator/game/unrelated files;
15. storage metadata does not mutate V4 semantic lifecycle/capture identity or V3 terminal authority;
16. V3/V4 compatibility and current smoke workflow remain green;
17. current docs/CLI/schema/tests/default policy are mutually consistent.

If implementation-owned self-check exposes a concrete defect, fix that defect cluster inside V5 and rerun only affected checks plus the final coherent module self-check.

## Testing cadence

This is implementation recovery, **not independent QA**.

Do not create Fresh QA, cross-check, second opinion, QA V2/V3/V4/V5, readiness audit, Browser/WOF testing, real WinKawaks recapture, or Training Farm testing.

Use only implementation-owned checks required to finish the coherent V5 candidate, including as appropriate:

- compile/parse;
- V5 storage retention regression suite;
- strict policy/schema validation;
- pressure threshold/budget guard checks;
- archive/hash/receipt/collision/interruption checks;
- prune sole-copy/pin/partial/dry-run checks;
- orphan/conflict/path/locking checks;
- V3 segmented regression compatibility;
- V4 catalog regression compatibility where V5 integration depends on it;
- current `Collector Python smoke check`.

Do not multiply test stages. Complete implementation first, run one necessary module-boundary self-check, fix real failures, then close.

## Side-lane isolation

This task must not modify or block:

- `product/alpha/**`;
- Alpha V1 release/acceptance/proof/runtime;
- Transport / Recorder / PYLAUNCH / OneClick;
- Training Farm runtime/policy/savestate/RL/action injection;
- current 10-worker training lane.

Collector remains:

- `readOnly=true`;
- `writesGameMemory=false`;
- `inputInjection=false`.

Browser, WinKawaks and Stable-Retro/FBNeo provenance remain distinct.

## Durable completion

Before COMPLETE, write a durable Recovery V2 RESULT under `parallel/PM/**` recording at minimum:

- exact final bridge HEAD/tree;
- exact V5 changed/current blobs;
- storage policy schema/version/default policy identity;
- disk-pressure state and capture-budget contract;
- archive receipt/authority contract;
- two-phase prune and sole-copy protection rules;
- partial/pin/BASECAP protection behavior;
- V4/V3 integration boundaries;
- orphan/conflict handling;
- CLI/status JSON surface;
- crash/concurrency/path safety;
- implementation-owned self-check commands/results and workflow run if used;
- any precise remaining real-filesystem/runtime limitation.

Then close Recovery V2 canonical claim and stage under canonical dedup v2. Preserve the stopped original V5 claim as historical truth; do not rewrite it as though that worker completed normally.

## Stop

Claim acquisition is only ownership and is not progress completion. Do not stop at claim/stage creation, repository inspection, one patch, one helper, one test run, or documentation-only work.

Keep reporting sparse. Continue through the complete V5 storage/retention module, remaining integration/fixes, implementation-owned self-checks, durable RESULT and required recovery claim/stage closeout.

Do not move on to V6 from this worker.

Stop only at:

`COMPLETE — WINKAWAKS COLLECTOR V5 LONG-RUN STORAGE & RETENTION MANAGER — SAFE LARGE-SCALE LOCAL RETENTION MODULE COMPLETE`

or:

`BLOCKED — WINKAWAKS COLLECTOR V5 LONG-RUN STORAGE & RETENTION MANAGER — <precise unavoidable blocker>`

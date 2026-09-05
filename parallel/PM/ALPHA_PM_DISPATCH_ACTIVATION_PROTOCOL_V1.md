# Alpha PM Dispatch Activation Protocol V1

Status: coordination-only PM protocol. It does not authorize Alpha product/runtime changes.

## 1. Purpose

C5 makes `parallel/PM/CURRENT_DISPATCH.json` readable and fail-closed. C7 supplies the missing PM planning/verification side so PM does not hand-calculate manifest hashes, revisions, or `previousDispatch`.

Tool:

`parallel/PM/tools/alpha_pm_dispatch_activate.py`

The live pointer remains PM/coordinator-owned. The C7 tool never creates or updates `parallel/PM/CURRENT_DISPATCH.json`.

## 2. Trust chain reused by C7

A target activation is accepted for planning only when:

1. the target is a canonical direct child of `parallel/PM/DISPATCH_MANIFESTS/`;
2. C2 `alpha_pm_result_inbox.load_manifest` accepts the final immutable manifest;
3. C3 `alpha_worker_dispatch_contract.validate_dispatch` accepts manifest/prompt membership and result contracts;
4. the manifest filename is exactly `<dispatchId>.json`;
5. the exact manifest bytes are hashed by C7 and bound into the planned pointer;
6. when a current pointer exists, C5 `resolve_current_dispatch` accepts its ownership, repository, manifest hash, authority commit, and C2 identity before C7 consumes its revision/history.

C7 derives `manifestAuthorityCommit` from the validated target manifest and `manifestSha256` from the exact target bytes. No caller-supplied copy of either value becomes authority.

## 3. Plan a clean activation or transition

```text
python parallel/PM/tools/alpha_pm_dispatch_activate.py plan \
  --manifest parallel/PM/DISPATCH_MANIFESTS/<DISPATCH_ID>.json \
  --repo-root . \
  --pretty
```

Optional assertions:

- `--revision N` requires `N` to equal the exact next revision C7 derived;
- `--expected-authority-commit <40-hex>` rejects an unexpected target authority;
- `--expect-current-absent` rejects a surprise existing pointer;
- `--expected-current-sha256 <64-hex>` rejects stale current-pointer bytes;
- `--at-utc <UTC-Z>` exists for deterministic fixtures/replay and should normally be omitted by PM.

The plan emits:

- `operation: create|update`;
- target dispatch/manifest identity;
- exact next `revision`;
- exact `previousDispatch` snapshot, or `null` for first activation;
- `writeGuard.expectedOldState`;
- SHA-256 and Git blob SHA-1 of the old bytes when updating;
- SHA-256 and Git blob SHA-1 of the planned bytes;
- `plannedPointerJson`;
- `plannedPointerText`, the exact deterministic UTF-8 text PM must write.

The same inputs plus the same `--at-utc` produce byte-identical pointer text.

## 4. Revision and history rules

C7 does not ask PM to invent the next revision.

- No existing pointer -> `revision = 1`, `previousDispatch = null`.
- Valid existing pointer at revision `N` -> `revision = N + 1`.
- `previousDispatch` is copied from the validated current pointer's exact dispatch identity: `dispatchId`, `manifestPath`, `manifestAuthorityCommit`, `manifestSha256`, and `revision`.
- Re-activating the same `dispatchId` is rejected. A transition requires a new immutable dispatch identity, matching the C5 invariant that current and previous dispatch IDs differ.
- Any explicit `--revision` other than the exact derived next value fails closed.

## 5. Concurrency guard before PM write

For create plans, PM must preserve the `ABSENT` precondition:

```text
python parallel/PM/tools/alpha_pm_dispatch_activate.py guard \
  --repo-root . \
  --expect-absent
```

For update plans, PM rechecks the plan's `writeGuard.expectedOldSha256` immediately before writing:

```text
python parallel/PM/tools/alpha_pm_dispatch_activate.py guard \
  --repo-root . \
  --expected-old-sha256 <PLAN_EXPECTED_OLD_SHA256>
```

A mismatch means another PM/coordinator changed the pointer; discard the plan and re-plan from latest state.

When the actual repository write mechanism supports compare-and-swap, PM should also supply `writeGuard.expectedOldGitBlobSha1` as the expected old Git blob identity. That converts the content guard into the write API's own stale-write precondition rather than relying only on a pre-write check.

C7 itself never performs the live write, so PM must use a write mechanism that preserves this guard. Do not copy `plannedPointerText` into the live file after a failed or skipped guard.

## 6. Verify after PM writes

After PM writes the exact planned text, verify both bytes and C5 resolution:

```text
python parallel/PM/tools/alpha_pm_dispatch_activate.py verify \
  --repo-root . \
  --expected-pointer-sha256 <PLAN_PLANNED_POINTER_SHA256> \
  --expected-dispatch-id <DISPATCH_ID> \
  --expected-revision <REVISION> \
  --pretty
```

PASS requires:

1. the PM-written pointer bytes match the planned SHA-256 when supplied;
2. C5 can re-read and resolve the pointer against the exact manifest;
3. optional dispatch/revision assertions match.

C5 worker-result state does not redefine activation identity. A pointer can be structurally valid while workers are `NOT_FINISHED`; C7 reports C5's `pmAction` for continuation but does not infer worker completion.

## 7. Fail-closed conditions

Planning or verification rejects at least:

- malformed, mutable, draft, or C2-invalid target manifest;
- C3 dispatch/prompt contract failure;
- target path traversal, noncanonical location, or filename/dispatch mismatch;
- wrong repository identity;
- target authority assertion mismatch;
- malformed/stale existing pointer;
- existing pointer manifest hash or authority mismatch;
- current pointer changing while C5 validation is in progress;
- same-dispatch reactivation;
- revision regression/non-monotonic assertion;
- stale old-content guard;
- post-write pointer hash, dispatch, revision, or C5-resolution mismatch.

Any such failure means PM must not activate from that plan.

## 8. PM handoff sequence

The safe sequence is:

`latest main -> C7 plan -> review exact plan -> C7 guard -> PM guarded write -> C7 verify -> use C5/C2 worker truth`

This keeps the mutable pointer small and PM-owned while eliminating hand-maintained hash/revision/history state.

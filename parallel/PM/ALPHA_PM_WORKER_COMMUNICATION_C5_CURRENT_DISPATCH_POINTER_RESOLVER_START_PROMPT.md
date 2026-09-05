stageId: `ALPHA_PM_WORKER_COMMUNICATION_C5_CURRENT_DISPATCH_POINTER_RESOLVER`
dedupProtocol: `v2`
dedupKey: `alpha.pm.worker-communication.current-dispatch-pointer-resolver-v1`
dedupMode: `exclusive`
resultProtocol: `wof-alpha-worker-result-v1`
resultJsonPath: `parallel/PM/RESULTS/ALPHA_PM_WORKER_COMMUNICATION_C5_CURRENT_DISPATCH_POINTER_RESOLVER_RESULT.json`
resultMdPath: `parallel/PM/RESULTS/ALPHA_PM_WORKER_COMMUNICATION_C5_CURRENT_DISPATCH_POINTER_RESOLVER_RESULT.md`
terminalCommitPrefix: `WORKER_RESULT ALPHA_PM_WORKER_COMMUNICATION_C5_CURRENT_DISPATCH_POINTER_RESOLVER`
dispatchManifestPath: `parallel/PM/DISPATCH_MANIFESTS/ALPHA_PM_WORKER_COMMUNICATION_C4_C5_2_WORKER_V1.json`

# Alpha PM Worker Communication C5 — Current Dispatch Pointer + Resolver

Repository: `ouyong520/wof-ai-private`

Read latest main first, then:

- `parallel/PM/ALPHA_PM_WORKER_COMMUNICATION_C4_C5_2_WORKER_DISPATCH.md`
- `parallel/PM/ALPHA_PM_DISPATCH_CONTRACT_V1.md`
- `parallel/PM/ALPHA_PM_RESULT_INBOX_PROTOCOL_V1.md`
- `parallel/PM/ALPHA_WORKER_RESULT_FAST_FEEDBACK_PROTOCOL_V1.md`
- `parallel/PM/STAGE_DEDUP_GUARD.md`

Scope: PM/Worker coordination only. No Alpha product behavior changes. Collector / Unified Collector / Training Farm / 10训 are out of scope.

## Dedup

Perform latest-main dedup preflight. Create-only canonical claim, re-read exact claimToken/fields/state ACTIVE, then create-only stage claim and re-read exact token. Any failure is fail-closed. Do not invent recovery.

## Mission

Make Git sufficient to recover the current PM dispatch without chat memory. Define a PM-owned current-dispatch pointer contract plus a resolver that reaches one immutable dispatch manifest and then uses the C2 result-inbox semantics to expose exact worker RESULT status.

Desired PM fast path:

`parallel/PM/CURRENT_DISPATCH.json -> immutable manifest -> exact RESULT.json files -> PM action`

## Owned deliverables

Prefer new files only:

- `parallel/PM/schemas/alpha_current_dispatch_v1.schema.json`
- `parallel/PM/templates/alpha_current_dispatch_v1.json`
- `parallel/PM/tools/alpha_pm_current_dispatch.py`
- `parallel/PM/tests/test_alpha_pm_current_dispatch.py`
- `parallel/PM/ALPHA_PM_CURRENT_DISPATCH_PROTOCOL_V1.md`

You may add a bootstrap/example pointer under a clearly non-authoritative template/fixture path. Do not mutate a live PM pointer unless the prompt explicitly assigns a concrete current manifest after the contract is proven. Future product workers are forbidden from writing the PM-owned pointer.

## Pointer contract

The pointer must identify at least:

- schema/version;
- `pmOwned: true`;
- repository;
- current `dispatchId`;
- exact `manifestPath` under `parallel/PM/DISPATCH_MANIFESTS/`;
- manifest authority commit / expected identity sufficient to reject accidental redirection;
- update timestamp or revision metadata;
- optional previous-dispatch reference for auditability.

The pointer is mutable only by PM/coordinator. Worker RESULT files and ordinary workers must never update it.

## Resolver behavior

A CLI/library must:

1. load a specified pointer or the canonical future path `parallel/PM/CURRENT_DISPATCH.json`;
2. validate pointer schema and ownership marker;
3. reject traversal/external paths;
4. load the exact immutable manifest;
5. verify dispatchId/repository/authority identity against the pointer;
6. select slots such as `1`, `1 2`, `1 3` using the C2 manifest slot semantics;
7. delegate/reuse C2 result-inbox truth rules for COMPLETE/SUBCOMPLETE/BLOCKED/NOT_FINISHED/malformed result handling;
8. emit one concise machine-readable summary suitable for PM continuation;
9. never infer completion from chat, commit messages, claims, or Markdown when the exact RESULT.json is absent.

## Fail-closed cases

Cover missing pointer, malformed pointer, non-PM-owned pointer, missing manifest, immutable=false manifest, dispatchId mismatch, repository mismatch, path traversal, unsupported manifest schema, unknown slot, malformed RESULT, and stale/redirected identity.

Do not create a worker-owned global dashboard. This pointer is coordinator-owned routing metadata only.

## Focused tests

Cover pointer validation, exact manifest resolution, valid 1/2/3 slot shorthand, missing RESULT=NOT_FINISHED, COMPLETE/BLOCKED mix, malformed result, pointer/manifest mismatch, traversal, and a new-session scenario proving status can be reconstructed from Git files alone.

## Terminal reporting

Write exactly the RESULT.json/RESULT.md declared above. RESULT JSON must use the C1 schema and accurately list implementation commits, changed files, tests, integration readiness, blocker, and nextAction.

Final result commit prefix:

`WORKER_RESULT ALPHA_PM_WORKER_COMMUNICATION_C5_CURRENT_DISPATCH_POINTER_RESOLVER <STATE>`

Close your own canonical/stage correctly before COMPLETE. Chat only returns COMPLETE / SUBCOMPLETE / precise BLOCKED.

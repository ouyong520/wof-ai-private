stageId: `ALPHA_PM_WORKER_COMMUNICATION_C2_DISPATCH_MANIFEST_FAST_READER`
dedupProtocol: `v2`
dedupKey: `alpha.pm.worker-communication.dispatch-manifest-fast-reader-v1`
dedupMode: `exclusive`
resultProtocol: `wof-alpha-worker-result-v1`
resultJsonPath: `parallel/PM/RESULTS/ALPHA_PM_WORKER_COMMUNICATION_C2_DISPATCH_MANIFEST_FAST_READER_RESULT.json`
resultMdPath: `parallel/PM/RESULTS/ALPHA_PM_WORKER_COMMUNICATION_C2_DISPATCH_MANIFEST_FAST_READER_RESULT.md`
terminalCommitPrefix: `WORKER_RESULT ALPHA_PM_WORKER_COMMUNICATION_C2_DISPATCH_MANIFEST_FAST_READER`

# Alpha PM Worker Communication C2 — Dispatch Manifest / PM Fast Reader

Repository: `ouyong520/wof-ai-private`

Read first:
- latest `main`;
- `parallel/PM/ALPHA_PM_WORKER_GIT_COMMUNICATION_2_WORKER_DISPATCH.md`;
- `parallel/PM/ALPHA_WORKER_RESULT_FAST_FEEDBACK_PROTOCOL_V1.md`;
- `parallel/PM/STAGE_DEDUP_GUARD.md`.

Scope: Alpha PM/worker coordination only. No Alpha runtime/updater/HUD/renderer product behavior changes. Collector / Unified Collector / Training Farm / 10训 are out of scope.

## Mandatory dedup

Perform latest-main dedup preflight, create-only canonical claim, re-read and verify exact claimToken, create-only stage claim with the same token, then re-read and verify. Any create/verification failure is fail-closed. Do not invent recovery.

## Goal

Implement immutable dispatch manifests plus a PM fast-reader/inbox helper so PM can determine worker completion and next action by reading exact result paths instead of reconstructing chat/history.

## Architecture

A dispatch manifest is coordinator-created and immutable for one dispatch. It lists each worker's:

- `stageId`
- `promptPath`
- `dedupKey`
- `resultProtocol`
- `resultJsonPath`
- `resultMdPath`
- `terminalCommitPrefix`

Workers never edit the manifest and never update a shared mutable dashboard.

## Deliverables

Prefer coordination-only paths:

- `parallel/PM/schemas/alpha_dispatch_manifest_v1.schema.json`
- `parallel/PM/templates/alpha_dispatch_manifest_v1.json`
- `parallel/PM/tools/alpha_pm_result_inbox.py`
- `parallel/PM/tests/test_alpha_pm_result_inbox.py`
- `parallel/PM/ALPHA_PM_RESULT_INBOX_PROTOCOL_V1.md`

The reader/helper must support a local checkout path and one manifest file, and produce a compact JSON summary for every declared worker with one of:

- `NOT_FINISHED` when declared result JSON is missing;
- `SUBCOMPLETE`;
- `COMPLETE`;
- `BLOCKED`;
- `INVALID_RESULT` when a result exists but is malformed/inconsistent.

For terminal results, compact summary must expose at least:

- stageId
- state
- verdict
- integrationReady
- implementationCommits
- changedFiles
- tests summary
- productProof.status
- ownerGate.required/question
- blocker.code/ownerRequired/pmRequired
- nextAction
- resultJsonPath
- resultMdPath

The helper must fail closed on:

- path traversal / result path outside `parallel/PM/RESULTS/`;
- duplicate stageId;
- duplicate resultJsonPath;
- malformed manifest;
- mismatched result stageId;
- unsupported result protocol/state.

It must not require network access and must not mutate Git state or any manifest/result file.

## PM operating contract

Document the exact fast path:

1. PM reads current immutable dispatch manifest.
2. PM/direct tooling checks declared result JSON paths.
3. Missing result = worker not terminal; no guessing.
4. Existing JSON = first source for state/verdict/commits/tests/blocker/next action.
5. PM reads result Markdown only for deeper evidence.
6. PM inspects implementation commits only when accepting/integrating.
7. Chat text is convenience only, never authority.

## Focused tests

Cover mixed dispatch with COMPLETE/BLOCKED/NOT_FINISHED workers, malformed result, stage mismatch, duplicate paths, traversal rejection, and deterministic compact summary.

## Terminal reporting

Follow `parallel/PM/ALPHA_WORKER_RESULT_FAST_FEEDBACK_PROTOCOL_V1.md` using the exact result paths declared above. Final result commit must begin with:

`WORKER_RESULT ALPHA_PM_WORKER_COMMUNICATION_C2_DISPATCH_MANIFEST_FAST_READER <STATE>`

Close your own canonical/stage claim correctly before reporting COMPLETE. Return only COMPLETE/SUBCOMPLETE or precise BLOCKED.
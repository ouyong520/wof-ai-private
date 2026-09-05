# Alpha Worker Finish Protocol V1

Status: coordination-only terminal publisher for the Alpha PM ↔ Worker Git loop.

This protocol does not change dedup ownership, dispatch authority, Alpha runtime/product behavior, or PM result precedence. The worker still owns claim closeout under `parallel/PM/STAGE_DEDUP_GUARD.md`; this publisher only turns one compact finish payload plus immutable Git authority into the exact terminal RESULT pair.

## Command

```text
python parallel/PM/tools/alpha_worker_finish.py publish \
  --manifest parallel/PM/DISPATCH_MANIFESTS/<DISPATCH_ID>.json \
  --slot <N> \
  --input <finish.json> \
  --repo-root .
```

Start from `parallel/PM/templates/alpha_worker_finish_input_v1.json` and change only worker-variable result fields. Do not put `stageId`, `dedupKey`, `claimToken`, `startCommit`, RESULT paths, or terminal commit prefix into the finish payload; those are resolved from the immutable manifest and Git claims.

## Required terminal sequence

1. Finish implementation and the minimum implementation-owned self-check.
2. Close or retain the worker's canonical/stage claims exactly as required for the intended terminal state.
3. Run the publisher once.
4. Commit the two create-only artifacts using the exact subject printed by the publisher: `WORKER_RESULT <stageId> <STATE>`.
5. PM reads the manifest-declared `RESULT.json` first. Existing status/call-sign evidence remains fallback only; dedicated worker follow-up remains last resort.

The publisher never pushes Git commits and never mutates claims.

## Authority resolution

The publisher validates the immutable dispatch manifest with the existing C2 inbox parser, selects one exact numbered slot, and takes these fields only from that manifest:

- `stageId`
- `promptPath`
- `dedupKey`
- `resultProtocol`
- `resultJsonPath`
- `resultMdPath`
- `terminalCommitPrefix`

It then reads `parallel/PM/STAGE_CLAIMS/<stageId>.json`, follows that stage claim's canonical claim path, and requires exact worker identity, `claimToken`, `effectiveDedupKey`, and `startCommit` agreement. No finish-input field can redirect authority or output paths.

## Terminal claim-state gate

- `COMPLETE`: canonical and stage claims must both be `COMPLETE` for the same token.
- `BLOCKED`: canonical and stage claims must both be `BLOCKED` for the same token.
- `SUBCOMPLETE`: both claims must have the same token and same state, either `ACTIVE` or `COMPLETE`; the finish payload must carry a concrete `nextAction` describing the remaining dependency.

Any mixed/mismatched/unknown claim state fails closed.

## Result construction and validation

The finish payload contains exactly the worker-variable C1 fields: `state`, `verdict`, `implementationCommits`, `integrationReady`, `changedFiles`, `tests`, `productProof`, `ownerGate`, `blocker`, `nextAction`, `evidencePaths`, and `safety`.

The publisher hydrates `schema`, `stageId`, `dedupKey`, `claimToken`, and `startCommit`, then calls the existing C1 `alpha_worker_result.validate_result` plus deterministic path verification before writing anything. `RESULT.md` is rendered from that same validated in-memory result object, so the two artifacts cannot be independently hand-authored and drift.

## Create-only pair semantics

Both manifest-declared output files must be absent. The publisher refuses to overwrite either file. If creation of the second artifact fails after the first was created, it removes the first artifact before returning failure; a pre-existing artifact is never removed. No shared mutable worker dashboard/index is created.

On success stdout is one compact JSON object containing the exact result paths and exact terminal commit subject. Errors are fail-closed and printed as `ERROR <CODE>: <detail>`.

## PM precedence unchanged

C6 changes only how workers publish terminal artifacts. PM still uses this precedence:

1. manifest-declared structured `RESULT.json`;
2. existing status/call-sign fallback when no valid result is available;
3. dedicated worker follow-up only when durable Git evidence is insufficient.

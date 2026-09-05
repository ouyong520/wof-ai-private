stageId: `ALPHA_PM_WORKER_COMMUNICATION_C7_CURRENT_DISPATCH_ACTIVATOR`
dedupProtocol: `v2`
dedupKey: `alpha.pm.worker-communication.current-dispatch-activator-v1`
dedupMode: `exclusive`
resultProtocol: `wof-alpha-worker-result-v1`
resultJsonPath: `parallel/PM/RESULTS/ALPHA_PM_WORKER_COMMUNICATION_C7_CURRENT_DISPATCH_ACTIVATOR_RESULT.json`
resultMdPath: `parallel/PM/RESULTS/ALPHA_PM_WORKER_COMMUNICATION_C7_CURRENT_DISPATCH_ACTIVATOR_RESULT.md`
terminalCommitPrefix: `WORKER_RESULT ALPHA_PM_WORKER_COMMUNICATION_C7_CURRENT_DISPATCH_ACTIVATOR`
dispatchManifestPath: `parallel/PM/DISPATCH_MANIFESTS/ALPHA_PM_WORKER_COMMUNICATION_C7_C8_2_WORKER_V1.json`

# Alpha PM Worker Communication C7 — Current Dispatch Activator

Repository: `ouyong520/wof-ai-private`

Read first:
- latest `main`;
- `parallel/PM/ALPHA_PM_WORKER_COMMUNICATION_C7_C8_2_WORKER_DISPATCH.md`;
- `parallel/PM/ALPHA_PM_CURRENT_DISPATCH_PROTOCOL_V1.md`;
- `parallel/PM/ALPHA_PM_DISPATCH_CONTRACT_V1.md`;
- `parallel/PM/TESTING_CADENCE_POLICY.md`;
- this dispatch manifest.

Scope is PM/Worker coordination implementation only. Do not modify Alpha runtime/HUD/renderer/updater/product logic. Collector / Unified Collector / Training Farm / 10训 are out of scope.

## Ownership

Perform dedup-v2 exactly as declared: latest-main preflight -> create-only canonical claim -> re-read exact claimToken -> create-only stage claim -> re-read exact same claimToken. Any create/verification failure is fail-closed. Do not invent recovery.

## Goal

Implement the missing PM-only write/transition side of the C5 current-dispatch contract. C5 can resolve a canonical pointer but intentionally does not create/update it. Provide a deterministic activator/planner so PM can safely select a new immutable dispatch without manually calculating hashes/revisions/previous-dispatch identity.

Preferred new files:
- `parallel/PM/tools/alpha_pm_dispatch_activate.py`
- `parallel/PM/ALPHA_PM_DISPATCH_ACTIVATION_PROTOCOL_V1.md`
- optional narrow example/input template if useful.

Do not rewrite C1-C6 implementation files. Reuse C2/C3/C5 public validation/resolver behavior.

## Required behavior

A PM-facing command should support at least a dry-run/plan mode such as:

`python parallel/PM/tools/alpha_pm_dispatch_activate.py plan --manifest parallel/PM/DISPATCH_MANIFESTS/<ID>.json --repo-root .`

It must:
1. validate target manifest with existing C2/C3 contracts and require immutable final schema;
2. bind exact repository, dispatchId, canonical manifest path, manifest authorityCommit, and SHA-256 of exact manifest bytes;
3. read existing `parallel/PM/CURRENT_DISPATCH.json` when present and validate it through C5 before using its revision/history;
4. derive monotonic next `revision` and exact `previousDispatch` identity;
5. produce the exact next pointer JSON deterministically;
6. support create-vs-update planning with an expected old content/hash guard so PM cannot accidentally overwrite a concurrent pointer change;
7. provide a verification mode that re-reads a PM-written pointer and resolves it with C5 before declaring activation valid;
8. fail closed on invalid/stale current pointer, malformed manifest, wrong repository, traversal/path mismatch, mutable manifest, authority mismatch, or revision regression.

The worker must **not** itself create or update the live `parallel/PM/CURRENT_DISPATCH.json`; that remains a PM/coordinator operation. The tool may render the exact content and safe write instructions/guards for PM.

## Implementation-first cadence

Build the complete activator flow first. Only minimum self-checks are expected: Python parse/compile, one clean plan from no pointer, one transition from a valid prior pointer, and one stale/concurrent-guard failure. Do not build a broad QA suite or open independent QA.

## Terminal reporting

Write the exact manifest-declared RESULT.json and RESULT.md. Result must clearly state what is now automated, implementation commit(s), changed files, minimal self-checks, integrationReady, blocker if any, and exact PM next action. Final result commit subject begins:

`WORKER_RESULT ALPHA_PM_WORKER_COMMUNICATION_C7_CURRENT_DISPATCH_ACTIVATOR <STATE>`

Return only COMPLETE / SUBCOMPLETE / precise BLOCKED in chat.

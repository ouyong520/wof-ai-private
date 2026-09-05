stageId: `ALPHA_PM_WORKER_COMMUNICATION_C1_RESULT_ENVELOPE_VALIDATOR`
dedupProtocol: `v2`
dedupKey: `alpha.pm.worker-communication.result-envelope-validator-v1`
dedupMode: `exclusive`
resultProtocol: `wof-alpha-worker-result-v1`
resultJsonPath: `parallel/PM/RESULTS/ALPHA_PM_WORKER_COMMUNICATION_C1_RESULT_ENVELOPE_VALIDATOR_RESULT.json`
resultMdPath: `parallel/PM/RESULTS/ALPHA_PM_WORKER_COMMUNICATION_C1_RESULT_ENVELOPE_VALIDATOR_RESULT.md`
terminalCommitPrefix: `WORKER_RESULT ALPHA_PM_WORKER_COMMUNICATION_C1_RESULT_ENVELOPE_VALIDATOR`

# Alpha PM Worker Communication C1 — Result Envelope / Validator

Repository: `ouyong520/wof-ai-private`

Read first:
- latest `main`;
- `parallel/PM/ALPHA_PM_WORKER_GIT_COMMUNICATION_2_WORKER_DISPATCH.md`;
- `parallel/PM/ALPHA_WORKER_RESULT_FAST_FEEDBACK_PROTOCOL_V1.md`;
- `parallel/PM/STAGE_DEDUP_GUARD.md`.

Scope: Alpha PM/worker coordination only. No Alpha runtime/updater/HUD/renderer product behavior changes. Collector / Unified Collector / Training Farm / 10训 are out of scope.

## Mandatory dedup

Perform latest-main dedup preflight, then create-only canonical claim, re-read and verify exact claimToken, then create-only stage claim with the same token, re-read and verify. Any create/verification failure is fail-closed. Do not invent recovery.

## Goal

Implement a small, deterministic worker terminal-result contract so any future Alpha worker can produce a result that PM can read in seconds.

## Deliverables

Prefer these coordination-only paths:

- `parallel/PM/schemas/alpha_worker_result_v1.schema.json`
- `parallel/PM/templates/alpha_worker_result_v1.json`
- `parallel/PM/tools/alpha_worker_result.py`
- `parallel/PM/tests/test_alpha_worker_result_protocol.py`
- narrow docs only if needed.

The helper/validator must support at least:

1. validate a result JSON against required fields and enum values;
2. derive/verify deterministic result paths from `stageId`;
3. reject malformed/missing `stageId`, `state`, `implementationCommits`, `changedFiles`, `tests`, `productProof`, `ownerGate`, `blocker`, `nextAction`, `safety`;
4. reject `COMPLETE` when required terminal evidence is structurally absent;
5. reject product-visible claims that lack explicit product-proof classification;
6. preserve distinction between implementation proof, machine draw proof, and Owner visual proof;
7. support exact states `SUBCOMPLETE`, `COMPLETE`, `BLOCKED`;
8. support BLOCKED machine code + pmRequired/ownerRequired/recoveryAllowedByWorker;
9. produce concise validation errors suitable for PM/worker use.

Do not create or require a shared mutable dashboard.

## Focused tests

Cover valid COMPLETE/SUBCOMPLETE/BLOCKED examples and malformed cases, deterministic result paths, false-green rejection, and unsupported state rejection.

## Terminal reporting

Follow `parallel/PM/ALPHA_WORKER_RESULT_FAST_FEEDBACK_PROTOCOL_V1.md` using the exact result paths declared at the top of this prompt. Final result commit must begin with:

`WORKER_RESULT ALPHA_PM_WORKER_COMMUNICATION_C1_RESULT_ENVELOPE_VALIDATOR <STATE>`

Close your own canonical/stage claim correctly before reporting COMPLETE. Return only COMPLETE/SUBCOMPLETE or precise BLOCKED.
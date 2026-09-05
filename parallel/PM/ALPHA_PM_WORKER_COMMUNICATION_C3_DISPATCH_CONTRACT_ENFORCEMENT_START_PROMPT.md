stageId: `ALPHA_PM_WORKER_COMMUNICATION_C3_DISPATCH_CONTRACT_ENFORCEMENT`
dedupProtocol: `v2`
dedupKey: `alpha.pm.worker-communication.dispatch-contract-enforcement-v1`
dedupMode: `exclusive`
resultProtocol: `wof-alpha-worker-result-v1`
resultJsonPath: `parallel/PM/RESULTS/ALPHA_PM_WORKER_COMMUNICATION_C3_DISPATCH_CONTRACT_ENFORCEMENT_RESULT.json`
resultMdPath: `parallel/PM/RESULTS/ALPHA_PM_WORKER_COMMUNICATION_C3_DISPATCH_CONTRACT_ENFORCEMENT_RESULT.md`
terminalCommitPrefix: `WORKER_RESULT ALPHA_PM_WORKER_COMMUNICATION_C3_DISPATCH_CONTRACT_ENFORCEMENT`

# Alpha PM Worker Communication C3 — Dispatch Contract Enforcement

Repository: `ouyong520/wof-ai-private`

Read first:
- latest `main`;
- `parallel/PM/ALPHA_PM_SHORT_HANDOFF_FORMAT.md`;
- `parallel/PM/ALPHA_WORKER_RESULT_FAST_FEEDBACK_PROTOCOL_V1.md`;
- `parallel/PM/ALPHA_PM_WORKER_GIT_COMMUNICATION_2_WORKER_DISPATCH.md`;
- `parallel/PM/DISPATCH_MANIFESTS/ALPHA_PM_WORKER_GIT_COMMUNICATION_2_WORKER_V1.json`;
- `parallel/PM/STAGE_DEDUP_GUARD.md`.

Scope: Alpha PM/Worker coordination tooling only. Do not modify Alpha runtime, HUD, updater, renderer, enemy logic, semantic logic, Collector, Unified Collector, or Training Farm / 10训.

## Mandatory dedup

Perform latest-main dedup preflight, then create-only canonical claim, re-read and verify exact claimToken, then create-only stage claim with the same token, re-read and verify. Any create/verification failure is fail-closed. Do not invent recovery.

## Goal

Make future PM task dispatches self-describing and mechanically enforce that every worker assignment declares where PM will later read its terminal result.

A future worker start prompt/dispatch must no longer be considered communication-complete unless it carries all of:

- `stageId`;
- complete dedup-v2 metadata;
- `resultProtocol`;
- deterministic `resultJsonPath`;
- deterministic `resultMdPath`;
- `terminalCommitPrefix`;
- manifest membership or an explicit solo manifest;
- the requirement to follow `ALPHA_WORKER_RESULT_FAST_FEEDBACK_PROTOCOL_V1.md`.

## Deliverables

Prefer coordination-only files such as:

- `parallel/PM/templates/alpha_worker_start_prompt_header.md`;
- `parallel/PM/templates/alpha_dispatch_manifest_v1.json`;
- `parallel/PM/tools/alpha_worker_dispatch_contract.py`;
- `parallel/PM/tests/test_alpha_worker_dispatch_contract.py`;
- narrow docs if needed.

Do not modify C1/C2 implementation-owned files if they appear concurrently. Reuse their public contracts only when already durable on latest main; otherwise keep C3 implementation structurally independent and integration-ready.

## Required behavior

The dispatch-contract helper/validator must support at least:

1. validate a worker start prompt header for required communication metadata;
2. validate a dispatch manifest worker entry has exact stageId/prompt/result paths/terminal prefix;
3. derive deterministic result paths from stageId and reject mismatches;
4. reject missing dedup-v2 metadata before worker dispatch;
5. reject prompts that omit terminal reporting protocol;
6. reject manifest entries that point multiple workers to the same RESULT file;
7. reject shared mutable worker-owned status/dashboard paths;
8. support 1-worker, 2-worker, and 3-worker manifests;
9. provide concise machine-readable validation output suitable for PM preflight;
10. make the short chat handoff possible: the chat only needs a short task sentence + Git authority paths because all execution/result metadata is durable in Git.

## Focused tests

Cover:

- valid solo/2-worker/3-worker dispatches;
- missing stageId/dedup/result path/terminal prefix;
- duplicate result path collision;
- deterministic path mismatch;
- missing result protocol;
- malformed manifest worker entry;
- acceptance of immutable per-dispatch manifests without a global mutable dashboard.

## Terminal reporting

Follow `parallel/PM/ALPHA_WORKER_RESULT_FAST_FEEDBACK_PROTOCOL_V1.md` using the exact paths declared at the top of this prompt.

Final terminal result commit must begin with:

`WORKER_RESULT ALPHA_PM_WORKER_COMMUNICATION_C3_DISPATCH_CONTRACT_ENFORCEMENT <STATE>`

Close your own canonical/stage claim correctly before reporting COMPLETE. Return only COMPLETE/SUBCOMPLETE or precise BLOCKED.
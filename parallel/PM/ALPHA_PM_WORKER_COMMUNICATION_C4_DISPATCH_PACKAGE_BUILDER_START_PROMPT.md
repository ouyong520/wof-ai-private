stageId: `ALPHA_PM_WORKER_COMMUNICATION_C4_DISPATCH_PACKAGE_BUILDER`
dedupProtocol: `v2`
dedupKey: `alpha.pm.worker-communication.dispatch-package-builder-v1`
dedupMode: `exclusive`
resultProtocol: `wof-alpha-worker-result-v1`
resultJsonPath: `parallel/PM/RESULTS/ALPHA_PM_WORKER_COMMUNICATION_C4_DISPATCH_PACKAGE_BUILDER_RESULT.json`
resultMdPath: `parallel/PM/RESULTS/ALPHA_PM_WORKER_COMMUNICATION_C4_DISPATCH_PACKAGE_BUILDER_RESULT.md`
terminalCommitPrefix: `WORKER_RESULT ALPHA_PM_WORKER_COMMUNICATION_C4_DISPATCH_PACKAGE_BUILDER`
dispatchManifestPath: `parallel/PM/DISPATCH_MANIFESTS/ALPHA_PM_WORKER_COMMUNICATION_C4_C5_2_WORKER_V1.json`

# Alpha PM Worker Communication C4 — Dispatch Package Builder

Repository: `ouyong520/wof-ai-private`

Read latest main first, then:

- `parallel/PM/ALPHA_PM_WORKER_COMMUNICATION_C4_C5_2_WORKER_DISPATCH.md`
- `parallel/PM/ALPHA_PM_DISPATCH_CONTRACT_V1.md`
- `parallel/PM/ALPHA_WORKER_RESULT_FAST_FEEDBACK_PROTOCOL_V1.md`
- `parallel/PM/ALPHA_PM_RESULT_INBOX_PROTOCOL_V1.md`
- `parallel/PM/STAGE_DEDUP_GUARD.md`

Scope: PM/Worker coordination only. No Alpha product behavior changes. Collector / Unified Collector / Training Farm / 10训 are out of scope.

## Dedup

Perform latest-main dedup preflight. Create-only canonical claim, re-read exact claimToken/fields/state ACTIVE, then create-only stage claim and re-read exact token. Any failure is fail-closed. Do not invent recovery.

## Mission

Build a deterministic PM dispatch-package generator so PM can define 1–3 worker jobs in a compact spec and mechanically produce/validate the durable communication package instead of manually reconstructing prompt headers, RESULT paths, terminal prefixes, and manifest entries.

## Owned deliverables

Prefer new files only:

- `parallel/PM/schemas/alpha_dispatch_spec_v1.schema.json`
- `parallel/PM/templates/alpha_dispatch_spec_v1.json`
- `parallel/PM/tools/alpha_pm_dispatch_builder.py`
- `parallel/PM/tests/test_alpha_pm_dispatch_builder.py`
- `parallel/PM/ALPHA_PM_DISPATCH_BUILDER_PROTOCOL_V1.md`

Do not modify C3-owned contract/validator/template files. Consume/import them where useful.

## Required behavior

The builder must accept a compact dispatch specification containing dispatch-level authority plus 1, 2, or 3 workers. For every worker it must deterministically derive or verify:

- `stageId`;
- unique `dedupKey`;
- `dedupProtocol=v2` and valid `dedupMode`;
- exact prompt path;
- `resultProtocol=wof-alpha-worker-result-v1`;
- deterministic `parallel/PM/RESULTS/<stageId>_RESULT.json`;
- deterministic `parallel/PM/RESULTS/<stageId>_RESULT.md`;
- `terminalCommitPrefix=WORKER_RESULT <stageId>`;
- numbered manifest slot.

It must be able to emit a final `wof-alpha-dispatch-manifest-v1` object compatible with C2 schema and a prompt-header block compatible with the C3 dispatch contract. It may emit files into an explicitly supplied output directory or print deterministic output; it must never silently overwrite existing Git authority files.

## Fail-closed rules

Reject at least:

- worker count outside 1..3;
- duplicate stageId/dedupKey/result paths;
- malformed/traversal repository paths;
- missing authority path/commit;
- unsupported dedup mode/protocol;
- non-deterministic or redirected RESULT paths;
- shared mutable worker status/dashboard files;
- an output target that already exists unless running a validation-only mode;
- a generated package that fails existing C2/C3 validators.

The builder must compose with existing validators rather than weakening/reimplementing their truth rules.

## Focused tests

Cover valid 1/2/3-worker specs, deterministic repeated output, collisions, traversal, existing-target refusal, malformed authority, invalid worker count, result-path derivation, final manifest compatibility, and C3 validation handoff where available.

## Terminal reporting

Write exactly the RESULT.json/RESULT.md declared above. RESULT JSON must use the C1 schema and accurately list implementation commits, changed files, tests, integration readiness, blocker, and nextAction.

Final result commit prefix:

`WORKER_RESULT ALPHA_PM_WORKER_COMMUNICATION_C4_DISPATCH_PACKAGE_BUILDER <STATE>`

Close your own canonical/stage correctly before COMPLETE. Chat only returns COMPLETE / SUBCOMPLETE / precise BLOCKED.

# Alpha PM ↔ Worker Git Communication Mechanism — 2 Worker Dispatch

Repository: `ouyong520/wof-ai-private`
Scope: Alpha PM/worker coordination only. No Alpha product runtime behavior changes. Collector / Unified Collector / Training Farm / 10训 are out of scope.

## Goal

Make PM↔worker communication Git-native and fast:

1. PM creates a task/start prompt and immutable dispatch manifest.
2. Manifest declares deterministic result paths for every worker.
3. Worker performs work and writes terminal result to those exact Git paths.
4. Owner only sends `1`, `1 2`, or `1 3`.
5. PM reads the manifest and directly fetches each worker JSON result.
6. Missing file means not terminal yet; existing file gives state, commits, tests, blocker, Owner gate, and next action.
7. Markdown is detailed evidence; JSON is the fast path.
8. Worker chat text is not authority and is never required for PM reconstruction.

Existing base protocol:
`parallel/PM/ALPHA_WORKER_RESULT_FAST_FEEDBACK_PROTOCOL_V1.md`

## C1 — Result Envelope / Validator

Execution authority:
`parallel/PM/ALPHA_PM_WORKER_COMMUNICATION_C1_RESULT_ENVELOPE_VALIDATOR_START_PROMPT.md`

Owns:
- canonical JSON schema/template for worker result;
- deterministic result-path naming helper/validator;
- validation CLI/library usable by future workers/tests;
- focused tests/docs/result.

Must not edit Alpha product runtime/updater/HUD/renderer files.

## C2 — Dispatch Manifest / PM Fast Reader

Execution authority:
`parallel/PM/ALPHA_PM_WORKER_COMMUNICATION_C2_DISPATCH_MANIFEST_FAST_READER_START_PROMPT.md`

Owns:
- immutable dispatch-manifest schema/template;
- PM fast-reader/inbox helper that reads exact result paths from a manifest;
- compact summary output for COMPLETE/SUBCOMPLETE/BLOCKED/NOT_FINISHED;
- focused tests/docs/result.

Must not edit Alpha product runtime/updater/HUD/renderer files.

## Non-racing architecture

Workers never mutate one shared dashboard/index. A dispatch manifest is coordinator-created and immutable for that dispatch. Each worker owns unique deterministic terminal paths:

`parallel/PM/RESULTS/<stageId>_RESULT.json`
`parallel/PM/RESULTS/<stageId>_RESULT.md`

A PM reader may aggregate locally/in-memory from those immutable per-stage files but must not require workers to update a shared central file.

## Future dispatch rule

Every future Alpha worker start prompt should declare at least:

- `resultProtocol: wof-alpha-worker-result-v1`
- `resultJsonPath: parallel/PM/RESULTS/<stageId>_RESULT.json`
- `resultMdPath: parallel/PM/RESULTS/<stageId>_RESULT.md`
- `terminalCommitPrefix: WORKER_RESULT <stageId>`

Every future multi-worker dispatch should have one immutable machine-readable manifest listing those paths.

## PM read algorithm

When Owner sends `1`, `1 2`, or `1 3`:

1. read latest main;
2. read current dispatch manifest;
3. fetch each declared `resultJsonPath` directly;
4. 404/missing => `NOT_FINISHED`;
5. existing JSON => parse state, verdict, implementation commits, changed files, tests, product proof, owner gate, blocker, next action;
6. read Markdown only if deeper evidence is needed;
7. inspect implementation commit(s) for acceptance/integration;
8. dispatch next work based on durable Git result, never chat claims.

## Acceptance

Communication mechanism is ready when C1+C2 are integration-ready and PM can determine worker terminal status and next action from one dispatch manifest + small JSON result files without searching full history or relying on worker chat.
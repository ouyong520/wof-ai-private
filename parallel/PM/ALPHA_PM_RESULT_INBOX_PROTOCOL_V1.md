# Alpha PM Result Inbox Protocol V1

Status: coordination-only fast path for Alpha PM ↔ Worker Git communication.

This protocol adds an **immutable dispatch manifest** and a **local PM fast reader**. It does not change Alpha runtime, updater, HUD, renderer, Collector, Unified Collector, Training Farm, or 10训 behavior.

## 1. Immutable dispatch manifest

For every multi-worker Alpha dispatch, the PM/coordinator creates a new manifest once, preferably at:

`parallel/PM/DISPATCH_MANIFESTS/<dispatchId>.json`

Schema:

`parallel/PM/schemas/alpha_dispatch_manifest_v1.schema.json`

Template:

`parallel/PM/templates/alpha_dispatch_manifest_v1.json`

"Immutable" is an operating rule, not a mutable status flag: after the coordinator creates a manifest for a dispatch, workers never edit it and PM does not reuse that path for a changed dispatch. Any worker set/path/authority change gets a new `dispatchId` and a new manifest path. Git history remains the durable audit trail.

The manifest binds each numbered `slot` to exactly one worker and records:

- `stageId`
- `promptPath`
- `dedupKey`
- `resultProtocol`
- `resultJsonPath`
- `resultMdPath`
- `terminalCommitPrefix`

The reader additionally enforces deterministic terminal paths:

`parallel/PM/RESULTS/<stageId>_RESULT.json`

`parallel/PM/RESULTS/<stageId>_RESULT.md`

and terminal prefix:

`WORKER_RESULT <stageId>`

Duplicate slot, `stageId`, result JSON path, or result Markdown path is rejected.

## 2. Owner shorthand → manifest slot

The manifest's `slot` is the machine-readable meaning of the Owner's worker shorthand.

- Owner sends `1` → PM reads slot 1.
- Owner sends `1 2` → PM reads slots 1 and 2.
- Owner sends `1 3` → PM reads slots 1 and 3.

No chat-history reconstruction is required. If a requested slot is not in the immutable manifest, the reader fails closed.

## 3. PM fast reader

Tool:

`parallel/PM/tools/alpha_pm_result_inbox.py`

It needs only a local checkout root and one immutable manifest. It performs no network access, invokes no Git command, and does not mutate the checkout.

Read all workers:

```text
python parallel/PM/tools/alpha_pm_result_inbox.py parallel/PM/DISPATCH_MANIFESTS/<dispatch>.json --repo-root . --pretty
```

Read Owner shorthand `1 3`:

```text
python parallel/PM/tools/alpha_pm_result_inbox.py parallel/PM/DISPATCH_MANIFESTS/<dispatch>.json --repo-root . --slots 1 3 --pretty
```

Default stdout is compact one-line JSON for machine use. `--pretty` is for human inspection.

## 4. Result states

For each declared worker the reader produces exactly one fast state:

- `NOT_FINISHED`: declared `RESULT.json` does not exist. PM must not infer completion from chat.
- `SUBCOMPLETE`: valid worker result says SUBCOMPLETE.
- `COMPLETE`: valid worker result says COMPLETE.
- `BLOCKED`: valid worker result says BLOCKED.
- `INVALID_RESULT`: a result file exists but is malformed, inconsistent with the manifest, uses an unsupported protocol/state, or misses required result-envelope fields.

`NOT_FINISHED` is not an error. `BLOCKED` is not a parser error. Both are valid facts for PM routing.

## 5. Compact worker summary

A valid terminal result surfaces at least:

- slot / `stageId`
- state
- verdict
- `integrationReady`
- implementation commits
- changed files
- tests totals and items
- `productProof.status`
- `ownerGate.required` / `ownerGate.question`
- `blocker.code` / `blocker.ownerRequired` / `blocker.pmRequired` when blocked
- `nextAction`
- exact result JSON / Markdown paths

The Markdown result is not part of the fast path. PM opens it only for deeper evidence. PM inspects implementation commits only for acceptance/integration review.

## 6. Fail-closed rules

Manifest-level failures stop the reader before trusting any worker result:

- malformed/unsupported manifest
- duplicate slot
- duplicate `stageId`
- duplicate result JSON/Markdown path
- non-deterministic result path or terminal prefix
- absolute path, `..` traversal, backslash path, or path outside `parallel/PM/RESULTS/`
- local symlink resolution that escapes `parallel/PM/RESULTS/`
- unsupported manifest result protocol
- unknown requested slot

Existing result files fail closed to per-worker `INVALID_RESULT` for:

- malformed JSON
- result `stageId` mismatch
- result `dedupKey` mismatch
- unsupported result protocol
- unsupported terminal state
- missing/malformed required envelope fields

Exit codes:

- `0`: manifest is valid and no result is `INVALID_RESULT` (workers may still be NOT_FINISHED or BLOCKED).
- `1`: manifest is valid but at least one existing result is `INVALID_RESULT`.
- `2`: manifest/selection/path safety failed closed.

## 7. PM operating contract

When Owner sends worker numbers:

1. Read latest `main`.
2. Read the current immutable dispatch manifest.
3. Run/read the exact declared `RESULT.json` paths for requested slots.
4. Missing file means `NOT_FINISHED`; do not guess.
5. Existing valid JSON is first authority for state, verdict, commits, changed files, tests, integration readiness, product proof, Owner gate, blocker, and next action.
6. Read the worker Markdown only when deeper evidence is needed.
7. Inspect implementation commit(s) only for acceptance/integration.
8. Dispatch next work from durable Git evidence, never from worker chat claims.

Workers never update a shared central dashboard or the dispatch manifest.

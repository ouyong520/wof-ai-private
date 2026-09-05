# Alpha PM -> Worker Dispatch Contract V1

Status: **AUTHORITATIVE FOR NEW ALPHA PM WORKER DISPATCHES**

Scope: PM/Worker coordination only. This contract does not authorize Alpha runtime, HUD, renderer, updater, semantic logic, Collector, Unified Collector, or Training Farm / 10训 changes.

## 1. Communication-complete means four durable pieces

A new Alpha worker assignment is ready to send only when all four exist:

1. **Short chat handoff** — one short task sentence, authoritative Git paths, and one execution sentence. Chat is presentation only and is never execution authority.
2. **Git start prompt / dispatch authority** — complete execution details and dedup-v2 metadata live in Git.
3. **Immutable dispatch manifest** — one per dispatch, with exactly 1, 2, or 3 worker entries. Every worker has unique deterministic terminal RESULT paths.
4. **Declared terminal result contract** — each worker declares `resultProtocol`, `resultJsonPath`, `resultMdPath`, and `terminalCommitPrefix`, and must follow `parallel/PM/ALPHA_WORKER_RESULT_FAST_FEEDBACK_PROTOCOL_V1.md`.

If any piece is absent or the validator reports `ok: false`, PM must not dispatch the worker.

## 2. Required worker prompt metadata

Every new worker start prompt header must declare:

- `stageId`;
- `dedupProtocol: v2`;
- `dedupKey`;
- `dedupMode`;
- `resultProtocol: wof-alpha-worker-result-v1`;
- deterministic `resultJsonPath`;
- deterministic `resultMdPath`;
- `terminalCommitPrefix: WORKER_RESULT <stageId>`.

The recommended header also includes `dispatchManifestPath` so the prompt is self-describing. A prompt is still communication-complete when its exact `promptPath` is a member of the immutable manifest being validated.

For `dedupMode: independent-validation`, the prompt must also contain the PM-assigned `independentValidationGroup` and `independentValidationKey` required by `parallel/PM/STAGE_DEDUP_GUARD.md`.

Use:

`parallel/PM/templates/alpha_worker_start_prompt_header.md`

## 3. Immutable manifest rules

Create one manifest under:

`parallel/PM/DISPATCH_MANIFESTS/<DISPATCH_ID>.json`

Use the C2-owned durable contract:

- `parallel/PM/schemas/alpha_dispatch_manifest_v1.schema.json`
- `parallel/PM/templates/alpha_dispatch_manifest_v1.json`

C3 consumes these files but does not rewrite them.

Rules:

- final manifests use `schema: wof-alpha-dispatch-manifest-v1` and carry `createdAtUtc`, `authorityCommit`, and numbered `slot` entries from the C2 contract;
- `immutable` must be `true`;
- worker count must be 1, 2, or 3 and final slots must be exactly `1..N`;
- every worker entry must declare exact `stageId`, `promptPath`, `dedupKey`, result protocol/paths, and terminal commit prefix;
- RESULT paths are deterministic from `stageId` and may not be redirected;
- no two workers may share a RESULT JSON or Markdown path;
- workers must not share a mutable status/dashboard file;
- do not replace per-stage RESULT files with a central worker-owned dashboard.

A solo worker still gets an explicit one-worker immutable manifest. This keeps PM fast-read behavior identical for `1`, `1 2`, and `1 3` handoffs.

## 4. Mechanical PM preflight gate

Before sending the short chat handoff, run:

```text
python parallel/PM/tools/alpha_worker_dispatch_contract.py validate-dispatch parallel/PM/DISPATCH_MANIFESTS/<DISPATCH_ID>.json --repo-root .
```

The command emits one JSON object. Dispatch is allowed only when:

```json
{"ok": true}
```

The validator checks prompt metadata, dedup-v2 presence, terminal reporting protocol, deterministic result paths, manifest immutability, 1/2/3 worker shape, prompt/manifest exact membership, duplicate RESULT collisions, and shared mutable status/dashboard paths.

Useful narrower checks:

```text
python parallel/PM/tools/alpha_worker_dispatch_contract.py validate-prompt parallel/PM/<WORKER_START_PROMPT>.md
python parallel/PM/tools/alpha_worker_dispatch_contract.py validate-manifest parallel/PM/DISPATCH_MANIFESTS/<DISPATCH_ID>.json
python parallel/PM/tools/alpha_worker_dispatch_contract.py derive <STAGE_ID>
```

Narrow checks do not replace `validate-dispatch` for the final PM handoff gate.

## 5. Short chat format after preflight PASS

Chat should remain minimal:

```text
负责 <short mission sentence>。

引用：
parallel/PM/<WORKER_START_PROMPT>.md
parallel/PM/DISPATCH_MANIFESTS/<DISPATCH_ID>.json

按 Git authority 执行。完成后必须写入 Git 指定 RESULT 文件；聊天只回 COMPLETE / SUBCOMPLETE / 精确 BLOCKED。
```

Do not paste the full dedup metadata, acceptance matrix, file boundaries, or result schema into chat. They belong in Git.

## 6. Worker terminal contract

Workers write exactly the paths declared in the manifest and prompt:

`parallel/PM/RESULTS/<stageId>_RESULT.json`

`parallel/PM/RESULTS/<stageId>_RESULT.md`

The final result commit must begin:

`WORKER_RESULT <stageId> <STATE>`

where state is `COMPLETE`, `SUBCOMPLETE`, or `BLOCKED`.

PM reads the manifest first, then each exact RESULT JSON. Missing RESULT means `NOT_FINISHED`; PM does not reconstruct status from chat history.

## 7. Compatibility

Existing bootstrap manifests using `wof-alpha-dispatch-manifest-v1-draft` remain readable by the validator so C1/C2/C3 can converge without rewriting immutable historical dispatches. New manifests must use `wof-alpha-dispatch-manifest-v1`.

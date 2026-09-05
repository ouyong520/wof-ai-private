# Alpha PM Current Dispatch Protocol V1

Status: coordination-only PM routing contract. No Alpha product/runtime behavior is changed.

## 1. Goal

A new PM session must be able to recover the active worker dispatch from Git alone:

`parallel/PM/CURRENT_DISPATCH.json -> immutable dispatch manifest -> exact RESULT.json files -> PM action`

Chat history, worker claims, commit messages, and RESULT Markdown are not completion authority for this fast path.

## 2. PM-owned pointer

The canonical future pointer path is:

`parallel/PM/CURRENT_DISPATCH.json`

Only PM/coordinator may create or update that file. Ordinary workers, worker RESULT writers, and product code must never mutate it.

Pointer schema:

`parallel/PM/schemas/alpha_current_dispatch_v1.schema.json`

Non-authoritative example/template:

`parallel/PM/templates/alpha_current_dispatch_v1.json`

C5 intentionally does **not** create or mutate the live canonical pointer. The template demonstrates the contract against the C4/C5 immutable dispatch manifest; PM activates a live pointer only when PM explicitly selects the current dispatch.

## 3. Required identity binding

A pointer binds all of the following:

- `schema: wof-alpha-current-dispatch-v1`;
- `pmOwned: true`;
- exact `repository` identity;
- exact `dispatchId`;
- exact direct manifest path under `parallel/PM/DISPATCH_MANIFESTS/`;
- manifest-declared `authorityCommit` as `manifestAuthorityCommit`;
- SHA-256 of the exact manifest bytes as `manifestSha256`;
- `updatedAtUtc` and monotonic PM-owned `revision` metadata;
- optional `previousDispatch` identity for auditability.

The manifest filename must equal `<dispatchId>.json`. The content hash prevents an existing pointer from silently following a rewritten/redirected target even if the path remains the same. Immutable manifests remain create-once historical authorities; dispatch changes require a new manifest/dispatch identity, then a PM pointer update.

## 4. PM pointer update procedure

Before PM points at a new dispatch:

1. Read latest `main`.
2. Validate the target manifest under the C2/C3 dispatch contracts and confirm `immutable: true`.
3. Record its exact `dispatchId`, `authorityCommit`, repository-relative path, and SHA-256 bytes digest.
4. Increment `revision`; copy the previous pointer identity into `previousDispatch` when one exists.
5. Create/update only `parallel/PM/CURRENT_DISPATCH.json` as PM/coordinator.
6. Re-read the pointer and run the resolver before relying on it.

Workers continue writing only their manifest-declared per-stage RESULT files. They do not update the pointer or a shared dashboard.

## 5. Resolver

Tool:

`parallel/PM/tools/alpha_pm_current_dispatch.py`

Resolve the canonical pointer and all workers:

```text
python parallel/PM/tools/alpha_pm_current_dispatch.py --repo-root . --pretty
```

Resolve Owner shorthand `1 3`:

```text
python parallel/PM/tools/alpha_pm_current_dispatch.py --repo-root . --slots 1 3 --pretty
```

Resolve an explicitly supplied pointer, such as the non-authoritative template:

```text
python parallel/PM/tools/alpha_pm_current_dispatch.py parallel/PM/templates/alpha_current_dispatch_v1.json --repo-root . --pretty
```

Default expected repository identity is `ouyong520/wof-ai-private`; `--repository` exists for an explicit relocated/test checkout identity.

The resolver is local-only and read-only. It does not invoke Git or the network and performs no mutation.

## 6. Resolver trust sequence

The resolver fails closed unless all routing identity checks pass:

1. pointer file exists and parses as strict V1 JSON;
2. `pmOwned` is exactly `true`;
3. pointer repository equals the expected repository;
4. `manifestPath` is canonical, traversal-free, direct under `parallel/PM/DISPATCH_MANIFESTS/`, and filename-bound to `dispatchId`;
5. resolved manifest stays under the manifest directory;
6. exact manifest bytes match `manifestSha256`;
7. C2 accepts the manifest schema/immutability/path/result contract;
8. manifest `dispatchId` equals pointer `dispatchId`;
9. manifest `authorityCommit` equals `manifestAuthorityCommit`;
10. requested slots exist in that exact manifest.

Only then does C5 delegate worker truth to C2 `alpha_pm_result_inbox`.

## 7. Worker truth is C2 truth

C5 does not implement a second worker-result interpretation. It reuses C2 `build_inbox_summary`, so exact RESULT semantics remain:

- missing exact `RESULT.json` -> `NOT_FINISHED`;
- valid terminal JSON -> `COMPLETE`, `SUBCOMPLETE`, or `BLOCKED`;
- malformed/inconsistent existing JSON -> `INVALID_RESULT`;
- unknown slot or unsafe manifest -> fail closed.

The resolver never infers terminal status from worker chat, claim state, terminal commit messages, or Markdown.

## 8. Machine-readable continuation summary

Successful stdout is one `wof-alpha-current-dispatch-resolution-v1` JSON object containing pointer identity, selected slots, C2 state counts, exact worker summaries, and one `pmAction`:

- `REJECT_INVALID_RESULT`;
- `REVIEW_BLOCKER`;
- `WAIT_FOR_EXACT_RESULT_JSON`;
- `REVIEW_SUBCOMPLETE_NEXT_ACTION`;
- `CONTINUE_FROM_COMPLETE_RESULTS`.

This gives a new PM session enough durable state to continue without reconstructing prior chat.

Exit codes mirror C2 intent:

- `0`: pointer/manifest valid and no `INVALID_RESULT`;
- `1`: routing is valid but an existing worker RESULT is `INVALID_RESULT`;
- `2`: pointer/manifest/selection identity failed closed.

## 9. Fail-closed cases

Covered cases include missing/malformed pointer, non-PM-owned pointer, repository mismatch, traversal/external path, missing manifest, unsupported manifest schema, `immutable: false`, dispatch mismatch, authority-commit mismatch, stale/redirected manifest hash, unknown slot, malformed result, and new-session reconstruction from Git files only.

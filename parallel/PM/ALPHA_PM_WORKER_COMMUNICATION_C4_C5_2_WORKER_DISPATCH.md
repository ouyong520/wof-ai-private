# Alpha PM↔Worker Communication C4/C5 — 2 Worker Dispatch

Repository: `ouyong520/wof-ai-private`

Scope: Alpha PM/Worker coordination only. No Alpha runtime/HUD/updater/renderer/product changes. Collector / Unified Collector / Training Farm / 10训 are out of scope.

Baseline observed before dispatch: `2c0e3433f42c8ec9b5aab6f49f7e3ebc7635baa9`.

Accepted inputs:

- C1 RESULT envelope/validator: COMPLETE.
- C2 immutable manifest + fast reader: COMPLETE.
- C3 dispatch contract enforcement: ACTIVE and independently implementing contract/validator/template integration. C4/C5 must not modify C3-owned files.

## Goal

Close the last two PM communication gaps:

1. PM should not hand-author every manifest/result path/header repeatedly; a deterministic builder should turn a compact dispatch spec into a communication-complete package and fail closed before chat handoff.
2. A new PM chat/session should not need conversation memory to know which manifest is current; Git should expose one PM-owned current-dispatch pointer and a resolver that reaches the immutable manifest and exact RESULT files.

## C4 — Dispatch Package Builder

Start prompt:
`parallel/PM/ALPHA_PM_WORKER_COMMUNICATION_C4_DISPATCH_PACKAGE_BUILDER_START_PROMPT.md`

Implement a coordination-only builder that consumes a compact dispatch specification and deterministically derives/validates worker stage metadata, RESULT paths, terminal prefixes, worker prompt headers, and one final immutable `wof-alpha-dispatch-manifest-v1` manifest. It must compose with C1/C2/C3 tooling rather than replacing it.

No shared mutable worker dashboard. All generated worker/result paths must be deterministic and create-only-safe.

## C5 — Current Dispatch Pointer + Resolver

Start prompt:
`parallel/PM/ALPHA_PM_WORKER_COMMUNICATION_C5_CURRENT_DISPATCH_POINTER_RESOLVER_START_PROMPT.md`

Implement a PM-owned current-dispatch pointer contract and resolver. Future PM flow becomes:

`read CURRENT_DISPATCH.json -> resolve immutable manifest -> read exact RESULT.json files -> act`.

Workers must never mutate the current pointer. Only PM/coordinator writes it. The resolver must fail closed on missing/malformed/traversal/mismatched/stale pointers and reuse the C2 fast-reader semantics for worker status.

## Separation

C4 owns new dispatch-builder spec/schema/tool/tests/docs only.

C5 owns new current-dispatch pointer schema/template/resolver/tests/docs only.

C4 and C5 must not modify:

- `parallel/PM/ALPHA_PM_DISPATCH_CONTRACT_V1.md`;
- `parallel/PM/tools/alpha_worker_dispatch_contract.py`;
- `parallel/PM/templates/alpha_worker_start_prompt_header.md`;
- C1/C2 implementation files except read/import/consume;
- C3 RESULT/claim files;
- any Alpha product source.

## Terminal reporting

Both workers must follow:

- `parallel/PM/ALPHA_WORKER_RESULT_FAST_FEEDBACK_PROTOCOL_V1.md`;
- C3 authoritative dispatch contract when available on latest main;
- their exact manifest-declared RESULT paths.

PM will consume only the immutable manifest plus each exact RESULT.json for routine status. Markdown is deep evidence only.

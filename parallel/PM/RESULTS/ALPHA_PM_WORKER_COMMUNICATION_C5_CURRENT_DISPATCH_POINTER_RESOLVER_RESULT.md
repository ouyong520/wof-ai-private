# Alpha PM Worker Communication C5 — Current Dispatch Pointer + Resolver Result

State: **COMPLETE**

## Verdict

PM-owned current-dispatch pointer contract, exact manifest identity resolver, and C2 RESULT delegation are implemented and tested. A new PM session can reconstruct the selected dispatch and worker states from Git files without chat-memory reconstruction.

## What changed

- Added `parallel/PM/schemas/alpha_current_dispatch_v1.schema.json` for the strict PM-owned pointer contract.
- Added non-authoritative `parallel/PM/templates/alpha_current_dispatch_v1.json`, bound to the C4/C5 immutable manifest by dispatch ID, manifest authority commit, and exact manifest SHA-256.
- Added `parallel/PM/tools/alpha_pm_current_dispatch.py`, a local read-only resolver for the future canonical `parallel/PM/CURRENT_DISPATCH.json` path or an explicitly supplied pointer.
- Added `parallel/PM/tests/test_alpha_pm_current_dispatch.py` with fail-closed and new-session coverage.
- Added `parallel/PM/ALPHA_PM_CURRENT_DISPATCH_PROTOCOL_V1.md` documenting PM-only pointer ownership and the update/resolution flow.

C5 intentionally did not create or mutate the live `parallel/PM/CURRENT_DISPATCH.json`; activation remains a PM/coordinator operation for a concretely selected current dispatch. Ordinary workers are forbidden from writing that pointer.

## Resolver behavior

The resolver validates the pointer schema and `pmOwned: true`, expected repository, canonical direct manifest path, dispatch identity, authority commit, and exact manifest-byte SHA-256. It rejects traversal, missing or redirected manifests, unsupported/non-immutable manifests, identity mismatches, and unknown slots before trusting worker status.

After routing identity is proven, worker truth is delegated to the C2 `alpha_pm_result_inbox` public behavior. Missing exact RESULT JSON remains `NOT_FINISHED`; valid terminal JSON remains `COMPLETE`, `SUBCOMPLETE`, or `BLOCKED`; malformed/inconsistent existing JSON remains `INVALID_RESULT`. Chat, claims, commit messages, and RESULT Markdown are never substituted for the exact RESULT JSON.

## Tests

- **PASS** — `test_alpha_pm_current_dispatch`: 16 focused tests covering pointer validation, exact manifest resolution, slot shorthand, missing RESULT, COMPLETE/BLOCKED mix, malformed result, pointer/manifest mismatches, traversal, unknown slots, stale/redirected identity, and Git-only new-session reconstruction.
- **PASS** — Python compile check for the resolver and focused tests.
- **PASS** — Draft 2020-12 schema/template validation.
- **PASS** — template resolution smoke against `ALPHA_PM_WORKER_COMMUNICATION_C4_C5_2_WORKER_V1`, selecting slots 1 and 2 without chat state.

## Implementation commits

- `fa3d17a72ff12e429dd5ff01d83ec6394caaee94` — current-dispatch resolver.
- `50003aa4f2aca2113fca7db01ac7f6b190f7e077` — focused resolver tests.
- `55932eb996162e631b3ffd9a8bba0dd7c3c32625` — pointer schema.
- `e37e7d93dd127149a6d458eeef04d2cfa4fb7c56` — non-authoritative pointer template.
- `7f4be30176bc0fec02d4a52c86d34741bbad3b93` — current-dispatch protocol documentation.

## Scope / safety

Coordination-only changes. No Alpha product runtime/HUD/renderer/updater behavior and no Collector, Unified Collector, Training Farm, or 10训 behavior was changed. No RAM writes or input injection were performed.

## PM next action

When PM/coordinator selects a current immutable dispatch, activate/update `parallel/PM/CURRENT_DISPATCH.json` using the C5 schema/template and exact manifest identity. New PM sessions can then run `alpha_pm_current_dispatch.py` and continue from the exact manifest-declared RESULT JSON files.

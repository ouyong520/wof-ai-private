# P47 Bounded Owner Diagnostic Readiness Gate

This gate answers exactly one repository-side question:

- `READY_FOR_ONE_BOUNDED_OWNER_DIAGNOSTIC`
- `BLOCKED`

It does **not** run WOF, perform Owner validation, promote anything, move `alpha-live`, write game RAM, inject input, repair a renderer/source path, or mint retry/source-export/renderer authority.

## Terminal authority

The evaluator reads P43/P45/P46 terminal `RESULT` plus their closed canonical/stage claims. Worker `PROGRESS` is intentionally not an evaluator input. The final collector also requires the current terminal RESULT bytes to be identical to the exact RESULT bytes at each claim-pinned `resultCommit`.

## Exact candidate gate

The evaluator requires:

- P43 tested commit `0c23e22b0387d0b3042c5601ab0a9e897ce1c476`;
- P43 tested tree `e6da807b9efa29d5ab819013dbe2da4ded995aa6`;
- exact `P43_POST_P45_P46_INTEGRATED_CANDIDATE.json` blob;
- exact `P43_POST_P45_P46_DEPENDENCY_PINS.json` blob;
- every P43 `testedBlobMap` path to match current Git bytes;
- every P45 exact-file pin and the P46 exact source pin to match current Git bytes;
- P45 tested commit `3dac7a9e2cbe4a23c3de44eb15cf45f19b136149`;
- P46 tested commit `210efdda5bbf3715989c751eb90442f26f42d0a9`.

Any missing/stale/mismatched RESULT, claim, tree, candidate, blob, or dependency pin yields `BLOCKED` and `runBudget=0`.

## Diagnostic-only safety boundary

READY additionally requires zero-click/zero-manual-seed, read-only operation, RAM writes `0`, no input injection, no promotion/alpha-live movement, bounded P43/P46 runtime/event/log behavior, deterministic teardown, exact `runtimeEpoch` / `rendererEpoch` / `authorityKey` binding, exact Page/Worker/WASM association preservation, and complete P39/P42/P46 raw-evidence preservation.

Stale/mixed authority binding, `Module`/`Module.asm` identity drift, wrapper replacement/teardown conflict, candidate drift, or missing dependencies are fail-closed.

P46 WASM function index/name/offset truth states remain only `AVAILABLE`, `NOT_AVAILABLE`, or `UNRESOLVED`; symbol/offset guessing remains forbidden.

P40 remains terminal BLOCKED with `NATIVE_PLAYER_MARKER_DISPLAYED_SUBMIT_SOURCE_EXPORT_NOT_PRESENT`. P47 does not change P29, P32, P40, renderer authority, retry eligibility, promotion eligibility, or source-export authority.

## Run budget

The requested budget must be exactly `1`. READY emits `runBudget=1`; every BLOCKED classification emits `runBudget=0`.

## Focused test entrypoint

`.github/workflows/alpha-p47-bounded-owner-diagnostic-readiness.yml` performs only deterministic repository-side checks: syntax, focused synthetic fail-closed cases, exact terminal RESULT byte provenance, actual-repo classification, and a final READY/budget/authority assertion. It never starts the game.

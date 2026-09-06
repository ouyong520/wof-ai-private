# Alpha V1 P49 — Owner Windows One-Run Handoff Bridge

StageId:
`ALPHA_V1_PRODUCT_TAKEOVER_P49_OWNER_WINDOWS_ONE_RUN_HANDOFF_BRIDGE`

DedupKey:
`alpha.v1.product-takeover.owner-windows-one-run-handoff-bridge-v1`

Fresh PM authority at dispatch:
- main: `c551100d1480c2d22b6901afbf6092361a78d130`;
- P47 terminal COMPLETE / `READY_FOR_ONE_BOUNDED_OWNER_DIAGNOSTIC`, tested commit `f0634c81f0efb54819cef10e0c4cf8567cd5ca9a`;
- P48 terminal COMPLETE with `BLOCKED_PRE_RUN`, RESULT commit `89c8777025156f3704170006cf5c6f617cb4d14d`;
- P48 exact truth: `runStarted=false`, `runBudgetConsumed=false`, `remainingRunBudget=1`, `retryAttempted=false`;
- P48 first blocker: `OWNER_WINDOWS_EXECUTION_CHANNEL_NOT_CONNECTED` at `OWNER_RUNTIME_EXECUTION_CHANNEL_PREFLIGHT`;
- P43 exact diagnostic candidate: `0c23e22b0387d0b3042c5601ab0a9e897ce1c476`;
- P45 tested commit: `3dac7a9e2cbe4a23c3de44eb15cf45f19b136149`;
- P46 tested commit: `210efdda5bbf3715989c751eb90442f26f42d0a9`;
- P40 remains BLOCKED: `NATIVE_PLAYER_MARKER_DISPLAYED_SUBMIT_SOURCE_EXPORT_NOT_PRESENT`.

## Purpose

Remove only the real P48 pre-run infrastructure blocker by materializing an exact, deterministic, fail-closed Owner-Windows handoff bundle that the Owner can execute locally. This worker must NOT run the real game and must NOT consume the remaining one-run budget.

P49 is not a retry of P48 and must not reopen P48. It is a new handoff/bridge stage because the prior GitHub worker had no direct Owner Windows filesystem/process/browser-debugger channel.

## Required work

1. Fresh-read latest main, P47 terminal RESULT/closed claims, P48 terminal RESULT/closed claims/progress, and verify exactly:
   - `runStarted=false`;
   - `runBudgetConsumed=false`;
   - `remainingRunBudget=1`;
   - no later receipt/live-run record has consumed the budget.
2. Run dedup-v2 preflight and acquire one exclusive P49 canonical + stage claim.
3. Fresh-read exact P43/P45/P46 tested bytes, P43 candidate/dependency pins, P38 candidate pointer/provenance, and verify no required diagnostic implementation drift.
4. Materialize a local Owner-Windows handoff bundle under `parallel/OWNER_DIAGNOSTIC/` with at minimum:
   - one obvious `.cmd` entrypoint;
   - deterministic PowerShell/Python preflight/runner as needed;
   - machine-readable authority/permit metadata;
   - concise Owner instructions;
   - focused deterministic tests.
5. The local bundle must use the existing exact P43 entrypoint:
   `parallel/OWNER_DIAGNOSTIC/WOF_ALPHA_P43_BOUNDED_DIAGNOSTIC.cmd`
   and must not reimplement P43/P45/P46 diagnostic semantics.
6. Required local inputs may be explicit arguments or explicit environment variables, but must never be guessed:
   - metadata repository root;
   - exact source checkout path;
   - browser WebSocket debugger URL;
   - output directory.
   The managed interpreter remains the P43-required `%LOCALAPPDATA%\WOF Alpha Current Main\venv\Scripts\python.exe` and existence must be verified locally.
7. Local preflight must fail closed before live start unless all of these are true:
   - metadata repo contains the exact pinned P49/P48/P47/P43 authority files;
   - source checkout HEAD exactly equals `82b0b09ecd902f502ae5509bcb3ee5a713f43fee` and is clean;
   - managed interpreter exists;
   - browser WebSocket debugger URL is explicit and reachable;
   - output directory is writable and does not contain a prior consumed-run marker/receipt for this permit;
   - exact P43/P45/P46 candidate/dependency/blob pins still match;
   - remaining run budget is exactly 1;
   - no promotion / alpha-live movement / unsafe state is observed.
8. Create a one-run permit identity bound to the exact P47/P48/P43 authority and exact P49 tested bundle bytes. The local runner must atomically mark `RUN_STARTED` immediately before invoking the P43 `.cmd` and must refuse a second start for the same permit even if the first invocation times out/fails.
9. Preserve the project rule: before `RUN_STARTED`, a preflight failure consumes no budget; after `RUN_STARTED`, the single remaining budget is consumed regardless of live outcome. No automatic retry.
10. After a local run, preserve/point to the complete P43 receipt/raw bundle and produce a small import/handoff record containing at least:
    - permit identity;
    - runStarted;
    - runBudgetConsumed;
    - P43 receipt path + SHA256 when present;
    - firstFailingGate;
    - output directory;
    - exact authority commits.
    Do not filter raw P39/P42/P46/P36/P32 evidence.
11. Provide a separate post-run import/publish helper only if it can be deterministic and cannot alter live evidence. Do not automatically push, promote, or move alpha-live as part of the live runner.

## Safety / authority boundary

- P49 worker itself: no real WOF run, no Owner visual validation, no RAM write, no input injection, no install, no promotion, no alpha-live movement.
- The produced local runner may invoke exactly one later PM-authorized bounded diagnostic only after its local preflight passes.
- Zero click / zero manual seed remains mandatory for the diagnostic itself.
- P39/P42/P46 are diagnostic evidence only.
- No renderer authority, `rendererSourceProof`, P29 PASS, P32 qualification, retry eligibility, promotion eligibility, or source export may be minted.
- P40 remains BLOCKED until real evidence truthfully changes it.
- No guessed source path, debugger URL, WASM symbol, offset, object identity, or timing/order semantic mapping.

## Testing

Deterministic repository-side tests only. Include at minimum:
- P48 budget consumed => handoff BLOCKED;
- P48 runStarted true => handoff BLOCKED;
- missing/stale P47/P48/P43/P45/P46 authority => BLOCKED;
- exact source checkout mismatch/dirty fixture => local preflight BLOCKED;
- missing managed interpreter fixture => BLOCKED;
- missing/unreachable explicit debugger URL fixture => BLOCKED;
- pre-existing run-start marker => second start BLOCKED;
- preflight failure before RUN_STARTED => budget remains unconsumed;
- simulated start transition is atomic and one-way;
- no automatic second invocation after simulated failure;
- exact happy-path fixture produces one valid local handoff/permit without running real WOF.

Freeze one exact tested P49 bundle commit/tree/blob map and run focused exact-byte self-checks against those bytes.

## Progress / terminal reporting

Follow the repository checkpoint/result protocols. Terminal COMPLETE means the Owner-local handoff bundle is exact-byte-tested and ready for separate local execution. It does NOT mean the real diagnostic ran and does NOT consume the one-run budget.

Final terminal commit prefix:
`WORKER_RESULT ALPHA_V1_PRODUCT_TAKEOVER_P49_OWNER_WINDOWS_ONE_RUN_HANDOFF_BRIDGE COMPLETE`

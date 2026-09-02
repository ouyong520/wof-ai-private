# Alpha V1 Proof-Authority Hardening Integration Fix V4 Recovery V5

## PM authorization

This is an explicit PM-authorized stale-worker recovery. The prior Integration Fix V4 worker has stopped while its canonical claim remains ACTIVE. Do not overwrite, delete, steal, reuse, or mutate the old V4 claim/token. Use a fresh recovery dedup key and preserve all historical claims as residue.

## Goal

Resume the stopped current-main Proof-Authority Hardening Integration Fix V4 from its durable implementation state and finish only the remaining authority-v2 integration closeout needed to authorize the one final Fresh QA.

## Current durable state to re-read, never assume

Re-read current `main`, the V4 start prompt, Recovery V3 closeout BLOCKED result, V4 canonical/stage claims, current proof-tool blobs, current `RUN_MANIFEST.json`, and all commits after V4 claim creation.

Known durable implementation commits include, subject to current-main verification:
- external authority-v2 trust contract;
- Worker authority-v2 signer/lifecycle authority;
- Top authority-v2 trust/lifecycle binding;
- coherent authority-v2 loader bootstrap;
- authority-v2 implementation regression expansion.

The worker stopped before a terminal RESULT. At PM recovery staging time, `RUN_MANIFEST.json` was still on the old proof-authority-fix-v1 pins.

## Required work

1. Verify the exact current authority-v2 candidate is coherent across proof core, Top, Worker, loader, external trust/root contract, lifecycle/mapping authority, evidence schema, regression and safety inputs.
2. Run only the implementation-owned authority-v2 regression needed to close this implementation stage. Do not run the prepared Final Fresh-QA fixture.
3. Confirm the non-self-authenticating signer/root trust path is runnable and does not trust a Worker's self-announced key/fingerprint.
4. Confirm exact authority tuple binding and revocation across proofSession, workerGeneration, runtimeEpoch, pairGeneration and pairNonce.
5. Confirm player respawn and enemy replacement/lifecycle invalidation, same-slot continuity fail-closed, enemy type-offset lifecycle isolation, surface/drawing-buffer mapping authority, strict primitive epoch/warningSampleAt/target, stale/replay rejection, cross-authority aggregation rejection and private terminal-state enforcement.
6. Confirm exact safety invariants: `readOnly=true`, `ramWrites=0`, `inputInjection=false`, `workerReplacement=false`.
7. Repin `parallel/ALPHA_V1_ANCHORED_OVERLAYS_ONE_SESSION_LIVE_PROOF_TOOLING/RUN_MANIFEST.json` to the exact coherent authority-v2 fixed candidate and current critical blobs. Do not certify incomplete/stale blobs.
8. Write a durable Recovery V5 RESULT and close only the Recovery V5 claim/stage token you own.

## Hard boundaries

Do not start Browser/WOF.
Do not run the one Final Fresh QA.
Do not modify `product/alpha/**`.
Do not modify danger rules, target semantics, Transport, input/AI, PYLAUNCH, Recorder, OneClick runtime, or already-PASS gates.
Do not run second-opinion/cross-check/extra QA.

## Dedup

Use canonical dedup v2 recovery with a new key such as:
`alpha.v1.proof-authority-hardening-integration-fix-v4-recovery-v5`

The historical V4 ACTIVE claim remains untouched.

## Terminal success

Only when the current authority-v2 runnable proof path, implementation regression, safety boundary and exact RUN_MANIFEST are coherent, publish:

`COMPLETE — ALPHA V1 PROOF-AUTHORITY HARDENING INTEGRATION FIX V4 RECOVERY V5 — AUTHORITY-V2 RUNNABLE PATH / TRUST ROOT / LIFECYCLE / MANIFEST COHERENT — READY FOR THE ONE FINAL FRESH QA`

Otherwise publish one precise BLOCKED result and stop.

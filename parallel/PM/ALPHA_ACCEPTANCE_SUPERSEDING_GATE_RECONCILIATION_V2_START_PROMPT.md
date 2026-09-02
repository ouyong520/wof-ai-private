# WOF Alpha — Acceptance Superseding-Gate Reconciliation V2

stageId: `ALPHA_ACCEPTANCE_SUPERSEDING_GATE_RECONCILIATION_V2`
dedupProtocol: `v2`
dedupKey: `alpha.acceptance.superseding-gate-reconciliation.current-head`
dedupMode: `exclusive`

Priority: **P1 Alpha acceptance/release gate**

Purpose: update and independently verify the repository-only Alpha acceptance preflight so it consumes current authoritative successor gates on current `main`, preserves historical BLOCKED evidence without requiring it to be rewritten, and treats mandatory enemy target-head labels as a first-release gate. This V2 prompt supersedes the unclaimed pre-v2 `ALPHA_ACCEPTANCE_SUPERSEDING_GATE_RECONCILIATION_V1` start prompt for new execution.

## Start / canonical dedup

Before task work, re-read latest `main`, `parallel/PM/STAGE_DEDUP_GUARD.md`, current stage/canonical claims, recent Alpha/Formal/Unified/PYLAUNCH/OneClick/endurance commits, and at minimum:

- `parallel/PM/ALPHA_ACCEPTANCE_SUPERSEDING_GATE_RECONCILIATION_START_PROMPT.md` as historical intent;
- current Alpha Acceptance prep/result/orchestrator/tests;
- current Formal Recovery V2 implementation result;
- `ALPHA_FORMAL_REAL_ADAPTER_CURRENT_BLOB_REVALIDATION_V1` claim/result;
- current PYLAUNCH Startup Attestation fresh QA result/claim;
- current Unified Recorder in-flight atomicity QA result/claim;
- current Unified current-head preflight Fresh QA V2 result/claim;
- current True 5h endurance claim/run/checkpoint evidence;
- current Owner OneClick V3 prompt/claim/result if any;
- current enemy target-head-label implementation, strict-type fix result, V1 BLOCKED QA, V2 QA/cross-check claims/results if they exist;
- current Release Freeze V2 prompt.

If equivalent current-head acceptance gate reconciliation is already COMPLETE/PASS, stop `ALREADY COMPLETE — SAFE TO CLOSE`.

Otherwise the first mutation is create-only canonical claim:

`parallel/PM/DEDUP_CLAIMS/alpha.acceptance.superseding-gate-reconciliation.current-head.json`

with a fresh unpredictable `claimToken`. Re-read current `main` and verify exact ownership per dedup v2 before creating:

`parallel/PM/STAGE_CLAIMS/ALPHA_ACCEPTANCE_SUPERSEDING_GATE_RECONCILIATION_V2.json`

Any ownership ambiguity or occupied equivalent claim fails closed as `ALREADY CLAIMED — SAFE TO CLOSE`.

## Hard upstream rule

Current authoritative Formal Real-Adapter fresh QA/current-blob revalidation must be COMPLETE/PASS before changing acceptance gate logic. That prerequisite is satisfied only if the current exact Formal result/claim says so; do not inherit chat state.

Other release gates may still be pending while this stage executes. The acceptance preflight itself must correctly remain BLOCKED on any required missing/stale/BLOCKED gate. This stage can PASS as a repository gate-reconciliation implementation/QA stage when the preflight policy is current and fail-closed; it must not fabricate that the release candidate is already admissible.

## Required reconciliation

At minimum:

1. historical adversarial Formal BLOCKED evidence remains immutable historical evidence and is not required to change state;
2. require current authoritative Formal successor/current-blob PASS semantics and exact freshness where pinned;
3. require current PYLAUNCH Startup Attestation PASS/current blobs;
4. require current Unified Recorder generation/in-flight PASS/current runtime where release policy consumes it;
5. require current Owner OneClick package PASS/current manifest when mandatory by Release Freeze;
6. require true 5h endurance PASS/current pinned Safe Transport snapshot when mandatory by current Release Freeze policy;
7. require mandatory enemy target-head-label implementation COMPLETE plus fresh independent QA PASS/currentness on exact release-consumed blobs; V1 historical BLOCKED must remain historical after a valid successor PASS;
8. if Head Labels QA V2 is still pending/BLOCKED, current live preflight must block precisely rather than guess success;
9. preserve bounded real Browser/WOF acceptance requirement for visible correct `1P/2P/3P`, movement/camera following, real retarget with no stale label, and uncertainty fail-closed;
10. preserve Chinese-first precise blocker text and no Browser access before repository gates pass;
11. validate result/verdict semantics, not merely `state=COMPLETE`;
12. preserve read-only/no-RAM-write/no-input/no-Worker-replacement/no-Blob-rewrite safety invariants.

## Required deterministic QA

Add/update repository-side acceptance preflight tests for at least:

- historical Formal BLOCKED + current successor/current-blob PASS => no false block from historical state alone;
- current Formal successor missing/BLOCKED/stale => block;
- PYLAUNCH successor missing/BLOCKED/blob drift => block;
- Unified Recorder successor missing/BLOCKED/blob drift => block when required;
- required Owner OneClick package missing/stale => block when required;
- required 5h endurance missing/BLOCKED/stale snapshot => block when required;
- Head Labels implementation missing or V2/current fresh QA missing/BLOCKED/stale => block before Browser;
- a fixture with all repository-side gates green => preflight-only PASS while still reporting bounded real target-label visual acceptance pending if no live evidence exists.

Run current repository acceptance preflight/unit commands where available. Do not launch Browser/WOF in this stage.

## Write boundary

Write only:
- `parallel/ALPHA_ACCEPTANCE_CURRENT_HEAD_PREP/**` gate/preflight/docs/tests as needed;
- `parallel/ALPHA_ACCEPTANCE_SUPERSEDING_GATE_RECONCILIATION_V2/**` evidence/result;
- this stage claim and canonical claim updates.

Do not modify product/Alpha transport, Formal implementation, PYLAUNCH, Unified/Recorder, Owner OneClick, Safe Transport, HUD, or historical claims/results.

## Drift rule

Immediately before finalization, re-read current `main` and authoritative release-gate claims/results. If a release-consumed policy/blob changed, retest/reconcile against current facts. Documentation-only drift may be recorded as non-invalidating if release-consumed blobs/policies are unchanged.

## Stops

Success:
`PASS — ALPHA ACCEPTANCE SUPERSEDING-GATE RECONCILIATION V2 — REPO PREFLIGHT POLICY CURRENT / RELEASE ADMISSION STILL FAIL-CLOSED ON OPEN GATES`

Failure:
`BLOCKED — ALPHA ACCEPTANCE SUPERSEDING-GATE RECONCILIATION V2 — <precise blocker>`

Owner action during this repository stage: **NO**.

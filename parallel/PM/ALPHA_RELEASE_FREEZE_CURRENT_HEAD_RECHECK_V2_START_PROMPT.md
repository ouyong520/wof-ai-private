# WOF Alpha — Release Freeze Current-HEAD Recheck V2

stageId: `ALPHA_RELEASE_FREEZE_CURRENT_HEAD_RECHECK_V2`

Priority: **P1 final repository release gate**

Follow `parallel/PM/STAGE_DEDUP_GUARD.md` before any work.

## PM reason

The historical `ALPHA_RELEASE_FREEZE_READINESS_AUDIT_V1` targeted an older HEAD and correctly found then-current blockers, but its verdict must not be mechanically reused after subsequent fixes/QA. This stage is a fresh current-head reconciliation/audit after the successor gates close.

The goal is not to invent more work; it is to determine whether the exact current HEAD can be frozen, and if not, name the smallest remaining real blocker.

## Dedup / claim

Re-read latest main, all Alpha release-gate claims/results, current package manifest, acceptance preflight, and any newer freeze audit.

If a newer current-head freeze result already certifies the same release-candidate product/package snapshot, stop:

`ALREADY COMPLETE — SAFE TO CLOSE`

If equivalent freeze recheck is ACTIVE, stop:

`ALREADY CLAIMED — SAFE TO CLOSE`

Otherwise atomically create:

`parallel/PM/STAGE_CLAIMS/ALPHA_RELEASE_FREEZE_CURRENT_HEAD_RECHECK_V2.json`

with exact audit-target current main commit.

## Hard upstream gates

Do not start a final freeze audit while required release-owned fixes are still moving. Require current evidence for:

1. Formal Real-Adapter Integration Recovery V2 COMPLETE;
2. `ALPHA_TRANSPORT_FORMAL_REAL_ADAPTER_INTEGRATION_FRESH_QA_V1` COMPLETE/PASS on current production blobs;
3. `PYLAUNCH_STARTUP_ATTESTATION_QA_V1` COMPLETE/PASS and tested PYLAUNCH blobs still current;
4. `UNIFIED_LIVE_PROOF_RECORDER_AUTHORITY_GENERATION_QA_V1` COMPLETE/PASS on current Unified runtime;
5. `OWNER_ONECLICK_CURRENT_HEAD_RELEASE_REFRESH_V3` COMPLETE/PASS with manifest matching current selected release runtime;
6. `ALPHA_ACCEPTANCE_SUPERSEDING_GATE_RECONCILIATION_V1` COMPLETE/PASS and repo-only acceptance preflight green;
7. current required Safe Transport regression gates green;
8. `ALPHA_TRANSPORT_TRUE_5H_ENDURANCE_RECOVERY_V2` COMPLETE/PASS if current release policy still requires true 5h robustness evidence.

If the current authoritative release policy has superseded or explicitly removed any listed historical requirement, document that exact superseding evidence rather than silently carrying or dropping it.

## Audit method

For every historical blocker classify current disposition exactly as one of:

- `STILL_BLOCKING`
- `FIXED_WAITING_FRESH_QA`
- `SUPERSEDED`
- `CLOSED`

Do not infer current state from an old claim label alone. Verify the blocker condition against current source blobs and successor QA evidence.

At minimum re-check:

- detector-local exact World 921031 identity freshness;
- same-targetId runtime/execution-context replacement fail closed;
- formal transport pair/session/generation/nonce/runtime-epoch/rebind authority;
- PYLAUNCH startup Browser attestation + runtime generation freshness;
- Unified Recorder source-generation authority;
- current Owner OneClick manifest/current runtime equality;
- RC5/bootstrap/game-unaffected failure behavior;
- read-only/no-input/no-Worker-replacement/no-Blob-rewrite invariants;
- Acceptance repo preflight current successor gates;
- current true 5h evidence validity against exact Safe Transport snapshot;
- HUDANCHOR current release-facing P1 status, without reopening already closed confidence/bounds fixes unless current source drift invalidated their fresh QA.

## Current-HEAD drift and package rule

Pin the exact audit-target HEAD and all release-consumed production/package blobs. Re-read main immediately before finalization.

If main moved only by PM/result/audit documentation and every release-consumed blob is unchanged, record non-invalidating metadata drift explicitly.

If any release-consumed blob moved, do not declare freeze PASS until its required freshness-sensitive QA/package evidence is rebound or rerun.

## Read / write boundary

This is an audit/reconciliation lane.

Write only:

- `parallel/ALPHA_RELEASE_FREEZE_CURRENT_HEAD_RECHECK_V2/**`;
- the dedicated stage claim.

Do not modify product/runtime/package implementation in this audit. If a real defect is found, stop and assign the owning lane rather than fixing across boundaries.

## Acceptance / Owner boundary

Separate repository release readiness from real Owner WOF acceptance:

- If all repository-side gates are PASS but the prepared Alpha acceptance contract still requires one bounded real Browser/WOF session with normal owner play/confirmation, classify that as the **only remaining Owner action** and do not call runtime acceptance PASS without evidence.
- Do not request Owner action while any repository-side P0/P1 gate remains open.
- Do not require DevTools, Worker Console, pasted JavaScript, RAM writes, or gameplay input injection.

## Success stops

### Repository freeze-ready

If every repository-side release gate is current and green, package is current, required robustness evidence is valid, and no P0/P1 remains:

`PASS — ALPHA RELEASE FREEZE CURRENT-HEAD RECHECK V2 — REPOSITORY FREEZE-READY`

Record whether final bounded Owner acceptance is still required by the current acceptance contract.

### Fully accepted/freeze-ready

Only if current authoritative acceptance evidence is also already present and valid for the exact release snapshot:

`PASS — ALPHA CURRENT-HEAD ACCEPTANCE + RELEASE FREEZE GATES CLOSED`

Do not fabricate this branch.

## Failure stop

On any real current P0/P1 blocker or stale mandatory gate:

`BLOCKED — ALPHA RELEASE FREEZE CURRENT-HEAD RECHECK V2 — <smallest real blocker>`

Update claim BLOCKED with exact current evidence and downstream owner lane.

Owner action: **NO unless and until every repository-side gate is green and the only remaining current contract requirement is the bounded real Browser/WOF acceptance.**
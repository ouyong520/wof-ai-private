# Alpha V1 Proof-Authority Hardening V2 — Final Fresh QA Independent Fixture Prep

stageId: `ALPHA_V1_PROOF_AUTHORITY_HARDENING_V2_FINAL_FRESH_QA_FIXTURE_PREP`
dedupProtocol: `v2`
dedupKey: `alpha.v1.proof-authority-hardening-v2.final-fresh-qa-fixture-prep`
dedupMode: `exclusive`

Priority: **P0 pre-live QA acceleration / independent fixture preparation**

Repository: `ouyong520/wof-ai-private`

## Context

Proof-Authority Hardening Fix V2 is still an ACTIVE implementation owner. The final independent Fresh QA must not start until that implementation closes COMPLETE with exact fixed blobs.

The project intends to run exactly **one** Fresh QA after Hardening V2. Do not create another cross-check loop.

## Goal

Prepare the independent deterministic negative/positive authority fixtures and expected assertions now, so once Hardening V2 completes the final Fresh QA can execute immediately against the exact fixed blobs.

This stage is **fixture preparation only**. It must not issue PASS/BLOCKED against the current proof implementation.

## Must read

- `parallel/PM/ALPHA_V1_ANCHORED_OVERLAYS_PROOF_AUTHORITY_HARDENING_FIX_V2_START_PROMPT.md`;
- `parallel/ALPHA_V1_ANCHORED_OVERLAYS_ONE_SESSION_LIVE_PROOF_TOOLING/PROOF_AUTHORITY_FIX_CROSSCHECK_V2_RESULT.md`;
- current proof-tooling public interfaces / RUN_MANIFEST only as needed to build an independent fixture contract.

Implementation-owned regression may be inspected only to avoid duplicating it; it is supportive evidence later, never the independent fixture authority.

## Required fixture coverage

Prepare deterministic cases/assertions covering at least:

1. untrusted witness/signer provenance is rejected;
2. repository/synthetic evidence cannot be accepted as real live Worker/Browser evidence;
3. accepted authority is bound to the exact proof session, Worker/runtime generation and pair authority;
4. old capability is invalid after authority generation/epoch/pair changes;
5. phases/events from different authority identities cannot aggregate into one terminal success;
6. player respawn/replacement invalidates old body/head calibration;
7. enemy same-slot replacement is not treated as same-occupant retarget without lifecycle continuity;
8. unsafe enemy calibration/type-offset reuse across lifecycle fails closed;
9. stale or mismatched surface/drawing-buffer mapping authority fails closed;
10. malformed/coercible epoch inputs fail closed;
11. malformed/coercible/non-finite warning timestamps fail closed with no freshness fallback;
12. malformed/coercible target inputs fail closed where consumed;
13. public mutable/session-serialized state cannot force terminal `IMPLEMENTATION_READY`;
14. stale/replayed transaction evidence is rejected;
15. valid same-authority, same-lifecycle retarget/live flow remains accepted;
16. safety boundaries remain exact: readOnly=true, ramWrites=0, inputInjection=false, workerReplacement=false;
17. synthetic evidence cannot activate production projection/calibration profile.

## Independence rules

- Create a QA-owned fixture namespace distinct from implementation regression files.
- Do not copy expected outputs from Hardening V2's own regression.
- Derive expected outcomes from the PM hardening contract and Cross-check V2 blocker semantics.
- Fixture must be deterministic and runnable against a later exact SUT blob set.
- It may validate its own fixture schema/helpers, but must not execute the current proof implementation to produce a release verdict.

## Deliverable

Produce:

- independent fixture files;
- fixture catalog mapping each case to expected allow/deny/fail-closed behavior;
- exact future Fresh-QA command/entrypoint;
- list of SUT files/blobs that must be pinned after Hardening V2 closes;
- explicit statement that this prep stage issued no SUT verdict.

Do not create the actual final Fresh-QA canonical claim yet. That belongs to the post-Hardening execution stage.

## Scope

QA-prep only.
Do not modify `product/alpha/**`.
Do not modify proof implementation.
Do not start Browser/WOF.
Do not modify danger rules, target semantics, Transport, PYLAUNCH, Recorder, OneClick, input/AI.
Do not declare release readiness.

## Success

`COMPLETE — ALPHA V1 PROOF-AUTHORITY HARDENING V2 FINAL FRESH-QA FIXTURE PREP — INDEPENDENT FIXTURE READY / NO SUT VERDICT ISSUED`

## Failure

`BLOCKED — ALPHA V1 PROOF-AUTHORITY HARDENING V2 FINAL FRESH-QA FIXTURE PREP — <precise fixture-preparation blocker>`

Strict canonical dedup v2. Stop duplicate-safe if equivalent fixture-prep work is already COMPLETE or ACTIVE.
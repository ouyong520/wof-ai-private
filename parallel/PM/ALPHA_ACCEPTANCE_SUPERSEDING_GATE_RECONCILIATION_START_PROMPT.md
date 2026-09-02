# WOF Alpha — Acceptance Superseding-Gate Reconciliation

stageId: `ALPHA_ACCEPTANCE_SUPERSEDING_GATE_RECONCILIATION_V1`

Priority: **P1 Alpha acceptance/release gate**

Follow `parallel/PM/STAGE_DEDUP_GUARD.md` before any work.

## PM reconciliation finding

`ALPHA_ACCEPTANCE_CURRENT_HEAD_PREP_V1` is correctly COMPLETE as **prep only**, but its current preflight is stale relative to the superseding release-gate model.

Current `parallel/ALPHA_ACCEPTANCE_CURRENT_HEAD_PREP/acceptance_orchestrator.py` hardcodes both:

- `ALPHA_TRANSPORT_FORMAL_REAL_ADAPTER_INTEGRATION_RECOVERY_V2.json` must be `COMPLETE`; and
- historical `ALPHA_FORMAL_INTEGRATION_ADVERSARIAL_REVIEW_V1.json` must itself become `COMPLETE`.

The historical adversarial claim is intentionally durable BLOCKED evidence and must not be rewritten. Its exact detector-local/same-targetId blocker was fixed later by Recovery V2, and closure must be represented by the newer independent Formal Integration fresh-QA result.

Therefore, without reconciliation, even a valid new fresh-QA PASS would still be blocked by an obsolete historical claim-state check.

## Dedup / claim

Re-read latest main, acceptance prep/result, historical adversarial result, and all current formal-integration QA claims.

If the current acceptance preflight already consumes the authoritative superseding fresh-QA gate and no longer requires rewriting the historical blocker, stop:

`ALREADY COMPLETE — SAFE TO CLOSE`

If equivalent reconciliation is ACTIVE, stop:

`ALREADY CLAIMED — SAFE TO CLOSE`

Otherwise atomically create:

`parallel/PM/STAGE_CLAIMS/ALPHA_ACCEPTANCE_SUPERSEDING_GATE_RECONCILIATION_V1.json`

with exact current main start commit.

## Hard upstream gate

Do not invent the successor claim name or PASS semantics before evidence exists. Proceed with the final gate rewrite only after:

`ALPHA_TRANSPORT_FORMAL_REAL_ADAPTER_INTEGRATION_FRESH_QA_V1` = COMPLETE/PASS.

Also re-read current Release Freeze requirements before finalizing the full preflight gate set.

If the formal fresh-QA result is not yet green, stop without product changes:

`WAITING_GATE — ACCEPTANCE GATE RECONCILIATION WAITS FOR FORMAL FRESH QA`

## Goal

Make the bounded current-head acceptance preflight consume **current authoritative successor gates** rather than requiring historical BLOCKED claims to be rewritten, while remaining fail closed before any Browser/WOF access.

## Required reconciliation

At minimum:

1. preserve `ALPHA_FORMAL_INTEGRATION_ADVERSARIAL_REVIEW_V1` as immutable historical BLOCKED evidence;
2. require Recovery V2 COMPLETE plus the new independent Formal Integration fresh-QA COMPLETE/PASS result that supersedes that blocker;
3. keep durable Formal Integration result/seam requirements;
4. keep current local Safe Transport/Formal Integration/PYLAUNCH offline command gates;
5. consume current PYLAUNCH startup-attestation PASS only while its tested production blobs remain current;
6. consume current `UNIFIED_LIVE_PROOF_RECORDER_AUTHORITY_GENERATION_QA_V1` fresh-QA PASS if current Release Freeze policy requires it before real acceptance;
7. consume Owner OneClick current-snapshot package PASS if current Release Freeze policy requires current package delivery before real acceptance;
8. consume true 5h endurance PASS only if the current authoritative Release Freeze policy still treats it as mandatory; do not silently drop an existing mandatory gate, and do not add unrelated gates merely for completeness;
9. emit precise Chinese-first blocker text naming the current missing/superseded gate;
10. remain fail closed before Browser access if any required current release gate is not green.

The gate implementation should validate not merely `state=COMPLETE` but the result/verdict fields needed to distinguish COMPLETE/PASS from a claim whose state or result does not actually certify the required release condition.

## Required QA

Add deterministic repository-side preflight tests covering at least:

- historical adversarial claim remains BLOCKED + successor fresh QA PASS => no block from the historical state alone;
- successor fresh QA missing/BLOCKED => preflight blocks;
- current production blob drift relative to a freshness-sensitive QA result => preflight blocks or reports stale according to that gate's contract;
- missing durable result => blocks;
- required Recorder/OneClick/endurance release gate missing => blocks when current freeze policy marks it mandatory;
- all current repo-side gates green => `--preflight-only` PASS without connecting Browser.

Run:

`python parallel/ALPHA_ACCEPTANCE_CURRENT_HEAD_PREP/acceptance_orchestrator.py --preflight-only`

or its current equivalent. The successful preflight must not require a live Browser/WOF instance.

## Read / write boundary

Read all current release-gate claims/results/contracts.

Write only:

- `parallel/ALPHA_ACCEPTANCE_CURRENT_HEAD_PREP/**` gate/preflight/docs/tests as needed;
- the dedicated stage claim.

Do not modify product/Alpha transport, PYLAUNCH, Recorder/Live Proof, Owner OneClick, HUD, or historical claim files.

## Downstream consumer

- Alpha Release Freeze current-HEAD recheck;
- the already-prepared bounded real Browser/WOF acceptance, only after repo-side gates are green.

## Drift rule

Immediately before finalizing, re-read main and current authoritative gate claims/results. If a successor gate changed, update/retest the acceptance preflight against the new current facts; do not freeze old claim names merely because this stage started earlier.

## Success stop

`PASS — ALPHA ACCEPTANCE SUPERSEDING-GATE RECONCILIATION — REPO PREFLIGHT CURRENT`

Update claim COMPLETE with tested HEAD, exact gate set consumed, deterministic test evidence, and ownerAction=`NO` for this repository-side stage.

## Failure stop

`BLOCKED — ALPHA ACCEPTANCE SUPERSEDING-GATE RECONCILIATION — <precise blocker>`

If the only remaining step after all repository-side gates pass is the bounded real Browser/WOF acceptance described by the prep, say so explicitly; do not fabricate runtime evidence.

Owner action during this stage: **NO**.
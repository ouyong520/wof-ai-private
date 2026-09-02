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

A later product decision also makes **enemy target head labels mandatory for Alpha V1**: every supported live enemy must be able to show its current target directly above the enemy as `1P`, `2P`, or `3P`, with retarget-safe/fail-closed behavior. Acceptance must not omit this requirement merely because the older prep predates it.

## Dedup / claim

Re-read latest main, acceptance prep/result, historical adversarial result, all current formal-integration QA claims, and current Alpha V1 target-head-label implementation/QA evidence.

If the current acceptance preflight already consumes the authoritative superseding fresh-QA gates, includes the mandatory Alpha V1 enemy target-head-label gate, and no longer requires rewriting the historical blocker, stop:

`ALREADY COMPLETE — SAFE TO CLOSE`

If equivalent reconciliation is ACTIVE, stop:

`ALREADY CLAIMED — SAFE TO CLOSE`

Otherwise atomically create:

`parallel/PM/STAGE_CLAIMS/ALPHA_ACCEPTANCE_SUPERSEDING_GATE_RECONCILIATION_V1.json`

with exact current main start commit.

## Hard upstream gate

Do not invent successor claim names or PASS semantics before evidence exists. Proceed with the final gate rewrite only after the authoritative Formal Real-Adapter fresh QA is COMPLETE/PASS on the relevant current production blobs.

Also re-read current Release Freeze requirements before finalizing the full preflight gate set.

If the formal fresh-QA result is not yet green/current, stop without product changes:

`WAITING_GATE — ACCEPTANCE GATE RECONCILIATION WAITS FOR FORMAL FRESH QA`

## Goal

Make the bounded current-head acceptance preflight consume **current authoritative successor gates and current Alpha V1 mandatory product requirements** rather than requiring historical BLOCKED claims to be rewritten, while remaining fail closed before any Browser/WOF access.

## Required reconciliation

At minimum:

1. preserve `ALPHA_FORMAL_INTEGRATION_ADVERSARIAL_REVIEW_V1` as immutable historical BLOCKED evidence;
2. require Recovery V2 COMPLETE plus the current independent Formal Integration fresh-QA COMPLETE/PASS result that supersedes that blocker;
3. keep durable Formal Integration result/seam requirements;
4. keep current local Safe Transport/Formal Integration/PYLAUNCH offline command gates;
5. consume current PYLAUNCH startup-attestation PASS only while its tested production blobs remain current;
6. consume current authoritative Unified Recorder generation/in-flight fresh-QA PASS if current Release Freeze policy requires it before real acceptance;
7. consume Owner OneClick current-snapshot package PASS if current Release Freeze policy requires current package delivery before real acceptance;
8. consume true 5h endurance PASS only if the current authoritative Release Freeze policy still treats it as mandatory; do not silently drop an existing mandatory gate, and do not add unrelated gates merely for completeness;
9. require `ALPHA_ENEMY_TARGET_HEAD_LABELS_V1` implementation COMPLETE plus its fresh independent QA PASS/currentness before bounded real acceptance is allowed;
10. preserve a real Browser/WOF acceptance check for the mandatory target-head-label UX: supported live enemies visibly show `1P`/`2P`/`3P` above the correct enemy, labels follow movement, and at least one real retarget changes the label without leaving a stale previous target; projection uncertainty must fail closed rather than show a false player label;
11. emit precise Chinese-first blocker text naming the current missing/superseded gate;
12. remain fail closed before Browser access if any required current release gate is not green.

The gate implementation should validate not merely `state=COMPLETE` but the result/verdict fields needed to distinguish COMPLETE/PASS from a claim whose state or result does not actually certify the required release condition.

## Required QA

Add deterministic repository-side preflight tests covering at least:

- historical adversarial claim remains BLOCKED + successor fresh QA PASS => no block from the historical state alone;
- successor fresh QA missing/BLOCKED => preflight blocks;
- current production blob drift relative to a freshness-sensitive QA result => preflight blocks or reports stale according to that gate's contract;
- missing durable result => blocks;
- required Recorder/OneClick/endurance release gate missing => blocks when current freeze policy marks it mandatory;
- target-head-label implementation or fresh QA missing/stale/BLOCKED => preflight blocks before Browser access;
- all current repo-side gates green => `--preflight-only` PASS without connecting Browser, while still reporting the bounded real target-head-label visual acceptance as pending if it has not yet been performed.

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

If the only remaining step after all repository-side gates pass is the bounded real Browser/WOF acceptance, explicitly include the mandatory enemy `1P`/`2P`/`3P` head-label visual/retarget check in that owner action; do not fabricate runtime evidence.

Owner action during this stage: **NO**.
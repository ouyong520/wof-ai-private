# Alpha V1 Post-Live Acceptance / Freeze Handoff Prep

stageId: `ALPHA_V1_POST_LIVE_ACCEPTANCE_FREEZE_HANDOFF_PREP`
dedupProtocol: `v2`
dedupKey: `alpha.v1.post-live-acceptance-freeze-handoff-prep`
dedupMode: `exclusive`

Priority: **P1 release-close preparation**

Repository: `ouyong520/wof-ai-private`

## Goal

Prepare the exact repository-side handoff that should run after the bounded real Browser/WOF acceptance session succeeds, so a live PASS does not trigger another round of ad-hoc QA or packaging work.

Reuse existing acceptance tooling, V1.0.0 player-test release preparation, Owner OneClick V4 immutable candidate, and release-gate artifacts. Do not rebuild capabilities that already exist.

## Must determine

1. Exact existing acceptance entrypoint/tooling to consume the final live evidence.
2. Exact evidence fields required from the Owner/session for PASS / FAIL / NOT EXERCISED.
3. Which repository gates are already durably CLOSED and must not be rerun after live PASS.
4. Exact conditions for Release Freeze.
5. Exact conditions for `V1.0.0 PLAYER TEST RELEASE` vs `NOT RELEASED`.
6. What to do if only a non-mandatory subcase is `NOT EXERCISED`.
7. What to do if a mandatory subcase is `NOT EXERCISED` without forcing a full-game replay.
8. Verify that a proof-only Hardening/Fresh-QA completion does not require regenerating the OneClick V4 package unless a package-selected runtime blob actually changed.
9. Produce the shortest post-live sequence, ideally one acceptance record/update followed by freeze/release decision.

## Scope

Repository-only preparation.
Do not start Browser/WOF.
Do not modify `product/alpha/**`.
Do not modify danger rules, target semantics, Transport, PYLAUNCH, Recorder, OneClick runtime, or proof tooling.
Do not rerun existing PASS QA.
Do not declare V1 released before real live evidence exists.

## Success

`COMPLETE — ALPHA V1 POST-LIVE ACCEPTANCE / FREEZE HANDOFF PREP — LIVE PASS CAN FLOW DIRECTLY TO FINAL ACCEPTANCE/FREEZE WITHOUT REDUNDANT QA`

## Failure

`BLOCKED — ALPHA V1 POST-LIVE ACCEPTANCE / FREEZE HANDOFF PREP — <precise missing handoff authority>`

Strict canonical dedup v2. Stop duplicate-safe if equivalent work is already COMPLETE or ACTIVE.

# WOF Alpha V1.0.0 — User-Test Release Prep

stageId: `ALPHA_V1_0_0_USER_TEST_RELEASE_PREP_V1`
dedupProtocol: `v2`
dedupKey: `alpha.v1.0.0.user-test-release-prep`
dedupMode: `exclusive`

Priority: **P1 V1.0.0 user-facing release preparation**

## Purpose

Alpha V1.0.0 is approaching its first real-player test release. The remaining P0 implementation/live-proof gates are owned by other stages. This stage must not compete with them or certify release early. Its job is to make the eventual V1.0.0 build usable by a normal Chinese-speaking tester the moment those gates close.

The deliverable is not an internal architecture document. It is a concise player-facing test-release experience and a durable PM release-prep result.

## Start / canonical dedup v2

Before substantive work, re-read current `main`, `parallel/PM/STAGE_DEDUP_GUARD.md`, `parallel/PM/PM_CORE_OPERATING_CHARTER.md`, `parallel/PM/PRODUCT_VERSION_ROADMAP.md`, current stage/canonical claims, recent relevant commits, and at minimum:

- `parallel/PM/ENEMY_TARGET_LOCK_HUD_REQUIREMENT.md`;
- latest Alpha acceptance/current-head result(s);
- latest player-head warning integration/QA/fix result(s);
- latest enemy-head target-label QA result;
- latest anchored-overlay live-proof prep/tooling status;
- `parallel/OWNER_ONECLICK/RESULT.md` and current owner one-click package/entry documentation;
- current Alpha user-facing startup/readme/help surfaces as needed.

If an equivalent current V1.0.0 user-test release prep is already COMPLETE, stop `ALREADY COMPLETE — SAFE TO CLOSE`.

Otherwise first mutation must be create-only canonical claim:

`parallel/PM/DEDUP_CLAIMS/alpha.v1.0.0.user-test-release-prep.json`

with a fresh unpredictable `claimToken`. Re-read current `main` and exact canonical file and verify all v2 ownership fields/token/state. Only then create:

`parallel/PM/STAGE_CLAIMS/ALPHA_V1_0_0_USER_TEST_RELEASE_PREP_V1.json`

Any ownership ambiguity => `ALREADY CLAIMED — SAFE TO CLOSE`.

## Required user-facing release preparation

Prepare a small, Chinese-first V1.0.0 tester package experience that can be finalized after the remaining release gates close.

At minimum define and, where repository ownership allows, implement/document:

1. **One obvious start path** — a normal tester should know what to run/click without understanding Recorder/PYLAUNCH/Transport/HUDANCHOR internals.
2. **What the tester should visibly see** — player-head danger reminder, enemy-head `1P / 2P / 3P`, fixed-HUD fallback when anchoring is not trustworthy, and retarget behavior.
3. **What is intentionally unsupported** — do not imply universal attack coverage, movement guidance, 0-damage assistance, or support beyond current validated scope.
4. **Fail-closed UX** — explain briefly that a missing head marker/fixed-HUD fallback can be correct behavior when positioning authority is uncertain; never instruct the player to treat wrong/drifting placement as acceptable.
5. **A 3–5 minute first-test script** using normal gameplay only: left/right, depth movement, jump, rapid forward/camera scroll, visible enemy labels, retarget where naturally available, and one resize/fullscreen transition if part of the release path.
6. **Simple bug feedback capture** — request only player-observable facts useful to reproduce: what happened, expected behavior, whether marker drifted/wrong player/wrong target/disappeared, approximate scene/enemy, and one screenshot/video if practical. Do not ask users to inspect memory addresses, logs or developer internals by default.
7. **Release notes** framed by user-visible value, not internal commits: what V1.0.0 lets the player do, known limitations, and what the next patches are expected to improve.
8. **Version discipline** — do not call refactor/QA/tooling work a new user release. Preserve the roadmap rule: V1.0.1/V1.0.2 only ship for visible player experience improvements after V1.0.0.
9. **Final release gate placeholder** — clearly state V1.0.0 remains NOT RELEASED until current bounded Browser/WOF non-drift proof and all current P0/P1 release gates pass. Do not pin a final release commit or package hash while upstream product/tooling is still moving.
10. **No product semantic changes** — this stage must not alter danger rules, target semantics, Transport authority, projection constants, game input/AI, or `product/alpha/**` behavior.

## Allowed write scope

Prefer a dedicated lane such as:

- `parallel/ALPHA_V1_0_0_USER_TEST_RELEASE_PREP/**`;
- player-facing release/test documentation under an existing Alpha docs/package surface only if clearly appropriate;
- this stage claim and canonical claim updates.

Do not refresh/freeze a final package manifest that would immediately become stale while current P0 product/tooling stages are still moving. If a package refresh is required later, classify it as a downstream release-finalization gate.

## Stop

PASS only when a normal player can be handed the prepared V1.0.0 test instructions/release notes/feedback flow without needing to understand project internals, while the document still fails closed on the unreleased gate:

`PASS — ALPHA V1.0.0 USER-TEST RELEASE PREP READY — PLAYER-FACING TEST EXPERIENCE PREPARED / FINAL RELEASE GATES STILL REQUIRED`

BLOCKED:

`BLOCKED — ALPHA V1.0.0 USER-TEST RELEASE PREP — <precise blocker>`

Owner action: **NO** during this stage.

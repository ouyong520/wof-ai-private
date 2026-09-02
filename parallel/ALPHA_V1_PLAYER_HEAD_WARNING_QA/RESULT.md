# RESULT — Alpha V1 Player-Head Danger Warning Fresh Independent QA

Stage: `ALPHA_V1_PLAYER_HEAD_WARNING_QA_V1`

Status: **BLOCKED — ALPHA V1 PLAYER-HEAD DANGER WARNING FRESH QA — malformed semantic warning sampleAt bypasses the retarget freshness barrier and can authorize pre-retarget spatial/projection data**

Owner action: **NO**

Browser/WOF launched: **NO**

Product implementation modified: **NO**

## Canonical ownership

- dedupKey: `alpha.v1.player-head-danger-warning.post-integration-fresh-qa`
- canonical claim commit: `e9350b648d0ce7c530d027501e333a11755f8991`
- stage claim commit: `9090328f7e26e2e22c98d1f6980010fd74f67142`
- claimToken ownership was re-read and verified before substantive QA.

## Current SUT

The integration contract was still current at the blocker recheck. The player-head helper blob remained:

- `product/alpha/wof_alpha_player_head_warning.js` — `43b54e361f9bffcc4be278549692d0fb229aae7e`

The production projection profile remains intentionally `UNPROVED` / `DISABLED_UNTIL_BOUNDED_BROWSER_WOF_PROOF`; this QA did not activate or fabricate projection constants.

## Precise blocker

The helper's retarget freshness gate is conditional on `warningSampleAt` already being a primitive finite number:

```js
if(finite(warningSampleAt)&&finite(playerState.sampleAt)&&playerState.sampleAt<warningSampleAt){
  return failAnchor(player,'SPATIAL_BEFORE_WARNING_SAMPLE');
}
if(finite(warningSampleAt)&&finite(projection.sampleAt)&&projection.sampleAt<warningSampleAt){
  return failAnchor(player,'PROJECTION_BEFORE_WARNING_SAMPLE');
}
```

Therefore a missing or malformed semantic warning timestamp disables both retarget barriers rather than failing closed.

The HUD passes `lastMsg?.sampleAt` directly into `warningSampleAt`; its message admission checks the current schema/session/transport pair but does not validate `sampleAt` itself before calling the helper. The Safe Transport pair matcher likewise validates pair/session envelope authority rather than payload timestamp type.

This means the fail-closed invariant is incomplete: if a current-authority semantic warning state has retargeted to P2 while its `sampleAt` is missing/malformed, an older P2 player/projection sample can still authorize an anchored warning. Required behavior is fixed-HUD fallback/no anchored coordinate until semantic timing authority is valid and the post-retarget spatial/projection barrier is satisfied.

The normal current worker emits numeric `sampleAtEpoch = Date.now()`, so this is not a claim that ordinary current worker output is malformed. It is a repository fail-closed defect in the public helper/HUD contract, analogous to other malformed/coercible authority inputs that this QA is required to attack.

## Fresh independent fixture

Durable fixture:

- `parallel/ALPHA_V1_PLAYER_HEAD_WARNING_QA/independent_retarget_sampleat_qa.mjs`
- fixture blob: `0a6e0628b974b3afe715546f45b2c0474d39b81a`
- fixture commit: `b1373e510a93eaaf3968a51e2e93ba3268da14bb`

Durable result:

- `parallel/ALPHA_V1_PLAYER_HEAD_WARNING_QA/independent_retarget_sampleat_result.json`
- result blob: `902c4d72e354438d479447a63b037d6b78f8eead`
- result commit: `04b68f86c002bf65ee0924f7ea6cda84a01a5aa8`

Execution used a byte-exact local reconstruction of the current helper; `git hash-object` matched the current Git blob exactly:

`43b54e361f9bffcc4be278549692d0fb229aae7e`

Command equivalent in a repository checkout:

`node parallel/ALPHA_V1_PLAYER_HEAD_WARNING_QA/independent_retarget_sampleat_qa.mjs`

Result:

- total: **9**
- controls PASS: **3**
- required fail-closed cases FAIL: **6**
- exit code: **1**
- evidence class: `FRESH_INDEPENDENT_RETARGET_SAMPLEAT_REPOSITORY_QA_NOT_BROWSER_WOF_PROOF`

Positive controls independently confirmed:

1. finite `warningSampleAt=1010` with player/projection sample `1000` correctly returns `SPATIAL_BEFORE_WARNING_SAMPLE`;
2. malformed warning epoch correctly fails closed;
3. stale player data correctly fails closed.

All six malformed semantic timestamp attacks incorrectly returned `anchored=1, fixed=0`:

- missing `warningSampleAt`;
- `null`;
- numeric string `"1010"`;
- boxed number;
- `NaN`;
- `Infinity`.

## Why QA stops here

The start prompt explicitly says that if a product defect is found, this lane must stop `BLOCKED` with the smallest precise blocker and evidence and must not modify `product/alpha/**`.

Accordingly this QA does not continue through the remaining broad matrix or use the implementation-stage 21/21 regression to override the newly discovered adversarial failure. That committed regression is supportive-only and does not contain this malformed semantic timestamp attack.

No Browser/WOF proof was attempted, and no live visual/projection claim is made.

## Required narrow follow-up

A narrow implementation fix should make semantic warning timing authority strict/fail-closed before retarget freshness comparisons, with regression coverage for missing, malformed and coercible `warningSampleAt` values. It should preserve the existing valid numeric retarget behavior, 20 ms active spatial publication, 80 ms freshness, fixed-HUD fallback, danger rules, target semantics and Transport authority.

## Final verdict

**BLOCKED — ALPHA V1 PLAYER-HEAD DANGER WARNING FRESH QA — malformed semantic warning sampleAt bypasses the retarget freshness barrier and can authorize pre-retarget spatial/projection data**

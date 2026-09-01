# WOF PRODUCT / ALPHA RC3 FIX — START PROMPT

You own the next bounded WOF Alpha repair stage after PM rejected the RC2 candidate on two remaining release blockers.

Repository:
- `ouyong520/wof-ai-private`

Read first, in this order:
- `parallel/PM/RC2_REVIEW_BLOCKERS.md`
- `parallel/PM/RUNTIME_IDENTITY_CORRECTION.md`
- `parallel/ALPHAID/RECOMMENDED_GUARD.md`
- `parallel/ALPHALIFE/RECOMMENDED_INVALIDATION_POLICY.md`
- `parallel/ALPHALIFE/RC2_REGRESSION_CASES.md`
- `product/alpha/ALPHA_RC2_REPORT.md`
- current `product/alpha/**`
- latest `parallel/ALPHAQA/**`

## Role

This is a fresh PRODUCT FIX stage. It supersedes the completed RC2 implementation chat.

You may modify `product/alpha/**`.
Do not modify PM, ALPHAID, ALPHALIFE or ALPHAQA findings to make them pass.

Your only goal is to produce a new Alpha candidate that preserves the useful RC2 fixes while correcting the two PM blockers below.

## C1 — P0 — bind to the actual Browser program identity

The project owner's live Browser probe has positively matched the canonical main-program halves for:

```text
MAME set: wof
Description: Warriors of Fate (World 921031)
SHA-1 half 1: 10b8cb53a4600e3e76f471a3eee8a600e93096fc
SHA-1 half 2: 52c2d05279623d93b27856e6b76830796a089eae
historical live dispatch delta: +0x34
```

The old prose label `wofr1 / World 921002` must not remain the positive runtime identity for this Browser lineage.

Required implementation:

1. authoritative gate = exact full 1 MiB CPU-logical SHA-256 equality;
2. no reset-vector / sparse dispatch / layout-only fallback may enable warnings;
3. layout/vector/dispatch checks may be used only as locator/sanity helpers;
4. update support labels/signatures/docs/manifest to `wof / World 921031` for this Alpha lineage;
5. fail closed while hash is pending, missing, malformed, mismatched or throws;
6. hash once per Worker/runtime startup, not every poll;
7. preserve read-only and no input injection.

The golden 921031 full CPU-logical SHA-256 will be committed by PM after the one-shot read-only Browser probe. If it is not yet present when you start, prepare the implementation/tests with an explicit placeholder that keeps warnings disabled; do not invent a digest and do not fall back to sparse fingerprint acceptance.

Read `parallel/PM/RUNTIME_IDENTITY_CORRECTION.md` for the handoff state.

Required tests:
- exact supported digest accepts;
- old 921002 or any wrong digest rejects;
- layout + vector + `+0x34` dispatch without full digest rejects;
- hash pending rejects/silences;
- hash error rejects;
- one-byte/digest mutation rejects.

## C2 — P1 — follow the lifecycle audit exactly

The Browser contract still has no proven enemy instance/generation token.

Therefore:

```text
same slot + same type != proven continuity
```

Do not use previous/current history for user-facing warnings unless continuity is positively proven.

For this narrow Alpha, the safe policy is:

- quarantine F1 `T16_B4_DANGER_40` from user-facing production;
- quarantine F2 `T20_5136_B0_TO_B255_1250`;
- quarantine F3 `D867BA_3232_TM6_220`;
- quarantine F4 `D8811E_3232_TM6_135`;
- keep F5 `T18_5440_CYCLE_BODY7512_TM4_LEVEL_90` only as a stateless/hold-only current-level warning;
- keep F6 `T18_5424_CYCLE_BODY7520_TM4_LEVEL_90` only as a stateless/hold-only current-level warning.

For F5/F6:
- publish iff the exact current predicate matches;
- clear on the first current nonmatch;
- a replacement that independently matches creates fresh current evidence;
- never inherit `atMs`, age, watch/cycle state or target provenance from a previous occupant.

Do not preserve six user-facing rules merely for feature count. PM freeze explicitly allows shipping fewer rules for safety.

Required adversarial tests:
- A arms/history state then hidden same-type B appears ACTIVE directly: no inherited warning;
- A previous snapshot + hidden same-type B current snapshot creates apparent entry/transition: no history warning;
- same-type B neutral current: no old warning;
- F5/F6 current match shows; first nonmatch clears immediately;
- matching replacement F5/F6 is fresh current evidence only.

## Preserve useful RC2 fixes

Keep unless a new test proves them unsafe:
- random per-session transport binding / cross-tab isolation;
- all simultaneous warning groups shown;
- safe legacy `WOFHUD.dispose()` takeover;
- simple user bootstrap candidate;
- current live target reread and side recompute;
- UNKNOWN/invalid target silent;
- no game RAM writes;
- no gameplay input injection/autoplay;
- no T18 BODY4728-specific A4704 rule;
- no T23/T24/discovery/local promotion.

## Required outputs

Update/create under `product/alpha/**`:
- corrected core/loader/manifest/docs;
- regression tests for identity and lifecycle blockers;
- a new report `ALPHA_RC3_REPORT.md`;
- exact list of active production rules vs quarantined frozen candidates;
- current user bootstrap instructions.

Do not call old RC2 `PASS` after changing semantics. This is a new candidate and needs a fresh independent QA stage.

## Stop condition

Stop only when:

A. a new RC3 candidate exists, all offline tests pass, exact 921031 full SHA-256 is bound if available, and it is ready for a fresh independent QA retest; or

B. the only remaining blocker is the explicit PM one-shot 921031 full SHA-256 Browser probe, in which case keep production warnings fail-closed and document that exact dependency.

Do not start attack discovery, WOF-052, broad collection or Beta features in this thread.

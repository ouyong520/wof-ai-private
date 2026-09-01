# HUDANCHOR Player-Follow Confidence Fail-Closed Fix Result

Stage: `HUDANCHOR_PLAYER_FOLLOW_CONFIDENCE_FAILCLOSED_FIX_V1`

Status: **HUDANCHOR PLAYER-FOLLOW CONFIDENCE FAIL-CLOSED FIX READY — READY FOR FRESH QA + LONG-STRESS V2**

## Fix delivered

Updated:

- `parallel/HUDANCHOR_PLAYER_FOLLOW/src/player_follow_reference.js`
- `parallel/HUDANCHOR_PLAYER_FOLLOW/test/confidence_failclosed_regression.js`

`PlayerAnchorResolver.resolve()` no longer converts missing/non-finite confidence into permissive anchored authority.

Every confidence value that currently participates in player-head anchor authority is now required to be finite and inside the valid `[0, 1]` confidence domain:

- player-state confidence;
- projection-state confidence;
- live drawing-buffer/mapping confidence;
- projected-result confidence returned by `projectNative(...)`.

Invalid values fail closed with deterministic reasons:

- `INVALID_PLAYER_CONFIDENCE`;
- `INVALID_PROJECTION_CONFIDENCE`;
- `INVALID_DRAWING_BUFFER_CONFIDENCE`;
- `INVALID_PROJECTED_CONFIDENCE`.

This includes `NaN`, `Infinity`, `-Infinity`, missing confidence and finite out-of-domain confidence. No permissive fallback or clamp is allowed to promote those values into anchored authority.

Valid finite confidence behavior remains unchanged: no new confidence threshold was introduced, values in `[0, 1]` remain eligible under the existing contract, and the returned anchor confidence remains the minimum of the four valid authority surfaces.

Because invalid confidence now returns `anchor.ok === false`, the existing renderer path deterministically:

1. routes the warning to fixed HUD;
2. clears follow/smoothing state for that player;
3. never reuses the previous player-head coordinate;
4. preserves immediate old-target invalidation during retarget.

Existing finite out-of-bounds anchor fail-closed behavior remains unchanged.

## Regression coverage

Added targeted deterministic regression:

`parallel/HUDANCHOR_PLAYER_FOLLOW/test/confidence_failclosed_regression.js`

Coverage includes:

1. projection confidence = `NaN` / `+Infinity` / `-Infinity`;
2. player confidence = `NaN` / `+Infinity` / `-Infinity`;
3. drawing-buffer confidence = `NaN` / `+Infinity` / `-Infinity`;
4. projected confidence = `NaN` / `+Infinity` / `-Infinity`;
5. missing confidence on every authority surface;
6. finite out-of-domain confidence is invalid rather than clamped into authority;
7. valid finite confidence at and near `[0,1]` boundaries remains anchored;
8. existing minimum-confidence metadata semantics remain unchanged;
9. invalid confidence after a valid anchored frame clears follow state and recovery resets smoothing;
10. retarget `P1 -> P2` during invalid confidence removes the P1 cue immediately and fixed-fallbacks P2.

Executed with Node `v22.16.0`.

Targeted result:

```json
{"status":"PASS","passed":18,"total":18,"fixture":"SYNTHETIC_CONFIDENCE_FAILCLOSED_ONLY_NOT_BROWSER_PROOF"}
```

Existing bounds regression, unchanged:

```json
{"status":"PASS","passed":8,"total":8,"fixture":"SYNTHETIC_BOUNDS_ONLY_NOT_BROWSER_PROOF"}
```

Existing full player-follow synthetic regression, unchanged:

```json
{"status":"PASS","passed":15,"total":15,"fixture":"SYNTHETIC_ONLY_NOT_BROWSER_PROOF"}
```

## Long-stress blocker closure

The existing V1 long-stress runner was reconstructed byte-for-byte from its committed blob and run without weakening its invariant or editing its source.

Before the fix, against source blob `4beb7f8d4c9f815e125ed795aca536f02562f5d1`:

- directed `invalid projection confidence must fail closed`: **FAIL**;
- overall status: **BLOCKED**;
- `failureCount`: **49**.

After the fix, against patched source blob `e36e80fdad7bcf7f73485f9093aa9014428c86b1`:

- directed invalid-projection-confidence case: **PASS**;
- directed checks: **8 / 8 PASS**;
- deterministic corpus: **16 seeds x 1,024 transitions = 16,384 transitions**;
- `failureCount`: **0**;
- total invalid-confidence anchored observations: **0**;
- final runner status: **PASS**.

The V1 runner contains a historical literal `SUT_BLOB` metadata string for the pre-fix blob. This stage did not modify the long-stress lane because it is outside the hard write boundary. The runner's actual `require('../HUDANCHOR_PLAYER_FOLLOW/src/player_follow_reference')` loaded the patched SUT; local Git blob verification confirmed that executed source was `e36e80fdad7bcf7f73485f9093aa9014428c86b1`. Fresh long-stress V2 should pin/report the new source blob independently.

## Commit / blob evidence

Implementation commit:

- `250f8cb7715b6c9c2acb69e855cb06b62ce94576`

Regression commit:

- `8a0d79e2da9f5661b2183a325d6c9a9c4b8a92d1`

Executed/committed blobs:

- fixed source: `e36e80fdad7bcf7f73485f9093aa9014428c86b1`;
- confidence regression: `1efcac65e9cc5598358c86e968a6b148d9e970a2`;
- unchanged bounds regression: `d5798e3470625d440092aa00a05142157f99799b`;
- unchanged full synthetic regression: `b7d56a74ef520bccb47055bc59558da6dfcb6139`;
- unchanged synthetic fixture: `79e42e675d371ec91715116227fecf0ed3c27d97`;
- unchanged V1 long-stress runner: `1cfde530abbd146e11ece6ae645a3baf7a5e336a`.

## Product / safety semantics preserved

Authoritative behavior remains:

`怪物锁定谁 -> 在被锁定角色 P1/P2/P3 头顶显示提示 -> 跟随角色 -> 不漂移 -> 换锁立即切换`

Preserved:

- fixed HUD as fail-closed fallback whenever anchored spatial authority is invalid/stale/untrusted;
- read-only presentation semantics;
- no RAM writes;
- no gameplay input injection;
- no Worker replacement/wrap;
- no guessed Browser projection constants;
- no changes to Browser proof automation, `parallel/HUDANCHOR/**`, `product/alpha/**`, PYLAUNCH, Recorder, Prospective, Transport or Live Proof.

## Delivery reassessment

Authoritative classification for this repository-side fix: **ACCEPTED_COMPLETE**.

- **Does this close the P1 long-stress blocker?** Yes. The exact blocker-directed case now fails closed, and the unchanged 16,384-transition V1 corpus completes with zero failures against the patched SUT.
- **What downstream stage is newly unblocked?** Fresh independent confidence QA and fresh player-follow long-stress V2 are unblocked. After those repository-side gates pass, the lane can resume the real-projection freeze / Browser-proof critical path.
- **Can long-stress V2 restart now?** Yes. It should pin the new SUT blob and retain the same fail-closed invariant.
- **Is any real Browser/WOF fact still required?** Not for this confidence-authority fix or its synthetic/long-stress validation. Real Browser/WOF player/camera projection facts and live native-to-drawing-buffer mapping are still required for eventual production anchored rendering; they must be externally proved and must not be guessed.
- **Owner action:** NO.

## Stop condition

**HUDANCHOR PLAYER-FOLLOW CONFIDENCE FAIL-CLOSED FIX READY — READY FOR FRESH QA + LONG-STRESS V2**

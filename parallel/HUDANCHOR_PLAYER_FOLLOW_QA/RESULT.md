# HUDANCHOR Player-Follow Reference — Fresh Independent QA Result

Stage: `HUDANCHOR_PLAYER_FOLLOW_REFERENCE_QA_V1`

Terminal status: **BLOCKED — FRESH FIX LANE REQUIRED**

## Precise blocker

`PlayerAnchorResolver.resolve()` validates that `anchorXNative`, `anchorYNative`, `bodyXNative`, and `bodyYNative` are finite, but its projection-bounds rejection checks **only** `bodyXNative/bodyYNative`.

Therefore a projection can return an in-bounds body reference together with a finite but out-of-bounds warning anchor and still receive `ok: true`.

The renderer then maps that invalid anchor into drawing-buffer coordinates and clamps the warning rectangle to the content-rect edge, producing an anchored marker at the screen edge instead of failing closed to fixed HUD.

This directly violates QA requirement 13:

> invalid/out-of-bounds/non-finite anchors must fail closed to fixed-HUD fallback

and can create a visibly detached/stale-looking indicator even though the body projection itself is valid.

## Fresh adversarial regression

Added:

`parallel/HUDANCHOR_PLAYER_FOLLOW_QA/adversarial_out_of_bounds_anchor_regression.js`

The independent fixture intentionally returns:

- body reference: `(192, 112)` inside `0..384 x 0..224` validation bounds;
- case A anchor: `(192, -1000)`;
- case B anchor: `(1000, 80)`.

Required result for both cases:

- `plan.anchored.length === 0`;
- `plan.fixed.length === 1`;
- fixed fallback reason is `PROJECTION_OUT_OF_BOUNDS`.

With the current source logic, both anchors pass the native bounds gate because only the body reference is checked. The mapping then produces finite drawing-buffer points (`yDb=-2000` in case A and `xDb=2000` in case B for the 2x fixture), after which `AnchoredWarningRenderer` clamps the draw rectangle to the content viewport edge and emits it through `anchored` rather than `fixed`.

## Source evidence

Current implementation blob rechecked on `main`:

`parallel/HUDANCHOR_PLAYER_FOLLOW/src/player_follow_reference.js`

blob SHA:

`47a03e1ce459e153ba2b5db42ba10a4d0d746490`

Relevant control flow:

1. all four projected coordinates are checked for finiteness;
2. `validationBounds` are validated;
3. only `projected.bodyXNative` and `projected.bodyYNative` are compared with those bounds;
4. `projected.anchorXNative/anchorYNative` are mapped without a bounds rejection;
5. renderer clamps the resulting rectangle and emits an anchored item.

## Required fresh fix lane

The implementation lane is read-only to this QA stage, so no implementation edit was made.

A fresh fix lane should make the resolver reject finite out-of-bounds **anchor coordinates as well as body coordinates** before native -> drawing-buffer mapping. The fix should preserve the existing fail-closed reason (`PROJECTION_OUT_OF_BOUNDS` is sufficient) and rerun this QA regression plus the implementation lane's existing synthetic suite.

The fix must not invent Browser camera/bias/Y-Z constants and must not broaden into danger rules, RAM writes, input injection, Worker replacement, Blob/Data/ObjectURL rewrite, or product/alpha changes.

## Context boundary confirmed

The QA read and respected:

- authoritative player-head target-lock requirement;
- current player-follow reference implementation and its own 15/15 synthetic suite (not treated as independent proof);
- HUDANCHOR reverse result and `projection_candidate.json`;
- HUDANCHOR Browser proof tooling as read-only context.

Real Browser projection truth remains unproved and was not certified or guessed by this QA.

## Write-scope audit

Writes were confined to:

- `parallel/HUDANCHOR_PLAYER_FOLLOW_QA/**`;
- mandatory PM claim file.

No changes were made to implementation, HUDANCHOR proof/reverse lanes, `product/alpha/**`, PYLAUNCH, Recorder, Prospective, or Browser Fleet.

## Stop condition

**BLOCKED — finite out-of-bounds player anchors are accepted and clamped instead of failing closed to fixed HUD; fresh fix lane required.**

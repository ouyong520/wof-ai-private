# GEO top / bottom closure

Updated: 2026-09-01

Evidence boundary: WinKawaks-local discovery only. Read-only. No game-memory writes. No Browser/WASM production promotion.

## Final verdict

The `top / bottom` phase is closed at the retained **player-object field** level:

- **CONFIRMED floor/depth anchor:** `player+0x08`.
- **CONFIRMED vertical/Z displacement family:** `player+0x0C` integer/modulo component with `player+0x11` subpixel/phase component.
- **REJECTED as explicit sprite top/bottom/extent:** `player+0x9E`.
- **REJECTED as explicit sprite top/bottom/extent:** `player+0xAA`.
- **NO explicit animation-varying sprite top/bottom bound field has been demonstrated inside the retained 0xE0 player object.**
- Actual visual sprite top/bottom therefore remains **descriptor-derived / unresolved outside the proven player-object fields**. The retained evidence is more consistent with frame/sprite descriptor or render-shape data than with a live per-frame bound byte in the player object.

This is a negative representation result, not a claim that sprite bounds do not exist anywhere in game state.

No new animation capture is justified. The canonical BASECAP corpus already contains the required action/animation acquisition scene.

The next permitted GEO phase is `camera / screen coordinate`.

## What is already proven geometrically

The live player coordinate roles are separated:

```text
world X ~= 256 * U8(+0x0B) + U8(+0x04)
floor/depth Y = U8(+0x08)
vertical/Z ~= unwrap_mod256(U8(+0x0C) + U8(+0x11)/256)
```

These are position/displacement anchors. None supplies a frame-dependent sprite half-height or visual top/bottom extent by itself.

In particular:

- `+0x08` is the ground-plane/depth anchor, not a visual sprite-bottom pixel edge;
- `+0x0C/+0x11` describe elevation/vertical displacement, not the current animation frame's top/bottom sprite dimensions.

A future screen-space top/bottom formula must combine the projected anchor/elevation with frame-specific render geometry once that render geometry is resolved.

## Why `+0x9E` is rejected as top/bottom or height

Across the earlier player corpus, `+0x9E` is stable inside player×capture episodes even while animation/action state changes. It therefore does not behave like a per-frame visual top/bottom offset or height.

Across 18 retained stable player modes it takes values including:

```text
0, 18, 30, 31, 32, 34, 36, 38
```

No stable sibling U8/U16 field was found that converts it into a consistent extent through equality, constant difference, or one-to-one factorization.

Enemy cross-check also breaks a universal extent interpretation: enemy `+0x9E` was observed as zero across the audited enemy slot-frames while player values vary.

The narrow surviving interpretation is an independent player-specific form/render/descriptor/state parameter, not a proven top/bottom/height value.

## Why `+0xAA` is rejected as top/bottom or radius

`+0xAA` also fails a universal geometric-extent interpretation. Player values can be stable while enemy objects at the same relative offset are materially dynamic. Its behavior does not establish an axis, sign, scale, or relation to a visual edge.

Therefore it cannot be promoted to width, height, radius, top, or bottom.

## Canonical animation acquisition already exists

The required dynamic scene is already covered by BASECAP v1:

```text
BASECAP-B13-attack-12s60-20260901-0558Z
```

The bounded RAWMINE post-completion audit compared this canonical ordinary-attack run with canonical B00 idle and found **NO_MATERIAL_INCREMENT_B13**. The dominant activity (`+0x7F`) was shared/background-like rather than P1-specific, and no other P1 offset gained useful controlled attack/animation support.

Thus repeating ordinary attack/action animation would duplicate an already canonical scene without supplying a new discriminator.

## Retained raw search result

Multiple high-frequency GEO/EFIELD captures already include complete 0xE0 player objects during movement, jumps, attacks, natural combat, and state transitions. Despite that diversity, no independent player-object byte has been demonstrated to vary as a frame-specific top/bottom extent while remaining geometrically interpretable.

This makes the following representation the current best-supported model:

```text
player object:
  position / depth / elevation / orientation / animation-state references

outside explicit proven player-object geometry bytes:
  frame/sprite descriptor -> render shape / frame-specific visual bounds
```

The second line is a structural inference from the failed explicit-field search; the exact descriptor pointer/table and exact pixel bounds are not yet proven.

## Scope of closure

Closed:

- search for a directly usable explicit live top/bottom/height field in the retained 0xE0 player object;
- `+0x9E` and `+0xAA` extent hypotheses;
- need for another ordinary animation capture.

Not claimed:

- exact sprite-frame descriptor address;
- exact visual top pixel or bottom pixel formula;
- exact screen-space top/bottom before camera/projection is solved.

Those unresolved items are representation/projection derivations rather than missing BASECAP acquisition scenes.

## Stop rule

Do not queue another B13-like attack/animation task. Reuse retained static/ROM/render evidence if a descriptor derivation becomes necessary.

Proceed to canonical B20 and the `camera / screen coordinate` phase.
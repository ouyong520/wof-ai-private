# WOF PLAYER-ANCHORED WARNING HUD AUDIT — START PROMPT

You own a bounded Beta-support research lane for the WOF / Warriors of Fate / 三国志II Future Danger project.

Repository:
- `ouyong520/wof-ai-private`

## Goal

Design and prove the safest way to place a Future Danger warning above the currently threatened P1/P2/P3 character in the Browser game.

This is NOT an Alpha blocker and must not modify the current Alpha release implementation.

## Read first

Read current GitHub state relevant to geometry/rendering/HUD:
- `parallel/PM/ROADMAP.md`
- `parallel/PM/ALPHA_FREEZE_SPEC.md`
- latest Browser HUD / WebGL probe code and findings
- `parallel/GEO/**`
- any camera/screen-coordinate research
- current `product/alpha/wof_alpha_hud.js` read-only for interface context only
- target/retarget evidence from Browser production-shadow work

## Scope and write boundary

Write only under:
- `parallel/HUDANCHOR/**`

Do NOT modify:
- `product/alpha/**`
- Alpha manifests/rules
- production warning semantics

Do NOT use image/color/pixel tracking as the primary solution.
Do NOT guess DOM coordinates from RAM/world coordinates without a proven transform.

## Required questions

1. Identify the best authoritative Browser source for P1/P2/P3 screen position.
2. Determine whether world X/Y/depth plus camera state can be transformed reliably into game-canvas coordinates.
3. Determine how jumping, depth movement, camera scrolling, scaling, fullscreen/window resizing, DPR and canvas letterboxing affect the anchor.
4. Determine whether existing native WebGL render structures expose a better screen-space/player-sprite anchor than reconstructing from world coordinates.
5. Preserve live retarget behavior: when an enemy retargets P1→P2/P3, the warning anchor must follow the current threatened player.
6. Define fail-closed behavior: if the anchor is uncertain, fall back to fixed in-game HUD rather than drawing over the wrong character.
7. Produce a minimal Browser proof plan if retained evidence is insufficient.

## Desired UX

For a valid warning:
- visually associate the warning with the threatened P1/P2/P3;
- place it slightly above that player's visible character/sprite;
- avoid covering the face/body more than necessary;
- handle multiple simultaneous threatened players;
- keep fixed HUD fallback available.

## Required outputs

Create:
- `parallel/HUDANCHOR/README.md`
- `parallel/HUDANCHOR/ANCHOR_MODEL.md`
- `parallel/HUDANCHOR/BROWSER_EVIDENCE.md`
- `parallel/HUDANCHOR/IMPLEMENTATION_RECOMMENDATION.md`
- `parallel/HUDANCHOR/MINIMAL_BROWSER_PROBE.md` only if a small human Browser proof is required.

Clearly classify the result as one of:
- IMPLEMENTATION READY
- NEEDS ONE MINIMAL BROWSER PROOF
- BLOCKED BY MISSING CAMERA/SCREEN TRANSFORM EVIDENCE

## Stop condition

Stop when a Beta implementation owner could implement player-anchored warnings without guessing, or when exactly one minimal Browser proof remains.

Do not start unrelated GEO/attack research, Safe Path, WOF-052, or Alpha product changes.
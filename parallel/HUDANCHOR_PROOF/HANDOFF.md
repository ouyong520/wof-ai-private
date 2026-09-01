# HUD Anchor Browser Proof Tooling — Handoff

## Status

Tooling target: **READY FOR ONE BOUNDED OWNER BROWSER RUN**

This lane does not claim the Beta anchored HUD is implementation-ready yet. Only a successful Browser proof result with:

```text
IMPLEMENTATION_READY
```

may promote the projection constants to a later Beta implementation thread.

## What changed from the previous HUDANCHOR probe

The previous probe was useful but left too much manual work:

- separate manual visual interpretation of three DOM markers;
- manual result command plus prose verdict;
- drawing-buffer mapping was reported but the marker itself was not the direct-WebGL proof plane;
- resize/fullscreen and movement coverage were not objective PASS gates.

The new support-only probe closes those tooling gaps:

1. same one-line loader auto-detects Worker vs Top context;
2. Worker automatically ranks and quality-gates bounded camera candidates;
3. one calibration click is converted through current drawing buffer + `gl.VIEWPORT`;
4. `Y-Z`, `Y+Z`, and `Y` candidate labels are rendered directly into the game WebGL surface;
5. movement coverage is detected from live RAM rather than described back by the owner;
6. resize/fullscreen/DPR/viewport changes are detected and recovery is required;
7. P2/P3 are only required when actually live/observable;
8. final visual classification is one button;
9. final output is one JSON and PASS is fail-closed.

## Camera proof model

The Worker keeps the existing bounded scan before the player object block:

```text
0xFF0000 .. 0xFFBDFF
step 2
read u16be
```

The player object block is deliberately excluded so P1/P2/P3 position words cannot win as false camera candidates.

The candidate score reuses plausibility, strong screen-X occupancy, range, change count, movement-follow correlation, and smoothness. Calibration is blocked until the top candidate passes the quality gate.

A successful owner visual proof freezes:

```text
nativeX = worldX - camera + xBias
```

with the selected camera address/read form from the same session.

## Y/Z proof model

The single calibration point derives three direct warning-anchor hypotheses:

```text
Y-Z + yBiasMinus
Y+Z + yBiasPlus
Y   + yBiasNone
```

The operator does not report coordinates. During depth movement and one jump, the direct-WebGL labels reveal which model remains at the chosen above-character location. The final PASS button freezes exactly that model.

The stored `aboveCharacterOffsetNative` is intentionally a **logical constant from the raw player floor/Z reference to the chosen warning anchor**. It is not a claim that current sprite-top or sprite height has been discovered.

## Drawing-buffer proof model

The top probe records the game WebGL viewport and maps native coordinates into it directly:

```text
viewportTop = drawingBufferHeight - (viewportY + viewportHeight)
xDb = viewportX + nativeX / 384 * viewportWidth
yDb = viewportTop + nativeY / 224 * viewportHeight
```

Calibration runs the inverse mapping from the user's one click.

This is why the proof can survive CSS size, DPR, fullscreen, and letterboxing changes without baking those values into the game-space projection constants.

## Owner action remaining

Run `OPERATOR_STEPS.md` once and return the generated JSON only.

Do not do a new Collector sweep, video frame count, combat capture, or Alpha edit for this proof.

## Next decision

- `IMPLEMENTATION_READY` -> hand the frozen projection block to a **separate Beta HUD implementation thread**.
- `FAILED_COMPONENT:<component>` -> narrow only that component; do not reopen broad player geometry research.

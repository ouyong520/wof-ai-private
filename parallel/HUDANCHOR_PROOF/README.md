# WOF HUD Anchor Browser Proof Tooling

Status: **support-only proof tooling; no Alpha product changes**

This lane reduces the remaining player-head Browser projection proof to one bounded session and one compact result JSON.

## Boundary

This directory is the only write surface for this tooling stage.

It does **not** modify:

- `product/alpha/**`
- warning/rule semantics
- Beta HUD behavior
- emulator speed/input settings

It does not use pixel/color tracking as projection evidence.

## What the probe proves/falsifies

The probe combines the already-proved player object structure with live Browser evidence and checks:

1. horizontal camera/native-X transform;
2. floor/depth screen-Y tracking;
3. jump/Z contribution (`Y-Z`, `Y+Z`, or `Y`);
4. direct WebGL drawing-buffer placement;
5. a stable logical above-character offset;
6. P1/P2/P3 structural reuse when extra players are live;
7. resize/fullscreen/DPR/viewport remapping;
8. fail-closed output if required evidence is missing.

## Important improvement over the older HUDANCHOR v2 probe

The visible candidate markers are now drawn **inside the game WebGL drawing buffer**. DOM is used only for instructions and final buttons.

The top-page probe captures the live `gl.VIEWPORT` before drawing its marker and maps:

```text
client click
  -> drawing-buffer pixels
  -> current game viewport
  -> 384x224 native game coordinates
```

The reverse path used by the candidate marker is:

```text
native 384x224
  -> current WebGL viewport
  -> drawing-buffer pixels
  -> direct WebGL marker draw
```

This makes resize/fullscreen/letterbox/DPR changes part of the proof rather than a separate DOM assumption.

## Runtime split

The emulator still has two relevant JS contexts:

- Worker: CPS RAM and player/camera candidate scan;
- Top page: canvas/WebGL and visual projection.

A top-page script cannot safely reach the existing Worker realm directly, so the smallest practical operation remains the **same one-line loader in each context**. The two halves communicate through `BroadcastChannel`.

## Loader

Run this exact line once in the game Worker Console and once in the Top page Console:

```js
fetch('https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/parallel/HUDANCHOR_PROOF/wof_hudanchor_proof.js?'+Date.now()).then(r=>r.text()).then(t=>(0,eval)(t))
```

Then follow `OPERATOR_STEPS.md`.

## Result

The Top probe exposes:

```js
WOFHUDANCHOR.result()
```

A final PASS/FAIL button also generates the JSON automatically and attempts to copy it to the clipboard.

The only successful terminal verdict is:

```text
IMPLEMENTATION_READY
```

Every incomplete or disproved path fails closed as:

```text
FAILED_COMPONENT:<component>
```

See `RESULT_SCHEMA.md`.

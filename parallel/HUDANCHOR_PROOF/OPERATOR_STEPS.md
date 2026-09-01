# HUD Anchor Browser Proof — Operator Steps

This is one bounded Browser proof. No combat choreography and no manual coordinate transcription are required.

## 1. Load Worker half

In the game **Worker Console**, run:

```js
fetch('https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/parallel/HUDANCHOR_PROOF/wof_hudanchor_proof.js?'+Date.now()).then(r=>r.text()).then(t=>(0,eval)(t))
```

Expected:

```text
✅ HUDANCHOR proof Worker ready
```

## 2. Load Top half

In the **Top page Console**, run the exact same line.

Expected:

```text
✅ HUDANCHOR proof Top ready
```

A small instruction panel appears outside the game-coordinate evidence path.

## 3. Camera signal

Control P1 normally and move left/right far enough that the **background visibly scrolls**.

The panel automatically waits until the bounded CPS camera scan has a sufficiently strong/stable candidate. No address selection is required from you.

## 4. One calibration click

When the panel says Camera is stable, click **once** at the center point where the warning should sit above P1's head.

This click is the only coordinate ground truth you provide. It is converted through the live WebGL drawing buffer and current `gl.VIEWPORT`; it is not pixel recognition.

## 5. Normal movement proof

Without reloading:

1. keep moving left/right and make the background scroll;
2. move clearly upward/downward in floor depth;
3. jump once;
4. resize the browser window or toggle fullscreen once, then return to a stable layout.

The panel marks each objective evidence bucket automatically.

Three direct-WebGL candidate labels may separate during jump:

- `Y-Z`
- `Y+Z`
- `Y`

Observe which one remains at the chosen above-character point. During ordinary non-jump movement they may overlap.

If P2/P3 are live, press `F6` to cycle focus and look at each live player for about one second. If P2/P3 are not live, this requirement is automatically treated as not observable rather than forcing another player session.

`F7` re-arms calibration only if the initial click was bad.

## 6. Finish with one button

When all objective evidence marks are complete, click exactly one final conclusion in the panel:

- `PASS Y-Z`
- `PASS Y+Z`
- `PASS Y`
- or the specific failure button (`X/camera drift`, `depth drift`, `jump/Z fails`, `marker/DB fails`, `resize drift`, `P2/P3 drift`, `clearance unstable`).

The probe immediately generates one compact JSON and attempts to copy it to the clipboard.

If needed, the same JSON is available with:

```js
WOFHUDANCHOR.result()
```

Do not manually summarize coordinates. Return the JSON object only.

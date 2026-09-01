# HUDANCHOR Minimal Browser Proof

Status: **the only remaining human Browser proof for this lane**

This is one bounded test session. It does not modify Alpha or production semantics.

## Why two console contexts are unavoidable

The current Browser architecture separates:

- live CPS RAM / Future Danger runtime in the game **Worker** context, and
- the actual game canvas/WebGL surface in the **Top page** context.

Existing HUD code already bridges those contexts with `BroadcastChannel`.

The anchor proof deliberately follows that real architecture. Do not assume RAM and the canvas share one JS global.

The same probe file auto-detects which context it is running in.

## Loader

Use this exact same one-line loader once in the game Worker Console and once in the Top page Console:

```js
fetch('https://raw.githubusercontent.com/ouyong520/wof-ai-private/main/parallel/HUDANCHOR/wof_player_anchor_browser_probe.js?'+Date.now()).then(r=>r.text()).then(t=>(0,eval)(t))
```

No other code paste is required.

## Test sequence

### 1. Worker Console

Run the loader.

Expected:

```text
✅ HUDANCHOR Worker probe v2 started
```

Then control P1 normally and move far enough horizontally that the **background/whole game visibly scrolls** for roughly 15 seconds. This gives the existing bounded camera-correlation model enough signal.

Do not attack or perform a new research capture. This is only a live Browser projection check.

### 2. Top page Console

Run the same loader.

Expected:

```text
✅ HUDANCHOR Top probe v2 started
```

The page overlay will show the Worker sample count and current best camera candidate.

Wait until the background has already visibly scrolled and the camera candidate is present/stable.

### 3. One calibration click

Click **once** at the exact location where you would want the center of the warning to sit: centered on P1, slightly above P1's head.

That click is used only as one-time screen ground truth for this proof. It is not pixel recognition and it is not intended as a production calibration flow.

At the click, the probe:

- records P1 live `x/y/z`,
- locks the current best camera candidate,
- derives the candidate native X bias,
- derives three vertical hypotheses from the same point:
  - `Y-Z`
  - `Y+Z`
  - `Y` only.

### 4. Validate the transform

Without reloading:

1. continue horizontal movement while the background scrolls,
2. move P1 clearly upward/downward in floor depth,
3. jump once.

Three same-style text markers appear. They are identified by **labels**, not by color:

```text
P1 Y-Z
P1 Y+Z
P1 Y
```

Observe which one remains at the desired above-character point.

The expected leading model is `Y-Z`, but the test exists specifically so this is proved rather than assumed.

If P2/P3 are present, press `F6` to cycle the diagnostic anchor across P1/P2/P3. This checks that the already-proved shared player structure projects identically. It is optional if only P1 is live.

`F7` only re-arms calibration if the initial click was bad.

## Result command

At the end, run in the **Top page Console**:

```js
WOFANCHORPROBE.result()
```

Copy the returned object and report one short visual verdict:

```text
PASS Y-Z
```

or, for example:

```text
FAIL: X drifts during camera scroll
```

```text
FAIL: Y follows depth but no Z model follows jump
```

The returned object includes:

- camera address/value and ranked candidates,
- Worker sample count,
- P1/P2/P3 current state received from Worker,
- one-time calibration constants,
- predicted native coordinates,
- predicted WebGL drawing-buffer coordinates,
- canvas CSS/content rectangle,
- drawing-buffer size.

## Pass criteria

Promote HUDANCHOR to **IMPLEMENTATION READY** only if all are true in the same test session:

1. **Horizontal:** marker stays centered over the player during ordinary X movement.
2. **Camera scroll:** marker does not drift when the background scrolls.
3. **Depth:** marker follows upper/lower floor movement.
4. **Jump:** exactly one Z model remains attached through jump; record which model.
5. **Canvas mapping:** marker remains attached after a normal resize/fullscreen toggle if tested; if the mapping is temporarily invalid it must recover without a permanent offset.
6. **P2/P3:** if available, the same projection works when diagnostic focus is cycled.

The calibration click itself may be a few pixels imperfect; pass/fail is about **relative tracking stability**, not anatomical precision of that first click.

## If the test passes

Commit the returned projection evidence under `parallel/HUDANCHOR/**`, freeze:

- camera address/read form,
- native coordinate assumptions actually confirmed by the test,
- X bias/model,
- Y/Z model,
- above-character clearance,
- drawing-buffer mapping rule.

Then hand `README.md`, `ANCHOR_MODEL.md`, `BROWSER_EVIDENCE.md`, and `IMPLEMENTATION_RECOMMENDATION.md` to a Beta implementation thread.

No new Collector sweep is needed.

## If the test fails

Do **not** expand into broad research.

Use the failure class to narrow exactly one component:

- X-only drift -> camera address/scale/sign,
- depth-only drift -> Y projection scale/bias,
- jump-only drift -> Z sign/scale,
- resize-only drift -> content-viewport/letterbox mapping,
- P2/P3-only drift -> investigate per-player render reference, despite shared object structure.

Until that component is closed, Beta must keep the fixed in-game HUD fallback.

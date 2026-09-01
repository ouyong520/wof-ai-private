# HUDANCHOR Player Projection Reverse — Minimal Live Proof

## Scope

Exactly **one uninterrupted Browser proof session** remains. Reuse `parallel/HUDANCHOR_PROOF/OPERATOR_STEPS.md` and its existing one-JSON result. Do not reopen Collector sweeps, combat capture, video frame counting, broad RAM mapping, Alpha edits, or formal HUD implementation.

## Owner input bound

The owner supplies only:

1. normal P1 movement;
2. one click at the desired warning-anchor center above P1;
3. one visible depth excursion;
4. one jump;
5. one browser resize or fullscreen transition and recovery;
6. one final visual classification button;
7. the generated JSON only.

No address selection, coordinate transcription, JS value copying, screenshot measurement, or manual arithmetic is required.

## Exact proof sequence

### A. Camera identity / X transform

Use the existing bounded Worker scanner only:

```text
0xFF0000 .. 0xFFBDFF, step 2, u16be
```

Move P1 horizontally until the background genuinely scrolls. Do not calibrate until the tool's existing camera quality gate passes:

- samples >= 80
- candidate range >= 8
- changes >= 5
- valid ratio >= 0.70
- strong ratio >= 0.45
- player-follow ratio >= 0.55
- top score gap >= 0.10 when a runner-up exists

Then make the single calibration click. The proof freezes the candidate address/read identity and derives:

```text
nativeX = worldX - camera + xBias
```

After calibration, require at least:

- world-X excursion >= 24
- camera excursion >= 6
- the locked camera address still equals the calibration camera address

Any drift or camera identity change fails closed.

### B. Floor/depth Y and Z sign

With the same calibration and session:

- depth/floor-Y excursion >= 8;
- Z excursion >= 8 from one jump.

The direct-WebGL proof plane renders only these three candidates:

```text
Y-Z + bias
Y+Z + bias
Y   + bias
```

The final visual classification must select exactly one stable model (`PASS Y-Z`, `PASS Y+Z`, or `PASS Y`). A depth or jump failure returns the existing exact failed component rather than guessing.

### C. Above-character clearance

The calibration click defines the desired warning-anchor center. The winning Y model's frozen bias is the logical `aboveCharacterOffsetNative` from the raw player floor/Z reference to that chosen point.

Acceptance requires that the selected candidate remains visually stable at that point through the horizontal, depth and jump coverage. `clearance unstable` is a fail-closed result.

### D. Drawing buffer / CSS / DPR / fullscreen

Use the existing current-frame WebGL mapping only:

```text
viewportTop = dbHeight - (vpY + vpHeight)
xDb = vpX + nativeX / 384 * vpWidth
yDb = viewportTop + nativeY / 224 * vpHeight
```

Require valid direct-WebGL evidence plus at least one actual layout change and recovery. The existing objective thresholds are:

- WebGL hook count >= 30
- marker draw count >= 30
- valid current viewport
- layout change count > 0
- stable remapping/recovery after the change

No fixed CSS scale or DPR constant may be promoted.

### E. P1/P2/P3 reuse

The common player record/projection structure is closed offline. During this one run:

- if P2/P3 are live/observable, the existing tool requires roughly 1200 ms focus for each live extra player and a valid projected point;
- if they are not live, do not force another multiplayer session solely for this stage.

A visible P2/P3 drift fails `p2p3_reuse` and narrows only that component.

## Terminal artifact

Return only the generated proof JSON.

Success must be:

```json
{"verdict":"IMPLEMENTATION_READY"}
```

with a non-null frozen `projection` block containing camera address/read, native X formula/bias, selected Y model/formula/bias, logical above-character offset, and live WebGL viewport mapping.

Any missing gate must remain:

```text
FAILED_COMPONENT:<component>
```

This is the exact bounded live proof remaining for `HUDANCHOR_PLAYER_PROJECTION_REVERSE_V1`.
